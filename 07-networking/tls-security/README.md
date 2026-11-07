# TLS and Security Basics

## 1. The concept

Plain TCP is readable and modifiable by anyone on the path. **TLS** (Transport Layer Security, the "S" in HTTPS) adds three guarantees on top of a connection:

- **Confidentiality:** eavesdroppers see only ciphertext.
- **Integrity:** tampering is detected.
- **Authentication:** the client can verify it is talking to the real server (and optionally the server verifies the client: **mutual TLS**).

## 2. Cryptography building blocks

| Primitive | Purpose | Examples | Notes |
|-----------|---------|----------|-------|
| **Hash** | Fixed-size fingerprint, one way | SHA-256 | Integrity checks; not for passwords alone |
| **HMAC** | Hash with a secret key: authenticates a message | HMAC-SHA256 | Signed webhooks, tokens |
| **Symmetric encryption** | One shared key encrypts and decrypts, fast | AES-GCM, ChaCha20-Poly1305 | Bulk data |
| **Asymmetric** | Public/private key pair | RSA, ECDSA, Ed25519, X25519 | Signatures and key exchange; slow |
| **Key exchange** | Agree on a shared secret over an open channel | ECDHE | Gives **forward secrecy** |
| **Password hashing** | Deliberately slow, salted hash | scrypt, bcrypt, Argon2 | Never SHA-256 alone |

Rules: never invent your own cryptography; use vetted libraries; use **authenticated** encryption (GCM, Poly1305); keep keys out of source code.

```python
import hashlib, hmac, os

print(hashlib.sha256(b"abc").hexdigest()[:16])
tag = hmac.new(b"key", b"msg", hashlib.sha256).hexdigest()
print(hmac.compare_digest(tag, hmac.new(b"key", b"msg", hashlib.sha256).hexdigest()))
salt = os.urandom(16)
h = hashlib.scrypt(b"pw", salt=salt, n=2**14, r=8, p=1)
print(len(h))
```

`compare_digest` compares in constant time (plain `==` can leak timing). The salt makes identical passwords hash differently and defeats precomputed tables.

## 3. The TLS handshake (TLS 1.3)

```text
Client                                          Server
  | -- ClientHello (versions, ciphers, key share) -->  |
  | <-- ServerHello (key share) + certificate +        |
  |     signature + Finished  ------------------------ |   keys derived with ECDHE here
  | -- Finished ------------------------------------> |
  |        encrypted application data both ways        |      total: 1 round trip
```

1. Both sides contribute an ephemeral key share; ECDHE derives a shared secret nobody on the wire can compute. Session keys come from it, so recorded traffic stays secret even if the server's long-term key later leaks (**forward secrecy**).
2. The server sends its **certificate** and proves it holds the matching private key by signing the handshake.
3. The client validates the certificate (below), then both switch to symmetric encryption.

TLS 1.2 needs 2 round trips; TLS 1.3 needs 1 (0-RTT resumption is possible but replayable). Disable SSLv3, TLS 1.0 and 1.1.

### Certificates and trust

A **certificate** binds a public key to a name (`example.com`) and is signed by a **Certificate Authority (CA)**. The client builds a **chain**: leaf certificate, signed by an intermediate, signed by a root CA already in the OS/browser **trust store**. It checks signatures, validity dates, revocation status, and that the **hostname matches** the certificate's Subject Alternative Names. **Let's Encrypt** issues free short-lived certificates through automated ACME validation.

```python
import ssl, socket, threading, subprocess, tempfile, os, hashlib

d = tempfile.mkdtemp()
cert, key = os.path.join(d, "c.pem"), os.path.join(d, "k.pem")
subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-keyout", key,
                "-out", cert, "-days", "1", "-subj", "/CN=localhost",
                "-addext", "subjectAltName=DNS:localhost"], check=True, capture_output=True)

server_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
server_ctx.load_cert_chain(cert, key)
srv = socket.socket(); srv.bind(("127.0.0.1", 0)); srv.listen()
def serve():
    for _ in range(2):
        try:
            conn, _ = srv.accept()
            with server_ctx.wrap_socket(conn, server_side=True) as tls:
                tls.sendall(tls.recv(100)[::-1])
        except ssl.SSLError:
            pass
threading.Thread(target=serve, daemon=True).start()
port = srv.getsockname()[1]
```

```python
ctx = ssl.create_default_context(cafile=cert)
with socket.create_connection(("127.0.0.1", port)) as raw, ctx.wrap_socket(raw, server_hostname="localhost") as tls:
    tls.sendall(b"secret")
    print(tls.recv(100), tls.version())
    print(tls.getpeercert()["subject"])

# 2. default trust store -> rejects an unknown (self-signed) certificate
try:
    with socket.create_connection(("127.0.0.1", port)) as raw:
        ssl.create_default_context().wrap_socket(raw, server_hostname="localhost")
except ssl.SSLCertVerificationError as e:
    print("rejected:", e.verify_message)
```

The first connection succeeds because the client was told to trust that specific certificate. The second uses the default trust store and is **rejected**, because nothing vouches for a self-signed certificate; that rejection is the security working. (The first block needs the `openssl` command-line tool to create the demo certificate.)

## 4. Common web security threats

| Threat | What happens | Defense |
|--------|--------------|---------|
| **Man-in-the-middle** | Attacker relays and reads traffic | TLS with certificate validation; HSTS |
| **SQL injection** | Input becomes SQL | **Parameterized queries**, least-privilege DB user |
| **XSS** (cross-site scripting) | Attacker script runs in your page | Escape output, Content-Security-Policy, `HttpOnly` cookies |
| **CSRF** | Another site makes the browser send an authenticated request | `SameSite` cookies, CSRF tokens |
| **Broken authentication** | Weak passwords, stolen sessions | Hash passwords (scrypt/Argon2), MFA, rate limiting, short sessions |
| **SSRF** | Server is tricked into fetching internal URLs | Allow-lists, block private IP ranges |
| **Secrets leakage** | Keys in git or logs | Secret managers, environment injection, rotation |
| **DoS / abuse** | Overload | Rate limiting, caching, autoscaling, WAF |

Core principles: **least privilege**, **defense in depth**, **validate input and encode output**, fail closed, keep dependencies patched, log security events without logging secrets.

### Authentication vs authorization

**Authentication** = who are you (password, passkey, OAuth login). **Authorization** = what may you do (roles, ownership checks). Check authorization on **every** request on the server; hiding a button is not security. **OAuth 2.0** delegates access (a token for specific scopes); **OpenID Connect** adds identity on top.

## 5. Two real-world examples

### Example 1: Why the padlock matters less than certificate validation
A developer "fixes" an SSL error in a script with `verify=False`. The traffic is encrypted, but to *whoever answers*, including an attacker on café Wi-Fi who presents their own certificate. Encryption without authentication gives a secure channel to the wrong party. The right fix is to install the correct CA certificate or fix the hostname.

### Example 2: Webhook signature verification
A payment provider sends your server a webhook. Anyone can POST to that URL, so the provider sends `X-Signature: HMAC-SHA256(secret, body)`. Your server recomputes the HMAC over the **raw body** and compares with `compare_digest`; mismatches are rejected. Include a timestamp in the signed data to defeat replays.

## 6. Tips, tricks and pitfalls

- Never disable certificate verification in production code, even "temporarily".
- Always parameterize SQL: `cur.execute("SELECT * FROM users WHERE id = ?", (uid,))`.
- Use scrypt, bcrypt or Argon2 for passwords, with unique salts; never roll your own token or crypto scheme.
- Redirect HTTP to HTTPS and set `Strict-Transport-Security`.
- Rotate and expire secrets; scan repositories for leaked keys.
- Return generic login errors ("invalid credentials") and rate-limit attempts.
- Treat all input as hostile, including headers, filenames and JSON from your own mobile app.
- Renew certificates automatically; expired certificates are a classic outage.

## 7. Check yourself

1. What three guarantees does TLS give?
2. Why use asymmetric crypto only for the handshake and symmetric for data?
3. What is forward secrecy and which mechanism gives it?
4. How does a client decide to trust a server certificate?
5. Hash vs HMAC vs password hash?
6. How do you prevent SQL injection and XSS?
7. What does `SameSite` protect against?
8. Why is `verify=False` dangerous even though the traffic is "encrypted"?

<details>
<summary>Answers</summary>

1. Confidentiality, integrity, and authentication of the server (optionally the client).
2. Asymmetric operations are slow and size-limited; they establish a shared secret, then fast symmetric ciphers protect the bulk data.
3. Past sessions stay secret even if the server's long-term private key is later stolen; ephemeral Diffie-Hellman (ECDHE) provides it.
4. It validates the certificate chain up to a root in its trust store, checks signatures, dates, revocation and that the hostname matches the certificate's names.
5. A hash fingerprints data (no key). An HMAC adds a secret key to authenticate a message. A password hash is deliberately slow and salted to resist brute force.
6. SQL injection: parameterized queries. XSS: context-aware output escaping, Content-Security-Policy, `HttpOnly` cookies.
7. CSRF: the browser will not attach the cookie to most cross-site requests.
8. Without verification you cannot tell the real server from an attacker, so you may be encrypting traffic straight to the attacker.

</details>

[Exercises](exercises.md) · [Summary](summary.md)
