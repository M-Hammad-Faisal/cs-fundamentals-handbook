# APIs and Real-Time Communication

How programs expose services to each other over HTTP, and how servers push live data to clients.

## Detailed lesson

- [REST APIs, SSE and WebSockets lab](01-rest-apis-and-websockets-lab.md): REST design rules, a complete CRUD API with pagination, validation, idempotency keys and ETags, Server-Sent Events, and the WebSocket handshake and frame format implemented by hand

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

## Quick reference

| Need | Use |
|------|-----|
| CRUD over resources | REST (`GET/POST/PUT/PATCH/DELETE`, plural nouns, status codes) |
| One-way live updates to a browser | Server-Sent Events |
| Two-way low-latency messages | WebSocket |
| Server-to-server notification | webhook (verify with an HMAC signature) |
| Safe retries of `POST` | `Idempotency-Key` header |
| Large collections | pagination (offset for small data, cursor for large) |

Related: [HTTP from scratch](../dns-http/01-http-from-scratch.md), [load balancing and resilience](../load-balancing-cdn/01-load-balancing-and-resilience-lab.md), [TLS and security](../tls-security/01-cryptography-and-tls-lab.md).

Back to [networking](../README.md).
