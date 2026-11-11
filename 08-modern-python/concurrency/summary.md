# Threads, Processes and Futures: One-Page Summary

## Key facts

- **Pools:** `ThreadPoolExecutor` for waiting on I/O, `ProcessPoolExecutor` for CPU work; `submit` returns a `Future`, `map` keeps order, `as_completed` yields results as they finish, `.result()` re-raises a worker's exception.
- **The GIL:** in the standard build one thread runs Python bytecode at a time, so threads do not speed up CPU-bound pure Python; they do overlap I/O waits. Processes have their own interpreter and run in parallel, at the cost of pickling data and start-up time.
- **Races:** `counter += 1` is read, add, write; two threads can lose an update. Protect shared data with `threading.Lock` (`with lock:`) or avoid sharing by passing messages.
- **Producer-consumer:** `queue.Queue` is thread-safe; use `put`, `get`, `task_done`, `join`, and a sentinel value to stop workers.
- **Clean shutdown:** a `threading.Event` that workers check, then `join`.
- **Choosing:** many network connections, use `asyncio`; a few blocking calls, use threads; CPU-bound, use processes or a native library such as NumPy.

## Pitfalls

- Using threads to speed up CPU-bound Python.
- Shared mutable state without a lock; acquiring two locks in different orders (deadlock).
- Worker exceptions that nobody reads because `.result()` was never called.
- Starting processes without an `if __name__ == "__main__":` guard (the spawn start method re-imports your module).
- Creating thousands of threads instead of a bounded pool.

## Self-check

- **Which tool for I/O-bound work and which for CPU-bound work, and why?** Threads or asyncio for I/O-bound work (waiting overlaps, the GIL is released while waiting); processes for CPU-bound work (each has its own interpreter and GIL).
- **What is a future, and what happens to an exception raised in a worker?** A placeholder for a result that will arrive; the exception is stored and re-raised when you call `.result()` (so you must call it).
- **Why are process pools slower to start, and what must be true of their arguments?** Each worker is a new interpreter and arguments and results are serialised; so arguments must be picklable (no lambdas, open files, connections).
- **How does a lock fix `counter += 1`?** It makes the read-modify-write sequence atomic: only one thread can be inside the critical section at a time.
- **What does a bounded queue give you?** Backpressure: producers block when consumers fall behind, bounding memory and latency.
- **How do you stop a thread cleanly?** Set an `Event` that the thread checks between units of work, then `join()` it.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Threads, Processes and Futures in Practice](01-threads-processes-and-futures.md)
