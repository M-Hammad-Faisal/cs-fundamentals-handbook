# Concurrency, Synchronization and Deadlocks: Exercises

These problems go with the [Concurrency, Synchronization and Deadlocks lesson](README.md). Try each one before opening its solution.

## Problems

1. Show a lost-update race using 4 threads incrementing a shared counter, then fix it with a lock. Why does the unsafe version fail even in CPython?
2. Is this thread-safe? Explain and fix: `if key not in cache: cache[key] = compute(key)`.
3. Write a bounded producer/consumer with `queue.Queue(maxsize=3)`, two producers and two consumers, that shuts down cleanly.
4. Reproduce a two-lock deadlock (use timeouts so the demo ends) and fix it with a global lock order.
5. List the four Coffman conditions and, for the dining philosophers (5 forks), name a strategy breaking each one.
6. Implement a simple thread-safe `RateLimiter` allowing at most `N` calls running at once using a semaphore.
7. Explain why holding a lock while doing network I/O is dangerous.
8. When would you choose processes, threads or `asyncio` for: (a) 10,000 idle websockets, (b) image resizing, (c) a shared in-memory cache with frequent writes?

<details>
<summary>Solutions</summary>

**1.** See the lesson's `Counter`. The GIL only guarantees one bytecode runs at a time, not that a *read-modify-write* sequence is atomic, so threads interleave between the read and the write.

**2.** Not safe: two threads can both see the key missing and both compute (and one overwrites the other). Use a lock around the check and set, or `cache.setdefault(key, compute(key))` (still computes twice), or a per-key lock / `functools.lru_cache`.
```python
import threading
lock, cache = threading.Lock(), {}
def get(key, compute):
    with lock:
        if key not in cache:
            cache[key] = compute(key)
        return cache[key]
```

**3.**
```python
import queue, threading
q = queue.Queue(maxsize=3)
out, lock = [], threading.Lock()
def producer(start):
    for i in range(start, start + 5): q.put(i)
def consumer():
    while (x := q.get()) is not None:
        with lock: out.append(x)
ps = [threading.Thread(target=producer, args=(s,)) for s in (0, 100)]
cs = [threading.Thread(target=consumer) for _ in range(2)]
for t in ps + cs: t.start()
for t in ps: t.join()
for _ in cs: q.put(None)       # one sentinel per consumer
for t in cs: t.join()
print(sorted(out))
```

**4.** See `deadlock_demo` and `ordered_demo` in the lesson; the fix sorts the two locks (for example by `id`) before acquiring.

**5.** Mutual exclusion: let philosophers share forks when possible (rarely applicable). Hold and wait: pick up both forks atomically or none. No preemption: a philosopher who cannot get the second fork puts the first one down (try-lock with timeout). Circular wait: number the forks and always take the lower number first (or allow at most 4 philosophers at the table).

**6.**
```python
import threading
class Limiter:
    def __init__(self, n): self.sem = threading.Semaphore(n)
    def run(self, fn, *a):
        with self.sem:
            return fn(*a)
```

**7.** Other threads needing the lock stall for the full network latency (which is unbounded without timeouts), throughput collapses, and if the I/O path ever needs the same lock it deadlocks. Copy the data you need under the lock, release it, then do the I/O.

**8.** (a) `asyncio`: thousands of mostly idle connections, tiny memory each. (b) Processes: CPU-bound, so use all cores. (c) Threads with a lock (or a single owner task with a queue): shared mutable state; or an external store such as Redis if multiple processes need it.

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Race Conditions and Synchronization](01-race-conditions-and-synchronization.md) · [Deadlock](02-deadlock.md)
