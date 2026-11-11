# The Python Data Model and CPython Internals

**Prerequisites:** [classes first look](../../00-foundations/python-fundamentals/07-classes-first-look.md), [classes and objects](../../04-oop/classes-objects/README.md), [polymorphism and dunder methods](../../04-oop/polymorphism-dunder/README.md), [memory: stack and heap](../../00-foundations/computer-basics/memory-stack-heap.md). **You will learn:** what really happens when you write `obj.attr`, how **descriptors** power properties and methods, how **metaclasses** and `__init_subclass__` customise classes, how **reference counting and the garbage collector** manage memory, what `__slots__` and `weakref` save, how to read **bytecode** with `dis`, how the **import system** works, and what the **GIL** is, all checked by running code.

## 1. In plain words

Python's friendly surface sits on a small, consistent machine. Every value is an **object** (with an identity, a type and a value); every operator and built-in function is a thin wrapper over **special methods** (`__add__`, `__len__`, `__getitem__`) that your own classes can provide; attribute access follows a **fixed lookup procedure**; and CPython (the standard interpreter) compiles your code to **bytecode** run by a stack-based virtual machine. Knowing this machinery turns "magic" behaviour (properties, `@classmethod`, `super()`, `with`, `for`) into rules you can predict and use.

## 2. Everything is an object, and names are labels

A variable is a **name bound to an object**, not a box holding a value. Assignment never copies; it attaches another label.

```python
import sys

a = [1, 2, 3]
b = a                                       # a second name for the SAME list
print(a is b, id(a) == id(b))
# True True
b.append(4)
print(a)
# [1, 2, 3, 4]

print(type(5), type(type(5)), type(len), type(lambda: 0))
# <class 'int'> <class 'type'> <class 'builtin_function_or_method'> <class 'function'>
print(isinstance(int, object), isinstance(object, type), issubclass(type, object))
# True True True

# CPython keeps a count of references to every object; getrefcount adds one for its own argument
x = object()
base = sys.getrefcount(x)
y = x
print(sys.getrefcount(x) - base)            # one more name pointing at it
# 1
```

## 3. Memory management: reference counting plus a cycle collector

CPython frees an object **the instant its reference count reaches zero** (deterministic, which is why `with` and `__del__` behave predictably). Reference counting cannot free **cycles** (A refers to B refers to A), so a **cyclic garbage collector** periodically finds unreachable cycles.

```python
import gc, weakref

class Resource:
    def __init__(self, name):
        self.name = name
    def __del__(self):
        print(f"  freed {self.name}")

print("refcount drops to zero:")
r = Resource("plain")
del r                                       # freed immediately, no collector needed
# refcount drops to zero:
#   freed plain

print("a reference cycle:")
a, b = Resource("A"), Resource("B")
a.other, b.other = b, a                     # A -> B -> A
del a, b                                    # counts never reach zero: both are still referenced by each other
print("after del: still alive (nothing printed)")
unreachable = gc.collect()                  # the cycle collector finds and frees them
print("collector found", unreachable, "unreachable objects")
# a reference cycle:
# after del: still alive (nothing printed)
#   freed A
#   freed B
# collector found 2 unreachable objects        (the count depends on the Python version: older ones also count each __dict__)

print(gc.get_threshold())                   # generation thresholds: young objects are checked often, old ones rarely
# (2000, 10, 10)
```

(The exact threshold tuple differs between Python versions.) Practical consequences: do not rely on `__del__` for important cleanup (use `with` and context managers); break cycles with **weak references** when an object must refer to something without keeping it alive.

```python
cache = weakref.WeakValueDictionary()       # entries vanish when nothing else references the value

class Big:
    pass

obj = Big()
cache["k"] = obj
print("k" in cache)
# True
del obj                                     # the last strong reference goes away
print("k" in cache)
# False
```

## 4. Attribute lookup and descriptors

When you write `obj.name`, Python runs `type(obj).__getattribute__(obj, "name")`, which follows this order:

1. Look up `name` on the **class** (and its bases, in MRO order). If it is a **data descriptor** (defines `__set__` or `__delete__`), call its `__get__` and stop.
2. Otherwise look in the **instance's `__dict__`**.
3. Otherwise, if the class attribute is a **non-data descriptor** (only `__get__`, like a plain function) or an ordinary value, use that.
4. Otherwise call `__getattr__` if the class defines it, else raise `AttributeError`.

A **descriptor** is any object with `__get__`, `__set__` or `__delete__`, stored as a class attribute. Functions, `property`, `classmethod`, `staticmethod` and `__slots__` entries are all descriptors. You can write your own:

```python
class Positive:
    """A reusable validated attribute: the same logic applied to many fields."""
    def __set_name__(self, owner, name):
        self.private = "_" + name                  # called once when the class is created
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self                            # accessed on the class itself
        return getattr(obj, self.private)
    def __set__(self, obj, value):
        if value <= 0:
            raise ValueError(f"{self.private[1:]} must be positive, got {value}")
        setattr(obj, self.private, value)

class Order:
    price = Positive()
    quantity = Positive()
    def __init__(self, price, quantity):
        self.price, self.quantity = price, quantity     # goes through Positive.__set__

o = Order(9.5, 3)
print(o.price * o.quantity)
# 28.5
try:
    o.quantity = -1
except ValueError as e:
    print(e)
# quantity must be positive, got -1
print(sorted(vars(o)))                            # the real values live in private instance attributes
# ['_price', '_quantity']
```

**Methods are descriptors too.** A function stored in a class has `__get__`, which returns a **bound method** with the instance filled in as `self`. That is the whole trick behind methods:

```python
class Greeter:
    def hello(self):
        return "hi from " + type(self).__name__

g = Greeter()
print(Greeter.hello)                              # a plain function on the class
# <function Greeter.hello at 0x...>              (the address varies)
print(g.hello.__self__ is g, g.hello.__func__ is Greeter.hello)
# True True
print(Greeter.hello(g) == g.hello())              # identical: the bound method just supplies g
# True
```

**`property`** is a ready-made data descriptor; the difference between **data** and **non-data** descriptors decides who wins when an instance attribute has the same name:

```python
class Demo:
    @property
    def computed(self):                           # data descriptor (property defines __set__, raising if no setter)
        return "from property"
    def method(self):                             # non-data descriptor (function)
        return "from class"

d = Demo()
d.__dict__["computed"] = "instance value"         # sneak a value into the instance dict
d.__dict__["method"] = "instance value"
print(d.computed, "|", d.method)
# from property | instance value
```

The property still wins (data descriptor beats instance `__dict__`); the plain method is hidden by the instance attribute (non-data descriptor loses). This is also why `functools.cached_property`, which defines only `__get__`, can store its result in the instance `__dict__` and then be bypassed on later reads (fast).

## 5. Classes are objects: metaclasses and `__init_subclass__`

A class is itself an object, created by calling its **metaclass** (by default `type`). `class A: ...` is roughly `A = type("A", bases, namespace)`.

```python
Point = type("Point", (), {"x": 1, "describe": lambda self: f"Point x={self.x}"})   # make a class at runtime
print(Point().describe(), type(Point))
# Point x=1 <class 'type'>
```

For most customisation you do not need a metaclass. **`__init_subclass__`** runs whenever a subclass is created and is simpler and safer:

```python
class Plugin:
    registry = {}
    def __init_subclass__(cls, name=None, **kwargs):
        super().__init_subclass__(**kwargs)
        Plugin.registry[name or cls.__name__.lower()] = cls     # auto-register every subclass

class CsvExporter(Plugin, name="csv"):
    pass
class JsonExporter(Plugin):
    pass

print(sorted(Plugin.registry))
# ['csv', 'jsonexporter']
```

A **metaclass** is for cases that must change how the class object itself is built or behaves (ORMs, enum, abstract base classes, singletons):

```python
class RequireDocstrings(type):
    def __new__(mcls, name, bases, namespace):
        for attr, value in namespace.items():
            if callable(value) and not attr.startswith("_") and not value.__doc__:
                raise TypeError(f"{name}.{attr} needs a docstring")
        return super().__new__(mcls, name, bases, namespace)

class Documented(metaclass=RequireDocstrings):
    def run(self):
        "Runs it."

try:
    class Undocumented(metaclass=RequireDocstrings):
        def run(self):
            pass
except TypeError as e:
    print(e)
# Undocumented.run needs a docstring
```

Rule of thumb: **decorators** for functions, **class decorators** or **`__init_subclass__`** for classes, and a metaclass only when nothing simpler works.

## 6. `__slots__`: smaller objects

Normally each instance carries a `__dict__` (a hash table) so you can add attributes freely. `__slots__` fixes the attribute set and stores values in a compact array, saving memory when you create **millions** of small objects, and catching typos.

```python
import tracemalloc

class WithDict:
    def __init__(self, x, y):
        self.x, self.y = x, y

class WithSlots:
    __slots__ = ("x", "y")
    def __init__(self, x, y):
        self.x, self.y = x, y

def memory_for(cls, n=100_000):
    tracemalloc.start()
    objs = [cls(i, i) for i in range(n)]
    used = tracemalloc.get_traced_memory()[0]
    tracemalloc.stop()
    return used

dict_bytes, slots_bytes = memory_for(WithDict), memory_for(WithSlots)
print("slots use less memory:", slots_bytes < dict_bytes, f"(about {dict_bytes / slots_bytes:.1f}x smaller)")
# slots use less memory: True (about 1.5x smaller)        (the ratio varies by Python version)

s = WithSlots(1, 2)
try:
    s.z = 3
except AttributeError as e:
    print("no new attributes:", type(e).__name__)
# no new attributes: AttributeError
```

(`@dataclass(slots=True)` gives you this declaratively.) Caveats: no `__dict__` means no dynamic attributes, and multiple inheritance with slots gets awkward.

## 7. Bytecode: what the interpreter really runs

CPython compiles each function to **bytecode**, a list of simple stack-machine instructions, and runs it in a loop. The `dis` module shows it.

```python
import dis

def add_tax(price, rate=0.2):
    total = price * (1 + rate)
    return round(total, 2)

ops = [i.opname for i in dis.get_instructions(add_tax)]
print(len(ops) > 5, "BINARY_OP" in ops, "RETURN_VALUE" in ops or "RETURN_CONST" in ops)
# True True True
print(add_tax.__code__.co_varnames, add_tax.__defaults__)
# ('price', 'rate', 'total') (0.2,)

# a constant expression is folded at compile time, so there is no work left at run time
folded = compile("x = 60 * 60 * 24", "<s>", "exec")
print(86400 in folded.co_consts, "BINARY_OP" in [i.opname for i in dis.get_instructions(folded)])
# True False
```

(`dis.dis(add_tax)` prints a readable listing; its exact opcodes change between Python releases, which is why the checks above only test for presence.) Insights you can draw: **local variable access is faster than globals or attributes** (so hoisting `len` or a method into a local helps hot loops), **function calls cost** more than inline expressions, and the interpreter specialises hot instructions adaptively in recent versions. This is the machinery behind the [performance lesson](../performance-profiling/README.md).

## 8. The import system

`import x` finds a module, executes its code **once**, and caches the result in `sys.modules`; later imports return the cached module object. That is why module-level code runs once and why circular imports misbehave (the second module sees a half-initialised first).

```python
import sys, importlib, importlib.util, types

import json
print("json" in sys.modules, sys.modules["json"] is json)
# True True
print(importlib.util.find_spec("json").origin.endswith("__init__.py"), importlib.util.find_spec("no_such_module_xyz"))
# True None

# build a module out of thin air and register it: now `import fake_config` works
fake = types.ModuleType("fake_config")
fake.DEBUG = True
sys.modules["fake_config"] = fake
import fake_config
print(fake_config.DEBUG, fake_config.__name__)
# True fake_config

# a module is just a namespace filled by running code in it
mod = types.ModuleType("counter_mod")
code = compile("calls = 0\ndef bump():\n    global calls\n    calls += 1\n    return calls", "<counter_mod>", "exec")
exec(code, mod.__dict__)
print(mod.bump(), mod.bump())
# 1 2
```

`__name__ == "__main__"` is true only for the file you run directly, which is why scripts guard their entry point. Packages are directories with `__init__.py` (or namespace packages without). **Import hooks** (`importlib.abc.MetaPathFinder`) let tools such as pytest rewrite assertions at import time. For virtual environments and packaging, see the [tooling lesson](../packaging-tooling/README.md).

## 9. The GIL and free threading

CPython has a **global interpreter lock (GIL)**: only one thread executes Python bytecode at a time. It protects the interpreter's internal data (such as reference counts) with a single lock instead of many. Effects:

- **CPU-bound** pure-Python code does not speed up with threads; use **processes** (`multiprocessing`, `ProcessPoolExecutor`) or native libraries that release the GIL (NumPy).
- **I/O-bound** code (network, disk) speeds up with threads or `asyncio`, since the GIL is released while waiting.
- Recent Python versions offer an optional **free-threaded build** with no GIL; you can ask the running interpreter:

```python
import sys

gil_enabled = sys._is_gil_enabled() if hasattr(sys, "_is_gil_enabled") else True
print("GIL enabled in this interpreter:", gil_enabled)
# GIL enabled in this interpreter: True        (False on a free-threaded build)
```

The [threads, processes and futures lesson](../concurrency/01-threads-processes-and-futures.md) measures these differences.

## 10. Common mistakes

- Believing assignment copies (`b = a`) and then being surprised by shared mutation; use `copy`/`deepcopy` or build a new object.
- Relying on `__del__` or garbage collection timing for cleanup instead of context managers.
- Creating reference cycles (parent and child pointing at each other) in long-running programs without weak references.
- Using a metaclass where `__init_subclass__` or a decorator would do.
- Putting mutable defaults on class attributes (`items = []`): the list is shared by every instance (an instance attribute set in `__init__` is what you want).
- Using `__slots__` everywhere "for speed": it matters only with huge numbers of small objects.
- Doing expensive work at import time, which slows startup and creates import-order bugs.
- Assuming threads give a speed-up for CPU-bound Python code.

## 11. Two real-world examples

**Example 1: The ORM field.** A database library defines `name = CharField(max_length=50)` on model classes. `CharField` is a **descriptor** with `__set_name__`, so it learns its own column name, validates on assignment and converts on read; the model's metaclass collects all fields into a schema. Understanding descriptors and `__set_name__` explains exactly how such libraries work.

**Example 2: The memory-hungry loader.** A service loaded 20 million small records as ordinary class instances and used 4 GB. Switching the record class to `@dataclass(slots=True)` cut per-object overhead substantially, and later moving the numeric columns into a NumPy array reduced it a further order of magnitude.

## 12. Practice

1. Write a descriptor `Typed(expected_type)` that raises `TypeError` unless the value has that type, and use it for a `Person` with `name: str` and `age: int`.
2. Show with `sys.getrefcount` how the count changes when you put an object in a list and then remove it.
3. Make two classes that reference each other in a cycle, add `weakref.ref` to break it, and show `gc.collect()` returns 0 for the weak version.
4. Use `__init_subclass__` to enforce that every subclass defines a `run` method.
5. Use `dis.get_instructions` to list the opcode names of `lambda a, b: a + b` and confirm it contains one `BINARY_OP`.
6. Explain why `d.__dict__["computed"] = "x"` did not override the property but did hide the method.

<details>
<summary>Solutions</summary>

1. ```python
   class Typed:
       def __init__(self, expected_type):
           self.expected_type = expected_type
       def __set_name__(self, owner, name):
           self.private = "_" + name
       def __get__(self, obj, objtype=None):
           return self if obj is None else getattr(obj, self.private)
       def __set__(self, obj, value):
           if not isinstance(value, self.expected_type):
               raise TypeError(f"expected {self.expected_type.__name__}, got {type(value).__name__}")
           setattr(obj, self.private, value)
   class Person:
       name = Typed(str)
       age = Typed(int)
       def __init__(self, name, age):
           self.name, self.age = name, age
   print(Person("Ada", 36).age)
   try:
       Person("Ada", "36")
   except TypeError as e:
       print(e)
   # 36
   # expected int, got str
   ```
2. ```python
   import sys
   obj = object()
   before = sys.getrefcount(obj)
   holder = [obj]
   during = sys.getrefcount(obj)
   holder.clear()
   after = sys.getrefcount(obj)
   print(during - before, after - before)
   # 1 0
   ```
3. ```python
   import gc, weakref
   class Parent:
       pass
   class Child:
       pass
   p, c = Parent(), Child()
   p.child = c
   c.parent = weakref.ref(p)                     # weak back-reference: no cycle of strong references
   del p, c
   print(gc.collect())
   # 0
   ```
4. ```python
   class Task:
       def __init_subclass__(cls, **kw):
           super().__init_subclass__(**kw)
           if "run" not in cls.__dict__:
               raise TypeError(f"{cls.__name__} must define run()")
   class Good(Task):
       def run(self): pass
   try:
       class Bad(Task):
           pass
   except TypeError as e:
       print(e)
   # Bad must define run()
   ```
5. ```python
   import dis
   names = [i.opname for i in dis.get_instructions(lambda a, b: a + b)]
   print(names.count("BINARY_OP"))
   # 1
   ```
   (The loads of `a` and `b` use `LOAD_FAST`-family instructions; recent versions may fuse them into one, so the exact list differs between releases, but there is always exactly one addition.)
6. `property` defines `__set__`, so it is a **data descriptor** and takes priority over the instance `__dict__`. A plain function defines only `__get__` (a **non-data descriptor**), so an entry with the same name in the instance `__dict__` takes priority over it.

</details>

## 13. Check yourself

1. What does it mean that variables are names bound to objects?
2. When does CPython free an object, and what does the cycle collector add?
3. State the attribute lookup order and say where data descriptors fit.
4. How do bound methods work?
5. When would you use `__init_subclass__` versus a metaclass?
6. What do `__slots__` give you and cost you?
7. What is the GIL, and which workloads does it hurt?

<details>
<summary>Answers</summary>

1. Assignment attaches a label to an object without copying; several names can refer to the same object, so mutation through one is visible through the others.
2. Immediately when its reference count reaches zero; the cycle collector finds groups of objects that only reference each other and frees them.
3. Class data descriptor, then instance `__dict__`, then class non-data descriptor or plain class attribute, then `__getattr__`.
4. A function in a class is a non-data descriptor; its `__get__` returns a method object that stores the instance and passes it as the first argument.
5. `__init_subclass__` for hooks that run when subclasses are created (registries, validation); a metaclass only when you must change how the class object itself is constructed or behaves.
6. They give smaller instances and no accidental attributes; they cost dynamic attributes and make multiple inheritance harder.
7. A lock allowing one thread to run Python bytecode at a time; it limits speed-ups for CPU-bound pure-Python threads (use processes or native code), but I/O-bound threads still benefit.

</details>

[Back to Modern Python](../README.md)
