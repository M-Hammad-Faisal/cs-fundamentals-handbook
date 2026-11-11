# Dataclasses, NamedTuple and Enums

## 1. The concept

Many classes exist only to **hold data**: a point, an order line, a configuration, an API response. Writing them by hand is repetitive: an `__init__` that copies each argument to `self`, a `__repr__` for debugging, an `__eq__` to compare. **Dataclasses** (`@dataclass`, since Python 3.7) generate all of that from a list of annotated fields. **Enums** give a fixed set of named constants (order status, colors, permissions) instead of loose strings and numbers.

Together they let you model data **clearly, safely and with very little code**.

## 2. Dataclasses

### Without and with a dataclass

```python
class PointManual:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def __repr__(self):
        return f"PointManual(x={self.x!r}, y={self.y!r})"
    def __eq__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)

from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

p = Point(1.5, 2.0)
print(p)                                  # Point(x=1.5, y=2.0)
print(p == Point(1.5, 2.0), p.x)          # True 1.5
p.x = 10                                  # mutable by default
print(p)                                  # Point(x=10, y=2.0)
```

`@dataclass` read the annotations (`x: float`, `y: float`) and generated `__init__`, `__repr__` and `__eq__` for you.

### Defaults and `field()`

```python
from dataclasses import dataclass, field

@dataclass
class Order:
    id: int
    customer: str
    items: list[str] = field(default_factory=list)       # a NEW list per instance
    status: str = "pending"
    notes: str = field(default="", repr=False)           # excluded from repr
    created_by: str = field(default="system", compare=False)   # ignored in ==

o1, o2 = Order(1, "ana"), Order(2, "bo")
o1.items.append("pen")
print(o1.items, o2.items)                                 # ['pen'] []
print(o1)                                                 # Order(id=1, customer='ana', items=['pen'], status='pending', created_by='system')
```

**Mutable defaults are rejected** (this prevents the classic shared-list bug):

```python
try:
    @dataclass
    class Bad:
        tags: list[str] = []                              # mutable default
except ValueError as e:
    print(type(e).__name__)                               # ValueError (mutable default <class 'list'> ... use default_factory)
```

Useful `field()` options:

| Option | Meaning |
|--------|---------|
| `default=` / `default_factory=` | Immutable default / function producing a fresh default |
| `init=False` | Not an `__init__` parameter (set it yourself, for example in `__post_init__`) |
| `repr=False` | Hide from `repr` |
| `compare=False` | Ignore in `==` and ordering |
| `hash=` | Include in `hash()` |
| `kw_only=True` | Must be passed by keyword |
| `metadata={...}` | Attach information for libraries and validators |

### Class options

```python
@dataclass(frozen=True, order=True, slots=True, kw_only=True)
class Version:
    major: int
    minor: int = 0
    patch: int = 0

v1, v2 = Version(major=1, minor=2), Version(major=1, minor=10)
print(v1 < v2, sorted([v2, v1]) == [v1, v2])              # True True   (order=True compares field by field)
try:
    v1.major = 2
except Exception as e:
    print(type(e).__name__)                               # FrozenInstanceError
print({v1: "release"}[Version(major=1, minor=2)])         # release   (frozen + eq => hashable)
```

| Option | Effect |
|--------|--------|
| `frozen=True` | Immutable; attribute assignment raises `FrozenInstanceError`; instances become hashable |
| `order=True` | Generates `<`, `<=`, `>`, `>=` comparing fields as a tuple in declaration order |
| `slots=True` | Uses `__slots__`: less memory, faster attribute access, no stray attributes (3.10+) |
| `kw_only=True` | All fields keyword-only (3.10+) |
| `eq=True` (default) | Generates `__eq__`; with `eq=True, frozen=False` the class is **unhashable** |
| `repr`, `init` | Turn off generation if you write your own |

### Validation and derived fields with `__post_init__`

```python
from dataclasses import dataclass, field, InitVar

@dataclass
class Rectangle:
    width: float
    height: float
    area: float = field(init=False)                       # computed, not passed in

    def __post_init__(self):
        if self.width <= 0 or self.height <= 0:
            raise ValueError("sides must be positive")
        self.area = self.width * self.height

print(Rectangle(2, 3))                                    # Rectangle(width=2, height=3, area=6)
try:
    Rectangle(-1, 3)
except ValueError as e:
    print(e)                                              # sides must be positive

@dataclass
class User:
    name: str
    password: InitVar[str]                                # used in __post_init__, NOT stored as a field
    password_hash: str = field(init=False, repr=False)

    def __post_init__(self, password):
        self.password_hash = f"hash({password})"          # stand-in for a real hash function

u = User("ana", "secret")
print(u, hasattr(u, "password"))                          # User(name='ana') False
```

### Inheritance and field ordering

Fields without defaults cannot follow fields with defaults. `kw_only` fixes this cleanly:

```python
from dataclasses import KW_ONLY

@dataclass
class Base:
    id: int
    active: bool = True

@dataclass
class Child(Base):
    _: KW_ONLY                                            # fields after this are keyword-only
    name: str                                             # no default is fine because it is keyword-only

print(Child(1, name="ana"))                               # Child(id=1, active=True, name='ana')
```

Child dataclasses inherit the parent's fields (parent fields first). Inheritance works, but prefer composition for anything beyond a small shared base (see [composition](../../04-oop/composition-design/README.md)).

### Helper functions

```python
from dataclasses import asdict, astuple, replace, fields, is_dataclass

@dataclass(frozen=True)
class Address:
    city: str
    zip: str

@dataclass(frozen=True)
class Customer:
    name: str
    address: Address

c = Customer("ana", Address("Lahore", "54000"))
print(asdict(c))                      # {'name': 'ana', 'address': {'city': 'Lahore', 'zip': '54000'}}   (recursive)
print(astuple(c))                     # ('ana', ('Lahore', '54000'))
c2 = replace(c, name="bo")            # a copy with one field changed (works with frozen)
print(c2.name, c.name)                # bo ana
print([f.name for f in fields(c)], is_dataclass(c))          # ['name', 'address'] True
```

### Pattern matching works out of the box

```python
@dataclass
class Circle:
    r: float
@dataclass
class Square:
    side: float

def area(shape):
    match shape:
        case Circle(r=r):
            return round(3.14159 * r * r, 2)
        case Square(side=s):
            return s * s

print(area(Circle(2)), area(Square(3)))                   # 12.57 9
```

## 3. `NamedTuple` and `TypedDict` for comparison

```python
from typing import NamedTuple, TypedDict

class Coord(NamedTuple):                                  # immutable, tuple-compatible
    lat: float
    lon: float

c = Coord(31.5, 74.3)
lat, lon = c                                              # unpacking works
print(c, c[0], c.lon, isinstance(c, tuple))               # Coord(lat=31.5, lon=74.3) 31.5 74.3 True

class MoviePayload(TypedDict):                            # a plain dict with known keys (for typing only)
    title: str
    year: int

m: MoviePayload = {"title": "Up", "year": 2009}
print(type(m).__name__)                                   # dict
```

### Which one should I use?

| Need | Choose |
|------|--------|
| Mutable record with defaults, methods, validation | `@dataclass` |
| Immutable value object, hashable | `@dataclass(frozen=True)` |
| Lightweight immutable record that is also a tuple (unpacking, tuple keys) | `NamedTuple` |
| Typing for JSON-like dictionaries | `TypedDict` |
| Validation and parsing of **untrusted** data (APIs, config files) | **pydantic** (or `attrs` with validators) |
| Tons of instances, memory critical | `@dataclass(slots=True)` or plain `__slots__` |
| Behavior-heavy class with invariants | a regular class |

Dataclasses do **no validation of types** at runtime: `Point("a", "b")` is accepted. Use `__post_init__` checks or pydantic when you need that.

## 4. Enums

An **enum** is a set of **named constants**. Compared with strings or integers, an enum prevents typos, supports `isinstance`, iterates, and makes code self-documenting.

```python
from enum import Enum

class Status(Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"

s = Status.PAID
print(s, s.name, s.value)                                 # Status.PAID PAID paid
print(Status("shipped"), Status["PENDING"])               # Status.SHIPPED Status.PENDING   (lookup by value / by name)
print(list(Status))                                       # [<Status.PENDING: 'pending'>, <Status.PAID: 'paid'>, <Status.SHIPPED: 'shipped'>]
print(s is Status.PAID, s == "paid", s.value == "paid")   # True False True   (members are not equal to raw strings)
try:
    Status("lost")
except ValueError as e:
    print("ValueError:", e)                               # ValueError: 'lost' is not a valid Status
```

### Variants

```python
from enum import IntEnum, StrEnum, Flag, auto, unique

class Priority(IntEnum):                                  # compares and does arithmetic like ints
    LOW = 1
    HIGH = 3
print(Priority.HIGH > Priority.LOW, Priority.HIGH + 1)    # True 4

class Color(StrEnum):                                     # (3.11+) members ARE strings
    RED = auto()                                          # auto() gives the lowercased name: "red"
    GREEN = auto()
print(Color.RED == "red", f"color={Color.GREEN}")         # True color=green

class Perm(Flag):                                         # combine members with | and test with &
    READ = auto()
    WRITE = auto()
    EXEC = auto()

rw = Perm.READ | Perm.WRITE
print(rw, Perm.READ in rw, Perm.EXEC in rw)               # Perm.READ|WRITE True False

@unique                                                   # forbid two names sharing a value
class Unit(Enum):
    METER = 1
    KILOMETER = 2
```

### Enums with data and behavior

```python
class Planet(Enum):
    MERCURY = (3.303e23, 2.4397e6)
    EARTH = (5.976e24, 6.37814e6)

    def __init__(self, mass, radius):                     # each member's value tuple is unpacked here
        self.mass, self.radius = mass, radius

    @property
    def surface_gravity(self):
        return 6.67430e-11 * self.mass / (self.radius ** 2)

print(round(Planet.EARTH.surface_gravity, 2))             # 9.8

class Shape(Enum):
    CIRCLE = "circle"
    SQUARE = "square"

    @classmethod
    def parse(cls, text):                                 # friendly parsing with a clear error
        try:
            return cls(text.strip().lower())
        except ValueError:
            raise ValueError(f"unknown shape {text!r}; choose from {[m.value for m in cls]}") from None

print(Shape.parse(" Circle "))                            # Shape.CIRCLE
```

### Enums and `match`

```python
def label(status: Status) -> str:
    match status:
        case Status.PENDING:
            return "waiting for payment"
        case Status.PAID:
            return "ready to ship"
        case Status.SHIPPED:
            return "on its way"

print(label(Status.PAID))                                 # ready to ship
```

With a type checker, add an `assert_never(status)` default (see [type hints](../typing-hints/README.md)) so adding a new member flags every unhandled place.

### Enums in dataclasses and serialization

```python
import json

@dataclass
class Shipment:
    id: int
    status: Status = Status.PENDING

ship = Shipment(1, Status.SHIPPED)
payload = json.dumps({"id": ship.id, "status": ship.status.value})     # store the value, not the member
print(payload)                                                          # {"id": 1, "status": "shipped"}
back = Shipment(**{**json.loads(payload), "status": Status(json.loads(payload)["status"])})
print(back)                                                             # Shipment(id=1, status=<Status.SHIPPED: 'shipped'>)
```

(`StrEnum`/`IntEnum` members serialize directly with `json.dumps` because they are strings/ints.)

## 5. Two real-world examples

### Example 1: A typed configuration object
A service loads settings from environment variables and a file into one **frozen dataclass**:

```python
import os

@dataclass(frozen=True, slots=True)
class Settings:
    database_url: str
    debug: bool = False
    workers: int = 4
    log_level: str = "INFO"

    @classmethod
    def from_env(cls, env=os.environ):
        return cls(database_url=env["DATABASE_URL"],
                   debug=env.get("DEBUG", "0") == "1",
                   workers=int(env.get("WORKERS", 4)))

settings = Settings.from_env({"DATABASE_URL": "sqlite:///a.db", "WORKERS": "8"})
print(settings)    # Settings(database_url='sqlite:///a.db', debug=False, workers=8, log_level='INFO')
```

Immutable (nobody changes it mid-run), self-documenting, easy to construct in tests (`Settings("sqlite://", workers=1)`), hashable and comparable.

### Example 2: Order workflow with an enum state machine

```python
class OrderState(StrEnum):
    CREATED = auto()
    PAID = auto()
    SHIPPED = auto()
    CANCELLED = auto()

ALLOWED = {
    OrderState.CREATED: {OrderState.PAID, OrderState.CANCELLED},
    OrderState.PAID: {OrderState.SHIPPED, OrderState.CANCELLED},
    OrderState.SHIPPED: set(),
    OrderState.CANCELLED: set(),
}

@dataclass
class OrderRecord:
    id: int
    state: OrderState = OrderState.CREATED
    def move_to(self, new: OrderState):
        if new not in ALLOWED[self.state]:
            raise ValueError(f"cannot go from {self.state} to {new}")
        self.state = new

order = OrderRecord(1)
order.move_to(OrderState.PAID); order.move_to(OrderState.SHIPPED)
print(order)                                              # OrderRecord(id=1, state=<OrderState.SHIPPED: 'shipped'>)
try:
    order.move_to(OrderState.CANCELLED)
except ValueError as e:
    print(e)                                              # cannot go from shipped to cancelled
```

## 6. Tips, tricks and pitfalls

- Use `field(default_factory=list)` for mutable defaults; dataclasses will refuse a bare `[]`.
- `frozen=True` gives immutability and hashability; mutate a frozen instance with `replace()`.
- `order=True` compares **all fields in order**; mark irrelevant ones `compare=False`.
- `@dataclass` does **not** validate or convert types; add `__post_init__` checks or use pydantic.
- Do not put expensive work in `__post_init__` that makes construction surprising.
- `asdict()` deep-copies recursively and ignores custom serialization; handle `datetime`, `Enum`, `Decimal` yourself when writing JSON.
- `slots=True` blocks adding new attributes and has quirks with multiple inheritance and `cached_property`.
- Prefer `StrEnum`/`IntEnum` when members must interoperate with strings/ints (JSON, databases), plain `Enum` when they should be distinct from raw values.
- Compare enum members with `is` or `==`, never with their raw values.
- Do not subclass an enum that has members; do not reuse values without `@unique` unless you want aliases.
- Never rely on enum **ordering** unless you use `IntEnum`/`order` explicitly.

## 7. Check yourself

1. What does `@dataclass` generate by default?
2. Why is `tags: list = []` rejected, and what is the fix?
3. What do `frozen=True`, `order=True` and `slots=True` do?
4. When does a dataclass become unhashable?
5. What is `__post_init__` for? What is `InitVar`?
6. Dataclass vs `NamedTuple` vs `TypedDict` vs pydantic?
7. What are `Enum`, `IntEnum`, `StrEnum` and `Flag` for?
8. How do you serialize an enum member to JSON?
9. Why is `Status.PAID == "paid"` false for a plain `Enum`?

<details>
<summary>Answers</summary>

1. `__init__`, `__repr__` and `__eq__` (plus ordering, hash, slots, frozen behavior when requested).
2. A mutable default would be shared by all instances; use `field(default_factory=list)`.
3. `frozen`: immutable and hashable; `order`: comparison operators by field order; `slots`: uses `__slots__` for less memory and no new attributes.
4. When `eq=True` and `frozen=False` (the default): `__hash__` is set to `None`.
5. `__post_init__` runs after the generated `__init__` for validation and derived fields; an `InitVar` is a parameter passed to `__init__` and `__post_init__` but not stored as a field.
6. Dataclass: mutable record with behavior; `NamedTuple`: immutable tuple-like record; `TypedDict`: typed dict shapes for checkers; pydantic: runtime validation and parsing of untrusted data.
7. `Enum`: distinct named constants; `IntEnum`: members that are ints; `StrEnum`: members that are strings; `Flag`: combinable bit flags (permissions).
8. Store `member.value` (or use `StrEnum`/`IntEnum`, which serialize directly), and rebuild with `Status(value)`.
9. Plain enum members are distinct objects from their values; compare `Status.PAID.value == "paid"` or use `StrEnum`.

</details>

[Exercises](exercises.md) · [Summary](summary.md)

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

Back to the [part overview](../README.md).
