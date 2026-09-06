"""Unit tests for the credential-checking seam (app/auth.py).

These exercise verify_credentials() directly, without going through the
HTTP layer, so the anti-enumeration and exact-match contract is pinned at
the single place validation logic lives.
"""

from app.auth import verify_credentials

from tests.conftest import KNOWN_EMAIL, KNOWN_PASSWORD, UNKNOWN_EMAIL


def test_verify_credentials_true_for_valid_pair():
    """Correct email + correct password returns True."""
    assert verify_credentials(KNOWN_EMAIL, KNOWN_PASSWORD) is True


def test_verify_credentials_false_for_wrong_password():
    """Known email with a wrong password returns False."""
    assert verify_credentials(KNOWN_EMAIL, "wrong-password") is False


def test_verify_credentials_false_for_unknown_email():
    """Unknown email returns False regardless of password."""
    assert verify_credentials(UNKNOWN_EMAIL, KNOWN_PASSWORD) is False


def test_verify_credentials_unknown_and_wrong_are_indistinguishable():
    """Both failure modes return the exact same False value.

    This is the seam-level anti-enumeration guarantee: a caller cannot
    tell an unknown-email failure apart from a wrong-password failure.
    """
    unknown = verify_credentials(UNKNOWN_EMAIL, "whatever")
    wrong = verify_credentials(KNOWN_EMAIL, "whatever")
    assert unknown is False
    assert wrong is False
    assert unknown == wrong


def test_verify_credentials_is_case_sensitive_on_email():
    """Email match is exact; a different-case email does not authenticate."""
    assert verify_credentials(KNOWN_EMAIL.upper(), KNOWN_PASSWORD) is False


def test_verify_credentials_rejects_email_with_surrounding_whitespace():
    """Email match is exact; surrounding whitespace does not authenticate."""
    assert verify_credentials(f" {KNOWN_EMAIL} ", KNOWN_PASSWORD) is False


def test_verify_credentials_is_case_sensitive_on_password():
    """Password comparison is exact; a different-case password fails."""
    assert verify_credentials(KNOWN_EMAIL, KNOWN_PASSWORD.upper()) is False


def test_verify_credentials_rejects_password_with_trailing_whitespace():
    """Password comparison is exact; trailing whitespace fails."""
    assert verify_credentials(KNOWN_EMAIL, KNOWN_PASSWORD + " ") is False


def test_verify_credentials_rejects_empty_password_for_known_email():
    """An empty password for a real email must not authenticate."""
    assert verify_credentials(KNOWN_EMAIL, "") is False


def test_verify_credentials_rejects_empty_email():
    """An empty email string is treated as unknown and fails."""
    assert verify_credentials("", KNOWN_PASSWORD) is False
