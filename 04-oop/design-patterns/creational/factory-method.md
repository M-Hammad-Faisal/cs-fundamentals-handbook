# Factory Method Pattern (and the Simple Factory)

**Family:** creational · **Also called:** virtual constructor · **How often you will use it:** very often · **Difficulty:** easy

## 1. In plain words

A **factory** is a place whose job is to **create objects for you**, so you ask for "a Red color" or "a PDF exporter" by name or by need, and do not write `Red()` or `PdfExporter()` all over your code.

Analogy: you tell a **restaurant kitchen** "one margherita"; you do not go and assemble the pizza yourself. You depend on the *menu* (an interface), not on how it is cooked.

There are three related ideas, from simplest to most formal:

| Name | What it is |
|------|-----------|
| **Simple factory** | One function (or class) with a `create(kind)` that decides which class to build. Not an official GoF pattern, but the most used. |
| **Factory Method** (GoF) | A base class has a method `create_something()` that **subclasses override** to build the right product. |
| **Registry factory** | A dictionary (often filled automatically) maps names to classes. Open for extension. |

## 2. The problem

```python
def export(data, fmt):
    if fmt == "json":
        exporter = JsonExporter()
    elif fmt == "csv":
        exporter = CsvExporter()
    elif fmt == "xml":
        exporter = XmlExporter()
    return exporter.export(data)
```

Every new format means editing this function, and the same `if/elif` ladder tends to be copied into other places.

## 3. The solution

```text
          Creator (abstract)                      Product (interface)
        + create_product()  <-- override            + operation()
        + some_logic()  (uses the product)               ^
              ^                                  ______|______
      ______|______                             |             |
     |             |                       ProductA       ProductB
 CreatorA       CreatorB
(create_product -> ProductA)  (create_product -> ProductB)
```

The code that *uses* the product (`some_logic`) never names a concrete class; only the creators do.

## 4. Step by step

### Step 1: a simple factory (function + dictionary)

```python
import json

class JsonParser:
    def parse(self, text): return json.loads(text)

class CsvParser:
    def parse(self, text): return [line.split(",") for line in text.splitlines()]

def parser_for(filename):
    parsers = {"json": JsonParser, "csv": CsvParser}
    ext = filename.rsplit(".", 1)[-1]
    try:
        return parsers[ext]()
    except KeyError:
        raise ValueError(f"unsupported format: {ext}") from None

print(parser_for("a.json").parse('{"k": 1}'), parser_for("b.csv").parse("x,y\n1,2"))
# {'k': 1} [['x', 'y'], ['1', '2']]
```

### Step 2: the GoF Factory Method (subclasses decide)

```python
from abc import ABC, abstractmethod

class Button(ABC):
    @abstractmethod
    def draw(self): ...

class WinButton(Button):
    def draw(self): return "[Windows button]"

class WebButton(Button):
    def draw(self): return "<button>"

class Dialog(ABC):
    def render(self):                              # business logic, never mentions a concrete button
        button = self.create_button()              # <- the factory method
        return f"Dialog[{button.draw()}]"

    @abstractmethod
    def create_button(self) -> Button: ...

class WindowsDialog(Dialog):
    def create_button(self): return WinButton()

class WebDialog(Dialog):
    def create_button(self): return WebButton()

print(WindowsDialog().render(), WebDialog().render())
# Dialog[[Windows button]] Dialog[<button>]
```

### Step 3: a self-registering factory (new types need no edits)

```python
class Exporter:
    registry = {}

    def __init_subclass__(cls, fmt=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if fmt:
            Exporter.registry[fmt] = cls            # every subclass registers itself

    @classmethod
    def create(cls, fmt):
        return cls.registry[fmt]()

class PdfExporter(Exporter, fmt="pdf"):
    def export(self, data): return f"pdf:{data}"

class XmlExporter(Exporter, fmt="xml"):
    def export(self, data): return f"xml:{data}"

print(Exporter.create("xml").export("d"))           # xml:d

class MdExporter(Exporter, fmt="md"):                # added later: the factory is untouched
    def export(self, data): return f"md:{data}"
print(sorted(Exporter.registry))                    # ['md', 'pdf', 'xml']
```

## 5. The Pythonic way

- **Classes are objects**, so a dict of classes *is* a factory: `{"red": Red}[name]()`.
- A **`classmethod`** is a natural factory: `datetime.fromisoformat(...)`, `dict.fromkeys(...)`, `Path.home()`. Because it receives `cls`, subclasses get their own type back.
- Functions are factories too: `make_logger(level)` returning configured objects.
- Standard-library factories: `open()` (returns different file classes), `logging.getLogger`, `int("5")`, `collections.namedtuple`.

```python
class Shape:
    @classmethod
    def from_dict(cls, data):                       # alternative constructor
        return cls(**data)

class Circle(Shape):
    def __init__(self, r): self.r = r

print(type(Circle.from_dict({"r": 2})).__name__)    # Circle (the subclass, not Shape)
```

## 6. When to use it (and when not to)

**Use it when** the exact class depends on input, configuration or environment; when you want users or plugins to add new types without editing core code; when creation logic is repeated or complex.

**Skip it when** there is only one class and no variation expected (YAGNI), or a plain constructor call is clear enough.

## 7. Pros and cons

| Pros | Cons |
|------|------|
| Callers depend on an interface, not concrete classes | More classes and indirection |
| One place to change creation logic (Open/Closed) | A simple factory with a growing `if` ladder becomes a smell: use a registry |
| Easy to add new products | The GoF form needs a parallel hierarchy of creators |
| Easier testing (return fakes) | |

## 8. Related patterns

- [Abstract Factory](abstract-factory.md): a factory of *families* (several create methods).
- [Builder](builder.md): constructs *one complex object* step by step.
- [Prototype](prototype.md): creates by cloning instead of by class.
- [Template Method](../behavioral/template-method.md): Factory Method is a template method whose varying step is creation.

## 9. Two real-world examples

**Example 1: Opening files.** `open(path, "rb")` returns a `BufferedReader`; `open(path, "r")` returns a `TextIOWrapper`; the code you write after it uses `read()` either way. Python hides which class was built.

**Example 2: Payment providers.** A checkout asks `PaymentFactory.create(country)` and gets a `StripeGateway` for most countries or a `LocalBankGateway` for one market. The checkout code only calls `gateway.charge(amount)`. Adding a new provider means adding one class and one registry line.

## 10. Common mistakes

- Returning different *kinds* of objects that do not share an interface (callers need `isinstance` checks again).
- A factory that knows too much (it should only create).
- Giant `if/elif` ladders that never get refactored into a registry.
- Using `globals()[name]()` for lookup (as in quick demos): it is fragile and unsafe with user input; use an explicit dictionary.

## 11. Practice

1. Write `shape_from_dict({"type": "circle", "r": 2})` using a registry decorator `@register("circle")`.
2. Create a factory returning different `Notifier` objects (`email`, `sms`) and raising a helpful error for unknown names.
3. Rewrite `export(data, fmt)` from section 2 using the registry factory.

<details>
<summary>Solutions</summary>

**1.**
```python
import math
SHAPES = {}
def register(name):
    def deco(cls):
        SHAPES[name] = cls
        return cls
    return deco

@register("circle")
class Circle2:
    def __init__(self, r): self.r = r
    def area(self): return math.pi * self.r ** 2

@register("rect")
class Rect2:
    def __init__(self, w, h): self.w, self.h = w, h
    def area(self): return self.w * self.h

def shape_from_dict(d):
    d = dict(d)
    return SHAPES[d.pop("type")](**d)

print(round(shape_from_dict({"type": "circle", "r": 2}).area(), 2), shape_from_dict({"type": "rect", "w": 2, "h": 3}).area())
# 12.57 6
```

**2.**
```python
class EmailNotifier:
    def send(self, to, msg): return f"email {to}: {msg}"
class SmsNotifier:
    def send(self, to, msg): return f"sms {to}: {msg}"
def notifier(kind):
    kinds = {"email": EmailNotifier, "sms": SmsNotifier}
    if kind not in kinds:
        raise ValueError(f"unknown notifier {kind!r}; choose from {sorted(kinds)}")
    return kinds[kind]()
print(notifier("sms").send("a", "hi"))
try:
    notifier("fax")
except ValueError as e:
    print(e)
```

**3.**
```python
def export(data, fmt):
    return Exporter.create(fmt).export(data)       # no if/elif ladder
print(export("x", "pdf"))                          # pdf:x
```

</details>

## 12. Check yourself

1. What is the difference between a simple factory and the GoF Factory Method?
2. Why is a `classmethod` a good factory in Python?
3. What smell tells you a simple factory should become a registry?
4. How does a self-registering factory support the Open/Closed Principle?
5. Name two Python standard-library factories.

<details>
<summary>Answers</summary>

1. A simple factory is one function or class with a `create(kind)` that chooses a class. Factory Method is a method on a base class that **subclasses override** to decide which product to create.
2. It receives `cls`, so subclasses called through it create instances of the subclass, and it gives a readable alternative constructor name.
3. A growing `if/elif` ladder that is edited for every new type.
4. New types register themselves (for example in `__init_subclass__`), so the factory code never changes when types are added.
5. `open()`, `logging.getLogger()`, `datetime.fromisoformat()`, `dict.fromkeys()`, `Path.home()`.

</details>

## More examples

Runnable script from your companion repository: [`creationalPattern/factoryPattern.py`](https://github.com/M-Hammad-Faisal/design-patterns-python/blob/master/creationalPattern/factoryPattern.py)

[Family overview](README.md) · [All patterns](../README.md)
