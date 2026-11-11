# Classes and Objects in Depth

## 1. The concept

**Object-oriented programming (OOP)** organizes a program as a set of **objects**: bundles of **state** (data) and **behavior** (functions that work on that data). A **class** is the blueprint; an **object** (instance) is one thing built from it.

In Python this goes further than in most languages: **everything is an object**, including integers, functions, modules and classes themselves. Every object has three things:

| Property | Meaning | How to see it |
|----------|---------|---------------|
| **Identity** | Who it is (unique while alive) | `id(obj)`, compared with `is` |
| **Type** | What kind of thing it is | `type(obj)` |
| **Value** | What it contains | compared with `==` |

```python
a = [1, 2, 3]
b = a                 # b is another NAME for the same object
c = [1, 2, 3]         # c is a different object with an equal value
print(a is b, a == c, a is c)       # True True False
b.append(4)
print(a)                            # [1, 2, 3, 4]   (a and b are the same list)
print(type(a), type(type(a)))       # <class 'list'> <class 'type'>
```

**Variables are names bound to objects, not boxes holding values.** Assignment never copies; it attaches another name. This single idea explains most "weird" Python behavior (shared defaults, aliasing, `is` vs `==`).

Use `is` only for singletons (`None`, `True`); use `==` for value comparison.

## 2. Defining a class

```python
class BankAccount:
    """A simple account. Demonstrates the main parts of a class."""

    bank_name = "Python Bank"          # class attribute: shared by every instance
    _count = 0                         # class-level counter (convention: leading underscore = internal)

    def __init__(self, owner, balance=0):
        self.owner = owner             # instance attributes: one copy per object
        self.balance = balance
        BankAccount._count += 1

    def deposit(self, amount):         # instance method: receives the object as `self`
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.balance += amount
        return self.balance

    @classmethod
    def from_string(cls, text):        # class method: receives the class, builds instances
        owner, balance = text.split(":")
        return cls(owner, int(balance))

    @staticmethod
    def is_valid_amount(amount):       # static method: no self, no cls; a plain function in the class namespace
        return amount > 0

    @classmethod
    def count(cls):
        return cls._count

    def __repr__(self):
        return f"BankAccount(owner={self.owner!r}, balance={self.balance})"


acct = BankAccount("Ayesha", 100)
acct.deposit(50)
print(acct)                                 # BankAccount(owner='Ayesha', balance=150)
print(BankAccount.from_string("Bilal:70"))  # BankAccount(owner='Bilal', balance=70)
print(BankAccount.is_valid_amount(-5))      # False
print(BankAccount.count())                  # 2
```

### The three kinds of methods

| Kind | Decorator | First parameter | Use |
|------|-----------|-----------------|-----|
| **Instance method** | none | `self` (the object) | Work with one object's state |
| **Class method** | `@classmethod` | `cls` (the class) | Alternative constructors, class-level state; works correctly with subclasses |
| **Static method** | `@staticmethod` | none | A utility that belongs logically to the class but needs neither object nor class |

`obj.method(x)` is just sugar for `Class.method(obj, x)`: Python passes the object as `self` automatically. That is why `self` is explicit in the signature.

### Class attributes versus instance attributes

Lookup order for `obj.name`: the **instance** `__dict__`, then the **class**, then its base classes. Assigning through an instance (`obj.name = ...`) always creates or changes an **instance** attribute and never modifies the class attribute.

```python
class Config:
    retries = 3                 # class attribute
    options = []                # DANGER: a mutable class attribute is shared by everyone

a, b = Config(), Config()
a.retries = 10                  # creates an instance attribute on a only
print(Config.retries, a.retries, b.retries)    # 3 10 3

a.options.append("x")           # mutates the ONE shared list
print(b.options)                # ['x']  (surprise!)
```

Put per-object mutable state in `__init__` (`self.options = []`), never at class level.

## 3. The object lifecycle

1. `__new__(cls, ...)` **creates** the empty object (rarely overridden; needed for immutable types and singletons).
2. `__init__(self, ...)` **initializes** it.
3. The object lives while at least one name or container references it. CPython uses **reference counting** and frees an object the moment its count hits zero, plus a **cyclic garbage collector** for reference cycles.
4. `__del__` is a finalizer: unreliable timing and never the right place to release resources. Use `with` and `try/finally` instead.

```python
import gc, weakref

class Node:
    def __init__(self, name):
        self.name = name
        self.peer = None

a, b = Node("a"), Node("b")
a.peer, b.peer = b, a            # a reference cycle: counts never reach zero by themselves
probe = weakref.ref(a)           # a weak reference does not keep its target alive
del a, b
print(probe() is not None)       # True: the cycle keeps both alive
gc.collect()                     # the cycle collector finds and frees them
print(probe() is None)           # True
```

`weakref` is the tool for caches and observers that must not keep objects alive.

## 4. Where attributes live: `__dict__` and `__slots__`

By default each instance stores its attributes in a dict (`obj.__dict__`), which makes Python flexible (add attributes at any time) but uses memory.

```python
class P:
    def __init__(self, x, y):
        self.x, self.y = x, y

p = P(1, 2)
print(p.__dict__)                # {'x': 1, 'y': 2}
p.z = 3                          # adding attributes on the fly is allowed
print(sorted(vars(p)))           # ['x', 'y', 'z']
```

`__slots__` replaces the per-instance dict with a fixed set of fields:

```python
import sys

class PlainPoint:
    def __init__(self, x, y):
        self.x, self.y = x, y

class SlotPoint:
    __slots__ = ("x", "y")
    def __init__(self, x, y):
        self.x, self.y = x, y

pp, sp = PlainPoint(1, 2), SlotPoint(1, 2)
plain = sys.getsizeof(pp) + sys.getsizeof(pp.__dict__)
slots = sys.getsizeof(sp)
print(slots < plain)             # True: noticeably smaller per instance
try:
    sp.z = 3
except AttributeError as e:
    print("blocked:", type(e).__name__)      # blocked: AttributeError
```

Use slots when you create **millions** of small objects; accept the trade-offs (no dynamic attributes, awkward with multiple inheritance, no `__weakref__` unless you add it).

### Dynamic attribute access

| Hook | Called when |
|------|-------------|
| `__getattribute__(self, name)` | on **every** attribute read (rarely overridden) |
| `__getattr__(self, name)` | only when normal lookup **fails** (proxies, lazy attributes) |
| `__setattr__(self, name, value)` | on every assignment |
| `__delattr__(self, name)` | on `del obj.name` |

Built-ins: `getattr(obj, "name", default)`, `setattr`, `hasattr`, `delattr`, `dir(obj)`, `vars(obj)`.

```python
class Settings:
    def __init__(self, **kw):
        self._data = dict(kw)
    def __getattr__(self, name):                  # called only for missing attributes
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError(name) from None

s = Settings(host="localhost", port=8080)
print(s.host, s.port)            # localhost 8080
print(getattr(s, "debug", False))    # False
```

## 5. Identity, equality, hashing and copying

Defining your own `==` means you should think about `hash` too:

- If a class defines `__eq__` and not `__hash__`, Python sets `__hash__` to `None`: instances become **unhashable** (cannot be dict keys or set members).
- Objects that compare equal **must** have equal hashes.
- Only make objects hashable if they are effectively **immutable**; mutating a key breaks the dict.

```python
class Money:
    def __init__(self, amount, currency):
        self.amount, self.currency = amount, currency
    def __eq__(self, other):
        if not isinstance(other, Money):
            return NotImplemented            # let Python try the other side / fall back
        return (self.amount, self.currency) == (other.amount, other.currency)
    def __hash__(self):
        return hash((self.amount, self.currency))
    def __repr__(self):
        return f"Money({self.amount}, {self.currency!r})"

prices = {Money(5, "USD"): "coffee"}
print(prices[Money(5, "USD")])                   # coffee
print(Money(5, "USD") == Money(5, "EUR"))        # False
print(Money(5, "USD") == 5)                      # False (NotImplemented on both sides)
```

### Shallow and deep copy

```python
import copy

original = {"name": "ana", "tags": ["a", "b"]}
shallow = copy.copy(original)          # new dict, SAME inner list
deep = copy.deepcopy(original)         # new dict AND new inner list
original["tags"].append("c")
print(shallow["tags"], deep["tags"])   # ['a', 'b', 'c'] ['a', 'b']
```

### `__repr__` versus `__str__`

- `__repr__`: for **developers**; unambiguous, ideally looks like code that recreates the object. Always define it.
- `__str__`: for **users**; friendly text used by `print` and `str()`. Falls back to `__repr__`.

## 6. Two real-world examples

### Example 1: A `Money` value object in a billing system
Floating-point numbers and bare integers lose the currency and invite bugs (adding dollars to euros). A small immutable class holding `amount` and `currency`, with `__eq__`, `__hash__`, `__add__` (rejecting mismatched currencies) and `__repr__`, makes invalid operations impossible and valid ones readable. The pattern (a **value object**) appears for dates, coordinates, IDs and measurements. Python's `decimal.Decimal`, `datetime` and `pathlib.Path` are all value objects.

### Example 2: Per-connection state with a class method constructor
A database client class keeps a `host`, `port` and open socket per instance, a class attribute for the default port, and a `from_url("postgres://u:p@h:5432/db")` class method that parses and builds the instance. Because it is a `classmethod`, a subclass `SecureClient.from_url(...)` returns a `SecureClient`, not the base class, which a hard-coded constructor call would break. This is the standard shape of alternative constructors in the standard library (`dict.fromkeys`, `datetime.fromtimestamp`, `Path.home`).

## 7. Tips, tricks and pitfalls

- Never use a **mutable default argument** (`def f(items=[])`): the default is created once at definition time and shared. Use `None` and create the list inside.
- Never put per-instance mutable state at class level.
- Prefer `is None` / `is not None` for None checks; use `==` for values.
- Define `__repr__` for every class; it saves hours of debugging.
- Do not rely on `__del__`; use context managers (`with`) for resources.
- If you define `__eq__`, decide whether the class is hashable (immutable) or not.
- Use `@classmethod` rather than hard-coding the class name for alternative constructors, so subclasses work.
- Compare floats with `math.isclose`, money with `Decimal` or integer cents.
- Use `__slots__` only when profiling shows object count matters.

## 8. Check yourself

1. What are identity, type and value, and which operators/functions inspect each?
2. Why does `b = a; b.append(1)` change `a`? How do you get an independent copy?
3. What are the differences between instance, class and static methods?
4. What happens if you assign `obj.x = 5` and `x` is also a class attribute?
5. Why is a mutable class attribute dangerous?
6. What is wrong with defining `__eq__` but not `__hash__`?
7. What does `__slots__` do and what does it cost?
8. `__repr__` versus `__str__`?
9. What does `__getattr__` do differently from `__getattribute__`?

<details>
<summary>Answers</summary>

1. Identity (`id`, `is`), type (`type`, `isinstance`), value (`==`).
2. Both names refer to the same list; assignment never copies. Use `list(a)`, `a.copy()`, `a[:]` for a shallow copy, `copy.deepcopy(a)` for nested structures.
3. Instance methods get the object (`self`) and use its state; class methods get the class (`cls`) and suit alternative constructors; static methods get neither and are plain functions namespaced in the class.
4. It creates an instance attribute that shadows the class attribute for that object only; the class attribute and other instances are unchanged.
5. All instances share the same object, so one instance's mutation shows up in all of them.
6. Python sets `__hash__ = None`, making instances unhashable, so they cannot be used in sets or as dict keys. (And if you do define both, equal objects must have equal hashes.)
7. It removes the per-instance `__dict__`, saving memory and preventing arbitrary new attributes. Cost: no dynamic attributes, more care with inheritance, and no weak references unless `__weakref__` is listed.
8. `__repr__` is the unambiguous developer representation (used in the REPL, logs, containers); `__str__` is the readable user-facing text and defaults to `__repr__`.
9. `__getattribute__` runs on every attribute access; `__getattr__` runs only when normal lookup fails, which makes it safe for proxies and lazy defaults.

</details>

[Exercises](exercises.md) · [Summary](summary.md)

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

Back to the [part overview](../README.md).
