# Replication, Quorums and Sharding

**Prerequisites:** [Failures, time and clocks](../foundations/01-failures-time-and-clocks.md), [hash tables](../../02-data-structures/hash-tables/README.md), [databases and transactions](../../05-databases/transactions-acid/README.md). **You will learn:** the two ways to scale a data store: **replication** (copies, for availability and read capacity) and **sharding** (splitting, for write capacity and size); **replication lag** and what it breaks; **quorums** (`R + W > N`) proved by brute force; and **consistent hashing** with virtual nodes, measured against `hash % N`.

## 1. In plain words

One database server eventually runs out of something: disk, memory, CPU, or simply **survival** (if it dies, you are down). Two separate remedies:

- **Replication:** keep **copies** of the same data on several machines. Survives a machine failure and spreads read traffic.
- **Sharding (partitioning):** split the data into **pieces**, each on a different machine. Spreads writes and storage when the data does not fit on one machine.

Real systems use both: each shard is replicated.

## 2. Replication: leader and followers

The most common design: one **leader** accepts writes and appends them to a **log**; **followers** copy the log and serve reads.

```python
class Leader:
    def __init__(self):
        self.log, self.data = [], {}
    def write(self, key, value):
        self.log.append((key, value))             # the replication log: an ordered list of changes
        self.data[key] = value

class Follower:
    def __init__(self, leader, name):
        self.leader, self.name, self.applied, self.data = leader, name, 0, {}
    def catch_up(self, max_entries=None):
        entries = self.leader.log[self.applied:]
        if max_entries is not None:
            entries = entries[:max_entries]
        for key, value in entries:                # replay the leader's changes in order
            self.data[key] = value
        self.applied += len(entries)
    @property
    def lag(self):
        return len(self.leader.log) - self.applied

leader = Leader()
f1, f2 = Follower(leader, "f1"), Follower(leader, "f2")
leader.write("name", "Ada")
f1.catch_up(); f2.catch_up()
leader.write("name", "Ada Lovelace")
leader.write("city", "London")
f1.catch_up(1)                                    # f1 has applied one more entry, f2 none

print("leader:", leader.data["name"])
print("f1    :", f1.data.get("name"), "| lag", f1.lag)
print("f2    :", f2.data.get("name"), "| lag", f2.lag)
# leader: Ada Lovelace
# f1    : Ada Lovelace | lag 1
# f2    : Ada | lag 2
```

**Synchronous** replication waits for followers to confirm before acknowledging a write (safe, slower, a dead follower blocks writes); **asynchronous** replication acknowledges immediately (fast, but **replication lag** exists and a leader crash can lose the most recent writes). Many systems use **semi-synchronous**: wait for one follower.

**Anomalies caused by lag** (the follower `f2` above returns the old name):

- **Read-your-writes violation:** you update your profile and the next page load, served by a lagging follower, shows the old one. *Fix:* read your own recent writes from the leader, or from a follower that has caught up to your write's log position.
- **Monotonic-read violation:** you see new data, refresh, and see older data because you hit a different follower. *Fix:* pin a user to one replica.
- **Failover:** when the leader dies, a follower is promoted. Risks: lost writes on the old leader, **split brain** (two nodes both think they are leader; solved with [consensus](../consensus/01-consensus-and-raft.md) and leases), and clients still talking to the old leader.

**Other topologies:** **multi-leader** (several writable regions; needs conflict resolution, see [vector clocks](../foundations/01-failures-time-and-clocks.md)) and **leaderless** (Dynamo, Cassandra: send writes to several nodes, use quorums, next section).

## 3. Quorums: `R + W > N`

In a leaderless system with `N` replicas, a write succeeds once `W` replicas acknowledge it, and a read asks `R` replicas and takes the newest version. If **`R + W > N`**, every read set must overlap every write set in at least one replica, so a read always sees the latest successful write. We can check the claim by brute force over every possible pair of sets:

```python
import itertools

def always_overlaps(n: int, w: int, r: int) -> bool:
    nodes = range(n)
    for write_set in itertools.combinations(nodes, w):
        for read_set in itertools.combinations(nodes, r):
            if not set(write_set) & set(read_set):
                return False                      # found a read that could miss the latest write
    return True

for n, w, r in [(3, 1, 1), (3, 2, 2), (3, 3, 1), (3, 1, 3), (5, 3, 3), (5, 2, 3), (5, 2, 2)]:
    print(f"N={n} W={w} R={r}  R+W>N: {r + w > n!s:<5}  reads always see latest write: {always_overlaps(n, w, r)}")
# N=3 W=1 R=1  R+W>N: False  reads always see latest write: False
# N=3 W=2 R=2  R+W>N: True   reads always see latest write: True
# N=3 W=3 R=1  R+W>N: True   reads always see latest write: True
# N=3 W=1 R=3  R+W>N: True   reads always see latest write: True
# N=5 W=3 R=3  R+W>N: True   reads always see latest write: True
# N=5 W=2 R=3  R+W>N: False  reads always see latest write: False
# N=5 W=2 R=2  R+W>N: False  reads always see latest write: False
```

The trade-off is a dial: `W=N, R=1` makes reads fast but any down replica blocks writes; `W=1, R=N` the reverse; `W=R=majority` tolerates `floor((N-1)/2)` failures in both directions. The quorum condition is necessary but **not sufficient** for strict consistency: concurrent writes, sloppy quorums and failed partial writes can still produce stale or conflicting reads (hence read repair, anti-entropy and version vectors). This is the heart of the **CAP** trade-off: during a network partition a system must choose between **consistency** (refuse some requests) and **availability** (answer, possibly stale).

## 4. Sharding: splitting the data

Choose a **shard key** and map each key to a shard. Two main strategies:

| Strategy | How | Good | Bad |
|----------|-----|------|-----|
| **Range** | shard 1 holds keys A to F, shard 2 G to M, ... | efficient range scans | hot spots (new keys, such as increasing ids or timestamps, all land on the last shard) |
| **Hash** | shard = hash(key) mod N (or a ring) | even spread | range queries must ask every shard |

The hot-spot problem, shown with auto-incrementing ids:

```python
import hashlib
from collections import Counter

def h(s: str) -> int:                              # stable hash (Python's built-in hash() changes between runs)
    return int(hashlib.md5(s.encode()).hexdigest(), 16)

range_bounds = [250, 500, 750]                     # shard 0: ids 1-250, shard 1: 251-500, shard 2: 501-750, shard 3: the rest
def range_shard(i):
    for shard, bound in enumerate(range_bounds):
        if i <= bound:
            return shard
    return 3

new_ids = range(1001, 1101)                        # the next 100 inserts have increasing ids
print("range:", sorted(Counter(range_shard(i) for i in new_ids).items()))
print("hash :", sorted(Counter(h(str(i)) % 4 for i in new_ids).items()))
# range: [(3, 100)]
# hash : [(0, 25), (1, 22), (2, 22), (3, 31)]
```

All 100 new writes hit shard 3 under range sharding; hashing spreads them. Pick the shard key for **even load** and for the queries you run most: a key that does not appear in most queries forces **scatter-gather** (ask every shard).

## 5. Consistent hashing

With `hash(key) % N`, adding a server changes `N`, and **almost every key moves** to a different server (a cache flush, or a huge data migration). **Consistent hashing** places both servers and keys on a circle (a ring of hash values); a key belongs to the first server clockwise from it. Adding or removing a server only moves the keys in the arc next to it. **Virtual nodes** (each server appears at many ring positions) smooth the distribution.

```python
import bisect, hashlib, statistics
from collections import Counter

def h(s: str) -> int:
    return int(hashlib.md5(s.encode()).hexdigest(), 16)

class Ring:
    def __init__(self, nodes=(), vnodes=100):
        self.vnodes, self.points, self.owner = vnodes, [], {}
        for node in nodes:
            self.add(node)

    def add(self, node):
        for i in range(self.vnodes):               # one server = many points on the ring
            p = h(f"{node}#{i}")
            bisect.insort(self.points, p)
            self.owner[p] = node

    def remove(self, node):
        for i in range(self.vnodes):
            p = h(f"{node}#{i}")
            self.points.remove(p)
            del self.owner[p]

    def lookup(self, key):
        i = bisect.bisect(self.points, h(key)) % len(self.points)    # first point clockwise (wrap around)
        return self.owner[self.points[i]]

keys = [f"user:{i}" for i in range(10_000)]

for vnodes in (1, 100):
    ring = Ring(["A", "B", "C", "D"], vnodes)
    counts = Counter(ring.lookup(k) for k in keys)
    spread = statistics.pstdev(counts.values()) / (len(keys) / 4)    # relative standard deviation: 0 = perfectly even
    print(f"vnodes={vnodes:<3} {sorted(counts.items())}  imbalance={spread:.2f}")
# vnodes=1   [('A', 309), ('B', 124), ('C', 4077), ('D', 5490)]  imbalance=0.94
# vnodes=100 [('A', 2577), ('B', 2466), ('C', 2509), ('D', 2448)]  imbalance=0.02

ring = Ring(["A", "B", "C", "D"], 100)
before = {k: ring.lookup(k) for k in keys}
ring.add("E")                                                        # add a fifth server
moved = sum(before[k] != ring.lookup(k) for k in keys) / len(keys)
mod_moved = sum(h(k) % 4 != h(k) % 5 for k in keys) / len(keys)      # the naive scheme, 4 -> 5 servers
print(f"adding a server moves {moved:.0%} of keys with consistent hashing, {mod_moved:.0%} with hash % N")
# adding a server moves 19% of keys with consistent hashing, 80% with hash % N
```

One virtual node per server gives a wildly uneven split (one server holds 55 percent of the keys, another 1 percent); 100 virtual nodes balance it to within about 2 percent. And adding the fifth server moves about `1/5 = 20%` of the keys, the theoretical minimum, instead of 80 percent. Dynamo, Cassandra, memcached clients and many load balancers use this idea. (Alternatives: a **directory** service that maps key ranges to shards, as in HBase and many managed databases, or a fixed large number of **logical partitions** that are reassigned among servers, as in Kafka and Elasticsearch.)

## 6. Operating a sharded system

- **Rebalancing:** move partitions to new servers gradually, throttled, keeping the old copy serving until the new one is complete.
- **Hot keys:** one celebrity user or one trending item overloads one shard regardless of hashing. Remedies: cache, split the key (`user:42#0..9`), or dedicate a shard.
- **Cross-shard operations:** joins and transactions across shards need scatter-gather or distributed transactions ([sagas and two-phase commit](../transactions/01-idempotency-retries-and-sagas.md)); design so that most operations touch one shard.
- **Resharding in advance:** pick more logical shards than servers (for example 256 logical shards on 4 servers) so growth means moving whole shards, not splitting data.
- **Secondary indexes** are per shard (fast to write, scatter to read) or global (one consistent index, slower writes).

## 7. Common mistakes

- Sharding too early: replication and a bigger machine (**vertical scaling**) are simpler and often enough.
- Choosing a shard key with a **hot spot** (monotonic ids or timestamps with range sharding, low-cardinality values like country).
- Reading from a replica right after writing, then being surprised by stale data.
- Using Python's built-in `hash()` for sharding: it is randomised per process for strings.
- Assuming `R + W > N` means linearizable reads under all failures.
- Forgetting that replication is **not a backup**: a bad `DELETE` replicates instantly.
- Using `hash % N` for caches: every server added or lost empties most of the cache.

## 8. Two real-world examples

**Example 1: The social network's read replicas.** A site had one primary database and ten read replicas. Profile edits appeared to "revert" for users because the next request went to a lagging replica. The team added "read your writes": after a user writes, their reads go to the primary for 10 seconds (or until their replica's log position passes the write's position).

**Example 2: The cache that melted.** A cache tier used `key % N`. When one cache node was added, 80 percent of keys moved at once, the cache hit rate collapsed and the database behind it was overwhelmed. Switching to consistent hashing meant adding a node displaced only its share of keys, and the database never noticed.

## 9. Practice

1. In the leader/follower demo, make `f2` catch up fully and print `f2.data`. What invariant makes this safe even if `catch_up` is called repeatedly?
2. For `N=7`, which `(W, R)` pairs with `W + R = 8` are valid quorums, and which gives the fastest reads?
3. Add `remove("B")` to the ring and measure how many keys move; confirm they all move to the remaining nodes and that no key moves between untouched nodes.
4. Why does a range-sharded table keyed by timestamp create a hot spot, and how would you fix it without losing time-range queries?
5. Design a `read_your_writes` helper: a client records the log position of its last write and only reads from a follower whose `applied` is at least that.
6. A dataset is 20 TB and receives 50,000 writes/s. One machine handles 5 TB and 10,000 writes/s. How many shards at minimum, and why add replicas as well?

<details>
<summary>Solutions</summary>

1. ```python
   f2.catch_up()
   print(f2.data, f2.lag)
   # {'name': 'Ada Lovelace', 'city': 'London'} 0
   ```
   Each follower remembers how many log entries it has applied (`applied`), so replays never repeat or skip entries; calling `catch_up` again does nothing once lag is 0.
2. ```python
   n = 7
   print([(8 - r, r) for r in range(1, 8)])
   # [(7, 1), (6, 2), (5, 3), (4, 4), (3, 5), (2, 6), (1, 7)]
   ```
   All satisfy `W + R > 7`. `W=7, R=1` gives the fastest reads (but any down replica stops writes).
3. ```python
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
5. ```python
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

## 10. Check yourself

1. What is the difference between replication and sharding?
2. What is replication lag, and name one anomaly it causes and a fix.
3. State the quorum condition and why overlap guarantees a fresh read.
4. Why is `hash(key) % N` a bad scheme when servers are added?
5. What do virtual nodes do in consistent hashing?
6. Compare range and hash sharding.
7. Why is replication not a backup?

<details>
<summary>Answers</summary>

1. Replication copies the same data to several machines (availability, read scale); sharding splits the data across machines (storage and write scale).
2. Followers apply the leader's log after a delay, so reads can be stale. Read-your-writes violations are fixed by reading recent writes from the leader or an up-to-date follower.
3. `R + W > N`: any read set and any write set share at least one replica, so the read sees the newest acknowledged version among its responses.
4. Changing `N` remaps almost every key (about `N/(N+1)` of them), causing mass data movement or a cache flush.
5. They give each server many positions on the ring, which evens out the load and lets a new server take small slices from many neighbours.
6. Range sharding supports range scans but can create hot spots; hash sharding spreads load evenly but makes range queries scatter to all shards.
7. Deletes and corruptions are replicated too, so every copy loses the data; backups are separate, versioned snapshots.

</details>

[Back to Distributed Systems](../README.md)
