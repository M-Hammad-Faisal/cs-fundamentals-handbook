# Performance and Profiling: Exercises

1. Use `timeit` to compare building a list of squares with a `for`/`append` loop, a list comprehension and `map`. Which wins, and by roughly how much?
2. Profile this function with `cProfile`, find the bottleneck and fix it. Show both versions give the same answer:
   ```python
   def common(a, b):
       return [x for x in a if x in b]          # a and b are lists of 20,000 ints
   ```
3. Show that repeated string concatenation in a loop is slower than `join` for 200,000 pieces (use `timeit` with `number=1`).
4. Use `tracemalloc` to compare the peak memory of summing squares with a list versus a generator for 1,000,000 numbers.
5. Memoize a recursive function (`fib`) with `lru_cache` and measure `fib(32)` with and without it. Why is the speed-up so large?
6. Compare `list.pop(0)` and `deque.popleft()` as queues of 50,000 items.
7. Demonstrate the N+1 problem in SQLite: load 500 orders and their customer names with 501 queries, then with one `JOIN`. Time both.
8. Write a micro-benchmark helper `bench(fn, *args, repeat=5, number=10)` returning the best per-call time, and use it to compare two implementations of "count word frequencies" (`dict` loop vs `Counter`).
9. Explain why parallelizing a CPU-bound loop with threads in CPython does not help but processes do. When would threads help?
10. A report generator takes 12 s. List the exact steps (tools and order) you would take to make it faster, including how you would know when to stop.

<details>
<summary>Solutions</summary>

**1.**
```python
from timeit import timeit
loop = timeit("""
r = []
for i in range(1000):
    r.append(i * i)
""", number=2000)
comp = timeit("[i * i for i in range(1000)]", number=2000)
mapped = timeit("list(map(lambda i: i * i, range(1000)))", number=2000)
print(comp < loop, comp < mapped)                      # True True  (typically 20-40% faster than the loop)
```

**2.** The hidden cost is `x in b` on a list (O(n) each, so O(n^2) overall).
```python
import cProfile, pstats, io, random

def common_slow(a, b):
    return [x for x in a if x in b]

def common_fast(a, b):
    sb = set(b)                                         # O(n) once, then O(1) lookups
    return [x for x in a if x in sb]

random.seed(0)
a = [random.randrange(40_000) for _ in range(20_000)]
b = [random.randrange(40_000) for _ in range(20_000)]
pr = cProfile.Profile(); pr.runcall(common_slow, a, b)
out = io.StringIO(); pstats.Stats(pr, stream=out).sort_stats("tottime").print_stats(2)
print(common_slow(a, b) == common_fast(a, b))           # True
from timeit import timeit
print(timeit(lambda: common_fast(a, b), number=1) < timeit(lambda: common_slow(a, b), number=1) / 20)   # True
```

**3.**
```python
from timeit import timeit
concat = timeit("""
s = ""
for i in range(200_000):
    s += "x"
""", number=1)
joined = timeit('"".join("x" for _ in range(200_000))', number=1)
print(joined < concat * 2)                              # True or close: CPython sometimes optimizes += on str, but join is always safe
```
(CPython has an in-place optimization for `s += t` that often hides the quadratic cost; `join` is the portable, always-linear choice.)

**4.**
```python
import tracemalloc

def peak(fn):
    tracemalloc.start()
    fn()
    _, p = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return p

list_peak = peak(lambda: sum([i * i for i in range(1_000_000)]))
gen_peak = peak(lambda: sum(i * i for i in range(1_000_000)))
print(gen_peak < list_peak / 100)                       # True
```

**5.**
```python
from functools import lru_cache
from timeit import timeit

def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)

@lru_cache(maxsize=None)
def fib_cached(n):
    return n if n < 2 else fib_cached(n - 1) + fib_cached(n - 2)

print(fib(24) == fib_cached(24), timeit(lambda: fib(24), number=1) > timeit(lambda: fib_cached(24), number=1) * 100)   # True True
```
The naive version recomputes the same subproblems exponentially many times (about 1.6^n calls); the cache turns it into n distinct computations (O(n)).

**6.**
```python
from timeit import timeit
slow = timeit("while q: q.pop(0)", setup="q = list(range(50_000))", number=1)
fast = timeit("while q: q.popleft()", setup="from collections import deque; q = deque(range(50_000))", number=1)
print(fast < slow)                                      # True
```

**7.**
```python
import sqlite3, time
db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT);
CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER, total REAL);
""")
db.executemany("INSERT INTO customers VALUES (?, ?)", [(i, f"c{i}") for i in range(500)])
db.executemany("INSERT INTO orders VALUES (?, ?, ?)", [(i, i, i * 1.5) for i in range(500)])

start = time.perf_counter()
names = []
for oid, cid in db.execute("SELECT id, customer_id FROM orders").fetchall():       # 1 query ...
    names.append(db.execute("SELECT name FROM customers WHERE id = ?", (cid,)).fetchone()[0])   # ... + 500 more
n_plus_one = time.perf_counter() - start

start = time.perf_counter()
joined = [r[0] for r in db.execute("SELECT c.name FROM orders o JOIN customers c ON c.id = o.customer_id")]
single = time.perf_counter() - start
print(names == joined, single < n_plus_one)             # True True  (against a networked database the gap is far bigger)
```

**8.**
```python
from timeit import repeat
from collections import Counter

def bench(fn, *args, repeat_=5, number=10):
    return min(repeat(lambda: fn(*args), repeat=repeat_, number=number)) / number

def count_loop(words):
    d = {}
    for w in words:
        d[w] = d.get(w, 0) + 1
    return d

def count_counter(words):
    return Counter(words)

words = ["a", "b", "a", "c", "b", "a"] * 20_000
print(count_loop(words) == dict(count_counter(words)), bench(count_counter, words) < bench(count_loop, words))
```

**9.** The GIL lets only one thread run Python bytecode at a time, so CPU-bound threads take turns instead of running in parallel (and add switching overhead); processes have separate interpreters and GILs, so they run on separate cores. Threads help for I/O-bound work (network, disk) because the GIL is released while waiting, and for C extensions that release the GIL (hashing, compression, NumPy).

**10.** (1) Set a target (for example under 2 s) and create a realistic, repeatable test input; (2) measure the baseline with `time.perf_counter`; (3) profile with `cProfile` (or `py-spy` in production), sorting by cumulative and own time; (4) read the top entries, check whether the cost is I/O (queries, requests) or CPU; (5) fix the biggest item: better algorithm or data structure, batching/joins, caching, then a faster layer if necessary; (6) re-measure after each change and keep only improvements; (7) add a benchmark/test; (8) stop when the target is met, or when the remaining time is spread thinly with no single hot spot and further effort costs more than it saves.

</details>

[Lesson](README.md) · [Summary](summary.md)
