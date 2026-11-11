# Inheritance, Method Resolution Order and Multiple Inheritance

## 1. The concept

**Inheritance** lets a new class (the **subclass**, **child** or **derived** class) reuse and specialize another class (the **superclass**, **parent** or **base** class). It models an **is-a** relationship: a `SavingsAccount` *is an* `Account`.

What a subclass gets for free: all attributes and methods of the parent. What it can do:

- **Extend:** add new attributes and methods.
- **Override:** replace an inherited method with its own version.
- **Extend and reuse:** override but call the parent's version with `super()`.

Inheritance serves two distinct purposes that are worth keeping apart:

| Purpose | Meaning | Example |
|---------|---------|---------|
| **Subtyping** | A `Dog` can be used wherever an `Animal` is expected (polymorphism) | `animals: list[Animal]` |
| **Code reuse** | Borrow implementation from a base class | A `Stack` reusing `list` internals |

Subtyping is the strong, valuable use. Pure code reuse is often better done with **composition** (see [composition](../composition-design/README.md)).

## 2. The basics

```python
class Account:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount

    def describe(self):
        return f"{self.owner}: {self.balance}"


class SavingsAccount(Account):
    def __init__(self, owner, balance=0, rate=0.02):
        super().__init__(owner, balance)       # initialize the parent part
        self.rate = rate                       # new attribute

    def add_interest(self):                    # new method
        self.balance += self.balance * self.rate

    def describe(self):                        # override + reuse
        return super().describe() + f" (rate {self.rate:.0%})"


s = SavingsAccount("Ayesha", 1000)
s.deposit(500)                                 # inherited
s.add_interest()
print(s.describe())                            # Ayesha: 1530.0 (rate 2%)
print(isinstance(s, Account), isinstance(s, SavingsAccount))   # True True
print(issubclass(SavingsAccount, Account), type(s).__name__)   # True SavingsAccount
```

- `super()` returns a proxy that finds the next class in the **method resolution order** (more below). Always call `super().__init__(...)` unless you deliberately skip the parent's setup.
- `isinstance(obj, Cls)` is true for `Cls` **and its subclasses**; `type(obj) is Cls` is exact. Prefer `isinstance`.
- Forgetting `super().__init__()` leaves the parent's attributes unset: a classic bug.

## 3. The five types of inheritance

### 3.1 Single inheritance
One parent, one child.

```python
class Vehicle:
    def move(self): return "moving"
class Car(Vehicle):
    pass
print(Car().move())          # moving
```

### 3.2 Multilevel inheritance
A chain: grandparent, parent, child.

```python
class Animal:
    def breathe(self): return "breathing"
class Mammal(Animal):
    def feed_young(self): return "milk"
class Dog(Mammal):
    def bark(self): return "woof"
d = Dog()
print(d.breathe(), d.feed_young(), d.bark())      # breathing milk woof
print([c.__name__ for c in Dog.__mro__])          # ['Dog', 'Mammal', 'Animal', 'object']
```

### 3.3 Hierarchical inheritance
One parent, many children.

```python
class Shape:
    def area(self): raise NotImplementedError
class Circle(Shape):
    def __init__(self, r): self.r = r
    def area(self): return round(3.14159 * self.r ** 2, 2)
class Square(Shape):
    def __init__(self, s): self.s = s
    def area(self): return self.s ** 2
print([sh.area() for sh in (Circle(1), Square(3))])    # [3.14, 9]
```

### 3.4 Multiple inheritance
A class with more than one parent.

```python
class Flyer:
    def move(self): return "flying"
    def fly(self): return "up"
class Swimmer:
    def move(self): return "swimming"
    def swim(self): return "down"
class Duck(Flyer, Swimmer):
    pass
duck = Duck()
print(duck.fly(), duck.swim(), duck.move())        # up down flying   (Flyer is first in the order)
```

### 3.5 Hybrid inheritance
A combination (typically multiple + multilevel), the **diamond** being the classic case:

```text
        Base
       /    \
   Left      Right
       \    /
       Bottom
```

```python
class Base:
    def hello(self): return "Base"
class Left(Base):
    def hello(self): return "Left>" + super().hello()
class Right(Base):
    def hello(self): return "Right>" + super().hello()
class Bottom(Left, Right):
    def hello(self): return "Bottom>" + super().hello()
print(Bottom().hello())     # Bottom>Left>Right>Base
```

Note `Base` appears **once**, and `Right` runs between `Left` and `Base`. That is C3 linearization at work.

## 4. Method Resolution Order (MRO) and C3 linearization

When you call `obj.method()`, Python searches classes in a fixed order, the **MRO**, stored in `Cls.__mro__`. For multiple inheritance Python uses the **C3 linearization** algorithm, which guarantees:

1. A class always appears **before** its parents.
2. The **order of bases** in the `class` statement is preserved.
3. Each class appears **exactly once** (this solves the diamond problem).

```python
print([c.__name__ for c in Bottom.__mro__])       # ['Bottom', 'Left', 'Right', 'Base', 'object']
```

**How C3 merges** (for `Bottom(Left, Right)`): `L[Bottom] = Bottom + merge(L[Left], L[Right], [Left, Right])` where `L[Left] = [Left, Base, object]` and `L[Right] = [Right, Base, object]`. Repeatedly take the first head that does not appear in the **tail** of any other list: `Left` (ok), then `Base` is in the tail of `[Right, Base, object]`, so skip it and take `Right`, then `Base`, then `object`.

If no valid order exists, Python refuses to create the class:

```python
class A: pass
class B(A): pass
try:
    class C(A, B): pass          # asks for A before its own subclass B: impossible
except TypeError as e:
    print("TypeError:", "consistent method resolution order" in str(e))    # TypeError: True
```

### `super()` follows the MRO, not "the parent"

`super()` means "the **next class in the MRO** after the current one", which is why the diamond above ran `Right` between `Left` and `Base`. This makes **cooperative multiple inheritance** possible: every class calls `super()` and the chain visits each class once.

```python
class Logged:
    def __init__(self, **kwargs):
        print("Logged.__init__")
        super().__init__(**kwargs)
class Timestamped:
    def __init__(self, **kwargs):
        print("Timestamped.__init__")
        super().__init__(**kwargs)
class Record(Logged, Timestamped):
    def __init__(self, name, **kwargs):
        print("Record.__init__")
        self.name = name
        super().__init__(**kwargs)

r = Record(name="x")
# Record.__init__
# Logged.__init__
# Timestamped.__init__
print([c.__name__ for c in Record.__mro__])       # ['Record', 'Logged', 'Timestamped', 'object']
```

Rules for cooperative inheritance:
1. Every method in the chain calls `super().method(...)`.
2. Accept `**kwargs` and pass them along, so classes you cannot see in the chain can take their own arguments.
3. The last class before `object` must not forward unknown arguments blindly to `object.__init__` (it takes none); terminate the chain in a base class.

Calling `Parent.method(self)` directly (instead of `super()`) **breaks** the cooperative chain in a diamond (`Base` could run twice). Use `super()`.

## 5. Mixins: small, focused behavior added through inheritance

A **mixin** is a class meant to be inherited alongside others to add one capability. It is not instantiated alone and does not stand for an "is-a" concept.

```python
import json

class JsonMixin:
    def to_json(self):
        return json.dumps(self.__dict__, sort_keys=True)

class ReprMixin:
    def __repr__(self):
        args = ", ".join(f"{k}={v!r}" for k, v in sorted(self.__dict__.items()))
        return f"{type(self).__name__}({args})"

class User(JsonMixin, ReprMixin):
    def __init__(self, name, age):
        self.name, self.age = name, age

u = User("Ayesha", 30)
print(u)                  # User(age=30, name='Ayesha')
print(u.to_json())        # {"age": 30, "name": "Ayesha"}
```

Mixin guidelines: one responsibility, no `__init__` state of its own (or use cooperative `super().__init__(**kwargs)`), put mixins **before** the main base in the bases list, and name them `...Mixin`.

## 6. Inheritance hooks and special cases

### Template method: the parent defines the algorithm, children fill in the steps

```python
class DataImporter:
    def run(self, source):                 # the fixed algorithm
        raw = self.read(source)
        rows = self.parse(raw)
        return [self.validate(r) for r in rows if r]
    def read(self, source): raise NotImplementedError
    def parse(self, raw): raise NotImplementedError
    def validate(self, row): return row    # optional hook with a default

class CsvImporter(DataImporter):
    def read(self, source): return source
    def parse(self, raw): return [line.split(",") for line in raw.splitlines()]
    def validate(self, row): return [c.strip() for c in row]

print(CsvImporter().run("a, b\n c,d"))     # [['a', 'b'], ['c', 'd']]
```

### `__init_subclass__`: react when someone subclasses you

```python
class Plugin:
    registry = {}
    def __init_subclass__(cls, name=None, **kwargs):
        super().__init_subclass__(**kwargs)
        Plugin.registry[name or cls.__name__.lower()] = cls

class Csv(Plugin, name="csv"): pass
class Json(Plugin): pass
print(sorted(Plugin.registry))             # ['csv', 'json']
```

### Subclassing built-in containers

Built-in `dict` and `list` methods written in C often **do not call** your overrides (for example `dict.update` ignores an overridden `__setitem__`). Subclass `collections.UserDict`, `UserList`, or the ABCs in `collections.abc` instead.

```python
from collections import UserDict

class LowerDict(UserDict):
    def __setitem__(self, key, value):
        super().__setitem__(key.lower(), value)

d = LowerDict()
d.update({"A": 1})                         # update goes through __setitem__ here
print(dict(d))                             # {'a': 1}
```

### Custom exception hierarchies

```python
class AppError(Exception): pass
class ValidationError(AppError): pass
class NotFound(AppError): pass

for exc in (ValidationError("bad"), NotFound("gone")):
    try:
        raise exc
    except AppError as e:                  # one handler catches the whole family
        print(type(e).__name__, e)
```

## 7. When inheritance goes wrong

- **Fragile base class:** a change to the parent silently breaks children that depended on its internals.
- **Deep hierarchies** (more than two or three levels) are hard to understand: to know what a method does you must read every level.
- **Liskov violations:** a subclass that cannot honor the parent's contract (a `Square` subclass of `Rectangle` whose `width` setter also changes `height`) surprises callers. See [SOLID](../solid/README.md).
- **Inheriting just to reuse code** couples unrelated concepts: a `Stack` that subclasses `list` exposes `insert` and `sort`, which break stack semantics. Prefer **composition**: hold a list and expose only `push`/`pop`.
- **Diamond with non-cooperative methods:** one class forgets `super()` and the chain stops.
- **Overriding without understanding** what the parent's method promises (side effects, call order).

Rule of thumb: **favor composition over inheritance**; inherit when there is a true is-a relationship, a stable base, and you want polymorphism.

## 8. Two real-world examples

### Example 1: Django class-based views
`ListView` is built from `MultipleObjectTemplateResponseMixin`, `BaseListView`, `ContextMixin` and `View`, a **hybrid** hierarchy using cooperative `super()` calls. You subclass `ListView` and override `get_queryset` or `get_context_data` (template-method hooks), and add mixins such as `LoginRequiredMixin` (put first in the bases so its `dispatch` runs before the rest). Reading `ListView.__mro__` is the way to know which `get_context_data` will actually run.

### Example 2: A plugin system with a registry
A report generator defines a `Exporter` base class using `__init_subclass__` to register every subclass by name (`csv`, `json`, `pdf`). Adding a new format means writing one subclass in its own module: no `if/elif` chain to edit. The base class holds the template method (`export(data)` calls `header()`, `rows()`, `footer()`); each plugin supplies the steps. This is the Open/Closed Principle expressed through inheritance.

## 9. Tips, tricks and pitfalls

- Call `super().__init__(...)` in every `__init__` unless you have a specific reason not to.
- Check the real order with `Cls.__mro__` (or `Cls.mro()`) when multiple inheritance is involved.
- In multiple inheritance, design for **cooperation**: `super()` everywhere, `**kwargs` forwarding.
- Prefer shallow hierarchies (1-2 levels) and small, single-purpose mixins.
- Prefer `isinstance` over `type(x) == Cls`.
- Do not subclass `dict`/`list`/`str` to change core behavior; use `UserDict`/`UserList`, composition, or ABCs.
- Make base classes either clearly **abstract** (cannot be instantiated) or clearly **concrete and stable**.
- Document which methods subclasses are expected to override and what the contract is.
- If you find yourself writing "if isinstance(x, A) ... elif isinstance(x, B)" in client code, polymorphism (overriding) is probably what you want.

## 10. Check yourself

1. What does it mean that inheritance models "is-a"? Give a bad example.
2. Name and illustrate the five types of inheritance.
3. What is the diamond problem and how does Python solve it?
4. What does `super()` actually do?
5. Compute the MRO of `class D(B, C)` where `B(A)` and `C(A)`.
6. Why can `class C(A, B)` fail when `B` is a subclass of `A`?
7. What are the rules of cooperative multiple inheritance?
8. What is a mixin and how does it differ from a base class?
9. Why is subclassing `dict` risky?
10. Give three reasons to prefer composition over inheritance.

<details>
<summary>Answers</summary>

1. The subclass can be used anywhere the superclass is expected and honors its contract. Bad example: `Stack(list)` or `Square(Rectangle)`, which break the base class's guarantees.
2. Single (`Car(Vehicle)`), multilevel (`Dog(Mammal(Animal))`), hierarchical (`Circle(Shape)`, `Square(Shape)`), multiple (`Duck(Flyer, Swimmer)`), hybrid (diamond `Bottom(Left, Right)` over `Base`).
3. A class inherits the same base through two paths, so it is ambiguous which version of a method runs (or whether the base runs twice). Python uses C3 linearization so each class appears once in a deterministic order and `super()` walks that order.
4. It returns a proxy that dispatches to the next class after the current one in the instance's MRO, not simply "the parent".
5. `[D, B, C, A, object]`.
6. It asks for `A` before `B`, but `B` must come before its parent `A`; no linearization satisfies both, so Python raises a `TypeError`.
7. Every method calls `super()`, signatures accept and forward `**kwargs`, and the chain ends in a base class that does not forward arguments to `object`.
8. A mixin is a small class adding one capability, not meant to be instantiated or to represent an is-a concept; a base class defines the main identity and interface.
9. C methods bypass overridden Python methods (for example `update` ignoring `__setitem__`), producing inconsistent behavior; use `UserDict` or composition.
10. Looser coupling (no fragile-base-class problem), behavior can be swapped at runtime, you expose only the API you want, and you avoid deep hierarchies and Liskov violations.

</details>

[Exercises](exercises.md) · [Summary](summary.md)

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

Back to the [part overview](../README.md).
