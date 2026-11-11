# Replication and Sharding: One-Page Summary

## Questions worth remembering

- **What is the difference between replication and sharding?** Replication copies the same data to several machines (availability, read scale); sharding splits the data across machines (storage and write scale).
- **What is replication lag, and name one anomaly it causes and a fix.** Followers apply the leader's log after a delay, so reads can be stale. Read-your-writes violations are fixed by reading recent writes from the leader or an up-to-date follower.
- **State the quorum condition and why overlap guarantees a fresh read.** `R + W > N`: any read set and any write set share at least one replica, so the read sees the newest acknowledged version among its responses.
- **Why is `hash(key) % N` a bad scheme when servers are added?** Changing `N` remaps almost every key (about `N/(N+1)` of them), causing mass data movement or a cache flush.
- **What do virtual nodes do in consistent hashing?** They give each server many positions on the ring, which evens out the load and lets a new server take small slices from many neighbours.
- **Compare range and hash sharding.** Range sharding supports range scans but can create hot spots; hash sharding spreads load evenly but makes range queries scatter to all shards.

Practice problems with solutions are in the **Practice** section of each lesson.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Replication, Quorums and Sharding](01-replication-and-sharding.md)
