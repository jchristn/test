"""In-memory credential store.

WARNING: Plaintext in-memory passwords are used here for this scoped
exercise ONLY. The production migration path is to hash passwords
(bcrypt/argon2) and persist them in a durable store (database/IdP).
This module is the single seam that a future store/IdP swap replaces.
"""

# Mapping of email -> plaintext password. Seeded with a deterministic user.
USERS = {
    "user@example.com": "password123",
}
