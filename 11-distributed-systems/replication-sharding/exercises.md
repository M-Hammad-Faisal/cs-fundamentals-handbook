# Replication and Sharding: Exercises

Try each problem before opening its solution. These are the practice problems of this topic's lessons, collected in one place.

## Replication, Quorums and Sharding

1. In the leader/follower demo, make `f2` catch up fully and print `f2.data`. What invariant makes this safe even if `catch_up` is called repeatedly?
2. For `N=7`, which `(W, R)` pairs with `W + R = 8` are valid quorums, and which gives the fastest reads?
3. Add `remove("B")` to the ring and measure how many keys move; confirm they all move to the remaining nodes and that no key moves between untouched nodes.
4. Why does a range-sharded table keyed by timestamp create a hot spot, and how would you fix it without losing time-range queries?
5. Design a `read_your_writes` helper: a client records the log position of its last write and only reads from a follower whose `applied` is at least that.
6. A dataset is 20 TB and receives 50,000 writes/s. One machine handles 5 TB and 10,000 writes/s. How many shards at minimum, and why add replicas as well?

<details>
<summary>Solutions</summary>

1. ```python no-run
   f2.catch_up()
   print(f2.data, f2.lag)
   # {'name': 'Ada Lovelace', 'city': 'London'} 0
   ```
   Each follower remembers how many log entries it has applied (`applied`), so replays never repeat or skip entries; calling `catch_up` again does nothing once lag is 0.
2. ```python no-run
   n = 7
   print([(8 - r, r) for r in range(1, 8)])
   # [(7, 1), (6, 2), (5, 3), (4, 4), (3, 5), (2, 6), (1, 7)]
   ```
   All satisfy `W + R > 7`. `W=7, R=1` gives the fastest reads (but any down replica stops writes).
3. ```python no-run
   ring = Ring(["A", "B", "C", "D"], 100)
   before = {k: ring.lookup(k) for k in keys}
   ring.remove("B")
   after = {k: ring.lookup(k) for k in keys}
   moved = [k for k in keys if before[k] != after[k]]
   print(all(before[k] == "B" for k in moved), all(after[k] != "B" for k in moved), round(len(moved) / len(keys), 2))
   # True True 0.25
   ```
   Only keys that were on `B` move, and they spread to the remaining servers.
4. New rows always have the newest timestamp, so every write goes to the last range. Fix: prefix the key with a hash bucket (`bucket = hash(id) % 16` then `(bucket, timestamp)`) so writes spread over 16 ranges, and query each bucket for a time range (scatter-gather).
5. ```python no-run
   def read_your_writes(leader, followers, last_write_position):
       for f in followers:
           if f.applied >= last_write_position:
               return f
       return leader
   print(read_your_writes(leader, [f1], 3).__class__.__name__, read_your_writes(leader, [f1], 2).__class__.__name__)
   # Leader Follower
   ```
6. Storage needs `20 / 5 = 4` shards and writes need `50,000 / 10,000 = 5` shards, so at least 5 (the larger of the two), plus headroom. Replicas are for **availability and failure recovery**, not capacity: without them, losing one machine loses a fifth of the data and its writes.

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Replication, Quorums and Sharding](01-replication-and-sharding.md)
