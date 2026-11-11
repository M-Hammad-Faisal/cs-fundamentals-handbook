# Messaging and Storage: Exercises

These problems go with the [Messaging and Storage lesson](README.md). Try each one before opening its solution.

<details>
<summary>Setup code the solutions use (copied from the lessons)</summary>

```python
import hashlib

class Log:
    """An append-only log. Each record gets the next offset; records are never changed."""
    def __init__(self):
        self.records = []
    def append(self, record) -> int:
        self.records.append(record)
        return len(self.records) - 1                 # the offset of the new record
    def read(self, offset: int, max_records: int = 10):
        return list(enumerate(self.records[offset:offset + max_records], start=offset))

def partition_for(key: str, n_partitions: int) -> int:
    return int(hashlib.md5(key.encode()).hexdigest(), 16) % n_partitions

class Topic:
    def __init__(self, n_partitions):
        self.partitions = [Log() for _ in range(n_partitions)]
    def publish(self, key, value):
        p = partition_for(key, len(self.partitions))
        offset = self.partitions[p].append((key, value))
        return p, offset

def assign(partitions: int, consumers: list[str]) -> dict:
    """Round-robin partition assignment inside a consumer group."""
    plan = {c: [] for c in consumers}
    for p in range(partitions):
        plan[consumers[p % len(consumers)]].append(p)
    return plan
```

</details>

## Problems

1. Add `Log.read_from_key(key)` that returns all records for a key. How would you make it efficient at scale?
2. In `demo("process-first")`, make the handler idempotent so the final processed list has no duplicates (use a set of seen offsets).
3. Show with `assign` how many consumers beyond the partition count are useful (compute for 8 partitions and 8, 12 consumers).
4. Why is a tombstone needed instead of just removing the key from the memtable?
5. Compute the Bloom filter bit-array size for 1,000,000 keys at 10 bits per key, in megabytes.
6. Why does LSM compaction temporarily need extra disk space?

<details>
<summary>Solutions</summary>

1. ```python
   def read_from_key(log, key):
       return [(off, rec) for off, rec in log.read(0, len(log.records)) if rec[0] == key]
   t = Topic(4)
   for i in range(6):
       t.publish("u1", f"e{i}")
   p, _ = t.publish("u1", "e6")
   print(len(read_from_key(t.partitions[p], "u1")))
   # 7
   ```
   Scanning is O(n); at scale keep a key-to-offsets index per partition (or key your partitions so one consumer owns the key and builds its own state).
2. ```python
   def idempotent_demo():
       log = Log()
       for r in ["a", "b", "c", "d"]:
           log.append(r)
       seen, out, committed = set(), [], 0
       for attempt in range(2):                            # the first attempt "crashes" at offset 2 before committing
           for off, rec in log.read(committed):
               if off not in seen:
                   seen.add(off); out.append(rec)
               if attempt == 0 and off == 2:
                   break
               committed = off + 1
       return out
   print(idempotent_demo())
   # ['a', 'b', 'c', 'd']
   ```
3. ```python
   print(assign(8, [f"c{i}" for i in range(8)]) == {f"c{i}": [i] for i in range(8)}, [len(v) for v in assign(8, [f"c{i}" for i in range(12)]).values()])
   # True [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0]
   ```
   Beyond one consumer per partition, extra consumers are idle (useful only as hot standbys).
4. Older SSTables may still contain the key; removing it from the memtable would make the old value reappear. The tombstone shadows older versions until compaction drops both.
5. `1,000,000 * 10 bits = 10,000,000 bits = 1,250,000 bytes`, about 1.25 MB.
6. Compaction writes the merged output before deleting the inputs, so for a while both exist (worst case roughly double the data being merged).

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Logs, Queues and LSM Trees](01-logs-queues-and-lsm-trees.md)
