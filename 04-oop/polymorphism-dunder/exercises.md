# Polymorphism and the Python Data Model: Exercises

1. Refactor this to remove the type checks using polymorphism:
   ```python
   def pay(employee):
       if employee.kind == "salaried":   return employee.annual / 12
       elif employee.kind == "hourly":   return employee.hours * employee.rate
       elif employee.kind == "contract": return employee.invoice_total
   ```
2. Implement `Fraction`-like class `Ratio(n, d)` with `+`, `-`, `*`, `==`, `<`, `__hash__`, `__repr__`, normalization by gcd, and support for `int + Ratio` through reflected methods.
3. Build `Matrix2x2` supporting `@` (`__matmul__`), `+`, `__eq__`, `__getitem__((row, col))`, and `__iter__` over rows. Verify `A @ I == A`.
4. Implement a `Money` class where `Money(5, "USD") + Money(3, "EUR")` raises a clear error, `sum([...])` works (hint: `__radd__` with `0`), and sorting works.
5. Create a read-only `Mapping` (via `collections.abc.Mapping`) that wraps a dict. Which methods did you have to write? Which came free?
6. Write a context manager (class-based and `@contextmanager`) that temporarily changes the working directory and restores it even on error.
7. Write a generator `windows(iterable, n)` that yields sliding windows lazily, then use it on an infinite counter with `itertools.islice`.
8. Use `singledispatch` to write `serialize(obj)` handling `int`, `str`, `list`, `dict`, and a fallback; register a custom class later without editing `serialize`.
9. Explain why `1 in OneShot("ab")` followed by `list(o)` loses data, and design the class to avoid it.
10. Make a `Counter`-like callable object that remembers how many times it was called and can be used as a decorator.

<details>
<summary>Solutions</summary>

**1.**
```python
class Salaried:
    def __init__(self, annual): self.annual = annual
    def pay(self): return self.annual / 12
class Hourly:
    def __init__(self, hours, rate): self.hours, self.rate = hours, rate
    def pay(self): return self.hours * self.rate
class Contract:
    def __init__(self, invoice_total): self.invoice_total = invoice_total
    def pay(self): return self.invoice_total
print([e.pay() for e in (Salaried(120000), Hourly(40, 25), Contract(3000))])   # [10000.0, 1000, 3000]
```
Adding `Intern` requires a new class only.

**2.**
```python
from math import gcd
class Ratio:
    def __init__(self, n, d=1):
        if d == 0: raise ZeroDivisionError("zero denominator")
        g = gcd(n, d) or 1
        if d < 0: n, d = -n, -d
        self.n, self.d = n // g, d // g
    def _coerce(self, o):
        if isinstance(o, int): return Ratio(o)
        if isinstance(o, Ratio): return o
        return None
    def __add__(self, o):
        o = self._coerce(o)
        if o is None: return NotImplemented
        return Ratio(self.n * o.d + o.n * self.d, self.d * o.d)
    __radd__ = __add__
    def __sub__(self, o):
        o = self._coerce(o)
        if o is None: return NotImplemented
        return Ratio(self.n * o.d - o.n * self.d, self.d * o.d)
    def __mul__(self, o):
        o = self._coerce(o)
        if o is None: return NotImplemented
        return Ratio(self.n * o.n, self.d * o.d)
    __rmul__ = __mul__
    def __eq__(self, o):
        o = self._coerce(o)
        return NotImplemented if o is None else (self.n, self.d) == (o.n, o.d)
    def __lt__(self, o):
        o = self._coerce(o)
        return NotImplemented if o is None else self.n * o.d < o.n * self.d
    def __hash__(self): return hash((self.n, self.d))
    def __repr__(self): return f"Ratio({self.n}, {self.d})"
print(Ratio(1, 2) + Ratio(1, 3), 1 + Ratio(1, 2), Ratio(2, 4) == Ratio(1, 2), Ratio(1, 3) < Ratio(1, 2))
```

**3.**
```python
class Matrix2x2:
    def __init__(self, rows): self.rows = [list(r) for r in rows]
    def __getitem__(self, rc): r, c = rc; return self.rows[r][c]
    def __iter__(self): return iter(tuple(r) for r in self.rows)
    def __eq__(self, o): return isinstance(o, Matrix2x2) and self.rows == o.rows
    def __add__(self, o): return Matrix2x2([[a + b for a, b in zip(r1, r2)] for r1, r2 in zip(self.rows, o.rows)])
    def __matmul__(self, o):
        return Matrix2x2([[sum(self[i, k] * o[k, j] for k in range(2)) for j in range(2)] for i in range(2)])
    def __repr__(self): return f"Matrix2x2({self.rows})"
A, I = Matrix2x2([[1, 2], [3, 4]]), Matrix2x2([[1, 0], [0, 1]])
print(A @ I == A, A + A, A[1, 0])
```

**4.**
```python
from functools import total_ordering
@total_ordering
class Money:
    def __init__(self, amount, cur): self.amount, self.cur = amount, cur
    def __add__(self, o):
        if o == 0: return self                      # lets sum() start from 0
        if not isinstance(o, Money): return NotImplemented
        if o.cur != self.cur: raise ValueError(f"cannot add {self.cur} and {o.cur}")
        return Money(self.amount + o.amount, self.cur)
    __radd__ = __add__
    def __eq__(self, o): return isinstance(o, Money) and (self.amount, self.cur) == (o.amount, o.cur)
    def __lt__(self, o):
        if o.cur != self.cur: raise ValueError("currency mismatch")
        return self.amount < o.amount
    def __hash__(self): return hash((self.amount, self.cur))
    def __repr__(self): return f"Money({self.amount}, {self.cur!r})"
print(sum([Money(1, "USD"), Money(2, "USD")]), sorted([Money(3, "USD"), Money(1, "USD")]))
try: Money(5, "USD") + Money(3, "EUR")
except ValueError as e: print(e)
```

**5.**
```python
from collections.abc import Mapping
class ReadOnly(Mapping):
    def __init__(self, d): self._d = dict(d)
    def __getitem__(self, k): return self._d[k]
    def __iter__(self): return iter(self._d)
    def __len__(self): return len(self._d)
m = ReadOnly({"a": 1})
print(m["a"], m.get("z", 0), list(m.items()), "a" in m)    # write 3 methods; get/items/keys/values/__contains__/__eq__ are free
```

**6.**
```python
import os, tempfile
from contextlib import contextmanager
class Chdir:
    def __init__(self, path): self.path = path
    def __enter__(self): self.old = os.getcwd(); os.chdir(self.path); return self
    def __exit__(self, *exc): os.chdir(self.old); return False
@contextmanager
def chdir(path):
    old = os.getcwd(); os.chdir(path)
    try: yield
    finally: os.chdir(old)
start = os.getcwd(); d = tempfile.mkdtemp()
with chdir(d): inside = os.getcwd()
print(os.getcwd() == start, os.path.samefile(inside, d))
try:
    with Chdir(d): raise RuntimeError
except RuntimeError: print(os.getcwd() == start)
```

**7.**
```python
from collections import deque
from itertools import count, islice
def windows(it, n):
    buf = deque(maxlen=n)
    for x in it:
        buf.append(x)
        if len(buf) == n: yield tuple(buf)
print(list(islice(windows(count(1), 3), 3)))     # [(1, 2, 3), (2, 3, 4), (3, 4, 5)]
```

**8.**
```python
from functools import singledispatch
@singledispatch
def serialize(o): raise TypeError(f"cannot serialize {type(o).__name__}")
@serialize.register
def _(o: int): return str(o)
@serialize.register
def _(o: str): return '"' + o + '"'
@serialize.register
def _(o: list): return "[" + ",".join(serialize(i) for i in o) + "]"
@serialize.register
def _(o: dict): return "{" + ",".join(f"{serialize(k)}:{serialize(v)}" for k, v in o.items()) + "}"
class Point:
    def __init__(self, x, y): self.x, self.y = x, y
@serialize.register(Point)
def _(p): return f'{{"x":{p.x},"y":{p.y}}}'
print(serialize({"a": [1, "b", Point(1, 2)]}))
```

**9.** `1 in o` iterates the iterator to look for `1`, consuming items. An iterator is single-use. Make the class an **iterable** whose `__iter__` returns a fresh iterator over stored data (`return iter(self._items)` or a generator) instead of being its own iterator.

**10.**
```python
import functools
class CountCalls:
    def __init__(self, fn): functools.update_wrapper(self, fn); self.fn, self.calls = fn, 0
    def __call__(self, *a, **kw): self.calls += 1; return self.fn(*a, **kw)
@CountCalls
def hello(name): return f"hi {name}"
hello("a"); hello("b"); print(hello.calls, hello("c"))
```

</details>

[Lesson](README.md) · [Summary](summary.md)
