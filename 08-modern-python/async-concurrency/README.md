# Concurrency in Python: Threads, Processes and asyncio

## 1. The concept

A program often **waits**: for the network, a disk, a database, a user. While it waits, the CPU sits idle. **Concurrency** is structuring a program so that it makes progress on many things during overlapping time. **Parallelism** is using multiple CPU cores at the same instant.

Python gives three main tools, each suited to a different kind of work:

| Tool | Model | Best for | Limits |
|------|-------|----------|--------|
| **`asyncio`** | One thread, cooperative tasks that `await` | Thousands of **I/O-bound** connections (web servers, API clients, crawlers) | Code must be async-aware; one blocking call stalls everything |
| **Threads** (`threading`, `ThreadPoolExecutor`) | OS threads sharing memory | I/O-bound work with **blocking libraries**; moderate concurrency | The **GIL** stops threads from running Python bytecode in parallel; shared-state bugs |
| **Processes** (`multiprocessing`, `ProcessPoolExecutor`) | Separate interpreters | **CPU-bound** work (parallelism on all cores) | Start-up and data-transfer cost; no shared memory by default |

Background on OS threads, locks and the GIL: [Operating systems: concurrency](../../06-operating-systems/concurrency-deadlocks/README.md) and [processes and threads](../../06-operating-systems/processes-threads/README.md).

### The GIL, honestly

CPython's **Global Interpreter Lock** lets only one thread execute Python bytecode at a time. So:

- Threads **do not speed up CPU-bound pure-Python code**.
- Threads **do** overlap **I/O waits** (the GIL is released while blocking on I/O).
- C extensions (NumPy, hashing, compression) often release the GIL, so threads can parallelize them.
- Python 3.13+ offers an optional **free-threaded build** (no GIL) and 3.14 adds `InterpreterPoolExecutor` for per-interpreter parallelism; check `sys._is_gil_enabled()`. Most code and libraries still assume the classic build, so choose processes for CPU parallelism unless you have verified otherwise.

```python
import sys
print(sys.version_info >= (3, 10), hasattr(sys, "_is_gil_enabled"))        # True True
```

### Quick decision guide

```text
Is the work mostly waiting (network, disk, DB)?
 ├─ yes: many thousands of connections / libraries support async  -> asyncio
 │       a few dozen, blocking libraries                          -> threads (ThreadPoolExecutor)
 └─ no (CPU-bound):  pure Python                                  -> processes (ProcessPoolExecutor)
                     NumPy/C code that releases the GIL           -> threads may be enough
```

## 2. Threads and thread pools

```python
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch(url):
    time.sleep(0.2)                     # stands in for a network call
    return f"data from {url}"

urls = [f"https://example.test/{i}" for i in range(8)]

start = time.perf_counter()
results = [fetch(u) for u in urls]                              # sequential
sequential = time.perf_counter() - start

start = time.perf_counter()
with ThreadPoolExecutor(max_workers=8) as pool:
    results2 = list(pool.map(fetch, urls))                      # concurrent: the waits overlap
threaded = time.perf_counter() - start

print(results == results2, sequential > 1.5, threaded < 0.6)    # True True True

with ThreadPoolExecutor(4) as pool:
    futures = {pool.submit(fetch, u): u for u in urls[:3]}
    for fut in as_completed(futures):                           # handle results as they finish
        print(futures[fut][-1], fut.result()[:9])
```

`Future` objects represent results that will arrive; `result()` re-raises the worker's exception. Always create pools with `with` so threads are shut down. The OS-level hazards (races, locks, deadlocks) are in [concurrency and deadlocks](../../06-operating-systems/concurrency-deadlocks/README.md).

## 3. Processes for CPU-bound work

```python
from concurrent.futures import ProcessPoolExecutor
import time

def cpu_task(n):
    return sum(i * i for i in range(n))

if __name__ == "__main__":                                      # required for multiprocessing on macOS/Windows
    jobs = [12_000_000] * 4

    start = time.perf_counter()
    [cpu_task(n) for n in jobs]
    serial = time.perf_counter() - start

    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=4) as pool:
        list(pool.map(cpu_task, jobs))
    parallel = time.perf_counter() - start
    print(f"serial {serial:.2f}s, 4 processes {parallel:.2f}s")  # faster on a multi-core machine once jobs are big enough
```

Notes: tiny jobs are not worth it because starting processes has a cost (try `[200_000] * 4` and compare); arguments and results are **pickled** (sent between processes), so keep them small and picklable; start-up has a cost, so batch work (`chunksize`); use `if __name__ == "__main__":`.

## 4. `asyncio` fundamentals

`asyncio` runs **many tasks on one thread**. A task runs until it hits an `await` on something that must wait; then the **event loop** switches to another task. Switching happens **only at `await` points** (cooperative multitasking), so no locks are needed for simple shared state, but a task that never awaits blocks everyone.

### Coroutines and `await`

```python
import asyncio

async def greet(name, delay):
    await asyncio.sleep(delay)          # a non-blocking wait: other tasks run meanwhile
    return f"hello {name}"

async def main():
    print(await greet("ana", 0.01))     # await a coroutine: run it and get its result

asyncio.run(main())                      # create the event loop, run main(), close the loop
```

Calling `greet("ana", 1)` does **not** run it; it returns a coroutine object. You must `await` it or schedule it as a task.

### Running things concurrently

```python
import asyncio, time

async def fetch(name, delay):
    await asyncio.sleep(delay)
    return f"{name} done"

async def main():
    start = time.perf_counter()
    results = await asyncio.gather(fetch("a", 0.2), fetch("b", 0.2), fetch("c", 0.2))
    elapsed = time.perf_counter() - start
    print(results, elapsed < 0.4)       # ['a done', 'b done', 'c done'] True   (0.2 s total, not 0.6 s)

asyncio.run(main())
```

### Tasks and `TaskGroup` (structured concurrency, 3.11+)

```python
import asyncio

async def worker(n):
    await asyncio.sleep(0.01 * n)
    if n == 3:
        raise ValueError("bad job")
    return n * 10

async def main():
    # TaskGroup: if one task fails, the rest are cancelled and the errors surface together
    try:
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(worker(n)) for n in (1, 2, 3, 4)]
    except* ValueError as eg:                                    # except* handles an ExceptionGroup
        print("failed:", [str(e) for e in eg.exceptions])        # failed: ['bad job']

    async with asyncio.TaskGroup() as tg:                        # all succeed: results from the tasks
        ok = [tg.create_task(worker(n)) for n in (1, 2)]
    print([t.result() for t in ok])                              # [10, 20]

asyncio.run(main())
```

`asyncio.gather(*coros, return_exceptions=True)` collects results **and** exceptions instead of raising the first one. Prefer `TaskGroup` for new code: tasks cannot be forgotten or leak.

### Timeouts and cancellation

```python
import asyncio

async def slow():
    try:
        await asyncio.sleep(10)
    except asyncio.CancelledError:
        print("cleaning up")             # cancellation is an exception raised at the await point
        raise                            # always re-raise CancelledError

async def main():
    try:
        async with asyncio.timeout(0.05):                       # 3.11+
            await slow()
    except TimeoutError:
        print("timed out")

asyncio.run(main())                      # cleaning up  /  timed out
```

### Limiting concurrency: `Semaphore`

```python
import asyncio

active, peak = 0, 0

async def limited(sem, i):
    global active, peak
    async with sem:                       # at most N inside at once
        active += 1
        peak = max(peak, active)
        await asyncio.sleep(0.02)
        active -= 1

async def main():
    sem = asyncio.Semaphore(3)
    await asyncio.gather(*(limited(sem, i) for i in range(10)))
    print("peak concurrency:", peak)      # peak concurrency: 3

asyncio.run(main())
```

Use a semaphore to respect API rate limits or database connection caps while still launching many tasks.

### Producer / consumer with `asyncio.Queue`

```python
import asyncio

async def producer(q):
    for i in range(5):
        await q.put(i)
    await q.put(None)                     # sentinel: no more work

async def consumer(q, out):
    while (item := await q.get()) is not None:
        out.append(item * item)

async def main():
    q, out = asyncio.Queue(maxsize=2), []                       # bounded: back-pressure on the producer
    await asyncio.gather(producer(q), consumer(q, out))
    print(out)                            # [0, 1, 4, 9, 16]

asyncio.run(main())
```

### Async context managers and iterators

```python
import asyncio

class Connection:
    async def __aenter__(self):
        await asyncio.sleep(0)            # pretend to connect
        print("connected")
        return self
    async def __aexit__(self, exc_type, exc, tb):
        print("closed")
    async def rows(self):                 # an async generator
        for i in range(3):
            await asyncio.sleep(0)
            yield {"id": i}

async def main():
    async with Connection() as conn:
        ids = [row["id"] async for row in conn.rows()]          # async comprehension
        print(ids)

asyncio.run(main())                       # connected / [0, 1, 2] / closed
```

## 5. The #1 asyncio mistake: blocking the event loop

A blocking call inside a coroutine freezes **every** task until it finishes.

```python
import asyncio, time

async def bad():
    time.sleep(0.2)                       # BLOCKS the whole loop (use await asyncio.sleep)

async def ticker(log):
    for _ in range(3):
        log.append("tick")
        await asyncio.sleep(0.05)

async def main():
    log = []
    await asyncio.gather(ticker(log), bad())
    print(len(log))                       # 3, but the ticks were delayed by the blocking call

asyncio.run(main())
```

Fixes for blocking code:

```python
import asyncio, time

def blocking_io():                        # a legacy library call, or CPU work
    time.sleep(0.1)
    return "result"

async def main():
    result = await asyncio.to_thread(blocking_io)                # run in a worker thread (3.9+)
    print(result)                                                # result
    loop = asyncio.get_running_loop()
    # CPU-bound: await loop.run_in_executor(process_pool, cpu_function, arg)

asyncio.run(main())
```

Rules: use **async libraries** for I/O (`httpx`/`aiohttp`, `asyncpg`, `aiosqlite`), `asyncio.to_thread` for unavoidable blocking calls, and a **process pool** for CPU-bound work. Never call `asyncio.run` inside a running loop; use `await`.

## 6. A real async network example: many clients, one thread

```python
import asyncio

async def handle(reader, writer):
    data = await reader.readline()
    writer.write(data.upper())
    await writer.drain()
    writer.close()
    await writer.wait_closed()

async def client(port, i):
    reader, writer = await asyncio.open_connection("127.0.0.1", port)
    writer.write(f"hello {i}\n".encode())
    await writer.drain()
    reply = await reader.readline()
    writer.close()
    await writer.wait_closed()
    return reply.decode().strip()

async def main():
    server = await asyncio.start_server(handle, "127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]
    async with server:
        replies = await asyncio.gather(*(client(port, i) for i in range(20)))
    print(len(replies), replies[:2])      # 20 ['HELLO 0', 'HELLO 1']

asyncio.run(main())
```

Twenty simultaneous connections are served by **one thread**; this is how async web servers and bots handle many thousands of clients.

## 7. Threads, processes and async: comparison

| | Threads | Processes | asyncio |
|--|---------|-----------|---------|
| Memory per unit | MBs (stack) | tens of MBs (interpreter) | KBs (a task) |
| Typical max concurrency | hundreds | cores x few | tens of thousands |
| Shared state | yes (needs locks) | no (IPC) | yes, but switches only at `await` |
| CPU parallelism | no (GIL) | **yes** | no |
| Debugging | races, nondeterminism | pickling errors | forgotten `await`, blocking calls |
| Needs async-aware libraries | no | no | **yes** |

You can combine them: an async server that offloads CPU work to a process pool and blocking calls to threads.

## 8. Two real-world examples

### Example 1: A crawler checking 5,000 URLs
Sequentially at 300 ms each that is 25 minutes. With `asyncio` and a `Semaphore(50)` (be polite to servers) plus `httpx.AsyncClient`, the same crawl takes about 30 seconds on one thread. Each task awaits the network, and the loop interleaves them. Timeouts (`asyncio.timeout`) stop slow sites from stalling the batch, and a `TaskGroup` ensures nothing leaks.

### Example 2: A web API with a CPU-heavy endpoint
A FastAPI app (async) serves lots of light requests. One endpoint resizes images (CPU-bound). Running that inline would freeze all requests, so the handler does `await loop.run_in_executor(process_pool, resize, data)`. Other requests keep flowing while the resize runs on another core. Database calls use an async driver; a legacy PDF library (blocking) is wrapped with `asyncio.to_thread`.

## 9. Tips, tricks and pitfalls

- Always `await` coroutines; a never-awaited coroutine does nothing (Python warns: "coroutine ... was never awaited").
- Do not block the loop: no `time.sleep`, `requests.get`, heavy loops or big `json.loads` inside `async def` without offloading.
- Prefer `TaskGroup` (3.11+) to bare `create_task`; keep a reference to tasks you create (they can be garbage-collected).
- Always re-raise `asyncio.CancelledError` after cleanup.
- Use `asyncio.Semaphore` / bounded `Queue` for back-pressure; unbounded concurrency overwhelms servers and memory.
- Set **timeouts** on every external call (`asyncio.timeout`, library timeouts).
- Do not share one blocking resource (a sqlite connection, a socket) between threads without protection.
- `multiprocessing` needs `if __name__ == "__main__":` and picklable functions (no lambdas/closures).
- For processes, minimize data passed between them; return summaries, not huge objects.
- Measure before choosing: more concurrency is not automatically faster (context-switch and coordination costs).
- Do not mix `asyncio.run()` calls inside running loops; in notebooks use `await` directly.

## 10. Check yourself

1. Concurrency versus parallelism?
2. When do threads help in Python, and when do they not?
3. What does `await` do to the running task and the event loop?
4. What is the difference between calling a coroutine function and awaiting it?
5. Why is `time.sleep` inside `async def` a bug?
6. What does `asyncio.gather` do compared with `TaskGroup`?
7. How do you limit the number of concurrent requests in asyncio?
8. Which tool for: 10,000 idle websockets; resizing 1,000 images; calling a blocking legacy library from an async app?
9. Why must `multiprocessing` code use `if __name__ == "__main__":`?

<details>
<summary>Answers</summary>

1. Concurrency is making progress on several tasks during overlapping time (possibly on one core); parallelism is executing simultaneously on multiple cores.
2. Threads help for I/O-bound work (the GIL is released while waiting) and for C code that releases the GIL; they do not speed up CPU-bound pure Python because of the GIL.
3. It suspends the current task until the awaited thing is ready and lets the event loop run other tasks meanwhile.
4. Calling returns a coroutine object without running it; awaiting (or scheduling as a task) actually runs it and returns its result.
5. It blocks the whole thread and therefore the event loop, freezing all other tasks; use `await asyncio.sleep`.
6. `gather` runs awaitables concurrently and returns results (first exception propagates unless `return_exceptions=True`); `TaskGroup` provides structured concurrency: all tasks are tied to a scope, one failure cancels the others and errors are grouped.
7. With an `asyncio.Semaphore` (or a bounded queue with a fixed number of workers).
8. Idle websockets: `asyncio`. Image resizing: a process pool. Blocking legacy library: `asyncio.to_thread` (or a thread pool).
9. On platforms using the spawn start method (macOS, Windows, and increasingly Linux defaults) child processes re-import the main module; without the guard they would recursively start new processes.

</details>

[Exercises](exercises.md) · [Summary](summary.md)
