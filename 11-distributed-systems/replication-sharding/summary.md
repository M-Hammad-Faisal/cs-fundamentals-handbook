# Replication and Sharding: One-Page Summary

## Key facts

- **Replication:** a leader takes writes and ships them to followers; asynchronous replication is fast but can lose recent writes on failover, synchronous waits for followers; followers can serve reads but may be stale (replication lag).
- **Quorums:** with `N` replicas, a write acknowledged by `W` and a read from `R` overlap when `R + W > N`, so a read sees the latest acknowledged write; `W = N` or `R = N` trade availability for consistency.
- **Sharding:** split data across nodes by key to scale writes and storage; **hash** sharding spreads load evenly but loses range scans, **range** sharding keeps order but can create hot spots.
- **Consistent hashing:** nodes and keys sit on a ring and a key belongs to the next node clockwise; adding or removing a node moves only about `1/N` of the keys; virtual nodes even out the load.
- **Operating it:** rebalance gradually, watch for hot keys, plan for cross-shard queries and transactions, and choose the shard key carefully because it is hard to change.

## Pitfalls

- Reading from a follower and expecting your own write to be there.
- `R + W > N` without a plan for failed nodes or clock-based conflict resolution.
- A shard key with a hot value (a celebrity user, today's date).
- Modulo hashing (`hash(key) % N`), which remaps almost every key when `N` changes.

## Self-check

- **What is the difference between replication and sharding?** Replication copies the same data to several machines (availability, read scale); sharding splits the data across machines (storage and write scale).
- **What is replication lag, and name one anomaly it causes and a fix.** Followers apply the leader's log after a delay, so reads can be stale. Read-your-writes violations are fixed by reading recent writes from the leader or an up-to-date follower.
- **State the quorum condition and why overlap guarantees a fresh read.** `R + W > N`: any read set and any write set share at least one replica, so the read sees the newest acknowledged version among its responses.
- **Why is `hash(key) % N` a bad scheme when servers are added?** Changing `N` remaps almost every key (about `N/(N+1)` of them), causing mass data movement or a cache flush.
- **What do virtual nodes do in consistent hashing?** They give each server many positions on the ring, which evens out the load and lets a new server take small slices from many neighbours.
- **Compare range and hash sharding.** Range sharding supports range scans but can create hot spots; hash sharding spreads load evenly but makes range queries scatter to all shards.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Replication, Quorums and Sharding](01-replication-and-sharding.md)
