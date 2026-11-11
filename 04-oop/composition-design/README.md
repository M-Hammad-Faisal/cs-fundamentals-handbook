# Composition, Delegation, Coupling and Object Design

## 1. The concept

Inheritance answers "what **is** this?" Composition answers "what does this **have** or **use**?". A `Car` *has an* `Engine`; a `Logger` *uses a* `Handler`. In composition one object holds references to others and **delegates** work to them.

The classic design advice, "**favor composition over inheritance**", exists because composition gives you:

| Benefit | Why |
|---------|-----|
| **Looser coupling** | Depends on a small interface, not on a parent's internals |
| **Runtime flexibility** | Swap a part while the program runs (`car.engine = ElectricEngine()`) |
| **Smaller, focused classes** | Each part has one job and can be tested alone |
| **Hidden surface** | Expose only the methods you choose (`Stack` over `list`) |
| **No hierarchy explosion** | N behaviors x M variants stay N + M classes, not N x M |

## 2. Composition and delegation

```python
class Engine:
    def __init__(self, hp):
        self.hp = hp
        self.running = False
    def start(self):
        self.running = True
        return f"{self.hp}hp engine running"

class Car:
    def __init__(self, engine):
        self.engine = engine             # "has-a": injected, not created inside
    def start(self):
        return "Car: " + self.engine.start()     # delegation

class ElectricEngine:                    # a different part honoring the same interface (start)
    def start(self):
        return "silent motor humming"

print(Car(Engine(150)).start())          # Car: 150hp engine running
car = Car(Engine(150))
car.engine = ElectricEngine()            # change behavior at runtime
print(car.start())                       # Car: silent motor humming
```

### Hierarchy explosion, and the composition fix

With inheritance, combining behaviors multiplies classes: `PdfReport`, `CsvReport`, `EmailedPdfReport`, `EmailedCsvReport`, `S3PdfReport`, ... With composition you choose a **format** and a **destination** independently:

```python
import json

class JsonFormat:
    def render(self, rows): return json.dumps(rows)
class CsvFormat:
    def render(self, rows):
        return "\n".join(",".join(map(str, r.values())) for r in rows)

class ListDestination:                    # stands in for email/S3/file
    def __init__(self): self.sent = []
    def deliver(self, payload): self.sent.append(payload)

class Report:
    def __init__(self, fmt, dest):
        self.fmt, self.dest = fmt, dest
    def run(self, rows):
        self.dest.deliver(self.fmt.render(rows))

rows = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
dest = ListDestination()
Report(CsvFormat(), dest).run(rows)
Report(JsonFormat(), dest).run(rows)
print(dest.sent)      # ['1,2\n3,4', '[{"a": 1, "b": 2}, {"a": 3, "b": 4}]']
```

This is the **Strategy** pattern ([behavioral patterns](../design-patterns/behavioral/strategy.md)). Two formats and N destinations need 2 + N small classes, not 2 x N.

### Automatic delegation with `__getattr__`

Forward unknown attributes to a wrapped object while overriding a few:

```python
class LoggingList:
    """Wraps a list, logs appends, forwards everything else."""
    def __init__(self):
        self._inner = []
        self.log = []
    def append(self, x):
        self.log.append(f"append {x}")
        self._inner.append(x)
    def __getattr__(self, name):               # only for names not found normally
        return getattr(self._inner, name)
    def __len__(self):                         # special methods are looked up on the type, so define them
        return len(self._inner)

ll = LoggingList()
ll.append(1); ll.append(2)
print(ll.log, ll.count(1), len(ll))            # ['append 1', 'append 2'] 1 2
```

Note that dunder methods (`__len__`, `__iter__`, ...) are **not** found through `__getattr__`; define them explicitly. This is the **Proxy/Decorator** idea in miniature.

## 3. Object relationships

| Relationship | Meaning | Lifetime | Python shape |
|--------------|---------|----------|--------------|
| **Dependency** ("uses") | A method takes or creates the other temporarily | Short | parameter or local variable |
| **Association** | Objects know each other | Independent | attribute reference |
| **Aggregation** (weak "has-a") | Whole has parts, parts can live elsewhere | Independent | `Team` holds `Player`s created elsewhere |
| **Composition** (strong "has-a") | Parts cannot exist without the whole | Whole owns parts | `House` creates its `Room`s |
| **Inheritance** | is-a | Class level | `class B(A)` |

```text
Customer 1 ---- * Order 1 <>---- * OrderLine      (<> = owns: composition)
Team o---- * Player                                (o = aggregation)
Report ..> Formatter                               (..> = dependency)
```

## 4. Coupling and cohesion

- **Cohesion** = how closely a class's parts belong together. **High cohesion** (one clear purpose) is good: `EmailValidator` validates emails. Low cohesion is the `Utils`/`Manager`/`Helper` junk drawer.
- **Coupling** = how much one module knows about another. **Low coupling** is good: depend on narrow interfaces, not concrete classes or internals.

Kinds of coupling from worst to best: content (reaching into another's internals) > common (shared globals) > control (passing flags that steer behavior) > stamp (passing whole structures when you need one field) > data (passing only needed values) > message (calling a narrow interface).

```python
# Tight coupling: the class builds its own dependency and reaches into its internals
class OrderServiceTight:
    def __init__(self):
        self.mailer = SmtpMailer("smtp.example.com")       # hard-coded: cannot test or swap
    def place(self, order):
        self.mailer.connection.send(order.customer.address.email, "thanks")   # chain of internals
```

## 5. Dependency injection (DI)

Do not create your collaborators inside a class; **receive** them. Then the caller decides the implementation, tests can pass fakes, and the class depends only on an interface.

```python
class OrderService:
    def __init__(self, repo, notifier, clock):
        self.repo, self.notifier, self.clock = repo, notifier, clock       # constructor injection
    def place(self, customer_email, items):
        order = {"email": customer_email, "items": list(items), "at": self.clock()}
        self.repo.save(order)
        self.notifier.send(customer_email, f"Order of {len(order['items'])} items received")
        return order

# Production wiring (real objects) would be built in ONE place at the program's edge.
# Tests inject simple fakes:
class FakeRepo:
    def __init__(self): self.saved = []
    def save(self, o): self.saved.append(o)
class FakeNotifier:
    def __init__(self): self.sent = []
    def send(self, to, msg): self.sent.append((to, msg))

repo, notifier = FakeRepo(), FakeNotifier()
svc = OrderService(repo, notifier, clock=lambda: "2026-01-01")
svc.place("a@x.com", ["pen", "ink"])
print(repo.saved[0]["at"], notifier.sent)
# 2026-01-01 [('a@x.com', 'Order of 2 items received')]
```

Benefits: deterministic tests (a fake clock), no network in unit tests, swapping implementations without editing the service. Keep the "wiring" in a **composition root** (`main()`); DI frameworks are optional, plain constructors are enough in Python.

Other injection styles: **setter** injection (assign an attribute later), **parameter** injection (pass the collaborator to one method), and passing **functions** (like `clock`) instead of objects.

## 6. Entities, value objects and aggregates (a light domain-modeling vocabulary)

| Concept | Identity | Mutability | Equality | Example |
|---------|----------|------------|----------|---------|
| **Value object** | None | Immutable | By value | `Money(5, "USD")`, `Email`, `DateRange` |
| **Entity** | Has an ID that persists | Mutable | By ID | `Customer`, `Order` |
| **Aggregate** | A cluster with one **root** entity | Changed only through the root | | `Order` (root) with its `OrderLine`s |

Rules of thumb: model concepts with rules as value objects (validate once in the constructor, then trust them everywhere); modify an aggregate only through its root so invariants (e.g. "order total = sum of lines") stay true.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Email:
    value: str
    def __post_init__(self):
        if "@" not in self.value:
            raise ValueError(f"invalid email: {self.value!r}")

class Order:                                      # aggregate root
    def __init__(self, order_id):
        self.id = order_id
        self._lines = []                          # internal entities, reachable only via the root
    def add_line(self, sku, qty, unit_price):
        if qty <= 0:
            raise ValueError("quantity must be positive")
        self._lines.append((sku, qty, unit_price))
    @property
    def total(self):
        return sum(q * p for _, q, p in self._lines)

o = Order(1)
o.add_line("pen", 2, 5)
o.add_line("ink", 1, 7)
print(o.total, Email("a@x.com") == Email("a@x.com"))     # 17 True
try:
    Email("nope")
except ValueError as e:
    print(e)                                             # invalid email: 'nope'
```

## 7. Designing a class: a worked example

**Requirement:** a library lets members borrow books; members may hold at most 3 loans; borrowed books are unavailable.

**Step 1: find nouns (candidate classes) and verbs (methods).** Member, Book, Loan, Library; borrow, return.
**Step 2: assign responsibilities (CRC cards).** *Library*: knows books and members, coordinates `checkout`. *Member*: knows its loans and the limit. *Book*: knows its availability. *Loan*: records who and what.
**Step 3: decide relationships.** Library composes Books and Members; a Loan associates Member and Book.
**Step 4: protect invariants** (loan limit, availability) in the class that owns the data.

```python
class Book:
    def __init__(self, title):
        self.title = title
        self._available = True
    @property
    def available(self): return self._available
    def _mark(self, value): self._available = value

class Member:
    MAX_LOANS = 3
    def __init__(self, name):
        self.name = name
        self._loans = []
    def can_borrow(self):
        return len(self._loans) < self.MAX_LOANS
    @property
    def loans(self): return tuple(self._loans)

class Library:
    def __init__(self):
        self._books, self._members = {}, {}
    def add_book(self, title):
        self._books[title] = Book(title)
    def join(self, name):
        self._members[name] = Member(name)
    def checkout(self, member_name, title):
        member, book = self._members[member_name], self._books[title]
        if not book.available:
            raise ValueError(f"{title!r} is already borrowed")
        if not member.can_borrow():
            raise ValueError(f"{member_name} has reached the loan limit")
        book._mark(False)
        member._loans.append(book)
    def give_back(self, member_name, title):
        member, book = self._members[member_name], self._books[title]
        member._loans.remove(book)
        book._mark(True)

lib = Library()
for t in ("A", "B", "C", "D"):
    lib.add_book(t)
lib.join("ana"); lib.join("bo")
for t in ("A", "B", "C"):
    lib.checkout("ana", t)
for who, title in (("ana", "D"), ("bo", "A")):
    try:
        lib.checkout(who, title)
    except ValueError as e:
        print(e)
# ana has reached the loan limit
# 'A' is already borrowed
lib.give_back("ana", "A")
lib.checkout("bo", "A")
print([b.title for b in lib._members["bo"].loans])      # ['A']
```

(`Library` reaches into `Member._loans` and `Book._mark` because they are collaborators in one module; in a larger design you would give `Member` `add_loan`/`remove_loan` methods so each object guards its own state.)

## 8. Code smells that point to design problems

| Smell | Symptom | Typical fix |
|-------|---------|-------------|
| **God class** | One class with dozens of methods and unrelated fields | Split by responsibility (SRP) |
| **Feature envy** | A method uses another object's data more than its own | Move the method to that class |
| **Primitive obsession** | Strings/ints everywhere for concepts (`email: str`, `price: float`) | Value objects (`Email`, `Money`) |
| **Long parameter list** | 6+ parameters | Parameter object, builder, or split the function |
| **Shotgun surgery** | One change touches many classes | Group related behavior |
| **Inappropriate intimacy** | Classes reach into each other's internals | Narrow interfaces, Law of Demeter |
| **Switch on type** | `if isinstance ... elif ...` repeated | Polymorphism |
| **Data clump** | The same 3 fields travel together | Extract a class |
| **Refused bequest** | Subclass ignores inherited behavior | Use composition instead |

Refactor in **small, test-protected steps**; the unit tests from DI are what make that safe.

## 9. Testing object-oriented code

Design for testability and the structure gets better:

- Inject collaborators so tests substitute **fakes** (simple working stand-ins), **stubs** (canned answers) or **mocks** (assert on interactions via `unittest.mock`).
- Test **behavior through the public interface**, not private attributes.
- Prefer fakes over mocks when feasible; mocks tied to implementation make refactoring painful.
- One concept per test; arrange, act, assert.

```python
import unittest
from unittest.mock import Mock

class TestOrderService(unittest.TestCase):
    def test_sends_confirmation(self):
        repo, notifier = Mock(), Mock()
        svc = OrderService(repo, notifier, clock=lambda: "t")
        svc.place("a@x.com", ["pen"])
        notifier.send.assert_called_once_with("a@x.com", "Order of 1 items received")
        repo.save.assert_called_once()

suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestOrderService)
result = unittest.TextTestRunner(verbosity=0).run(suite)
print(result.wasSuccessful())                # True
```

## 10. Two real-world examples

### Example 1: Python's `logging` module
A `Logger` does not subclass "file logger" and "network logger". It **has** a list of `Handler`s (stream, file, HTTP, syslog), each of which **has** a `Formatter` and `Filter`s. You configure behavior by assembling parts: log to the console in a simple format and to a rotating file in JSON, simultaneously. New destinations are new handlers; the logger never changes. This is composition, delegation and the Strategy pattern working together, and it is why logging scales from scripts to large systems.

### Example 2: Requests `Session` and transport adapters
`requests.Session` composes **adapters** mounted per URL prefix (`session.mount("https://", HTTPAdapter(max_retries=3))`). Retry policy, connection pooling and even offline test adapters are plugged in without subclassing `Session`. Tests mount a fake adapter that returns canned responses; no network, no monkeypatching of the library. A design built on small replaceable parts is easy to extend and to test.

## 11. Tips, tricks and pitfalls

- Default to composition; reach for inheritance only for true is-a with polymorphism.
- Inject dependencies (constructor arguments); build the object graph in one composition root.
- Depend on narrow interfaces (protocols, ABCs, or just "a callable"), not on concrete classes.
- Make value objects immutable and validate them at construction (`Email`, `Money`).
- Respect the Law of Demeter: avoid `a.b.c.d()` chains.
- Keep classes cohesive; if a name ends in `Manager`, `Helper` or `Utils`, check for a missing concept.
- Do not delegate through `__getattr__` and forget dunders (they are looked up on the type).
- Do not over-engineer: introduce an interface or a pattern when a second variant or a test need actually appears.
- Watch for hidden global state (module-level singletons); it defeats DI and testing.

## 12. Check yourself

1. State "favor composition over inheritance" and give three reasons.
2. How does composition avoid class explosion?
3. Difference between aggregation and composition? Give examples.
4. Define cohesion and coupling; which do you want high or low?
5. What is dependency injection and how does it help testing?
6. Value object vs entity vs aggregate root?
7. Name three code smells and fixes.
8. Why do dunder methods not work through `__getattr__` delegation?
9. Fake vs stub vs mock?

<details>
<summary>Answers</summary>

1. Prefer building behavior by combining objects (has-a) over deep subclassing (is-a). Reasons: looser coupling to the parent's internals, behavior can change at runtime, smaller focused classes, only the needed interface is exposed, and no hierarchy explosion.
2. Behaviors vary independently as separate objects (format x destination = 2 + N classes) instead of a subclass for every combination.
3. Aggregation: parts can exist independently of the whole (a team and its players). Composition: parts are owned and live and die with the whole (a house and its rooms, an order and its lines).
4. Cohesion: how well a class's parts belong together (want high). Coupling: dependence between modules (want low).
5. Passing collaborators in from outside instead of constructing them inside. Tests inject fakes (in-memory repo, fixed clock), so they run fast and deterministically without network or database.
6. Value object: immutable, equality by value, no identity (`Money`). Entity: has a persistent identity, mutable (`Customer`). Aggregate root: the entity through which a cluster of related objects is modified so invariants hold (`Order` and lines).
7. God class (split by responsibility), primitive obsession (introduce value objects), switch on type (polymorphism), feature envy (move method), long parameter lists (parameter object).
8. Implicit special-method lookup happens on the type, bypassing instance `__getattr__`; define the dunders you need explicitly.
9. A fake is a lightweight working implementation (in-memory repo). A stub returns canned answers. A mock records calls so you can assert on interactions.

</details>

[Exercises](exercises.md) · [Summary](summary.md)

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

Back to the [part overview](../README.md).
