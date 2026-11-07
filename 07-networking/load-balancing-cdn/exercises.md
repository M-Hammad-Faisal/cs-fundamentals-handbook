# Load Balancing, Proxies, CDNs and Resilience: Exercises

1. Simulate 1,000 requests with random durations against round robin and least connections. Which gives a more even maximum load, and why?
2. Implement **power of two choices** and compare its imbalance with random assignment.
3. Add a half-open state with a cool-down to `CircuitBreaker`.
4. Implement a **sliding-window** rate limiter allowing 5 requests per 10 seconds per user.
5. Design the health check endpoint for a service that depends on a database and a cache. What should return 200, and what should not take the instance out of rotation?
6. A CDN has a 60% hit ratio and your origin handles 1,000 req/s at that. What happens to origin load if you raise the hit ratio to 95%?
7. Explain how a deployment can drop requests, and which two features prevent it.
8. You must shard sessions across 5 Redis nodes and add a sixth next month. Which routing scheme and why?

<details>
<summary>Solutions</summary>

**1.** Least connections evens the load when durations differ, because it reacts to actual in-flight work; round robin ignores durations, so a server that happened to get several long requests falls behind.
```python
import random, heapq
random.seed(1)
durs = [random.expovariate(1) for _ in range(1000)]
def rr_max(n=5):
    load = [0.0] * n
    for i, d in enumerate(durs): load[i % n] += d
    return max(load)
def ll_max(n=5):
    load = [(0.0, i) for i in range(n)]; heapq.heapify(load)
    for d in durs:
        t, i = heapq.heappop(load); heapq.heappush(load, (t + d, i))
    return max(t for t, _ in load)
print(round(rr_max(), 1), round(ll_max(), 1))     # least-loaded finishes sooner (smaller max)
```

**2.**
```python
import random
def p2c(loads):
    a, b = random.sample(range(len(loads)), 2)
    i = a if loads[a] <= loads[b] else b
    loads[i] += 1
    return i
def run(pick, n=10, k=10000):
    loads = [0] * n
    for _ in range(k): pick(loads)
    return max(loads) - min(loads)
rand = lambda loads: loads.__setitem__(i := random.randrange(len(loads)), loads[i] + 1)
print(run(p2c), run(rand))     # p2c gives a far smaller spread
```

**3.**
```python
import time
class Breaker:
    def __init__(self, limit=3, cooldown=5.0, clock=time.monotonic):
        self.limit, self.cooldown, self.clock = limit, cooldown, clock
        self.fails, self.opened_at = 0, None
    def call(self, fn):
        if self.opened_at is not None:
            if self.clock() - self.opened_at < self.cooldown:
                raise RuntimeError("circuit open")
            # half-open: allow one trial call below
        try:
            r = fn()
        except Exception:
            self.fails += 1
            if self.fails >= self.limit or self.opened_at is not None:
                self.opened_at = self.clock()
            raise
        self.fails, self.opened_at = 0, None
        return r
```

**4.**
```python
from collections import defaultdict, deque
class SlidingWindow:
    def __init__(self, limit=5, window=10.0):
        self.limit, self.window, self.hits = limit, window, defaultdict(deque)
    def allow(self, user, now):
        q = self.hits[user]
        while q and q[0] <= now - self.window: q.popleft()
        if len(q) < self.limit:
            q.append(now); return True
        return False
sw = SlidingWindow()
print([sw.allow("u", t) for t in (0, 1, 2, 3, 4, 5)], sw.allow("u", 10.5))   # five True, then False, then True
```

**5.** Liveness (`/livez`): returns 200 if the process runs (restart if not). Readiness (`/readyz`): 200 only when the instance can serve (database reachable, warmed up, migrations done); failing it removes the instance from rotation without killing it. A cache outage should *degrade* (slower) rather than fail readiness for the whole fleet, otherwise a shared dependency failure takes every instance out at once.

**6.** Origin traffic is the miss share: `1000 * (1 - 0.95) / (1 - 0.60) = 125 req/s` for the same user traffic (total 2,500 req/s: 40% miss = 1000 to origin; 5% miss = 125). The origin load drops 8 times.

**7.** Instances that stop abruptly cut in-flight requests, and the LB may still send traffic to an instance that is shutting down or not yet ready. **Readiness checks** (only route to ready instances) and **connection draining** with graceful shutdown (stop accepting, finish in-flight, then exit) prevent it.

**8.** Consistent hashing (with virtual nodes) so adding the sixth node moves only about 1/6 of the sessions; `hash % N` would remap about 5/6 and log most users out. Alternatives: store sessions in a shared database or use signed stateless tokens.

</details>

[Lesson](README.md) · [Summary](summary.md)
