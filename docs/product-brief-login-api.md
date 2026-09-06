# Product Brief: Login API Service

Mission: msn_mtpa0oar_weEvSSlf1sN
Status: Product definition for downstream implementation

## Product Vision

Deliver a minimal, correct authentication service built on FastAPI that lets a
client verify a user's email and password against a known set of credentials.
The service is a foundational building block: it proves the request/response
contract for authentication and gives downstream teams a stable, testable
surface to build richer identity features on later.

Strategy: ship the smallest thing that is correct, observable, and easy to
extend. Value comes from a predictable contract (clear status codes, clear
request shape) rather than from feature breadth. Success means a client can
reliably distinguish "authenticated" from "not authenticated" and can confirm
the service is alive before depending on it.

In-scope for this mission:
- GET / healthcheck endpoint.
- POST /login endpoint that validates an email/password pair from the JSON body
  against an in-memory dictionary of users.
- 200 on a valid match, 401 on an invalid match.
- Basic automated tests covering the success and failure paths.

Explicitly out of scope (do not build):
- Real password hashing, salting, or a user database.
- Token issuance (JWT, sessions, cookies), refresh flows, or logout.
- User registration, password reset, or account management.
- Rate limiting, lockout, or brute-force protection beyond noting the risk.

Success criteria:
- Correct credentials return HTTP 200.
- Incorrect email or password returns HTTP 401.
- The healthcheck returns HTTP 200 with a simple, stable payload.
- Tests pass and cover both the 200 and 401 outcomes plus healthcheck.

## Use Cases

Personas:
- Client developer: integrates against the login endpoint and needs a
  predictable contract and clear status codes.
- Operator / deployer: needs a healthcheck to confirm the service is up before
  routing traffic to it.
- Future maintainer: needs the credential store and validation logic isolated
  so it can be swapped for a real backend without changing the API contract.

Primary workflows:
1. Liveness check. Operator or load balancer calls GET / and expects 200 with a
   small JSON body (for example {"status": "ok"}). This runs before and during
   service uptime.
2. Successful login. Client sends POST /login with a JSON body containing a
   known email and matching password. Service returns 200.
3. Failed login. Client sends POST /login with an unknown email, or a known
   email with a wrong password. Service returns 401 in both cases.
4. Malformed request. Client sends POST /login with missing fields or a
   non-JSON body. Service returns 422 (FastAPI validation default) so the client
   can distinguish a bad request from a rejected credential.

## Experience Requirements

Request contract (POST /login):
- Body is JSON with exactly two string fields: email and password.
- Use a Pydantic model so missing or wrong-typed fields yield a 422 with a
  descriptive validation error automatically.

Response contract:
- 200: valid email + password match. Return a small JSON body such as
  {"status": "ok"} or {"authenticated": true}. Keep it minimal and stable.
- 401: email not found, OR email found but password does not match. Both cases
  return the SAME 401 with a generic message (for example
  {"detail": "Invalid credentials"}). Do not reveal whether the email exists;
  a distinct "user not found" message would leak account existence.
- 422: malformed/missing body fields (FastAPI default validation).

Healthcheck (GET /):
- Always 200 when the process is running. Body is a small constant JSON object.
- No authentication required.

Error recovery and clarity:
- A caller who gets 401 knows to re-check credentials; the message is
  intentionally generic and identical for both failure reasons.
- A caller who gets 422 knows the request shape was wrong, not the credentials.
- Comparisons should be exact string matches against the in-memory dictionary.
  Document the security limitation: plaintext passwords in memory are for this
  scoped exercise only and must not be used in production.

## Validation

Observable outcomes the implementation must prove with automated tests:
- GET / returns 200 and the expected body.
- POST /login with a valid known email/password returns 200.
- POST /login with a known email but wrong password returns 401.
- POST /login with an unknown email returns 401.
- POST /login with a missing field (no password or no email) returns 422.

Recommended approach:
- Use FastAPI's TestClient (starlette) with pytest so tests run without a live
  server.
- Seed the in-memory user dictionary with at least one deterministic test user
  so tests are self-contained and repeatable.
- Assert both status code and, where relevant, response body.

Signals of done:
- All tests pass locally.
- The four status-code behaviors above (200 login, 401 wrong password, 401
  unknown user, 200 healthcheck) are each covered by a distinct test.
- No secrets or real credentials are committed.

## Future Readiness

Extensibility:
- Isolate the credential store behind a small function or class
  (for example verify_credentials(email, password)) so the in-memory dictionary
  can later be replaced by a database or identity provider without changing the
  route handlers or the API contract.
- Keep the Pydantic request model as the single source of truth for the body
  shape so adding fields later is additive.

Operational readiness:
- The GET / healthcheck is the hook for container liveness/readiness probes.
- Note in code comments that passwords are stored and compared in plaintext for
  this exercise; the migration path is hashing (for example bcrypt/argon2) plus
  a persistent store.

Adoption and compatibility:
- Returning the same 401 for unknown-user and wrong-password avoids account
  enumeration and keeps the contract stable if the backend changes.
- 422 for malformed bodies is FastAPI's default and should be preserved so
  clients can reliably distinguish input errors from auth failures.

Documentation needs:
- A short README section (or docstrings) describing the two endpoints, the
  request body shape, and the meaning of 200/401/422.

Known assumptions (resolved to unblock implementation):
- "email/password in POST body" means a JSON body, not form data.
- Success returns 200 with a small JSON confirmation body; no token is issued.
- Unknown user and wrong password both return 401 with an identical generic
  message to prevent enumeration.
- The in-memory dictionary is seeded in code (email -> password) and is not
  persisted between restarts.

[ARMADA:RESULT] COMPLETE
