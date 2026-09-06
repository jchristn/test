# Login API

A minimal FastAPI authentication service that verifies an email/password pair
against an in-memory credential store. It exposes a liveness/readiness
healthcheck and a single login endpoint, and is intended as a small,
self-contained example rather than a production system.

## Install

Install the dependencies with pip:

```
pip install -r requirements.txt
```

## Run

Start the service with uvicorn:

```
uvicorn app.main:app --reload
```

The application is defined in `app/main.py`. By default uvicorn serves on
`http://127.0.0.1:8000`, so the examples below use that base URL.

## Test

Run the test suite with pytest:

```
pytest
```

## Endpoints

### GET /

Liveness/readiness hook. Requires no authentication and returns 200 with a
small JSON body. Use it to check that the service is up.

Example:

```
curl http://127.0.0.1:8000/
```

### POST /login

Accepts a JSON request body:

```
{"email": "...", "password": "..."}
```

Example:

```
curl -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secret"}'
```

Responses:

- 200: the email and password match a known credential.
- 401: the credentials are not valid. The same generic message is returned for
  both an unknown email and a wrong password. Using an identical response for
  both cases prevents account enumeration (a caller cannot tell whether a given
  email is registered).
- 422: the request body is malformed or is missing required fields.

## Security Note

For this exercise only, passwords are stored and compared in plaintext in
memory. This is not safe and must not be used in production. The migration path
is to hash passwords (for example with a slow, salted algorithm) and to compare
against a persistent store instead of an in-memory dictionary.
