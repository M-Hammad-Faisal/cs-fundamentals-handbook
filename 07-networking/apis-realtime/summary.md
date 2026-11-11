# APIs and Real-Time Communication: One-Page Summary

- **REST:** resources are plural nouns (`/users/42`); methods carry the action (`GET` read, `POST` create, `PUT` replace, `PATCH` partial update, `DELETE` remove). Safe methods (`GET`) change nothing; `GET`, `PUT` and `DELETE` are idempotent; `POST` is not unless you add an **idempotency key**.
- **Status codes:** `200` OK, `201` created, `204` no content, `304` not modified, `400` malformed, `401` not authenticated, `403` forbidden, `404` not found, `409` conflict, `422` validation failed, `429` too many requests, `5xx` server fault.
- **Collections:** paginate (offset for small data, **cursor** for large or changing data), filter, sort; never return unbounded lists.
- **Validation:** check every field on the server; return all errors at once with `422`; never trust the client.
- **Caching:** `ETag` plus `If-None-Match` gives cheap `304` responses; `Cache-Control` says how long a copy stays fresh.
- **Live data:** polling (simplest, wasteful), **Server-Sent Events** (one-way, plain HTTP, auto-reconnect), **WebSocket** (two-way, framed messages after an HTTP upgrade), **webhook** (server-to-server callback, verify an HMAC signature and a timestamp).
- **WebSocket facts:** handshake key plus a fixed GUID, SHA-1, base64 gives `Sec-WebSocket-Accept`; client frames are masked, server frames are not; small payload lengths fit in 7 bits.
- **Design checklist:** versioning (`/v1`), consistent errors, authentication on every route, rate limits, idempotent writes, documentation generated from code.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [REST APIs, SSE and WebSockets lab](01-rest-apis-and-websockets-lab.md) · Python: [building a web API with FastAPI](../../08-modern-python/backend-with-fastapi/01-building-a-web-api-with-fastapi.md)
