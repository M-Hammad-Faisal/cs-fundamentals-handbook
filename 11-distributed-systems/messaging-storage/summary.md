# Messaging and Storage: One-Page Summary

## Questions worth remembering

- **What makes an append-only log useful, and how does it differ from a queue?** It is ordered, fast to write, replicable and replayable because records are retained; a classic queue deletes a message once consumed.
- **How do you get at-most-once and at-least-once delivery from the same consumer loop?** Commit the offset before processing for at-most-once (a crash loses the record); process first and commit after for at-least-once (a crash reprocesses it).
- **What does a partition key guarantee, and what does it not?** All records with the same key go to the same partition and stay in order there; there is no ordering across partitions.
- **How many consumers in a group can usefully read a topic with 6 partitions?** Six: each partition is read by one consumer of the group, so extra consumers are idle.
- **Outline the LSM write and read paths.** Write: append to the WAL and update the memtable, flush to an SSTable when full. Read: memtable, then SSTables newest to oldest; background compaction merges files.
- **What is a tombstone and why is it needed?** A deletion marker that shadows older versions in earlier files; without it a deleted key would reappear.

Practice problems with solutions are in the **Practice** section of each lesson.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Logs, Queues and LSM Trees](01-logs-queues-and-lsm-trees.md)
