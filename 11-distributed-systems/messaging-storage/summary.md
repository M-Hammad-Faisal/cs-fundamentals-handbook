# Messaging and Storage: One-Page Summary

## Key facts

- **Log:** an append-only, ordered sequence of records; each consumer tracks its own **offset**, so many consumers can read independently and replay.
- **Delivery guarantees:** commit the offset *before* processing gives at-most-once (can lose); *after* processing gives at-least-once (can duplicate); make consumers idempotent to get effectively-once.
- **Partitions and groups:** a topic is split into partitions; order is guaranteed only within a partition (choose a key such as user id); in a consumer group each partition is read by one consumer, so parallelism is limited by the partition count.
- **LSM tree:** writes go to a write-ahead log and an in-memory table, flush to immutable sorted files (SSTables), and background **compaction** merges files and drops old versions; fast writes, reads may touch several files.
- **Bloom filter:** a bit array with several hash functions that answers "definitely not present" or "maybe present"; it has no false negatives and a tunable false-positive rate, and lets reads skip files.

## Pitfalls

- Expecting global ordering across partitions.
- More consumers than partitions (the extras sit idle).
- Committing offsets before the work is durable.
- Forgetting that a Bloom filter cannot delete items and can say "maybe" for absent keys.
- Ignoring compaction cost and write amplification.

## Self-check

- **What makes an append-only log useful, and how does it differ from a queue?** It is ordered, fast to write, replicable and replayable because records are retained; a classic queue deletes a message once consumed.
- **How do you get at-most-once and at-least-once delivery from the same consumer loop?** Commit the offset before processing for at-most-once (a crash loses the record); process first and commit after for at-least-once (a crash reprocesses it).
- **What does a partition key guarantee, and what does it not?** All records with the same key go to the same partition and stay in order there; there is no ordering across partitions.
- **How many consumers in a group can usefully read a topic with 6 partitions?** Six: each partition is read by one consumer of the group, so extra consumers are idle.
- **Outline the LSM write and read paths.** Write: append to the WAL and update the memtable, flush to an SSTable when full. Read: memtable, then SSTables newest to oldest; background compaction merges files.
- **What is a tombstone and why is it needed?** A deletion marker that shadows older versions in earlier files; without it a deleted key would reappear.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Logs, Queues and LSM Trees](01-logs-queues-and-lsm-trees.md)
