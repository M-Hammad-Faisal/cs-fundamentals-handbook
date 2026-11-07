# Type Hints and Static Typing

## 1. The concept

Python is **dynamically typed**: a variable can hold any type and errors surface at runtime. **Type hints** (PEP 484 and successors) let you **annotate** the types you intend. The interpreter **ignores them at runtime**; external tools (**mypy**, **pyright**, your IDE) read them and find bugs before the code runs. This is **gradual typing**: you can add hints a little at a time, and hinted and unhinted code interoperate.

Why bother:

| Benefit | How |
|---------|-----|
| Catch bugs early | Wrong argument types, `None` not handled, misspelled attributes |
| Documentation that cannot rot | Signatures say what goes in and out |
| Better tooling | Autocomplete, safe renames, jump to definition |
| Safer refactoring | The checker lists every call site you broke |
| Design pressure | Hard-to-type code is often badly designed code |

```python
def greet(name: str, times: int = 1) -> str:
    return name * times

print(greet("ab", 2))                 # abab
print(greet.__annotations__)          # {'name': <class 'str'>, 'times': <class 'int'>, 'return': <class 'str'>}
print(greet("x", "3") if False else "Python does not enforce hints at runtime")
```

Running a checker over wrong calls reports problems without executing anything (real `mypy --strict` output):

```text
mp.py:6: error: Argument 2 to "greet" has incompatible type "str"; expected "int"  [arg-type]
mp.py:8: error: Incompatible types in assignment (expression has type "str", variable has type "int")  [assignment]
mp.py:13: error: Item "None" of "str | None" has no attribute "upper"  [union-attr]
```

## 2. The basic annotations

```python
# Variables
count: int = 0
ratio: float = 0.5
name: str = "ana"
flags: list[bool] = [True, False]                 # built-in generics (3.9+): no need for typing.List
scores: dict[str, int] = {"ana": 90}
point: tuple[float, float] = (1.0, 2.0)           # fixed-length tuple
numbers: tuple[int, ...] = (1, 2, 3)              # variable-length tuple
unique: set[str] = {"a"}

# Optional and unions (3.10+ syntax uses |)
def find(users: dict[str, int], name: str) -> int | None:     # same as Optional[int]
    return users.get(name)

def parse(value: int | str) -> int:
    return int(value)

# Callable and function-typed parameters
from collections.abc import Callable, Iterable, Sequence, Mapping, Iterator

def apply_all(fn: Callable[[int], int], xs: Iterable[int]) -> list[int]:
    return [fn(x) for x in xs]

print(apply_all(lambda n: n * 2, range(3)), find({"ana": 1}, "bo"), parse("42"))   # [0, 2, 4] None 42
```

**Guidelines for choosing types:**

- **Accept the most general type you need, return the most specific.** Parameters: `Iterable[int]`, `Sequence[str]`, `Mapping[str, int]`. Returns: `list[int]`, `dict[str, int]`.
- `X | None` means the value may be `None`; the checker forces you to handle it.
- `Any` turns checking off for that value (use sparingly); `object` means "anything, but I can only do object things"; `Never` means "does not return".
- `Callable[[A, B], R]` describes a function taking `A, B` and returning `R`; `Callable[..., R]` accepts any arguments.
- Annotate **function signatures** first (parameters and return); local variables are usually inferred.
- Use `None` as the return type for functions returning nothing.

### Useful special forms

```python
from typing import Literal, Final, ClassVar, Annotated, NewType, TypeAlias

Mode = Literal["r", "w", "a"]                     # only these exact values
def open_mode(mode: Mode) -> str:
    return mode

MAX_RETRIES: Final = 3                            # a constant: reassignment is flagged

UserId = NewType("UserId", int)                   # a distinct type for the checker (an int at runtime)
def load_user(uid: UserId) -> str:
    return f"user-{uid}"
print(load_user(UserId(7)), type(UserId(7)).__name__)          # user-7 int

Vector: TypeAlias = list[float]                   # a readable alias
Meters = Annotated[float, "unit: meters"]         # attach metadata (used by validation libraries)

class Config:
    instances: ClassVar[int] = 0                  # a class-level variable, not an instance field
```

`NewType` prevents mixing `UserId` and `OrderId` (both `int` at runtime) at zero cost.

## 3. Generics

A **generic** function or class works for many types while keeping their relationship: "returns the same type it was given".

### TypeVar and the modern syntax

```python
from typing import TypeVar

T = TypeVar("T")

def first_item(items: list[T]) -> T:               # classic style (all versions)
    return items[0]

def last_item[T](items: list[T]) -> T:             # new syntax (3.12+): no TypeVar declaration needed
    return items[-1]

print(first_item([1, 2, 3]), last_item(["a", "b"]))   # 1 b
```

The checker infers `first_item([1, 2])` is `int` and `first_item(["a"])` is `str`.

### Generic classes

```python
class Stack[T]:                                    # 3.12+ syntax; older: class Stack(Generic[T])
    def __init__(self) -> None:
        self._items: list[T] = []
    def push(self, item: T) -> None:
        self._items.append(item)
    def pop(self) -> T:
        return self._items.pop()
    def __len__(self) -> int:
        return len(self._items)

ints = Stack[int]()
ints.push(1); ints.push(2)
print(ints.pop(), len(ints))                       # 2 1
# ints.push("x")  <- the checker reports an error; at runtime it would work
```

### Bounded and constrained type variables

```python
from typing import Protocol

class SupportsLessThan(Protocol):
    def __lt__(self, other, /) -> bool: ...

def biggest[T: SupportsLessThan](a: T, b: T) -> T:     # T must support "<"
    return b if a < b else a

def add[N: (int, float)](a: N, b: N) -> N:             # constrained: exactly int or float
    return a + b

print(biggest(3, 9), biggest("pear", "apple"), add(2, 3), add(1.5, 2.0))   # 9 pear 5 3.5
```

### Preserving signatures in decorators: ParamSpec

```python
import functools
from collections.abc import Callable

def logged[**P, R](fn: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print("calling", fn.__name__)
        return fn(*args, **kwargs)
    return wrapper

@logged
def area(w: float, h: float) -> float:
    return w * h

print(area(2, 3))        # calling area  then 6
```

The checker still knows `area` takes two floats and returns a float. (Older spelling: `P = ParamSpec("P")`.)

### `Self` for fluent and factory methods

```python
from typing import Self

class Builder:
    def __init__(self) -> None:
        self.parts: list[str] = []
    def add(self, part: str) -> Self:              # returns the same (sub)class type
        self.parts.append(part)
        return self
    @classmethod
    def create(cls) -> Self:
        return cls()

class SpecialBuilder(Builder):
    def special(self) -> Self:
        return self.add("special")

print(SpecialBuilder.create().add("a").special().parts)    # ['a', 'special']
```

## 4. Structural typing: Protocols

A `Protocol` describes **what an object can do**, and any class with those members matches without inheriting (static duck typing). See also [encapsulation and abstraction](../../04-oop/encapsulation-abstraction/README.md).

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Renderable(Protocol):
    def render(self) -> str: ...

class Chart:
    def render(self) -> str:
        return "<chart/>"

class Table:
    def render(self) -> str:
        return "<table/>"

def render_all(items: list[Renderable]) -> str:
    return "".join(i.render() for i in items)

print(render_all([Chart(), Table()]), isinstance(Chart(), Renderable))    # <chart/><table/> True
```

Use **Protocols** for "anything shaped like X" (especially for third-party types and test fakes) and **ABCs** when you control the hierarchy and want enforcement and shared code.

## 5. Typed structures: `TypedDict`, `NamedTuple`, dataclasses

```python
from typing import TypedDict, NamedTuple, NotRequired

class UserDict(TypedDict):                         # a dict with known keys (JSON-like data)
    id: int
    name: str
    email: NotRequired[str]

class Point(NamedTuple):                           # immutable, tuple-compatible record
    x: float
    y: float

user: UserDict = {"id": 1, "name": "ana"}
p = Point(1.0, 2.0)
x, y = p
print(user["name"], p, x + y)                      # ana Point(x=1.0, y=2.0) 3.0
```

`TypedDict` has no runtime enforcement (it is a plain `dict`); it is for typing JSON payloads. For richer objects use [dataclasses](../dataclasses-enums/README.md). Runtime validation of untrusted data needs a library such as **pydantic**.

## 6. Narrowing, overloads and exhaustiveness

The checker **narrows** types inside branches:

```python
def describe(value: int | str | list[int] | None) -> str:
    if value is None:
        return "nothing"
    if isinstance(value, int):
        return f"int {value + 1}"              # here value is int
    if isinstance(value, str):
        return f"str {value.upper()}"          # here value is str
    return f"list of {len(value)}"             # here value is list[int]

print(describe(None), describe(4), describe("a"), describe([1, 2]))
# nothing int 5 str A list of 2
```

**Custom narrowing** with `TypeGuard` / `TypeIs`:

```python
from typing import TypeIs

def is_str_list(items: list[object]) -> TypeIs[list[str]]:
    return all(isinstance(i, str) for i in items)

data: list[object] = ["a", "b"]
if is_str_list(data):
    print(", ".join(data))                     # the checker now treats data as list[str]
```

**Exhaustiveness checking** with `assert_never` makes the checker flag unhandled cases when you extend a union or `Literal`:

```python
from typing import Literal, assert_never

Shape = Literal["circle", "square"]

def sides(shape: Shape) -> int:
    if shape == "circle":
        return 0
    elif shape == "square":
        return 4
    else:
        assert_never(shape)                    # if "triangle" is added to Shape, mypy errors HERE

print(sides("square"))                         # 4
```

**`@overload`** describes functions whose return type depends on argument types (the runtime function is still one):

```python
from typing import overload

@overload
def parse_value(raw: str, as_int: Literal[True]) -> int: ...
@overload
def parse_value(raw: str, as_int: Literal[False] = False) -> str: ...
def parse_value(raw: str, as_int: bool = False) -> int | str:
    return int(raw) if as_int else raw

print(parse_value("5", True) + 1, parse_value("5"))   # 6 5
```

## 7. Runtime facts about annotations

- Annotations are stored in `__annotations__` and ignored by the interpreter.
- `typing.get_type_hints(obj)` resolves string annotations; since **Python 3.14**, annotations are evaluated **lazily** (PEP 649/749), so forward references (using a class before it is defined) work without quotes, and `annotationlib.get_annotations()` is the inspection API. In older versions use `from __future__ import annotations` or quote the names (`"Node"`).
- Libraries read annotations at runtime: **dataclasses**, **pydantic**, **FastAPI** (request validation and OpenAPI docs from signatures), **typer**, **attrs**.

```python
import typing

class Node:
    def __init__(self, value: int, next: "Node | None" = None) -> None:
        self.value, self.next = value, next

print(typing.get_type_hints(Node.__init__)["next"])        # Node | None
```

## 8. Using a type checker

```text
pip install mypy                  # or: pip install pyright
mypy --strict src/                # check a package
```

A typical `pyproject.toml` setup:

```toml
[tool.mypy]
python_version = "3.12"
strict = true                     # or enable checks one by one for gradual adoption
files = ["src"]
```

How to adopt it in an existing codebase:

1. Start with **new code and public function signatures**; leave the rest unannotated.
2. Run the checker in CI so it never gets worse; use per-module overrides (`ignore_errors = true`) for legacy modules.
3. Replace `# type: ignore` with `# type: ignore[code]` and a comment; keep a short list.
4. Add annotations where the checker infers `Any` and where bugs actually occurred.
5. Use stub packages (`types-requests`) or inline types for third-party libraries.
6. Tighten settings over time (`disallow_untyped_defs`, `warn_return_any`, `strict`).

## 9. Two real-world examples

### Example 1: A FastAPI endpoint
`def create_user(user: UserIn) -> UserOut:` is both **documentation** and **behavior**: FastAPI reads the annotations to validate the request body, convert types, generate the OpenAPI schema and render interactive docs. Passing `user_id: int` in the path rejects `/users/abc` with a 422 automatically. The type hints are the single source of truth for the API contract, and mypy checks that the handler returns what it promises.

### Example 2: Catching a `None` bug before production
A function returns `User | None` from a lookup, and a caller does `find_user(id).email`. Without types it fails only when an id is missing in production (`AttributeError: 'NoneType'`). With hints the checker flags `Item "None" of "User | None" has no attribute "email"` during CI. The fix is to handle the missing case explicitly (raise a domain error, return a default, or use a `NullUser`), which is exactly the design you wanted anyway.

## 10. Tips, tricks and pitfalls

- Hints are **not enforced** at runtime; validate untrusted input explicitly (pydantic, manual checks).
- Prefer `collections.abc` types (`Sequence`, `Mapping`, `Iterable`) for parameters; concrete types for returns.
- Avoid `Any` in public APIs; use `object`, a Protocol or a generic instead.
- `list[int]` is **invariant**: a `list[bool]` is not accepted where `list[int]` is required (it could be mutated with an int). Use `Sequence[int]` for read-only access.
- Annotate `__init__` return as `None` so the checker checks the body.
- `Optional[X]` does **not** mean "optional argument": it means "may be `None"`. A parameter with a default is optional; its type may or may not include `None`.
- Do not duplicate type information in comments or docstrings.
- Use `typing.TYPE_CHECKING` for imports needed only for annotations (avoids import cycles).
- Over-specifying generics and overloads makes code unreadable; keep types as simple as the design allows.

## 11. Check yourself

1. Are type hints enforced at runtime? What reads them?
2. `X | None` versus a parameter with a default value: are they the same?
3. Why prefer `Sequence[int]` over `list[int]` for parameters?
4. What does a `TypeVar` express that `Any` does not?
5. When use a `Protocol` instead of an ABC?
6. What does `assert_never` give you?
7. What problem does `ParamSpec` solve?
8. Why is `list[bool]` not a valid `list[int]`?
9. Describe a gradual adoption plan for a large untyped codebase.

<details>
<summary>Answers</summary>

1. No. The interpreter stores them in `__annotations__` and ignores them. Static checkers (mypy, pyright), IDEs, and libraries such as pydantic, FastAPI and dataclasses read them.
2. No. `X | None` says the value may be `None` (the caller must pass something, possibly `None`); a default makes the argument omittable. They are independent.
3. It accepts any read-only sequence (list, tuple, range) so callers are not forced to build a list, and it documents that you do not mutate it.
4. The relationship between types: "the return type equals the input type". `Any` gives up checking and loses that link.
5. When you want to accept any object with the right methods without requiring inheritance (third-party classes, test fakes, small consumer-side interfaces); use an ABC when you control the hierarchy and want enforcement and shared behavior.
6. Static exhaustiveness checking: if you add a new member to a union or `Literal` and forget to handle it, the checker reports an error at the `assert_never` call.
7. It lets a decorator preserve the exact parameter types of the function it wraps, so the decorated function keeps its full signature for the checker.
8. Lists are mutable: if a `list[bool]` were accepted as `list[int]`, the function could append an arbitrary int and break the original list's type. Use `Sequence[int]` (covariant, read-only).
9. Annotate new code and public signatures; run the checker in CI with a baseline so errors do not increase; use per-module ignores for legacy code; add stubs for third-party libraries; progressively enable stricter flags; fix `Any` leaks in hot spots.

</details>

[Exercises](exercises.md) · [Summary](summary.md)
