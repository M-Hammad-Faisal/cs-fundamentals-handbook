# Polymorphism and the Python Data Model (Dunder Methods)

## 1. The concept

**Polymorphism** ("many forms") means one interface, many implementations: the same call does the right thing for different kinds of object. It is what lets you write code against a general idea (`shape.area()`) without checking concrete types.

| Kind | Mechanism | Python tools |
|------|-----------|--------------|
| **Subtype polymorphism** | A subclass overrides a method; the call is resolved at runtime (**dynamic dispatch**) | inheritance, ABCs |
| **Duck typing** | "If it walks like a duck": anything with the needed methods works | no declaration needed; `Protocol` for checking |
| **Ad hoc polymorphism** | Same name, behavior chosen by argument type | operator overloading, `functools.singledispatch` |
| **Parametric polymorphism** | Same code works for any type parameter | generics (`list[T]`), see [Modern Python](../../08-modern-python/README.md) |

## 2. Subtype polymorphism and dynamic dispatch

```python
import math

class Shape:
    def area(self):
        raise NotImplementedError
    def describe(self):                       # written once, works for every subclass
        return f"{type(self).__name__} with area {self.area():.2f}"

class Circle(Shape):
    def __init__(self, r): self.r = r
    def area(self): return math.pi * self.r ** 2

class Rect(Shape):
    def __init__(self, w, h): self.w, self.h = w, h
    def area(self): return self.w * self.h

class Triangle(Shape):
    def __init__(self, b, h): self.b, self.h = b, h
    def area(self): return 0.5 * self.b * self.h

shapes = [Circle(1), Rect(2, 3), Triangle(4, 5)]
for s in shapes:
    print(s.describe())
# Circle with area 3.14
# Rect with area 6.00
# Triangle with area 10.00
print(round(sum(s.area() for s in shapes), 2))     # 19.14
```

`describe()` and the loop contain no `if isinstance(...)`. Adding a `Hexagon` requires **no change** to existing code: that is the **Open/Closed Principle** delivered by polymorphism. Whenever you see a chain of `if type is A ... elif type is B ...`, ask whether overriding would do the job.

## 3. Duck typing and EAFP

Python does not care what a thing **is**, only what it **can do**.

```python
class Duck:
    def speak(self): return "Quack"
class Robot:
    def speak(self): return "Beep"
class Rock:
    pass

def make_noise(thing):
    try:
        return thing.speak()                  # EAFP: Easier to Ask Forgiveness than Permission
    except AttributeError:
        return "(silence)"

print([make_noise(x) for x in (Duck(), Robot(), Rock())])    # ['Quack', 'Beep', '(silence)']
```

**EAFP** (try it, handle failure) is idiomatic Python; **LBYL** ("look before you leap": `if hasattr(...)`) is racy and noisier. Built-in functions are polymorphic through **protocols**: `len(x)` calls `x.__len__()`, `for i in x` calls `x.__iter__()`, `x + y` calls `x.__add__(y)`.

## 4. The Python data model: dunder ("magic") methods

Special methods named `__like_this__` let your classes plug into the language: operators, `len`, iteration, `with`, calling, formatting. You never call them directly; the interpreter does.

| Category | Methods | Triggered by |
|----------|---------|--------------|
| Construction | `__new__`, `__init__`, `__del__` | `Cls(...)` |
| Representation | `__repr__`, `__str__`, `__format__`, `__bytes__` | `repr()`, `print`, `f"{x:spec}"` |
| Comparison | `__eq__`, `__ne__`, `__lt__`, `__le__`, `__gt__`, `__ge__`, `__hash__` | `==`, `<`, ..., `hash()` |
| Arithmetic | `__add__`, `__sub__`, `__mul__`, `__truediv__`, `__floordiv__`, `__mod__`, `__pow__`, `__neg__`, `__abs__` | `+ - * / // % ** -x abs(x)` |
| Reflected / in-place | `__radd__`, ..., `__iadd__`, ... | `3 + x`, `x += 1` |
| Conversion | `__bool__`, `__int__`, `__float__`, `__index__` | `bool(x)`, `if x:`, `int(x)` |
| Container | `__len__`, `__getitem__`, `__setitem__`, `__delitem__`, `__contains__`, `__iter__`, `__reversed__` | `len(x)`, `x[i]`, `in`, `for` |
| Iterator | `__iter__`, `__next__` | `next(it)` |
| Callable | `__call__` | `x(...)` |
| Context manager | `__enter__`, `__exit__` | `with x:` |
| Attribute access | `__getattr__`, `__getattribute__`, `__setattr__`, `__delattr__`, `__dir__` | `x.name` |
| Descriptor | `__get__`, `__set__`, `__delete__`, `__set_name__` | attribute on a class |
| Async | `__await__`, `__aiter__`, `__anext__`, `__aenter__`, `__aexit__` | `await`, `async for`, `async with` |

### A complete example: a `Vector` that feels built in

```python
import math
from functools import total_ordering

@total_ordering
class Vector:
    """2D vector with arithmetic, comparison, iteration, formatting."""
    __slots__ = ("x", "y")

    def __init__(self, x=0, y=0):
        self.x, self.y = x, y

    # representation
    def __repr__(self):
        return f"Vector({self.x!r}, {self.y!r})"
    def __str__(self):
        return f"({self.x}, {self.y})"
    def __format__(self, spec):
        spec = spec or "g"
        return f"({format(self.x, spec)}, {format(self.y, spec)})"

    # equality, hashing, ordering (by length)
    def __eq__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)
    def __hash__(self):
        return hash((self.x, self.y))
    def __lt__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return abs(self) < abs(other)

    # arithmetic
    def __add__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return Vector(self.x + other.x, self.y + other.y)
    def __sub__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return Vector(self.x - other.x, self.y - other.y)
    def __mul__(self, k):                      # vector * scalar
        if not isinstance(k, (int, float)):
            return NotImplemented
        return Vector(self.x * k, self.y * k)
    __rmul__ = __mul__                         # scalar * vector
    def __neg__(self):
        return Vector(-self.x, -self.y)
    def __abs__(self):
        return math.hypot(self.x, self.y)
    def __bool__(self):
        return bool(self.x or self.y)

    # iteration and unpacking
    def __iter__(self):
        yield self.x
        yield self.y

v, w = Vector(3, 4), Vector(1, 2)
print(v + w, v - w, v * 2, 2 * v, -v)          # (4, 6) (2, 2) (6, 8) (6, 8) (-3, -4)
print(abs(v), bool(Vector()), bool(v))         # 5.0 False True
print(repr(v), f"{v:.1f}")                     # Vector(3, 4) (3.0, 4.0)
x, y = v                                       # unpacking uses __iter__
print(x, y, list(v), max(v, w))                # 3 4 [3, 4] (3, 4)
print(sorted([v, w, Vector(0, 1)]))            # [Vector(0, 1), Vector(1, 2), Vector(3, 4)]
print(v > w, v >= w, {v: "a"}[Vector(3, 4)])   # True True a
```

Why it works: `v + w` becomes `type(v).__add__(v, w)`; `2 * v` first tries `int.__mul__(2, v)`, which returns `NotImplemented`, so Python tries the **reflected** `v.__rmul__(2)`.

### Rules for operator overloading

- Return **`NotImplemented`** (not raise) when you do not understand the other operand, so Python can try the other side's reflected method and finally raise `TypeError` itself.
- Keep operations **unsurprising**: `+` should be associative-ish and not mutate operands. Use `__iadd__` for in-place `+=` (mutating types like lists) and return `self`; if you do not define it, `+=` falls back to `__add__`.
- **Immutable value objects** return **new** objects.
- `@functools.total_ordering` fills in the missing comparisons from `__eq__` and one of `<, <=, >, >=`.
- If `__eq__` is defined, define `__hash__` consistently (or leave the class unhashable).
- Do not abuse operators: `+` for "send email" is a bad idea. Use them where a mathematical or collection meaning is natural.

## 5. Container protocols

Implement a few methods and you get a lot for free. Inheriting from `collections.abc.Sequence` requires only `__getitem__` and `__len__` and supplies `__contains__`, `__iter__`, `__reversed__`, `index` and `count`.

```python
from collections.abc import Sequence

class Playlist(Sequence):
    def __init__(self, songs):
        self._songs = list(songs)
    def __len__(self):
        return len(self._songs)
    def __getitem__(self, index):
        if isinstance(index, slice):                       # support slicing, returning the same type
            return Playlist(self._songs[index])
        return self._songs[index]
    def __repr__(self):
        return f"Playlist({self._songs!r})"

p = Playlist(["intro", "verse", "chorus", "outro"])
print(len(p), p[0], p[-1], p[1:3])          # 4 intro outro Playlist(['verse', 'chorus'])
print("chorus" in p, list(reversed(p)))     # True ['outro', 'chorus', 'verse', 'intro']
print(p.index("verse"), p.count("intro"))   # 1 1
print(list(p))                              # ['intro', 'verse', 'chorus', 'outro']
```

## 6. Callable objects and context managers

```python
class Retry:
    """An object that behaves like a function and remembers configuration."""
    def __init__(self, attempts):
        self.attempts = attempts
        self.calls = 0
    def __call__(self, fn, *args):
        last = None
        for _ in range(self.attempts):
            self.calls += 1
            try:
                return fn(*args)
            except ValueError as e:
                last = e
        raise last

flaky_state = {"n": 0}
def flaky():
    flaky_state["n"] += 1
    if flaky_state["n"] < 3:
        raise ValueError("not yet")
    return "ok"

retry = Retry(attempts=5)
print(retry(flaky), retry.calls)            # ok 3
```

```python
import time

class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self                                    # bound by "as t"
    def __exit__(self, exc_type, exc, tb):
        self.elapsed = time.perf_counter() - self.start
        return False                                   # False: do not swallow exceptions

with Timer() as t:
    sum(range(100_000))
print(t.elapsed >= 0)                                  # True

from contextlib import contextmanager

@contextmanager
def tag(name):
    print(f"<{name}>", end="")
    try:
        yield
    finally:
        print(f"</{name}>")

with tag("b"):
    print("bold", end="")                              # <b>bold</b>
```

`__exit__` runs even when the body raises; returning a truthy value from it suppresses the exception (do this only on purpose). Context managers are how Python guarantees cleanup (files, locks, transactions).

## 7. Iterators and generators

An **iterable** has `__iter__` returning an **iterator**; an iterator has `__next__` and raises `StopIteration` when done. A **generator function** (with `yield`) builds an iterator for you.

```python
class Countdown:
    def __init__(self, start): self.start = start
    def __iter__(self):                          # fresh iterator each time: reusable
        n = self.start
        while n > 0:
            yield n
            n -= 1

c = Countdown(3)
print(list(c), list(c))                          # [3, 2, 1] [3, 2, 1]

class OneShot:                                   # an iterator is single-use
    def __init__(self, items): self._it = iter(items)
    def __iter__(self): return self
    def __next__(self): return next(self._it)
o = OneShot("ab")
print(list(o), list(o))                          # ['a', 'b'] []
```

Generators are lazy: they produce one value at a time, use constant memory and can model infinite streams.

## 8. "Overloading" methods in Python

Python has **no** method overloading by signature (a later `def` with the same name replaces the earlier one). Alternatives:

```python
from functools import singledispatch, singledispatchmethod

@singledispatch
def to_text(x):
    return f"object: {x!r}"

@to_text.register
def _(x: int):
    return f"int: {x}"

@to_text.register(list)
def _(x):
    return "list of " + ", ".join(to_text(i) for i in x)

print(to_text(5), "|", to_text([1, 2]), "|", to_text(3.5))
# int: 5 | list of int: 1, int: 2 | object: 3.5

class Formatter:
    @singledispatchmethod
    def fmt(self, x):
        return str(x)
    @fmt.register
    def _(self, x: bool):
        return "yes" if x else "no"
    @fmt.register
    def _(self, x: float):
        return f"{x:.2f}"

f = Formatter()
print(f.fmt(True), f.fmt(3.14159), f.fmt("s"))   # yes 3.14 s
```

Other options: default and keyword arguments, `*args`/`**kwargs`, alternative constructors (`@classmethod`), and `typing.overload` (declares multiple signatures **for type checkers only**; the runtime function is still one).

## 9. Two real-world examples

### Example 1: `pathlib` and the `/` operator
`Path("data") / "raw" / "file.csv"` reads like a path because `Path.__truediv__` (and `__rtruediv__` for `"data" / Path(...)`) builds a new immutable `Path`. The class also implements `__fspath__`, so anything that accepts "a path-like" (`open`, `os.path`, `shutil`) works with it: duck typing through a protocol, plus operator overloading used where the meaning is natural.

### Example 2: Django `QuerySet`
A `QuerySet` implements `__iter__`, `__len__`, `__getitem__` (slicing becomes SQL `LIMIT/OFFSET`), `__bool__`, `__and__`/`__or__` (combine filters) and is lazy: the database query happens only when you iterate. Code written for "something iterable of rows" (templates, serializers, `for` loops) works with a QuerySet, a list or a generator alike. Because the container protocol is just dunder methods, a test can pass a plain list in place of a database result.

## 10. Tips, tricks and pitfalls

- Write polymorphic code against behavior, not concrete types; avoid `type(x) == ...` chains.
- Return `NotImplemented` from binary operators for unsupported operands; never raise `TypeError` yourself there.
- Define `__repr__` first; add `__str__` only if the user-facing text differs.
- `__eq__` without `__hash__` makes instances unhashable; mutable objects should not be hashable.
- Do not call dunder methods directly (`x.__len__()`); call `len(x)`.
- Iterators are exhausted after one pass; iterables that return a **new** iterator each time (generators in `__iter__`) are reusable.
- `__bool__` falls back to `__len__`; an empty container is falsy: `if items:` is idiomatic.
- Be careful with overloading `__getattr__`: it hides typos (misspelled attributes silently succeed if you return defaults).
- Use `abc`/`collections.abc` to get free behavior (`Sequence`, `Mapping`, `MutableMapping`) from a handful of methods.

## 11. Check yourself

1. Name four kinds of polymorphism and a Python tool for each.
2. What is dynamic dispatch? How does it remove `if/elif` type checks?
3. EAFP versus LBYL?
4. What happens on `2 * v` when `int.__mul__` does not know `Vector`?
5. Why return `NotImplemented` instead of raising `TypeError`?
6. Which methods must you implement to subclass `collections.abc.Sequence`? What do you get?
7. What is the difference between an iterable and an iterator?
8. What does `__exit__` returning `True` do?
9. How do you "overload" a function by argument type in Python?
10. Why should an `__eq__` and `__hash__` be defined together?

<details>
<summary>Answers</summary>

1. Subtype (overriding, ABCs), duck typing (any object with the right methods, `Protocol`), ad hoc (operator overloading, `singledispatch`), parametric (generics).
2. The method that runs is chosen at runtime from the object's actual class, so client code calls `shape.area()` and each subclass supplies its own version; no type tests are needed and new subclasses need no client changes.
3. EAFP tries the operation and handles the exception; LBYL checks conditions first. EAFP is idiomatic Python and avoids race conditions between check and use.
4. Python tries the reflected method `v.__rmul__(2)`; if that is also missing or returns `NotImplemented`, it raises `TypeError`.
5. Returning it lets Python try the other operand's reflected method and fall back correctly, so other types can cooperate with yours; raising short-circuits that.
6. `__getitem__` and `__len__`. You get `__contains__`, `__iter__`, `__reversed__`, `index`, `count`.
7. An iterable can produce an iterator (`__iter__`); an iterator produces values (`__next__`) and is consumed once, returning itself from `__iter__`.
8. It suppresses the exception raised in the `with` body; return a falsy value (or nothing) to let it propagate.
9. `functools.singledispatch` for functions and `singledispatchmethod` for methods (dispatching on the first argument's type), or use default/keyword arguments.
10. Equal objects must hash equal; otherwise dictionaries and sets misbehave. Defining only `__eq__` sets `__hash__` to `None` (unhashable).

</details>

[Exercises](exercises.md) · [Summary](summary.md)

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

Back to the [part overview](../README.md).
