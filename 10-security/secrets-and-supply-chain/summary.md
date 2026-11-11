# Secrets and Supply Chain: One-Page Summary

## Questions worth remembering

- **Why is deleting a leaked secret from the latest commit not enough?** It stays in git history and in any clone or fork, and bots harvest public leaks within minutes; the secret must be revoked and rotated.
- **Where should secrets live instead of source code?** In environment variables or a secret manager, injected at runtime, different per environment, scoped to least privilege, and rotatable.
- **How does a scanner recognise secrets?** By known formats (for example the `AKIA` prefix) and by detecting high-entropy, random-looking strings.
- **What is typosquatting, and what is dependency confusion?** Typosquatting: a malicious package with a name close to a popular one. Dependency confusion: a public package with the same name as an internal one that the installer prefers.
- **What does `--require-hashes` protect against?** A tampered or substituted file (a compromised mirror or a hijacked re-upload), because the installer refuses any artifact whose hash differs from the one recorded.
- **How does hash chaining make a log tamper-evident?** Each entry includes the hash of the previous one, so changing any entry changes its hash and breaks the link to the next one; verification fails.

Practice problems with solutions are in the **Practice** section of each lesson.

[Lesson](README.md) · [Secrets, Dependencies and Hardening](01-secrets-dependencies-and-hardening.md)
