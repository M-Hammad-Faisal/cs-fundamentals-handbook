# Iterators, Generators, Comprehensions and Functional Tools: Exercises

These problems go with the [Iterators, Generators, Comprehensions and Functional Tools lesson](README.md). Try each one before opening its solution.

## Problems

1. Rewrite as comprehensions: (a) squares of the odd numbers below 20; (b) a dict mapping each word to its length for words longer than 3 letters; (c) the flattened list of a list of lists of ints.
2. Write a generator `fibonacci()` (infinite) and use `itertools.islice` to take the first 12 values and `takewhile` to take those under 100.
3. Write `read_in_chunks(f, size)` and `grep(lines, word)` generators and combine them into a pipeline that counts matching lines in a file object without loading it all.
4. Implement `batched(iterable, n)` yourself (do not use `itertools.batched`) and test on `range(10)`.
5. Explain and fix: `adders = [lambda x: x + i for i in range(3)]; print([a(10) for a in adders])` prints `[12, 12, 12]`.
6. Write a `counter()` closure with `increment`, `decrement`, `value` functions sharing state, without a class.
7. Use `functools.partial` to create `log_error = log("ERROR", ...)` from a general `log(level, message)`; use `operator.itemgetter` to sort records by two keys.
8. Memoize a slow function with `lru_cache`, show `cache_info()` hits, and explain why it must be pure. Then show why `@cache` on a method can leak memory and how to avoid it.
9. Build a coroutine `moving_average(window)` using `send()`.
10. Write a generator-based context manager `temporary_value(d, key, value)` that sets a dict key inside a `with` block and restores the old state after.
11. What is wrong with `[print(x) for x in range(3)]` and `groupby` on unsorted data? Show the groupby gotcha.

<details>
<summary>Solutions</summary>

**1.**
```python
odd_squares = [n * n for n in range(20) if n % 2]
lengths = {w: len(w) for w in ["a", "tree", "house", "cat"] if len(w) > 3}
flat = [x for row in [[1, 2], [3], [4, 5]] for x in row]
print(odd_squares, lengths, flat)
# [1, 9, 25, 49, 81, 121, 169, 225, 289, 361] {'tree': 4, 'house': 5} [1, 2, 3, 4, 5]
```

**2.**
```python
from itertools import islice, takewhile

def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

print(list(islice(fibonacci(), 12)))
print(list(takewhile(lambda n: n < 100, fibonacci())))
```

**3.**
```python
import io

def read_in_chunks(f, size):
    while chunk := f.read(size):
        yield chunk

def lines_from_chunks(chunks):
    leftover = ""
    for chunk in chunks:
        leftover += chunk
        *complete, leftover = leftover.split("\n")
        yield from complete
    if leftover:
        yield leftover

def grep(lines, word):
    return (line for line in lines if word in line)

f = io.StringIO("alpha\nbeta error\ngamma\nerror again\ndelta")
print(sum(1 for _ in grep(lines_from_chunks(read_in_chunks(f, 4)), "error")))      # 2
```

**4.**
```python
def batched(iterable, n):
    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) == n:
            yield tuple(batch)
            batch = []
    if batch:
        yield tuple(batch)
print(list(batched(range(10), 4)))                                  # [(0, 1, 2, 3), (4, 5, 6, 7), (8, 9)]
```

**5.** Late binding: every lambda sees the final `i` (2), so `10 + 2 = 12`. Fix: `lambda x, i=i: x + i` (bind the current value) or `functools.partial(operator.add, i)`.
```python
adders = [lambda x, i=i: x + i for i in range(3)]
print([a(10) for a in adders])                                      # [10, 11, 12]
```

**6.**
```python
def make_counter(start=0):
    count = start
    def increment():
        nonlocal count
        count += 1
        return count
    def decrement():
        nonlocal count
        count -= 1
        return count
    def value():
        return count
    return increment, decrement, value

inc, dec, val = make_counter()
inc(); inc(); dec()
print(val())                                                        # 1
```

**7.**
```python
from functools import partial
from operator import itemgetter

def log(level, message):
    return f"[{level}] {message}"
log_error = partial(log, "ERROR")
print(log_error("disk full"))                                       # [ERROR] disk full

records = [{"team": "b", "age": 30}, {"team": "a", "age": 41}, {"team": "a", "age": 25}]
print(sorted(records, key=itemgetter("team", "age")))               # sorted by team, then age
```

**8.**
```python
from functools import lru_cache
import time

@lru_cache(maxsize=None)
def slow_double(n):
    time.sleep(0.01)
    return n * 2

slow_double(5); slow_double(5); slow_double(6)
print(slow_double.cache_info())                                     # CacheInfo(hits=1, misses=2, maxsize=None, currsize=2)
```
It must be pure: the cache returns the stored result without running the function again, so side effects would vanish and changing inputs/state would give stale answers. On a method, `@cache` keys on `self`, so the cache holds a reference to every instance forever (a leak). Fix: cache a module-level function of the needed values, use `functools.cached_property` for per-instance values, or keep a per-instance cache dictionary.

**9.**
```python
from collections import deque

def moving_average(window):
    values = deque(maxlen=window)
    average = None
    while True:
        value = yield average
        values.append(value)
        average = sum(values) / len(values)

ma = moving_average(3); next(ma)
print([ma.send(x) for x in (10, 20, 30, 40)])                       # [10.0, 15.0, 20.0, 30.0]
```

**10.**
```python
from contextlib import contextmanager
_missing = object()

@contextmanager
def temporary_value(d, key, value):
    old = d.get(key, _missing)
    d[key] = value
    try:
        yield d
    finally:
        if old is _missing:
            del d[key]
        else:
            d[key] = old

config = {"mode": "prod"}
with temporary_value(config, "mode", "test"):
    inside = config["mode"]
print(inside, config)                                               # test {'mode': 'prod'}
```

**11.** The list comprehension is used only for side effects and builds a useless list of `None`; use a `for` loop. `groupby` groups only *adjacent* equal keys:
```python
from itertools import groupby
print([(k, len(list(g))) for k, g in groupby("aabaa")])             # [('a', 2), ('b', 1), ('a', 2)]  (sort first to merge groups)
```

</details>

[Lesson](README.md) · [Summary](summary.md)
