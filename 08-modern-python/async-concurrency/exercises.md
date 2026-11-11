# Concurrency in Python: Exercises

These problems go with the [Concurrency in Python lesson](README.md). Try each one before opening its solution.

## Problems

1. Use `ThreadPoolExecutor` to "download" 10 URLs (each `time.sleep(0.1)`) and show total time is about 0.1 to 0.2 s, not 1 s.
2. Show that threads do not speed up CPU-bound pure Python: time `cpu_task(n)` four times sequentially versus in four threads.
3. Write an `async` function `fetch(name, delay)` and run five of them with `asyncio.gather`; then with a `TaskGroup`. Show the timing difference from running them one after another.
4. Add a **timeout** so that any fetch slower than 0.15 s becomes the string `"timeout"` instead of raising.
5. Limit concurrency to 3 simultaneous tasks with a `Semaphore` and prove the peak using a counter.
6. Implement a producer/consumer with `asyncio.Queue(maxsize=2)` and 3 consumers; stop them cleanly with sentinels.
7. This code is slow. Explain why and fix it:
   ```python
   async def main():
       for url in urls:
           await fetch(url)            # one at a time
   ```
8. A coroutine calls `requests.get(...)` (blocking). Show two ways to fix it without rewriting the library.
9. Cancel a running task and make it clean up (print "closing") before it ends. What must you do with `CancelledError`?
10. Choose a tool (asyncio, threads, processes) and justify: (a) scraping 20,000 pages, (b) computing SHA-256 of 500 large files, (c) calling a legacy blocking SOAP client in an async web app, (d) training a model on CPU in pure Python.

<details>
<summary>Solutions</summary>

**1.**
```python
import time
from concurrent.futures import ThreadPoolExecutor

def download(url):
    time.sleep(0.1)
    return url

urls = [f"u{i}" for i in range(10)]
start = time.perf_counter()
with ThreadPoolExecutor(10) as pool:
    done = list(pool.map(download, urls))
print(len(done), time.perf_counter() - start < 0.5)             # 10 True
```

**2.**
```python
def cpu_task(n):
    return sum(i * i for i in range(n))

start = time.perf_counter()
for _ in range(4):
    cpu_task(1_500_000)
sequential = time.perf_counter() - start

start = time.perf_counter()
with ThreadPoolExecutor(4) as pool:
    list(pool.map(cpu_task, [1_500_000] * 4))
threaded = time.perf_counter() - start
print(round(sequential, 2), round(threaded, 2))                 # about equal on a GIL build: no speedup
```

**3.**
```python
import asyncio

async def fetch(name, delay):
    await asyncio.sleep(delay)
    return name

async def main():
    start = time.perf_counter()
    r1 = await asyncio.gather(*(fetch(n, 0.1) for n in "abcde"))
    t_gather = time.perf_counter() - start
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch(n, 0.1)) for n in "abcde"]
    t_group = time.perf_counter() - start - t_gather
    start = time.perf_counter()
    for n in "abcde":
        await fetch(n, 0.1)                                      # one after another
    t_seq = time.perf_counter() - start
    print(r1, [t.result() for t in tasks], t_gather < 0.3, t_group < 0.3, t_seq > 0.45)

asyncio.run(main())
```

**4.**
```python
async def fetch_with_timeout(name, delay, limit=0.15):
    try:
        async with asyncio.timeout(limit):
            return await fetch(name, delay)
    except TimeoutError:
        return "timeout"

async def main():
    print(await asyncio.gather(fetch_with_timeout("fast", 0.05), fetch_with_timeout("slow", 0.5)))   # ['fast', 'timeout']

asyncio.run(main())
```

**5.**
```python
active = peak = 0

async def job(sem):
    global active, peak
    async with sem:
        active += 1
        peak = max(peak, active)
        await asyncio.sleep(0.02)
        active -= 1

async def main():
    sem = asyncio.Semaphore(3)
    await asyncio.gather(*(job(sem) for _ in range(12)))
    print(peak)                                                 # 3

asyncio.run(main())
```

**6.**
```python
async def producer(q, n_consumers):
    for i in range(8):
        await q.put(i)
    for _ in range(n_consumers):
        await q.put(None)                                       # one sentinel per consumer

async def consumer(q, out):
    while (item := await q.get()) is not None:
        await asyncio.sleep(0.001)
        out.append(item)

async def main():
    q, out = asyncio.Queue(maxsize=2), []
    await asyncio.gather(producer(q, 3), *(consumer(q, out) for _ in range(3)))
    print(sorted(out))                                          # [0, 1, 2, 3, 4, 5, 6, 7]

asyncio.run(main())
```

**7.** The loop awaits each fetch before starting the next, so total time is the sum of all waits. Start them together:
```python
async def main():
    results = await asyncio.gather(*(fetch(f"u{i}", 0.05) for i in range(6)))
    print(len(results))

asyncio.run(main())
```
(Add a `Semaphore` if you must limit concurrency.)

**8.** `await asyncio.to_thread(requests.get, url)` (run in a worker thread), or `await loop.run_in_executor(None, requests.get, url)`; the real fix is an async client such as `httpx.AsyncClient`.

**9.**
```python
async def worker():
    try:
        await asyncio.sleep(10)
    except asyncio.CancelledError:
        print("closing")
        raise                                                   # always re-raise after cleanup

async def main():
    task = asyncio.create_task(worker())
    await asyncio.sleep(0.01)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("task cancelled:", task.cancelled())

asyncio.run(main())                                             # closing / task cancelled: True
```

**10.** (a) `asyncio` with a semaphore and an async HTTP client (I/O-bound, huge concurrency). (b) Threads (hashlib releases the GIL for large buffers) or processes; both work, threads are lighter. (c) `asyncio.to_thread` (or a thread pool): blocking library, I/O-bound. (d) Processes (`ProcessPoolExecutor`/`multiprocessing`): CPU-bound pure Python needs separate interpreters (or move the heavy part to NumPy or C code).

</details>

[Lesson](README.md) · [Summary](summary.md)
