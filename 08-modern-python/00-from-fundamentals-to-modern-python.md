# From Python Fundamentals to Modern Python

**Prerequisites:** all of [Python fundamentals](../00-foundations/python-fundamentals/README.md) (variables, control flow, functions, collections, files and errors, testing, a first look at classes). **You will learn:** how to turn the beginner code you already write into the idiomatic style the eight chapters of this part teach, one habit at a time, with a before and after for each, and where to read more.

## 1. In plain words

Beginner Python works. Modern Python is the same language written the way experienced developers write it: less boilerplate, more guarantees, easier to test and change. You do not need to learn a new language. You need about eight habit changes, and each one maps to a chapter here. This lesson is the map: read the pairs, then follow the link for depth.

## 2. Habit 1: say what the types are  → [typing](typing-hints/README.md)

```python
# before: the reader must guess
def total(prices, tax):
    return sum(prices) * (1 + tax)

# after: the contract is in the signature, and mypy can check it
def total_typed(prices: list[float], tax: float) -> float:
    return sum(prices) * (1 + tax)

print(total_typed([10.0, 5.0], 0.2))                     # 18.0
print(total_typed.__annotations__)                       # {'prices': list[float], 'tax': <class 'float'>, 'return': <class 'float'>}
```

Hints do not change how the code runs; a checker (`mypy`, `pyright`) reads them and catches `total_typed("x", 1)` before you run it.

## 3. Habit 2: use dataclasses instead of hand-written classes  → [dataclasses](dataclasses-enums/README.md)

```python
# before (from the classes lesson): boilerplate
class PointOld:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __repr__(self):
        return f"PointOld(x={self.x}, y={self.y})"
    def __eq__(self, other):
        return isinstance(other, PointOld) and (self.x, self.y) == (other.x, other.y)

# after: the same behaviour, generated
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: float
    y: float

print(Point(1, 2))                                       # Point(x=1, y=2)
print(Point(1, 2) == Point(1, 2), PointOld(1, 2) == PointOld(1, 2))       # True True
```

## 4. Habit 3: use enums, not magic strings

```python
from enum import Enum

# before: a typo like "shiped" silently never matches
status = "shipped"
print(status == "shiped")                                # False   (no error, just a bug)

# after: a closed set of values; a typo is an immediate AttributeError
class Status(Enum):
    PENDING = "pending"
    SHIPPED = "shipped"

print(Status("shipped") is Status.SHIPPED)               # True
try:
    Status.SHIPED
except AttributeError as e:
    print("caught:", e)                                  # caught: type object 'Status' has no attribute 'SHIPED'
```

## 5. Habit 4: comprehensions, generators and the standard library  → [generators](generators-functional/README.md)

```python
from collections import Counter, defaultdict
from itertools import islice

words = ["apple", "bob", "cat", "apple", "bob", "apple"]

# before: manual loops and bookkeeping
counts = {}
for w in words:
    if w in counts:
        counts[w] += 1
    else:
        counts[w] = 1

# after: say what you mean
print(counts == Counter(words))                          # True
print(Counter(words).most_common(1))                     # [('apple', 3)]
by_len = defaultdict(list)
for w in words:
    by_len[len(w)].append(w)
print(dict(by_len))                                      # {5: ['apple', 'apple', 'apple'], 3: ['bob', 'cat', 'bob']}

squares_big = [n * n for n in range(10) if n % 2 == 0]   # comprehension: build a list
lazy = (n * n for n in range(10**12))                    # generator: computes nothing until asked
print(squares_big, list(islice(lazy, 3)))                # [0, 4, 16, 36, 64] [0, 1, 4]
```

## 6. Habit 5: `with`, `pathlib` and f-strings for everyday I/O

```python
from pathlib import Path
import tempfile

# before: manual open/close and string concatenation
folder = Path(tempfile.mkdtemp())
f = open(str(folder) + "/notes.txt", "w")
f.write("hello")
f.close()                                                # forgotten close() leaks the file if an error happens first

# after: the context manager closes it even on errors; pathlib joins paths with /
path = folder / "notes.txt"
with path.open("w") as fh:
    fh.write("hello again")
print(path.read_text(), path.suffix, path.exists())      # hello again .txt True
name, n = "Ada", 3
print(f"{name} has {n} items, {n / 7:.2f} each")         # Ada has 3 items, 0.43 each
```

## 7. Habit 6: modern syntax that removes code  → [modern syntax](modern-syntax/README.md)

```python
# match for structured branching (Python 3.10+)
def describe(event):
    match event:
        case {"type": "click", "x": x, "y": y}:
            return f"click at {x},{y}"
        case {"type": "key", "key": k} if k.isupper():
            return f"shout {k}"
        case {"type": "key", "key": k}:
            return f"key {k}"
        case _:
            return "unknown"

print(describe({"type": "click", "x": 1, "y": 2}))       # click at 1,2
print(describe({"type": "key", "key": "A"}))             # shout A
print(describe({"type": "scroll"}))                      # unknown

# the walrus operator, | for dict merge and for types
data = [3, 8, 1]
if (n := len(data)) > 2:
    print(f"{n} items")                                  # 3 items
print({"a": 1} | {"b": 2})                               # {'a': 1, 'b': 2}
def parse(s: str) -> int | None:                         # "int or None" without importing Optional
    return int(s) if s.isdigit() else None
print(parse("42"), parse("x"))                           # 42 None
```

## 8. Habit 7: handle failure precisely, log, and test with pytest  → [exceptions, logging, testing](exceptions-logging-testing/README.md)

```python
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("demo")

# before: print and a bare except hide the real problem
def load_bad(text):
    try:
        return int(text)
    except:                                              # catches everything, even KeyboardInterrupt
        return 0

# after: catch only what you expect, say why, keep the traceback available
def load(text: str) -> int:
    try:
        return int(text)
    except ValueError:
        log.warning("not a number: %r, using 0", text)
        return 0

print(load("12"), load("abc"))                           # 12 0       (and a WARNING line is logged)

# tests: plain assert functions, run with `pytest` (see the testing chapter)
def test_load():
    assert load("5") == 5
    assert load("oops") == 0
test_load()
```

## 9. Habit 8: choose the right kind of concurrency, and measure  → [concurrency](async-concurrency/README.md), [performance](performance-profiling/README.md)

```python
import asyncio, time

async def fetch(name, delay):
    await asyncio.sleep(delay)                           # stands in for a network wait
    return name

async def main():
    start = time.perf_counter()
    results = await asyncio.gather(fetch("a", 0.2), fetch("b", 0.2), fetch("c", 0.2))
    return results, time.perf_counter() - start

results, elapsed = asyncio.run(main())
print(results, "sequential would take 0.6 s; measured", "under 0.4 s" if elapsed < 0.4 else "too slow")
# ['a', 'b', 'c'] sequential would take 0.6 s; measured under 0.4 s

import timeit
print(timeit.timeit("x in lst", "lst = list(range(10_000)); x = 9_999", number=200) >
      timeit.timeit("x in st", "st = set(range(10_000)); x = 9_999", number=200))   # True   a set lookup beats a list scan: measure, don't guess
```

Rule of thumb: waiting on I/O → `asyncio` or threads; heavy CPU work → processes; and before any tuning, measure ([the GIL lab](../06-operating-systems/processes-threads/02-threads-and-the-gil-lab.md) shows why).

## 10. Habit 9: a real project layout  → [packaging and tooling](packaging-tooling/README.md)

```text
myproject/
├── pyproject.toml        # name, version, dependencies, tool settings (replaces setup.py and requirements juggling)
├── src/myproject/
│   ├── __init__.py
│   └── core.py
└── tests/
    └── test_core.py
```

```bash
uv venv && uv pip install -e ".[dev]"     # an isolated environment, never `pip install` into the system Python
ruff check . && ruff format .             # lint and format
mypy src                                  # static types
pytest                                    # tests
```

## 11. Two real-world examples

**Example 1: A data script that grew into a service.** A 300-line script of untyped dicts passed between functions broke whenever a field was renamed. Replacing the dicts with frozen dataclasses and adding type hints let `mypy` find 14 wrong field accesses in one run; the tests then pinned the behaviour, and the refactor shipped without an incident.

**Example 2: A slow import job.** A script fetched 500 URLs one by one (about 8 minutes). Switching to `asyncio.gather` with a concurrency limit cut it to under 30 seconds, because the time was spent waiting on the network, not computing.

## 12. Common mistakes

- Adding type hints and never running a type checker (they then only decorate).
- Using a mutable default argument (`def f(x=[])`) or a dataclass field with a list default (use `field(default_factory=list)`).
- Catching `Exception` or using a bare `except:` everywhere.
- Reaching for `asyncio` or threads for CPU-bound work (use processes) or optimizing before measuring.
- Installing packages globally instead of in a virtual environment.
- Rewriting working code in a new style with no tests to prove it still behaves the same.

## 13. Practice

1. Rewrite `def area(w, h): return w * h` with type hints, then add a `Rectangle` frozen dataclass with an `area` method.
2. Replace the strings `"red"`, `"green"`, `"blue"` in a function with an `Enum`.
3. Turn this loop into a comprehension: `out = []; for n in nums: if n > 0: out.append(n * 2)`.
4. Rewrite `open`/`close` code for a log file using `with` and `pathlib`.
5. Use `match` to handle the tuples `("add", a, b)` and `("neg", a)`.
6. Which kind of concurrency fits: (a) downloading 100 files, (b) resizing 100 large images?

<details>
<summary>Solutions</summary>

1. ```python
   from dataclasses import dataclass

   def area(w: float, h: float) -> float:
       return w * h

   @dataclass(frozen=True)
   class Rectangle:
       w: float
       h: float
       def area(self) -> float:
           return self.w * self.h

   print(area(2, 3), Rectangle(2, 3).area())       # 6 6
   ```
2. ```python
   from enum import Enum

   class Color(Enum):
       RED = "red"
       GREEN = "green"
       BLUE = "blue"

   print(Color("red"), list(Color))
   ```
3. ```python
   nums = [3, -1, 2, 0]
   print([n * 2 for n in nums if n > 0])           # [6, 4]
   ```
4. ```python
   from pathlib import Path
   import tempfile

   log = Path(tempfile.mkdtemp()) / "app.log"
   with log.open("a") as f:
       f.write("started\n")
   print(log.read_text())                           # started
   ```
5. ```python
   def run(op):
       match op:
           case ("add", a, b):
               return a + b
           case ("neg", a):
               return -a
           case _:
               raise ValueError(op)

   print(run(("add", 2, 3)), run(("neg", 4)))      # 5 -4
   ```
6. (a) Downloads wait on the network: `asyncio` or threads. (b) Resizing is CPU work: `multiprocessing` (processes), since threads share the GIL.

</details>

## 14. Check yourself

1. Do type hints change how a program runs? What reads them?
2. What does `@dataclass` generate for you?
3. Why prefer an `Enum` to string constants?
4. When is a generator better than a list?
5. Why use `with` for files?
6. Which concurrency model suits I/O waits, and which CPU work?
7. What goes in `pyproject.toml`?

<details>
<summary>Answers</summary>

1. No; type checkers such as mypy and pyright (and editors) read them.
2. `__init__`, `__repr__`, `__eq__` and optionally ordering, hashing and immutability (`frozen=True`).
3. A closed set of values: typos fail loudly, and tools can check exhaustiveness.
4. When the data is large or infinite or you only need a few items: it computes lazily and uses little memory.
5. It guarantees the file is closed even if an error occurs.
6. I/O waits: `asyncio` or threads; CPU-bound work: processes.
7. The project's name, version, dependencies and the settings for its tools (ruff, mypy, pytest).

</details>

Next: start with [type hints](typing-hints/README.md), then work through the chapters in order.

[Back to Modern Python](README.md)
