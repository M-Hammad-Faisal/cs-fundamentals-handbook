# Concurrency in Python: One-Page Summary

## Key facts

- **Concurrency** = overlapping progress; **parallelism** = simultaneous execution on cores.
- **Choose:** I/O-bound with huge concurrency -> `asyncio`; I/O-bound with blocking libraries -> threads; CPU-bound pure Python -> processes. The **GIL** blocks parallel bytecode in threads (free-threaded 3.13+ builds are optional; check `sys._is_gil_enabled()`).
- **Threads:** `ThreadPoolExecutor.map/submit`, `as_completed`; always `with`; beware shared state (see OS concurrency chapter).
- **Processes:** `ProcessPoolExecutor`; `if __name__ == "__main__":`; arguments and results are pickled; tiny jobs are not worth the start-up cost.
- **asyncio:** `async def`/`await`; `asyncio.run`; `gather`, **`TaskGroup`** (structured concurrency, `except*`), `asyncio.timeout`, `Semaphore`, bounded `Queue`, `to_thread`, `async with`, `async for`.
- **Cancellation** raises `CancelledError` at an `await`: clean up and **re-raise**.
- **#1 bug:** blocking the event loop (`time.sleep`, `requests`, heavy CPU). Offload with `to_thread` or a process pool.
- **Back-pressure:** semaphores and bounded queues; set timeouts on every external call.

## Pitfalls

- A blocking call (`time.sleep`, `requests`, a sync driver) inside a coroutine freezes the whole loop: use `await asyncio.sleep`, an async library or `asyncio.to_thread`.
- Forgetting `await`: you get a coroutine object and nothing runs.
- Fire-and-forget tasks whose exceptions are lost: keep a reference, or use `asyncio.TaskGroup`.
- Unbounded concurrency against one service: bound it with a semaphore.
- Swallowing `CancelledError` with a broad `except`; running CPU-bound work in a coroutine.
- Also: un-awaited coroutines, dropped task references, unbounded concurrency, lambdas/closures with processes, `asyncio.run` inside a running loop.

[Lesson](README.md) · [Exercises](exercises.md)
