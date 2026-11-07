# TLS and Security Basics: Exercises

1. Compute SHA-256 of `"abc"` and show that changing one character changes the whole digest. Why is a hash not encryption?
2. Implement `sign(secret, body)` and `verify(secret, body, tag)` for webhooks using HMAC-SHA256 and a constant-time comparison.
3. Store and check a password with `hashlib.scrypt`: generate a salt, derive a hash, verify a login attempt.
4. Show a SQL injection against a string-built query in SQLite and fix it with a parameterized query.
5. Explain what the browser verifies when it shows a padlock for `https://shop.example.com`.
6. An attacker can see all your network traffic but cannot break the crypto. What can they still learn from a TLS connection?
7. Your certificate expired overnight. List the checks and automation you would add so it never happens again.
8. Explain CSRF with an example and two defenses.

<details>
<summary>Solutions</summary>

**1.**
```python
import hashlib
print(hashlib.sha256(b"abc").hexdigest()[:16], hashlib.sha256(b"abd").hexdigest()[:16])
```
A hash is one way and keyless: you cannot recover the input, and anyone can compute it. Encryption is reversible with the key.

**2.**
```python
import hmac, hashlib
def sign(secret: bytes, body: bytes) -> str:
    return hmac.new(secret, body, hashlib.sha256).hexdigest()
def verify(secret: bytes, body: bytes, tag: str) -> bool:
    return hmac.compare_digest(sign(secret, body), tag)
t = sign(b"k", b'{"id":1}')
print(verify(b"k", b'{"id":1}', t), verify(b"k", b'{"id":2}', t))   # True False
```

**3.**
```python
import hashlib, hmac, os
def hash_pw(pw: str):
    salt = os.urandom(16)
    return salt, hashlib.scrypt(pw.encode(), salt=salt, n=2**14, r=8, p=1)
def check_pw(pw: str, salt, digest) -> bool:
    return hmac.compare_digest(hashlib.scrypt(pw.encode(), salt=salt, n=2**14, r=8, p=1), digest)
s, d = hash_pw("hunter2")
print(check_pw("hunter2", s, d), check_pw("wrong", s, d))   # True False
```

**4.**
```python
import sqlite3
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE users (name TEXT, secret TEXT)")
db.execute("INSERT INTO users VALUES ('ana', 's1'), ('bo', 's2')")
evil = "x' OR '1'='1"
print(db.execute(f"SELECT * FROM users WHERE name = '{evil}'").fetchall())      # leaks every row
print(db.execute("SELECT * FROM users WHERE name = ?", (evil,)).fetchall())      # []
```

**5.** That the certificate chains to a trusted root, signatures and validity dates are good, it is not revoked, and `shop.example.com` appears in its Subject Alternative Names; and that the server proved possession of the private key in the handshake.

**6.** Metadata: the server's IP and usually its name (SNI, unless Encrypted Client Hello is used), the connection timing and the amount of data transferred. Not the content.

**7.** Automate renewal (ACME/certbot, managed certificates), monitor expiry with alerts at 30/14/7 days, test the renewal path, use short-lived certificates, and keep an inventory of every certificate and its owner.

**8.** A logged-in bank cookie is sent automatically, so `evil.com` can auto-submit a form to `bank.com/transfer`. Defenses: `SameSite=Lax/Strict` cookies, anti-CSRF tokens (a per-session secret required in a header or hidden field), checking `Origin`, requiring re-authentication for sensitive actions.

</details>

[Lesson](README.md) · [Summary](summary.md)
