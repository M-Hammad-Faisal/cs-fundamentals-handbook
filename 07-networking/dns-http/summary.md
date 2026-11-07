# DNS and HTTP: One-Page Summary

## DNS
- Hierarchical, cached: stub > recursive resolver > root > TLD > authoritative. Answers carry a **TTL**.
- Records: A/AAAA, CNAME, MX, TXT, NS, SRV, PTR. Lower TTL before migrations. Tools: `dig`, `dig +trace`.
- Wire format: header + length-prefixed labels + type + class; compression pointers.

## HTTP
- Stateless request/response: method, target, headers, body; status classes 1xx-5xx.
- **Safe** (GET, HEAD) vs **idempotent** (GET, PUT, DELETE); POST is neither: use idempotency keys.
- 401 unauthenticated, 403 forbidden, 429 rate limited, 502/503/504 upstream trouble.
- **Caching:** `Cache-Control`, `ETag` + `If-None-Match` -> 304; hash asset filenames.
- **Versions:** 1.1 keep-alive; 2 multiplexing + header compression; 3 on QUIC (UDP).
- **Cookies:** `HttpOnly`, `Secure`, `SameSite`. Sessions vs JWTs (revocation). CORS is browser-only.
- **REST:** resources as URLs, methods as verbs, proper status codes, pagination, versioning.

[Lesson](README.md) · [Exercises](exercises.md)
