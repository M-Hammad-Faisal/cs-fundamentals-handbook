# Foundations of Distributed Systems: One-Page Summary

## Questions worth remembering

- **Name the three ways a request with no reply could have failed.** The request was lost; the server crashed (or is slow); the server did the work but the reply was lost.
- **What is the difference between crash-stop and Byzantine failures?** A crashed node simply stops; a Byzantine node may keep running but send wrong or malicious messages.
- **Why can't you order events across machines by wall-clock time?** Clocks drift and are adjusted by NTP, so a later event can carry an earlier timestamp.
- **State the Lamport clock rules and the guarantee they give. What is the guarantee's converse, and does it hold?** Increment on every event; send the counter with messages; on receive set `max(own, received) + 1`. Guarantee: `a → b` implies `L(a) < L(b)`. The converse (smaller timestamp means happened-before) does not hold.
- **How does a vector clock detect concurrent updates?** Each process keeps a counter per process; if neither vector dominates the other, neither event knew about the other, so they are concurrent.
- **Name two ways to resolve conflicting updates.** Last-write-wins (simple, may lose data), application-level merge (such as set union), or CRDTs.

Practice problems with solutions are in the **Practice** section of each lesson.

[Lesson](README.md) · [Failures, Time and Clocks in Distributed Systems](01-failures-time-and-clocks.md)
