# Classes and Objects in Depth: Exercises

1. Without running it, predict the output, then explain:
   ```python
   a = [1, 2]; b = a; c = a[:]
   b.append(3)
   print(a, c, a is b, a is c, a == c)
   ```
2. Write a `Temperature` class storing Celsius with `from_fahrenheit` (class method) and `to_fahrenheit` (instance method), a good `__repr__`, and ordering by temperature using `functools.total_ordering`.
3. Fix this class and explain the bug:
   ```python
   class Cart:
       def __init__(self, items=[]):
           self.items = items
   ```
4. Create `Vector2D(x, y)` as a value object: `__eq__`, `__hash__`, `__add__`, `__repr__`, and make it usable as a dict key. Why must it be immutable?
5. Write a class `Counter` with a class attribute that tracks how many instances were created and a class method returning it. Show that instances do not break the count after `del`.
6. Show the difference between shallow and deep copy on a nested structure (a list of lists), then write a class with a `copy()` method that deep-copies its state.
7. Use `__getattr__` to build a read-only `Namespace` from a dict that supports `ns.a.b.c` for nested dicts and raises `AttributeError` for missing names.
8. Use `weakref` to build a cache that does not keep objects alive. Demonstrate that an entry disappears when the last strong reference goes away.
9. Measure memory of 100,000 instances with and without `__slots__` using `tracemalloc`.

<details>
<summary>Solutions</summary>

**1.** `[1, 2, 3] [1, 2] True False False`. `b` is another name for `a`; `c` is a copy.

**2.**
```python
from functools import total_ordering

@total_ordering
class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius
    @classmethod
    def from_fahrenheit(cls, f):
        return cls((f - 32) * 5 / 9)
    def to_fahrenheit(self):
        return self.celsius * 9 / 5 + 32
    def __eq__(self, other):
        return isinstance(other, Temperature) and self.celsius == other.celsius
    def __lt__(self, other):
        if not isinstance(other, Temperature):
            return NotImplemented
        return self.celsius < other.celsius
    def __hash__(self):
        return hash(self.celsius)
    def __repr__(self):
        return f"Temperature({self.celsius:g}C)"

print(Temperature.from_fahrenheit(212), Temperature(0) < Temperature(5), Temperature(0) >= Temperature(5))
```

**3.** The default list is created once and shared by every `Cart()` that uses the default. Fix:
```python
class Cart:
    def __init__(self, items=None):
        self.items = list(items) if items is not None else []
```

**4.**
```python
class Vector2D:
    __slots__ = ("_x", "_y")
    def __init__(self, x, y):
        self._x, self._y = x, y
    x = property(lambda self: self._x)
    y = property(lambda self: self._y)
    def __eq__(self, o): return isinstance(o, Vector2D) and (self.x, self.y) == (o.x, o.y)
    def __hash__(self): return hash((self.x, self.y))
    def __add__(self, o):
        if not isinstance(o, Vector2D): return NotImplemented
        return Vector2D(self.x + o.x, self.y + o.y)
    def __repr__(self): return f"Vector2D({self.x}, {self.y})"
d = {Vector2D(1, 2): "a"}
print(d[Vector2D(1, 2)], Vector2D(1, 2) + Vector2D(3, 4))
```
It must be immutable because a mutated key would sit in the wrong hash bucket and become unreachable.

**5.**
```python
class Counter:
    created = 0
    def __init__(self):
        Counter.created += 1
    @classmethod
    def total_created(cls):
        return cls.created
a, b = Counter(), Counter(); del a
print(Counter.total_created())     # 2 (it counts creations, not live instances)
```

**6.**
```python
import copy
grid = [[0, 0], [0, 0]]
shallow, deep = copy.copy(grid), copy.deepcopy(grid)
grid[0][0] = 9
print(shallow[0][0], deep[0][0])   # 9 0

class Doc:
    def __init__(self, tags): self.tags = tags
    def copy(self): return copy.deepcopy(self)
d1 = Doc(["a"]); d2 = d1.copy(); d1.tags.append("b"); print(d2.tags)   # ['a']
```

**7.**
```python
class Namespace:
    def __init__(self, data): self._data = data
    def __getattr__(self, name):
        try:
            v = self._data[name]
        except KeyError:
            raise AttributeError(name) from None
        return Namespace(v) if isinstance(v, dict) else v
ns = Namespace({"a": {"b": {"c": 42}}})
print(ns.a.b.c)
try: ns.missing
except AttributeError as e: print("AttributeError", e)
```

**8.**
```python
import weakref, gc
class Thing: pass
cache = weakref.WeakValueDictionary()
t = Thing(); cache["k"] = t
print("k" in cache)       # True
del t; gc.collect()
print("k" in cache)       # False
```

**9.**
```python
import tracemalloc
class A:
    def __init__(self): self.x = self.y = 0
class B:
    __slots__ = ("x", "y")
    def __init__(self): self.x = self.y = 0
for cls in (A, B):
    tracemalloc.start()
    objs = [cls() for _ in range(100_000)]
    print(cls.__name__, tracemalloc.get_traced_memory()[0] // 1024, "KiB")
    tracemalloc.stop()
```
`B` uses markedly less memory.

</details>

[Lesson](README.md) · [Summary](summary.md)
