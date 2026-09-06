"""Credential-checking seam.

This module is the single place where credential validation logic lives.
Routes must call verify_credentials() rather than touching the user store
directly, so a future store/IdP swap only needs to change this seam and
app/users.py.
"""

from app.users import USERS


def verify_credentials(email: str, password: str) -> bool:
    """Return True only when the email exists AND the stored password
    matches exactly (exact string comparison).

    Returns the same False for both unknown-email and wrong-password so
    that no caller can distinguish the two cases (prevents account
    enumeration).
    """
    stored = USERS.get(email)
    if stored is None:
        return False
    return stored == password
