# Foundations of Distributed Systems: One-Page Summary

## Key facts

- **Failure model:** a message may be lost, delayed, duplicated or reordered, and a node may crash or pause; you cannot tell a slow node from a dead one, so you use timeouts and design for retries.
- **Wall clocks lie:** clocks drift and jump, so timestamps from different machines cannot order events reliably.
- **Happened-before:** event A happened before B if they are on the same node in that order, or A is the send and B the receive of a message, or by transitivity; other pairs are **concurrent**.
- **Lamport clock:** a counter, incremented on each event, set to `max(local, received) + 1` on receive; if A happened before B then `L(A) < L(B)`, but the reverse does not hold.
- **Vector clock:** one counter per node; `V(A) < V(B)` means A happened before B, and incomparable vectors mean concurrent events (a conflict to resolve).
- **Simulation:** a deterministic simulated network (seeded randomness) makes distributed bugs reproducible.

## Pitfalls

- Using wall-clock timestamps to decide which write is newer.
- Reading `L(A) < L(B)` as proof that A caused B.
- Treating a timeout as proof that the other side did nothing.
- Testing only the failure-free path.

## Self-check

- **Name the three ways a request with no reply could have failed.** The request was lost; the server crashed (or is slow); the server did the work but the reply was lost.
- **What is the difference between crash-stop and Byzantine failures?** A crashed node simply stops; a Byzantine node may keep running but send wrong or malicious messages.
- **Why can't you order events across machines by wall-clock time?** Clocks drift and are adjusted by NTP, so a later event can carry an earlier timestamp.
- **State the Lamport clock rules and the guarantee they give. What is the guarantee's converse, and does it hold?** Increment on every event; send the counter with messages; on receive set `max(own, received) + 1`. Guarantee: `a → b` implies `L(a) < L(b)`. The converse (smaller timestamp means happened-before) does not hold.
- **How does a vector clock detect concurrent updates?** Each process keeps a counter per process; if neither vector dominates the other, neither event knew about the other, so they are concurrent.
- **Name two ways to resolve conflicting updates.** Last-write-wins (simple, may lose data), application-level merge (such as set union), or CRDTs.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Failures, Time and Clocks in Distributed Systems](01-failures-time-and-clocks.md)
