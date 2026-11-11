# Encapsulation and Abstraction: Exercises

These problems go with the [Encapsulation and Abstraction lesson](README.md). Try each one before opening its solution.

## Problems

1. Build `Rectangle` with `width` and `height` properties that reject non-positive values, plus a read-only `area`. Write tests showing invalid values are rejected in `__init__` too.
2. A class exposes `self.items` (a list) publicly. Show a bug this allows, then redesign it so callers cannot corrupt the invariant "no duplicates".
3. Explain what is wrong with this and fix it using a property:
   ```python
   class User:
       def __init__(self, email):
           self.email = email
   u = User("not-an-email")
   ```
4. Write a reusable `Range(lo, hi)` descriptor and use it for `age` (0-130) and `score` (0-100) on one class.
5. Define an abstract `Notifier` with `send(to, message)` and implement `EmailNotifier`, `SmsNotifier` and `FakeNotifier` (records messages). Write `alert(notifier, users)` that works with all three.
6. Rewrite exercise 5's interface as a `Protocol` and show a class that satisfies it without inheriting.
7. Show name mangling: create a base and a subclass that both define `__token` and demonstrate that they do not collide. List the real attribute names.
8. Make `cached_property` demonstrate laziness: count how many times the expensive function runs for 3 accesses on 2 instances. How do you invalidate the cache?
9. Identify the leaky abstraction: `def get_user(id)` silently runs a database query and raises `ConnectionError` sometimes. How would you document or reshape it?

<details>
<summary>Solutions</summary>

**1.**
```python
class Rectangle:
    def __init__(self, width, height):
        self.width, self.height = width, height      # setters validate
    @property
    def width(self): return self._w
    @width.setter
    def width(self, v):
        if v <= 0: raise ValueError("width must be positive")
        self._w = v
    @property
    def height(self): return self._h
    @height.setter
    def height(self, v):
        if v <= 0: raise ValueError("height must be positive")
        self._h = v
    @property
    def area(self): return self._w * self._h
r = Rectangle(2, 3); print(r.area)
for bad in ((0, 1), (1, -1)):
    try: Rectangle(*bad)
    except ValueError as e: print(e)
```

**2.** Bug: `obj.items.append("a"); obj.items.append("a")` creates duplicates; `obj.items = None` breaks everything. Redesign:
```python
class UniqueBag:
    def __init__(self):
        self._items = []
    def add(self, x):
        if x not in self._items:
            self._items.append(x)
    @property
    def items(self):
        return tuple(self._items)
b = UniqueBag(); b.add("a"); b.add("a"); print(b.items)    # ('a',)
```

**3.**
```python
class User:
    def __init__(self, email): self.email = email
    @property
    def email(self): return self._email
    @email.setter
    def email(self, v):
        if "@" not in v: raise ValueError("invalid email")
        self._email = v
try: User("not-an-email")
except ValueError as e: print(e)
```
Existing callers (`u.email`, `u.email = ...`) are unchanged.

**4.**
```python
class Range:
    def __init__(self, lo, hi): self.lo, self.hi = lo, hi
    def __set_name__(self, owner, name): self.name = "_" + name
    def __get__(self, obj, t=None): return self if obj is None else getattr(obj, self.name)
    def __set__(self, obj, v):
        if not self.lo <= v <= self.hi: raise ValueError(f"{self.name[1:]} out of range")
        setattr(obj, self.name, v)
class Student:
    age = Range(0, 130); score = Range(0, 100)
    def __init__(self, age, score): self.age, self.score = age, score
s = Student(20, 95)
try: s.score = 101
except ValueError as e: print(e)
```

**5.**
```python
from abc import ABC, abstractmethod
class Notifier(ABC):
    @abstractmethod
    def send(self, to, message): ...
class EmailNotifier(Notifier):
    def send(self, to, message): print(f"email to {to}: {message}")
class SmsNotifier(Notifier):
    def send(self, to, message): print(f"sms to {to}: {message}")
class FakeNotifier(Notifier):
    def __init__(self): self.sent = []
    def send(self, to, message): self.sent.append((to, message))
def alert(notifier: Notifier, users):
    for u in users: notifier.send(u, "server down")
fake = FakeNotifier(); alert(fake, ["a", "b"]); print(fake.sent); alert(EmailNotifier(), ["a"])
```

**6.**
```python
from typing import Protocol
class SupportsSend(Protocol):
    def send(self, to: str, message: str) -> None: ...
class Pager:                       # no inheritance
    def send(self, to, message): print("page", to, message)
def alert2(n: SupportsSend, users):
    for u in users: n.send(u, "x")
alert2(Pager(), ["ops"])
```

**7.**
```python
class Base:
    def __init__(self): self.__token = "base"
    def base_token(self): return self.__token
class Child(Base):
    def __init__(self):
        super().__init__()
        self.__token = "child"
    def child_token(self): return self.__token
c = Child()
print(c.base_token(), c.child_token(), sorted(vars(c)))   # base child ['_Base__token', '_Child__token']
```

**8.**
```python
from functools import cached_property
calls = 0
class Heavy:
    @cached_property
    def value(self):
        global calls; calls += 1; return 42
a, b = Heavy(), Heavy()
for _ in range(3): a.value; b.value
print(calls)                         # 2 (once per instance)
del a.value                          # invalidate: the next access recomputes
a.value; print(calls)                # 3
```

**9.** It leaks: the name suggests a cheap lookup, but it does I/O, can fail with infrastructure errors, and may be slow. Reshape: make the dependency explicit (`UserRepository.get(id)`), document the failure modes (`UserNotFound`, `RepositoryUnavailable`), translate low-level errors into domain errors, and keep I/O out of code paths that look like pure functions.

</details>

[Lesson](README.md) · [Summary](summary.md)
