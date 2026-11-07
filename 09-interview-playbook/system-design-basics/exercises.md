# System Design Basics: Exercises

The helpers from the lesson (`qps`, `storage`, `human_bytes`, `servers_needed`, `bandwidth_mbps`, `LRUCache`, `TokenBucket`, `Snowflake`, `base62_encode`, `series`, `parallel`) are available.

## Estimation

1. A photo app has 50 million DAU; each user uploads 0.5 photos per day (2 MB each) and views 40 photos per day (200 KB thumbnails). Estimate upload QPS, view QPS, daily and 5-year storage (with 3 replicas), and peak egress bandwidth (peak = 3x average).
2. A service must achieve 99.95% availability. What is the maximum downtime per month? If it depends on three serial components of 99.99% each, does it meet the target? What if you replicate the weakest one (99.9%) twice?
3. A chat app has 10 million concurrent WebSocket connections. If one gateway server handles 100,000 connections, how many servers (with 50% headroom)? Memory per connection is 20 KB: total RAM for connections?

## Building blocks (code)

4. Implement `SlidingWindowRateLimiter(limit, window_seconds, clock)` allowing `limit` requests per rolling window per user. Test it with a fake clock.
5. Add **TTL** support to `LRUCache` (entries expire after N seconds, with an injectable clock).
6. Implement a **consistent-hash ring** with virtual nodes and show that adding a fourth server moves roughly a quarter of the keys.
7. Write a Bloom filter (`add`, `might_contain`) using k hash functions over a bit array; measure its false-positive rate for 1,000 items.

## Design prompts (write the outline: requirements, estimates, API, data model, architecture, deep dive, trade-offs)

8. Design a **rate limiter** service used by many API servers.
9. Design a **notification system** (email/SMS/push) that never double-sends.
10. Design **Pastebin** (store text snippets with expiry, up to 10 MB).
11. Design a **key-value store** (put/get/delete) that scales horizontally and survives node failures.

<details>
<summary>Solutions</summary>

**1.**
```python
dau = 50_000_000
uploads_day, views_day = dau * 0.5, dau * 40
up_avg, up_peak = qps(uploads_day, peak_factor=3)
view_avg, view_peak = qps(views_day, peak_factor=3)
daily_upload_bytes = uploads_day * 2_000_000
print(up_avg, up_peak, view_avg, view_peak)                              # 289 868 23148 69444
print(human_bytes(daily_upload_bytes), human_bytes(storage(uploads_day, 2_000_000, years=5)))   # 50.0 TB 273.8 PB
print(round(bandwidth_mbps(view_peak, 200_000)))                          # 111110  (about 111 Gbps of thumbnails at peak: needs a CDN)
```
Conclusions: uploads are modest in QPS but enormous in storage (hundreds of PB over 5 years: object storage with tiering and compression), views are 80x more frequent and need a **CDN and caching**; 111 Gbps cannot come from one origin.

**2.**
```python
month_seconds = 30 * 24 * 3600
print(round((1 - 0.9995) * month_seconds / 60, 1), "minutes per month allowed")      # 21.6
chain = series(0.9999, 0.9999, 0.9999)
print(round(chain, 5), chain >= 0.9995)                                              # 0.9997 True
weak = series(0.9999, 0.9999, parallel(0.999, 0.999))
print(round(weak, 6), weak >= 0.9995)                                                # 0.999799 True
```
Three 99.99% components in series give about 99.97%, which meets 99.95%. The question is more interesting with a 99.9% component: `series(0.9999, 0.9999, 0.999)` is about 99.88% (fails), and replicating that component twice (`parallel`) lifts the chain back above target.

**3.**
```python
import math
print(servers_needed(10_000_000, 100_000, headroom=0.5))                  # 200
print(human_bytes(10_000_000 * 20_000))                                   # 200.0 GB of connection state across the fleet
```
About 200 gateway servers (1 GB of connection memory each), plus the routing store that maps users to gateways.

**4.**
```python
from collections import defaultdict, deque

class SlidingWindowRateLimiter:
    def __init__(self, limit, window_seconds, clock):
        self.limit, self.window, self.clock = limit, window_seconds, clock
        self.hits = defaultdict(deque)
    def allow(self, user):
        now, q = self.clock(), self.hits[user]
        while q and q[0] <= now - self.window:
            q.popleft()                                                   # forget requests outside the window
        if len(q) < self.limit:
            q.append(now)
            return True
        return False

t = [0.0]
rl = SlidingWindowRateLimiter(3, 10, clock=lambda: t[0])
print([rl.allow("u") for _ in range(4)])                                  # [True, True, True, False]
t[0] = 10.5
print(rl.allow("u"), rl.allow("other"))                                   # True True
```
(In a distributed setup the counters live in Redis, using a sorted set per user or an atomic Lua script, so all API servers share one view.)

**5.**
```python
class TTLCache(LRUCache):
    def __init__(self, capacity, ttl, clock):
        super().__init__(capacity)
        self.ttl, self.clock = ttl, clock
    def put(self, key, value):
        super().put(key, (value, self.clock() + self.ttl))
    def get(self, key):
        entry = super().get(key)
        if entry is None:
            return None
        value, expires = entry
        if self.clock() >= expires:
            self.data.pop(key, None)                                      # lazily delete expired entries
            return None
        return value

now = [0]
tc = TTLCache(10, ttl=5, clock=lambda: now[0])
tc.put("k", "v")
print(tc.get("k")); now[0] = 6; print(tc.get("k"))                        # v None
```

**6.**
```python
import bisect, hashlib

def h(value):
    return int(hashlib.md5(value.encode()).hexdigest(), 16)

class Ring:
    def __init__(self, nodes, vnodes=100):
        self.ring = sorted((h(f"{n}#{i}"), n) for n in nodes for i in range(vnodes))
    def get(self, key):
        return self.ring[bisect.bisect(self.ring, (h(key), "")) % len(self.ring)][1]

keys = [f"user{i}" for i in range(10_000)]
before, after = Ring(["a", "b", "c"]), Ring(["a", "b", "c", "d"])
moved = sum(before.get(k) != after.get(k) for k in keys)
print(moved, 0.15 < moved / len(keys) < 0.35)                             # 2179 True   (about 1/4, not 3/4)
```

**7.**
```python
import hashlib

class BloomFilter:
    def __init__(self, size_bits=10_000, hashes=5):
        self.size, self.k, self.bits = size_bits, hashes, bytearray(size_bits)
    def _positions(self, item):
        for i in range(self.k):
            yield int(hashlib.sha256(f"{i}:{item}".encode()).hexdigest(), 16) % self.size
    def add(self, item):
        for p in self._positions(item):
            self.bits[p] = 1
    def might_contain(self, item):
        return all(self.bits[p] for p in self._positions(item))

bf = BloomFilter()
for i in range(1000):
    bf.add(f"in-{i}")
assert all(bf.might_contain(f"in-{i}") for i in range(1000))             # never a false negative
false_positives = sum(bf.might_contain(f"out-{i}") for i in range(5000)) / 5000
print(false_positives < 0.05)                                            # True  (about 1% with these parameters)
```
Use: "definitely not present" answers avoid expensive lookups (for example blocking scans for non-existent short codes).

**8. Rate limiter service (outline).** *Requirements:* limit by user/API key/IP, low latency (adds under 5 ms), accurate enough, must not take the API down if it fails, configurable rules. *Estimate:* 100,000 checks/s. *Algorithm:* token bucket (bursts) or sliding window counter. *Architecture:* middleware in the gateway calls Redis (one key per `user:rule`) with an atomic Lua script (`GET`, compute, `SET` with TTL); local in-memory counters with periodic sync for ultra-low latency. *Failure mode:* if Redis is down, **fail open** (allow) for normal traffic and **fail closed** for abusive endpoints; respond `429` with `Retry-After`. *Scale:* shard Redis by key; avoid hot keys with per-node sub-limits. *Trade-offs:* accuracy versus latency; per-region versus global limits; a small over-limit leak is acceptable.

**9. Notification system (outline).** API accepts events; a **queue** (partitioned) decouples producers; workers render templates and call providers (email/SMS/push). *Never double-send:* idempotency key per `(event, user, channel)` stored in a database with a unique constraint; worker checks/inserts before sending; at-least-once delivery plus dedup gives effectively-once. Retries with exponential backoff and jitter; provider failover; dead-letter queue and alerts; per-user preferences and quiet hours; per-provider token-bucket rate limits; priority queues (OTP before marketing); delivery status callbacks stored for audit; scale workers horizontally.

**10. Pastebin (outline).** *Requirements:* create/read text snippets, optional expiry, 10 MB max, 1M new pastes/day, 10:1 reads. *Estimates:* about 12 writes/s, 120 reads/s average; 1M x 10 KB average = 10 GB/day (3.6 TB/year): store **content in object storage** (S3), **metadata** (id, owner, created, expires, size, S3 key) in a database. *ID:* base62 of a unique counter or random 8-char key. *Read path:* CDN -> app -> cache (hot pastes) -> metadata DB -> object store. *Expiry:* TTL field and a cleanup job (plus lazy check on read). *Deep dive:* abuse prevention (rate limits, size limits, malware scanning), private/unlisted pastes with signed URLs, syntax highlighting done client-side, compression of stored text.

**11. Key-value store (outline).** *API:* `put(key, value)`, `get(key)`, `delete(key)`. *Partitioning:* consistent hashing with virtual nodes. *Replication:* each key stored on N=3 successor nodes; **quorum** reads and writes (W + R > N) give tunable consistency; *failure handling:* sloppy quorum and **hinted handoff** for temporary failures, **read repair** and **anti-entropy (Merkle trees)** to heal replicas, **gossip** for membership and failure detection; *conflicts:* vector clocks or last-write-wins; *storage engine:* write-ahead log + memtable + SSTables (LSM tree) with compaction, Bloom filters to skip files; *trade-offs:* CAP (AP-leaning with tunable quorums), latency versus consistency, compaction costs. (This is the Dynamo/Cassandra design.)

</details>

[Lesson](README.md) · [Summary](summary.md)
