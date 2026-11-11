# Security

Thinking like an attacker, and writing Python that holds up: threat modeling, authentication and authorization, the web vulnerabilities that keep appearing, and protecting secrets and your supply chain. Every lesson has runnable code that shows the attack and the fix.

**Prerequisites:** [Python fundamentals](../00-foundations/python-fundamentals/README.md), [networking and TLS basics](../07-networking/tls-security/README.md), [databases](../05-databases/README.md).

## Learning path

| # | Lesson | You will learn |
|---|--------|----------------|
| 1 | [Threat modeling and secure Python](threat-modeling/01-threat-modeling-and-secure-python.md) | trust boundaries, STRIDE, risk ranking; `pickle`, shell injection, `random` versus `secrets`, timing leaks, allow-lists |
| 2 | [Authentication and authorization](authentication/01-authn-authz-sessions-jwt.md) | password hashing, sessions, building JWT and breaking `alg: none`, IDOR, RBAC, OAuth 2.0 with PKCE, login throttling |
| 3 | [Common web vulnerabilities](web-vulnerabilities/01-owasp-top-ten-in-python.md) | SQL injection, XSS, SSRF, path traversal, zip-slip, open redirect, mass assignment, security headers, ReDoS |
| 4 | [Secrets, dependencies and hardening](secrets-and-supply-chain/01-secrets-dependencies-and-hardening.md) | keeping secrets out of code and logs, secret scanning, supply-chain attacks, hash pinning, tamper-evident audit log, hardening checklist |

## Related lessons elsewhere

- [Cryptography and TLS lab](../07-networking/tls-security/01-cryptography-and-tls-lab.md): hashes, HMAC, RSA, a real TLS handshake
- [Containers and namespaces](../06-operating-systems/containers/01-containers-and-namespaces.md): isolation that hardening builds on
- [REST APIs and WebSockets](../07-networking/apis-realtime/01-rest-apis-and-websockets-lab.md): the interfaces you are protecting

## Ground rules for this part

Everything here is for **defending systems you own or are authorised to test**. The demos only print or touch temporary files; none contacts the network. Attacking systems you do not own is illegal.

Back to the [handbook home](../README.md).
