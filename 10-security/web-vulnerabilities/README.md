# Web Vulnerabilities

Injection, XSS, SSRF, path traversal and friends, each shown vulnerable and fixed.

## Detailed lessons

- [Common web vulnerabilities](01-owasp-top-ten-in-python.md)

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

## Quick reference

| Question | Answer |
|----------|--------|
| What single habit prevents SQL injection, and what does it not cover? | Parameterized queries; they bind values but not identifiers, so column and table names still need allow-lists. |
| What does escaping for context mean, and why is "sanitize on input" weaker? | Encoding data correctly for where it is inserted (HTML, attribute, JavaScript, URL, SQL). Data can reach several contexts, so input sanitization cannot be right for all of them; output encoding is. |
| What is SSRF, and why are DNS rebinding and redirects a problem for URL checks? | The server is tricked into fetching an attacker-chosen (often internal) URL. A host can resolve to a safe address at check time and an internal one at fetch time, and a safe URL can redirect to an internal one, so check the address actually used and control redirects. |
| How do you stop path traversal and zip-slip? | Resolve the final path and verify it stays inside the allowed directory (check every archive member); prefer generated names over user-supplied ones. |
| What is mass assignment, and what is the fix? | Copying all client-supplied fields into a model so users can set privileged fields; accept only an explicit allow-list or schema. |

Back to the [part overview](../README.md).
