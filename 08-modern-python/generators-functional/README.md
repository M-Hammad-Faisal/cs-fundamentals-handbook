# Iterators, Generators, Comprehensions and Functional Tools

## 1. The concept

Python lets you process data **lazily** (one item at a time, as needed) and treat **functions as values** (pass them around, return them, store them). Combined, these give concise, memory-efficient code: pipelines that handle a 50 GB log file with a few kilobytes of memory, and small reusable functions glued together.

Key ideas:

| Idea | Tool |
|------|------|
| Produce values on demand | **generators** (`yield`), generator expressions |
| Describe a new collection in one line | **comprehensions** (list, set, dict) |
| Build streams from streams | **itertools**, generator pipelines |
| Functions as data | closures, `lambda`, `functools.partial`, `functools.reduce`, `operator` |
| Cache results | `functools.cache`, `lru_cache` |

(The iterator protocol itself, `__iter__`/`__next__`, is covered in [polymorphism and the data model](../../04-oop/polymorphism-dunder/README.md) and the [Iterator pattern](../../04-oop/design-patterns/behavioral/iterator.md).)

## 2. Comprehensions

```python
nums = range(10)
squares = [n * n for n in nums]                                  # list comprehension
evens = [n for n in nums if n % 2 == 0]                          # with a filter
labels = ["even" if n % 2 == 0 else "odd" for n in range(4)]     # with a conditional expression
pairs = [(x, y) for x in range(3) for y in range(3) if x < y]    # nested loops
lookup = {name: len(name) for name in ["ana", "bilal"]}          # dict comprehension
unique_lengths = {len(w) for w in ["a", "bb", "cc"]}             # set comprehension
print(squares, evens, labels)
# [0, 1, 4, 9, 16, 25, 36, 49, 64, 81] [0, 2, 4, 6, 8] ['even', 'odd', 'even', 'odd']
print(pairs, lookup, unique_lengths)
# [(0, 1), (0, 2), (1, 2)] {'ana': 3, 'bilal': 5} {1, 2}

matrix = [[1, 2, 3], [4, 5, 6]]
flat = [x for row in matrix for x in row]                        # read left to right like nested for loops
transposed = [[row[i] for row in matrix] for i in range(3)]
print(flat, transposed)                                          # [1, 2, 3, 4, 5, 6] [[1, 4], [2, 5], [3, 6]]
```

Rules of thumb: comprehensions are clearer than `map`/`filter` with `lambda` and faster than `append` in a loop. Stop at **two** levels of nesting or one condition; beyond that use a normal loop. The loop variable does not leak (comprehensions have their own scope).

The **walrus operator** `:=` avoids computing something twice in a filter:

```python
data = ["3", "x", "7", "", "12"]
numbers = [n for s in data if (n := s.strip()).isdigit()]
print(numbers)                                                   # ['3', '7', '12']
```

## 3. Generators

A **generator function** contains `yield`. Calling it returns a **generator object** (an iterator) without running the body; each `next()` runs until the next `yield`, then **pauses with its local state intact**.

```python
def countdown(n):
    print("starting")
    while n > 0:
        yield n                     # pause here and hand a value to the caller
        n -= 1
    print("done")

gen = countdown(3)                  # nothing printed yet: the body has not run
print(next(gen))                    # starting  then  3
print(next(gen))                    # 2
print(list(gen))                    # [1]   (and prints "done")
```

### Why generators matter

```python
import sys

squares_list = [i * i for i in range(1_000_000)]               # 1,000,000 numbers stored
squares_gen = (i * i for i in range(1_000_000))                # a generator expression: stores nothing
print(sys.getsizeof(squares_list) > 100 * sys.getsizeof(squares_gen))      # True
print(sum(squares_gen))                                        # 333332833333500000
```

| Benefit | Detail |
|---------|--------|
| **Constant memory** | Items are produced and discarded one at a time |
| **Laziness** | Work happens only for items actually consumed (`any`, `next`, `islice` can stop early) |
| **Infinite sequences** | `while True: yield ...` is fine |
| **Pipelines** | Chain stages without building intermediate lists |

A generator is **single use**: once exhausted it yields nothing more.

### `yield from`, `send`, `close`

```python
def chain_two(a, b):
    yield from a                    # delegate to another iterable
    yield from b

print(list(chain_two([1, 2], "ab")))                           # [1, 2, 'a', 'b']

def running_average():
    total, count, average = 0.0, 0, None
    while True:
        value = yield average       # receives a value from send()
        total += value
        count += 1
        average = total / count

avg = running_average()
next(avg)                           # prime it: run to the first yield
print(avg.send(10), avg.send(20), avg.send(60))                # 10.0 15.0 30.0
avg.close()                         # raises GeneratorExit inside, allowing cleanup
```

Generators that `send` are **coroutines** (the ancestor of `async`/`await`, see [async](../async-concurrency/README.md)).

### A generator pipeline over a "big file"

```python
import io

log = io.StringIO("""2026-01-01 INFO start
2026-01-01 ERROR disk full
2026-01-02 INFO ok
2026-01-02 ERROR timeout
2026-01-03 ERROR disk full
""")

def read_lines(f):
    for line in f:
        yield line.rstrip("\n")

def errors_only(lines):
    for line in lines:
        if " ERROR " in line:
            yield line

def messages(lines):
    for line in lines:
        yield line.split(" ", 2)[2]

from collections import Counter
print(Counter(messages(errors_only(read_lines(log)))))         # Counter({'disk full': 2, 'timeout': 1})
```

Each stage handles one line at a time; with a 50 GB file, memory use is still tiny. Real files are iterated the same way: `for line in open(path)`.

### Generators for resources and state machines

```python
from contextlib import contextmanager

@contextmanager
def opened(name, log):
    log.append(f"open {name}")
    try:
        yield name                  # the body of the "with" runs here
    finally:
        log.append(f"close {name}")

events = []
with opened("db", events) as db:
    events.append(f"use {db}")
print(events)                       # ['open db', 'use db', 'close db']
```

## 4. `itertools`: the standard-library toolbox for iterators

```python
import itertools as it

print(list(it.islice(it.count(10, 5), 4)))                     # [10, 15, 20, 25]   (infinite counter, sliced)
print(list(it.chain([1, 2], [3], (4,))))                       # [1, 2, 3, 4]
print(list(it.zip_longest("ab", [1, 2, 3], fillvalue="-")))    # [('a', 1), ('b', 2), ('-', 3)]
print(list(it.accumulate([1, 2, 3, 4])))                       # [1, 3, 6, 10]  (running totals)
print(list(it.takewhile(lambda x: x < 4, [1, 2, 5, 3])))       # [1, 2]
print(list(it.dropwhile(lambda x: x < 4, [1, 2, 5, 3])))       # [5, 3]
print(list(it.pairwise([1, 4, 9, 16])))                        # [(1, 4), (4, 9), (9, 16)]
print(list(it.batched(range(7), 3)))                           # [(0, 1, 2), (3, 4, 5), (6,)]   (3.12+)

words = sorted(["apple", "avocado", "banana", "blueberry", "cherry"])
print({k: list(g) for k, g in it.groupby(words, key=lambda w: w[0])})
# {'a': ['apple', 'avocado'], 'b': ['banana', 'blueberry'], 'c': ['cherry']}   (input must be sorted by the key)

print(list(it.product("ab", [1, 2])))                          # [('a', 1), ('a', 2), ('b', 1), ('b', 2)]
print(list(it.permutations("abc", 2)))                         # [('a', 'b'), ('a', 'c'), ('b', 'a'), ('b', 'c'), ('c', 'a'), ('c', 'b')]
print(list(it.combinations("abc", 2)))                         # [('a', 'b'), ('a', 'c'), ('b', 'c')]
a, b = it.tee([1, 2, 3])                                       # two independent iterators from one
print(list(a), list(b))                                        # [1, 2, 3] [1, 2, 3]
```

## 5. Functions as values

### Closures

A **closure** is a function that remembers variables from the scope where it was created.

```python
def make_multiplier(factor):
    def multiply(x):
        return x * factor           # "factor" is captured from the enclosing function
    return multiply

double, triple = make_multiplier(2), make_multiplier(3)
print(double(5), triple(5))                                    # 10 15

def counter():
    count = 0
    def increment():
        nonlocal count              # rebind the captured variable (without nonlocal this would fail)
        count += 1
        return count
    return increment

c = counter()
print(c(), c(), c())                                           # 1 2 3
```

**Late-binding gotcha:** closures capture the *variable*, not its value at creation time.

```python
funcs = [lambda: i for i in range(3)]
print([f() for f in funcs])                                    # [2, 2, 2]   (all see the final i)
funcs = [lambda i=i: i for i in range(3)]                      # bind the current value as a default argument
print([f() for f in funcs])                                    # [0, 1, 2]
```

### `lambda`, `map`, `filter`, `sorted(key=...)`

```python
people = [("ana", 31), ("bilal", 25), ("cy", 40)]
print(sorted(people, key=lambda p: p[1]))                      # [('bilal', 25), ('ana', 31), ('cy', 40)]
print(max(people, key=lambda p: p[1]))                         # ('cy', 40)
print(list(map(str.upper, ["a", "b"])))                        # ['A', 'B']
print(list(filter(None, [0, 1, "", "x", None])))               # [1, 'x']   (None filters out falsy values)
```

A `lambda` is a one-expression anonymous function; use it for short keys and callbacks, and use `def` for anything bigger or reused. Prefer comprehensions to `map`/`filter` with `lambda`.

### `functools` and `operator`

```python
from functools import partial, reduce, cache, lru_cache, cmp_to_key
import operator

def power(base, exp):
    return base ** exp

square = partial(power, exp=2)                                 # fix some arguments of a function
print(square(7), partial(int, base=2)("1010"))                 # 49 10

print(reduce(operator.mul, [1, 2, 3, 4]))                      # 24   (fold a sequence to one value)
print(sorted(people, key=operator.itemgetter(1))[0])           # ('bilal', 25)   (itemgetter replaces a lambda)

@cache                                                         # memoize: remember results per arguments
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)

print(fib(80), fib.cache_info().currsize)                      # 23416728348467685 81

@lru_cache(maxsize=2)                                          # bounded cache: evicts least recently used
def slow_square(n):
    return n * n
slow_square(1); slow_square(2); slow_square(3)
print(slow_square.cache_info())                                # CacheInfo(hits=0, misses=3, maxsize=2, currsize=2)
```

`functools.cache`/`lru_cache` require **hashable arguments** and are only safe for **pure** functions (same inputs, same output, no side effects).

### Higher-order functions and decorators

```python
import functools

def log_calls(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        wrapper.history.append((args, kwargs))
        return fn(*args, **kwargs)
    wrapper.history = []
    return wrapper

@log_calls
def add(a, b):
    return a + b

add(1, 2); add(3, b=4)
print(add.history)                                             # [((1, 2), {}), ((3,), {'b': 4})]
```

More on decorators: [Decorator pattern](../../04-oop/design-patterns/structural/decorator.md).

## 6. Pure functions and immutability (functional style in practice)

A **pure function** returns the same result for the same arguments and changes nothing outside itself. Pure code is easy to test, cache, reason about and run in parallel.

```python
def add_item_impure(cart, item):
    cart.append(item)                    # mutates the argument: callers get surprises
    return cart

def add_item_pure(cart, item):
    return [*cart, item]                 # builds a new list

original = ["pen"]
new = add_item_pure(original, "ink")
print(original, new)                     # ['pen'] ['pen', 'ink']
```

Python is not a purely functional language; use the style where it helps: transform data with comprehensions and generators, keep mutation local, prefer tuples/frozen dataclasses for shared data.

## 7. Two real-world examples

### Example 1: Processing a huge CSV without loading it
An analytics job must total revenue per country from a 30 GB CSV on a 4 GB machine. A generator pipeline streams rows:

```python
import csv, io
from collections import defaultdict

csv_text = "country,amount\nPK,10\nUS,5\nPK,7\nUS,1\nAE,20\n"

def rows(f):
    yield from csv.DictReader(f)

def parsed(rows_):
    for r in rows_:
        yield r["country"], float(r["amount"])

totals = defaultdict(float)
for country, amount in parsed(rows(io.StringIO(csv_text))):    # real code: open("big.csv")
    totals[country] += amount
print(dict(totals))                                            # {'PK': 17.0, 'US': 6.0, 'AE': 20.0}
```

Memory stays flat regardless of file size; each stage is tiny and testable.

### Example 2: A memoized API client and a retry decorator
Function-level caching (`@lru_cache` on a pure lookup) removes thousands of identical requests; `@retry(times=3)` (a decorator factory) adds resilience without touching the business functions; `functools.partial(fetch, session=session)` pre-binds shared arguments. Small functions composed with higher-order helpers replace large classes with configuration flags.

## 8. Tips, tricks and pitfalls

- Use `sum(x for x in ...)` / `any(...)` / `all(...)` directly on generator expressions; no brackets needed, no intermediate list.
- A generator is **exhausted after one pass**; call the generator function again for a fresh one.
- Do not use a list comprehension just for side effects (`[print(x) for x in xs]`); write a `for` loop.
- A comprehension should read like a sentence; break complex ones into a function or loop.
- `itertools.groupby` needs input **sorted by the same key**.
- Mutable default arguments (`def f(x, acc=[])`) are shared between calls; use `None`.
- Closures in loops capture variables, not values (late binding): bind with a default argument or `functools.partial`.
- Cache only pure functions with hashable arguments; `lru_cache` on methods can keep `self` alive (memory leak).
- Remember `yield from` for delegating to sub-generators, and `try/finally` inside generators for cleanup.
- `reduce` is rarely clearer than a loop or `sum`/`max`/`any`; use it for genuine folds.
- Exceptions inside a generator are raised at the `next()` call that triggers them, not where the generator was created.

## 9. Check yourself

1. How does a generator differ from a function that returns a list?
2. What does `yield` do to the function's state between calls?
3. What does a generator expression save compared to a list comprehension?
4. What does `yield from` do?
5. Why does `[lambda: i for i in range(3)]` give `[2, 2, 2]`, and how do you fix it?
6. What does `nonlocal` do?
7. What are the requirements for safely using `lru_cache`?
8. What does `itertools.groupby` require of its input?
9. What is a pure function and why is it useful?

<details>
<summary>Answers</summary>

1. A generator produces items lazily one at a time and pauses between them; a list-returning function computes everything up front and holds it all in memory.
2. It pauses the function and keeps its local variables and position; the next `next()` resumes right after the `yield`.
3. Memory: it stores no results, only the state needed to produce the next one; it also lets you stop early.
4. It delegates iteration to another iterable (or generator), yielding all its items, and passes through `send`/`throw`.
5. The lambdas capture the variable `i`, which ends at 2; bind the current value with a default argument (`lambda i=i: i`) or use `functools.partial`.
6. It lets an inner function rebind a variable in the enclosing function's scope (without it, assignment would create a new local).
7. Arguments must be hashable and the function should be pure (deterministic with no side effects), since results are reused.
8. The input must already be sorted by the grouping key; it groups only consecutive equal keys.
9. A pure function's result depends only on its arguments and it changes nothing outside; it is easy to test, cache, parallelize and reason about.

</details>

[Exercises](exercises.md) · [Summary](summary.md)
