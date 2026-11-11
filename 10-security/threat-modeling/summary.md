# Threat Modeling and Secure Python: One-Page Summary

## Key facts

- **Four questions:** what are we building, what can go wrong, what will we do about it, did we do a good job? Draw data flows and **trust boundaries**, then walk each crossing.
- **STRIDE** names what can go wrong: **S**poofing, **T**ampering, **R**epudiation, **I**nformation disclosure, **D**enial of service, **E**levation of privilege. Rank threats by likelihood times impact and fix the biggest first.
- **Principles:** least privilege, defence in depth, fail closed, never trust input from across a trust boundary, keep the attack surface small.
- **Python traps:** `pickle.load` on untrusted data runs code; dynamic evaluation and `shell=True` with user input are injection; use `secrets` (not `random`) for tokens; compare secrets with `hmac.compare_digest`.
- **Validate with an allow-list:** accept only what you expect (type, length, range, pattern) and reject everything else.

## Pitfalls

- Modelling threats once and never again when the design changes.
- Using `random` for tokens or password-reset codes.
- Deny-lists ("block these characters") instead of allow-lists.
- Treating internal network traffic as trusted.
- Listing threats without owners or follow-up.

## Self-check

- **What are the four questions of threat modeling?** What are we building; what can go wrong; what will we do about it; did we do a good job.
- **What is a trust boundary, and why do bugs cluster there?** A boundary is where data moves from a less-trusted zone to a more-trusted one. Bugs cluster there because input that was never checked is suddenly treated as trustworthy.
- **Expand STRIDE and name a defence for each letter.** Spoofing (strong authentication), Tampering (HMAC, signatures, TLS), Repudiation (audit logs), Information disclosure (encryption, access control), Denial of service (rate limits), Elevation of privilege (least privilege, per-request checks).
- **Why is unpickling untrusted data equivalent to remote code execution?** Pickle lets an object name a function to call when it is rebuilt, so the attacker's data chooses code that runs in your process.
- **Why does passing arguments as a list prevent shell injection?** No shell parses the string, so characters such as `;` and `|` are plain data inside one argument, not command separators.
- **When must you use `secrets` instead of `random`?** For any value an attacker must not guess: session ids, reset tokens, API keys, one-time codes, salts.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Threat Modeling and Secure Python](01-threat-modeling-and-secure-python.md)
