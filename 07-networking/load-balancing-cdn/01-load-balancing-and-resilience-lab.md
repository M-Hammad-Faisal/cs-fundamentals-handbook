# Load Balancing and Resilience Lab

**Prerequisites:** [HTTP from scratch](../dns-http/01-http-from-scratch.md), [sockets lab](../tcp-ip-osi/02-sockets-tcp-udp-lab.md), [hash tables and consistent hashing](../../02-data-structures/hash-tables/03-dict-set-internals-and-bloom-filters.md), [queues](../../02-data-structures/stacks-queues/02-queues-deques-priority-queues.md). **You will learn (by running everything locally):** how a **load balancer** spreads traffic (**round robin, weighted, least connections, hash-based**), how it uses **health checks**, how clients stay resilient with **timeouts, retries with exponential backoff and jitter, and circuit breakers**, how **rate limiters** protect a service (**token bucket, sliding window**), and how a **CDN/cache** raises hit ratios. You will build a working **reverse proxy** in front of three backends.

## 1. In plain words

One server can only handle so many requests. A **load balancer (LB)** sits in front of several identical servers and **distributes** incoming requests among them, so the system handles more traffic (**horizontal scaling**), survives a server failing (**availability**), and can be updated one server at a time.

```text
                     +--> backend A
clients ---> LOAD BALANCER --> backend B        (the clients only know the LB's address)
                     +--> backend C
```

## 2. A working load balancer on localhost

Three backends that each report their own name, and a reverse proxy that forwards requests to them in turn:

```python
import http.server, http.client, threading, itertools, collections

def start_backend(name):
    class Backend(http.server.BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"
        def log_message(self, *a): pass
        def do_GET(self):
            if self.path == "/health":
                body, status = b"ok", 200
            else:
                body, status = f"response from {name}".encode(), 200
            self.send_response(status)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Backend)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server

backends = {name: start_backend(name) for name in ("A", "B", "C")}
ports = {name: srv.server_address[1] for name, srv in backends.items()}

class RoundRobin:
    def __init__(self, names):
        self._cycle = itertools.cycle(names)
    def pick(self, request_path=None):
        return next(self._cycle)

def start_load_balancer(strategy):
    class Proxy(http.server.BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"
        def log_message(self, *a): pass
        def do_GET(self):
            name = strategy.pick(self.path)
            conn = http.client.HTTPConnection("127.0.0.1", ports[name], timeout=2)
            conn.request("GET", self.path)
            upstream = conn.getresponse()
            body = upstream.read()
            conn.close()
            self.send_response(upstream.status)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("X-Served-By", name)
            self.end_headers()
            self.wfile.write(body)
    lb = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Proxy)
    threading.Thread(target=lb.serve_forever, daemon=True).start()
    return lb

lb = start_load_balancer(RoundRobin(["A", "B", "C"]))
LB_PORT = lb.server_address[1]

def get(path="/"):
    conn = http.client.HTTPConnection("127.0.0.1", LB_PORT, timeout=2)
    conn.request("GET", path)
    resp = conn.getresponse()
    body = resp.read()
    conn.close()
    return resp.getheader("X-Served-By"), body.decode()

print([get()[0] for _ in range(7)])               # ['A', 'B', 'C', 'A', 'B', 'C', 'A']
print(get("/anything"))                           # ('B', 'response from B')
```

The clients talk only to the LB's address; the work spreads across A, B and C. This is what **nginx, HAProxy, Envoy, and cloud load balancers (AWS ALB/NLB)** do, with far more robustness.

## 3. Balancing strategies (simulated)

The strategies differ in how they choose; let us compare them on the same workload. Requests have different **costs** (some are slow), servers may differ in **capacity**.

```python
import random, collections

def simulate(strategy_factory, num_requests=3000, seed=1):
    rng = random.Random(seed)
    names = ["A", "B", "C"]
    strategy = strategy_factory(names)
    active = collections.Counter()                       # requests currently in flight per server
    busy_until = {n: 0.0 for n in names}                 # when each server becomes free (single worker each)
    waits, now = [], 0.0
    served = collections.Counter()
    for i in range(num_requests):
        now += rng.expovariate(1.0)                      # random arrivals, about 1 per time unit
        cost = rng.choice([0.5, 0.5, 0.5, 0.5, 4.0])     # mostly quick, sometimes a slow request
        target = strategy.pick(i, active, busy_until, now)
        start = max(now, busy_until[target])
        waits.append(start - now)
        busy_until[target] = start + cost
        served[target] += 1
    waits.sort()
    return dict(served), round(sum(waits) / len(waits), 2), round(waits[int(0.95 * len(waits))], 2)

class RR:
    def __init__(self, names): self.names, self.i = names, -1
    def pick(self, i, active, busy_until, now):
        self.i += 1; return self.names[self.i % len(self.names)]

class Random_:
    def __init__(self, names): self.names, self.rng = names, random.Random(7)
    def pick(self, i, active, busy_until, now): return self.rng.choice(self.names)

class LeastBusy:                                         # a stand-in for "least connections": pick the server that frees up first
    def __init__(self, names): self.names = names
    def pick(self, i, active, busy_until, now): return min(self.names, key=lambda n: busy_until[n])

for label, factory in (("round robin", RR), ("random", Random_), ("least busy", LeastBusy)):
    print(f"{label:12}", simulate(factory))
# round robin  ({'A': 1000, 'B': 1000, 'C': 1000}, 0.49, 2.98)      (requests per server, mean wait, 95th-percentile wait)
# random       ({'B': 997, 'A': 1054, 'C': 949}, 0.95, 4.4)
# least busy   ({'A': 1001, 'B': 1005, 'C': 994}, 0.11, 0.7)
```

Look at the numbers: round robin hands every server exactly 1000 requests, yet its mean wait is 0.49 and its slowest 5% wait nearly 3 time units, because it keeps feeding a server that is stuck on a slow request. Random is worse (0.95 mean, 4.4 at the 95th percentile). **Least busy**, which looks at actual load, cuts the mean wait to 0.11 and the tail to 0.7. Equal *counts* are not equal *load*.

| Strategy | How it picks | Good when | Weakness |
|----------|--------------|-----------|----------|
| **Round robin** | rotate | equal servers, similar requests | ignores actual load |
| **Weighted round robin** | rotate, proportional to capacity weights | servers of different size | static weights |
| **Random / power of two choices** | random (or best of 2 random) | stateless LBs at scale | plain random can be uneven |
| **Least connections** | fewest in-flight requests | long-lived or uneven requests | needs load tracking |
| **IP / key hash** | `hash(client or key) % N` | **stickiness** (same user to same server), caches | uneven; reshuffles when N changes: use [consistent hashing](../../02-data-structures/hash-tables/03-dict-set-internals-and-bloom-filters.md) |
| **Latency-based / geo** | nearest or fastest | global services | needs measurements |

### Weighted round robin and power of two choices

```python
def weighted_round_robin(weights):
    schedule = [name for name, w in weights.items() for _ in range(w)]
    return itertools.cycle(schedule)

wrr = weighted_round_robin({"big": 3, "small": 1})
print([next(wrr) for _ in range(8)])                    # ['big', 'big', 'big', 'small', 'big', 'big', 'big', 'small']

def power_of_two(load, rng):
    a, b = rng.sample(list(load), 2)                    # look at two random servers, send to the less loaded one
    return a if load[a] <= load[b] else b

rng = random.Random(5)
for strategy in ("random", "two choices"):
    load = collections.Counter({f"s{i}": 0 for i in range(10)})
    for _ in range(10_000):
        target = rng.choice(list(load)) if strategy == "random" else power_of_two(load, rng)
        load[target] += 1
    print(f"{strategy:12} busiest server holds {max(load.values())} requests (ideal {10_000 // 10})")
# random       busiest server holds 1046 requests (ideal 1000)
# two choices  busiest server holds 1002 requests (ideal 1000)
```

Checking just **two random servers** and picking the lighter one flattens the distribution dramatically, with no global view needed ("the power of two choices").

### Stickiness (session affinity)

If servers hold per-user state in memory, the same user must reach the same server. Options: hash the client IP or a session cookie to a server; better, **make servers stateless** and keep sessions in Redis or a database so any server can answer.

## 4. Health checks: do not send traffic to dead servers

The LB probes each backend (for example `GET /health` every 5 seconds) and removes failing ones from rotation until they recover.

```python
class HealthChecker:
    def __init__(self, ports, fail_after=2):
        self.ports, self.fail_after = ports, fail_after
        self.failures = collections.Counter()
        self.healthy = set(ports)

    def probe(self, name):
        try:
            conn = http.client.HTTPConnection("127.0.0.1", self.ports[name], timeout=0.5)
            conn.request("GET", "/health")
            ok = conn.getresponse().status == 200
            conn.close()
        except OSError:
            ok = False
        if ok:
            self.failures[name] = 0
            self.healthy.add(name)
        else:
            self.failures[name] += 1
            if self.failures[name] >= self.fail_after:
                self.healthy.discard(name)               # take it out of rotation after consecutive failures

    def round(self):
        for name in self.ports:
            self.probe(name)
        return sorted(self.healthy)

checker = HealthChecker(ports)
print(checker.round())                                   # ['A', 'B', 'C']

backends["B"].shutdown(); backends["B"].server_close()   # backend B crashes
print(checker.round(), checker.round())                  # ['A', 'B', 'C'] ['A', 'C']    (removed after two consecutive failures)
```

Settings to tune: **interval, timeout, number of failures to eject, number of successes to readmit**. A shallow check (is the port open?) misses broken apps; a deep check (can it reach the database?) can take every server out of rotation at once when the database blips. Use both **liveness** (should I restart it?) and **readiness** (should it receive traffic?).

## 5. Client-side resilience

Even with an LB, calls fail: networks hiccup, servers overload. Clients need rules.

### Timeouts

Always set them (connect and read). No timeout means one stuck dependency freezes all your threads.

### Retries with exponential backoff and jitter

Retry **only idempotent requests** and only on **transient errors** (timeouts, 502/503/504, connection reset), never on 4xx. Wait **longer each time** (backoff) and add **random jitter** so thousands of clients do not retry in lock-step (a **retry storm** or **thundering herd**).

```python
import random

def backoff_delays(attempts, base=0.1, cap=5.0, rng=random):
    for attempt in range(attempts):
        ceiling = min(cap, base * 2 ** attempt)           # 0.1, 0.2, 0.4, 0.8, ... capped
        yield rng.uniform(0, ceiling)                     # "full jitter": a random point below the ceiling

print([round(min(5.0, 0.1 * 2 ** i), 2) for i in range(8)])      # [0.1, 0.2, 0.4, 0.8, 1.6, 3.2, 5.0, 5.0]
print([round(d, 2) for d in backoff_delays(5, rng=random.Random(2))])      # [0.1, 0.19, 0.02, 0.07, 1.34]   (random, each below its ceiling of 0.1, 0.2, 0.4, 0.8, 1.6)

def call_with_retries(operation, max_attempts=5, sleep=lambda s: None, rng=random.Random(1)):
    last_error = None
    for attempt, delay in enumerate(backoff_delays(max_attempts, rng=rng), start=1):
        try:
            return operation(attempt), attempt
        except ConnectionError as e:                      # only transient errors are retried
            last_error = e
            sleep(delay)
    raise last_error

def flaky(attempt):                                       # fails twice, then succeeds
    if attempt < 3:
        raise ConnectionError("temporary failure")
    return "ok"

print(call_with_retries(flaky))                           # ('ok', 3)
```

### Circuit breaker: stop hammering a failing dependency

After too many failures the breaker **opens**: calls fail immediately without touching the sick service (letting it recover and protecting your own threads). After a cool-down it goes **half-open** and lets one trial call through: success closes it, failure re-opens it.

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=3, reset_timeout=30.0, clock=None):
        self.failure_threshold, self.reset_timeout = failure_threshold, reset_timeout
        self.clock = clock or (lambda: 0.0)
        self.state, self.failures, self.opened_at = "closed", 0, 0.0

    def call(self, operation):
        if self.state == "open":
            if self.clock() - self.opened_at >= self.reset_timeout:
                self.state = "half-open"                  # allow one trial request
            else:
                raise RuntimeError("circuit open: failing fast")
        try:
            result = operation()
        except ConnectionError:
            self.failures += 1
            if self.state == "half-open" or self.failures >= self.failure_threshold:
                self.state, self.opened_at = "open", self.clock()
            raise
        self.failures, self.state = 0, "closed"
        return result

now = {"t": 0.0}
breaker = CircuitBreaker(failure_threshold=3, reset_timeout=30, clock=lambda: now["t"])
healthy = {"up": False}
def dependency():
    if not healthy["up"]:
        raise ConnectionError("down")
    return "fine"

results = []
for _ in range(5):
    try:
        breaker.call(dependency)
    except (ConnectionError, RuntimeError) as e:
        results.append(type(e).__name__ + ":" + str(e))
print(results)
# ['ConnectionError:down', 'ConnectionError:down', 'ConnectionError:down', 'RuntimeError:circuit open: failing fast', 'RuntimeError:circuit open: failing fast']
print(breaker.state)                                      # open

now["t"] = 31.0; healthy["up"] = True                     # 31 seconds later the service has recovered
print(breaker.call(dependency), breaker.state)            # fine closed    (the half-open trial succeeded)
```

Companions: **bulkheads** (separate thread pools per dependency so one slow service cannot exhaust everything), **fallbacks** (cached or default data when a call fails), **load shedding** (deliberately reject low-priority requests under overload), and **timeouts propagated downstream** ("deadline" headers).

## 6. Rate limiting: protecting a service from too many requests

**Token bucket:** a bucket holds up to `capacity` tokens and refills at `rate` tokens per second. Each request spends a token. It allows **bursts** up to the capacity but enforces the long-run average rate.

```python
class TokenBucket:
    def __init__(self, rate, capacity, clock):
        self.rate, self.capacity, self.clock = rate, capacity, clock
        self.tokens, self.last = capacity, clock()

    def allow(self, cost=1):
        now = self.clock()
        self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)     # refill for the elapsed time
        self.last = now
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False

t = {"now": 0.0}
bucket = TokenBucket(rate=2, capacity=5, clock=lambda: t["now"])        # 2 requests per second, bursts of 5
print([bucket.allow() for _ in range(7)])                 # [True, True, True, True, True, False, False]   (burst of 5, then rejected)
t["now"] = 1.0                                            # one second later: 2 tokens refilled
print([bucket.allow() for _ in range(3)])                 # [True, True, False]
```

**Sliding window log:** remember the timestamps of recent requests and count those in the last `window` seconds. Exact, but stores one entry per request.

```python
from collections import deque

class SlidingWindow:
    def __init__(self, limit, window, clock):
        self.limit, self.window, self.clock, self.events = limit, window, clock, deque()
    def allow(self):
        now = self.clock()
        while self.events and self.events[0] <= now - self.window:
            self.events.popleft()                         # forget requests outside the window
        if len(self.events) < self.limit:
            self.events.append(now)
            return True
        return False

t2 = {"now": 0.0}
limiter = SlidingWindow(limit=3, window=10, clock=lambda: t2["now"])
out = []
for second in (0, 1, 2, 3, 9, 10, 11, 12):
    t2["now"] = float(second)
    out.append((second, limiter.allow()))
print(out)
# [(0, True), (1, True), (2, True), (3, False), (9, False), (10, True), (11, True), (12, True)]
```

HTTP convention: respond **`429 Too Many Requests`** with a **`Retry-After`** header. Apply limits **per client/API key/IP** and per endpoint; keep counters in a shared store such as Redis when you run several servers. Variants: fixed window (simple, but allows double bursts at window edges), leaky bucket (smooths output to a constant rate).

## 7. CDNs and caching

A **CDN** (content delivery network) is a worldwide fleet of cache servers (**edge locations**). Users are routed (via DNS or anycast) to a nearby edge, which serves **cached copies** of static content (images, JavaScript, video) and only contacts your **origin** server on a miss. Benefits: lower latency (the speed of light matters: 150 ms across an ocean), far less load on the origin, protection from traffic spikes and DDoS.

The key metric is the **cache hit ratio**. Let us simulate an edge cache with LRU eviction and per-object TTL against realistic **skewed** traffic (a few popular objects, a long tail):

```python
from collections import OrderedDict

class EdgeCache:
    def __init__(self, capacity, ttl, clock):
        self.capacity, self.ttl, self.clock = capacity, ttl, clock
        self.items = OrderedDict()                        # key -> expiry time; order = recency
        self.hits = self.misses = 0

    def get(self, key):
        now = self.clock()
        expiry = self.items.get(key)
        if expiry is not None and expiry > now:
            self.items.move_to_end(key)
            self.hits += 1
            return "HIT"
        self.misses += 1                                  # miss or expired: fetch from the origin and store
        self.items[key] = now + self.ttl
        self.items.move_to_end(key)
        if len(self.items) > self.capacity:
            self.items.popitem(last=False)                # evict the least recently used object
        return "MISS"

def zipf_requests(n_objects, n_requests, s=1.1, seed=4):
    rng = random.Random(seed)
    weights = [1 / (rank ** s) for rank in range(1, n_objects + 1)]      # rank 1 is the most popular
    return rng.choices(range(n_objects), weights=weights, k=n_requests)

requests = zipf_requests(n_objects=10_000, n_requests=50_000)
for capacity in (50, 500, 5000):
    clock = {"t": 0.0}
    cache = EdgeCache(capacity, ttl=3600, clock=lambda: clock["t"])
    for r in requests:
        clock["t"] += 0.01
        cache.get(r)
    print(f"cache of {capacity:5} objects ({capacity / 100:4.1f}% of the catalog): hit ratio {cache.hits / (cache.hits + cache.misses):.0%}")
# cache of    50 objects ( 0.5% of the catalog): hit ratio 44%
# cache of   500 objects ( 5.0% of the catalog): hit ratio 70%
# cache of  5000 objects (50.0% of the catalog): hit ratio 89%
```

Because popularity is **skewed** (a few objects get most requests), even a small cache holds a large share of traffic: caching just 5% of the objects serves about 70% of requests.

**What to cache and how:** static assets with long `Cache-Control: max-age` and **fingerprinted filenames** (`app.3f9c1.js`); API responses that are the same for everyone (short TTL); never user-specific private pages in shared caches. **Invalidation** ("purge") when content changes: either purge by URL/tag or use versioned URLs so you never need to.

Related layers of caching: **browser cache** -> **CDN edge** -> **reverse proxy cache (nginx, Varnish)** -> **application cache (Redis, memcached)** -> **database buffer pool**. Each layer absorbs requests before they reach the next.

## 8. Layer 4 versus layer 7 load balancing

| | **L4** (transport) | **L7** (application) |
|---|--------------------|----------------------|
| Looks at | IP and port | HTTP path, headers, cookies |
| Speed | very fast, simple | more CPU, much more flexible |
| Can do | spread TCP/UDP connections | route `/api` vs `/images`, terminate TLS, rewrite headers, canary releases, auth |
| Examples | AWS NLB, IPVS, HAProxy (tcp mode) | nginx, Envoy, AWS ALB, HAProxy (http mode) |

Common L7 routing rule: `/api/* -> app servers`, `/static/* -> storage or CDN`, `Host: admin.example.com -> admin service`. LBs also **terminate TLS** (offload encryption) and add `X-Forwarded-For` so the backend learns the real client IP.

```python
def l7_route(path, host):
    if host.startswith("admin."):
        return "admin-service"
    if path.startswith("/api/"):
        return "app-servers"
    if path.startswith("/static/"):
        return "object-storage"
    return "web-servers"

print([l7_route(p, h) for p, h in (("/api/users", "shop.com"), ("/static/a.css", "shop.com"), ("/", "admin.shop.com"), ("/cart", "shop.com"))])
# ['app-servers', 'object-storage', 'admin-service', 'web-servers']
```

Who balances the balancers? Several LBs share a **virtual IP** (VRRP/keepalived), or DNS/anycast spreads clients across LBs, or managed cloud LBs do it for you. The LB must not be a single point of failure.

## 9. Putting a system together

```text
users -> DNS (geo/latency) -> CDN edge (static, cache) -> L7 load balancer (TLS, routing, health checks)
      -> stateless app servers (autoscaled) -> cache (Redis) -> database (primary + replicas)
         with timeouts, retries with backoff, circuit breakers, rate limits at the edges
```

Design rules: keep app servers **stateless** (so any can serve any request and you can add or remove them freely); put state in shared stores; **scale horizontally** behind the LB; **degrade gracefully** (serve cached or reduced content rather than error pages); and **test failure** (kill a server on purpose: chaos engineering).

## 10. Two real-world examples

**Example 1: Black Friday.** An online shop normally runs 4 app servers. The autoscaler sees CPU rising and adds 20 more; the load balancer's health checks add them only when ready and the CDN serves all product images from the edge, so the origin sees under 10% of the traffic. A slow payment provider trips the circuit breaker, so the site shows "payment temporarily unavailable, saved your cart" instead of freezing every request thread.

**Example 2: A retry storm.** A database blips for 2 seconds. 10 000 clients all retry immediately and again immediately after; the database, just recovering, receives three times its normal load and falls over for 20 minutes. Exponential backoff with jitter would have spread the retries over many seconds and let it recover.

## 11. Common mistakes

- Retrying non-idempotent requests (duplicate orders and payments) or retrying with no backoff.
- No timeouts, or timeouts longer than the caller's own deadline.
- Sticky sessions with stateful servers (a server dies and its users lose their sessions).
- Health checks that only test that the port is open, or deep checks that cascade failures.
- Making the load balancer a single point of failure.
- Caching personalized responses in a shared cache.
- Rate limiting only by IP when many users share one (corporate NAT), or not at all for login endpoints.
- Never testing what happens when a dependency is down.

## 12. Practice

1. Three servers with weights 5, 3 and 2: how many of 100 requests does each get under weighted round robin?
2. Why is round robin poor when some requests take 100x longer than others?
3. A token bucket has `rate=10/s`, `capacity=20`. A client sends 30 requests instantly. How many are allowed? How long until it can send 10 more?
4. Which status code and header should a rate limiter return?
5. What does a circuit breaker do in the **half-open** state?
6. Why add jitter to retry delays?
7. Why is a 5% cache of a skewed catalog so effective?
8. Use `l7_route` to decide where `GET /api/orders` for host `shop.com` goes.

<details>
<summary>Solutions</summary>

1. 50, 30 and 20 (proportional to the weights).
2. It sends equal numbers of requests to each server regardless of how long they take, so a server stuck with several slow requests builds a queue while others idle; least connections adapts.
3. 20 are allowed (the bucket's burst capacity), 10 are rejected. Refilling 10 tokens at 10 per second takes 1 second.
4. `429 Too Many Requests` with a `Retry-After` header.
5. It lets a limited number of trial requests through; success closes the circuit, failure re-opens it for another cool-down.
6. Without jitter, all clients retry at exactly the same moments, producing synchronized spikes (retry storms); randomness spreads the load.
7. Traffic follows a heavy-tailed popularity distribution: the few most popular objects account for most requests, so a small cache of them serves most of the traffic.
8. ```python
   print(l7_route("/api/orders", "shop.com"))                     # app-servers
   ```

</details>

## 13. Check yourself

1. What problems does a load balancer solve?
2. Compare round robin and least connections.
3. What do health checks do and what is the difference between liveness and readiness?
4. What do exponential backoff and jitter each add?
5. How does a circuit breaker protect both caller and callee?
6. Token bucket versus sliding window: when would you pick each?
7. What is the CDN cache hit ratio and why does it matter?

<details>
<summary>Answers</summary>

1. Capacity (spread load over many servers), availability (route around failed servers), and easy rolling updates; clients see one address.
2. Round robin rotates blindly (simple, fine for uniform requests); least connections sends to the least busy server (better for uneven or long requests) but needs load tracking.
3. They remove unhealthy servers from rotation. Liveness asks "is the process alive (restart if not)?"; readiness asks "can it handle traffic right now?"
4. Backoff spreads retries over increasing intervals so a struggling service can recover; jitter randomizes them so clients do not retry in sync.
5. It stops calls to a failing dependency (freeing the caller's threads and giving the callee room to recover) and probes carefully before resuming.
6. Token bucket: allow short bursts but cap the average rate (cheap). Sliding window: exact "N requests per window" accounting when strict limits matter.
7. The fraction of requests served from the edge cache; higher means lower latency and less origin load and cost.

</details>

## 14. Clean up

```python
lb.shutdown(); lb.server_close()
for name, srv in backends.items():
    if name != "B":                                       # B was shut down earlier
        srv.shutdown(); srv.server_close()
print("servers stopped")                                  # servers stopped
```

[Back to load balancing and CDNs](README.md)
