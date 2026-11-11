# Performance, Profiling and Memory: One-Page Summary

## Key facts

- **Workflow:** goal, measure (realistic data), find the hot spot, fix, re-measure, keep a benchmark. Never guess.
- **Measure time:** `time.perf_counter` (durations), `timeit`/`python -m timeit` (comparisons; repeat, take the **min**), `cProfile` + `pstats` (`tottime` = own time, `cumtime` = with callees), `py-spy`, `line_profiler`, `scalene`, `pyinstrument`.
- **Measure memory:** `sys.getsizeof` (shallow), `tracemalloc` (by line, peak).
- **Biggest wins, in order:** algorithm and data structure (`set`/`dict` O(1) vs list O(n), `deque`, `bisect`, `heapq`) > avoid repeated work (cache, hoist, compile regex once, `join`) > built-ins in C (`sum`, `max`, `Counter`, comprehensions) > fewer I/O round trips (batch, `JOIN`, N+1) > faster layer (NumPy/pandas, processes, Cython/Numba/Rust, PyPy) > micro-tuning.
- **Memory:** generators and streaming, `__slots__`/slotted dataclasses, `array`/NumPy, bounded caches, weak refs, `memoryview`.
- **Concurrency:** threads for I/O-bound, processes for CPU-bound; it does not fix a bad algorithm.

## Pitfalls

- Optimising before measuring: profile first (`cProfile`, then line-level or memory tools).
- Micro-benchmarks that run once or include set-up: use `timeit` with repeats.
- Tweaking constants when the algorithm is the problem; optimising code that is not hot.
- Unbounded caches (`lru_cache(maxsize=None)`) that become memory leaks.
- Building strings with `+=` in loops instead of `"".join`.
- Also: premature optimization, benchmarking tiny inputs or one run, hidden O(n) (`x in list`, `pop(0)`, `insert(0)`), unbounded caches, unreadable micro-optimizations.

[Lesson](README.md) · [Exercises](exercises.md)
