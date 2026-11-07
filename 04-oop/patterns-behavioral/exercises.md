# Behavioral Patterns: Exercises

1. **Strategy:** implement `PriceCalculator` with strategies `Regular`, `Student` (20% off), `Bulk` (10% off when quantity >= 10). Do it with classes, then with plain functions in a dictionary.
2. **Observer:** build a `Thermostat` that notifies observers when temperature crosses a threshold, supports unsubscribe, and does not let one failing handler stop the others.
3. **Command:** implement a `Calculator` with `AddCommand`, `MultiplyCommand` and a history supporting `undo()` and `redo()`.
4. **State:** model a traffic light (`red -> green -> yellow -> red`) with State classes, then again as a transition table. Which is shorter?
5. **Template Method:** write `DataPipeline.run()` with steps `extract`, `transform`, `load`, an optional `validate` hook, and two subclasses.
6. **Iterator:** write a generator `fibonacci()` (infinite), `take(n, iterable)`, and an iterable `Countdown` class that can be iterated twice.
7. **Chain of Responsibility:** write a validation chain for sign-up data (non-empty name, valid email, password length >= 8) returning the first error or "ok".
8. **Mediator:** implement a `Dialog` mediator coordinating a `Checkbox("I agree")` and a `Button("Submit")` so the button is enabled only when the box is checked.
9. **Memento:** add undo to a drawing app that stores `shapes` using snapshots, and compare memory cost with a Command-based undo.
10. **Visitor:** add a `DepthCalculator` visitor to the expression tree from the lesson without changing node classes.
11. **Null Object:** implement `NullUser` so `request.user.name`, `is_authenticated` and `can("edit")` work without `None` checks.
12. Name the pattern: (a) `sorted(words, key=len)`, (b) Django's `post_save`, (c) Celery task messages, (d) WSGI middleware stack, (e) `contextlib.nullcontext`.

<details>
<summary>Solutions</summary>

**1.**
```python
class Regular:
    def total(self, price, qty): return price * qty
class Student:
    def total(self, price, qty): return price * qty * 0.8
class Bulk:
    def total(self, price, qty): return price * qty * (0.9 if qty >= 10 else 1)
class PriceCalculator:
    def __init__(self, strategy): self.strategy = strategy
    def total(self, price, qty): return self.strategy.total(price, qty)
print(PriceCalculator(Student()).total(10, 2), PriceCalculator(Bulk()).total(10, 10))   # 16.0 90.0
STRATEGIES = {"regular": lambda p, q: p * q, "student": lambda p, q: p * q * 0.8,
              "bulk": lambda p, q: p * q * (0.9 if q >= 10 else 1)}
print(STRATEGIES["bulk"](10, 10))
```

**2.**
```python
class Thermostat:
    def __init__(self, threshold):
        self.threshold, self.temp, self._subs = threshold, 20, []
    def subscribe(self, fn):
        self._subs.append(fn); return lambda: self._subs.remove(fn)
    def set_temp(self, t):
        crossed = (self.temp <= self.threshold) != (t <= self.threshold)
        self.temp = t
        if crossed:
            for fn in list(self._subs):
                try: fn(t)
                except Exception as e: print("handler failed:", type(e).__name__)
seen = []
th = Thermostat(25)
def broken(t): raise RuntimeError
th.subscribe(broken); unsub = th.subscribe(seen.append)
th.set_temp(30); unsub(); th.set_temp(10)
print(seen)        # [30]
```

**3.**
```python
class Calc:
    def __init__(self): self.value = 0
class Add:
    def __init__(self, c, n): self.c, self.n = c, n
    def execute(self): self.c.value += self.n
    def undo(self): self.c.value -= self.n
class Mul:
    def __init__(self, c, n): self.c, self.n, self.prev = c, n, None
    def execute(self): self.prev = self.c.value; self.c.value *= self.n
    def undo(self): self.c.value = self.prev
class Hist:
    def __init__(self): self.done, self.undone = [], []
    def run(self, cmd): cmd.execute(); self.done.append(cmd); self.undone.clear()
    def undo(self):
        if self.done: c = self.done.pop(); c.undo(); self.undone.append(c)
    def redo(self):
        if self.undone: c = self.undone.pop(); c.execute(); self.done.append(c)
c, h = Calc(), Hist()
h.run(Add(c, 5)); h.run(Mul(c, 3)); print(c.value)      # 15
h.undo(); print(c.value); h.undo(); print(c.value); h.redo(); print(c.value)    # 5 0 5
```

**4.**
```python
class Light:
    def __init__(self): self.state = Red()
    def next(self): self.state = self.state.next()
class Red:    name = "red";    next = lambda self: Green()
class Green:  name = "green";  next = lambda self: Yellow()
class Yellow: name = "yellow"; next = lambda self: Red()
l = Light(); names = []
for _ in range(4): names.append(l.state.name); l.next()
print(names)                                            # ['red', 'green', 'yellow', 'red']
TRANSITIONS = {"red": "green", "green": "yellow", "yellow": "red"}
s = "red"; seq = []
for _ in range(4): seq.append(s); s = TRANSITIONS[s]
print(seq)                                              # the table is shorter when states have no behavior of their own
```

**5.**
```python
from abc import ABC, abstractmethod
class DataPipeline(ABC):
    def run(self):
        rows = self.transform(self.extract())
        if not self.validate(rows): raise ValueError("invalid data")
        return self.load(rows)
    @abstractmethod
    def extract(self): ...
    @abstractmethod
    def transform(self, rows): ...
    @abstractmethod
    def load(self, rows): ...
    def validate(self, rows): return True
class Doubler(DataPipeline):
    def extract(self): return [1, 2, 3]
    def transform(self, rows): return [r * 2 for r in rows]
    def load(self, rows): return sum(rows)
class Strict(Doubler):
    def validate(self, rows): return all(r > 100 for r in rows)
print(Doubler().run())
try: Strict().run()
except ValueError as e: print(e)
```

**6.**
```python
from itertools import islice
def fibonacci():
    a, b = 0, 1
    while True:
        yield a; a, b = b, a + b
def take(n, it): return list(islice(it, n))
class Countdown:
    def __init__(self, n): self.n = n
    def __iter__(self): return iter(range(self.n, 0, -1))
c = Countdown(3)
print(take(8, fibonacci()), list(c), list(c))
```

**7.**
```python
import re
def not_empty(d): return None if d.get("name") else "name is required"
def valid_email(d): return None if re.fullmatch(r"[^@\s]+@[^@\s]+\.\w+", d.get("email", "")) else "invalid email"
def long_password(d): return None if len(d.get("password", "")) >= 8 else "password too short"
def validate(data, chain=(not_empty, valid_email, long_password)):
    for check in chain:
        error = check(data)
        if error: return error
    return "ok"
print(validate({"name": "a", "email": "a@x.com", "password": "12345678"}), validate({"name": "a", "email": "bad"}))
```

**8.**
```python
class Checkbox:
    def __init__(self, mediator): self.mediator, self.checked = mediator, False
    def toggle(self): self.checked = not self.checked; self.mediator.notify(self)
class Button:
    def __init__(self): self.enabled = False
class Dialog:
    def __init__(self):
        self.agree, self.submit = Checkbox(self), Button()
    def notify(self, sender):
        if sender is self.agree: self.submit.enabled = self.agree.checked
d = Dialog(); print(d.submit.enabled); d.agree.toggle(); print(d.submit.enabled); d.agree.toggle(); print(d.submit.enabled)
```

**9.**
```python
class Canvas:
    def __init__(self): self.shapes, self.undo_stack = [], []
    def checkpoint(self): self.undo_stack.append(tuple(self.shapes))      # memento: full copy per step
    def add(self, s): self.checkpoint(); self.shapes.append(s)
    def undo(self):
        if self.undo_stack: self.shapes = list(self.undo_stack.pop())
cv = Canvas(); cv.add("circle"); cv.add("square"); cv.undo(); print(cv.shapes)    # ['circle']
```
Memento stores whole snapshots (memory grows with document size per step); a Command-based undo stores only the inverse of each action (small), but every action needs a correct `undo`.

**10.**
```python
class Num:
    def __init__(self, v): self.v = v
    def accept(self, vis): return vis.visit_num(self)
class Add:
    def __init__(self, l, r): self.l, self.r = l, r
    def accept(self, vis): return vis.visit_add(self)
class Depth:
    def visit_num(self, n): return 1
    def visit_add(self, n): return 1 + max(n.l.accept(self), n.r.accept(self))
print(Add(Num(1), Add(Num(2), Num(3))).accept(Depth()))     # 3
```

**11.**
```python
class NullUser:
    name = "anonymous"
    is_authenticated = False
    def can(self, action): return False
class User:
    is_authenticated = True
    def __init__(self, name, perms): self.name, self.perms = name, perms
    def can(self, action): return action in self.perms
def handle(user=None):
    user = user or NullUser()
    return f"{user.name}: edit={user.can('edit')} auth={user.is_authenticated}"
print(handle(), "|", handle(User("ana", {"edit"})))
```

**12.** (a) Strategy, (b) Observer, (c) Command, (d) Chain of Responsibility, (e) Null Object.

</details>

[Lesson](README.md) · [Summary](summary.md)
