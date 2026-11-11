# Threads, Processes and Futures in Practice

**Prerequisites:** [processes and threads](../../06-operating-systems/processes-threads/README.md), [race conditions and synchronization](../../06-operating-systems/concurrency-deadlocks/01-race-conditions-and-synchronization.md), [the data model and the GIL](../internals/01-python-data-model-and-internals.md), [asyncio and concurrency overview](../async-concurrency/README.md). **You will learn:** how to choose between **threads, processes and asyncio**, how to use `concurrent.futures` (`ThreadPoolExecutor`, `ProcessPoolExecutor`, futures, `as_completed`, timeouts, exceptions), how to **measure** the I/O-bound and CPU-bound cases, how a **race condition** loses updates and how a **lock** fixes it, how to build a **producer-consumer** pipeline with `queue.Queue`, and how to **shut down cleanly**.

## 1. In plain words

Doing several things "at once" in Python means choosing a tool by asking **what is the program waiting for?**

- **Waiting for the outside world** (network, disk, a database): the CPU is idle, so overlap the waits. **Threads** or **asyncio** are enough.
- **Computing** (parsing, number crunching, compression): the CPU is the bottleneck. Because of the [GIL](../internals/01-python-data-model-and-internals.md), threads running Python code take turns, so you need **processes** (separate interpreters on separate cores) or native code that releases the GIL.

| Tool | Best for | Shares memory? | Cost to start | Beware |
|------|----------|----------------|---------------|--------|
| `threading` / `ThreadPoolExecutor` | I/O-bound, blocking libraries | yes (needs locks) | small | races; no CPU speed-up (with the GIL) |
| `multiprocessing` / `ProcessPoolExecutor` | CPU-bound | no (data is copied by pickling) | large (new interpreter) | arguments and results must be picklable; start-up cost |
| `asyncio` | thousands of concurrent I/O tasks | yes, single thread | tiny | every library must be async; one blocking call stalls all |

## 2. `concurrent.futures`: the high-level API

A **pool** runs functions on worker threads or processes. `submit` returns a **future** (a placeholder for a result that will arrive); `map` runs a function over many inputs and returns results **in input order**.

```python
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch(i):
    time.sleep(0.05)                                  # pretend network call: the thread is just waiting
    return i * i

start = time.perf_counter()
sequential = [fetch(i) for i in range(20)]
t_seq = time.perf_counter() - start

start = time.perf_counter()
with ThreadPoolExecutor(max_workers=10) as pool:
    threaded = list(pool.map(fetch, range(20)))       # 20 tasks on 10 threads
t_thr = time.perf_counter() - start

print("same results:", sequential == threaded)
print(f"I/O-bound speed-up with threads: {t_seq / t_thr:.0f}x  (large: waiting overlaps)")
print("speed-up is above 5x:", t_seq / t_thr > 5)
# same results: True
# I/O-bound speed-up with threads: 10x  (large: waiting overlaps)         (your number will differ)
# speed-up is above 5x: True
```

Twenty 50 ms waits take about one second one after another, but only about 0.1 s on ten threads, since the threads overlap their waiting.

### Futures, `as_completed`, timeouts and errors

```python
def work(n):
    time.sleep(0.01 * (5 - n))                        # task 0 is the slowest, task 4 the fastest
    if n == 3:
        raise ValueError("task 3 failed")
    return n

with ThreadPoolExecutor(max_workers=5) as pool:
    futures = {pool.submit(work, n): n for n in range(5)}
    finished_order, results, errors = [], {}, {}
    for fut in as_completed(futures):                 # yields each future as it FINISHES (not in submission order)
        n = futures[fut]
        finished_order.append(n)
        try:
            results[n] = fut.result()                 # re-raises the exception from the worker, if any
        except ValueError as exc:
            errors[n] = str(exc)

print("finished order (fastest first):", finished_order)
print("results:", dict(sorted(results.items())), "| errors:", errors)
# finished order (fastest first): [4, 3, 2, 1, 0]
# results: {0: 0, 1: 1, 2: 2, 4: 4} | errors: {3: 'task 3 failed'}
```

An exception inside a worker does **not** crash the program; it is stored in the future and **re-raised when you call `.result()`**. If you never call `.result()`, you never see it: always collect results. Useful controls: `fut.result(timeout=2)` raises `TimeoutError` if it takes too long (the work itself keeps running; you cannot kill a thread), `fut.cancel()` cancels a task that has not started, `fut.done()` checks without blocking, and `pool.shutdown(wait=True)` (done by the `with` block) waits for running tasks.

## 3. CPU-bound work: threads do not help, processes do

A pure-Python loop holds the GIL, so threads take turns. Processes each have their own interpreter and GIL. Here is a complete script (processes need an importable function and a `__main__` guard, so run it as a file, not interactively):

```python
# cpu_demo.py
import os, time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

def heavy(n):                                   # CPU-bound pure-Python work
    total = 0
    for i in range(n):
        total += i * i % 7
    return total

def timed(runner):
    start = time.perf_counter()
    result = runner()
    return time.perf_counter() - start, result

if __name__ == "__main__":
    jobs = [3_000_000] * 8
    t_seq, r1 = timed(lambda: [heavy(n) for n in jobs])
    with ThreadPoolExecutor(8) as pool:
        t_thr, r2 = timed(lambda: list(pool.map(heavy, jobs)))
    with ProcessPoolExecutor(8) as pool:
        t_proc, r3 = timed(lambda: list(pool.map(heavy, jobs)))
    print(f"sequential {t_seq:.2f}s | threads {t_thr:.2f}s | processes {t_proc:.2f}s")
    print("same answers:", r1 == r2 == r3)
    print("cpus:", os.cpu_count(), "| threads speed-up:", round(t_seq / t_thr, 1), "| processes speed-up:", round(t_seq / t_proc, 1))
# sequential 1.32s | threads 1.38s | processes 0.63s       (example run on an 8-core laptop; numbers vary)
# same answers: True
# cpus: 8 | threads speed-up: 1.0 | processes speed-up: 2.1
```

Threads: **no speed-up** (about 1.0x; the GIL lets one run at a time). Processes: a real speed-up, but well below 8x because **starting processes and sending arguments and results through pickling costs time**. That overhead means processes pay off only when each task is **substantial** (tens of milliseconds or more) and the data passed is small; use `chunksize` in `map` to batch many small tasks. On a **free-threaded** Python build (no GIL) threads can also speed up CPU work; check with `sys._is_gil_enabled()`.

Process-pool rules: functions and arguments must be **picklable** (module-level functions, not lambdas or nested functions); guard the entry point with `if __name__ == "__main__":` (on macOS and Windows, workers re-import your module); do not share mutable state (each worker has its own copy); for big arrays use `multiprocessing.shared_memory` or a library such as NumPy that releases the GIL.

## 4. Race conditions: shared memory needs locks

Threads share variables, and `counter += 1` is **three steps** (read, add, write), so two threads can interleave and lose an update. To make the bug reliable, this demo yields to other threads between the read and the write:

```python
import threading, time

class Counter:
    def __init__(self):
        self.value = 0
        self.lock = threading.Lock()

    def unsafe_increment(self):
        current = self.value                         # read
        time.sleep(0)                                # let another thread run: widens the race window
        self.value = current + 1                     # write (possibly overwriting someone else's update)

    def safe_increment(self):
        with self.lock:                              # only one thread at a time may run this block
            current = self.value
            time.sleep(0)
            self.value = current + 1

def hammer(method, threads=8, per_thread=500):
    def loop():
        for _ in range(per_thread):
            method()
    workers = [threading.Thread(target=loop) for _ in range(threads)]
    for w in workers: w.start()
    for w in workers: w.join()

unsafe, safe = Counter(), Counter()
hammer(unsafe.unsafe_increment)
hammer(safe.safe_increment)
print("expected 4000 | unsafe got fewer:", unsafe.value < 4000, "| safe got:", safe.value)
# expected 4000 | unsafe got fewer: True | safe got: 4000
```

The unsafe version silently **loses updates** (the exact number differs every run), which is what makes races so hard to debug. The lock makes the read-modify-write **atomic**. Guidelines:

- Prefer **not sharing**: pass data in and results out (queues, futures) rather than mutating shared variables.
- Keep critical sections **short**, and always use `with lock:` (never a bare `acquire` without a `finally`).
- Take multiple locks in a **consistent order** to avoid [deadlock](../../06-operating-systems/concurrency-deadlocks/02-deadlock.md).
- Standard types help: `queue.Queue` is thread-safe; `dict`/`list` single operations are atomic under the GIL but sequences of them are not.

## 5. Producer-consumer with `queue.Queue`

A queue between stages decouples fast producers from slow consumers and passes data safely. A **bounded** queue gives **backpressure**: producers block when it is full. A **sentinel** value tells consumers when to stop.

```python
import queue, threading

tasks = queue.Queue(maxsize=5)                       # bounded: put() blocks when 5 items are waiting
results = queue.Queue()
STOP = object()                                      # sentinel: "no more work"

def producer(n):
    for i in range(n):
        tasks.put(i)                                 # blocks if the queue is full (backpressure)
    for _ in range(3):
        tasks.put(STOP)                              # one stop signal per consumer

def consumer(name):
    while True:
        item = tasks.get()
        if item is STOP:
            break
        results.put((name, item * item))

consumers = [threading.Thread(target=consumer, args=(f"c{k}",)) for k in range(3)]
prod = threading.Thread(target=producer, args=(20,))
for t in consumers + [prod]:
    t.start()
for t in consumers + [prod]:
    t.join()

squares = sorted(v for _, v in list(results.queue))
print(len(squares), squares[:6], "| workers that did some work:", len({n for n, _ in results.queue}) >= 1)
# 20 [0, 1, 4, 9, 16, 25] | workers that did some work: True
```

All 20 items were processed exactly once, by whichever consumer was free. (`queue.Queue` also offers `task_done()`/`join()` to wait until every item has been **processed**, and `multiprocessing.Queue` is the cross-process equivalent.)

## 6. Clean shutdown with `threading.Event`

You cannot kill a Python thread from outside; ask it to stop and let it finish.

```python
import threading, time

stop = threading.Event()
ticks = []

def worker():
    while not stop.is_set():                          # check the flag between units of work
        ticks.append(time.monotonic())
        stop.wait(0.01)                               # sleeps, but wakes immediately when the event is set

t = threading.Thread(target=worker)
t.start()
time.sleep(0.05)
stop.set()                                            # request shutdown
t.join(timeout=1)
print("worker stopped cleanly:", not t.is_alive(), "| did some work:", len(ticks) >= 2)
# worker stopped cleanly: True | did some work: True
```

Mark background helpers as `daemon=True` only if losing them mid-task is harmless; otherwise stop and join them. Use `signal` handlers in the main thread to set the event on Ctrl+C.

## 7. Choosing: a decision guide

1. **Is the work waiting on I/O?** Use `ThreadPoolExecutor` for blocking libraries (`requests`, database drivers) or `asyncio` with async libraries for very many connections.
2. **Is it CPU-bound?** Use `ProcessPoolExecutor`, or move the hot loop to NumPy or another native library that releases the GIL; consider the free-threaded build for shared-memory parallelism.
3. **Is it a mix?** Pipeline it: threads or async for I/O, a process pool for the heavy step, connected by queues.
4. **Is each task tiny?** Concurrency overhead may exceed the work; batch tasks or measure before parallelising.
5. **Can you avoid shared state?** Then you can avoid locks.

Always **measure** (see [profiling](../performance-profiling/README.md)): add concurrency where a profile says time is spent waiting or computing, not by guesswork.

## 8. Common mistakes

- Using threads for CPU-bound pure-Python work and expecting speed-ups.
- Forgetting `if __name__ == "__main__":` with processes, causing recursive spawning on macOS and Windows.
- Passing lambdas, open files or database connections to a process pool (not picklable).
- Never calling `.result()`, silently losing worker exceptions.
- Unbounded thread creation (use a pool with `max_workers`) or unbounded queues.
- Sharing a database connection or `requests.Session` across threads without checking it is thread-safe.
- Sleeping in a loop to wait for another thread instead of using an `Event`, `Queue` or `Condition`.
- Holding a lock while doing slow I/O, which serialises everything.
- Assuming `list.append` from many threads is a design: use a queue.

## 9. Two real-world examples

**Example 1: The link checker.** A script that verified 5,000 URLs one after another took over an hour (almost all time waiting for servers). A `ThreadPoolExecutor(max_workers=50)` with a per-request timeout finished in under two minutes with the same code per URL, plus a small `as_completed` loop to gather failures.

**Example 2: The image thumbnailer.** A batch job resized 100,000 photos. Threads gave no speed-up (the resizing library held the GIL in Python-level loops), so the team switched to `ProcessPoolExecutor` with one worker per core and a `chunksize` of 50 files, and the job dropped from 6 hours to under 1, close to the number of cores.

## 10. Practice

1. Write `fetch_all(urls, fetch, workers=8, timeout=1.0)` that returns `{url: result_or_exception}` using futures, never raising for a single failure.
2. Re-run the counter demo with `threads=2` and `per_thread=5`. Does the unsafe version always lose updates with so little work? Why does that make races dangerous?
3. Describe the difference between ending consumers with a `STOP` sentinel and using `task_done()`/`join()`.
4. For a task of 1 ms of pure CPU, would you use a `ProcessPoolExecutor`? Estimate the break-even.
5. Give two ways to avoid a deadlock between two locks.
6. Explain why `pool.map` returns results in input order but `as_completed` does not.

<details>
<summary>Solutions</summary>

1. ```python
   def fetch_all(urls, fetch, workers=8, timeout=1.0):
       out = {}
       with ThreadPoolExecutor(max_workers=workers) as pool:
           futures = {pool.submit(fetch, u): u for u in urls}
           for fut in as_completed(futures):
               url = futures[fut]
               try:
                   out[url] = fut.result(timeout=timeout)
               except Exception as exc:
                   out[url] = exc
       return out
   res = fetch_all(["a", "b", "c"], lambda u: 1 // 0 if u == "b" else u.upper())
   print({k: (v if not isinstance(v, Exception) else type(v).__name__) for k, v in sorted(res.items())})
   # {'a': 'A', 'b': 'ZeroDivisionError', 'c': 'C'}
   ```
2. With only 10 increments the threads usually finish one after another and the result is correct; the bug appears only under real contention. That is why races survive testing and show up in production under load: you must prevent them by design (locks, queues, no sharing), not by testing alone.
3. `task_done()`/`join()` waits until all queued work has been *processed* without sentinels; a sentinel additionally tells consumers to exit. Use `join()` when you only need to wait for completion, a sentinel when workers must terminate.
4. Probably not: starting a process and sending the arguments costs on the order of milliseconds (more for the first task), so a 1 ms task is dominated by overhead. Batch many such tasks per call (`chunksize`) or use vectorised native code instead; processes pay off for tasks of tens of milliseconds and up.
5. Always acquire locks in the same global order; or use a single lock; or use `lock.acquire(timeout=...)` and back off; or avoid holding one lock while waiting for another.
6. `map` is defined to yield results in the order of the inputs (it waits for the first, then the second, and so on); `as_completed` yields each future the moment it finishes, so fast tasks appear first.

</details>

## 11. Check yourself

1. Which tool for I/O-bound work and which for CPU-bound work, and why?
2. What is a future, and what happens to an exception raised in a worker?
3. Why are process pools slower to start, and what must be true of their arguments?
4. How does a lock fix `counter += 1`?
5. What does a bounded queue give you?
6. How do you stop a thread cleanly?
7. What does `as_completed` do that `map` does not?

<details>
<summary>Answers</summary>

1. Threads or asyncio for I/O-bound work (waiting overlaps, the GIL is released while waiting); processes for CPU-bound work (each has its own interpreter and GIL).
2. A placeholder for a result that will arrive; the exception is stored and re-raised when you call `.result()` (so you must call it).
3. Each worker is a new interpreter and arguments and results are serialised; so arguments must be picklable (no lambdas, open files, connections).
4. It makes the read-modify-write sequence atomic: only one thread can be inside the critical section at a time.
5. Backpressure: producers block when consumers fall behind, bounding memory and latency.
6. Set an `Event` that the thread checks between units of work, then `join()` it.
7. It yields futures in completion order as they finish, rather than waiting in input order.

</details>

[Back to Modern Python](../README.md)
