# TLS and Security Basics: One-Page Summary

- **TLS** = confidentiality + integrity + authentication over TCP/QUIC.
- **Primitives:** hash (fingerprint), HMAC (keyed authentication), symmetric AEAD (AES-GCM, ChaCha20), asymmetric (signatures, key exchange), password hashing (scrypt/bcrypt/Argon2, salted). Never invent crypto; compare with `compare_digest`.
- **TLS 1.3 handshake:** 1 RTT; ephemeral ECDHE gives **forward secrecy**; server certificate + signature prove identity; then symmetric encryption.
- **Certificates:** chain to a trusted root CA; client checks signatures, dates, revocation, hostname. Self-signed = untrusted. Automate renewal (ACME).
- **Threats and fixes:** MITM (TLS, HSTS), SQL injection (parameterize), XSS (escape, CSP, HttpOnly), CSRF (SameSite, tokens), SSRF (allow-lists), weak auth (hashing, MFA, rate limits), leaked secrets.
- **AuthN vs AuthZ:** check authorization server-side on every request. OAuth = delegated access; OIDC = identity.
- **Never** disable verification, hash passwords with plain SHA-256, or trust client input.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Cryptography and TLS Lab](01-cryptography-and-tls-lab.md)
