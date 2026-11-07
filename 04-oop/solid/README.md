# SOLID Principles and Other Design Principles

## 1. The concept

**SOLID** is a set of five guidelines (popularized by Robert C. Martin) for writing object-oriented code that stays easy to change. They are not laws: they are heuristics that reduce the cost of change by keeping classes focused, extensible and substitutable.

| Letter | Principle | One-line version |
|--------|-----------|------------------|
| **S** | Single Responsibility | A class should have **one reason to change** |
| **O** | Open/Closed | Open for **extension**, closed for **modification** |
| **L** | Liskov Substitution | Subtypes must be **usable wherever the base type is expected** |
| **I** | Interface Segregation | Prefer **small, specific** interfaces over one fat one |
| **D** | Dependency Inversion | Depend on **abstractions**, not concretions |

Each section below shows a **violation**, the **symptoms** that tell you something is wrong, and a **refactoring**.

## 2. S: Single Responsibility Principle (SRP)

A class should have **one reason to change**: one actor or concern that can ask for modifications. "Responsibility" means a reason to change, not "does one tiny thing".

**Violation:** one class parses data, applies business rules, formats a report and writes to disk. A change to the file format, the tax rules or the report layout all edit the same class.

```python
import json, tempfile, os

class ReportTangled:
    def __init__(self, orders):
        self.orders = orders
    def total(self):                                     # business rule
        return sum(o["qty"] * o["price"] for o in self.orders)
    def render(self):                                    # presentation
        return f"TOTAL: {self.total():.2f}"
    def save(self, path):                                # persistence
        with open(path, "w") as f:
            f.write(self.render())
```

**Refactoring:** separate the reasons to change.

```python
class OrderCalculator:                                   # business rule
    def total(self, orders):
        return sum(o["qty"] * o["price"] for o in orders)

class TextReportFormatter:                               # presentation
    def render(self, total):
        return f"TOTAL: {total:.2f}"

class FileWriter:                                        # persistence
    def write(self, path, text):
        with open(path, "w") as f:
            f.write(text)

orders = [{"qty": 2, "price": 5.0}, {"qty": 1, "price": 7.5}]
text = TextReportFormatter().render(OrderCalculator().total(orders))
path = os.path.join(tempfile.mkdtemp(), "r.txt")
FileWriter().write(path, text)
print(text, open(path).read() == text)                   # TOTAL: 17.50 True
```

**Symptoms of violation:** class names with "And" or "Manager"; many unrelated imports; tests that need a database, the file system and a clock all at once; merge conflicts because different teams edit the same file. **Do not overdo it:** splitting into a class per function creates indirection without benefit. Split along real axes of change.

## 3. O: Open/Closed Principle (OCP)

You should be able to **add new behavior without editing existing, tested code**. You achieve this with abstraction (polymorphism, plug-ins, strategies).

**Violation:** every new discount type requires editing the same `if/elif` chain.

```python
def price_after_discount(kind, price):
    if kind == "none":
        return price
    elif kind == "student":
        return price * 0.8
    elif kind == "black_friday":
        return price * 0.5
    raise ValueError(kind)                               # must edit this function to add "employee"
```

**Refactoring:** each discount is a separate object behind a common interface; adding one is **new code, not an edit**.

```python
from abc import ABC, abstractmethod

class Discount(ABC):
    @abstractmethod
    def apply(self, price): ...

class NoDiscount(Discount):
    def apply(self, price): return price
class Student(Discount):
    def apply(self, price): return price * 0.8
class BlackFriday(Discount):
    def apply(self, price): return price * 0.5

class Checkout:
    def __init__(self, discount: Discount):
        self.discount = discount
    def total(self, price):
        return self.discount.apply(price)

class Employee(Discount):                                # added later: no edits above
    def apply(self, price): return price * 0.6

print(Checkout(Student()).total(100), Checkout(Employee()).total(100))     # 80.0 60.0
```

Variants of the same idea: a **registry** (dictionary mapping names to strategy classes), **plug-in discovery** (entry points, `__init_subclass__`), or simply **passing a function**. OCP is the goal; `if/elif` is acceptable while there are two stable cases (YAGNI), but not when each new feature edits the chain.

## 4. L: Liskov Substitution Principle (LSP)

If `S` is a subtype of `T`, objects of `T` can be replaced by objects of `S` **without breaking the program**. A subclass must honor the base class's **contract**:

- **Preconditions** cannot be strengthened (the subclass must not demand more).
- **Postconditions** cannot be weakened (it must not promise less).
- **Invariants** must be preserved.
- It must not throw exceptions the base contract does not allow.

**Violation (the classic):** `Square` as a subtype of `Rectangle`.

```python
class Rectangle:
    def __init__(self, w, h):
        self._w, self._h = w, h
    def set_width(self, w):  self._w = w
    def set_height(self, h): self._h = h
    def area(self): return self._w * self._h

class Square(Rectangle):
    def __init__(self, s): super().__init__(s, s)
    def set_width(self, w):  self._w = self._h = w       # keeps it square...
    def set_height(self, h): self._w = self._h = h       # ...and breaks the Rectangle contract

def stretch_to_6x2(rect: Rectangle):
    rect.set_width(6)
    rect.set_height(2)
    assert rect.area() == 12, f"area was {rect.area()}"

stretch_to_6x2(Rectangle(1, 1))                          # fine
try:
    stretch_to_6x2(Square(1))
except AssertionError as e:
    print("LSP violated:", e)                            # LSP violated: area was 4
```

Code written for `Rectangle` breaks when handed a `Square`: it is **not substitutable**, even though a square "is a" rectangle in geometry. The relationship that matters is behavioral, not taxonomic.

**Refactoring:** model the shared idea only (`Shape.area()`), make shapes **immutable**, or avoid the hierarchy.

```python
from dataclasses import dataclass

class Shape:
    def area(self): raise NotImplementedError

@dataclass(frozen=True)
class Rect(Shape):
    w: float
    h: float
    def area(self): return self.w * self.h

@dataclass(frozen=True)
class Sq(Shape):
    side: float
    def area(self): return self.side ** 2

print([s.area() for s in (Rect(6, 2), Sq(3))])           # [12, 9]
```

**More LSP smells:**
- A subclass method raises `NotImplementedError` or does nothing for an inherited operation (`Penguin.fly`): the base class is too broad. Split it (`Bird`, `FlyingBird`) or use composition.
- Subclass checks `isinstance` of its own type inside inherited logic.
- A subclass narrows accepted arguments (`save(self, obj: Admin)` when the base accepts any `User`).
- A subclass returns something with weaker guarantees (can return `None` where the base never does).

## 5. I: Interface Segregation Principle (ISP)

Clients should not be forced to depend on methods they do not use. Prefer several **small, role-specific** interfaces over one large one.

**Violation:** a fat interface forces implementations to stub methods they cannot support.

```python
from abc import ABC, abstractmethod

class Machine(ABC):                                      # fat interface
    @abstractmethod
    def print(self, doc): ...
    @abstractmethod
    def scan(self, doc): ...
    @abstractmethod
    def fax(self, doc): ...

class SimplePrinter(Machine):
    def print(self, doc): return f"printing {doc}"
    def scan(self, doc): raise NotImplementedError       # forced to implement what it cannot do
    def fax(self, doc): raise NotImplementedError
```

**Refactoring:** split into roles; compose them where a device has several.

```python
from typing import Protocol

class Printer(Protocol):
    def print(self, doc): ...
class Scanner(Protocol):
    def scan(self, doc): ...

class BasicPrinter:
    def print(self, doc): return f"printing {doc}"

class OfficeMachine:                                     # supports both roles
    def print(self, doc): return f"printing {doc}"
    def scan(self, doc): return f"scanning {doc}"

def run_print_job(p: Printer, doc):                      # needs only the Printer role
    return p.print(doc)

def run_scan_job(s: Scanner, doc):
    return s.scan(doc)

print(run_print_job(BasicPrinter(), "a"), "|", run_scan_job(OfficeMachine(), "b"))
# printing a | scanning b
```

In Python, **Protocols** and duck typing make small interfaces cheap: a function that needs only `read()` should accept any "readable", not a whole `FileManager`. ISP also applies to function signatures: do not pass a whole `User` object to a function that needs only an email.

## 6. D: Dependency Inversion Principle (DIP)

1. High-level modules (business rules) should not depend on low-level modules (databases, HTTP, files). **Both** should depend on **abstractions**.
2. Abstractions should not depend on details; **details depend on abstractions**.

"Inversion" refers to the **direction of the source-code dependency**: instead of `BusinessLogic -> MySqlDatabase`, you get `BusinessLogic -> Repository (interface) <- MySqlDatabase`.

**Violation:**

```python
class MySqlOrderRepository:
    def save(self, order): print("INSERT INTO orders ...")

class OrderServiceBad:
    def __init__(self):
        self.repo = MySqlOrderRepository()               # hard-wired low-level detail
    def place(self, order):
        self.repo.save(order)
```

**Refactoring:** the high-level service owns the abstraction it needs; the details implement it; the caller wires them together (dependency injection; see [composition](../composition-design/README.md)).

```python
from abc import ABC, abstractmethod

class OrderRepository(ABC):                              # the abstraction, owned by the business layer
    @abstractmethod
    def save(self, order): ...

class OrderService:
    def __init__(self, repo: OrderRepository):
        self.repo = repo
    def place(self, order):
        self.repo.save(order)

class SqlRepo(OrderRepository):
    def save(self, order): print("sql insert", order)
class InMemoryRepo(OrderRepository):
    def __init__(self): self.rows = []
    def save(self, order): self.rows.append(order)

mem = InMemoryRepo()
OrderService(mem).place({"id": 1})                       # unit test: no database
OrderService(SqlRepo()).place({"id": 2})                 # production: sql insert {'id': 2}
print(mem.rows)                                          # [{'id': 1}]
```

DIP is the principle; **dependency injection** is a technique to achieve it; an **IoC container** is optional tooling. The architecture built on DIP is called **hexagonal / ports and adapters / clean architecture**: business logic in the center with ports (interfaces), adapters (DB, web, queue) around it.

## 7. How the principles fit together

- **SRP** gives you small classes. **ISP** gives you small interfaces.
- **OCP** and **DIP** let you extend by adding implementations of abstractions instead of editing callers.
- **LSP** keeps those implementations safely interchangeable.
- Violating one often causes violating others: a god class (SRP) with a fat interface (ISP) bound to concrete details (DIP) cannot be extended without modification (OCP).

## 8. Other guiding principles

| Principle | Meaning | Caution |
|-----------|---------|---------|
| **DRY** (Don't Repeat Yourself) | Each piece of knowledge has one authoritative place | Do not merge code that is only *coincidentally* similar; duplication is cheaper than the wrong abstraction |
| **KISS** | Prefer the simplest design that works | Simple is not simplistic |
| **YAGNI** | Do not build for imagined future needs | Balance with obvious near-term variation |
| **Composition over inheritance** | Build behavior by combining objects | See [composition](../composition-design/README.md) |
| **Law of Demeter** | Talk only to your immediate collaborators | Avoid `a.b.c.d` chains |
| **Tell, don't ask** | Command objects instead of querying their state to decide | Keeps rules inside the owner |
| **Separation of concerns** | Different concerns (UI, logic, data) live in different modules | Leads to layers |
| **Principle of least astonishment** | Behave the way users of the API expect | Name things honestly |
| **Fail fast** | Detect and report errors at the earliest point | Validate in constructors |

## 9. Two real-world examples

### Example 1: A notification system that grew
A startup begins with `send_email(user, msg)`. SMS arrives: `if channel == "sms"`. Then push, Slack, WhatsApp: the function becomes a 200-line conditional that every feature edits and that breaks unrelated channels. The refactoring applies OCP and DIP: a `Notifier` interface with `send(user, msg)`, one class per channel, and a registry that maps channel names to classes. Adding Telegram is one new file plus one registry line; each channel has its own tests; the core `NotificationService` depends only on `Notifier`.

### Example 2: Testing a billing service without Stripe
A `BillingService` imports the Stripe SDK directly, so every test hits (or monkeypatches) the network. Introducing a `PaymentGateway` port (DIP) owned by the billing code, with a `StripeGateway` adapter and a `FakeGateway` for tests, makes tests fast and deterministic and allows adding PayPal later. The same refactoring splits reporting out of the billing class (SRP), and replaces `if provider == ...` with polymorphic gateways (OCP).

## 10. Tips, tricks and pitfalls

- Treat SOLID as **direction**, not dogma: apply it where change actually happens (the code that keeps getting edited).
- SRP: ask "who would ask me to change this?" If the answer is several different people or concerns, split.
- OCP: add the abstraction when the **second or third** variation appears ("rule of three"), not before.
- LSP: test subclasses against the **base class's tests**; if they fail, the hierarchy is wrong.
- ISP: small `Protocol`s at the consumer side beat large ABCs at the provider side.
- DIP: put the interface in the module that **uses** it, not the one that implements it.
- Do not create an interface for every class "just in case"; it adds noise without value.
- Over-applying SOLID yields dozens of tiny classes and indirection; optimize for readability.
- Many SOLID problems are fixed by the same tools: **composition, small interfaces, injection**.

## 11. Check yourself

1. State all five principles in one sentence each.
2. Why does `Square(Rectangle)` violate LSP even though a square is a rectangle?
3. How do you make this open for extension: a function with `if shape == "circle" ... elif shape == "square"`?
4. What is the difference between DIP, dependency injection and an IoC container?
5. How does ISP show up in Python (hint: `Protocol` and function signatures)?
6. A `User` class has `save_to_db()`, `send_welcome_email()` and `to_json()`. Which principle is violated and how do you fix it?
7. What does "inversion" invert in DIP?
8. Give one case where applying OCP too early is harmful.
9. What is the Law of Demeter?

<details>
<summary>Answers</summary>

1. SRP: one reason to change. OCP: extend without modifying. LSP: subtypes substitute for their base types. ISP: small, client-specific interfaces. DIP: depend on abstractions, not concretions.
2. Code written for `Rectangle` assumes width and height change independently (setting width 6 then height 2 gives area 12). A `Square` links them, so the same code gets area 4: the subclass breaks the base contract.
3. Give each shape a polymorphic `area()` (or register behaviors in a dictionary), so adding a shape means adding a class, not editing the function.
4. DIP is the design principle (depend on abstractions); dependency injection is a technique (pass collaborators in); an IoC container is a tool that automates the wiring.
5. Use small `Protocol`s (a function needing `read()` accepts any readable), and pass only the data a function needs rather than whole objects.
6. SRP: persistence, email and serialization are three reasons to change. Extract `UserRepository`, `WelcomeMailer` and a serializer; keep `User` as the domain object.
7. The direction of the source dependency: instead of the high-level module depending on the low-level one, the low-level module depends on an abstraction owned by the high-level module.
8. Adding plug-in frameworks and abstract factories for a rule that has one implementation and may never vary adds complexity and indirection that you then must maintain (YAGNI).
9. An object should only call methods of itself, its fields, its parameters and objects it creates; avoid reaching through chains like `a.b.c.d()`.

</details>

[Exercises](exercises.md) · [Summary](summary.md)
