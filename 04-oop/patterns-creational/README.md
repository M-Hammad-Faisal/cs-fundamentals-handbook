# Design Patterns I: Creational Patterns

## 1. What are design patterns?

A **design pattern** is a named, reusable solution to a commonly occurring design problem, described by its **intent**, **structure**, **trade-offs** and **when to use it**. The catalog most people mean is the 1994 "Gang of Four" (GoF) book, which defines 23 patterns in three families:

| Family | Concern | Patterns (this handbook) |
|--------|---------|--------------------------|
| **Creational** | *How objects are created* | Singleton, Factory Method, Abstract Factory, Builder, Prototype, Object Pool (this chapter) |
| **Structural** | *How objects are composed* | Adapter, Decorator, Facade, Proxy, Composite, Bridge, Flyweight ([next chapter](../patterns-structural/README.md)) |
| **Behavioral** | *How objects communicate and share responsibility* | Strategy, Observer, Command, State, Template Method, Iterator, Chain of Responsibility, Mediator, Memento, Visitor ([after that](../patterns-behavioral/README.md)) |

Patterns give you a **shared vocabulary** ("use a factory here") and proven trade-offs. They are not recipes to apply everywhere. In Python many GoF patterns **shrink or vanish** because the language has first-class functions, modules, duck typing and decorators. Use a pattern when it solves a problem you actually have; do not add one to look sophisticated.

## 2. Creational patterns: the idea

Creating objects directly with `ClassName(...)` couples your code to that exact class. Creational patterns **control and hide the creation process** so the rest of the code does not depend on which concrete class is built, how it is configured, or how many instances exist.

## 3. Singleton

**Intent:** guarantee a class has **exactly one instance** and provide a global access point.

**When:** a truly single shared resource: a configuration registry, a connection pool, a logger registry, a hardware device handle.

**The Pythonic Singleton is a module.** A module is imported once and its objects are shared:

```python
# skip
# settings.py
DEBUG = False
DATABASE_URL = "sqlite:///app.db"
# anywhere else:  import settings; settings.DEBUG
```

If you need a class-based one:

```python
import threading

class Singleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:                              # thread-safe creation
                if cls._instance is None:                # double-checked locking
                    cls._instance = super().__new__(cls)
        return cls._instance

class Config(Singleton):
    def __init__(self):
        if not hasattr(self, "values"):                  # __init__ runs on every Config() call
            self.values = {}

a, b = Config(), Config()
a.values["mode"] = "prod"
print(a is b, b.values)                                  # True {'mode': 'prod'}
```

A decorator or metaclass version:

```python
def singleton(cls):
    instances = {}
    def get(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get

@singleton
class Registry:
    def __init__(self):
        self.items = []

print(Registry() is Registry())                          # True
```

**Drawbacks (why many consider it an anti-pattern):**
- It is **global state** in disguise: hidden dependencies, hard to reason about.
- It makes **testing hard**: state leaks between tests, and you cannot substitute a fake.
- It violates **SRP** (manages its own lifecycle plus its job) and encourages tight coupling.

**Better alternative:** create **one instance at the program's edge** and **inject** it (dependency injection). You still have a single instance, but code receives it explicitly and tests can pass a different one.

## 4. Factory Method and the simple factory

**Intent:** move the decision about **which class to instantiate** into one place, so callers depend on an interface rather than concrete classes.

### Simple factory (function)

```python
import json

class JsonParser:
    def parse(self, text): return json.loads(text)
class CsvParser:
    def parse(self, text): return [line.split(",") for line in text.splitlines()]

def parser_for(filename):
    ext = filename.rsplit(".", 1)[-1]
    parsers = {"json": JsonParser, "csv": CsvParser}
    try:
        return parsers[ext]()
    except KeyError:
        raise ValueError(f"unsupported format: {ext}") from None

print(parser_for("a.json").parse('{"k": 1}'), parser_for("b.csv").parse("x,y\n1,2"))
# {'k': 1} [['x', 'y'], ['1', '2']]
```

### Factory Method (the GoF version, via subclassing)

A base class defines the algorithm and a **factory method** that subclasses override to create the right product:

```python
from abc import ABC, abstractmethod

class Dialog(ABC):
    def render(self):                                    # uses the product without knowing its class
        button = self.create_button()
        return f"Dialog[{button.draw()}]"
    @abstractmethod
    def create_button(self): ...

class WinButton:
    def draw(self): return "[Windows button]"
class WebButton:
    def draw(self): return "<button>"

class WindowsDialog(Dialog):
    def create_button(self): return WinButton()
class WebDialog(Dialog):
    def create_button(self): return WebButton()

print(WindowsDialog().render(), WebDialog().render())
# Dialog[[Windows button]] Dialog[<button>]
```

### Self-registering factory

```python
class Exporter:
    registry = {}
    def __init_subclass__(cls, fmt=None, **kw):
        super().__init_subclass__(**kw)
        if fmt:
            Exporter.registry[fmt] = cls
    @classmethod
    def create(cls, fmt):
        return cls.registry[fmt]()

class PdfExporter(Exporter, fmt="pdf"):
    def export(self, data): return f"pdf:{data}"
class XmlExporter(Exporter, fmt="xml"):
    def export(self, data): return f"xml:{data}"

print(Exporter.create("xml").export("d"))                # xml:d  (new formats register themselves; the factory is never edited)
```

**Use when** the exact type depends on input/config, or a library should let users plug in their own classes. **Python's built-ins** that act as factories: `open()` (returns different file classes), `dict.fromkeys`, `int()`/`str()`, `logging.getLogger`, `datetime.fromisoformat`.

## 5. Abstract Factory

**Intent:** create **families of related objects** that must be used together, without specifying their concrete classes.

```python
from abc import ABC, abstractmethod

class Theme(ABC):                                        # the abstract factory
    @abstractmethod
    def button(self): ...
    @abstractmethod
    def checkbox(self): ...

class LightTheme(Theme):
    def button(self): return "light-button"
    def checkbox(self): return "light-checkbox"
class DarkTheme(Theme):
    def button(self): return "dark-button"
    def checkbox(self): return "dark-checkbox"

def build_form(theme: Theme):                            # client code works with any family
    return [theme.button(), theme.checkbox()]

print(build_form(LightTheme()), build_form(DarkTheme()))
# ['light-button', 'light-checkbox'] ['dark-button', 'dark-checkbox']
```

The point is **consistency**: you cannot accidentally mix a dark button with a light checkbox, because both come from one factory. Typical uses: UI toolkits (per-platform widgets), cloud-provider SDK abstractions (`aws.storage()` + `aws.queue()` versus `gcp.storage()` + `gcp.queue()`), database drivers (connection + cursor + transaction for one vendor), test-versus-production wiring.

## 6. Builder

**Intent:** construct a **complex object step by step**, separating construction from representation. It solves "telescoping constructors" (a constructor with 12 optional parameters) and objects that must be validated as a whole before use.

```python
class Pizza:
    def __init__(self, size, crust, toppings, extra_cheese):
        self.size, self.crust, self.toppings, self.extra_cheese = size, crust, toppings, extra_cheese
    def __repr__(self):
        return f"Pizza({self.size}, {self.crust}, {self.toppings}, cheese={self.extra_cheese})"

class PizzaBuilder:
    def __init__(self):
        self._size, self._crust, self._toppings, self._cheese = "medium", "thin", [], False
    def size(self, s):
        self._size = s
        return self                                      # returning self allows a fluent chain
    def crust(self, c):
        self._crust = c
        return self
    def topping(self, t):
        self._toppings.append(t)
        return self
    def extra_cheese(self):
        self._cheese = True
        return self
    def build(self):
        if len(self._toppings) > 5:
            raise ValueError("too many toppings")        # validate the whole object once
        return Pizza(self._size, self._crust, tuple(self._toppings), self._cheese)

pizza = (PizzaBuilder().size("large").crust("thick")
         .topping("olives").topping("mushrooms").extra_cheese().build())
print(pizza)       # Pizza(large, thick, ('olives', 'mushrooms'), cheese=True)
```

In Python, keyword arguments with defaults often replace builders for simple cases (`Pizza(size="large", extra_cheese=True)`), and `dataclasses` (with `field(default_factory=...)` and `__post_init__` validation) cover most of the rest. Builders earn their place when:

- construction has **many steps or ordering rules** (an HTTP request, a SQL query, a test fixture, an email message with attachments),
- the product is **immutable** and must be assembled before it exists,
- you want a **readable fluent interface** (SQLAlchemy `select(...).where(...).order_by(...)`, `pathlib`, `requests.Request().prepare()`).

A **Director** is an optional class that knows common recipes (`margherita()`, `hawaiian()`) built from the builder.

## 7. Prototype

**Intent:** create new objects by **copying an existing one** (the prototype) instead of building from scratch. Useful when construction is expensive or the object is easier to describe by "like that one, but..."

```python
import copy

class Enemy:
    def __init__(self, kind, hp, loot):
        self.kind, self.hp, self.loot = kind, hp, loot
    def clone(self):
        return copy.deepcopy(self)                       # independent copy including nested data
    def __repr__(self):
        return f"Enemy({self.kind}, hp={self.hp}, loot={self.loot})"

goblin_template = Enemy("goblin", 30, ["coin", "dagger"])
g1 = goblin_template.clone()
g2 = goblin_template.clone()
g2.hp = 45
g2.loot.append("gem")
print(g1, g2, goblin_template, sep="\n")
# Enemy(goblin, hp=30, loot=['coin', 'dagger'])
# Enemy(goblin, hp=45, loot=['coin', 'dagger', 'gem'])
# Enemy(goblin, hp=30, loot=['coin', 'dagger'])
```

`copy.copy` gives a **shallow** copy (nested objects shared); `copy.deepcopy` copies everything; implement `__copy__`/`__deepcopy__` to control it. `dataclasses.replace(obj, field=new)` is the Pythonic "prototype with changes" for dataclass instances. Typical uses: game entities, document templates, configuration presets, cached expensive-to-build objects.

## 8. Object Pool

**Intent:** reuse a limited set of **expensive-to-create** objects (database connections, threads, large buffers) instead of creating and destroying them repeatedly.

```python
import queue
from contextlib import contextmanager

class Connection:
    count = 0
    def __init__(self):
        Connection.count += 1
        self.id = Connection.count

class Pool:
    def __init__(self, size):
        self._free = queue.Queue()
        for _ in range(size):
            self._free.put(Connection())
    @contextmanager
    def acquire(self, timeout=1):
        conn = self._free.get(timeout=timeout)           # blocks when the pool is empty
        try:
            yield conn
        finally:
            self._free.put(conn)                         # always return it

pool = Pool(2)
ids = []
for _ in range(5):
    with pool.acquire() as c:
        ids.append(c.id)
print(ids, Connection.count)                             # [1, 2, 1, 2, 1] 2  (only 2 connections ever created)
```

Real pools add health checks, maximum lifetime, and "reset on return". See SQLAlchemy's engine pool, `psycopg_pool`, `concurrent.futures.ThreadPoolExecutor`, HTTP keep-alive pools in `requests`/`urllib3`.

## 9. Choosing among creational patterns

| Need | Pattern |
|------|---------|
| Exactly one shared instance | Module-level object (best), Singleton, or inject a single instance |
| Pick the concrete class by input/config | Simple factory, registry, Factory Method |
| Create matching families of objects | Abstract Factory |
| Many optional parameters / stepwise construction / validation | Builder (or dataclass + kwargs) |
| Clone an expensive or preconfigured object | Prototype (`copy`, `dataclasses.replace`) |
| Reuse expensive resources | Object Pool |

## 10. Two real-world examples

### Example 1: A multi-database data layer
An analytics tool supports PostgreSQL, MySQL and SQLite. An **Abstract Factory** (`DbFamily`) returns a matching `Connection`, `QueryBuilder` and `Dialect` for each backend so code never mixes MySQL quoting with a PostgreSQL connection. A **registry factory** picks the family from a URL scheme (`postgres://` -> `PostgresFamily`). Connections come from an **Object Pool**. The rest of the code asks the factory for a connection and does not know the vendor.

### Example 2: Building an email message
A mail library offers `Message.builder().to("a@x.com").subject("Hi").body_html(...).attach("report.pdf").build()`. The **Builder** validates that there is at least one recipient and a subject, normalizes addresses, sets MIME boundaries and returns an immutable `Message`. Template emails (welcome, invoice) are **Prototypes**: `welcome_template.with_recipient(user)` produces a copy with fields replaced.

## 11. Tips, tricks and pitfalls

- In Python, ask first whether a **module**, a **function**, a **default argument** or a **dataclass** solves it before reaching for a class-based pattern.
- Singletons hide dependencies; prefer creating once and injecting. If you must have one, make it easy to reset in tests.
- Keep factory functions **pure and cheap** to call; put registration of new types in one clear place.
- A factory that grows a giant `if/elif` ladder is a signal to switch to a registry.
- Builders must validate in `build()`; do not return half-built objects.
- Remember `copy.deepcopy` cost and the shallow-copy sharing trap.
- Object pools must **always return** resources (use `try/finally` or a context manager) and handle timeouts.
- Name things by role (`create_x`, `build`, `from_*`, `get_*`) so readers recognize the pattern.

## 12. Check yourself

1. What are the three GoF pattern families and what does each address?
2. Why is a module often the best Singleton in Python?
3. What are the drawbacks of Singleton and what is the alternative?
4. How does Factory Method differ from Abstract Factory?
5. When would you use a Builder instead of keyword arguments?
6. What is the difference between shallow and deep copy, and why does it matter for Prototype?
7. What problem does an Object Pool solve? What must it guarantee?
8. Why does `Config()` in the double-checked-locking Singleton need a `hasattr` guard in `__init__`?
9. Give two Python standard-library examples of factories.

<details>
<summary>Answers</summary>

1. Creational (how objects are created), structural (how objects are composed), behavioral (how objects interact and divide responsibility).
2. A module is executed once and cached in `sys.modules`, so its objects are naturally shared; no special code or locking needed.
3. Hidden global state, hard-to-test code (state leaks, no substitution), tight coupling, SRP violation. Alternative: create one instance at the entry point and inject it.
4. Factory Method creates **one product** and lets subclasses decide the class by overriding a method; Abstract Factory creates **a family of related products** through several creation methods so they are used consistently.
5. When construction has many steps or optional parts, needs validation of the complete object, produces an immutable result, or benefits from a fluent API. For a handful of optional parameters, kwargs and dataclasses suffice.
6. Shallow copies share nested mutable objects; deep copies duplicate them. A prototype clone must not share mutable internals with the original unless intended.
7. It avoids repeatedly creating expensive resources by reusing a bounded set. It must guarantee resources are returned (even on exceptions), limit total size, and handle exhaustion (blocking with timeout or failing).
8. `__init__` runs on every `Config()` call even though `__new__` returns the same object, so without a guard it would reset the shared state each time.
9. `open()` (returns different I/O classes), `logging.getLogger(name)` (returns cached loggers), `datetime.fromisoformat`, `dict.fromkeys`, `Path.home()`.

</details>

[Exercises](exercises.md) · [Summary](summary.md)
