# Threads and the GIL Lab

**Prerequisites:** [processes in practice](01-processes-in-practice.md), [race conditions and synchronization](../concurrency-deadlocks/01-race-conditions-and-synchronization.md). **You will learn (by measuring on your own machine):** how to create and manage **threads** in Python; what the **Global Interpreter Lock (GIL)** is and why CPython has one; why threads **do not speed up CPU-bound Python** but **do** help **I/O-bound work and some C-level work like hashing**; how to get real parallelism with **processes**; what **is and is not atomic** under the GIL (with a race you can reproduce); what **free-threaded Python** changes; and a decision guide. The timing results below are from one 8-core laptop; yours will differ in size but not in shape.

## 1. Threads in plain words

A **thread** is a separate line of execution **inside one process**. Threads share the process's memory (variables, open files) but each has its own call stack. That makes them cheap to start and easy to share data between, and also the source of **race conditions** when they touch the same data.

```python
import threading, time

def greet(name, delay):
    time.sleep(delay)
    print(f"hello from {name} (thread {threading.current_thread().name})")

t1 = threading.Thread(target=greet, args=("A", 0.05), name="worker-1")
t2 = threading.Thread(target=greet, args=("B", 0.01), name="worker-2")
t1.start(); t2.start()
t1.join(); t2.join()                          # wait for both to finish
# hello from B (thread worker-2)
# hello from A (thread worker-1)             (B finishes first: it sleeps less)
print(threading.active_count())               # 1   (only the main thread remains)
```

Basics to know:

- `start()` begins running; `join()` waits (add `timeout=` to avoid waiting forever).
- A **daemon** thread (`daemon=True`) is killed abruptly when the program exits; use it only for background work you do not mind losing.
- A thread **cannot be killed from outside** in Python: ask it to stop with a flag or an `Event` and have it check regularly.
- Return values and exceptions: a plain `Thread` swallows the return value and prints an exception to stderr without telling the starter. **`concurrent.futures.ThreadPoolExecutor`** gives you results and re-raises exceptions in the caller:

```python
from concurrent.futures import ThreadPoolExecutor

def risky(n):
    if n == 3:
        raise ValueError("three is unlucky")
    return n * n

with ThreadPoolExecutor(max_workers=4) as pool:
    futures = [pool.submit(risky, n) for n in range(5)]
    results = []
    for f in futures:
        try:
            results.append(f.result())             # result() re-raises the worker's exception here
        except ValueError as e:
            results.append(f"error: {e}")
print(results)                                      # [0, 1, 4, 'error: three is unlucky', 16]
```

Stopping a thread politely, and per-thread storage:

```python
stop = threading.Event()
ticks = []

def ticker():
    while not stop.is_set():
        ticks.append(1)
        stop.wait(0.01)                             # sleeps, but wakes immediately when stop is set

worker = threading.Thread(target=ticker)
worker.start()
time.sleep(0.05)
stop.set(); worker.join()
print(0 < len(ticks) < 20, worker.is_alive())       # True False

local = threading.local()                           # each thread sees its own attributes
seen = {}
def remember(label):
    local.value = label
    time.sleep(0.01)
    seen[label] = local.value                       # still my own value, even though others ran in between
threads = [threading.Thread(target=remember, args=(i,)) for i in range(3)]
for th in threads: th.start()
for th in threads: th.join()
print(seen)                                         # {0: 0, 1: 1, 2: 2}
```

## 2. What is the GIL?

CPython (the standard Python) manages memory with **reference counting**: every object has a counter that goes up and down as references appear and disappear, and the object is freed at zero. If two threads changed a counter at the same instant, the count could end up wrong, leading to crashes or leaks. The simplest fix, chosen in the early 1990s, was one big lock: the **Global Interpreter Lock (GIL)**. **Only one thread executes Python bytecode at a time.** Threads take turns, switching about every 5 milliseconds.

```python
import sys

print(sys.getswitchinterval())                      # 0.005    seconds before a running thread is asked to give up the GIL
print(sys._is_gil_enabled() if hasattr(sys, "_is_gil_enabled") else "GIL always on (Python before 3.13)")      # True on the standard build
```

Consequences:

| Work | Threads help? | Why |
|------|:---:|-----|
| **Waiting** (network, disk, `time.sleep`, database calls) | **yes** | a thread waiting in the OS **releases the GIL**, so others run |
| **C code that releases the GIL** (hashing, compression, NumPy, `re` on big inputs, image libraries) | **yes** | the heavy loop runs outside the interpreter |
| **Pure-Python computation** | **no** | only one thread runs bytecode at a time; switching adds overhead |

(The GIL protects the **interpreter**, not **your data**: you still need locks, as section 5 shows.)

## 3. Experiments: when do threads help?

A tiny helper that times a function run serially and across 4 threads:

```python
import hashlib, os

def timed(fn):
    start = time.perf_counter()
    fn()
    return time.perf_counter() - start

def serial(task, times=4):
    return timed(lambda: [task() for _ in range(times)])

def threaded(task, times=4):
    def run():
        workers = [threading.Thread(target=task) for _ in range(times)]
        for w in workers: w.start()
        for w in workers: w.join()
    return timed(run)
```

### Experiment 1: CPU-bound pure Python (threads do NOT help)

```python
def cpu_task():
    total = 0
    for i in range(2_000_000):
        total += i * i

cpu_serial, cpu_threads = serial(cpu_task), threaded(cpu_task)
print(round(cpu_threads / cpu_serial, 2))           # about 1.0: four threads took about as long as running them one after another (a 4-core speedup would give 0.25)
print(cpu_threads > 0.5 * cpu_serial)               # True   (no meaningful speedup; on some machines threads are even slower)
```

### Experiment 2: I/O-bound waiting (threads help a lot)

```python
def io_task():
    time.sleep(0.2)                                 # stands in for a network request or disk read

io_serial, io_threads = serial(io_task), threaded(io_task)
print(round(io_serial, 1), round(io_threads, 1))    # 0.8 0.2
print(io_threads < 0.5 * io_serial)                 # True   (the four waits overlap)
```

### Experiment 3: C code that releases the GIL (threads help)

`hashlib` releases the GIL while hashing large buffers, so threads run in parallel:

```python
data = os.urandom(20_000_000)

def hash_task():
    hashlib.sha256(data).digest()

hash_serial, hash_threads = serial(hash_task), threaded(hash_task)
print(round(hash_serial / hash_threads, 1))         # about 3.7 on an 8-core laptop: a large speedup from threads
print(hash_threads < hash_serial)                   # True   (on a multi-core machine)
```

This is why NumPy, `zlib`, image libraries and many others scale with threads despite the GIL: the **heavy lifting happens in C with the lock released**.

### Experiment 4: processes (true parallelism for CPU-bound Python)

Each process has its own interpreter and its own GIL. Process pools need an importable `__main__` module, so we write a small script and run it:

```python
import subprocess, sys, tempfile, textwrap, pathlib

script = textwrap.dedent('''
    import time
    from concurrent.futures import ProcessPoolExecutor

    def cpu_task(_):
        total = 0
        for i in range(2_000_000):
            total += i * i
        return total

    if __name__ == "__main__":
        start = time.perf_counter()
        for _ in range(4):
            cpu_task(0)
        serial = time.perf_counter() - start
        with ProcessPoolExecutor(4) as pool:
            list(pool.map(cpu_task, range(4)))               # warm-up: start the workers
            start = time.perf_counter()
            list(pool.map(cpu_task, range(4)))
            parallel = time.perf_counter() - start
        print(round(serial / parallel, 1))
''')
path = pathlib.Path(tempfile.mkdtemp()) / "processes.py"
path.write_text(script)
speedup = float(subprocess.run([sys.executable, str(path)], capture_output=True, text=True).stdout)
print(speedup)                                      # 3.7 here (about 3 to 4 on a multi-core laptop)
print(speedup > 1.3)                                # True   (on a machine with 2 or more cores)
```

Summary of the four experiments on this laptop: CPU-bound threads 1.0x, waiting 4.0x, hashing 3.7x, processes 3.7x. The shape is stable across machines even when the numbers move.

**The cost of processes:** startup time, memory per process, and data must be **pickled** between them; a thread shares memory for free. Choose per task: [processes in practice](01-processes-in-practice.md) has the decision table.

## 4. Why threads still make sense

With these limits, why use threads at all?

1. **I/O concurrency** (web scraping, API calls, database queries, file transfers): the wait dominates, so even a few dozen threads give large speedups with simple blocking code.
2. **GUIs and servers** keep a responsive main thread while work happens in the background.
3. **Libraries that release the GIL** (hashing, compression, array math) scale across cores.
4. **Shared state** is easier than inter-process communication when the work is light.

For *thousands* of I/O connections, [`asyncio`](../../08-modern-python/async-concurrency/README.md) (one thread, cooperative tasks) scales better than a thread per connection.

## 5. What the GIL does NOT protect: races

The GIL makes individual bytecode instructions safe, but a Python line like `counter += 1` is **several** instructions. A thread switch can land between them:

```python
import dis

def increment():
    global counter
    counter += 1

counter = 0
dis.dis(increment)                                  # LOAD_GLOBAL counter ... BINARY_OP (+=) ... STORE_GLOBAL counter   (read, add, write: three steps)
```

### An honest note about reproducing the textbook race

On recent CPython versions the interpreter only checks for a thread switch at certain points (function calls, loop back-edges), so the plain loop below usually gives the right answer **even though it is not guaranteed to**:

```python
sys.setswitchinterval(1e-6)                         # ask for very frequent switching to provoke a race
counter = 0

def bump(n):
    global counter
    for _ in range(n):
        counter += 1

workers = [threading.Thread(target=bump, args=(100_000,)) for _ in range(4)]
for w in workers: w.start()
for w in workers: w.join()
print(counter)                                      # 400000 on CPython 3.15 here (this is luck of the implementation, NOT a promise)
sys.setswitchinterval(0.005)
```

The language **does not promise** `+=` is atomic. Older versions, other implementations (PyPy, Jython) and **free-threaded builds** lose updates with this exact code. Never rely on today's lucky behavior.

### A race you can always reproduce

When the read and the write are separated by anything that can **yield** (I/O, a call that releases the GIL, `time.sleep(0)`), updates are lost reliably:

```python
total = 0

def racy_add(n):
    global total
    for _ in range(n):
        current = total                              # read
        time.sleep(0)                                # any yield point here (a call, I/O, a log line) lets another thread run
        total = current + 1                          # write a stale value

workers = [threading.Thread(target=racy_add, args=(2_000,)) for _ in range(4)]
for w in workers: w.start()
for w in workers: w.join()
print(total, "of", 8_000)                            # a small fraction, for example 2400 of 8000: most increments were lost
print(total < 8_000)                                 # True
```

The fix is the same as before: make the read-modify-write one critical section.

```python
total, lock = 0, threading.Lock()

def safe_add(n):
    global total
    for _ in range(n):
        with lock:
            current = total
            time.sleep(0)                            # even with a yield inside, nobody else can enter the critical section
            total = current + 1

workers = [threading.Thread(target=safe_add, args=(500,)) for _ in range(4)]
for w in workers: w.start()
for w in workers: w.join()
print(total)                                         # 2000   (always exact)
```

### Which operations are atomic?

Single bytecode-level operations on built-in types are effectively atomic under the GIL: `list.append`, `dict[key] = value`, `x = y`, `list.pop()`. **Compound** operations are not: `x += 1`, `if key not in d: d[key] = compute()` (check-then-act), `d[key] += 1`.

```python
cache = {}
calls = []

def get_or_compute(key):
    if key not in cache:                             # check ...
        time.sleep(0.001)                            # ... another thread may pass the same check here ...
        calls.append(key)
        cache[key] = key * 2                         # ... and then both compute: duplicated work (or worse, duplicated side effects)
    return cache[key]

workers = [threading.Thread(target=get_or_compute, args=(7,)) for _ in range(5)]
for w in workers: w.start()
for w in workers: w.join()
print(len(calls) > 1)                                # True   the expensive step ran several times for one key
```

Fixes: hold a lock around check-and-compute, use `dict.setdefault` or `functools.lru_cache` (which is thread-safe for the cache structure, though the function may still run twice on a simultaneous miss), or compute once up front.

## 6. Deadlock and lock hygiene in threads (reminder)

Two locks taken in opposite orders deadlock ([deadlock lesson](../concurrency-deadlocks/02-deadlock.md)). Habits: hold locks briefly, take multiple locks in a fixed order, use `with`, prefer `queue.Queue` to pass work between threads (it does the locking for you), and prefer **not sharing mutable state** at all.

```python
import queue

jobs, results = queue.Queue(), queue.Queue()

def worker():
    while True:
        item = jobs.get()
        if item is None:                             # sentinel: no more work
            break
        results.put(item * item)

pool = [threading.Thread(target=worker) for _ in range(3)]
for th in pool: th.start()
for n in range(10): jobs.put(n)
for _ in pool: jobs.put(None)                        # one sentinel per worker
for th in pool: th.join()
print(sorted(results.get() for _ in range(10)))      # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
```

## 7. Free-threaded Python (no GIL)

Python 3.13 introduced an **experimental free-threaded build** (a separate interpreter, usually named `python3.13t`), and 3.14 made it officially supported. In it, threads really run Python code **in parallel on multiple cores**. What that means:

- CPU-bound threaded code can scale with the number of cores.
- **Unsynchronized code breaks more often**: races that the GIL happened to hide now appear. Correct locking becomes essential.
- Single-thread code runs a little slower (some percent), and **C extension modules must be rebuilt or marked as safe** for free-threading; the ecosystem is catching up.

```python
import sysconfig

print(sysconfig.get_config_var("Py_GIL_DISABLED") in (None, 0))      # True on the standard build; 1 on a free-threaded build
print(sys._is_gil_enabled())                          # True here; a free-threaded build can report False
```

Practical advice today: use the standard build for production unless you have measured a benefit, write thread-safe code regardless (it will keep working when free-threading becomes the default), and keep using processes or native libraries for CPU-heavy parallelism.

## 8. Choosing a concurrency tool

| Workload | Best tool | Why |
|----------|-----------|-----|
| Many slow I/O calls, moderate count (up to hundreds) | `ThreadPoolExecutor` | simple blocking code; the GIL is released while waiting |
| Thousands of I/O connections | `asyncio` | one thread, tiny memory per task |
| CPU-bound pure Python | `ProcessPoolExecutor` / `multiprocessing` | one GIL per process |
| CPU-bound array or numeric work | NumPy/Numba/Cython (releases the GIL), then threads or processes | the loop runs in C |
| Hashing, compression, image decode of large buffers | threads | libraries release the GIL |
| Isolation, untrusted code, crash containment | processes | separate memory |
| Truly shared fine-grained state with CPU work | free-threaded build (experimental) or redesign | the GIL would serialize it |

## 9. Two real-world examples

**Example 1: A web scraper.** Fetching 500 pages one by one takes 500 times the latency of a request; a `ThreadPoolExecutor(20)` finishes in roughly 500/20 times that, with ordinary blocking `requests` code and no `asyncio` rewrite. The GIL is irrelevant because each thread spends nearly all its time waiting on the network.

**Example 2: Hashing and compressing uploads.** A service computes SHA-256 and gzips every uploaded file. Running these in a thread pool uses all cores because `hashlib` and `zlib` release the GIL, whereas the same work written in pure Python would crawl on one core, no matter how many threads.

## 10. Common mistakes

- Expecting more threads to speed up CPU-bound pure Python.
- Assuming the GIL makes your code thread-safe because a demo "worked" on your machine.
- Check-then-act on shared dicts and lists without a lock.
- Starting a thread per task without a bound (use a pool).
- Daemon threads that hold resources (files, locks) and are killed mid-write at exit.
- Blocking forever with `join()`/`get()` and no timeout.
- Forgetting that an exception inside a plain thread does not stop or inform the main thread.
- Using threads where `asyncio` or processes fit better, or `multiprocessing` code without `if __name__ == "__main__":`.

## 11. Practice

1. Which of these gain from threads in standard CPython: (a) downloading 50 files, (b) a pure-Python prime sieve for 20 million numbers, (c) hashing 8 big files with `hashlib`, (d) summing a list with a Python `for` loop?
2. Use `ThreadPoolExecutor` to run `time.sleep(0.1)` ten times and show the elapsed time is about 0.1 to 0.3 s instead of 1 s.
3. Make the `get_or_compute` function compute each key at most once by adding a lock. Show `len(calls) == 1`.
4. Why is `list.append` safe across threads but `counter += 1` is not?
5. Convert experiment 1 to use `ProcessPoolExecutor` (in a script) and report the speedup.
6. What changes if you run `racy_add` on a free-threaded build?
7. How would you stop a worker thread that loops forever?

<details>
<summary>Solutions</summary>

1. (a) yes (waiting on the network), (b) no, (c) yes (`hashlib` releases the GIL), (d) no.
2. ```python
   start = time.perf_counter()
   with ThreadPoolExecutor(10) as pool:
       list(pool.map(lambda _: time.sleep(0.1), range(10)))
   elapsed = time.perf_counter() - start
   print(round(elapsed, 1), elapsed < 0.5)                         # 0.1 True
   ```
3. ```python
   cache, calls, guard = {}, [], threading.Lock()
   def get_or_compute_once(key):
       with guard:
           if key not in cache:
               time.sleep(0.001)
               calls.append(key)
               cache[key] = key * 2
       return cache[key]
   workers = [threading.Thread(target=get_or_compute_once, args=(7,)) for _ in range(5)]
   for w in workers: w.start()
   for w in workers: w.join()
   print(len(calls))                                               # 1
   ```
   (A lock per key is better for scalability, but this shows the idea.)
4. `list.append` is a single operation implemented in C that completes while the GIL is held, so it cannot be interrupted halfway; `counter += 1` is a read, an add and a write as separate steps with possible switches between them.
5. See experiment 4: with 4 workers on a multi-core machine the speedup is typically 3 to 4 times.
6. Nothing in the code changes, but updates would be lost even more readily and even `counter += 1` loops start failing; the lock version stays correct. Locks are what make the program correct on every build.
7. Give it a `threading.Event` (or a queue sentinel), have the loop check `event.is_set()` (or `event.wait(timeout)`) each iteration, set the event from the main thread and `join()` the worker.

</details>

## 12. Check yourself

1. What is the GIL and why does CPython have it?
2. Why do threads speed up I/O-bound code but not CPU-bound pure Python?
3. Why do threads speed up `hashlib` on big buffers?
4. How do you get real CPU parallelism in standard Python?
5. Is `counter += 1` atomic? What should you do?
6. What does a free-threaded build change?

<details>
<summary>Answers</summary>

1. A lock that lets only one thread execute Python bytecode at a time, which keeps reference counting and interpreter internals safe without per-object locks.
2. While waiting for I/O a thread releases the GIL so others run; CPU-bound bytecode always needs the GIL, so threads only take turns.
3. The library releases the GIL while it hashes in C, so several threads compute simultaneously on different cores.
4. Use multiple processes (`multiprocessing`/`ProcessPoolExecutor`), or native libraries that release the GIL.
5. No: it is a read, an add and a write; the language does not promise atomicity. Protect shared updates with a lock (or use an atomic structure such as `queue.Queue`).
6. Threads can run Python code in parallel on several cores, so CPU-bound threaded code can scale, but latent races that the GIL hid are exposed and proper locking becomes mandatory.

</details>

[Back to processes and threads](README.md) · Previous: [processes in practice](01-processes-in-practice.md)
