# Load Balancing, Proxies, CDNs and Resilience

## 1. The concept

One server has a capacity and a failure rate. To handle more traffic and survive failures, you run **many servers** behind a **load balancer (LB)** that spreads requests, removes unhealthy servers, and gives clients a single address.

```text
clients -> DNS -> [CDN edge] -> [Load balancer] -> app server 1
                                              \-> app server 2
                                              \-> app server 3 -> cache / database
```

## 2. Load balancer types

| Type | Works at | Sees | Pros | Examples |
|------|----------|------|------|----------|
| **L4** | TCP/UDP | IPs and ports | Very fast, protocol agnostic | AWS NLB, HAProxy (tcp), IPVS |
| **L7** | HTTP | URLs, headers, cookies | Path routing, TLS termination, auth, retries | nginx, Envoy, AWS ALB |

A **reverse proxy** sits in front of servers on behalf of the server side (nginx, Envoy); a **forward proxy** sits in front of clients. Many LBs are reverse proxies that also **terminate TLS**, compress, cache and enforce limits. A **API gateway** adds authentication, quotas and routing for APIs.

### Balancing algorithms

| Algorithm | How | When |
|-----------|-----|------|
| **Round robin** | Take turns | Uniform, short requests |
| **Weighted** | Bigger servers take more | Mixed hardware |
| **Least connections** | Pick the server with fewest active requests | Uneven or long requests |
| **IP/consistent hash** | Same key goes to the same server | Caches, sticky state |
| **Power of two choices** | Sample two servers, take the less loaded | Cheap and nearly as good as least-loaded |

```python
import itertools
from collections import Counter

servers = ["s1", "s2", "s3"]
rr = itertools.cycle(servers)
print([next(rr) for _ in range(7)])

class LeastConnections:
    def __init__(self, servers): self.active = {s: 0 for s in servers}
    def pick(self):
        s = min(self.active, key=self.active.get); self.active[s] += 1; return s
    def done(self, s): self.active[s] -= 1
lc = LeastConnections(servers)
a, b, c = lc.pick(), lc.pick(), lc.pick()
lc.done(b)
print(a, b, c, lc.pick())
def weighted(weights):
    pool = [s for s, w in weights.items() for _ in range(w)]
    return itertools.cycle(pool)
w = weighted({"big": 3, "small": 1})
print(Counter(next(w) for _ in range(8)))
```

```python
import hashlib, bisect

def h(v): return int(hashlib.md5(v.encode()).hexdigest(), 16)
class Ring:
    def __init__(self, nodes, vnodes=100):
        self.ring = sorted((h(f"{n}#{i}"), n) for n in nodes for i in range(vnodes))
    def get(self, key):
        return self.ring[bisect.bisect(self.ring, (h(key), "")) % len(self.ring)][1]
keys = [f"user{i}" for i in range(10000)]
r3, r4 = Ring(servers), Ring(servers + ["s4"])
moved = sum(r3.get(k) != r4.get(k) for k in keys)
mod = sum(h(k) % 3 != h(k) % 4 for k in keys)
print(moved, mod)
```

Consistent hashing sends the same user to the same cache node and moves only about `1/N` of the keys when a node is added (2402 of 10,000 here, against 7484 for `hash % N`), the same idea as in [NoSQL](../../05-databases/nosql/README.md).

### Health checks and failure

An LB probes servers (`GET /healthz` or a TCP connect) and stops sending traffic to failing ones. Good health endpoints check real readiness (dependencies reachable), not just "process is up". **Connection draining** lets in-flight requests finish before a server is removed (deploys, scale-in). The LB itself must not be a single point of failure: run pairs or use anycast/DNS across several.

### Sticky sessions vs stateless services

**Sticky sessions** pin a client to one server via cookie or IP hash, which breaks balance and loses state when the server dies. Prefer **stateless** app servers: keep session state in Redis or a signed token, so any server can handle any request and scaling or replacing servers is trivial.

## 3. CDNs and caching

A **CDN** (content delivery network) is a worldwide fleet of cache servers (**edge** or PoP locations). DNS or anycast routes users to a nearby edge, which serves cached copies and fetches from your **origin** only on a miss.

- Benefits: lower latency (physics: light takes time), less origin load, absorbs traffic spikes and DDoS, TLS termination near the user.
- Cache behavior is controlled by `Cache-Control`, `Vary` and the CDN rules; the **cache key** is usually URL plus selected headers.
- **Invalidation:** purge by URL or tag, or avoid it by using content-hashed asset names.
- **Cache hit ratio** is the metric to watch; origin shielding adds a mid-tier cache to protect the origin.
- Personalized or authenticated responses must not be cached in shared caches (`private`, `Vary: Cookie`, or bypass).

Caching layers, closest to furthest from the user: browser, CDN edge, reverse-proxy cache, application cache (Redis), database buffer cache.

## 4. Resilience patterns

Networks and dependencies fail. These patterns stop one failure from becoming an outage.

### Timeouts and retries with backoff

Always set a timeout. Retry **only idempotent** operations, with **exponential backoff and jitter** so a thousand clients do not retry in lockstep (a retry storm).

```python
import random

def backoff(attempt, base=0.1, cap=5):
    return random.uniform(0, min(cap, base * 2 ** attempt))
print([round(min(5, 0.1 * 2 ** i), 1) for i in range(8)])
```

### Circuit breaker

After repeated failures, stop calling the sick dependency for a while (fail fast) so it can recover and your threads are not all blocked on it. States: closed (normal), open (reject immediately), half-open (let a trial request through).

```python
class CircuitBreaker:
    def __init__(self, limit=3): self.fails, self.limit = 0, limit
    def call(self, fn):
        if self.fails >= self.limit: raise RuntimeError("circuit open")
        try:
            r = fn(); self.fails = 0; return r
        except Exception:
            self.fails += 1; raise
cb = CircuitBreaker()
def bad(): raise IOError
for _ in range(4):
    try: cb.call(bad)
    except Exception as e: last = type(e).__name__
print(last)
```

### Rate limiting (token bucket)

Allows bursts up to the bucket size while enforcing an average rate. Used per user or API key, usually returning `429` and `Retry-After`.

```python
def token_bucket(rate, capacity):
    tokens, last = capacity, 0.0
    def allow(now):
        nonlocal tokens, last
        tokens = min(capacity, tokens + (now - last) * rate); last = now
        if tokens >= 1: tokens -= 1; return True
        return False
    return allow
allow = token_bucket(rate=2, capacity=3)
print([allow(0) for _ in range(5)], allow(1.0))
```

### Others
- **Bulkheads:** isolate pools so one slow dependency cannot exhaust all threads.
- **Load shedding:** under overload, reject low-priority work early rather than collapsing.
- **Graceful degradation:** serve stale cache or a reduced feature when a dependency is down.
- **Redundancy across zones/regions** with health-checked failover.
- **Idempotency keys** make retries safe (see [DNS and HTTP](../dns-http/README.md)).

## 5. Two real-world examples

### Example 1: Black Friday for an online shop
Static assets and product images are served by a CDN with a 95%+ hit ratio, so the origin only sees API traffic. An L7 load balancer spreads API calls over stateless containers behind health checks; autoscaling adds servers as CPU rises; sessions live in Redis; a circuit breaker around the recommendation service means that if it fails, product pages still render without recommendations. Rate limits protect checkout from bots.

### Example 2: A retry storm that turned a blip into an outage
A database slows for 10 s. Every client times out and immediately retries three times, so the database sees four times the load and never recovers; the outage lasts an hour. The fix: exponential backoff with jitter, retry budgets (at most 10% extra traffic), circuit breakers, and server-side load shedding. Retries multiply load exactly when a system is weakest.

## 6. Tips, tricks and pitfalls

- Design services **stateless**; put state in a database, cache or token.
- Make health checks reflect real readiness, and add draining to deployments.
- Retries need **idempotency**, backoff, jitter and a cap.
- Choose timeouts deliberately (client timeout larger than server's, shorter than the user's patience) and propagate deadlines downstream.
- Never trust `X-Forwarded-For` unless set by your own proxy.
- Watch **p99 latency** and error rate, not only averages.
- Test failure: kill a server in staging, add latency, and see what the LB and clients do.

## 7. Check yourself

1. L4 vs L7 load balancer?
2. When prefer least-connections over round robin?
3. Why are sticky sessions a smell, and what is the alternative?
4. What does a CDN do and what is a cache hit ratio?
5. How does consistent hashing help a cache cluster?
6. Explain a retry storm and three defenses.
7. How does a circuit breaker work?
8. What does a token bucket allow that a fixed counter does not?

<details>
<summary>Answers</summary>

1. L4 balances TCP/UDP by IP and port (fast, content-blind). L7 understands HTTP and can route by path or header, terminate TLS, retry and inspect.
2. When requests vary a lot in duration (long uploads, slow queries), so equal turn-taking would overload some servers.
3. They pin load and state to one server (uneven balance, state lost on failure). Keep state in a shared store or signed token and run stateless servers.
4. It caches content at edge locations near users and serves it without hitting the origin; hit ratio is the share of requests served from cache.
5. Keys map to nodes on a ring, so adding or removing a node remaps only about `1/N` of the keys instead of nearly all, keeping the cache mostly warm.
6. Clients retry together and multiply load on a struggling service. Use exponential backoff with jitter, retry budgets, circuit breakers and load shedding.
7. It counts failures; past a threshold it opens and rejects calls immediately for a cool-down, then half-opens to test with a trial call and closes again if it succeeds.
8. It permits short bursts (up to the bucket size) while enforcing the average rate, smoothing out boundary effects.

</details>

[Exercises](exercises.md) · [Summary](summary.md)
