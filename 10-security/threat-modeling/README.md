# Threat Modeling and Secure Python

Thinking like an attacker on paper, and the Python-specific traps that cause breaches.

## Detailed lessons

- [Threat modeling and secure Python](01-threat-modeling-and-secure-python.md)

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

## Quick reference

| Question | Answer |
|----------|--------|
| What are the four questions of threat modeling? | What are we building; what can go wrong; what will we do about it; did we do a good job. |
| What is a trust boundary, and why do bugs cluster there? | A boundary is where data moves from a less-trusted zone to a more-trusted one. Bugs cluster there because input that was never checked is suddenly treated as trustworthy. |
| Expand STRIDE and name a defence for each letter. | Spoofing (strong authentication), Tampering (HMAC, signatures, TLS), Repudiation (audit logs), Information disclosure (encryption, access control), Denial of service (rate limits), Elevation of privilege (least privilege, per-request checks). |
| Why is unpickling untrusted data equivalent to remote code execution? | Pickle lets an object name a function to call when it is rebuilt, so the attacker's data chooses code that runs in your process. |
| Why does passing arguments as a list prevent shell injection? | No shell parses the string, so characters such as `;` and `/` are plain data inside one argument, not command separators. |

Back to the [part overview](../README.md).
