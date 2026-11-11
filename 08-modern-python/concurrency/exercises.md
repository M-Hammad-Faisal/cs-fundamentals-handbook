# Threads, Processes and Futures: Exercises

Try each problem before opening its solution. These are the practice problems of this topic's lessons, collected in one place.

## Threads, Processes and Futures in Practice

1. Write `fetch_all(urls, fetch, workers=8, timeout=1.0)` that returns `{url: result_or_exception}` using futures, never raising for a single failure.
2. Re-run the counter demo with `threads=2` and `per_thread=5`. Does the unsafe version always lose updates with so little work? Why does that make races dangerous?
3. Describe the difference between ending consumers with a `STOP` sentinel and using `task_done()`/`join()`.
4. For a task of 1 ms of pure CPU, would you use a `ProcessPoolExecutor`? Estimate the break-even.
5. Give two ways to avoid a deadlock between two locks.
6. Explain why `pool.map` returns results in input order but `as_completed` does not.

<details>
<summary>Solutions</summary>

1. ```python no-run
   def fetch_all(urls, fetch, workers=8, timeout=1.0):
       out = {}
       with ThreadPoolExecutor(max_workers=workers) as pool:
           futures = {pool.submit(fetch, u): u for u in urls}
           for fut in as_completed(futures):
               url = futures[fut]
               try:
                   out[url] = fut.result(timeout=timeout)
               except Exception as exc:
                   out[url] = exc
       return out
   res = fetch_all(["a", "b", "c"], lambda u: 1 // 0 if u == "b" else u.upper())
   print({k: (v if not isinstance(v, Exception) else type(v).__name__) for k, v in sorted(res.items())})
   # {'a': 'A', 'b': 'ZeroDivisionError', 'c': 'C'}
   ```
2. With only 10 increments the threads usually finish one after another and the result is correct; the bug appears only under real contention. That is why races survive testing and show up in production under load: you must prevent them by design (locks, queues, no sharing), not by testing alone.
3. `task_done()`/`join()` waits until all queued work has been *processed* without sentinels; a sentinel additionally tells consumers to exit. Use `join()` when you only need to wait for completion, a sentinel when workers must terminate.
4. Probably not: starting a process and sending the arguments costs on the order of milliseconds (more for the first task), so a 1 ms task is dominated by overhead. Batch many such tasks per call (`chunksize`) or use vectorised native code instead; processes pay off for tasks of tens of milliseconds and up.
5. Always acquire locks in the same global order; or use a single lock; or use `lock.acquire(timeout=...)` and back off; or avoid holding one lock while waiting for another.
6. `map` is defined to yield results in the order of the inputs (it waits for the first, then the second, and so on); `as_completed` yields each future the moment it finishes, so fast tasks appear first.

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Threads, Processes and Futures in Practice](01-threads-processes-and-futures.md)
