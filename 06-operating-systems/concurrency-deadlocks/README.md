# Concurrency, Synchronization and Deadlocks

## Detailed lessons

1. [Race conditions and synchronization](01-race-conditions-and-synchronization.md): locks, semaphores, events, condition variables, producer-consumer, readers-writers
2. [Deadlock](02-deadlock.md): Coffman conditions, lock ordering, detection, Banker's algorithm, dining philosophers

The rest of this page is the quick reference.

## 1. The concept

**Concurrency** means several tasks make progress during overlapping time (possibly interleaved on one core). **Parallelism** means they literally run at the same instant on different cores. Both create the same hazard: tasks touching **shared mutable state** in an unpredictable order.

A **race condition** is a bug whose outcome depends on timing. The core of every fix is making a **critical section** (code touching shared state) run by one task at a time, or removing the sharing.

## 2. Race conditions

`counter += 1` is really *read, add, write*. Two threads can both read 5 and both write 6, losing an update.

```python
import threading, time, queue

class Counter:
    def __init__(self):
        self.value = 0
        self.lock = threading.Lock()
    def unsafe_inc(self):
        v = self.value
        time.sleep(0)            # yield: another thread may run between read and write
        self.value = v + 1
    def safe_inc(self):
        with self.lock:
            v = self.value
            time.sleep(0)
            self.value = v + 1

def run(method, threads=4, n=2000):
    c = Counter()
    ts = [threading.Thread(target=lambda: [getattr(c, method)() for _ in range(n)]) for _ in range(threads)]
    for t in ts: t.start()
    for t in ts: t.join()
    return c.value

print(run("unsafe_inc"))   # far below 8000 (lost updates)
print(run("safe_inc"))     # 8000
```

Even on CPython with the GIL this happens, because the GIL switches threads between bytecodes, not between your logical operations.

## 3. Synchronization tools

| Tool | Purpose |
|------|---------|
| **Mutex / Lock** | Mutual exclusion: one holder at a time |
| **RLock** | Re-entrant: the same thread may re-acquire it |
| **Semaphore** | Counter permitting up to `N` concurrent holders (connection pools, rate limits) |
| **Condition variable** | Wait until a predicate becomes true; `wait`/`notify` |
| **Event** | One-shot or resettable flag (start/stop signals) |
| **Barrier** | Wait until `N` tasks reach a point |
| **Queue** | Thread-safe hand-off; usually the best default |
| **Atomic operations** | Hardware-level indivisible updates (in Python, `queue`, `itertools.count`, or locks) |
| **Read-write lock** | Many readers or one writer |

### Producer / consumer with a bounded queue

```python
def pipeline(items, workers=3):
    q, results, lock = queue.Queue(maxsize=5), [], threading.Lock()
    def worker():
        while (item := q.get()) is not None:
            with lock:
                results.append(item * item)
    ts = [threading.Thread(target=worker) for _ in range(workers)]
    for t in ts: t.start()
    for i in items: q.put(i)
    for _ in ts: q.put(None)
    for t in ts: t.join()
    return sorted(results)
print(pipeline(range(10)))
```

The bounded `maxsize` gives **back-pressure**: fast producers block instead of exhausting memory. A `None` sentinel tells each worker to stop.

### Semaphore

```python
active, peak, guard = 0, 0, threading.Lock()
sem = threading.Semaphore(2)
def job():
    global active, peak
    with sem:
        with guard:
            active += 1; peak = max(peak, active)
        time.sleep(0.05)
        with guard:
            active -= 1
ts = [threading.Thread(target=job) for _ in range(8)]
for t in ts: t.start()
for t in ts: t.join()
print("peak", peak)
```

### Condition variable (a bounded buffer)

```python
class BoundedBuffer:
    def __init__(self, cap):
        self.items, self.cap, self.cv = [], cap, threading.Condition()
    def put(self, x):
        with self.cv:
            self.cv.wait_for(lambda: len(self.items) < self.cap)
            self.items.append(x); self.cv.notify_all()
    def get(self):
        with self.cv:
            self.cv.wait_for(lambda: self.items)
            x = self.items.pop(0); self.cv.notify_all(); return x
buf, got = BoundedBuffer(2), []
c = threading.Thread(target=lambda: [got.append(buf.get()) for _ in range(6)])
c.start()
for i in range(6): buf.put(i)
c.join(); print(got)
```

Always wait in a **predicate loop** (`wait_for`), because wakeups can be spurious and another thread may take the item first.

## 4. Deadlock

A **deadlock** is a set of tasks each waiting for a resource another holds, forever. It needs all four **Coffman conditions**:

1. **Mutual exclusion:** resources are held exclusively.
2. **Hold and wait:** a task holds one resource while waiting for another.
3. **No preemption:** resources cannot be forcibly taken.
4. **Circular wait:** a cycle of tasks each waiting on the next.

Break any one to prevent deadlock. The most practical: **impose a global lock order** (breaks circular wait), or use **timeouts / try-lock** (breaks no preemption) and retry.

```python
a, b = threading.Lock(), threading.Lock()
def deadlock_demo():
    def t1():
        with a:
            time.sleep(0.1)
            if b.acquire(timeout=0.2): b.release(); return "t1 ok"
            return "t1 gave up"
    def t2():
        with b:
            time.sleep(0.1)
            if a.acquire(timeout=1.0): a.release(); return "t2 ok"
            return "t2 gave up"
    out = []
    ts = [threading.Thread(target=lambda f=f: out.append(f())) for f in (t1, t2)]
    for t in ts: t.start()
    for t in ts: t.join()
    return sorted(out)
print(deadlock_demo())

def ordered_demo():
    out = []
    def worker(name, first, second):
        first, second = sorted((first, second), key=id)    # global lock order
        with first:
            time.sleep(0.1)
            with second:
                out.append(name)
    ts = [threading.Thread(target=worker, args=("t1", a, b)), threading.Thread(target=worker, args=("t2", b, a))]
    for t in ts: t.start()
    for t in ts: t.join()
    return sorted(out)
print(ordered_demo())
```

The first run shows two threads that each hold one lock and want the other (the timeouts only exist so the demo ends: `t1` gives up after 0.2 s, releases its lock, and `t2` then succeeds). The second run always completes because both threads take the locks in the same order.

Related hazards:
- **Livelock:** tasks keep reacting to each other and make no progress (two people sidestepping in a corridor); add randomized backoff.
- **Starvation:** one task never gets the resource (unfair locks, priority); use fair queues or aging.
- **Priority inversion:** see [scheduling](../scheduling/README.md).
- **Detection and avoidance:** databases detect cycles in a wait-for graph and abort a victim (see [transactions](../../05-databases/transactions-acid/README.md)); the banker's algorithm avoids unsafe states but is rare in practice.

## 5. Concurrency models

| Model | Idea | Python example |
|-------|------|----------------|
| Threads + locks | Shared memory, manual sync | `threading` |
| Message passing | No shared state; send messages | `queue`, `multiprocessing.Queue` |
| Event loop (async) | One thread, cooperative switching at `await` | `asyncio` |
| Processes | Isolation, true parallelism | `ProcessPoolExecutor` |
| Actors, STM | Higher-level isolation | Erlang, Clojure, Akka |

Prefer **sharing less**: immutable data, per-task state, and queues. Locks are for what remains.

## 6. Two real-world examples

### Example 1: Bank transfer deadlock
Thread A transfers 10 from account 1 to 2 and locks `1` then `2`; thread B transfers from 2 to 1 and locks `2` then `1`. Under load they deadlock. The standard fix is to always lock the account with the lower id first, which is exactly the ordered-lock demo above. Databases hit the same pattern with row locks and resolve it by killing one transaction.

### Example 2: A thread pool and a rate-limited API
A worker pool of 50 threads crawls pages but the target allows 5 concurrent requests. A `Semaphore(5)` around the request keeps the pool busy with parsing while respecting the limit; a bounded queue between fetchers and parsers prevents memory blow-up when parsing is slower.

## 7. Tips, tricks and pitfalls

- Hold locks for the **shortest** time, never across I/O or callbacks into unknown code.
- Always use `with lock:` so locks are released on exceptions.
- Do not rely on "it passed once": races are timing-dependent; stress tests and tools (ThreadSanitizer for native code) help.
- Check-then-act (`if key not in d: d[key] = ...`) is a race without a lock or an atomic method (`setdefault`).
- Do not hold lock A while calling code that may take lock B in the opposite order.
- Daemon threads are killed abruptly; shut workers down with sentinels or events.
- Async code still has races across `await` points when it shares state.

## 8. Check yourself

1. Why can `counter += 1` lose updates even with the GIL?
2. What are the four Coffman conditions? Which is easiest to break?
3. Difference between a mutex and a semaphore?
4. Why wait on a condition variable in a loop?
5. Deadlock vs livelock vs starvation?
6. Why is a bounded queue better than an unbounded one?
7. Concurrency versus parallelism?

<details>
<summary>Answers</summary>

1. It is read, add, write as separate steps; the interpreter can switch threads between them, so two threads can overwrite each other's result.
2. Mutual exclusion, hold and wait, no preemption, circular wait. Circular wait, by always acquiring locks in a fixed global order.
3. A mutex has one owner and protects a critical section; a semaphore counts permits and allows up to `N` holders (and can be released by a different task).
4. Wakeups can be spurious and the condition may be false again by the time you run; re-check the predicate.
5. Deadlock: nobody progresses and everybody is blocked. Livelock: tasks are active but stuck reacting to each other. Starvation: some task never gets its turn while others progress.
6. It applies back-pressure so producers slow down instead of consuming unbounded memory.
7. Concurrency is structuring work as overlapping tasks (possible on one core); parallelism is executing simultaneously on multiple cores.

</details>

[Exercises](exercises.md) · [Summary](summary.md)

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

Back to the [part overview](../README.md).
