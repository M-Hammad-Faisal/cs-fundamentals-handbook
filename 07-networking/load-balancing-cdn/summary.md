# Load Balancing, Proxies, CDNs and Resilience: One-Page Summary

## Key facts

- **LB:** L4 (TCP/UDP, fast) vs L7 (HTTP-aware: routing, TLS termination, retries). Reverse proxy fronts servers; API gateway adds auth and quotas.
- **Algorithms:** round robin, weighted, **least connections**, hash/consistent hash (cache affinity), **power of two choices**.
- **Health checks** (liveness vs readiness) + **connection draining**. Make the LB itself redundant.
- **Stateless servers** beat sticky sessions: state in Redis/DB/tokens.
- **CDN:** edge caches near users, protect the origin, absorb spikes; control with `Cache-Control`/`Vary`; invalidate or use hashed filenames; watch hit ratio. Never cache personalized data in shared caches.
- **Resilience:** timeouts everywhere; retries only for idempotent calls with exponential backoff + jitter; **circuit breaker**; **token-bucket** rate limits (429 + Retry-After); bulkheads; load shedding; graceful degradation.
- **Retry storms** turn blips into outages; cap retries.
- Watch p99 latency and error rates; test failures on purpose.

## Pitfalls

- Sticky sessions that hide stateful servers and lose sessions on failover.
- Health checks that only test the port, or that are so deep one shared dependency removes every server at once.
- Unbounded retries (retry storms) and retrying calls that are not idempotent.
- Caching personalised responses in a shared cache, or forgetting `Vary`.
- No cache invalidation plan; a load balancer that is itself a single point of failure.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Load Balancing and Resilience Lab](01-load-balancing-and-resilience-lab.md)
