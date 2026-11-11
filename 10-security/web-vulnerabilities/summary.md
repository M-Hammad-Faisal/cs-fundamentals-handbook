# Web Vulnerabilities: One-Page Summary

## Key facts

- **SQL injection:** parameterised queries, never string-built SQL; validate identifiers (table or column names) against an allow-list.
- **XSS:** escape output for its context (HTML, attribute, JavaScript, URL), use a Content-Security-Policy, set cookies `HttpOnly`.
- **SSRF:** when the server fetches a user-supplied URL, allow only expected hosts, resolve and check the IP address (block private and link-local ranges such as cloud metadata), and re-check after redirects.
- **Path traversal and zip-slip:** resolve the final path and confirm it is inside the base folder before reading or extracting; reject `..` and absolute paths.
- **Open redirect:** only redirect to relative paths or allow-listed hosts.
- **Mass assignment:** bind only the fields you intend (explicit input models), never the whole request into a model with fields such as `is_admin`.
- **Security headers:** `Content-Security-Policy`, `Strict-Transport-Security`, `X-Content-Type-Options`, `Referrer-Policy`, frame protection.
- **ReDoS:** avoid nested quantifiers, bound input length, or use a linear-time engine.

## Pitfalls

- Escaping once at input instead of at output, for the context where the data lands.
- Blocking `localhost` by name but not by resolved address (DNS tricks, redirects, `0x7f.1`).
- Checking a path string for `..` instead of resolving it.
- Trusting client-sent fields such as `role`, `price` or `is_admin`.
- Relying on client-side validation alone.

## Self-check

- **What single habit prevents SQL injection, and what does it not cover?** Parameterized queries; they bind values but not identifiers, so column and table names still need allow-lists.
- **What does escaping for context mean, and why is "sanitize on input" weaker?** Encoding data correctly for where it is inserted (HTML, attribute, JavaScript, URL, SQL). Data can reach several contexts, so input sanitization cannot be right for all of them; output encoding is.
- **What is SSRF, and why are DNS rebinding and redirects a problem for URL checks?** The server is tricked into fetching an attacker-chosen (often internal) URL. A host can resolve to a safe address at check time and an internal one at fetch time, and a safe URL can redirect to an internal one, so check the address actually used and control redirects.
- **How do you stop path traversal and zip-slip?** Resolve the final path and verify it stays inside the allowed directory (check every archive member); prefer generated names over user-supplied ones.
- **What is mass assignment, and what is the fix?** Copying all client-supplied fields into a model so users can set privileged fields; accept only an explicit allow-list or schema.
- **Why can a short regex be an availability vulnerability?** Nested quantifiers cause exponential backtracking, so one crafted input can consume a CPU for seconds or hours.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Common Web Vulnerabilities in Python](01-owasp-top-ten-in-python.md)
