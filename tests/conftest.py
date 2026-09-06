"""Shared pytest fixtures for the login/healthcheck test suite."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.users import USERS


# A user that is guaranteed to exist in the seeded in-memory store.
KNOWN_EMAIL = "user@example.com"
KNOWN_PASSWORD = "password123"


@pytest.fixture
def client():
    """A FastAPI TestClient bound to the application under test."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def _seeded_user_present():
    """Guard the assumptions the suite makes about the seeded store.

    If the seed data changes, several tests below would silently become
    meaningless, so fail loudly here instead.
    """
    assert USERS.get(KNOWN_EMAIL) == KNOWN_PASSWORD
