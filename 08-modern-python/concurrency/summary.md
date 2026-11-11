# Threads, Processes and Futures: One-Page Summary

## Questions worth remembering

- **Which tool for I/O-bound work and which for CPU-bound work, and why?** Threads or asyncio for I/O-bound work (waiting overlaps, the GIL is released while waiting); processes for CPU-bound work (each has its own interpreter and GIL).
- **What is a future, and what happens to an exception raised in a worker?** A placeholder for a result that will arrive; the exception is stored and re-raised when you call `.result()` (so you must call it).
- **Why are process pools slower to start, and what must be true of their arguments?** Each worker is a new interpreter and arguments and results are serialised; so arguments must be picklable (no lambdas, open files, connections).
- **How does a lock fix `counter += 1`?** It makes the read-modify-write sequence atomic: only one thread can be inside the critical section at a time.
- **What does a bounded queue give you?** Backpressure: producers block when consumers fall behind, bounding memory and latency.
- **How do you stop a thread cleanly?** Set an `Event` that the thread checks between units of work, then `join()` it.

Practice problems with solutions are in the **Practice** section of each lesson.

[Lesson](README.md) · [Threads, Processes and Futures in Practice](01-threads-processes-and-futures.md)
