# Authentication and Authorization

Passwords, sessions, JWT, access control and OAuth 2.0 with PKCE.

## Detailed lessons

- [Authentication and authorization](01-authn-authz-sessions-jwt.md)

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

## Quick reference

| Question | Answer |
|----------|--------|
| Authentication versus authorization? | Authentication verifies identity ("who are you"); authorization decides permissions ("what may you do"). |
| Why a salt, and why a *slow* hash? | The salt makes equal passwords hash differently and defeats precomputed tables; a slow hash makes each guess expensive for an attacker with a stolen database. |
| Where is the state in a session, and where is it in a JWT? | In a session the state is on the server (id maps to data); in a JWT the claims travel inside the signed token and the server stores nothing. |
| What is the `alg: none` attack and how do you prevent it? | A verifier that trusts the token's own `alg` can be told "none" and skip the signature; prevent it by pinning the expected algorithm and key on the server. |
| What is an IDOR, and what is the fix? | Insecure direct object reference: using a client-supplied id without checking ownership; fix it with an object-level authorization check on every access. |

Back to the [part overview](../README.md).
