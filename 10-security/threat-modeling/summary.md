# Threat Modeling and Secure Python: One-Page Summary

## Questions worth remembering

- **What are the four questions of threat modeling?** What are we building; what can go wrong; what will we do about it; did we do a good job.
- **What is a trust boundary, and why do bugs cluster there?** A boundary is where data moves from a less-trusted zone to a more-trusted one. Bugs cluster there because input that was never checked is suddenly treated as trustworthy.
- **Expand STRIDE and name a defence for each letter.** Spoofing (strong authentication), Tampering (HMAC, signatures, TLS), Repudiation (audit logs), Information disclosure (encryption, access control), Denial of service (rate limits), Elevation of privilege (least privilege, per-request checks).
- **Why is unpickling untrusted data equivalent to remote code execution?** Pickle lets an object name a function to call when it is rebuilt, so the attacker's data chooses code that runs in your process.
- **Why does passing arguments as a list prevent shell injection?** No shell parses the string, so characters such as `;` and `|` are plain data inside one argument, not command separators.
- **When must you use `secrets` instead of `random`?** For any value an attacker must not guess: session ids, reset tokens, API keys, one-time codes, salts.

Practice problems with solutions are in the **Practice** section of each lesson.

[Lesson](README.md) · [Threat Modeling and Secure Python](01-threat-modeling-and-secure-python.md)
