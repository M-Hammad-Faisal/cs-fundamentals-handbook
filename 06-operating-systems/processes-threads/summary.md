# Processes and Threads: One-Page Summary

## Key facts

- **Process** = program in execution with a private address space. **Thread** = execution unit inside a process; shares heap/code/files, owns stack and registers.
- **States:** New, Ready, Running, Waiting, Terminated. The **PCB** holds the saved state; a **context switch** swaps it (pure overhead).
- **Unix:** `fork` (clone, copy-on-write), the `exec` family (replace program), `wait` (reap child). **Zombie** = exited, not reaped. **Orphan** = parent died.
- **IPC:** pipes, sockets, shared memory (fast, needs sync), message queues, signals.
- **Processes:** isolation, true CPU parallelism, heavier. **Threads:** cheap, shared state, risk of races.
- **Python:** the GIL means threads help I/O-bound work, not CPU-bound; use `multiprocessing` / `ProcessPoolExecutor` for CPU work.

## Pitfalls

- Treating threads as free: they share memory, so races and deadlocks appear.
- Zombie processes when a parent never waits for its children.
- Assuming threads speed up CPU-bound Python (the GIL) or that `fork` copies memory immediately (it is copy-on-write).
- Creating unbounded numbers of threads or processes instead of using a pool.
- Also: forking with threads, leaking zombies, running commands through a shell string, sharing mutable state without locks.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Processes in Practice](01-processes-in-practice.md) · [Threads and the GIL Lab](02-threads-and-the-gil-lab.md)
