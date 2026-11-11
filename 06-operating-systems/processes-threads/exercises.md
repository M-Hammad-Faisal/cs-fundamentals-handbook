# Processes and Threads: Exercises

These problems go with the [Processes and Threads lesson](README.md). Try each one before opening its solution.

## Problems

1. A parent calls `fork()` and both processes then run `print("hi")`. How many lines print? What if `fork()` is called twice in a row?
2. Write a program that forks a child; the child computes `sum(range(1000))` and sends it to the parent through a pipe; the parent prints it.
3. Explain what a zombie is and write code that creates one briefly, then reaps it.
4. Threads vs processes: choose one for (a) resizing 500 images, (b) downloading 500 URLs, (c) a game server with shared world state, (d) running untrusted plugins. Justify each.
5. Using `ThreadPoolExecutor`, fetch-simulate 10 tasks that each `sleep(0.1)` and show total time is about 0.1 s. Then do CPU-bound work and show threads do not help.
6. Why is calling `fork()` from a multithreaded program risky?
7. Name the states a process moves through when it calls `read()` on a slow disk.

<details>
<summary>Solutions</summary>

**1.** After one `fork()` two lines print (both processes continue after the call). After two consecutive forks there are 4 processes, so 4 lines (2 forks double the count each time: 2^n).

**2.**
```python
import os
r, w = os.pipe()
pid = os.fork()
if pid == 0:
    os.close(r)
    os.write(w, str(sum(range(1000))).encode())
    os._exit(0)
os.close(w)
print(int(os.read(r, 100)))     # 499500
os.waitpid(pid, 0)
```

**3.** A zombie is a child that has exited but whose parent has not called `wait`, so its process-table entry remains.
```python
import os, time
pid = os.fork()
if pid == 0:
    os._exit(0)                  # child exits immediately
time.sleep(0.5)                  # child is a zombie now (visible as "defunct" in ps)
os.waitpid(pid, 0)               # reaped
```

**4.** (a) Processes: CPU-bound, parallel on all cores. (b) Threads (or asyncio): I/O-bound, cheap. (c) Threads: shared mutable state, with careful locking. (d) Processes: isolation and the ability to kill or sandbox them.

**5.**
```python
import time
from concurrent.futures import ThreadPoolExecutor
def io(_): time.sleep(0.1)
def cpu(_): return sum(i * i for i in range(3_000_000))
for fn, n in ((io, 10), (cpu, 4)):
    t = time.perf_counter()
    with ThreadPoolExecutor(n) as ex: list(ex.map(fn, range(n)))
    print(fn.__name__, round(time.perf_counter() - t, 2))
# io is about 0.1 s; cpu takes roughly n times one job (no speedup) on a GIL build
```

**6.** Only the forking thread exists in the child. If another thread held a lock (for example the allocator or logging lock) at the moment of the fork, that lock stays locked forever in the child, causing deadlock.

**7.** Running, then Waiting (blocked on I/O) while the disk works, then Ready when the I/O completes, then Running again when the scheduler dispatches it.

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Processes in Practice](01-processes-in-practice.md) · [Threads and the GIL Lab](02-threads-and-the-gil-lab.md)
