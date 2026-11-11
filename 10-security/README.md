# Part 10: Security

Thinking like an attacker, and writing Python that holds up: threat modeling, authentication and authorization, the web vulnerabilities that keep appearing, and protecting secrets and your supply chain. Every lesson has runnable code that shows the attack and the fix.

**Prerequisites:** [Python fundamentals](../00-foundations/python-fundamentals/README.md), [networking and TLS basics](../07-networking/tls-security/README.md), [databases](../05-databases/README.md).

## Topics in this part

Read the topics in this order. Each has an overview, detailed lessons, exercises with solutions and a one-page summary (the full map is in the [index](../INDEX.md)).

<!-- topics:start -->
| Topic | Lessons | Exercises | Summary |
|-------|---------|-----------|---------|
| Threat Modeling and Secure Python | [overview](threat-modeling/README.md)<br>[Threat Modeling and Secure Python](threat-modeling/01-threat-modeling-and-secure-python.md) | [ex](threat-modeling/exercises.md) | [sum](threat-modeling/summary.md) |
| Authentication and Authorization | [overview](authentication/README.md)<br>[Authentication and Authorization](authentication/01-authn-authz-sessions-jwt.md) | [ex](authentication/exercises.md) | [sum](authentication/summary.md) |
| Web Vulnerabilities | [overview](web-vulnerabilities/README.md)<br>[Common Web Vulnerabilities in Python](web-vulnerabilities/01-owasp-top-ten-in-python.md) | [ex](web-vulnerabilities/exercises.md) | [sum](web-vulnerabilities/summary.md) |
| Secrets and Supply Chain | [overview](secrets-and-supply-chain/README.md)<br>[Secrets, Dependencies and Hardening](secrets-and-supply-chain/01-secrets-dependencies-and-hardening.md) | [ex](secrets-and-supply-chain/exercises.md) | [sum](secrets-and-supply-chain/summary.md) |
<!-- topics:end -->

## Related lessons elsewhere

- [Cryptography and TLS lab](../07-networking/tls-security/01-cryptography-and-tls-lab.md): hashes, HMAC, RSA, a real TLS handshake
- [Containers and namespaces](../06-operating-systems/containers/01-containers-and-namespaces.md): isolation that hardening builds on
- [REST APIs and WebSockets](../07-networking/apis-realtime/01-rest-apis-and-websockets-lab.md): the interfaces you are protecting

## Ground rules for this part

Everything here is for **defending systems you own or are authorised to test**. The demos only print or touch temporary files; none contacts the network. Attacking systems you do not own is illegal.

Back to the [handbook home](../README.md) · [index](../INDEX.md).
