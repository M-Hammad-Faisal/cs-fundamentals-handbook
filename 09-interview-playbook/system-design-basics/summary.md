# System Design Basics: One-Page Summary

**Framework (about 45 min):** 1) clarify requirements (functional + non-functional) 2) estimate scale 3) API + data model 4) high-level design (walk one request) 5) deep dive on the hard parts 6) bottlenecks, failures, trade-offs, what next.

**Estimation:** day ~ 86,400 s (use 100k); year ~ 30M s; avg QPS = per day / 86,400; peak ~ 2-3x average; storage = records x size x retention x replicas. Latencies: memory 100 ns, SSD 100 us, datacenter RTT 0.5 ms, cross-continent 100+ ms. Nines: 99.9% = 8.8 h/year, 99.99% = 53 min, 99.999% = 5 min; series multiply, parallel redundancy multiplies failure odds.

**Building blocks:** load balancer (stateless services) | caching (cache-aside default; LRU; watch stale data and stampedes) | databases (SQL first; replicate; shard by a good key) | queues (async, at-least-once, idempotent consumers, DLQ) | CDN + object storage | rate limiting (token bucket, Redis) | IDs (UUID/Snowflake) | cursor pagination.

**Principles:** scale out stateless services; cache everywhere; move work off the request path; partition data; replicate for availability; design for failure (timeouts, retries with jitter, circuit breakers); observe (SLIs/SLOs); start simple. **CAP/PACELC:** choose consistency for money and uniqueness, availability for feeds and counters.

**Classic designs:** URL shortener (base62 + cache + sharded KV, 302 for analytics) | news feed (fan-out on write for normal users, on read for celebrities) | chat (WebSockets, per-conversation ordering, presence TTLs) | notifications (queue + idempotency keys) | KV store (consistent hashing, quorums, LSM).

**Pitfalls:** no numbers, jumping to microservices, ignoring failures/monitoring/consistency, name-dropping tech without trade-offs, designing everything instead of going deep.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [System Design, Part 2](02-five-more-designs.md) · [System Design, Part 3](03-caching-failure-modes-and-reliability.md)
