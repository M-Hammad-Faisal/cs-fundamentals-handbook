# Encapsulation and Abstraction

## 1. The concepts

**Encapsulation** means bundling data with the code that works on it and **controlling access** so the object's internal state can only change in valid ways. The goal is to protect **invariants**: facts that must always be true (a balance never goes negative, a date range has `start <= end`).

**Abstraction** means exposing **what** something does and hiding **how**. Callers depend on a small, stable interface (`storage.save(item)`), not on the mechanism (files, SQL, S3), so the mechanism can change freely.

They are related but different:

| | Encapsulation | Abstraction |
|--|---------------|-------------|
| Question | Who may touch my state? | What must a caller know? |
| Tool | Access control, validation, properties | Interfaces, abstract classes, protocols |
| Benefit | Invariants cannot be broken from outside | Implementations can be swapped |

## 2. Access control in Python: conventions, not walls

Python has no `private` keyword. It relies on naming conventions and discipline ("we are all consenting adults").

| Spelling | Meaning | Enforced? |
|----------|---------|-----------|
| `name` | Public API | no |
| `_name` | **Internal**: not part of the public API, do not use from outside | by convention only |
| `__name` | **Name-mangled** to `_ClassName__name` to avoid clashes in subclasses | renamed, still reachable |

```python
class Account:
    def __init__(self, balance):
        self._balance = balance        # internal by convention
        self.__audit = []              # name-mangled

a = Account(100)
print(a._balance)                      # 100  (works; you were warned by the underscore)
print([n for n in vars(a)])            # ['_balance', '_Account__audit']
print(a._Account__audit)               # []   (mangling is not security)
try:
    a.__audit
except AttributeError as e:
    print("AttributeError")            # AttributeError
```

Use `__name` **only** to avoid accidental collisions with names in subclasses; for "private" intent, a single underscore is the Pythonic choice. A leading underscore on a module-level name also excludes it from `from module import *`.

## 3. Properties: controlled access that looks like an attribute

Start with a plain public attribute. If you later need validation or computation, convert it to a **property** **without changing any caller**. That is why Python code does not need Java-style getters and setters up front.

```python
class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius                 # goes through the setter: validated from the start

    @property
    def celsius(self):
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("below absolute zero")
        self._celsius = value

    @property
    def fahrenheit(self):                       # computed, read-only
        return self._celsius * 9 / 5 + 32

t = Temperature(25)
print(t.celsius, t.fahrenheit)                  # 25 77.0
t.celsius = 30
try:
    t.celsius = -300
except ValueError as e:
    print("rejected:", e)                       # rejected: below absolute zero
try:
    t.fahrenheit = 100
except AttributeError:
    print("fahrenheit is read-only")            # fahrenheit is read-only
```

Properties also support `@x.deleter`, and `functools.cached_property` computes a value once and stores it:

```python
from functools import cached_property

class Report:
    def __init__(self, rows):
        self.rows = rows
        self.computed = 0

    @cached_property
    def total(self):                            # expensive work happens once per instance
        self.computed += 1
        return sum(self.rows)

r = Report([1, 2, 3])
print(r.total, r.total, r.computed)             # 6 6 1
```

### Protecting invariants

```python
class BankAccount:
    def __init__(self, owner, opening=0):
        if opening < 0:
            raise ValueError("opening balance cannot be negative")
        self.owner = owner
        self._balance = opening
        self._history = []

    @property
    def balance(self):                          # readable, not directly assignable
        return self._balance

    @property
    def history(self):
        return tuple(self._history)             # return an immutable view, not the internal list

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("deposit must be positive")
        self._balance += amount
        self._history.append(("deposit", amount))

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("withdrawal must be positive")
        if amount > self._balance:
            raise ValueError("insufficient funds")
        self._balance -= amount
        self._history.append(("withdraw", amount))

acct = BankAccount("Ayesha", 100)
acct.deposit(50); acct.withdraw(30)
print(acct.balance, acct.history)               # 120 (('deposit', 50), ('withdraw', 30))
try:
    acct.balance = 1_000_000                    # cannot bypass the rules
except AttributeError:
    print("balance is read-only")               # balance is read-only
```

Every way of changing `_balance` goes through methods that enforce the rules, so the invariant "balance >= 0 and history matches" cannot be broken from outside.

**Defensive copying:** returning the internal list would let callers mutate your state behind your back. Return a tuple, a copy, or an immutable view; copy mutable arguments you store.

**Tell, don't ask:** prefer `account.withdraw(30)` (the object enforces rules) over `if account.balance >= 30: account.balance -= 30` (the caller duplicates the rules and can get them wrong).

**Law of Demeter:** talk to your immediate collaborators, not to their internals: `order.customer_city()` instead of `order.customer.address.city.name`. Fewer chains means fewer places break when internals change.

## 4. Descriptors: how properties really work

A **descriptor** is an object with `__get__`, `__set__` and/or `__delete__` placed as a **class attribute**. When you access `obj.attr`, Python calls the descriptor. `property`, methods, `classmethod`, `staticmethod` and `__slots__` fields are all descriptors. Writing your own lets you **reuse validation across many attributes**:

```python
class Positive:
    """Reusable validator: attribute must be a positive number."""
    def __set_name__(self, owner, name):
        self.name = "_" + name                 # called once when the class is created
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self                        # accessed on the class itself
        return getattr(obj, self.name)
    def __set__(self, obj, value):
        if value <= 0:
            raise ValueError(f"{self.name[1:]} must be positive")
        setattr(obj, self.name, value)

class Product:
    price = Positive()
    quantity = Positive()
    def __init__(self, price, quantity):
        self.price = price
        self.quantity = quantity

p = Product(9.99, 3)
print(p.price, p.quantity)                      # 9.99 3
try:
    p.quantity = 0
except ValueError as e:
    print(e)                                    # quantity must be positive
```

Descriptors power ORMs (`Django models.CharField`), dataclass fields, and validation libraries.

## 5. Abstraction: interfaces and contracts

An **interface** states what operations a thing supports without saying how. Code written against the interface works with any implementation.

### Abstract base classes (`abc`)

```python
from abc import ABC, abstractmethod

class Storage(ABC):
    """Contract: store and retrieve text by key."""

    @abstractmethod
    def save(self, key: str, value: str) -> None: ...

    @abstractmethod
    def load(self, key: str) -> str: ...

    def save_many(self, items: dict) -> None:       # shared concrete behavior built on the abstract parts
        for k, v in items.items():
            self.save(k, v)

class MemoryStorage(Storage):
    def __init__(self):
        self._d = {}
    def save(self, key, value):
        self._d[key] = value
    def load(self, key):
        return self._d[key]

try:
    Storage()                                       # cannot instantiate an incomplete abstraction
except TypeError as e:
    print("TypeError:", "abstract" in str(e))       # TypeError: True

class Broken(Storage):
    def save(self, key, value): ...                 # forgot load()
try:
    Broken()
except TypeError:
    print("missing abstract method detected at instantiation")

s = MemoryStorage()
s.save_many({"a": "1", "b": "2"})
print(s.load("b"))                                  # 2
```

An ABC gives you: **enforcement** (cannot instantiate until all abstract methods exist), **documentation** (the contract is explicit) and **shared code** (template methods like `save_many`). Abstract **properties** are declared with `@property` plus `@abstractmethod`.

### A second implementation: swapping the mechanism

```python
import sqlite3

class SqliteStorage(Storage):
    def __init__(self):
        self._db = sqlite3.connect(":memory:")
        self._db.execute("CREATE TABLE kv (k TEXT PRIMARY KEY, v TEXT)")
    def save(self, key, value):
        self._db.execute("INSERT OR REPLACE INTO kv VALUES (?, ?)", (key, value))
    def load(self, key):
        row = self._db.execute("SELECT v FROM kv WHERE k = ?", (key,)).fetchone()
        if row is None:
            raise KeyError(key)
        return row[0]

def archive(storage: Storage, data: dict):
    """Depends only on the abstraction."""
    storage.save_many(data)
    return {k: storage.load(k) for k in data}

for impl in (MemoryStorage(), SqliteStorage()):
    print(type(impl).__name__, archive(impl, {"x": "1", "y": "2"}))
# MemoryStorage {'x': '1', 'y': '2'}
# SqliteStorage {'x': '1', 'y': '2'}
```

`archive` never changes when a new backend (files, S3, Redis) appears: the essence of abstraction.

### Protocols: structural interfaces (duck typing with type checking)

With `typing.Protocol` a class conforms by **having the right methods**, no inheritance needed. Type checkers verify it statically; `runtime_checkable` allows `isinstance` checks.

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Closeable(Protocol):
    def close(self) -> None: ...

class Resource:                                     # does NOT inherit from Closeable
    def close(self):
        print("closed")

def shutdown(thing: Closeable):
    thing.close()

shutdown(Resource())                                # closed
print(isinstance(Resource(), Closeable), isinstance(object(), Closeable))   # True False
```

| Use | When |
|-----|------|
| **ABC** | You own the hierarchy, want enforcement at instantiation, or shared base code |
| **Protocol** | You want to accept third-party or unrelated types that "look right", with static checking |
| Plain duck typing | Small scripts; document the expectation |

### Levels of abstraction and leaky abstractions

Good designs have layers: `handle_request` calls `charge_customer`, which calls `gateway.charge`, which calls HTTP. Each level talks in its own vocabulary. An abstraction **leaks** when callers must know hidden details to use it correctly (an ORM that silently issues 1,000 queries, `open()` whose text mode depends on the platform locale, a "synchronous" remote call that can time out). Name leaks honestly in docs and keep abstractions small.

## 6. Two real-world examples

### Example 1: File-like objects
`open()`, `io.StringIO`, `gzip.open()`, sockets wrapped with `makefile()` and `tempfile` objects all support `read`, `write` and `close`. Functions such as `json.load(fp)` and `csv.reader(fp)` accept **any** of them. The abstraction ("something with `read()`") makes tests easy (pass a `StringIO`), enables streaming from the network, and means parsing code never needs to know where bytes come from.

### Example 2: A payment gateway interface
An e-commerce system defines `PaymentGateway` with `charge(amount, token)` and `refund(charge_id)`. Concrete classes wrap Stripe, PayPal and a `FakeGateway` for tests. Business logic (`Checkout`) receives a gateway and never imports a vendor SDK. Switching provider, adding a second one for a region, or testing without network calls is a configuration change. Encapsulation inside each gateway class hides API keys, retries and response parsing.

## 7. Tips, tricks and pitfalls

- Start with public attributes; convert to a `@property` only when you need validation or computation.
- Make invalid states **unrepresentable**: validate in `__init__` and in every mutator.
- Never return internal mutable collections; return copies or immutable views.
- Single underscore for internal names; double underscore only for avoiding subclass clashes.
- Do not build deep abstraction stacks "just in case": add an interface when there are (or clearly will be) two implementations or a testing need.
- Keep interfaces **small** (see Interface Segregation in [SOLID](../solid/README.md)).
- Do not do heavy work in a property getter; callers expect attribute-like cost. Use a method or `cached_property`.
- Prefer composition of small abstractions over a giant base class.

## 8. Check yourself

1. Define encapsulation and abstraction and how they differ.
2. What do `_x` and `__x` mean in Python? Is either truly private?
3. Why does Python code usually start with plain attributes instead of getters and setters?
4. How would you make `balance` readable but not directly assignable, while still allowing deposits?
5. What is a descriptor, and how does `property` relate to it?
6. ABC versus Protocol: when each?
7. What is defensive copying and why does it matter?
8. What does "tell, don't ask" mean?

<details>
<summary>Answers</summary>

1. Encapsulation: bundle data with behavior and control access to protect invariants. Abstraction: expose what an object does, hide how. Encapsulation is about guarding state; abstraction is about decoupling callers from implementations.
2. `_x` means "internal, not for outside use" by convention. `__x` is name-mangled to `_Class__x` to avoid subclass collisions. Neither is truly private; both remain reachable.
3. A plain attribute can later become a property with identical call syntax, so callers never need to change; upfront getters add noise without benefit.
4. Store `_balance`, expose a read-only `@property balance` (no setter), and mutate it only in methods like `deposit` and `withdraw` that enforce rules.
5. An object defining `__get__`/`__set__`/`__delete__` stored on a class; attribute access on instances triggers it. `property` is a built-in descriptor, as are functions (methods), `classmethod` and `staticmethod`.
6. ABC when you control the hierarchy and want enforcement and shared base code; Protocol when you want static, structural typing for classes that do not (or cannot) inherit from your interface.
7. Copying mutable data on the way in or out so outside code cannot mutate your internal state by holding a reference; it preserves invariants.
8. Give objects commands that they carry out and validate themselves, rather than reading their state and making decisions for them, which spreads and duplicates their rules.

</details>

[Exercises](exercises.md) · [Summary](summary.md)

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

Back to the [part overview](../README.md).
