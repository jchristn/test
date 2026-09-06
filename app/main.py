"""FastAPI application exposing a healthcheck and a login endpoint.

Discoverability: run the app and open ``/docs`` (Swagger UI) or ``/redoc``
for interactive, self-describing documentation of both endpoints, their
request shapes, and every response code below.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.auth import verify_credentials

app = FastAPI(
    title="Login API",
    version="1.0.0",
    description=(
        "A minimal authentication surface with two endpoints:\n\n"
        "- `GET /` -- unauthenticated liveness/health check.\n"
        "- `POST /login` -- validates an email/password pair.\n\n"
        "Login failures return an identical 401 for both unknown-email and "
        "wrong-password so the API cannot be used to enumerate accounts."
    ),
)


class LoginRequest(BaseModel):
    """Login request body.

    Both fields are required strings. A missing field, a null, or a
    non-string value causes FastAPI/Pydantic to auto-yield HTTP 422
    (with a field-level explanation) before the route runs.
    """

    email: str = Field(..., description="Registered account email.")
    password: str = Field(..., description="Account password.")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"email": "user@example.com", "password": "password123"}
            ]
        }
    }


@app.get(
    "/",
    summary="Health check",
    responses={200: {"description": "Service is up."}},
)
def healthcheck():
    """Liveness/health check.

    Returns HTTP 200 with a constant JSON body. No authentication and no
    request body required -- safe to poll from load balancers or uptime
    monitors.
    """
    return {"status": "ok"}


@app.post(
    "/login",
    summary="Authenticate a user",
    responses={
        200: {"description": "Credentials valid."},
        401: {
            "description": (
                "Invalid credentials. Returned identically for both an "
                "unknown email and a wrong password."
            )
        },
        422: {"description": "Request body missing or has mistyped fields."},
    },
)
def login(request: LoginRequest):
    """Authenticate a user.

    Accepts a ``LoginRequest`` JSON body and calls ``verify_credentials``.

    Responses:
    - 200: credentials valid; returns ``{"authenticated": true}``.
    - 401: unknown email OR wrong password. The identical ``"Invalid
      credentials"`` message is returned for both cases to prevent account
      enumeration.
    - 422: request body missing or mistyped fields (handled automatically
      by FastAPI/Pydantic validation).
    """
    if not verify_credentials(request.email, request.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"authenticated": True}
