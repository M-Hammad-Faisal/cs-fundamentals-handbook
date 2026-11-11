# Dataclasses, NamedTuple and Enums: Exercises

These problems go with the [Dataclasses, NamedTuple and Enums lesson](README.md). Try each one before opening its solution.

## Problems

1. Convert this class to a dataclass and list what was generated:
   ```python
   class Item:
       def __init__(self, sku, price, qty=1):
           self.sku, self.price, self.qty = sku, price, qty
       def __repr__(self):
           return f"Item({self.sku!r}, {self.price!r}, {self.qty!r})"
       def __eq__(self, o):
           return (self.sku, self.price, self.qty) == (o.sku, o.price, o.qty)
   ```
2. Build a `Cart` dataclass with an `items: list[Item]` field and a `total` property. Show why `items=[]` as a default fails and what to use.
3. Create a frozen, ordered `Money(amount_cents: int, currency: str)` that rejects negative amounts, and sort a list of them. Why does `order=True` compare currency too?
4. Write a dataclass `Temperature` with `celsius` and a computed `fahrenheit` field (not an `__init__` parameter).
5. Use `replace`, `asdict` and `astuple` on a nested frozen dataclass; explain what each is for.
6. Define `Weekday(IntEnum)` and a function `is_weekend(day)`; show comparison and iteration.
7. Define `Permission(Flag)` with READ/WRITE/DELETE and an `ADMIN` alias combining all; test membership.
8. Build a `TrafficLight` enum where each member has a duration and a `next()` method that cycles.
9. Make an `Order` dataclass with a `state: OrderState` enum and a transition table; reject illegal moves. Add a test.
10. Choose between dataclass, `NamedTuple`, `TypedDict` and pydantic for: (a) rows returned from a CSV reader, (b) a JSON request body from the internet, (c) a settings object, (d) 3D coordinates used as dict keys.

<details>
<summary>Solutions</summary>

**1.**
```python
from dataclasses import dataclass

@dataclass
class Item:
    sku: str
    price: float
    qty: int = 1

print(Item("pen", 2.5), Item("pen", 2.5) == Item("pen", 2.5))        # Item(sku='pen', price=2.5, qty=1) True
```
Generated: `__init__`, `__repr__`, `__eq__` (and `__match_args__` for pattern matching).

**2.**
```python
from dataclasses import field

@dataclass
class Cart:
    items: list[Item] = field(default_factory=list)
    @property
    def total(self) -> float:
        return sum(i.price * i.qty for i in self.items)

c = Cart(); c.items.append(Item("pen", 2.5, 4))
print(c.total, Cart().items is Cart().items)                         # 10.0 False
```
`items: list[Item] = []` raises `ValueError` because the list would be shared by every cart.

**3.**
```python
@dataclass(frozen=True, order=True)
class Money:
    amount_cents: int
    currency: str
    def __post_init__(self):
        if self.amount_cents < 0:
            raise ValueError("amount must not be negative")

print(sorted([Money(500, "USD"), Money(100, "USD"), Money(300, "EUR")]))
# [Money(amount_cents=100, currency='USD'), Money(amount_cents=300, currency='EUR'), Money(amount_cents=500, currency='USD')]
```
`order=True` compares fields as a tuple in declaration order (amount first, then currency). Comparing amounts of different currencies is usually meaningless; real money types often raise on mixed currencies instead.

**4.**
```python
@dataclass
class Temperature:
    celsius: float
    fahrenheit: float = field(init=False)
    def __post_init__(self):
        self.fahrenheit = self.celsius * 9 / 5 + 32

print(Temperature(100))                                              # Temperature(celsius=100, fahrenheit=212.0)
```

**5.**
```python
from dataclasses import replace, asdict, astuple

@dataclass(frozen=True)
class Pos:
    x: int; y: int
@dataclass(frozen=True)
class Unit:
    name: str; pos: Pos

u = Unit("scout", Pos(1, 2))
print(replace(u, name="tank"), asdict(u), astuple(u))
# `replace`: a modified copy (frozen instances cannot be edited); `asdict`: nested dict for JSON; `astuple`: nested tuple
```

**6.**
```python
from enum import IntEnum

class Weekday(IntEnum):
    MON = 1; TUE = 2; WED = 3; THU = 4; FRI = 5; SAT = 6; SUN = 7

def is_weekend(day: Weekday) -> bool:
    return day >= Weekday.SAT

print(is_weekend(Weekday.SUN), is_weekend(Weekday.MON), [d.name for d in Weekday][:3], Weekday.FRI < Weekday.SAT)
```

**7.**
```python
from enum import Flag, auto

class Permission(Flag):
    READ = auto(); WRITE = auto(); DELETE = auto()
    ADMIN = READ | WRITE | DELETE

user = Permission.READ | Permission.WRITE
print(Permission.WRITE in user, Permission.DELETE in user, Permission.ADMIN in user, Permission.ADMIN)
```

**8.**
```python
from enum import Enum

class TrafficLight(Enum):
    RED = 30
    GREEN = 25
    YELLOW = 5
    @property
    def seconds(self): return self.value
    def next(self):
        members = list(type(self))
        return members[(members.index(self) + 1) % len(members)]

light, seen = TrafficLight.RED, []
for _ in range(4):
    seen.append((light.name, light.seconds)); light = light.next()
print(seen)                                                          # [('RED', 30), ('GREEN', 25), ('YELLOW', 5), ('RED', 30)]
```

**9.**
```python
import unittest
from enum import StrEnum, auto

class State(StrEnum):
    NEW = auto(); PAID = auto(); SHIPPED = auto()

MOVES = {State.NEW: {State.PAID}, State.PAID: {State.SHIPPED}, State.SHIPPED: set()}

@dataclass
class Ord:
    id: int
    state: State = State.NEW
    def move(self, to: State):
        if to not in MOVES[self.state]:
            raise ValueError(f"illegal move {self.state} -> {to}")
        self.state = to

class T(unittest.TestCase):
    def test_flow(self):
        o = Ord(1); o.move(State.PAID); o.move(State.SHIPPED)
        self.assertEqual(o.state, State.SHIPPED)
    def test_illegal(self):
        with self.assertRaises(ValueError):
            Ord(1).move(State.SHIPPED)
print(unittest.TextTestRunner(verbosity=0).run(unittest.defaultTestLoader.loadTestsFromTestCase(T)).wasSuccessful())
```

**10.** (a) `NamedTuple` or a small frozen dataclass (rows are immutable records). (b) **pydantic** (untrusted input needs validation); `TypedDict` only to type the shape. (c) Frozen dataclass (possibly loaded via pydantic settings). (d) `NamedTuple` or `frozen=True` dataclass: both are hashable, so they work as dict keys.

</details>

[Lesson](README.md) · [Summary](summary.md)
