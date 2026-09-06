"""Shared pytest fixtures and constants for the login/healthcheck suite.

The known-user credentials are derived from the seeded store itself rather
than hardcoded, so the whole suite tracks app/users.py automatically and can
never silently drift from the seed data it is meant to exercise.
"""

import pytest
from fastapi.testclient import TestClient

from app.auth import verify_credentials
from app.main import app
from app.users import USERS


# Derive the deterministic known user from the seeded store, so every test
# module that imports these constants stays in lockstep with app/users.py.
# The store is seeded with a single deterministic user for this exercise;
# take that first entry.
KNOWN_EMAIL, KNOWN_PASSWORD = next(iter(USERS.items()))

# An email guaranteed NOT to be in the store, for the unknown-account path.
# Shared here so every module uses the same guaranteed-absent value instead
# of re-typing a literal that could accidentally collide with a future seed.
UNKNOWN_EMAIL = "nobody@example.com"


@pytest.fixture
def client():
    """A FastAPI TestClient bound to the application under test."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def _seed_assumptions_hold():
    """Guard the structural assumptions the suite depends on.

    Rather than re-check a hardcoded credential against itself, verify the
    invariants that would silently break tests if the seed changed shape:
    the store is non-empty, the derived pair actually authenticates through
    the real seam, and the unknown email is genuinely absent. Fail loudly
    here instead of letting downstream assertions become meaningless.
    """
    assert USERS, "seeded user store is empty"
    assert verify_credentials(KNOWN_EMAIL, KNOWN_PASSWORD) is True
    assert UNKNOWN_EMAIL not in USERS
