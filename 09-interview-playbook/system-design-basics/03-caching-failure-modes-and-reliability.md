# System Design, Part 3: Caching Failure Modes and Designing for Reliability

**Prerequisites:** [System design basics](README.md) (the caching section), [five more designs](02-five-more-designs.md), [observability and SLOs](../../11-distributed-systems/observability/01-observability-logs-metrics-traces-slos.md), [threads and the GIL](../../06-operating-systems/concurrency-deadlocks/README.md). **You will learn:** the ways a cache **fails** (stampede, stale data, penetration, synchronized expiry), how **load shedding and backpressure** keep an overloaded system alive, **Little's law** for capacity planning, how **event sourcing** and **CQRS** work, and a decision guide for **monolith versus microservices**, with runnable demos for each.

## 1. In plain words

A cache makes the common case fast and cheap; reliability work is about what happens when things are **not** common: a hot key expires, a user asks for something that does not exist, traffic doubles, a dependency slows down. Strong designs assume those moments will come and decide in advance what the system does: **fail fast, shed load, serve stale, degrade gracefully**.

## 2. A cache-aside baseline

**Cache-aside** (lazy loading): read from the cache; on a miss, read the database, store the value with a **TTL** (time to live), return it. Writes go to the database and then **invalidate** the cache entry.

```python
class TTLCache:
    def __init__(self, clock):
        self.clock, self.data = clock, {}              # key -> (value, expires_at)
        self.hits = self.misses = 0
    def get(self, key):
        entry = self.data.get(key)
        if entry and entry[1] > self.clock():
            self.hits += 1
            return entry[0]
        self.misses += 1
        return None
    def set(self, key, value, ttl):
        self.data[key] = (value, self.clock() + ttl)
    def delete(self, key):
        self.data.pop(key, None)

now = [0.0]
db = {"user:1": "Ada"}
cache = TTLCache(clock=lambda: now[0])

def read_user(key):
    value = cache.get(key)
    if value is None:                                   # miss: go to the database
        value = db[key]
        cache.set(key, value, ttl=60)
    return value

read_user("user:1"); read_user("user:1")
now[0] = 61                                             # the entry has expired
read_user("user:1")
print("hits:", cache.hits, "misses:", cache.misses)
# hits: 1 misses: 2
```

## 3. Failure 1: the cache stampede (thundering herd)

When a very **hot** key expires, every concurrent request misses at once and they **all** hit the database together, perhaps overloading it. The fix is **single-flight** (request coalescing): the first request loads the value while the others wait for its result.

```python
import threading, time

def run_herd(use_single_flight: bool, n_threads=10):
    db_calls = [0]
    cache = {}
    locks, locks_guard = {}, threading.Lock()

    def slow_db_load(key):
        db_calls[0] += 1
        time.sleep(0.2)                                  # an expensive query
        return f"value-of-{key}"

    def get(key):
        if key in cache:
            return cache[key]
        if not use_single_flight:
            cache[key] = slow_db_load(key)               # everybody who misses loads it
            return cache[key]
        with locks_guard:
            lock = locks.setdefault(key, threading.Lock())
        with lock:                                       # only one thread loads; the rest wait here...
            if key not in cache:                         # ...then find the value already cached (double-checked)
                cache[key] = slow_db_load(key)
        return cache[key]

    barrier = threading.Barrier(n_threads)
    def worker():
        barrier.wait()                                   # release all threads at the same instant
        get("hot-key")
    threads = [threading.Thread(target=worker) for _ in range(n_threads)]
    for t in threads: t.start()
    for t in threads: t.join()
    return db_calls[0]

print("without single-flight:", run_herd(False), "database calls for one key")
print("with single-flight   :", run_herd(True), "database call")
# without single-flight: 10 database calls for one key
# with single-flight   : 1 database call
```

Other defences: **stale-while-revalidate** (serve the expired value while one worker refreshes it in the background), **early refresh** (refresh a little before the TTL ends), and **pre-warming** hot keys after a deploy. Even a "simple" restart with a cold cache can topple a database; plan for it.

## 4. Failure 2: synchronized expiry (the avalanche)

If you load 1,000 keys at the same moment with the same TTL, they all expire at the same moment. **Add random jitter** to the TTL:

```python
import random
from collections import Counter

rng = random.Random(42)
keys = 1000
same = Counter(60 for _ in range(keys))                                   # every key expires 60 s after load
jittered = Counter(int(60 + rng.uniform(0, 12)) for _ in range(keys))      # 60 to 72 s
print("most keys expiring in the same second, fixed TTL   :", max(same.values()))
print("most keys expiring in the same second, jittered TTL:", max(jittered.values()))
# most keys expiring in the same second, fixed TTL   : 1000
# most keys expiring in the same second, jittered TTL: 91
```

The load on the database is a spike of 1,000 at one instant versus a spread of about 83 per second on average (at most 91 in the busiest second).

## 5. Failure 3: stale data from races

Cache-aside has a classic race: a reader loads the **old** value from the database, a writer updates the database and invalidates the cache, and **then** the slow reader stores its old value into the cache. The cache now serves stale data until the TTL expires. Replaying the exact interleaving:

```python
db2 = {"price": 100}
cache2 = {}

# Reader A: cache miss, reads the database...
old_value_read_by_A = db2["price"]                 # 100
# Writer B: updates the database, then invalidates the cache
db2["price"] = 120
cache2.pop("price", None)
# ...Reader A (slow) finally writes what it read into the cache
cache2["price"] = old_value_read_by_A

print("database:", db2["price"], "| cache:", cache2["price"])
# database: 120 | cache: 100
```

**Mitigations:** always set a **TTL** so staleness is bounded; **version** the data and refuse to overwrite a newer cached version; do a **delayed second invalidation** after writes; or route a key's reads and writes through one place (write-through cache) when consistency matters more than speed. Decide explicitly how stale each kind of data may be: a product description can lag a minute; an account balance usually cannot.

## 6. Failure 4: cache penetration

Requests for keys that **do not exist** (a typo, a crawler, an attack) always miss the cache and always hit the database. **Cache the negative result** with a short TTL, and put a **Bloom filter** of valid ids in front (see [Bloom filters](../../11-distributed-systems/messaging-storage/01-logs-queues-and-lsm-trees.md)) so impossible keys never reach the database.

```python
NOT_FOUND = object()
db_hits = [0]
neg_cache = {}

def get_product(pid, existing={"p1", "p2"}):
    if pid in neg_cache:
        return None                                    # answered from the negative cache
    db_hits[0] += 1                                    # a real database lookup
    if pid not in existing:
        neg_cache[pid] = NOT_FOUND                     # remember "does not exist" (with a short TTL in real life)
        return None
    return f"product {pid}"

for _ in range(1000):
    get_product("bogus-id")
print("database lookups for 1000 requests of a missing id:", db_hits[0])
# database lookups for 1000 requests of a missing id: 1
```

## 7. Overload: backpressure and load shedding

When arrivals exceed capacity, a queue grows and **latency grows without bound**: every request eventually succeeds, but too late to matter, and memory fills. A healthy system **limits** its queues and **rejects** early (load shedding), answering "busy" quickly so clients can back off.

```python
def simulate(arrival_per_sec, service_per_sec, seconds, queue_limit=None):
    queue_wait = []                                     # how long each served request waited in the queue
    queue, rejected, served = [], 0, 0
    for sec in range(seconds):
        for _ in range(arrival_per_sec):
            if queue_limit is not None and len(queue) >= queue_limit:
                rejected += 1                           # shed load: fail fast
            else:
                queue.append(sec)
        for _ in range(min(service_per_sec, len(queue))):
            arrived = queue.pop(0)
            queue_wait.append(sec - arrived)
            served += 1
    return max(queue_wait), served, rejected

for label, limit in [("unbounded queue", None), ("bounded queue (100)", 100)]:
    worst_wait, served, rejected = simulate(arrival_per_sec=120, service_per_sec=100, seconds=60, queue_limit=limit)
    print(f"{label:<20} worst wait {worst_wait:>2} s | served {served} | rejected {rejected}")
# unbounded queue      worst wait 10 s | served 6000 | rejected 0
# bounded queue (100)  worst wait  0 s | served 6000 | rejected 1200
```

Both serve exactly 6,000 requests in 60 seconds (100 per second, the capacity). The unbounded queue makes users wait up to 10 seconds and keeps growing (it would reach minutes in an hour); the bounded queue **rejects the excess immediately** and keeps latency low for the requests it accepts. Related techniques:

- **Backpressure:** push the overload upstream (slow the producer, a full queue returns an error, TCP windows) instead of absorbing it silently.
- **Load shedding by priority:** drop low-value work (analytics, recommendations) first, keep checkout alive.
- **Timeouts and deadlines** on every call; abandon work whose caller has already given up.
- **Bulkheads:** separate pools per dependency so one slow service cannot consume all threads ([circuit breakers](../../11-distributed-systems/transactions/01-idempotency-retries-and-sagas.md)).
- **Graceful degradation:** serve cached or default content (generic recommendations, no personalisation) when a dependency is down, and tell the user honestly.
- **Autoscaling** helps with sustained load but is too slow for sudden spikes: shed first, scale second.

## 8. Capacity planning with Little's law

**Little's law:** the average number of requests in the system `L` equals the arrival rate `λ` times the average time each spends in the system `W`: `L = λ × W`. It lets you size thread pools, connection pools and fleets.

```python
def servers_needed(requests_per_sec, latency_sec, concurrency_per_server, target_utilization=0.6):
    in_flight = requests_per_sec * latency_sec                    # Little's law: L = lambda * W
    return in_flight, in_flight / (concurrency_per_server * target_utilization)

in_flight, servers = servers_needed(requests_per_sec=5000, latency_sec=0.080, concurrency_per_server=50)
print(f"{in_flight:.0f} requests in flight on average; about {servers:.1f} servers at 60% target utilization")
# 400 requests in flight on average; about 13.3 servers at 60% target utilization
```

Run servers well below 100 percent: queueing theory shows waiting time **explodes** as utilization approaches 100 percent (at 90 percent average utilization, queues are already long; at 99 percent they are unbounded in practice). Add headroom for failures: if you need 14 servers and run across 3 zones, size for **losing one zone** (N+1 or N+2 redundancy).

## 9. Event sourcing and CQRS

**Event sourcing** stores **every change as an immutable event** (`AccountOpened`, `Deposited`, `Withdrawn`) instead of the current state; state is derived by **replaying** events (with periodic **snapshots** to avoid long replays). You get a full audit trail, time travel ("what was the balance last Tuesday?") and the ability to build new views later. **CQRS** (command query responsibility segregation) separates the **write model** (validates commands, appends events) from one or more **read models** (denormalised views built from the events for fast queries).

```python
events = []                                             # the append-only event log: the source of truth

def handle_deposit(account, amount):
    events.append({"type": "Deposited", "account": account, "amount": amount})

def handle_withdraw(account, amount):
    if current_balance(account) < amount:               # validate against the state derived from the log
        raise ValueError("insufficient funds")
    events.append({"type": "Withdrawn", "account": account, "amount": amount})

def current_balance(account, upto=None):
    balance = 0
    for e in events[:upto]:                             # replay (upto lets us time-travel)
        if e["account"] == account:
            balance += e["amount"] if e["type"] == "Deposited" else -e["amount"]
    return balance

handle_deposit("ada", 100); handle_withdraw("ada", 30); handle_deposit("ada", 50)
print("balance now:", current_balance("ada"), "| after 2 events:", current_balance("ada", upto=2))
# balance now: 120 | after 2 events: 70

read_model = {}                                          # a separate, query-optimised view built from events
for e in events:
    read_model[e["account"]] = read_model.get(e["account"], 0) + (e["amount"] if e["type"] == "Deposited" else -e["amount"])
print(read_model)
# {'ada': 120}
```

Costs: more moving parts, **eventual consistency** between write and read models, event **schema evolution** (old events must stay readable), and a steeper learning curve. Use it where the history itself is valuable (finance, audit, collaborative editing), not for a simple CRUD app.

## 10. Monolith or microservices?

| | Monolith | Microservices |
|--|----------|---------------|
| Deployment | one unit: simple | many independent units: flexible, complex |
| Team scaling | gets hard beyond ~30 to 50 engineers on one codebase | teams own services end to end |
| Operations | one thing to run and debug | networks, versioning, tracing, many pipelines |
| Data | one database, easy transactions | a database per service; sagas, eventual consistency |
| Failure | one bug can take everything down | isolation, but more things that can fail and **cascade** |
| Latency | in-process calls | network calls (microseconds become milliseconds, and can fail) |

**Guidance:** start with a **well-structured monolith** (clear internal modules, one deployable) and extract services only when a real pain justifies the cost: independent scaling of one hot component, a separate team that needs to ship on its own schedule, different reliability or technology needs. A **distributed monolith** (many services that must deploy together and call each other in long chains) has the costs of both worlds. In interviews, justify either choice with the requirements rather than fashion.

## 11. A reliability checklist for any design

1. **Timeouts** on every network call; **retries** only for idempotent operations, with backoff and jitter.
2. **Redundancy** across failure domains (machines, zones); no single point of failure.
3. **Graceful degradation** paths decided in advance; **feature flags** to switch off risky parts.
4. **Rate limiting and load shedding** at the edges; bounded queues.
5. **Observability:** SLOs, dashboards for the golden signals, tracing, alerts on symptoms.
6. **Safe deploys:** canary or gradual rollout, automatic rollback, database migrations that are backwards compatible.
7. **Backups and restore drills** (a backup you have never restored is a hope, not a backup); disaster recovery targets: **RPO** (how much data you can lose) and **RTO** (how long you can be down).
8. **Chaos and load testing:** break things on purpose before production does it for you.

## 12. Common mistakes

- Caching without a TTL or an invalidation story.
- Fixed TTLs for bulk-loaded data (the avalanche).
- No protection for hot keys or missing keys.
- Unbounded queues, thread pools or retries ("we will just buffer it").
- Running at 90 percent utilization because it looks efficient.
- Splitting into microservices on day one without the tooling to run them.
- No restore test for backups.
- Designing only the happy path in an interview: always say "and when X fails, we..."

## 13. Two real-world examples

**Example 1: The homepage that took the database down.** A news site cached its homepage for 60 seconds. Every minute, when the entry expired, thousands of concurrent requests recomputed it and the database spiked. Single-flight plus stale-while-revalidate (serve the old page while one worker rebuilds) flattened the spikes, and users never waited.

**Example 2: Rejecting on purpose.** During a flash sale, a ticketing site's queue grew to minutes of waiting and then collapsed. The rebuild added a bounded admission queue with a "you are in line" page, rejected excess requests instantly, and prioritised checkout over browsing. Fewer users got in at once, but the system stayed up and most purchases succeeded.

## 14. Practice

1. In `run_herd`, make the load return the value for each of 5 different keys with 10 threads each. How many database calls with single-flight?
2. Compute how many of 1,000 keys expire in the same second with TTL = 60 plus jitter in `[0, 30)`.
3. A service has 200 requests in flight on average and each takes 250 ms. What is its throughput? If you must keep latency at 250 ms with 5x the traffic, what must change?
4. Redesign the stale-cache race fix using a version number: show the final cache contents after the same interleaving.
5. Why does a bounded queue improve the experience of the requests it does accept?
6. Decide monolith or microservices for a three-person startup with one product. Justify in two sentences.

<details>
<summary>Solutions</summary>

1. 5 calls: one per key (each key has its own lock and loads once).
2. About `1000 / 30` is roughly 33 per second on average; the busiest second will be a little higher (around 45 with random variation). The point: a wider jitter lowers the peak.
3. Throughput `λ = L / W = 200 / 0.25 = 800` requests per second. At 5x traffic (4,000 per second) you need 5x the concurrency capacity (5x the servers or workers) to keep the same latency, or the queue grows.
4. ```python
   cache3, db3 = {}, {"price": (1, 100)}                     # (version, value)
   read = db3["price"]                                       # reader A reads (1, 100)
   db3["price"] = (2, 120); cache3["price"] = (2, 120)       # writer B updates database and cache with the new version
   if "price" not in cache3 or cache3["price"][0] < read[0]: # A only writes if the cache has no newer version
       cache3["price"] = read
   print(cache3["price"])
   # (2, 120)
   ```
5. They do not sit behind a long backlog, so their wait is short and bounded; the excess is turned away immediately, which lets those clients back off or retry elsewhere rather than waiting uselessly.
6. A monolith: three people cannot afford the operational overhead (many deployments, tracing, network failures), and one codebase with clear module boundaries is faster to build; split later only for a measured reason.

</details>

## 15. Check yourself

1. What is a cache stampede and two ways to prevent it?
2. Why add jitter to TTLs?
3. How can cache-aside serve stale data, and how do you bound it?
4. What is cache penetration and how do you stop it?
5. Why do unbounded queues make overload worse?
6. State Little's law and use it to size a worker pool.
7. When is a monolith the better choice?

<details>
<summary>Answers</summary>

1. Many concurrent misses on an expired hot key all hit the database; use single-flight/request coalescing and stale-while-revalidate (or early refresh).
2. So keys loaded together do not all expire together, avoiding synchronized spikes on the database.
3. A slow reader can write an old value after an update and invalidation; set a TTL, version the entries, or delay a second invalidation.
4. Requests for nonexistent keys always miss and hit the database; cache negative results briefly and use a Bloom filter of valid keys.
5. They accept work that cannot be served in time, so latency grows without bound and memory fills; bounded queues reject early so accepted work stays fast.
6. `L = λ × W`: the average concurrency equals arrival rate times time in system (for example 400 requests/s at 100 ms means about 40 in flight, so size the pool above that with headroom).
7. For small teams and early products where simplicity and speed matter, or whenever no concrete scaling or team-independence need justifies the operational cost.

</details>

[Back to System Design Basics](README.md)
