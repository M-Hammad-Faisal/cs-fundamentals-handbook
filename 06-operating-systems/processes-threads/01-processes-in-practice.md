# Processes in Practice: fork, exec, pipes, signals and concurrency models

**Prerequisites:** [what is an OS](../00-what-is-an-operating-system.md), [processes and threads overview](README.md). **You will learn (by running real code):** the **process life cycle**, how **`fork`** and **`exec`** create programs (and what **zombies** and **orphans** are), how to run other programs safely with **`subprocess`**, how processes talk through **pipes** and **signals**, and when to choose **threads, processes or `asyncio`**. Unix-like systems (Linux, macOS); on Windows use WSL.

## 1. Anatomy of a process

A **process** is a running program plus everything the OS tracks for it:

| Part | What it is |
|------|------------|
| **PID** | the process id, a number unique at that moment |
| **Address space** | private virtual memory: code, global data, heap, stack(s) |
| **Open files** | a table of file descriptors (0 stdin, 1 stdout, 2 stderr, ...) |
| **Registers and program counter** | saved when the process is not running (the PCB) |
| **Environment and working directory** | `os.environ`, `os.getcwd()` |
| **Credentials** | user/group ids (what it is allowed to do) |

```python
import os, sys

print(os.getpid() > 0, os.getppid() > 0)               # True True   (me and my parent)
print(os.getcwd() == os.path.abspath("."), "PATH" in os.environ)      # True True
print(sys.executable.endswith("python") or "python" in sys.executable)  # True
print(sorted(os.listdir("/proc/self/fd")) if os.path.exists("/proc/self") else "no /proc here (macOS)")
```

On Linux, `/proc/<pid>/` exposes live process details (`status`, `maps`, `fd`, `cmdline`). On macOS use `ps` or `lsof -p <pid>`.

## 2. Life cycle and states

```text
 New -> Ready <-> Running -> Terminated
              ^        |
              |        v
              +-- Waiting (blocked on I/O, a lock or a timer)
```

`ps` shows the state letter: `R` running/runnable, `S` sleeping (waiting), `D` uninterruptible disk wait, `T` stopped, `Z` **zombie**.

## 3. `fork`: cloning a process

`os.fork()` creates a **child** that is a copy of the caller. It returns **twice**: `0` in the child, the child's PID in the parent. Memory is shared copy-on-write, so forking is cheap.

```python
import os

r, w = os.pipe()                                        # a one-way channel, see section 6
pid = os.fork()
if pid == 0:                                            # ---- child ----
    os.close(r)
    os.write(w, f"child pid differs: {os.getpid() != os.getppid()}".encode())
    os._exit(7)                                         # exit status 7; os._exit skips Python cleanup in the clone
os.close(w)                                             # ---- parent ----
message = os.read(r, 100).decode()
finished_pid, status = os.waitpid(pid, 0)               # wait for the child and collect its exit status
print(message)                                          # child pid differs: True
print(finished_pid == pid, os.WIFEXITED(status), os.WEXITSTATUS(status))      # True True 7
```

Key facts:

- The child gets a **copy** of variables: changes in the child are invisible to the parent (separate address spaces).
- Both continue **after the `fork()` line**; always branch on the return value.
- The parent should **`wait`** for children (see zombies below).

```python
counter = 10
pid = os.fork()
if pid == 0:
    counter += 5                                        # changes only the child's copy
    os._exit(counter)                                   # exit code carries the value out
_, status = os.waitpid(pid, 0)
print(counter, os.WEXITSTATUS(status))                  # 10 15
```

### Doubling: how many processes?

Each `fork()` doubles the number of running processes:

```python
def count_processes(forks):
    r, w = os.pipe()
    for _ in range(forks):
        os.fork()                                       # every existing process forks again
    os.write(w, b"x")                                   # each process writes one byte
    while True:                                         # every process reaps its OWN children before leaving
        try:
            os.wait()
        except ChildProcessError:
            break
    if os.getpid() != ROOT:
        os._exit(0)
    os.close(w)
    return len(os.read(r, 1000))
ROOT = os.getpid()
print(count_processes(3))                               # 8    (2^3 processes ran the write)
```

## 4. `exec`: replacing the program

`fork` clones the *same* program. To run a **different** program, the child calls an **`exec`** function, which **replaces the process image** (same PID, new code and memory). The classic shell recipe is *fork, then exec in the child, then wait in the parent*.

```python
pid = os.fork()
if pid == 0:
    os.execvp("echo", ["echo", "hello from a new program"])      # never returns on success
    os._exit(127)                                       # only reached if exec failed
os.waitpid(pid, 0)                                      # prints: hello from a new program
```

Real programs use the higher-level `subprocess` module, which does fork/exec (or `posix_spawn`) safely and handles pipes, exit codes and timeouts:

```python
import subprocess, sys

result = subprocess.run(["echo", "hi"], capture_output=True, text=True)
print(repr(result.stdout), result.returncode)           # 'hi\n' 0

result = subprocess.run([sys.executable, "-c", "import sys; sys.exit(3)"])
print(result.returncode)                                # 3

result = subprocess.run(["ls", "/definitely/not/here"], capture_output=True, text=True)
print(result.returncode != 0, bool(result.stderr))      # True True

try:
    subprocess.run([sys.executable, "-c", "import time; time.sleep(5)"], timeout=0.2)
except subprocess.TimeoutExpired:
    print("killed after the timeout")                   # killed after the timeout

# check=True raises on failure instead of silently continuing
try:
    subprocess.run([sys.executable, "-c", "raise SystemExit(1)"], check=True)
except subprocess.CalledProcessError as e:
    print("failed with code", e.returncode)             # failed with code 1
```

**Safety rule:** pass the command as a **list** (`["ls", folder]`), never as one string built from user input. Strings interpreted by a shell invite command injection (`; rm -rf ~`).

Pipelines without a shell string (equivalent of `echo "b\na" | sort`):

```python
echo = subprocess.Popen(["printf", "b\\na\\n"], stdout=subprocess.PIPE)
sort = subprocess.Popen(["sort"], stdin=echo.stdout, stdout=subprocess.PIPE, text=True)
echo.stdout.close()
print(sort.communicate()[0].split())                    # ['a', 'b']
```

## 5. Zombies and orphans

- **Zombie:** a child that has **exited** but whose parent has not yet called `wait`. The kernel keeps a tiny entry (PID, exit status) so the parent *can* learn the result. Many zombies exhaust the PID table.
- **Orphan:** a child whose **parent exited first**. It is adopted by PID 1 (init/systemd/launchd), which reaps it.

```python
import time

pid = os.fork()
if pid == 0:
    os._exit(0)                                         # child exits immediately
time.sleep(0.2)                                         # the parent has not waited yet: the child is a zombie right now
state = subprocess.run(["ps", "-o", "stat=", "-p", str(pid)], capture_output=True, text=True).stdout.strip()
print(state.startswith("Z"))                            # True   ("Z" = zombie; shows as <defunct> in ps)
os.waitpid(pid, 0)                                      # reaping removes the zombie
gone = subprocess.run(["ps", "-p", str(pid)], capture_output=True).returncode != 0
print(gone)                                             # True
```

Avoid zombies: always `wait()`/`waitpid()`, use `subprocess.run` (it waits for you), or set `signal.signal(signal.SIGCHLD, signal.SIG_IGN)` to tell the kernel to reap automatically. Containers need a proper PID 1 (use `docker run --init`) so orphans get reaped.

## 6. Pipes: talking between processes

A **pipe** is a kernel buffer with a read end and a write end. Bytes written to one end can be read from the other, in order. (Shell `|` connects the stdout of one program to the stdin of the next with exactly this.)

```python
r, w = os.pipe()
if os.fork() == 0:                                      # child: writer
    os.close(r)
    for word in ("alpha", "beta", "gamma"):
        os.write(w, (word + "\n").encode())
    os._exit(0)                                         # exiting closes the write end
os.close(w)                                             # parent must close ITS copy of the write end too
with os.fdopen(r) as reader:
    print([line.strip() for line in reader])            # ['alpha', 'beta', 'gamma']   (the loop ends at EOF)
os.wait()
```

Why close unused ends? A reader sees **EOF** only when **every** write end is closed. Forgetting to close the parent's copy makes the reader hang forever, a classic bug.

Higher-level helpers in `multiprocessing` (`Pipe`, `Queue`) and sockets (`socket.socketpair`) cover most needs. Other IPC mechanisms: **shared memory** (fastest, needs locking), **message queues**, **sockets** (also across machines), **files**, **signals**.

```python
# save as mp_queue.py and run: python3 mp_queue.py
from multiprocessing import Process, Queue

def square_all(numbers, out):
    out.put([n * n for n in numbers])

if __name__ == "__main__":                               # required when the start method is "spawn" (macOS, Windows, newer Linux)
    q = Queue()
    p = Process(target=square_all, args=([1, 2, 3, 4], q))
    p.start()
    print(q.get())                                      # [1, 4, 9, 16]
    p.join()
    print(p.exitcode)                                   # 0
```

## 7. Signals: tiny asynchronous messages

A **signal** interrupts a process to say something happened. Common ones:

| Signal | Number (Linux) | Default | Typical cause |
|--------|----------------|---------|---------------|
| `SIGINT` | 2 | terminate | Ctrl+C |
| `SIGTERM` | 15 | terminate | polite "please stop" (`kill pid`) |
| `SIGKILL` | 9 | terminate, **cannot be caught** | forced kill (`kill -9`) |
| `SIGSTOP` / `SIGCONT` | | pause / resume | Ctrl+Z, `fg` |
| `SIGCHLD` | | ignore | a child exited |
| `SIGSEGV` | 11 | terminate + core dump | invalid memory access |
| `SIGALRM` | 14 | terminate | `alarm()` timer |

A program can install a **handler** for most signals (except `SIGKILL` and `SIGSTOP`):

```python
import signal

received = []
def handler(signum, frame):
    received.append(signal.Signals(signum).name)

signal.signal(signal.SIGUSR1, handler)
os.kill(os.getpid(), signal.SIGUSR1)                    # send a signal to myself
time.sleep(0.05)
print(received)                                         # ['SIGUSR1']
```

**Graceful shutdown** is the standard use: on `SIGTERM`, finish current work, close files and exit.

```python
running = True
def request_stop(signum, frame):
    global running
    running = False                                     # just set a flag; do the cleanup in the main loop

signal.signal(signal.SIGTERM, request_stop)

pid = os.fork()
if pid == 0:                                            # child: a worker loop that stops cleanly
    signal.signal(signal.SIGTERM, request_stop)
    while running:
        time.sleep(0.01)
    os._exit(42)                                        # cleaned up, exits with a recognizable code
time.sleep(0.1)
os.kill(pid, signal.SIGTERM)                            # parent politely asks it to stop
_, status = os.waitpid(pid, 0)
print(os.WIFEXITED(status), os.WEXITSTATUS(status))     # True 42
```

Compare with `SIGKILL` (no cleanup possible):

```python
pid = os.fork()
if pid == 0:
    time.sleep(10); os._exit(0)
os.kill(pid, signal.SIGKILL)
_, status = os.waitpid(pid, 0)
print(os.WIFSIGNALED(status), os.WTERMSIG(status))      # True 9
```

Keep signal handlers **tiny** (set a flag): they run asynchronously and can interrupt the program at awkward moments. Docker/Kubernetes send `SIGTERM`, wait a grace period (30 s), then `SIGKILL`: handle `SIGTERM`.

## 8. Threads, processes and `asyncio`: choosing

| | **Threads** | **Processes** | **`asyncio`** |
|---|-------------|---------------|---------------|
| Memory | shared (needs locks) | separate (needs IPC) | one thread, shared |
| Start cost | small | larger | tiny |
| True CPU parallelism in Python | no (GIL; yes on free-threaded builds) | **yes** | no |
| Good for | I/O-bound, moderate concurrency | CPU-bound work, isolation | thousands of I/O-bound connections |
| Crash isolation | none | **strong** | none |

Measure it yourself (save as `compare.py`; the `__main__` guard is required for process pools on `spawn` platforms):

```python
# compare.py
import asyncio, time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def cpu_task(n):
    return sum(i * i for i in range(n))

def io_task(_):
    time.sleep(0.1)                                     # stands in for a network call

async def async_io():
    await asyncio.gather(*(asyncio.sleep(0.1) for _ in range(10)))

def timed(fn):
    start = time.perf_counter(); fn(); return time.perf_counter() - start

if __name__ == "__main__":
    N = 3_000_000
    serial_cpu = timed(lambda: [cpu_task(N) for _ in range(4)])
    with ThreadPoolExecutor(4) as ex:
        thread_cpu = timed(lambda: list(ex.map(cpu_task, [N] * 4)))
    with ProcessPoolExecutor(4) as ex:
        list(ex.map(cpu_task, [1000] * 4))               # warm up the worker processes
        process_cpu = timed(lambda: list(ex.map(cpu_task, [N] * 4)))
    print("CPU-bound: serial %.2fs, threads %.2fs, processes %.2fs" % (serial_cpu, thread_cpu, process_cpu))

    serial_io = timed(lambda: [io_task(i) for i in range(10)])
    with ThreadPoolExecutor(10) as ex:
        thread_io = timed(lambda: list(ex.map(io_task, range(10))))
    async_time = timed(lambda: asyncio.run(async_io()))
    print("I/O-bound: serial %.1fs, threads %.1fs, asyncio %.1fs" % (serial_io, thread_io, async_time))
```

One run on a laptop (GIL build): `CPU-bound: serial 0.51s, threads 0.51s, processes 0.14s` and `I/O-bound: serial 1.0s, threads 0.1s, asyncio 0.1s`. Threads give no speedup for CPU-bound work, processes do, and for I/O waits threads and asyncio both overlap the sleeps. (Your CPU numbers will differ.)

Rules of thumb: **I/O-bound** -> threads or `asyncio`; **CPU-bound** -> processes (or native libraries like NumPy); **need isolation or to run untrusted code** -> processes; **need to scale beyond one machine** -> multiple processes and a queue (Celery, RQ) or a framework.

### Why `multiprocessing` uses "spawn" on macOS/Windows

`fork` copies **only the calling thread**: if another thread held a lock at that moment (the memory allocator's, logging's), the child inherits the locked lock and can hang forever. For that reason Python defaults to `spawn` (start a fresh interpreter) on macOS and Windows and, from 3.14, on Linux too (`forkserver`). Code using `spawn` must guard its entry point with `if __name__ == "__main__":`.

## 9. Two real-world examples

**Example 1: A web server.** Gunicorn forks several **worker processes** after loading the app (copy-on-write shares most memory), each handling requests. A worker that crashes or leaks memory is killed and replaced by the master process, which isolates failures and uses every core.

**Example 2: A shell pipeline.** `cat access.log | grep 500 | sort | uniq -c` starts four processes joined by pipes. Data streams through as it is produced, so the pipeline works on files far bigger than RAM and uses several cores at once.

## 10. Common mistakes

- Forgetting to `wait()` for children (zombies) or to close unused pipe ends (hangs).
- Using `os.fork()` after starting threads (deadlocks in the child).
- Building shell command strings from user input instead of passing a list.
- Doing real work in a signal handler.
- Forgetting `if __name__ == "__main__":` when using `multiprocessing` with `spawn`.
- Expecting threads to speed up CPU-bound pure Python code.
- Using `os._exit` vs `sys.exit` incorrectly: in a forked child use `os._exit` (skips parent's cleanup like flushing duplicated buffers).

## 11. Practice

1. After `os.fork()` in a script, how many times does the line `print("hi")` run if it comes right after the fork and every process reaches it?
2. Write code that forks a child which computes `sum(range(100))` and sends the answer to the parent through a pipe.
3. What is the difference between `fork` and `exec`? Why do shells use both?
4. How can a zombie be created and removed?
5. Run `["sleep", "5"]` with a 1-second timeout using `subprocess` and report whether it timed out.
6. Which signal can a process never catch or ignore?
7. For each task choose threads, processes or asyncio: (a) resizing 200 images, (b) calling 500 URLs, (c) a chat server with 10 000 idle connections, (d) running student-submitted code.

<details>
<summary>Solutions</summary>

1. Twice: one for the parent and one for the child (two processes).
2. ```python
   r, w = os.pipe()
   pid = os.fork()
   if pid == 0:
       os.close(r); os.write(w, str(sum(range(100))).encode()); os._exit(0)
   os.close(w)
   print(int(os.read(r, 100)))                           # 4950
   os.waitpid(pid, 0)
   ```
3. `fork` clones the current process; `exec` replaces the process's program with another. A shell forks a child (so the shell itself survives), the child execs the command, and the shell waits.
4. A child exits and the parent has not yet called `wait` (zombie); calling `os.waitpid(pid, 0)` reaps it. See the `ps` demonstration above.
5. ```python
   try:
       subprocess.run(["sleep", "5"], timeout=1)
   except subprocess.TimeoutExpired:
       print("timed out")                                # timed out
   ```
6. `SIGKILL` (and `SIGSTOP`).
7. (a) processes (CPU-bound), (b) threads or asyncio (I/O-bound), (c) asyncio (huge number of mostly idle connections), (d) processes (isolation, can be killed and resource-limited).

</details>

## 12. Check yourself

1. What does `fork` return in the parent and in the child?
2. What does `exec` do to the calling process?
3. What is a zombie and how do you prevent them?
4. Why must unused pipe ends be closed?
5. Why handle `SIGTERM` instead of relying on `SIGKILL`?
6. When do Python threads help and when not?

<details>
<summary>Answers</summary>

1. The child's PID in the parent, and 0 in the child.
2. It replaces its program image (code, data, stack) with a new program while keeping the same PID.
3. An exited child not yet reaped by its parent; prevent by waiting (`wait`/`waitpid`, `subprocess.run`) or ignoring `SIGCHLD`.
4. A reader sees end-of-file only when all write ends are closed; a stray open copy keeps the reader waiting forever.
5. `SIGTERM` can be caught to finish work and clean up; `SIGKILL` cannot be caught, so no cleanup happens.
6. They help for I/O-bound work (the GIL is released while waiting); not for CPU-bound pure Python code.

</details>

[Back to processes and threads](README.md)
