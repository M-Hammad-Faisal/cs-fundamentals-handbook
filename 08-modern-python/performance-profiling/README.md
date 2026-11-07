# Performance, Profiling and Memory

## 1. The concept

Performance work follows one rule: **measure first, change second, measure again.** Programmers are notoriously bad at guessing where time goes. The fix is almost never a clever micro-trick; it is usually a better **algorithm or data structure**, removing **repeated work**, doing **less I/O**, or moving the hot loop into a faster layer (a library written in C, vectorized code, a compiled extension).

> "Premature optimization is the root of all evil" (Donald Knuth): first make it correct and clear; optimize only the parts a profiler shows are slow, and only if they matter to users.

The workflow:

```text
1. Define a goal ("the report must render in under 2 s")
2. Measure with realistic data (timeit, profiler, tracemalloc)
3. Find the hot spot (the 5% of code that costs 90% of the time)
4. Fix it (algorithm > data structure > caching > less I/O > faster layer > micro-tuning)
5. Re-measure; keep the change only if it helps; add a test or benchmark so it stays fixed
```

Complexity theory (Big-O) tells you how cost **grows**; profiling tells you what costs **now**. See [Big-O](../../01-complexity/big-o/README.md).

## 2. Measuring time

### `time.perf_counter` for quick checks, `timeit` for fair comparisons

```python
import time
from timeit import timeit

start = time.perf_counter()
total = sum(i * i for i in range(200_000))
elapsed = time.perf_counter() - start
print(elapsed < 1.0)                       # True (a monotonic, high-resolution clock for measuring durations)

# timeit runs a snippet many times and avoids one-off noise; compare alternatives with it
t_list = timeit("999_999 in data", setup="data = list(range(1_000_000))", number=20)
t_set = timeit("999_999 in data", setup="data = set(range(1_000_000))", number=20)
print("list lookup slower than set lookup:", t_list > t_set * 100)      # True  (O(n) vs O(1))
```

From a terminal: `python -m timeit -s "setup" "statement"`. In notebooks: `%timeit`. Always benchmark with **realistic input sizes**; tiny inputs hide algorithmic differences, and the first run includes caching effects.

### Statistics matter

```python
from timeit import repeat
runs = repeat("sorted(data)", setup="import random; data = [random.random() for _ in range(10_000)]", repeat=5, number=20)
print(min(runs) <= max(runs))              # True: use min() of several repeats as the best estimate of the true cost
```

Machines are noisy (other processes, CPU frequency, caches), so repeat and take the **minimum** (or median).

## 3. Profiling: where does the time go?

`cProfile` records how much time each function takes (including calls it makes) so you can see the hot spots.

```python
import cProfile, pstats, io

def slow_unique(items):
    result = []
    for x in items:
        if x not in result:                # O(n) membership test on a list: the hidden cost
            result.append(x)
    return result

def fast_unique(items):
    return list(dict.fromkeys(items))      # O(n): dict keeps insertion order and removes duplicates

data = [i % 2000 for i in range(20_000)]

profiler = cProfile.Profile()
profiler.enable()
slow_unique(data)
fast_unique(data)
profiler.disable()

stream = io.StringIO()
pstats.Stats(profiler, stream=stream).sort_stats("cumulative").print_stats(5)
report = stream.getvalue()
print("slow_unique" in report and "fast_unique" in report)               # True
print(slow_unique(data) == fast_unique(data))                            # True: same result, very different cost
```

Run a whole script under the profiler: `python -m cProfile -o out.prof script.py`, then inspect with `python -m pstats out.prof` or visualize with `snakeviz`. Read these columns: `ncalls` (how many calls), `tottime` (time inside the function itself), `cumtime` (including callees). Large `tottime` = the function's own code is slow; large `cumtime` with small `tottime` = something it calls is slow.

Other tools: **`line_profiler`** (time per line), **`py-spy`** (sampling profiler for running processes, no code changes), **`scalene`** (CPU + memory + GPU), **`pyinstrument`** (statistical, readable call trees), `perf`/flame graphs for system-level views.

## 4. Measuring memory

```python
import sys, tracemalloc

print(sys.getsizeof([]), sys.getsizeof(list(range(100))) > sys.getsizeof([]))   # 56 True (sizes vary by version)

tracemalloc.start()
squares = [i * i for i in range(100_000)]                    # a list of 100,000 ints
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()
print(current > 1_000_000)                                   # True: well over 1 MB

tracemalloc.start()
lazy = (i * i for i in range(100_000))                       # a generator expression
total = sum(lazy)
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()
print(peak < 100_000)                                        # True: the generator never holds the data
```

`sys.getsizeof` measures **one object, shallowly** (not what it references); `tracemalloc` shows allocations by line (`snapshot.statistics("lineno")`). Memory problems are usually: loading everything into lists, accumulating forever (unbounded caches, global lists), many small Python objects, and reference cycles holding large data.

## 5. The big wins, in order of impact

### 1. Choose the right algorithm and data structure

```python
from timeit import timeit

# Membership: list is O(n), set/dict is O(1)
setup = "needles = list(range(0, 2000, 7)); haystack_list = list(range(2000)); haystack_set = set(haystack_list)"
slow = timeit("[n in haystack_list for n in needles]", setup=setup, number=200)
fast = timeit("[n in haystack_set for n in needles]", setup=setup, number=200)
print("set membership faster:", fast < slow)                                       # True

# Queue: list.pop(0) is O(n), deque.popleft() is O(1)
slow = timeit("while q: q.pop(0)", setup="q = list(range(20_000))", number=1)
fast = timeit("while q: q.popleft()", setup="from collections import deque; q = deque(range(20_000))", number=1)
print("deque faster than list as a queue:", fast < slow)                           # True

# Sorted data: binary search O(log n) beats a linear scan O(n)
import bisect
data = list(range(1_000_000))
print(bisect.bisect_left(data, 987_654))                                           # 987654 (about 20 comparisons instead of ~1,000,000)
```

Quick reference: dict/set lookup O(1); list index O(1), search O(n), insert/delete at the front O(n); `deque` O(1) at both ends; `heapq` for "smallest k"; `sorted` O(n log n); string concatenation in a loop O(n^2) (use `"".join`). See [data structures](../../02-data-structures/arrays-strings/README.md).

### 2. Do less work: avoid repeating it

```python
from functools import lru_cache
import time

calls = 0

@lru_cache(maxsize=None)
def expensive(n):
    global calls
    calls += 1
    return sum(range(n))

for _ in range(1000):
    expensive(100_000)                       # computed once, then served from the cache
print(calls)                                 # 1

# Hoist invariant work out of loops
import re
words = ["apple", "bob", "cat"] * 10_000
pattern = re.compile(r"^[a-c]")              # compile ONCE, not inside the loop
count = sum(1 for w in words if pattern.match(w))
print(count)                                 # 30000

# Build strings with join, not repeated +=
parts = [str(i) for i in range(10_000)]
joined = ",".join(parts)
print(len(joined))                           # 48889
```

### 3. Use built-ins and the standard library (they run in C)

```python
import random
from timeit import timeit

nums = [random.random() for _ in range(100_000)]
loop = timeit("""
total = 0
for n in nums:
    total += n
""", globals={"nums": nums}, number=20)
builtin = timeit("sum(nums)", globals={"nums": nums}, number=20)
print("sum() faster than a Python loop:", builtin < loop)                          # True

loop_max = timeit("""
best = nums[0]
for n in nums:
    if n > best: best = n
""", globals={"nums": nums}, number=20)
print("max() faster:", timeit("max(nums)", globals={"nums": nums}, number=20) < loop_max)   # True
```

Comprehensions beat `append` loops; `collections.Counter`, `defaultdict`, `itertools`, `bisect`, `heapq`, `statistics`, `str` methods are all implemented in C.

### 4. Reduce I/O and round trips

Most real programs are slow because of **waiting** (database queries, HTTP calls, disk), not CPU. Batch operations (`executemany`, bulk inserts, one query with a `JOIN` instead of 1,000 queries: the N+1 problem), read files in large chunks, cache remote data, and overlap waits with [threads or asyncio](../async-concurrency/README.md).

```python
import sqlite3, time

db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, v TEXT)")
rows = [(i, f"v{i}") for i in range(20_000)]

start = time.perf_counter()
db.executemany("INSERT INTO t VALUES (?, ?)", rows)          # one call, one transaction
batch = time.perf_counter() - start
db.execute("DELETE FROM t")
db.commit()

start = time.perf_counter()
for r in rows[:2_000]:                                       # one statement per row, commit each time
    db.execute("INSERT INTO t VALUES (?, ?)", r)
    db.commit()
single = (time.perf_counter() - start) * 10                  # scale 2,000 rows up to 20,000 for comparison
print("batching is faster:", batch < single)                 # True
```

(In real client/server databases the gap is much larger because each round trip crosses the network.) See also [indexes and query plans](../../05-databases/indexes-query-plans/README.md).

### 5. Choose the right layer for hot loops

| Option | Use when |
|--------|----------|
| **NumPy / pandas / Polars** | Numeric or tabular data: vectorized operations replace Python loops (often 10-100x faster) |
| **`multiprocessing` / `ProcessPoolExecutor`** | CPU-bound work that can be split across cores |
| **Cython, Numba, mypyc, PyO3/Rust, C extensions** | A well-defined hot function you have profiled |
| **PyPy** | Long-running pure-Python code (JIT compiler); check library compatibility |
| **CPython 3.11+** | Free speed-up (adaptive interpreter); newer versions add an experimental JIT and free-threaded builds |

```python
# Vectorization idea without third-party libraries: process in bulk using built-ins
values = list(range(1, 100_001))
total_loop = 0
for v in values:
    total_loop += v * v
total_bulk = sum(map(int.__mul__, values, values))           # the loop runs in C
print(total_loop == total_bulk)                              # True
# With NumPy:  (np.arange(1, 100_001) ** 2).sum()  does the whole loop in one compiled call
```

### 6. Memory-saving techniques

```python
import sys
from array import array

class Plain:
    def __init__(self, a, b): self.a, self.b = a, b

class Slotted:
    __slots__ = ("a", "b")
    def __init__(self, a, b): self.a, self.b = a, b

print(sys.getsizeof(Plain(1, 2).__dict__) + sys.getsizeof(Plain(1, 2)) > sys.getsizeof(Slotted(1, 2)))   # True

numbers = list(range(100_000))
compact = array("i", numbers)                                # packed C integers
list_total = sys.getsizeof(numbers) + sum(sys.getsizeof(n) for n in numbers)   # the pointers PLUS each int object
print(sys.getsizeof(compact) < list_total / 3)               # True

# Process large inputs as streams, not lists
def lines_with(path_lines, word):
    for line in path_lines:                                  # a generator: one line in memory at a time
        if word in line:
            yield line
```

Other options: generators and iterators, `__slots__` or frozen dataclasses with `slots=True`, `array`/NumPy for large homogeneous data, `memoryview` for zero-copy slicing of bytes, interning repeated strings, deleting references to big objects when finished, weak references for caches.

## 6. Reading a profile: a worked example

```python
import cProfile, pstats, io

def build_report(n):
    lines = []
    for i in range(n):
        lines.append(f"row {i}: " + ",".join(str(j) for j in range(20)))
    return "\n".join(lines)

def validate(report):
    return all("row" in line for line in report.split("\n"))

def main():
    report = build_report(5_000)
    return validate(report)

pr = cProfile.Profile()
pr.runcall(main)
out = io.StringIO()
pstats.Stats(pr, stream=out).sort_stats("tottime").print_stats(3)
print(out.getvalue().count("build_report") >= 1)             # True
```

How to interpret: sort by `tottime` to find functions whose own code is slow, by `cumtime` to find expensive call trees. Fix the top item, re-profile, repeat. The top 1-3 entries usually account for most of the runtime; ignore the rest.

## 7. Two real-world examples

### Example 1: The N+1 query problem
A page lists 200 orders and shows each customer's name. The code loops `for order in orders: order.customer.name`, issuing 1 query for orders plus 200 for customers (the "N+1" problem): 201 round trips at 2 ms is 0.4 s. A profile shows 95% of the time waiting in the database driver. Fix: one query with a `JOIN` (ORM: `select_related`/`joinedload`), taking 6 ms total. No CPU tuning could have achieved that; the profiler pointed at I/O.

### Example 2: A slow deduplication in a data job
A nightly job removes duplicate emails from 300,000 rows using `if email not in seen_list`, taking 40 minutes (O(n^2)). `cProfile` shows `list.__contains__` dominating. Replacing the list with a `set` (or `dict.fromkeys`) drops the job to 1 second. The change is one line, found only because the team measured instead of guessing.

## 8. Tips, tricks and pitfalls

- **Profile before optimizing**, with realistic data sizes, and keep a benchmark so regressions are caught.
- Fix algorithms and data structures first; micro-optimizations rarely matter (use `timeit`, not intuition).
- Avoid premature optimization: clarity first, speed where measured.
- Never benchmark with `print` in the loop, tiny inputs, or a single run; repeat and take the minimum.
- `lru_cache` trades memory for speed; bound it and use it only on pure functions with hashable arguments.
- Do not build giant lists when you only iterate once; use generators.
- String concatenation in loops is O(n^2) in the worst case; use `join`.
- Beware hidden costs: `x in list`, `list.pop(0)`, `list.insert(0, x)`, `copy.deepcopy`, regex compile in loops, repeated attribute lookups in hot loops (a local alias helps slightly), converting between types repeatedly.
- Concurrency does not fix a slow algorithm; threads help only I/O-bound code, processes help CPU-bound code.
- Memory leaks in Python are usually references you keep (caches, globals, listeners), not the interpreter forgetting objects.
- Use the right tool for numeric work: NumPy/pandas/Polars, not nested Python loops.
- Always weigh benefit against complexity and maintenance: a 5% gain that makes code unreadable is a bad trade.

## 9. Check yourself

1. What is the workflow of performance optimization?
2. Why use `timeit` instead of timing one run?
3. What do `tottime` and `cumtime` mean in `cProfile` output?
4. Why is `x in some_list` in a loop a classic performance bug, and what replaces it?
5. What is the N+1 query problem?
6. Name four ways to reduce memory use.
7. When do threads speed up code, and when do processes?
8. Why is `"".join(parts)` preferred to `+=` in a loop?
9. When does `lru_cache` help and what are its requirements?

<details>
<summary>Answers</summary>

1. Define a goal, measure with realistic data, find the hot spot with a profiler, fix it (algorithm and data structure first), re-measure, and keep a benchmark or test.
2. A single run is dominated by noise (caches, other processes); `timeit` repeats and lets you take the minimum for a reliable comparison.
3. `tottime` is time spent inside the function itself (excluding callees); `cumtime` includes everything it calls.
4. Membership in a list is O(n), so a loop becomes O(n^2); a `set` or `dict` gives O(1) lookups.
5. Running one query for a list and then one more per item (N additional queries) instead of one joined/batched query; the round trips dominate.
6. Generators and streaming, `__slots__` (or slotted dataclasses), `array`/NumPy for homogeneous data, avoiding duplicate copies, bounded caches, `memoryview`.
7. Threads help I/O-bound code (waits overlap; the GIL is released); processes help CPU-bound pure-Python code (true parallelism on multiple cores).
8. `+=` may copy the growing string each time (quadratic cost); `join` computes the total size once and builds the result in one pass.
9. When the same pure function is called repeatedly with the same hashable arguments; it must be deterministic, side-effect free, and you should bound its size.

</details>

[Exercises](exercises.md) · [Summary](summary.md)
