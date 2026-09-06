"""Integration tests for the FastAPI routes (app/main.py).

Exercised through TestClient so the full request/response cycle -- Pydantic
validation, route handling, and status/body shaping -- is covered.
"""

from tests.conftest import KNOWN_EMAIL, KNOWN_PASSWORD, UNKNOWN_EMAIL


# --- GET / (healthcheck) ----------------------------------------------------


def test_healthcheck_returns_200_ok(client):
    """GET / returns HTTP 200 with the constant health body."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_healthcheck_requires_no_body_or_auth(client):
    """GET / is pollable with no credentials and no request body."""
    response = client.get("/")
    assert response.status_code == 200


def test_post_to_healthcheck_is_method_not_allowed(client):
    """/ only defines GET; POST must be rejected with 405."""
    response = client.post("/")
    assert response.status_code == 405


# --- POST /login: success ---------------------------------------------------


def test_login_success_returns_authenticated_body(client):
    """Valid credentials return 200 with the distinct auth-success body."""
    response = client.post(
        "/login", json={"email": KNOWN_EMAIL, "password": KNOWN_PASSWORD}
    )
    assert response.status_code == 200
    assert response.json() == {"authenticated": True}


def test_login_success_body_differs_from_healthcheck(client):
    """Login success signal is semantically distinct from liveness."""
    health = client.get("/").json()
    login = client.post(
        "/login", json={"email": KNOWN_EMAIL, "password": KNOWN_PASSWORD}
    ).json()
    assert login != health


def test_login_ignores_extra_fields(client):
    """Unknown extra JSON keys are ignored; valid pair still authenticates."""
    response = client.post(
        "/login",
        json={
            "email": KNOWN_EMAIL,
            "password": KNOWN_PASSWORD,
            "remember_me": True,
        },
    )
    assert response.status_code == 200
    assert response.json() == {"authenticated": True}


# --- POST /login: 401 failures ----------------------------------------------


def test_login_wrong_password_returns_401(client):
    """Known email with wrong password returns 401 Invalid credentials."""
    response = client.post(
        "/login", json={"email": KNOWN_EMAIL, "password": "wrong-password"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}


def test_login_unknown_email_returns_401(client):
    """Unknown email returns 401 Invalid credentials."""
    response = client.post(
        "/login", json={"email": UNKNOWN_EMAIL, "password": KNOWN_PASSWORD}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}


def test_login_unknown_email_and_wrong_password_are_identical(client):
    """Anti-enumeration: both failure modes yield an identical 401 response.

    Same status code AND same body, so a caller cannot distinguish an
    unknown account from a wrong password.
    """
    wrong_password = client.post(
        "/login", json={"email": KNOWN_EMAIL, "password": "nope"}
    )
    unknown_email = client.post(
        "/login", json={"email": UNKNOWN_EMAIL, "password": "nope"}
    )
    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.json() == unknown_email.json()


def test_login_is_case_sensitive_on_email(client):
    """Different-case email does not authenticate (exact match contract)."""
    response = client.post(
        "/login", json={"email": KNOWN_EMAIL.upper(), "password": KNOWN_PASSWORD}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}


def test_login_rejects_email_with_whitespace(client):
    """Surrounding whitespace on the email does not authenticate."""
    response = client.post(
        "/login",
        json={"email": f" {KNOWN_EMAIL} ", "password": KNOWN_PASSWORD},
    )
    assert response.status_code == 401


def test_login_empty_password_returns_401(client):
    """A present-but-empty password fails validation of credentials (401)."""
    response = client.post(
        "/login", json={"email": KNOWN_EMAIL, "password": ""}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}


# --- POST /login: 422 request-shape errors ----------------------------------


def test_login_missing_password_returns_422(client):
    """Missing required field yields 422 before the route runs."""
    response = client.post("/login", json={"email": KNOWN_EMAIL})
    assert response.status_code == 422


def test_login_missing_email_returns_422(client):
    """Missing required field yields 422 before the route runs."""
    response = client.post("/login", json={"password": KNOWN_PASSWORD})
    assert response.status_code == 422


def test_login_empty_body_returns_422(client):
    """An empty JSON object is missing both required fields -> 422."""
    response = client.post("/login", json={})
    assert response.status_code == 422


def test_login_null_field_returns_422(client):
    """A null value for a required string field is a type error -> 422."""
    response = client.post(
        "/login", json={"email": None, "password": KNOWN_PASSWORD}
    )
    assert response.status_code == 422


def test_login_non_string_field_returns_422(client):
    """A non-string (int) value for a string field is a type error -> 422."""
    response = client.post(
        "/login", json={"email": 12345, "password": KNOWN_PASSWORD}
    )
    assert response.status_code == 422


def test_login_non_json_body_returns_422(client):
    """A body that is not a JSON object cannot be parsed as LoginRequest."""
    response = client.post(
        "/login",
        content="not json",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422


def test_get_to_login_is_method_not_allowed(client):
    """/login only defines POST; GET must be rejected with 405."""
    response = client.get("/login")
    assert response.status_code == 405


# --- OpenAPI surface --------------------------------------------------------


def test_openapi_registers_both_routes(client):
    """Both documented endpoints are present in the OpenAPI schema."""
    schema = client.get("/openapi.json").json()
    paths = schema["paths"]
    assert "get" in paths["/"]
    assert "post" in paths["/login"]
