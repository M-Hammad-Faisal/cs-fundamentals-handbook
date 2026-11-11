# Authentication and Authorization: Passwords, Sessions, JWT, OAuth

**Prerequisites:** [Threat modeling and secure Python](../threat-modeling/01-threat-modeling-and-secure-python.md), [cryptography and TLS lab](../../07-networking/tls-security/01-cryptography-and-tls-lab.md), [HTTP](../../07-networking/dns-http/README.md). **You will learn:** the difference between **authentication** ("who are you?") and **authorization** ("what may you do?"), how to store passwords, how **sessions** and **JWTs** work (building a JWT from scratch and breaking a careless verifier), how to prevent **IDOR** and privilege bugs, and how **OAuth 2.0 with PKCE** keeps tokens safe, all with runnable code.

## 1. In plain words

A hotel front desk checks your ID once (**authentication**) and hands you a key card. Each door then checks what that card opens (**authorization**). Web apps do the same: log in once, receive a **token** (a session id or a signed token), and present it on every request; every endpoint must check what that identity may do. Bugs happen at both steps, and the second is more common than the first.

## 2. Storing passwords

Never store passwords, or even plain fast hashes. Store a **slow, salted hash** so that a leaked database cannot be reversed cheaply. Python's standard library has `hashlib.scrypt` (memory-hard) and `hashlib.pbkdf2_hmac`; production code often uses `argon2-cffi` or `bcrypt`, but the idea is identical.

```python
import hashlib, hmac, os, time

def hash_password(password: str) -> str:
    salt = os.urandom(16)                                   # unique per user: identical passwords hash differently
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)
    return f"scrypt${salt.hex()}${digest.hex()}"            # store the algorithm and salt WITH the hash

def verify_password(password: str, stored: str) -> bool:
    _, salt_hex, digest_hex = stored.split("$")
    digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt_hex), n=2**14, r=8, p=1, dklen=32)
    return hmac.compare_digest(digest.hex(), digest_hex)    # constant-time comparison

stored = hash_password("correct horse battery staple")
print(stored[:24] + "...", len(stored))
print(verify_password("correct horse battery staple", stored), verify_password("password123", stored))
# True False
print(stored == hash_password("correct horse battery staple"))    # same password, different salt
# False

start = time.perf_counter(); verify_password("x", stored); ms = (time.perf_counter() - start) * 1000
print("one check takes tens of milliseconds:", 5 < ms < 1000)     # slow on purpose: makes guessing expensive
# one check takes tens of milliseconds: True
```

(The exact `stored[:24]` text and length depend on the random salt, so they are not shown.) Also: enforce a minimum length (long passphrases beat complex short ones), check against lists of breached passwords, and offer multi-factor authentication.

## 3. Sessions: the classic way

After a successful login the server creates a **random session id**, stores `id -> user` **on the server**, and sends the id in a **cookie**. Each request carries the cookie; the server looks it up.

```python
import secrets, time

class SessionStore:
    def __init__(self, ttl_seconds=1800):
        self.ttl = ttl_seconds
        self.data = {}                                    # session_id -> (user, expires_at)

    def create(self, user: str) -> str:
        sid = secrets.token_urlsafe(32)                   # unguessable
        self.data[sid] = (user, time.time() + self.ttl)
        return sid

    def user_for(self, sid: str, now=None):
        entry = self.data.get(sid)
        if entry is None:
            return None
        user, expires = entry
        if (now or time.time()) > expires:
            del self.data[sid]                            # expired
            return None
        return user

    def destroy(self, sid: str):
        self.data.pop(sid, None)                          # logout really logs out

store = SessionStore(ttl_seconds=60)
sid = store.create("ada")
print(store.user_for(sid), store.user_for("guessed-id"))
# ada None
print(store.user_for(sid, now=time.time() + 3600))        # an hour later: expired
# None
```

The cookie must be set with safe attributes:

| Attribute | Effect |
|-----------|--------|
| `HttpOnly` | JavaScript cannot read it, limiting damage from XSS |
| `Secure` | sent only over HTTPS |
| `SameSite=Lax` (or `Strict`) | not sent on most cross-site requests: the main defence against CSRF |
| `Max-Age` / `Expires` | bounded lifetime |

Create a **new** session id at login (otherwise an attacker who planted a known id before login, **session fixation**, shares your session), and destroy it at logout.

## 4. JWT: a signed token you carry

A **JSON Web Token** is `header.payload.signature`, each part base64url-encoded. The server signs it, so it can verify later **without a lookup**: the token itself carries the claims (`sub` = who, `exp` = expiry, maybe `role`). Anyone can *read* the payload; only the key holder can *forge* the signature. Built from scratch (HS256 = HMAC-SHA256):

```python
import base64, hashlib, hmac, json, time

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

token = make_jwt({"sub": "ada", "role": "user", "exp": time.time() + 900})
print(token.count("."), verify_jwt(token)["sub"])
# 2 ada

# Attack 1: change the role in the payload but keep the old signature
h, p, s = token.split(".")
forged_claims = json.loads(b64d(p)); forged_claims["role"] = "admin"
tampered = f"{h}.{b64e(json.dumps(forged_claims).encode())}.{s}"
try:
    verify_jwt(tampered)
except ValueError as e:
    print("tampered:", e)
# tampered: bad signature

# Attack 2: expired token
try:
    verify_jwt(make_jwt({"sub": "ada", "exp": time.time() - 1}))
except ValueError as e:
    print("old token:", e)
# old token: token expired
```

**The famous `alg: none` bug.** A careless verifier reads the algorithm *from the token* and, if it says `none`, skips the signature check. An attacker then writes any claims they like with no signature:

```python
def naive_verify(token: str, key=KEY) -> dict:             # VULNERABLE: obeys the token's own "alg"
    header_b64, payload_b64, sig_b64 = token.split(".")
    if json.loads(b64d(header_b64))["alg"] == "none":
        return json.loads(b64d(payload_b64))                # no signature check at all
    return verify_jwt(token, key)

evil = b64e(json.dumps({"alg": "none", "typ": "JWT"}).encode()) + "." + b64e(json.dumps({"sub": "admin", "exp": 9e12}).encode()) + "."
print(naive_verify(evil)["sub"])                            # attacker is "admin" with no key
# admin
try:
    verify_jwt(evil)                                        # our pinned-algorithm verifier
except ValueError as e:
    print("safe verifier:", e)
# safe verifier: unexpected algorithm
```

**JWT cautions:** the payload is **not encrypted** (do not put secrets in it); a JWT cannot be revoked before `exp` without a deny-list, so keep lifetimes short (minutes) and pair with refresh tokens; pin the algorithm and key; in production use a maintained library (PyJWT), not hand-rolled code. **Sessions vs JWT:** sessions are easy to revoke and keep data private; JWTs scale across servers without a shared store but are harder to revoke.

## 5. Authorization: check on every request

Authentication tells you *who*. Every endpoint must still ask *may this user do this to this object?* The most common web vulnerability is **broken access control**, especially **IDOR** (insecure direct object reference): the app looks up `/notes/42` without checking that note 42 belongs to the caller.

```python
NOTES = {1: {"owner": "ada", "text": "ada's secret plan"}, 2: {"owner": "bob", "text": "bob's shopping list"}}

def get_note_vulnerable(user: str, note_id: int):
    return NOTES[note_id]["text"]                       # any logged-in user can read ANY note by guessing ids

def get_note_safe(user: str, note_id: int):
    note = NOTES.get(note_id)
    if note is None or note["owner"] != user:           # same answer for "missing" and "not yours": no information leak
        raise LookupError("not found")
    return note["text"]

print(get_note_vulnerable("bob", 1))                    # bob reads ada's note
# ada's secret plan
try:
    get_note_safe("bob", 1)
except LookupError as e:
    print("safe:", e)
# safe: not found
print(get_note_safe("ada", 1))
# ada's secret plan
```

**Role-based access control (RBAC)** maps roles to permissions and checks them in one place:

```python
from functools import wraps

ROLE_PERMISSIONS = {"viewer": {"read"}, "editor": {"read", "write"}, "admin": {"read", "write", "delete", "manage_users"}}

def requires(permission: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(user: dict, *args, **kwargs):
            if permission not in ROLE_PERMISSIONS.get(user["role"], set()):
                raise PermissionError(f"{user['name']} ({user['role']}) lacks '{permission}'")
            return fn(user, *args, **kwargs)
        return wrapper
    return decorator

@requires("delete")
def delete_post(user, post_id):
    return f"post {post_id} deleted by {user['name']}"

print(delete_post({"name": "root", "role": "admin"}, 7))
# post 7 deleted by root
try:
    delete_post({"name": "vic", "role": "viewer"}, 7)
except PermissionError as e:
    print(e)
# vic (viewer) lacks 'delete'
```

Principles: **deny by default**; enforce on the **server** (hiding a button is not security); check the **object**, not just the role; log denied attempts.

## 6. OAuth 2.0 and PKCE: "Log in with ..."

OAuth 2.0 lets a user grant an app **limited access** to their data on another service **without giving the app their password**. The modern flow for web and mobile apps is the **authorization code flow with PKCE**:

1. App creates a random **code_verifier** and sends its hash, the **code_challenge**, with the user to the provider's login page (plus a random **state** to prevent CSRF).
2. User logs in and approves at the **provider**; the provider redirects back with a one-time **code**.
3. App exchanges the **code + code_verifier** for an **access token**. The provider checks that the verifier hashes to the challenge from step 1.

PKCE means a stolen code is useless without the verifier. The challenge function, checked against the example in the standard (RFC 7636):

```python
import base64, hashlib, secrets

def pkce_challenge(verifier: str) -> str:
    return base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()

rfc_verifier = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
print(pkce_challenge(rfc_verifier))
# E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM        (matches the RFC 7636 example)

class FakeProvider:
    """Just enough of an authorization server to show why PKCE works."""
    def __init__(self):
        self.pending = {}
    def authorize(self, user: str, challenge: str) -> str:            # step 2: user approved
        code = secrets.token_urlsafe(16)
        self.pending[code] = (user, challenge)
        return code
    def token(self, code: str, verifier: str) -> str:                 # step 3
        user, challenge = self.pending.pop(code)                      # codes are single-use
        if pkce_challenge(verifier) != challenge:
            raise PermissionError("verifier does not match challenge")
        return f"access-token-for-{user}"

provider = FakeProvider()
verifier = secrets.token_urlsafe(32)
code = provider.authorize("ada", pkce_challenge(verifier))
print(provider.token(code, verifier))
# access-token-for-ada

stolen_code = provider.authorize("ada", pkce_challenge(secrets.token_urlsafe(32)))
try:
    provider.token(stolen_code, "attacker guesses a verifier")       # attacker has the code, not the verifier
except PermissionError as e:
    print("attack blocked:", e)
# attack blocked: verifier does not match challenge
```

Related: **OpenID Connect (OIDC)** adds an **ID token** (a JWT saying who logged in) on top of OAuth so it can be used for login, and **scopes** limit what the access token may do (`read:email`, not `delete:everything`).

## 7. Throttling login attempts

```python
import time

class LoginThrottle:
    def __init__(self, max_failures=3, lock_seconds=60):
        self.max, self.lock = max_failures, lock_seconds
        self.fails = {}                                 # username -> (count, first_fail_time)

    def allowed(self, username: str, now: float) -> bool:
        count, first = self.fails.get(username, (0, now))
        if count >= self.max and now - first < self.lock:
            return False
        if now - first >= self.lock:
            self.fails.pop(username, None)
        return True

    def record_failure(self, username: str, now: float):
        count, first = self.fails.get(username, (0, now))
        self.fails[username] = (count + 1, first)

t = LoginThrottle()
for i in range(3):
    t.record_failure("ada", now=100.0 + i)
print(t.allowed("ada", 105.0), t.allowed("ada", 170.0))
# False True
```

## 8. Common mistakes

- Storing passwords in plain text, with a fast unsalted hash (MD5, SHA-1, plain SHA-256), or with encryption you can reverse.
- Telling attackers which half was wrong ("no such user" versus "wrong password"); use one generic message.
- Putting trust in the client: role in a cookie or a hidden form field the user can edit.
- Forgetting object-level checks (IDOR) because the role check passed.
- JWTs: accepting `alg: none`, not pinning the algorithm, never expiring, putting secrets in the payload.
- Cookies without `HttpOnly`, `Secure` and `SameSite`.
- Long-lived tokens with no way to revoke them; sessions that survive logout.
- Using OAuth without `state` or PKCE.

## 9. Two real-world examples

**Example 1: Sequential invoice ids.** A billing site served `/invoice/10231`. Any logged-in customer could change the number and read other customers' invoices: a textbook IDOR. The fix was an ownership check in the data layer (`WHERE id = ? AND customer_id = ?`) plus non-guessable ids, because ids that cannot be guessed are only defence in depth, not a fix.

**Example 2: The unsigned token.** A startup accepted JWTs whose header said `alg: none`, left over from a debugging switch in their library settings. Anyone could mint an admin token. Pinning the algorithm and key (as in `verify_jwt`) and upgrading the library closed it.

## 10. Practice

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

## 11. Check yourself

1. Authentication versus authorization?
2. Why a salt, and why a *slow* hash?
3. Where is the state in a session, and where is it in a JWT?
4. What is the `alg: none` attack and how do you prevent it?
5. What is an IDOR, and what is the fix?
6. Name three cookie attributes and what each prevents.
7. What does PKCE protect against?

<details>
<summary>Answers</summary>

1. Authentication verifies identity ("who are you"); authorization decides permissions ("what may you do").
2. The salt makes equal passwords hash differently and defeats precomputed tables; a slow hash makes each guess expensive for an attacker with a stolen database.
3. In a session the state is on the server (id maps to data); in a JWT the claims travel inside the signed token and the server stores nothing.
4. A verifier that trusts the token's own `alg` can be told "none" and skip the signature; prevent it by pinning the expected algorithm and key on the server.
5. Insecure direct object reference: using a client-supplied id without checking ownership; fix it with an object-level authorization check on every access.
6. `HttpOnly` (blocks script access, limiting XSS damage), `Secure` (HTTPS only), `SameSite` (limits cross-site sending, defending against CSRF).
7. An intercepted authorization code: without the code verifier the attacker cannot exchange the code for a token.

</details>

[Back to Security](../README.md)
