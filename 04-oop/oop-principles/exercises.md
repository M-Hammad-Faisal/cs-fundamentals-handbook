# OOP Principles: Exercises

## Part A: Concepts in code

**A1. Encapsulation.** Write a `Thermostat` class that stores a target temperature. Reject values outside 10 to 30 degrees C. Expose the value through a property with validation on the setter.

**A2. Abstraction.** Define an abstract `Notifier` with a `send(message)` method. Implement `EmailNotifier` and `SmsNotifier`. Write `alert(notifier, text)` that works with either. Show that `Notifier()` cannot be instantiated.

**A3. Inheritance types.** Build one example each of single, multilevel, hierarchical and multiple inheritance using vehicles. Print the `__mro__` of the multiple-inheritance class.

**A4. Polymorphism.** Create `Circle`, `Rectangle` and `Triangle` classes with an `area()` method. Compute the total area of a mixed list with one loop. Then add `Hexagon` without changing that loop.

**A5. Operator overloading.** Implement a `Money` class (amount, currency) with `+`, `==`, `<`, and `__repr__`. Raise an error when adding different currencies.

## Part B: Spot the problem

**B1.** What is wrong with this code?
```python
def add_item(item, items=[]):
    items.append(item)
    return items
```

**B2.** Why does this raise an error, and how do you fix it?
```python
class A:
    def __init__(self):
        self.x = 1

class B(A):
    def __init__(self):
        self.y = 2

print(B().x)
```

**B3.** Does this violate Liskov Substitution? Explain.
```python
class Bird:
    def fly(self): ...

class Penguin(Bird):
    def fly(self):
        raise NotImplementedError
```

**B4.** A class `ReportManager` fetches data, formats a PDF, uploads to S3 and sends email. Which SOLID principle does it violate and how would you split it?

## Part C: Design

**C1. Composition.** Model a `Car` that has an `Engine`. Make the engine swappable (petrol, electric) without changing `Car`.

**C2. Dependency injection.** Refactor this so it can be tested without sending real emails:
```python
class SignupService:
    def register(self, email):
        mailer = SmtpMailer()
        mailer.send(email, "Welcome!")
```

**C3. MRO.** Predict the output, then run it:
```python
class A:
    def who(self): return "A"
class B(A):
    def who(self): return "B" + super().who()
class C(A):
    def who(self): return "C" + super().who()
class D(B, C):
    def who(self): return "D" + super().who()

print(D().who())
print([c.__name__ for c in D.__mro__])
```

---

<details>
<summary>Solutions</summary>

**A1.**
```python
class Thermostat:
    def __init__(self, target=20):
        self.target = target

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, value):
        if not 10 <= value <= 30:
            raise ValueError("Target must be between 10 and 30")
        self._target = value
```

**A2.**
```python
from abc import ABC, abstractmethod

class Notifier(ABC):
    @abstractmethod
    def send(self, message): ...

class EmailNotifier(Notifier):
    def send(self, message): print(f"EMAIL: {message}")

class SmsNotifier(Notifier):
    def send(self, message): print(f"SMS: {message}")

def alert(notifier: Notifier, text):
    notifier.send(text)

# Notifier()  -> TypeError
```

**A3.**
```python
class Vehicle: ...
class Car(Vehicle): ...                  # single
class SportsCar(Car): ...                # multilevel
class Truck(Vehicle): ...                # hierarchical (Car and Truck share Vehicle)
class Floating: ...
class AmphibiousCar(Car, Floating): ...  # multiple
print(AmphibiousCar.__mro__)
```

**A4.** Each class defines `area()`; the loop is `sum(s.area() for s in shapes)`. A new `Hexagon` with its own `area()` needs no edit to the loop.

**A5.**
```python
from functools import total_ordering

@total_ordering
class Money:
    def __init__(self, amount, currency):
        self.amount, self.currency = amount, currency

    def _check(self, other):
        if self.currency != other.currency:
            raise ValueError("Currency mismatch")

    def __add__(self, other):
        self._check(other)
        return Money(self.amount + other.amount, self.currency)

    def __eq__(self, other):
        return (self.amount, self.currency) == (other.amount, other.currency)

    def __lt__(self, other):
        self._check(other)
        return self.amount < other.amount

    def __hash__(self):
        return hash((self.amount, self.currency))

    def __repr__(self):
        return f"Money({self.amount}, {self.currency!r})"
```

**B1.** The default list is created once and shared across calls, so items accumulate between calls. Use `items=None` and create a new list inside.

**B2.** `B.__init__` never calls `super().__init__()`, so `x` is never set and `B().x` raises `AttributeError`. Add `super().__init__()` at the start of `B.__init__`.

**B3.** Yes. Code that accepts a `Bird` and calls `fly()` breaks for a `Penguin`. Redesign: separate `FlyingBird` from `Bird`, or use a `Flyable` protocol.

**B4.** Single Responsibility. Split into a data fetcher, a PDF formatter, a storage uploader and a mailer, coordinated by a thin service.

**C1.**
```python
class PetrolEngine:
    def start(self): return "vroom"

class ElectricEngine:
    def start(self): return "hum"

class Car:
    def __init__(self, engine):
        self.engine = engine
    def start(self):
        return self.engine.start()
```

**C2.**
```python
class SignupService:
    def __init__(self, mailer):
        self.mailer = mailer
    def register(self, email):
        self.mailer.send(email, "Welcome!")

class FakeMailer:
    def __init__(self): self.sent = []
    def send(self, to, body): self.sent.append((to, body))
```

**C3.** Output: `DBCA`. MRO: `['D', 'B', 'C', 'A', 'object']`. Each `super()` call moves to the next class in the MRO, so `D` calls `B`, `B` calls `C` (not `A`), `C` calls `A`.

</details>
