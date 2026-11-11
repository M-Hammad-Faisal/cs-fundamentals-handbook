# Threads, Processes and Futures

Choosing and using concurrency in Python: which tool fits I/O-bound and CPU-bound work, how to use `concurrent.futures`, and how to avoid races.

## Detailed lessons

- [Threads, processes and futures in practice](01-threads-processes-and-futures.md): measured speed-ups, futures and errors, a race condition and its fix, producer-consumer queues, clean shutdown

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

## Quick reference

| Question | Answer |
|----------|--------|
| Which tool for I/O-bound work and which for CPU-bound work, and why? | Threads or asyncio for I/O-bound work (waiting overlaps, the GIL is released while waiting); processes for CPU-bound work (each has its own interpreter and GIL). |
| What is a future, and what happens to an exception raised in a worker? | A placeholder for a result that will arrive; the exception is stored and re-raised when you call `.result()` (so you must call it). |
| Why are process pools slower to start, and what must be true of their arguments? | Each worker is a new interpreter and arguments and results are serialised; so arguments must be picklable (no lambdas, open files, connections). |
| How does a lock fix `counter += 1`? | It makes the read-modify-write sequence atomic: only one thread can be inside the critical section at a time. |
| What does a bounded queue give you? | Backpressure: producers block when consumers fall behind, bounding memory and latency. |

Related: [asyncio and the concurrency overview](../async-concurrency/README.md), [processes and threads (OS)](../../06-operating-systems/processes-threads/README.md), [the GIL](../internals/01-python-data-model-and-internals.md).

Back to [modern Python](../README.md).
