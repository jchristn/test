"""FastAPI application exposing a healthcheck and a login endpoint."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.auth import verify_credentials

app = FastAPI(title="Login API")


class LoginRequest(BaseModel):
    """Login request body.

    Both fields are required strings. A missing or mistyped field causes
    FastAPI/Pydantic to auto-yield HTTP 422 before the route runs.
    """

    email: str
    password: str


@app.get("/")
def healthcheck():
    """Healthcheck endpoint.

    Returns HTTP 200 with a constant JSON body. No authentication.
    """
    return {"status": "ok"}


@app.post("/login")
def login(request: LoginRequest):
    """Authenticate a user.

    Accepts a LoginRequest JSON body and calls verify_credentials().

    Responses:
    - 200: credentials valid; returns a stable success body.
    - 401: unknown email OR wrong password. The identical message is
      returned for both cases to prevent account enumeration.
    - 422: request body missing or mistyped fields (handled automatically
      by FastAPI/Pydantic validation).
    """
    if not verify_credentials(request.email, request.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"status": "ok"}
