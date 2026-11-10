# Processes and Threads

## Detailed lessons (start here if you are new)

1. [Processes in practice](01-processes-in-practice.md): fork, exec, zombies, pipes, signals, `subprocess`, threads vs processes vs asyncio
2. [Threads and the GIL lab](02-threads-and-the-gil-lab.md): when threads help and when they do not, races you can reproduce, free-threaded Python

The rest of this page is the quick reference.

## 1. The concept

A **program** is a file on disk. A **process** is a running instance of it: its own **address space** (code, heap, stack, globals), open files, and an entry in the OS process table. A **thread** is a unit of execution *inside* a process. Threads of one process share the address space and open files, but each has its own stack, registers and program counter.

| | Process | Thread |
|---|---------|--------|
| Memory | Private address space | Shared with sibling threads |
| Creation cost | Heavy (set up an address space) | Light |
| Crash | Isolated: one process dying leaves others alive | A bad thread can take down the whole process |
| Communication | IPC needed (pipes, sockets, shared memory, queues) | Direct (shared variables) but needs locking |
| Context switch | Slower (swap address space, flush TLB) | Faster |

## 2. How it works

### Process states

```text
        admit            dispatch
 New ----------> Ready ------------> Running ----> Terminated
                  ^  ^                 |
        I/O done  |  +-- preempted ----+
                  |                    | wait for I/O or lock
                  +------ Waiting <----+
```

The **PCB** (process control block) stores the state, program counter, registers, memory maps, open file table and scheduling info. A **context switch** saves one PCB's CPU state and loads another's. It is pure overhead: no useful work happens while switching.

### Creating processes (Unix)

`fork` clones the calling process. The child gets a copy of the address space (copy-on-write, so pages are only duplicated when written). The `exec` family replaces the child's program with a new one. `wait` lets the parent collect the exit status; a child that has exited but not been waited for is a **zombie**; a child whose parent died is an **orphan** (adopted by `init`).

```python
import os

pid = os.fork()                      # Unix only
if pid == 0:
    print("child: running")
    os._exit(7)                      # child exits with status 7
else:
    _, status = os.waitpid(pid, 0)   # parent waits (no zombie left behind)
    print("parent: child exited with", os.WEXITSTATUS(status))
```

The parent prints `parent: child exited with 7`.

### Threads: user vs kernel

Modern OSes schedule **kernel threads**. Languages may add lighter **user-level** tasks on top (goroutines, asyncio tasks). Mapping models: 1:1 (Java, Python threads), M:N (Go), N:1 (old green threads).

### Inter-process communication (IPC)

| Mechanism | Idea | Use |
|-----------|------|-----|
| Pipe | One-way byte stream between related processes | Shell pipelines |
| Socket | Bidirectional, works across machines | Network services |
| Shared memory | Same physical pages mapped in both | Fastest; you must synchronize |
| Message queue | Discrete messages | Task distribution |
| Signal | Tiny asynchronous notification | `SIGTERM`, `SIGINT` |

```python
import os

r, w = os.pipe()
if os.fork() == 0:                   # child writes
    os.close(r)
    os.write(w, b"hello from child")
    os._exit(0)
os.close(w)                          # parent reads
print(os.read(r, 100).decode())      # hello from child
os.wait()
```

### Python specifics

CPython's **GIL** lets only one thread run Python bytecode at a time, so threads do not speed up CPU-bound pure-Python code, but they do overlap **I/O waits** (the GIL is released while blocking). For CPU-bound work use **processes**.

```python
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def cpu(n):
    return sum(i * i for i in range(n))

def io(_):
    time.sleep(0.2)                  # stands in for a network call

if __name__ == "__main__":
    t = time.perf_counter()
    with ThreadPoolExecutor(8) as ex:
        list(ex.map(io, range(8)))
    print(f"8 sleeps in threads: {time.perf_counter() - t:.2f}s")   # about 0.2s, not 1.6s

    t = time.perf_counter()
    with ProcessPoolExecutor(4) as ex:
        list(ex.map(cpu, [2_000_000] * 4))
    print(f"4 CPU jobs in 4 processes: {time.perf_counter() - t:.2f}s")
```

Free-threaded CPython builds remove the GIL, but most code and libraries still assume the classic behavior. Check your build with `sys._is_gil_enabled()` on 3.13+.

## 3. Two real-world examples

### Example 1: A web server's concurrency model
Gunicorn runs several **worker processes** (isolation, uses every core, a crash kills one worker), and each worker may use **threads** or an event loop for concurrent requests. Nginx uses few processes with an event loop each. The trade-off is memory per connection versus isolation versus CPU use.

### Example 2: A browser
Chrome gives each site its own **process**, so a crashing or malicious tab cannot read another tab's memory or kill the browser. Inside a process, threads handle rendering, networking and helpers.

## 4. Tips, tricks and pitfalls

- Use processes for **isolation and CPU parallelism**, threads for **shared state and I/O overlap**.
- Always `wait` on children (or use `subprocess.run`), otherwise you leak zombies.
- Forking a multithreaded program is dangerous: only the calling thread survives in the child, and held locks stay locked. Python's `multiprocessing` uses `spawn` or `forkserver` by default on current versions for this reason.
- Shared mutable state between threads needs synchronization (see [concurrency](../concurrency-deadlocks/README.md)).
- Run other programs with `subprocess.run([...])` using the list form, and avoid building shell command strings from input.

## 5. Check yourself

1. What does a thread share with its siblings, and what is private?
2. Why is a thread context switch cheaper than a process switch?
3. What do `fork`, `exec` and `wait` do? What is a zombie?
4. Why does copy-on-write make `fork` cheap?
5. When do Python threads help, and when not?
6. Name four IPC mechanisms and one use for each.

<details>
<summary>Answers</summary>

1. Shared: code, heap, globals, open files. Private: stack, registers, program counter, thread-local storage.
2. Threads share an address space, so the OS need not swap page tables or flush the TLB.
3. `fork` clones the process, `exec` replaces its program, `wait` collects a child's exit status. A zombie is a terminated child whose status has not been collected.
4. Parent and child share the same physical pages read-only; a page is copied only when one of them writes to it.
5. They help for I/O-bound work (the GIL is released while waiting). They do not speed up CPU-bound pure Python; use processes.
6. Pipe (shell pipelines), socket (network services), shared memory (fast bulk data), signal (terminate a process), message queue (task distribution).

</details>

[Exercises](exercises.md) · [Summary](summary.md)
