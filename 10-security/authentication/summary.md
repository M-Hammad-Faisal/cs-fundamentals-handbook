# Authentication and Authorization: One-Page Summary

## Key facts

- **Authentication vs authorization:** who you are versus what you may do; check authorization on **every** request, on the server.
- **Passwords:** never store them plain; use a slow, salted hash (scrypt, bcrypt or Argon2) with stored parameters so cost can rise over time; the salt makes equal passwords hash differently.
- **Sessions:** the server keeps the state and the cookie holds only a random id; cookies need `HttpOnly`, `Secure` and `SameSite`; logging out deletes the server record.
- **JWT:** a signed token that carries claims; the server stores nothing, so you cannot revoke it before it expires. Pin the expected algorithm (never trust `alg: none`), verify `exp`, keep access tokens short-lived and use a revocable refresh token.
- **Object-level checks:** an IDOR is using a client-supplied id without checking ownership; use role and ownership checks (RBAC) on each access.
- **OAuth 2.0 with PKCE:** the authorization-code flow for "Log in with ..."; the `state` value blocks login CSRF and the PKCE verifier protects the code.
- **Throttling:** rate-limit and lock out repeated login attempts, with the same response for unknown user and wrong password.

## Pitfalls

- Fast hashes (MD5, SHA-256) for passwords; encryption instead of hashing.
- Putting secrets or private data in a JWT payload (it is only signed, not encrypted).
- Authorizing in the UI only, or checking the role but not the owner.
- Long-lived tokens with no revocation path.
- Comparing tokens with `==` (timing leak).

## Self-check

- **Authentication versus authorization?** Authentication verifies identity ("who are you"); authorization decides permissions ("what may you do").
- **Why a salt, and why a *slow* hash?** The salt makes equal passwords hash differently and defeats precomputed tables; a slow hash makes each guess expensive for an attacker with a stolen database.
- **Where is the state in a session, and where is it in a JWT?** In a session the state is on the server (id maps to data); in a JWT the claims travel inside the signed token and the server stores nothing.
- **What is the `alg: none` attack and how do you prevent it?** A verifier that trusts the token's own `alg` can be told "none" and skip the signature; prevent it by pinning the expected algorithm and key on the server.
- **What is an IDOR, and what is the fix?** Insecure direct object reference: using a client-supplied id without checking ownership; fix it with an object-level authorization check on every access.
- **Name three cookie attributes and what each prevents.** `HttpOnly` (blocks script access, limiting XSS damage), `Secure` (HTTPS only), `SameSite` (limits cross-site sending, defending against CSRF).

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Authentication and Authorization](01-authn-authz-sessions-jwt.md)
