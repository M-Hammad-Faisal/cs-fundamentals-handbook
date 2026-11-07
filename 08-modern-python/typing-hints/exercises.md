# Type Hints: Exercises

1. Add type hints to this function and say what mypy would report for `average("abc")`:
   ```python
   def average(numbers):
       return sum(numbers) / len(numbers)
   ```
2. Write `first_or_default(items, default)` that works for any element type and returns the same type. Annotate it with a generic `T`.
3. This code compiles but crashes at runtime. Which annotation makes the checker catch it, and how do you fix the code?
   ```python
   # skip  (this crashes on purpose)
   def find_user(users: dict[str, str], key: str) -> str:
       return users.get(key)
   print(find_user({}, "ana").upper())
   ```
4. Define `Stack[T]` with `push`, `pop`, `peek` (returning `T | None` when empty) and `__len__`.
5. Create a `Literal`-typed `Direction` ("N", "E", "S", "W") and a function `turn_right` using exhaustive `if/elif` plus `assert_never`.
6. Write a typed decorator `@timed` using `ParamSpec` that preserves the signature of the wrapped function and prints the duration.
7. Define a `Protocol` `SupportsArea` and a function `total_area(shapes: Iterable[SupportsArea]) -> float`; pass two unrelated classes.
8. Use `TypedDict` for a JSON user payload with an optional `email`, and write `display_name(user: UserDict) -> str`.
9. Explain why `def f(xs: list[int])` rejects a `list[bool]` argument but `def f(xs: Sequence[int])` accepts it.
10. Plan how you would add typing to a 50,000-line untyped project in four steps.

<details>
<summary>Solutions</summary>

**1.**
```python
from collections.abc import Sequence

def average(numbers: Sequence[float]) -> float:
    return sum(numbers) / len(numbers)

print(average([1, 2, 3]))                            # 2.0
```
`average("abc")` is reported: `Argument 1 to "average" has incompatible type "str"; expected "Sequence[float]"`. (A `str` is a `Sequence[str]`, not of floats.) At runtime it would raise `TypeError`.

**2.**
```python
def first_or_default[T](items: list[T], default: T) -> T:
    return items[0] if items else default

print(first_or_default([3, 4], 0), first_or_default([], "none"))     # 3 none
```

**3.** `users.get(key)` returns `str | None`, so the declared `-> str` is wrong; mypy reports `Incompatible return value type (got "str | None", expected "str")`. Fix: declare `-> str | None` and handle `None` at the call site, or raise.
```python
def find_user(users: dict[str, str], key: str) -> str | None:
    return users.get(key)

name = find_user({}, "ana")
print(name.upper() if name is not None else "unknown")              # unknown
```

**4.**
```python
class Stack[T]:
    def __init__(self) -> None:
        self._items: list[T] = []
    def push(self, item: T) -> None:
        self._items.append(item)
    def pop(self) -> T:
        return self._items.pop()
    def peek(self) -> T | None:
        return self._items[-1] if self._items else None
    def __len__(self) -> int:
        return len(self._items)

s = Stack[str](); s.push("a")
print(s.peek(), len(s), Stack[int]().peek())                         # a 1 None
```

**5.**
```python
from typing import Literal, assert_never

Direction = Literal["N", "E", "S", "W"]

def turn_right(d: Direction) -> Direction:
    if d == "N": return "E"
    elif d == "E": return "S"
    elif d == "S": return "W"
    elif d == "W": return "N"
    else:
        assert_never(d)                                              # error here if a new direction is added

print(turn_right("W"))                                               # N
```

**6.**
```python
import functools, time
from collections.abc import Callable

def timed[**P, R](fn: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            print(f"{fn.__name__} took {time.perf_counter() - start:.6f}s")
    return wrapper

@timed
def add(a: int, b: int) -> int:
    return a + b

print(add(2, 3))
```

**7.**
```python
from collections.abc import Iterable
from typing import Protocol

class SupportsArea(Protocol):
    def area(self) -> float: ...

class Circle:
    def __init__(self, r: float) -> None: self.r = r
    def area(self) -> float: return 3.14159 * self.r ** 2

class Plot:                                                          # unrelated class that happens to match
    def __init__(self, w: float, h: float) -> None: self.w, self.h = w, h
    def area(self) -> float: return self.w * self.h

def total_area(shapes: Iterable[SupportsArea]) -> float:
    return sum(s.area() for s in shapes)

print(round(total_area([Circle(1), Plot(2, 3)]), 2))                 # 9.14
```

**8.**
```python
from typing import NotRequired, TypedDict

class UserDict(TypedDict):
    id: int
    name: str
    email: NotRequired[str]

def display_name(user: UserDict) -> str:
    email = user.get("email")
    return f"{user['name']} <{email}>" if email else user["name"]

print(display_name({"id": 1, "name": "Ana"}), display_name({"id": 2, "name": "Bo", "email": "b@x.com"}))
```

**9.** `list` is mutable and invariant: if a `list[bool]` were accepted, the function could `append(5)` and corrupt the caller's list of bools. `Sequence[int]` is read-only and covariant, so a sequence of bools (a subtype of int) is safe.

**10.** (1) Configure mypy/pyright in CI with a baseline so error counts cannot grow; (2) require annotations on all new and changed code and on public module interfaces; (3) add types to the most-imported, most-bug-prone modules first and replace broad `Any`/`# type: ignore` over time; (4) tighten flags progressively (`disallow_untyped_defs`, `warn_return_any`, then `strict`) per package, and add stub packages (`types-*`) for third-party libraries.

</details>

[Lesson](README.md) · [Summary](summary.md)
