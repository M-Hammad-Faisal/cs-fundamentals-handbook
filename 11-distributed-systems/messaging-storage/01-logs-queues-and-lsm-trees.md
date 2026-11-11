# Logs, Queues and LSM Trees: How Distributed Data Is Stored and Moved

**Prerequisites:** [Replication and sharding](../replication-sharding/01-replication-and-sharding.md), [idempotency and sagas](../transactions/01-idempotency-retries-and-sagas.md), [indexes and B-trees](../../05-databases/indexes-query-plans/README.md), [hash tables](../../02-data-structures/hash-tables/README.md). **You will learn:** the humble **append-only log** that underlies Kafka, databases and replication; **partitions**, **consumer groups** and **delivery guarantees**; how an **LSM tree** (the engine in Cassandra, RocksDB, LevelDB) turns random writes into sequential ones; and how a **Bloom filter** saves disk reads, each implemented and measured in Python.

## 1. In plain words

The simplest durable data structure is a **log**: a file you only ever **append** to. Appending is fast (sequential disk writes), ordered, and never overwrites anything, so it is easy to replicate and easy to recover. Surprisingly many systems are logs in disguise: a database's write-ahead log, Raft's replicated log, Kafka topics, git history and accounting ledgers. Two big ideas follow:

1. **Messaging:** producers append events; consumers read at their own pace and remember **where they are** (an offset).
2. **Storage:** keep recent writes in memory plus a log, then merge sorted files in the background (**LSM trees**).

## 2. A log with consumer offsets

```python
class Log:
    """An append-only log. Each record gets the next offset; records are never changed."""
    def __init__(self):
        self.records = []
    def append(self, record) -> int:
        self.records.append(record)
        return len(self.records) - 1                 # the offset of the new record
    def read(self, offset: int, max_records: int = 10):
        return list(enumerate(self.records[offset:offset + max_records], start=offset))

log = Log()
for event in ["signup:ada", "order:1", "order:2", "signup:bob", "order:3"]:
    log.append(event)

# two independent consumers, each remembers its own offset
analytics_offset, email_offset = 0, 3
print([r for _, r in log.read(analytics_offset)])      # analytics replays everything from the start
# ['signup:ada', 'order:1', 'order:2', 'signup:bob', 'order:3']
print([r for _, r in log.read(email_offset)])          # the email service only needs the latest
# ['signup:bob', 'order:3']
```

Unlike a classic queue (where reading **removes** the message), a log keeps its records, so you can **replay** history, add a new consumer later, rebuild a database or search index from scratch, and debug "what happened". Old records are deleted by **retention** (age or size) or **compaction** (keep only the latest record per key).

## 3. Delivery guarantees: where you commit the offset

A consumer processes a record and then **commits** its offset. A crash can strike between the two steps; the order you choose decides what a crash costs.

```python
class Consumer:
    def __init__(self, log):
        self.log, self.committed, self.processed = log, 0, []

    def run(self, mode, crash_at=None):
        """mode: 'commit-first' = at-most-once, 'process-first' = at-least-once."""
        offset = self.committed
        for off, record in self.log.read(offset):
            if mode == "commit-first":
                self.committed = off + 1                 # commit...
                if off == crash_at:
                    return "crashed"                      # ...crash before processing: the record is LOST
                self.processed.append(record)
            else:
                self.processed.append(record)             # process...
                if off == crash_at:
                    return "crashed"                      # ...crash before commit: the record is processed AGAIN later
                self.committed = off + 1
        return "done"

def demo(mode):
    log = Log()
    for r in ["a", "b", "c", "d"]:
        log.append(r)
    c = Consumer(log)
    c.run(mode, crash_at=2)                               # crash while handling record 'c'
    c.run(mode)                                           # restart from the committed offset
    return c.processed

print("at-most-once :", demo("commit-first"))
print("at-least-once:", demo("process-first"))
# at-most-once : ['a', 'b', 'd']
# at-least-once: ['a', 'b', 'c', 'c', 'd']
```

| Guarantee | Meaning | Cost |
|-----------|---------|------|
| **At-most-once** | never duplicated, may be lost | simplest; fine for metrics where a gap is tolerable |
| **At-least-once** | never lost, may be duplicated | the usual default; **requires idempotent consumers** |
| **Exactly-once (effect)** | as if processed once | achieved as at-least-once delivery **plus** deduplication or transactional writes of offset and result together |

Genuine "exactly-once delivery" over an unreliable network does not exist; systems that advertise it combine retries with idempotence or atomic commits (see the [outbox](../transactions/01-idempotency-retries-and-sagas.md)).

## 4. Partitions and consumer groups

One log on one machine limits throughput. A **topic** is split into **partitions** (each its own log). Records with the same **key** go to the same partition, so **ordering is guaranteed per key**, not across the whole topic. A **consumer group** shares the work: each partition is read by **exactly one** consumer in the group.

```python
import hashlib

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

topic = Topic(4)
for i in range(8):
    topic.publish(["ada", "bob", "cy"][i % 3], f"event{i}")
for p, part in enumerate(topic.partitions):
    print(f"partition {p}: {[v for _, v in (r for _, r in part.read(0))]}")
# partition 0: ['event1', 'event4', 'event7']
# partition 1: ['event0', 'event3', 'event6']
# partition 2: ['event2', 'event5']
# partition 3: []
print("2 consumers:", assign(4, ["c1", "c2"]))
print("rebalance after c2 leaves:", assign(4, ["c1"]))
print("5 consumers on 4 partitions:", assign(4, ["c1", "c2", "c3", "c4", "c5"]))
# 2 consumers: {'c1': [0, 2], 'c2': [1, 3]}
# rebalance after c2 leaves: {'c1': [0, 1, 2, 3]}
# 5 consumers on 4 partitions: {'c1': [0], 'c2': [1], 'c3': [2], 'c4': [3], 'c5': []}
```

Every event for `ada` (events 0, 3, 6) lands in partition 1, in order: that is the per-key ordering guarantee. Adding consumers speeds up processing only until there is **one consumer per partition**; the fifth consumer sits idle, so choose a partition count with future growth in mind. When a consumer joins or leaves, the group **rebalances**.

**Queue versus log versus pub/sub:** a work queue (RabbitMQ, SQS) distributes tasks and deletes them when done (good for job processing); a log (Kafka, Redpanda, Pulsar) retains ordered history and lets many independent consumer groups replay it (good for event streams and data pipelines).

## 5. Storing data: the LSM tree

Updating a B-tree on disk means **random writes** to many pages. The **log-structured merge tree (LSM)** converts them into sequential ones:

1. Write to an **append-only WAL** (write-ahead log, for crash recovery) and insert into an in-memory sorted table, the **memtable**.
2. When the memtable is full, **flush** it to disk as an immutable sorted file (an **SSTable**).
3. **Reads** check the memtable, then SSTables from newest to oldest.
4. **Deletes** write a **tombstone** marker (the old value may still sit in an older file).
5. In the background, **compaction** merges SSTables, dropping overwritten values and tombstones.

```python
import bisect

TOMBSTONE = object()                                   # marks "this key was deleted"

class SSTable:
    """An immutable sorted run of (key, value) pairs."""
    def __init__(self, items):
        self.keys = [k for k, _ in items]
        self.values = [v for _, v in items]
    def get(self, key):
        i = bisect.bisect_left(self.keys, key)         # binary search: O(log n)
        if i < len(self.keys) and self.keys[i] == key:
            return True, self.values[i]
        return False, None

class LSM:
    def __init__(self, memtable_limit=3):
        self.wal, self.memtable, self.sstables = [], {}, []       # sstables: newest last
        self.limit = memtable_limit
        self.table_reads = 0                                       # how many SSTables a read had to search

    def put(self, key, value):
        self.wal.append((key, value))                  # 1. durable sequential write (a real WAL is on disk)
        self.memtable[key] = value                     # 2. in-memory update
        if len(self.memtable) >= self.limit:
            self.flush()

    def delete(self, key):
        self.put(key, TOMBSTONE)

    def flush(self):
        self.sstables.append(SSTable(sorted(self.memtable.items())))
        self.memtable, self.wal = {}, []               # the WAL can be discarded once the data is in an SSTable

    def get(self, key):
        if key in self.memtable:
            v = self.memtable[key]
            return None if v is TOMBSTONE else v
        for table in reversed(self.sstables):          # newest first: the first hit is the latest version
            self.table_reads += 1
            found, v = table.get(key)
            if found:
                return None if v is TOMBSTONE else v
        return None

    def compact(self):
        """Merge all SSTables into one; newer values win and tombstones disappear."""
        merged = {}
        for table in self.sstables:                    # oldest to newest, so newer overwrites older
            merged.update(zip(table.keys, table.values))
        live = sorted((k, v) for k, v in merged.items() if v is not TOMBSTONE)
        self.sstables = [SSTable(live)]

db = LSM(memtable_limit=3)
for k, v in [("a", 1), ("b", 2), ("c", 3), ("a", 10), ("d", 4), ("e", 5)]:
    db.put(k, v)
db.delete("b")
print("tables on disk:", len(db.sstables), "| memtable:", {k: v for k, v in db.memtable.items() if v is not TOMBSTONE}, "| memtable has tombstone:", TOMBSTONE in db.memtable.values())
# tables on disk: 2 | memtable: {} | memtable has tombstone: True
print("a ->", db.get("a"), "| b ->", db.get("b"), "| c ->", db.get("c"), "| z ->", db.get("z"))
# a -> 10 | b -> None | c -> 3 | z -> None
db.flush()
db.compact()
print("after compaction: tables =", len(db.sstables), "keys =", db.sstables[0].keys)
# after compaction: tables = 1 keys = ['a', 'c', 'd', 'e']
```

`a` was written twice; reads return the newest (10). `b` was deleted by a tombstone, and compaction finally removed both the tombstone and the old value. The costs of the design: **read amplification** (a key may be searched in many SSTables), **write amplification** (data is rewritten by compaction) and **space amplification** (old versions linger until compaction). A B-tree has the opposite profile:

| | LSM tree | B-tree |
|--|----------|--------|
| Writes | very fast (sequential) | slower (random page updates, in-place) |
| Reads | may check several files (use Bloom filters) | one root-to-leaf path |
| Space | extra until compaction | in-place, some fragmentation |
| Used by | Cassandra, RocksDB, LevelDB, HBase, ScyllaDB | PostgreSQL, MySQL (InnoDB), SQLite |

## 6. Bloom filters: skip files that cannot contain the key

A read for a key that **does not exist** would otherwise search every SSTable. A **Bloom filter** is a small bit array that answers "definitely not here" or "maybe here": no false negatives, a tunable rate of false positives. Adding a key sets `k` bits chosen by `k` hash functions; a lookup checks those bits.

```python
import hashlib, math

class BloomFilter:
    def __init__(self, expected_items, bits_per_item=10):
        self.m = expected_items * bits_per_item                   # number of bits
        self.k = max(1, round(bits_per_item * math.log(2)))       # optimal number of hash functions
        self.bits = bytearray(self.m)                              # one byte per bit, for clarity

    def _positions(self, key):
        return [int(hashlib.md5(f"{i}|{key}".encode()).hexdigest(), 16) % self.m for i in range(self.k)]   # k different hash functions

    def add(self, key):
        for p in self._positions(key):
            self.bits[p] = 1

    def might_contain(self, key):
        return all(self.bits[p] for p in self._positions(key))

bf = BloomFilter(expected_items=1000, bits_per_item=10)
for i in range(1000):
    bf.add(f"user:{i}")

print("no false negatives:", all(bf.might_contain(f"user:{i}") for i in range(1000)))
# no false negatives: True
false_positives = sum(bf.might_contain(f"other:{i}") for i in range(10_000))
print(f"false positive rate: {false_positives / 10_000:.1%} (theory for 10 bits/item: about 0.8%)")
# false positive rate: 0.7% (theory for 10 bits/item: about 0.8%)
```

Ten bits per key (about 1.25 bytes) gives under 1 percent false positives. An LSM keeps one Bloom filter per SSTable in memory, so a lookup for an absent key skips almost every file. Using it:

```python
class LSMWithBloom(LSM):
    def __init__(self, memtable_limit=3):
        super().__init__(memtable_limit)
        self.blooms = []
    def flush(self):
        super().flush()
        bf = BloomFilter(expected_items=max(1, len(self.sstables[-1].keys)))
        for k in self.sstables[-1].keys:
            bf.add(k)
        self.blooms.append(bf)
    def get(self, key):
        if key in self.memtable:
            v = self.memtable[key]
            return None if v is TOMBSTONE else v
        for table, bf in zip(reversed(self.sstables), reversed(self.blooms)):
            if not bf.might_contain(key):
                continue                                           # definitely not in this file: skip the disk read
            self.table_reads += 1
            found, v = table.get(key)
            if found:
                return None if v is TOMBSTONE else v
        return None

plain, bloomed = LSM(3), LSMWithBloom(3)
for db_ in (plain, bloomed):
    for i in range(300):
        db_.put(f"key{i:04d}", i)
for i in range(1000):                                              # look up keys that do not exist
    plain.get(f"missing{i}"); bloomed.get(f"missing{i}")
print("SSTables searched for 1000 missing keys: plain =", plain.table_reads, "| with Bloom filters =", bloomed.table_reads)
# SSTables searched for 1000 missing keys: plain = 100000 | with Bloom filters = 1120
```

The plain LSM searched all 100 SSTables for every missing key (100,000 searches); with Bloom filters the total fell to **1,120**, about one search per lookup (the filters' small false-positive rate, accumulated over 100 files).

## 7. Common mistakes

- Treating at-least-once delivery as exactly-once: duplicates appear on retries and rebalances.
- Choosing a partition key with skew (everything for one tenant in one partition) or too few partitions to grow.
- Expecting ordering across partitions; only per-partition (per-key) order exists.
- Unbounded logs with no retention or compaction policy.
- Treating the memtable as durable: without the WAL, a crash loses recent writes.
- Forgetting compaction: reads slow down as SSTables pile up, and deletes never free space.
- Using a Bloom filter where false negatives would be harmful (they never occur, but you cannot delete from a plain one).
- Using a message queue as a database, or a database table as a high-volume stream, when the other fits better.

## 8. Two real-world examples

**Example 1: Rebuilding a search index.** A shop kept every product change as an event in a log. When the search schema changed, the team simply started a **new consumer group** reading from offset 0 and rebuilt the index while the old one kept serving; no migration script, no downtime.

**Example 2: The write-heavy sensor fleet.** A telemetry service ingesting hundreds of thousands of readings per second struggled on a B-tree database because of random page writes. Moving to an LSM-based store absorbed the writes sequentially; a Bloom filter per file kept point lookups fast, and time-window compaction dropped old data cheaply.

## 9. Practice

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

## 10. Check yourself

1. What makes an append-only log useful, and how does it differ from a queue?
2. How do you get at-most-once and at-least-once delivery from the same consumer loop?
3. What does a partition key guarantee, and what does it not?
4. How many consumers in a group can usefully read a topic with 6 partitions?
5. Outline the LSM write and read paths.
6. What is a tombstone and why is it needed?
7. What does a Bloom filter promise, and what does it not?

<details>
<summary>Answers</summary>

1. It is ordered, fast to write, replicable and replayable because records are retained; a classic queue deletes a message once consumed.
2. Commit the offset before processing for at-most-once (a crash loses the record); process first and commit after for at-least-once (a crash reprocesses it).
3. All records with the same key go to the same partition and stay in order there; there is no ordering across partitions.
4. Six: each partition is read by one consumer of the group, so extra consumers are idle.
5. Write: append to the WAL and update the memtable, flush to an SSTable when full. Read: memtable, then SSTables newest to oldest; background compaction merges files.
6. A deletion marker that shadows older versions in earlier files; without it a deleted key would reappear.
7. "Definitely not present" is always correct (no false negatives); "maybe present" may be wrong at a low, tunable false-positive rate.

</details>

[Back to Distributed Systems](../README.md)
