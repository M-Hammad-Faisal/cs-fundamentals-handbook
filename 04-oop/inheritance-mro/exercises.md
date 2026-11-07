# Inheritance and MRO: Exercises

1. Model `Employee`, `Manager(Employee)` and `Engineer(Employee)` with a `salary()` method; managers get a bonus per report. Use `super()` and show polymorphic totals for a mixed list.
2. Predict then verify the MRO and output:
   ```python
   class A:
       def who(self): return "A"
   class B(A):
       def who(self): return "B>" + super().who()
   class C(A):
       def who(self): return "C>" + super().who()
   class D(B, C):
       def who(self): return "D>" + super().who()
   print(D().who(), [k.__name__ for k in D.__mro__])
   ```
3. Hand-compute the C3 linearization of `class Z(X, Y)` where `X(A)`, `Y(A, B)`, `A(object)`, `B(object)`. Confirm with `Z.__mro__`.
4. Build three mixins (`TimestampMixin`, `JsonMixin`, `ValidationMixin`) and a model class using them cooperatively. Show that each mixin's `__init__` runs exactly once.
5. Show a case where calling `Parent.__init__(self)` explicitly runs `Base.__init__` twice in a diamond, and fix it with `super()`.
6. Reproduce the Square/Rectangle problem. Write a test showing Liskov is violated and redesign to fix it.
7. Replace `class Stack(list)` with a composition-based stack exposing only `push`, `pop`, `peek` and `__len__`.
8. Implement a plugin registry with `__init_subclass__` where each plugin declares an `extension = ".csv"` attribute and `get_plugin(filename)` picks the right one.
9. Demonstrate why subclassing `dict` and overriding `__setitem__` is unreliable, and fix it with `UserDict`.
10. When would you choose inheritance over composition? Give two criteria and one counterexample.

<details>
<summary>Solutions</summary>

**1.**
```python
class Employee:
    def __init__(self, name, base): self.name, self.base = name, base
    def salary(self): return self.base
class Manager(Employee):
    def __init__(self, name, base, reports=0):
        super().__init__(name, base); self.reports = reports
    def salary(self): return super().salary() + 1000 * self.reports
class Engineer(Employee):
    def salary(self): return super().salary() + 500
staff = [Employee("a", 3000), Manager("b", 5000, 3), Engineer("c", 4000)]
print([e.salary() for e in staff], sum(e.salary() for e in staff))   # [3000, 8000, 4500] 15500
```

**2.** MRO `['D', 'B', 'C', 'A', 'object']`; output `D>B>C>A`.

**3.** `L[X]=[X,A,object]`, `L[Y]=[Y,A,B,object]`. `merge([X,A,object],[Y,A,B,object],[X,Y])`: take `X`; next head `A` is in the tail of `[Y,A,B,object]`, so skip; take `Y`; then `A` (no longer in any tail except...) is it in the tail of `[A,B,object]`? It is the head there, so take `A`; then `object` is in the tail of `[B,object]`, so take `B`, then `object`. Result `[Z, X, Y, A, B, object]`.
```python
class A: pass
class B: pass
class X(A): pass
class Y(A, B): pass
class Z(X, Y): pass
print([k.__name__ for k in Z.__mro__])
```

**4.**
```python
import json, time
class TimestampMixin:
    def __init__(self, **kw): self.created = "t0"; super().__init__(**kw)
class JsonMixin:
    def to_json(self): return json.dumps(self.__dict__, sort_keys=True)
class ValidationMixin:
    def __init__(self, **kw):
        super().__init__(**kw)
        for k, v in self.__dict__.items():
            if v is None: raise ValueError(k)
class Model(TimestampMixin, ValidationMixin, JsonMixin):
    def __init__(self, name, **kw): self.name = name; super().__init__(**kw)
print(Model(name="x").to_json())
```

**5.**
```python
count = []
class Base:
    def __init__(self): count.append("Base")
class L(Base):
    def __init__(self): Base.__init__(self); count.append("L")      # explicit parent call
class R(Base):
    def __init__(self): Base.__init__(self); count.append("R")
class Bot(L, R):
    def __init__(self): L.__init__(self); R.__init__(self)
Bot(); print(count)                     # ['Base', 'L', 'Base', 'R']  (Base ran twice)
count.clear()
class L2(Base):
    def __init__(self): super().__init__(); count.append("L")
class R2(Base):
    def __init__(self): super().__init__(); count.append("R")
class Bot2(L2, R2):
    def __init__(self): super().__init__()
Bot2(); print(count)                    # ['Base', 'R', 'L']  (Base ran once)
```

**6.**
```python
class Rectangle:
    def __init__(self, w, h): self._w, self._h = w, h
    width = property(lambda s: s._w, lambda s, v: setattr(s, "_w", v))
    height = property(lambda s: s._h, lambda s, v: setattr(s, "_h", v))
    def area(self): return self._w * self._h
class Square(Rectangle):
    def __init__(self, s): super().__init__(s, s)
    width = property(lambda s: s._w, lambda s, v: (setattr(s, "_w", v), setattr(s, "_h", v)) and None)
def stretch(r: Rectangle):
    r.width = 10
    return r.area() == 10 * r.height          # true for any rectangle
print(stretch(Rectangle(2, 3)))              # True
sq = Square(2)
sq.width = 10; print(sq.area())              # 100: setting width also changed height
```
A `Square` surprises code written for `Rectangle`. Fix: do not model it as a subtype; make both implement a small `Shape` interface (`area()`), or make shapes immutable value objects.

**7.**
```python
class Stack:
    def __init__(self): self._items = []
    def push(self, x): self._items.append(x)
    def pop(self): return self._items.pop()
    def peek(self): return self._items[-1]
    def __len__(self): return len(self._items)
s = Stack(); s.push(1); s.push(2); print(s.pop(), len(s))
```

**8.**
```python
class Plugin:
    registry = {}
    extension = None
    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        if cls.extension: Plugin.registry[cls.extension] = cls
class CsvPlugin(Plugin): extension = ".csv"
class JsonPlugin(Plugin): extension = ".json"
def get_plugin(filename):
    import os
    return Plugin.registry[os.path.splitext(filename)[1]]
print(get_plugin("data.json").__name__)
```

**9.**
```python
class BadDict(dict):
    def __setitem__(self, k, v): super().__setitem__(k, v * 2)
b = BadDict(); b["a"] = 1; b.update(c=1)
print(dict(b))                          # {'a': 2, 'c': 1}  (update bypassed the override)
from collections import UserDict
class GoodDict(UserDict):
    def __setitem__(self, k, v): super().__setitem__(k, v * 2)
g = GoodDict(); g["a"] = 1; g.update(c=1); print(dict(g))    # {'a': 2, 'c': 2}
```

**10.** Choose inheritance when (1) there is a genuine is-a relationship that satisfies the base class's contract everywhere, and (2) you want substitutability/polymorphism and the base is stable (for example custom exceptions, framework extension points). Counterexample: a `Logger` that "has a" file handle should hold it, not subclass `File`.

</details>

[Lesson](README.md) · [Summary](summary.md)
