"""Pytest tests for the login/healthcheck endpoints.

These tests use FastAPI's TestClient so they run without a live server.
The app object is imported from app.main, and the known-user credentials
are the deterministic values seeded in app/users.py.
"""

from fastapi.testclient import TestClient

from app.main import app
from app.users import USERS

# Derive the deterministic known user from the seeded store itself, so the
# test can never silently drift from app/users.py. The store is seeded with a
# single deterministic user for this exercise; take that first entry.
KNOWN_EMAIL, KNOWN_PASSWORD = next(iter(USERS.items()))

# An email guaranteed NOT to be in the store, for the unknown-account path.
UNKNOWN_EMAIL = "nobody@example.com"
assert UNKNOWN_EMAIL not in USERS

client = TestClient(app)


def test_healthcheck_returns_200_ok():
    """GET / returns 200 with the expected healthcheck body."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_login_valid_credentials_returns_200():
    """POST /login with the seeded email + matching password returns 200."""
    response = client.post(
        "/login", json={"email": KNOWN_EMAIL, "password": KNOWN_PASSWORD}
    )
    assert response.status_code == 200
    assert response.json() == {"authenticated": True}


def test_login_wrong_password_returns_401():
    """POST /login with the seeded email but a wrong password returns 401."""
    response = client.post(
        "/login", json={"email": KNOWN_EMAIL, "password": "wrong-password"}
    )
    assert response.status_code == 401


def test_login_unknown_email_returns_401():
    """POST /login with an unknown email returns 401."""
    response = client.post(
        "/login", json={"email": UNKNOWN_EMAIL, "password": KNOWN_PASSWORD}
    )
    assert response.status_code == 401


def test_login_missing_field_returns_422():
    """POST /login with a missing required field returns 422."""
    missing_password = client.post("/login", json={"email": KNOWN_EMAIL})
    assert missing_password.status_code == 422

    missing_email = client.post("/login", json={"password": KNOWN_PASSWORD})
    assert missing_email.status_code == 422


def test_login_401_responses_are_identical():
    """Wrong-password and unknown-email 401s are identical (anti-enumeration)."""
    wrong_password = client.post(
        "/login", json={"email": KNOWN_EMAIL, "password": "wrong-password"}
    )
    unknown_email = client.post(
        "/login", json={"email": UNKNOWN_EMAIL, "password": "wrong-password"}
    )
    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.json() == unknown_email.json()
