# Processes and Threads: One-Page Summary

- **Process** = program in execution with a private address space. **Thread** = execution unit inside a process; shares heap/code/files, owns stack and registers.
- **States:** New, Ready, Running, Waiting, Terminated. The **PCB** holds the saved state; a **context switch** swaps it (pure overhead).
- **Unix:** `fork` (clone, copy-on-write), the `exec` family (replace program), `wait` (reap child). **Zombie** = exited, not reaped. **Orphan** = parent died.
- **IPC:** pipes, sockets, shared memory (fast, needs sync), message queues, signals.
- **Processes:** isolation, true CPU parallelism, heavier. **Threads:** cheap, shared state, risk of races.
- **Python:** the GIL means threads help I/O-bound work, not CPU-bound; use `multiprocessing` / `ProcessPoolExecutor` for CPU work.
- **Pitfalls:** forking with threads, leaking zombies, running commands through a shell string, sharing mutable state without locks.

[Lesson](README.md) · [Exercises](exercises.md)
