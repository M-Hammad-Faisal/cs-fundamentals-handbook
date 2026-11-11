# System Design Basics

## 1. The concept

A **system design interview** asks: "Design Twitter / a URL shortener / a chat app." There is no single right answer. The interviewer evaluates how you **clarify requirements, estimate scale, choose components, reason about trade-offs, and communicate**. Real engineers do the same work when they plan a feature that must serve a million users.

This chapter gives you:
1. a **repeatable framework**,
2. **back-of-the-envelope estimation** skills (with runnable helpers),
3. the **building blocks** and the trade-offs of each,
4. **worked designs** of classic problems with working mini-implementations.

**Continue with:** [part 2, five more designs](02-five-more-designs.md) (rate limiter, notification service, payment ledger, autocomplete, file storage), [part 3, caching failure modes and reliability](03-caching-failure-modes-and-reliability.md), and the [distributed systems](../../11-distributed-systems/README.md) track for the theory behind replication, consensus and sagas.

It builds on [networking](../../07-networking/tcp-ip-osi/README.md), [databases](../../05-databases/nosql/README.md) and [operating-systems concurrency](../../06-operating-systems/concurrency-deadlocks/README.md); revise those links when a term is new.

## 2. A framework for any design question (about 45 minutes)

| Step | Minutes | What to do |
|------|---------|-----------|
| 1. **Clarify requirements** | 5 | Functional ("what does it do?") and non-functional (scale, latency, availability, consistency, durability). Ask who the users are and what is out of scope. |
| 2. **Estimate scale** | 5 | Users, requests per second (QPS), storage per year, bandwidth, read/write ratio. |
| 3. **Define the API and data model** | 5 | The few key endpoints; the main entities and their relations; access patterns. |
| 4. **Draw the high-level design** | 10 | Clients, load balancer, services, database, cache, queue, CDN. Walk one request end to end. |
| 5. **Deep dive** | 15 | Pick the 1-2 hardest parts (data partitioning, feed generation, hot keys) and go deep. |
| 6. **Bottlenecks and trade-offs** | 5 | Single points of failure, scaling limits, consistency vs availability, monitoring, what you would do with more time. |

**Say the trade-offs out loud**: "I will use eventual consistency for the feed because availability matters more than a few seconds of staleness; but payments use strong consistency."

### Questions to ask in step 1

- Functional: What are the core features (MVP)? Read-heavy or write-heavy? Real time or batch? Public or private data? Search? Analytics?
- Scale: How many daily active users? Peak QPS? Data size and retention? Growth rate?
- Quality: Latency target (p99)? Availability target (99.9% vs 99.99%)? Is losing data acceptable? Is stale data acceptable?
- Constraints: Regions/compliance? Mobile or web? Existing systems to integrate with?

## 3. Back-of-the-envelope estimation

You do not need exact numbers; you need the **right order of magnitude**, to decide whether one server or a thousand are required.

### Numbers every engineer should know

| Operation | Approximate time |
|-----------|------------------|
| CPU L1 cache reference | 1 ns |
| Main memory reference | 100 ns |
| Read 1 MB sequentially from memory | 10-50 microseconds |
| SSD random read | 100 microseconds |
| Read 1 MB sequentially from SSD | 0.2-1 ms |
| Network round trip within a data center | 0.5 ms |
| HDD seek | 5-10 ms |
| Cross-continent round trip | 100-150 ms |

| Unit | Value |
|------|-------|
| 1 day | about 86,400 s (round to 100,000 s) |
| 1 month | about 2.5 million s |
| 1 year | about 31.5 million s (round to 30 million) |
| 1 KB / 1 MB / 1 GB / 1 TB / 1 PB | 10^3 / 10^6 / 10^9 / 10^12 / 10^15 bytes |
| A character (ASCII) / a long ID / a small JSON record | 1 B / 8 B / 0.2-2 KB |

Rules of thumb: memory is about 100x faster than SSD, SSD about 100x faster than disk, a data-center round trip about 1,000x faster than a transatlantic one. **Cache before you cross the network; avoid cross-region calls on the hot path.**

### A small estimation toolkit

```python
def qps(requests_per_day, peak_factor=2):
    """Average and peak requests per second."""
    average = requests_per_day / 86_400
    return round(average), round(average * peak_factor)

def storage(records_per_day, bytes_per_record, years=1, replication=3):
    """Raw bytes for N years, including replicas."""
    return records_per_day * bytes_per_record * 365 * years * replication

def human_bytes(n):
    for unit in ("B", "KB", "MB", "GB", "TB", "PB"):
        if n < 1000:
            return f"{n:.1f} {unit}"
        n /= 1000
    return f"{n:.1f} EB"

def servers_needed(peak_qps, qps_per_server, headroom=0.5):
    """Servers so that each runs at most `headroom` of its capacity (spare room for failures/spikes)."""
    import math
    return math.ceil(peak_qps / (qps_per_server * headroom))

def bandwidth_mbps(qps_value, bytes_per_response):
    return qps_value * bytes_per_response * 8 / 1_000_000

# Example: a URL shortener with 100 million new URLs per month and a 100:1 read-to-write ratio
writes_per_day = 100_000_000 / 30
avg_w, peak_w = qps(writes_per_day)
avg_r, peak_r = qps(writes_per_day * 100)
print("writes/s avg, peak:", avg_w, peak_w)                       # 39 77
print("reads/s  avg, peak:", avg_r, peak_r)                       # 3858 7716
print("5-year storage (500 B per record, 3 replicas):", human_bytes(storage(writes_per_day, 500, years=5)))   # 9.1 TB
print("app servers at 2,000 QPS each:", servers_needed(peak_r, 2000))     # 8
print("egress at peak for 1 KB responses (Mbps):", round(bandwidth_mbps(peak_r, 1000)))   # 62
```

The conclusion ("a handful of servers, about 9 TB, a read-heavy cache-friendly workload") immediately shapes the design: **cache reads, a single sharded database is enough, no exotic technology is needed**.

### Availability: "the nines"

```python
def downtime_per_year(availability_percent):
    seconds = (1 - availability_percent / 100) * 365 * 24 * 3600
    if seconds >= 3600:
        return f"{seconds / 3600:.1f} hours"
    if seconds >= 60:
        return f"{seconds / 60:.1f} minutes"
    return f"{seconds:.1f} seconds"

for a in (99, 99.9, 99.99, 99.999):
    print(a, "->", downtime_per_year(a))
# 99 -> 87.6 hours | 99.9 -> 8.8 hours | 99.99 -> 52.6 minutes | 99.999 -> 5.3 minutes

# Components in series multiply; redundancy in parallel multiplies the failure probabilities
def series(*avail): 
    out = 1.0
    for a in avail: out *= a
    return out
def parallel(*avail):
    fail = 1.0
    for a in avail: fail *= (1 - a)
    return 1 - fail
print(round(series(0.999, 0.999, 0.999), 4), round(parallel(0.99, 0.99), 4))        # 0.997 0.9999
```

Each extra nine costs far more. Three 99.9% services in a chain give only 99.7%; two redundant 99% replicas give 99.99%. That is why we remove single points of failure with **redundancy** (two or more of everything critical).

## 4. Building blocks and their trade-offs

### Load balancer (see [load balancing](../../07-networking/load-balancing-cdn/README.md))
Spreads requests over stateless servers, health-checks them, terminates TLS. L4 for speed, L7 for routing by path/header. Keep services **stateless** so any instance can serve any request; store sessions in a shared store or a signed token.

### Caching
Keep hot data in memory (Redis, Memcached, local process memory, CDN). Typical order: browser, CDN, reverse proxy, application cache, database cache.

| Strategy | How | Good for | Risk |
|----------|-----|----------|------|
| **Cache-aside** | App checks cache; on miss reads the DB and fills the cache | Read-heavy, general | Stale data until TTL/invalidation; cold start stampede |
| **Read-through** | Cache loads from DB itself | Simple clients | Same staleness |
| **Write-through** | Write to cache and DB together | Reads must be fresh | Slower writes |
| **Write-back** | Write to cache; flush to DB later | Write-heavy, tolerates loss | Data loss on crash |
| **Write-around** | Write to DB only; cache fills on read | Data rarely re-read | First read is slow |

**Eviction:** LRU (least recently used) is the default; LFU, FIFO and TTL exist too. **Hard problems:** invalidation (when to drop stale data), **cache stampede** (many requests miss at once: use locks, request coalescing, jittered TTLs), **hot keys**.

```python
from collections import OrderedDict

class LRUCache:
    """O(1) get and put with a hash map + doubly linked list (OrderedDict gives both)."""
    def __init__(self, capacity):
        self.capacity, self.data = capacity, OrderedDict()
    def get(self, key):
        if key not in self.data:
            return None
        self.data.move_to_end(key)                        # mark as most recently used
        return self.data[key]
    def put(self, key, value):
        self.data[key] = value
        self.data.move_to_end(key)
        if len(self.data) > self.capacity:
            self.data.popitem(last=False)                 # evict the least recently used

cache = LRUCache(2)
cache.put("a", 1); cache.put("b", 2); cache.get("a"); cache.put("c", 3)      # "b" is evicted
print(cache.get("b"), cache.get("a"), cache.get("c"))                         # None 1 3

# cache-aside in code
calls = []
def load_user(user_id, cache, db):
    user = cache.get(user_id)
    if user is None:                                      # miss: go to the database, then fill the cache
        calls.append(user_id)
        user = db[user_id]
        cache.put(user_id, user)
    return user

db, c = {1: "ana", 2: "bo"}, LRUCache(10)
load_user(1, c, db); load_user(1, c, db); load_user(2, c, db)
print(calls)                                                                  # [1, 2]   (user 1 hit the DB only once)
```

### Databases (see [databases](../../05-databases/relational-sql/README.md))
- **SQL (PostgreSQL, MySQL):** relations, joins, transactions, strong consistency; scales vertically first, then with read replicas and sharding.
- **NoSQL:** key-value (Redis, DynamoDB), document (MongoDB), wide-column (Cassandra), graph (Neo4j); horizontal scale, flexible schema, designed-for-access-patterns.
- **Replication:** leader-follower (read scaling, failover), multi-leader, leaderless (quorums).
- **Sharding (partitioning):** split data by key; range (hot spots), hash (even), consistent hashing (smooth resizing); cross-shard joins and transactions become hard; choose the **shard key** carefully (high cardinality, even load, matches access pattern).
- **Indexes** speed reads but slow writes; choose them from your queries ([indexes](../../05-databases/indexes-query-plans/README.md)).
- **Default advice:** start with PostgreSQL; add specialized stores for proven needs.

### Message queues and streams
Kafka, RabbitMQ, SQS decouple producers from consumers: absorb spikes, enable **async processing** (send email, resize image), retries, fan-out, event sourcing. Trade-offs: eventual consistency, ordering (per partition), at-least-once delivery (make consumers **idempotent**), monitoring lag, poison messages (dead-letter queues).

### CDN and object storage
Static assets and media go to **object storage** (S3) fronted by a **CDN** (see [CDNs](../../07-networking/load-balancing-cdn/README.md)); databases store only metadata and URLs.

### Rate limiting and protection
Protects services from abuse and overload (see the [token bucket](../../07-networking/load-balancing-cdn/README.md)); enforced at the gateway with counters in Redis.

```python
import time

class TokenBucket:
    """Allows bursts up to `capacity` and an average of `rate` requests per second."""
    def __init__(self, rate, capacity, clock=time.monotonic):
        self.rate, self.capacity, self.clock = rate, capacity, clock
        self.tokens, self.updated = capacity, clock()
    def allow(self):
        now = self.clock()
        self.tokens = min(self.capacity, self.tokens + (now - self.updated) * self.rate)
        self.updated = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False

fake_time = [0.0]
bucket = TokenBucket(rate=2, capacity=3, clock=lambda: fake_time[0])
print([bucket.allow() for _ in range(5)])                 # [True, True, True, False, False]   (burst of 3, then limited)
fake_time[0] = 1.0                                        # one second later: 2 tokens refilled
print([bucket.allow() for _ in range(3)])                 # [True, True, False]
```

### Unique ID generation
Auto-increment IDs do not work across shards and leak volume. Options: **UUIDs** (random, 128-bit, not sortable), **Snowflake-style** IDs (timestamp + machine id + sequence: unique, roughly time-ordered, 64-bit), database ticket servers.

```python
import time

class Snowflake:
    """64-bit style id: [timestamp ms | machine id (10 bits) | sequence (12 bits)]."""
    EPOCH = 1_700_000_000_000
    def __init__(self, machine_id, clock_ms=lambda: int(time.time() * 1000)):
        assert 0 <= machine_id < 1024
        self.machine_id, self.clock_ms = machine_id, clock_ms
        self.last_ms, self.sequence = -1, 0
    def next_id(self):
        now = self.clock_ms()
        if now == self.last_ms:
            self.sequence = (self.sequence + 1) & 0xFFF           # up to 4096 ids per millisecond per machine
            if self.sequence == 0:
                while now <= self.last_ms:                        # sequence exhausted: wait for the next ms
                    now = self.clock_ms()
        else:
            self.sequence = 0
        self.last_ms = now
        return ((now - self.EPOCH) << 22) | (self.machine_id << 12) | self.sequence

gen = Snowflake(machine_id=7, clock_ms=lambda: 1_700_000_005_000)
ids = [gen.next_id() for _ in range(3)]
print(ids[1] - ids[0], ids == sorted(set(ids)))                   # 1 True   (unique and increasing)
print((ids[0] >> 12) & 0x3FF)                                     # 7        (the machine id is recoverable)
```

### Pagination and API design
Use **cursor-based pagination** (`?after=<last_id>&limit=50`) for large or changing lists; offset pagination (`?page=1000`) gets slower and skips/duplicates items when data changes. Make writes **idempotent** (idempotency keys), version your API, and return consistent errors ([HTTP](../../07-networking/dns-http/README.md)).

## 5. Scalability principles

1. **Scale out, not just up:** many stateless servers behind a balancer beat one giant machine (and survive failures).
2. **Cache aggressively** at every layer; measure hit ratios.
3. **Push work off the request path:** queue slow jobs, respond fast.
4. **Partition data** so no machine holds or serves everything; avoid hot keys.
5. **Replicate for availability and read scale;** accept replication lag (eventual consistency) where the product allows.
6. **Design for failure:** timeouts, retries with backoff and jitter, circuit breakers, graceful degradation, health checks, multi-zone deployment.
7. **Denormalize deliberately** for read speed; accept write complexity.
8. **Observe everything:** metrics (rate, errors, duration), logs, traces, alerts; define **SLIs/SLOs** (for example 99.9% of requests under 300 ms).
9. **Keep it simple:** start with the simplest design that meets the numbers, then evolve. A monolith with a database and a cache serves a great deal of traffic.

### Consistency vs availability (CAP in practice)
During a network partition choose consistency (reject some requests, for money, inventory, uniqueness) or availability (serve possibly stale data, for feeds, likes, counters). Without a partition the trade is **latency versus consistency** (PACELC). Say which parts of your design need which, and why. See [NoSQL](../../05-databases/nosql/README.md).

## 6. Worked design 1: a URL shortener

**Requirements.** Create a short link for a long URL; redirect quickly; links last 5 years; analytics optional. 100M new links per month, 100:1 reads to writes; availability matters more than strict consistency; redirect latency under 50 ms.

**Estimates** (from the toolkit above): about 40 writes/s and 4,000 reads/s average (8,000 at peak); about 9 TB over 5 years including replicas. This is **read-heavy and small**: a cache will absorb most reads.

**API.** `POST /links {long_url, custom_alias?, ttl?}` returns `{short_url}`; `GET /{code}` returns **301/302** redirect (302 if you must count every click, since browsers cache 301s).

**Data model.** `links(code PRIMARY KEY, long_url, created_at, expires_at, user_id)`. Lookup is always by `code`: a key-value access pattern, so a sharded SQL table or a key-value store works.

**Generating the code.** Use 7 characters of base62 (`a-zA-Z0-9`): 62^7 is about 3.5 trillion codes, enough for decades. Options: (1) **counter + base62 encoding** (unique, no collisions, but predictable; allocate counter ranges per server to avoid a single bottleneck); (2) **hash of the URL** truncated to 7 chars (collisions need handling); (3) random codes with a uniqueness check.

```python
import string

ALPHABET = string.digits + string.ascii_lowercase + string.ascii_uppercase      # 62 characters

def base62_encode(n):
    if n == 0:
        return ALPHABET[0]
    chars = []
    while n:
        n, r = divmod(n, 62)
        chars.append(ALPHABET[r])
    return "".join(reversed(chars))

def base62_decode(code):
    n = 0
    for ch in code:
        n = n * 62 + ALPHABET.index(ch)
    return n

print(base62_encode(125), base62_encode(62**7 - 1), base62_decode(base62_encode(987654321)))
# 21 ZZZZZZZ 987654321

class UrlShortener:
    def __init__(self, start=1_000_000):
        self.counter, self.by_code, self.by_url = start, {}, {}
    def shorten(self, long_url):
        if long_url in self.by_url:                                   # idempotent: same URL, same code
            return self.by_url[long_url]
        self.counter += 1
        code = base62_encode(self.counter)
        self.by_code[code], self.by_url[long_url] = long_url, code
        return code
    def resolve(self, code):
        return self.by_code.get(code)

s = UrlShortener()
code = s.shorten("https://example.com/a/very/long/path?x=1")
print(code, s.resolve(code), s.shorten("https://example.com/a/very/long/path?x=1") == code, s.resolve("nope"))
# 4c93 https://example.com/a/very/long/path?x=1 True None
```

**High-level design.**

```text
Client -> CDN/edge -> Load balancer -> Stateless app servers -> Cache (Redis, cache-aside by code)
                                                     |                    | miss
                                                     |                    v
                                                     +--------------> Database (sharded by code hash, replicated)
                          Counter/ID service (ranges per server) ; analytics events -> queue -> stream processor
```

**Deep dive and trade-offs.** Cache the hottest codes (LRU, high hit ratio because of skew); shard by hash of `code`; replicate for availability; expire old links with a background job; protect creation with **rate limiting**; add a Bloom filter or cache for non-existent codes to blunt scans; use 302 and a click-event queue if analytics matter; custom aliases require a uniqueness check (unique index); abuse/malware scanning is a separate pipeline. **Consistency:** a short delay before a new link works everywhere is acceptable.

## 7. Worked design 2: a news feed (fan-out)

**Requirements.** Users follow others and see a ranked, recent feed. 100M DAU; reads dominate; feed freshness within seconds is fine; some accounts have 50M followers.

**The core decision: fan-out on write vs fan-out on read.**

| | Fan-out on **write** (push) | Fan-out on **read** (pull) |
|---|------------------------------|-----------------------------|
| Post time | Copy the post id into each follower's feed list | Store once |
| Read time | **Fast**: read the precomputed list | Slow: gather recent posts from everyone you follow, merge |
| Cost | Heavy for celebrities (millions of writes per post) | Heavy per read for users following many people |
| Best for | Normal users | Celebrities |

**Hybrid (what real systems do):** push for normal accounts; **pull for celebrities** at read time and merge with the precomputed feed.

```python
import heapq
from collections import defaultdict

class Feed:
    def __init__(self, celebrity_threshold=3):
        self.followers = defaultdict(set)        # author -> followers
        self.following = defaultdict(set)        # user -> authors
        self.posts = defaultdict(list)           # author -> [(timestamp, post_id)]
        self.feed = defaultdict(list)            # user -> precomputed [(timestamp, post_id)] (push model)
        self.threshold = celebrity_threshold
    def follow(self, user, author):
        self.following[user].add(author); self.followers[author].add(user)
    def is_celebrity(self, author):
        return len(self.followers[author]) >= self.threshold
    def post(self, author, ts, post_id):
        self.posts[author].append((ts, post_id))
        if not self.is_celebrity(author):        # fan-out on write for normal accounts
            for f in self.followers[author]:
                self.feed[f].append((ts, post_id))
    def read(self, user, limit=3):
        items = list(self.feed[user])            # precomputed items
        for a in self.following[user]:           # pull celebrities at read time
            if self.is_celebrity(a):
                items.extend(self.posts[a])
        return [pid for _, pid in heapq.nlargest(limit, items)]       # newest first

f = Feed()
for u in ("u1", "u2", "u3"):
    f.follow(u, "star")                          # "star" has 3 followers: a celebrity
f.follow("u1", "ana")
f.post("ana", 1, "ana-1"); f.post("star", 2, "star-1"); f.post("ana", 3, "ana-2")
print(f.read("u1"), f.read("u2"))                # ['ana-2', 'star-1', 'ana-1'] ['star-1']
```

**Deep dive.** Store feeds as capped lists (last ~800 ids) in Redis; hydrate post bodies from a cache by id; rank with a scoring service (recency + engagement) behind a cache; use a queue to do fan-out asynchronously; shard by user id; handle deletes lazily; monitor fan-out lag.

## 8. Worked design 3: a chat system

**Requirements.** 1:1 and group chat, delivery in order, online presence, history, offline delivery. Millions of concurrent connections.

**Key ideas.**
- **Persistent connections** (WebSocket, or long polling as a fallback) to a pool of **chat gateways**; a service maps user to the gateway holding their connection (kept in a fast store such as Redis).
- **Message flow:** sender -> gateway -> **message service** -> persist (append-only, partitioned by `conversation_id`) -> look up recipients' gateways -> push; if offline, store and send a push notification, then deliver on reconnect.
- **Ordering:** a per-conversation sequence number (assigned by the service/partition owner); clients sort by it and de-duplicate by message id; **delivery semantics** at-least-once + idempotent clients, with ack/read receipts.
- **Storage:** wide-column or key-value store partitioned by `(conversation_id, message_seq)` for fast "latest 50 messages" ([NoSQL](../../05-databases/nosql/README.md)).
- **Groups:** fan-out per member for small groups; for large channels publish to a topic and let members pull.
- **Presence:** heartbeats with TTLs in Redis (`SETEX user:42:online 30`), updated lazily to avoid storms.
- **Scale and failure:** stateless services behind load balancers, gateways drain gracefully on deploy, messages never lost once acknowledged (replicated log).

## 9. A checklist for the final minutes

- **Single points of failure?** Add redundancy and failover.
- **Hot spots?** Hot keys, celebrity users, popular files, one overloaded shard.
- **What if X fails?** Cache down, a shard unavailable, a region out, a queue backed up.
- **Data:** consistency needs per feature, backups, retention, privacy/compliance.
- **Operations:** monitoring, alerts, deployment (blue-green/canary), rollback, capacity planning.
- **Security:** authentication, authorization, TLS, rate limiting, input validation, secrets.
- **Cost:** cheapest design that meets the numbers; where could you simplify?
- **Evolution:** what you would build first (MVP) and what later.

## 10. Two real-world examples

### Example 1: A startup outgrows its single server
A product runs on one app server and one PostgreSQL instance. Traffic grows and pages slow down. A profile shows 80% of requests are reads of the same popular records. The team adds **Redis (cache-aside)** and two more stateless app servers behind a load balancer, moves uploads to **object storage + CDN**, and adds one **read replica** for reports. No microservices, no sharding yet: the estimates (2,000 QPS peak, 300 GB) did not justify them. Latency drops from 900 ms to 120 ms. Each step was taken because numbers said so, not because of fashion.

### Example 2: A notification system that must not double-send
Sending email/SMS/push for orders is moved off the request path into a **queue**. Workers consume at-least-once (a crash causes redelivery), so each message carries an **idempotency key** (`order-123:shipped:email`); the worker records processed keys in a database and skips duplicates. Failures retry with exponential backoff and jitter, poison messages go to a **dead-letter queue** with an alert, and a per-provider **rate limiter** (token bucket) respects the vendor's limits. Customers get exactly one email even through crashes and retries.

## 11. Tips, tricks and pitfalls

- **Drive the conversation:** state assumptions, confirm them, and signal what you are doing ("Next I will estimate the load").
- **Start simple** and add complexity only when numbers or requirements demand it; explain why each component exists.
- **Quantify**: even rough numbers beat adjectives ("about 8,000 reads per second").
- Do not name-drop technologies without reasons; compare at least two options and pick one with trade-offs.
- Do not forget **failure modes**, **monitoring** and **data consistency**; they separate senior answers from junior ones.
- Cover the **write path and the read path** separately.
- Avoid premature microservices and distributed transactions; prefer one database transaction where you can, sagas/outbox where you must ([transactions](../../05-databases/transactions-acid/README.md)).
- Do not design everything; **go deep** where the problem is hard (partitioning, ordering, hot keys).
- Practice by designing real systems you use (and by reading engineering blogs and post-mortems).
- Draw: boxes and arrows with data flowing; label protocols and storage types.

## 12. Check yourself

1. List the six steps of the framework.
2. Why estimate before drawing the design?
3. About how many seconds are in a day, and what QPS is 100 million requests per day?
4. How does availability change when components are in series versus in parallel?
5. Compare cache-aside, write-through and write-back.
6. Why are auto-increment IDs a problem in a sharded system and what are the alternatives?
7. Offset vs cursor pagination?
8. Explain fan-out on write vs read and the hybrid for celebrities.
9. How do you handle at-least-once message delivery safely?
10. What changes between a design for money transfers and one for a like counter?

<details>
<summary>Answers</summary>

1. Clarify requirements; estimate scale; define API and data model; high-level design; deep dive; bottlenecks and trade-offs.
2. The numbers decide the architecture (one server versus a sharded cluster), prevent over-engineering and expose read/write ratios and storage needs.
3. About 86,400 (round to 100,000). 100M/day is roughly 1,157 QPS on average (about 2,000-3,000 at peak).
4. In series availabilities multiply (the chain is weaker than any link); in parallel (redundant replicas) the failure probabilities multiply, so availability rises sharply.
5. Cache-aside: the app fills the cache on a miss (simple, may be stale). Write-through: write cache and DB together (fresh reads, slower writes). Write-back: write to cache and flush later (fast writes, risk of losing data).
6. A single counter becomes a bottleneck and collides across shards; use UUIDs, Snowflake-style time-ordered IDs, or per-node ID ranges.
7. Offset (`page=N`) gets slower with depth and shifts when data changes; cursor (`after=<id>`) is stable and efficient for large lists.
8. Write fan-out precomputes every follower's feed on post (fast reads, expensive for huge audiences); read fan-out gathers posts at read time (cheap writes, slow reads). Hybrid: push for ordinary users, pull celebrity posts at read time and merge.
9. Make consumers idempotent (idempotency keys or deduplication), use acknowledgements after processing, retry with backoff, and send poison messages to a dead-letter queue.
10. Money needs strong consistency, transactions and audit trails (reject rather than be wrong); a like counter can be eventually consistent and approximate, favoring availability and speed.

</details>

[Exercises](exercises.md) · [Summary](summary.md)
