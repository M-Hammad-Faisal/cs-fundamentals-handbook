# Secrets and Supply Chain: One-Page Summary

## Key facts

- **Keep secrets out of code:** read them from the environment or a secrets manager, keep `.env` in `.gitignore`, give each environment its own secrets and each service the least privilege.
- **A leaked secret is burned:** removing it from the latest commit does not remove it from history; rotate it first, then clean up.
- **Find secrets early:** secret scanners in pre-commit and CI; high-entropy and known-prefix patterns.
- **Never log secrets:** redact tokens, passwords and keys in logs and error messages; log ids, not values.
- **Supply chain:** pin and lock dependencies with hashes, review new dependencies, watch for typosquatting and dependency confusion, run an audit tool (`pip-audit`), use trusted publishing and signed releases, build in clean CI.
- **Audit log:** append-only records of who did what; chaining each entry's hash to the previous one makes tampering evident.
- **Hardening checklist:** least privilege, patched dependencies, minimal images, no debug mode, TLS everywhere, backups tested.

## Pitfalls

- Believing a deleted commit is a deleted secret.
- Printing a whole config or request (with headers) into logs.
- `pip install` from unpinned names or unreviewed packages.
- Sharing one powerful key across services and environments.
- Audit logs that an attacker with write access can silently edit.

## Self-check

- **Why is deleting a leaked secret from the latest commit not enough?** It stays in git history and in any clone or fork, and bots harvest public leaks within minutes; the secret must be revoked and rotated.
- **Where should secrets live instead of source code?** In environment variables or a secret manager, injected at runtime, different per environment, scoped to least privilege, and rotatable.
- **How does a scanner recognise secrets?** By known formats (for example the `AKIA` prefix) and by detecting high-entropy, random-looking strings.
- **What is typosquatting, and what is dependency confusion?** Typosquatting: a malicious package with a name close to a popular one. Dependency confusion: a public package with the same name as an internal one that the installer prefers.
- **What does `--require-hashes` protect against?** A tampered or substituted file (a compromised mirror or a hijacked re-upload), because the installer refuses any artifact whose hash differs from the one recorded.
- **How does hash chaining make a log tamper-evident?** Each entry includes the hash of the previous one, so changing any entry changes its hash and breaks the link to the next one; verification fails.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Secrets, Dependencies and Hardening](01-secrets-dependencies-and-hardening.md)
