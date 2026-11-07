# Composition and Object Design: Exercises

1. A `Bird` base class has `fly()`. `Penguin` inherits it and raises an error. Redesign with composition so that flying is an optional capability.
2. Model an `Employee` who can be a manager, an engineer, a part-timer, or combinations. Show the inheritance explosion, then implement it with composition (roles as parts).
3. Rewrite `OrderServiceTight` from the lesson with constructor injection and show a test with fakes (no SMTP).
4. Make a `TextProcessor` that accepts a list of step objects (each with `apply(text)`) and runs them in order: strip, lowercase, remove punctuation. Add a new step without touching `TextProcessor`.
5. Build `LimitedStack` by composition around a `list`, with `max_size`, `push` (raises on overflow), `pop`, `peek`, `__len__`, `__iter__` (top first) and `__repr__`.
6. Identify smells and refactor:
   ```python
   def make_invoice(name, street, city, zip, country, item1, price1, item2, price2, tax, currency, notes):
       ...
   ```
7. Draw (as text) the UML relationships for: a `University` has `Department`s; a `Department` has `Professor`s who can move departments; a `Course` is taught by a `Professor`; a `Course` has `Lesson`s that die with it.
8. Write a value object `DateRange(start, end)` (frozen, validates `start <= end`) with `overlaps(other)`, `days` and `__contains__`.
9. Write a unit test using `unittest.mock` for a `PasswordResetService(users, mailer)` verifying an email is sent only when the user exists.
10. Explain tight versus loose coupling in one example of your own, and rewrite the tight version.

<details>
<summary>Solutions</summary>

**1.**
```python
class Flying:
    def move(self): return "flapping through the air"
class Walking:
    def move(self): return "waddling"
class Bird:
    def __init__(self, name, mover): self.name, self.mover = name, mover
    def move(self): return f"{self.name}: {self.mover.move()}"
print(Bird("sparrow", Flying()).move(), "|", Bird("penguin", Walking()).move())
```
No `Penguin` ever pretends to fly, so no contract is broken.

**2.**
```python
class Role:
    def duties(self): raise NotImplementedError
class ManagerRole(Role):
    def duties(self): return ["approve budgets"]
class EngineerRole(Role):
    def duties(self): return ["write code"]
class PartTimeRole(Role):
    def duties(self): return ["works 20h/week"]
class Employee:
    def __init__(self, name, *roles): self.name, self.roles = name, list(roles)
    def duties(self): return [d for r in self.roles for d in r.duties()]
print(Employee("Sam", ManagerRole(), EngineerRole(), PartTimeRole()).duties())
```
With inheritance you would need `ManagerEngineer`, `PartTimeManager`, `PartTimeManagerEngineer`, ... (2^n combinations).

**3.**
```python
class OrderServiceLoose:
    def __init__(self, mailer): self.mailer = mailer
    def place(self, order): self.mailer.send(order["email"], "thanks")
class FakeMailer:
    def __init__(self): self.sent = []
    def send(self, to, msg): self.sent.append((to, msg))
m = FakeMailer(); OrderServiceLoose(m).place({"email": "a@x.com"}); print(m.sent)
```

**4.**
```python
import string
class Strip:      apply = staticmethod(lambda t: t.strip())
class Lower:      apply = staticmethod(lambda t: t.lower())
class NoPunct:    apply = staticmethod(lambda t: t.translate(str.maketrans("", "", string.punctuation)))
class TextProcessor:
    def __init__(self, steps): self.steps = steps
    def run(self, text):
        for s in self.steps: text = s.apply(text)
        return text
class Squeeze:    apply = staticmethod(lambda t: " ".join(t.split()))     # new step, no edits above
print(TextProcessor([Strip, Lower, NoPunct, Squeeze]).run("  Hello,   WORLD!  "))     # hello world
```

**5.**
```python
class LimitedStack:
    def __init__(self, max_size): self._items, self.max_size = [], max_size
    def push(self, x):
        if len(self._items) >= self.max_size: raise OverflowError("stack full")
        self._items.append(x)
    def pop(self): return self._items.pop()
    def peek(self): return self._items[-1]
    def __len__(self): return len(self._items)
    def __iter__(self): return reversed(self._items)
    def __repr__(self): return f"LimitedStack({self._items!r}, max_size={self.max_size})"
s = LimitedStack(2); s.push(1); s.push(2)
try: s.push(3)
except OverflowError as e: print(e)
print(list(s), s.pop(), len(s))
```

**6.** Smells: long parameter list, data clumps (address fields, item/price pairs), primitive obsession (country/currency strings, price floats). Refactor:
```python
from dataclasses import dataclass
@dataclass(frozen=True)
class Address: street: str; city: str; zip: str; country: str
@dataclass(frozen=True)
class LineItem: description: str; unit_price_cents: int; qty: int = 1
def make_invoice(name: str, address: Address, items: list[LineItem], tax_rate: float, currency: str, notes: str = ""): ...
```

**7.**
```text
University <>---- * Department            (composition: departments belong to the university)
Department o----- * Professor             (aggregation: professors can move)
Course ----> Professor                    (association: taught by)
Course <>---- * Lesson                    (composition: lessons die with the course)
```

**8.**
```python
from dataclasses import dataclass
from datetime import date
@dataclass(frozen=True)
class DateRange:
    start: date; end: date
    def __post_init__(self):
        if self.start > self.end: raise ValueError("start after end")
    @property
    def days(self): return (self.end - self.start).days + 1
    def overlaps(self, o): return self.start <= o.end and o.start <= self.end
    def __contains__(self, d): return self.start <= d <= self.end
r = DateRange(date(2026, 1, 1), date(2026, 1, 10))
print(r.days, date(2026, 1, 5) in r, r.overlaps(DateRange(date(2026, 1, 10), date(2026, 1, 12))))   # 10 True True
```

**9.**
```python
import unittest
from unittest.mock import Mock
class PasswordResetService:
    def __init__(self, users, mailer): self.users, self.mailer = users, mailer
    def request(self, email):
        user = self.users.find(email)
        if user is None: return False
        self.mailer.send(email, "reset link")
        return True
class T(unittest.TestCase):
    def test_known_user(self):
        users, mailer = Mock(), Mock(); users.find.return_value = object()
        self.assertTrue(PasswordResetService(users, mailer).request("a@x.com"))
        mailer.send.assert_called_once_with("a@x.com", "reset link")
    def test_unknown_user(self):
        users, mailer = Mock(), Mock(); users.find.return_value = None
        self.assertFalse(PasswordResetService(users, mailer).request("z@x.com"))
        mailer.send.assert_not_called()
r = unittest.TextTestRunner(verbosity=0).run(unittest.defaultTestLoader.loadTestsFromTestCase(T)); print(r.wasSuccessful())
```

**10.** Tight: `class Report: def __init__(self): self.db = PostgresDb("prod")` hard-codes the database, so you cannot test or swap it. Loose: `class Report: def __init__(self, db): self.db = db`, with any object providing `fetch(query)`; production passes `PostgresDb`, tests pass an in-memory fake.

</details>

[Lesson](README.md) · [Summary](summary.md)
