# Authentication and Authorization: Exercises

These problems go with the [Authentication and Authorization lesson](README.md). Try each one before opening its solution.

<details>
<summary>Setup code the solutions use (copied from the lessons)</summary>

```python
import hashlib, hmac, os, time
import base64, hashlib, hmac, json, time

def hash_password(password: str) -> str:
    salt = os.urandom(16)                                   # unique per user: identical passwords hash differently
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)
    return f"scrypt${salt.hex()}${digest.hex()}"            # store the algorithm and salt WITH the hash

stored = hash_password("correct horse battery staple")
KEY = b"server-secret-key-change-me"

def b64e(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()

def b64d(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))

def make_jwt(claims: dict, key=KEY) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    signing_input = b64e(json.dumps(header).encode()) + "." + b64e(json.dumps(claims).encode())
    sig = hmac.new(key, signing_input.encode(), hashlib.sha256).digest()
    return signing_input + "." + b64e(sig)

def verify_jwt(token: str, key=KEY) -> dict:
    header_b64, payload_b64, sig_b64 = token.split(".")
    header = json.loads(b64d(header_b64))
    if header.get("alg") != "HS256":                     # PIN the algorithm: never trust the token's own claim
        raise ValueError("unexpected algorithm")
    expected = hmac.new(key, f"{header_b64}.{payload_b64}".encode(), hashlib.sha256).digest()
    if not hmac.compare_digest(expected, b64d(sig_b64)):
        raise ValueError("bad signature")
    claims = json.loads(b64d(payload_b64))
    if claims.get("exp", 0) < time.time():
        raise ValueError("token expired")
    return claims

NOTES = {1: {"owner": "ada", "text": "ada's secret plan"}, 2: {"owner": "bob", "text": "bob's shopping list"}}
```

</details>

## Problems

1. Write `needs_rehash(stored)` that returns `True` if a stored hash uses fewer scrypt cost parameters than today's. Why store parameters with the hash?
2. Add a `role` claim check to `verify_jwt` through a helper `require_role(token, "admin")`.
3. Show that two users with the same password get different stored hashes.
4. Fix the following IDOR: `def delete_note(user, note_id): del NOTES[note_id]`.
5. Why must the OAuth `state` value be unguessable and checked on return?
6. A JWT lasts 24 hours and a user's account is stolen. What can you do, and what design would have made this easier?

<details>
<summary>Solutions</summary>

1. ```python
   def needs_rehash(stored: str, current_n: int = 2**14) -> bool:
       # In real systems you store n, r and p in the string; here the cost is fixed, so the idea is shown with a version tag.
       return not stored.startswith("scrypt$")
   print(needs_rehash(stored), needs_rehash("md5$abc"))
   # False True
   ```
   Storing the algorithm and its parameters lets you raise the cost over time and re-hash a user's password at their next successful login.
2. ```python
   def require_role(token: str, role: str) -> dict:
       claims = verify_jwt(token)
       if claims.get("role") != role:
           raise PermissionError("forbidden")
       return claims
   admin_token = make_jwt({"sub": "root", "role": "admin", "exp": time.time() + 60})
   print(require_role(admin_token, "admin")["sub"])
   # root
   ```
3. ```python
   print(hash_password("same") != hash_password("same"))
   # True
   ```
4. ```python
   def delete_note(user, note_id):
       note = NOTES.get(note_id)
       if note is None or note["owner"] != user:
           raise LookupError("not found")
       del NOTES[note_id]
   delete_note("bob", 2)
   print(sorted(NOTES))
   # [1]
   ```
5. `state` binds the response to the request the user started. If it is guessable or unchecked, an attacker can trick a victim's browser into completing the attacker's login (login CSRF), linking the attacker's account to the victim's session.
6. A JWT cannot be recalled before it expires; you can add its id to a deny-list the server checks, or rotate the signing key (logging everyone out). Short-lived access tokens (5 to 15 minutes) with a revocable refresh token make this easy.

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Authentication and Authorization](01-authn-authz-sessions-jwt.md)
