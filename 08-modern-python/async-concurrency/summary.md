# Concurrency in Python: One-Page Summary

- **Concurrency** = overlapping progress; **parallelism** = simultaneous execution on cores.
- **Choose:** I/O-bound with huge concurrency -> `asyncio`; I/O-bound with blocking libraries -> threads; CPU-bound pure Python -> processes. The **GIL** blocks parallel bytecode in threads (free-threaded 3.13+ builds are optional; check `sys._is_gil_enabled()`).
- **Threads:** `ThreadPoolExecutor.map/submit`, `as_completed`; always `with`; beware shared state (see OS concurrency chapter).
- **Processes:** `ProcessPoolExecutor`; `if __name__ == "__main__":`; arguments and results are pickled; tiny jobs are not worth the start-up cost.
- **asyncio:** `async def`/`await`; `asyncio.run`; `gather`, **`TaskGroup`** (structured concurrency, `except*`), `asyncio.timeout`, `Semaphore`, bounded `Queue`, `to_thread`, `async with`, `async for`.
- **Cancellation** raises `CancelledError` at an `await`: clean up and **re-raise**.
- **#1 bug:** blocking the event loop (`time.sleep`, `requests`, heavy CPU). Offload with `to_thread` or a process pool.
- **Back-pressure:** semaphores and bounded queues; set timeouts on every external call.
- **Pitfalls:** un-awaited coroutines, dropped task references, unbounded concurrency, lambdas/closures with processes, `asyncio.run` inside a running loop.

[Lesson](README.md) · [Exercises](exercises.md)
