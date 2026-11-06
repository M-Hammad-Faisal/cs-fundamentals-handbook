# Object-Oriented Programming: Principles, Inheritance and SOLID

## 1. The concept

**Object-oriented programming (OOP)** organizes software around *objects*: bundles of **data** (attributes) and **behavior** (methods) that model things in the problem domain. A **class** is the blueprint; an **object** (instance) is one concrete thing built from it.

```python
class BankAccount:                       # class: the blueprint
    def __init__(self, owner, balance=0):
        self.owner = owner               # data
        self.balance = balance

    def deposit(self, amount):           # behavior
        self.balance += amount

acct = BankAccount("Ayesha", 500)        # object: an instance
acct.deposit(250)
```

Why OOP exists: as programs grow, you need ways to manage complexity, reuse code, and change one part without breaking the rest. The four pillars below are the tools for that.

## 2. The four pillars

### 2.1 Encapsulation

**Bundle data with the methods that operate on it, and control access to the internals.** Callers use a small public interface and cannot corrupt the object's state.

Python has no hard `private`. It uses conventions:

| Syntax | Meaning |
|--------|---------|
| `name` | Public |
| `_name` | "Internal, please don't touch" (convention only) |
| `__name` | Name-mangled to `_ClassName__name` to avoid subclass clashes (not true privacy) |

```python
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self._balance = balance                 # internal state

    @property
    def balance(self):                          # read-only view
        return self._balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit must be positive")
        self._balance += amount

    def withdraw(self, amount):
        if amount > self._balance:
            raise ValueError("Insufficient funds")
        self._balance -= amount
```

Because every change goes through `deposit` and `withdraw`, the invariant "balance never goes negative" is enforced in one place.

**Real-world example 1: a payment gateway SDK.** You call `client.charge(card, amount)`. You never see how it signs requests, retries, or parses responses. The vendor can rewrite the internals without breaking your code.

**Real-world example 2: a car.** You use the steering wheel and pedals. The engine's fuel injection logic is hidden. You cannot set "fuel mix" directly, which prevents you from wrecking the engine.

### 2.2 Abstraction

**Expose *what* something does, hide *how* it does it.** Abstraction is about choosing the right level of detail. Encapsulation hides data; abstraction hides complexity.

In Python, abstract base classes (`abc`) let you define a contract that subclasses must fulfil:

```python
from abc import ABC, abstractmethod

class PaymentMethod(ABC):
    @abstractmethod
    def pay(self, amount: float) -> str: ...

class CreditCard(PaymentMethod):
    def pay(self, amount):
        return f"Charged {amount} to card"

class JazzCash(PaymentMethod):
    def pay(self, amount):
        return f"Paid {amount} via JazzCash"

def checkout(method: PaymentMethod, total):
    return method.pay(total)         # works with any PaymentMethod

# PaymentMethod()  -> TypeError: can't instantiate abstract class
```

`checkout` depends on the abstraction, not on any concrete payment type. Adding a new method (EasyPaisa) requires no change to `checkout`.

**Real-world example 1: file I/O.** `open()` gives you `read()` and `write()`. Whether the bytes live on an SSD, a network share, or in memory (`io.StringIO`), your code is the same.

**Real-world example 2: a database driver (DB-API).** You call `cursor.execute(sql)`. PostgreSQL, SQLite and MySQL drivers implement the same interface, so you can swap databases with few code changes.

### 2.3 Inheritance

**A class (child) reuses and extends another class (parent).** It models an "is-a" relationship: a `Dog` *is an* `Animal`.

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return "..."

class Dog(Animal):                      # Dog inherits from Animal
    def speak(self):                    # overrides parent behavior
        return f"{self.name} says Woof"

class Cat(Animal):
    def speak(self):
        return f"{self.name} says Meow"
```

`super()` calls the parent's version:

```python
class Puppy(Dog):
    def __init__(self, name, age_months):
        super().__init__(name)          # run Dog/Animal's init
        self.age_months = age_months
```

#### The types of inheritance

| Type | Shape | Example |
|------|-------|---------|
| **Single** | One parent, one child | `Dog(Animal)` |
| **Multilevel** | Chain: grandparent → parent → child | `Puppy(Dog(Animal))` |
| **Hierarchical** | One parent, many children | `Dog(Animal)`, `Cat(Animal)`, `Bird(Animal)` |
| **Multiple** | One child, several parents | `class FlyingFish(Fish, Bird)` |
| **Hybrid** | A mix of the above (often a diamond) | `D(B, C)` where `B(A)` and `C(A)` |

```python
# Multiple inheritance
class Flyer:
    def move(self): return "flies"

class Swimmer:
    def move(self): return "swims"

class Duck(Flyer, Swimmer):
    pass

Duck().move()        # "flies": Flyer comes first in the MRO
```

#### The diamond problem and the MRO

With multiple inheritance, what if two parents both inherit from the same grandparent? Which version of a method wins?

```python
class A:
    def hello(self): return "A"

class B(A):
    def hello(self): return "B"

class C(A):
    def hello(self): return "C"

class D(B, C):
    pass

D().hello()                  # "B"
print(D.__mro__)             # D -> B -> C -> A -> object
```

Python resolves this with the **C3 linearization**, called the **Method Resolution Order (MRO)**. Rules: children come before parents, and the order in which you list the parents is respected. Inspect it with `ClassName.__mro__` or `ClassName.mro()`.

`super()` follows the MRO, not just "the parent". In a cooperative hierarchy, each class calls `super().method()` and every class in the chain runs exactly once.

**Real-world example 1: a UI toolkit.** `Widget` → `Button`, `Checkbox`, `TextInput` (hierarchical). `Button` provides click handling, and `ImageButton(Button)` adds an icon (multilevel).

**Real-world example 2: Django class-based views.** `class ArticleList(LoginRequiredMixin, ListView)` is multiple inheritance. `LoginRequiredMixin` adds authentication, `ListView` adds listing, and the MRO decides the order they run.

#### Mixins

A **mixin** is a small class that adds one capability and is not meant to be used alone. It is a disciplined use of multiple inheritance.

```python
class JsonMixin:
    def to_json(self):
        import json
        return json.dumps(self.__dict__)

class User(JsonMixin):
    def __init__(self, name):
        self.name = name

User("Sara").to_json()       # '{"name": "Sara"}'
```

#### Composition over inheritance

**Composition** is a "has-a" relationship: build objects out of other objects. Prefer it when the relationship is not truly "is-a".

```python
# Inheritance (brittle): a Stack "is-a" list?  It also exposes insert(), sort()...
class StackBad(list):
    ...

# Composition (clean): a Stack "has-a" list and exposes only what it should
class Stack:
    def __init__(self):
        self._items = []
    def push(self, x): self._items.append(x)
    def pop(self): return self._items.pop()
    def __len__(self): return len(self._items)
```

Deep inheritance trees are hard to read and change. A change in a base class ripples through every descendant (the "fragile base class" problem). Composition keeps components independent and swappable.

> **Rule of thumb:** use inheritance for a genuine "is-a" with shared behavior and substitutability. Use composition for "has-a" or "uses-a", and when you want to swap behavior at runtime.

### 2.4 Polymorphism

**"Many forms": one interface, different behavior depending on the object.** You call the same method on different types and each responds in its own way.

```python
animals = [Dog("Rex"), Cat("Tom"), Animal("Generic")]
for a in animals:
    print(a.speak())          # each class supplies its own speak()
```

Kinds of polymorphism:

| Kind | Meaning | Python |
|------|---------|--------|
| **Subtype (overriding)** | Child replaces a parent method | `Dog.speak` |
| **Duck typing** | "If it quacks like a duck": no shared base needed | Any object with `.read()` works as a file |
| **Operator overloading** | Custom behavior for `+`, `==`, `len()` | `__add__`, `__eq__`, `__len__` |
| **Overloading (by signature)** | Same name, different parameters | Not built in; use default args or `functools.singledispatch` |
| **Parametric (generics)** | Same code for many types | `list[int]`, `TypeVar` |

```python
class Vector:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __add__(self, other):                 # operator overloading
        return Vector(self.x + other.x, self.y + other.y)

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"

Vector(1, 2) + Vector(3, 4)                   # Vector(4, 6)
```

Duck typing with `typing.Protocol` gives static checkers a way to verify structure without inheritance:

```python
from typing import Protocol

class Closeable(Protocol):
    def close(self) -> None: ...

def shutdown(resource: Closeable):
    resource.close()          # any object with close() qualifies
```

**Real-world example 1: logging handlers.** A logger calls `handler.emit(record)`. A `FileHandler`, `StreamHandler` and `SMTPHandler` each implement `emit` differently. The logger does not care which it holds.

**Real-world example 2: a drawing app.** `shape.draw()` is called on a list of `Circle`, `Rectangle` and `Triangle` objects. Each draws itself. Adding `Hexagon` needs no edit to the rendering loop.

## 3. Types of classes and methods in Python

| Kind | Purpose | Notes |
|------|---------|-------|
| **Concrete class** | Normal, instantiable class | Most classes |
| **Abstract class** | Defines a contract; cannot be instantiated | `ABC` + `@abstractmethod` |
| **Interface (Protocol)** | Pure structural contract | `typing.Protocol` |
| **Mixin** | Adds one reusable capability | Not used alone |
| **Dataclass** | Class mostly for holding data | `@dataclass` generates `__init__`, `__repr__`, `__eq__` |
| **Singleton** | Exactly one instance | Often a module-level object in Python |
| **Metaclass** | A class whose instances are classes | Advanced; used by ORMs and frameworks |

Method kinds:

```python
class Temperature:
    scale = "C"                                # class attribute (shared)

    def __init__(self, degrees):
        self.degrees = degrees                 # instance attribute (per object)

    def to_f(self):                            # instance method: gets self
        return self.degrees * 9 / 5 + 32

    @classmethod
    def from_fahrenheit(cls, f):               # class method: gets cls; alt constructor
        return cls((f - 32) * 5 / 9)

    @staticmethod
    def is_valid(degrees):                     # static method: no self/cls
        return degrees >= -273.15

    @property
    def kelvin(self):                          # computed attribute
        return self.degrees + 273.15
```

- Use `@classmethod` for **alternative constructors** and factory methods.
- Use `@staticmethod` for a function that logically belongs to the class but needs no instance or class data.
- Use `@property` to expose computed or validated values as attributes.

### Dunder (magic) methods worth knowing

| Method | Triggered by |
|--------|--------------|
| `__init__` | Object creation (initializer) |
| `__repr__` / `__str__` | `repr(obj)` (debugging) / `str(obj)`, `print` (display) |
| `__eq__`, `__lt__`, ... | Comparison operators |
| `__hash__` | `hash(obj)`; needed to use as a dict key or set member |
| `__len__`, `__getitem__`, `__iter__` | `len()`, indexing, iteration |
| `__enter__` / `__exit__` | `with` statements |
| `__call__` | Calling the object like a function |

> If you define `__eq__` without `__hash__`, Python sets `__hash__` to `None` and the object becomes unhashable.

## 4. SOLID principles

Five design guidelines for maintainable object-oriented code.

### S: Single Responsibility Principle

**A class should have one reason to change.**

```python
# Violates SRP: one class parses, saves, and emails
class ReportBad:
    def generate(self): ...
    def save_to_db(self): ...
    def email_to_boss(self): ...

# Follows SRP: each class does one job
class ReportGenerator:
    def generate(self): ...
class ReportRepository:
    def save(self, report): ...
class ReportMailer:
    def send(self, report): ...
```

*Real world:* a Django app keeps models (data), views (request handling), and serializers (formatting) separate so a change to the API format does not touch database code.

### O: Open/Closed Principle

**Open for extension, closed for modification.** Add new behavior by adding code, not by editing tested code.

```python
# Violates OCP: every new shape forces an edit
def area(shape):
    if shape.kind == "circle": ...
    elif shape.kind == "square": ...

# Follows OCP: add a class, change nothing else
class Shape(ABC):
    @abstractmethod
    def area(self): ...

class Circle(Shape):
    def __init__(self, r): self.r = r
    def area(self): return 3.14159 * self.r ** 2

class Square(Shape):
    def __init__(self, s): self.s = s
    def area(self): return self.s ** 2

def total_area(shapes):
    return sum(s.area() for s in shapes)
```

*Real world:* a plugin system (pytest plugins, browser extensions) extends the core without modifying it.

### L: Liskov Substitution Principle

**Subclasses must be usable anywhere the parent is expected, without surprising behavior.**

The classic violation:

```python
class Rectangle:
    def __init__(self, w, h): self.w, self.h = w, h
    def set_width(self, w): self.w = w
    def area(self): return self.w * self.h

class Square(Rectangle):                # a square "is-a" rectangle... or is it?
    def set_width(self, w):
        self.w = self.h = w             # surprises callers who expect height unchanged
```

Code that sets width to 5 on a `Rectangle` expecting area `5 * h` breaks when handed a `Square`. The inheritance looked natural but the *behavioral contract* differs. Fix by not inheriting, or by using immutable shapes or a shared abstraction.

Signs of an LSP violation: a subclass raises `NotImplementedError` for an inherited method, tightens input requirements, or weakens guarantees.

*Real world:* if `ReadOnlyFile` inherits from `File` and its `write()` raises an error, any function that accepts a `File` and writes will crash when given a `ReadOnlyFile`.

### I: Interface Segregation Principle

**Do not force classes to depend on methods they do not use.** Prefer several small interfaces to one big one.

```python
# Fat interface: a robot cannot eat
class Worker(ABC):
    @abstractmethod
    def work(self): ...
    @abstractmethod
    def eat(self): ...

# Segregated
class Workable(Protocol):
    def work(self): ...
class Eatable(Protocol):
    def eat(self): ...
```

*Real world:* Python's `collections.abc` splits behavior into `Iterable`, `Sized`, `Container`, `Mapping`, and so on, so you implement only what your type supports.

### D: Dependency Inversion Principle

**High-level code should depend on abstractions, not on concrete low-level details.** Pass dependencies in rather than creating them inside.

```python
# Tight coupling: hard to test, hard to swap
class OrderService:
    def __init__(self):
        self.mailer = SmtpMailer()          # hard-wired

# Dependency injection
class OrderService:
    def __init__(self, mailer: Mailer):     # depends on an abstraction
        self.mailer = mailer

# In production: OrderService(SmtpMailer())
# In tests:      OrderService(FakeMailer())
```

*Real world:* injecting a fake clock or fake payment client lets you test checkout logic without calling real services or waiting for real time.

## 5. Coupling and cohesion

- **Cohesion:** how closely related the things inside one class or module are. Aim for **high** cohesion (a class does one coherent thing).
- **Coupling:** how much one module depends on another's internals. Aim for **low** coupling (modules interact through small, stable interfaces).

High cohesion plus low coupling is the practical goal behind all the principles above.

## 6. Common design patterns (a quick map)

| Pattern | Problem it solves | Python flavor |
|---------|-------------------|---------------|
| **Factory** | Create objects without hard-coding the class | A function or `@classmethod` returning instances |
| **Singleton** | Exactly one shared instance | A module-level object |
| **Strategy** | Swap an algorithm at runtime | Pass a function or object |
| **Observer** | Notify many listeners of a change | Callback lists, signals (Django signals) |
| **Decorator** | Add behavior around an object or function | `@decorator` syntax |
| **Adapter** | Make an incompatible interface fit | A wrapper class |
| **Builder** | Construct complex objects step by step | Method chaining, keyword args |
| **Repository** | Hide data-storage details behind an interface | A class wrapping the ORM |

Strategy in Python is often just passing a function:

```python
def sort_by(items, key_fn):
    return sorted(items, key=key_fn)

sort_by(users, key_fn=lambda u: u.age)
```

## 7. Tips, tricks and pitfalls

- **Favor composition over inheritance.** Reach for inheritance only for a real "is-a" with substitutability.
- **Keep hierarchies shallow.** More than two or three levels is a smell.
- **Always call `super().__init__()`** in subclasses that override `__init__`, or the parent never initializes.
- **Never use a mutable default argument:** `def f(items=[])` shares one list across all calls. Use `items=None` and create inside.
- **Class attributes are shared.** Mutating a list stored as a class attribute affects every instance.
- **Define `__repr__` early.** It makes debugging and logs readable.
- **`@dataclass`** removes boilerplate for data-holder classes; add `frozen=True` for immutability and `slots=True` for lower memory.
- **Do not over-abstract.** Introduce an interface when you have two or more real implementations or a concrete testing need, not "just in case".
- **Python favors duck typing.** Do not add `isinstance` checks everywhere; trust the interface and handle errors when they occur.
- **Interview framing:** explain each pillar with a one-line definition, a tiny code example, and a real-world analogy.

## 8. Check yourself

1. How do encapsulation and abstraction differ?
2. Name the five types of inheritance and give a one-line example of each.
3. What is the diamond problem and how does Python's MRO solve it?
4. When would you choose composition over inheritance?
5. What is the difference between `@classmethod`, `@staticmethod` and an instance method?
6. Explain duck typing and how `typing.Protocol` relates to it.
7. Which SOLID principle does the Rectangle/Square example violate and why?
8. Why does defining `__eq__` make a class unhashable unless you also define `__hash__`?
9. Show how dependency injection makes a service easier to test.

<details>
<summary>Answers</summary>

1. Encapsulation hides *data* and controls access to it; abstraction hides *complexity* behind a simpler interface.
2. Single (`Dog(Animal)`), multilevel (`Puppy(Dog)`), hierarchical (`Dog` and `Cat` both from `Animal`), multiple (`Duck(Flyer, Swimmer)`), hybrid (a diamond such as `D(B, C)` where both extend `A`).
3. A class inheriting from two parents that share an ancestor could get that ancestor's method ambiguously. Python linearizes the hierarchy with C3 so each class appears once, children before parents, respecting the declared base order. `super()` follows this order.
4. When the relationship is "has-a" rather than "is-a", when you want to expose only part of another class's interface, or when you need to swap behavior at runtime.
5. An instance method receives the instance (`self`); a class method receives the class (`cls`) and is used for alternative constructors; a static method receives neither and is a namespaced utility function.
6. Duck typing means an object is acceptable if it has the needed methods, regardless of its class. `Protocol` lets static type checkers verify that structure without requiring inheritance.
7. Liskov Substitution: a `Square` cannot honor `Rectangle`'s contract that width and height change independently, so substituting it breaks callers.
8. Python assumes objects that compare equal must hash equal, so setting `__eq__` alone sets `__hash__ = None` to avoid inconsistent hashing. Define both (consistently) to use the object in sets and as dict keys.
9. The service takes its collaborators (mailer, clock, database) as constructor arguments. Tests pass fakes, so no real emails are sent and no real time passes.

</details>
