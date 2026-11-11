# Singleton Pattern

**Family:** creational · **Also called:** one-of-a-kind object · **How often you will use it:** rarely (and be careful) · **Difficulty:** easy to write, easy to misuse

## 1. In plain words

A **Singleton** guarantees that a class has **exactly one instance** for the whole program, and gives everyone the same access point to it.

Analogy: a country has **one president at a time**. Anyone who says "the president" means the same person; you cannot just create a second one.

Typical candidates: a configuration registry, a logging setup, a connection pool, a hardware device handle: things where two copies would be wrong or wasteful.

## 2. The problem

Two parts of a program create their own copy of something that must be shared:

```python
class Settings:
    def __init__(self):
        self.values = {}

a = Settings(); a.values["mode"] = "prod"
b = Settings()                          # a second, empty, unrelated copy
print(b.values)                         # {}  : the setting is "lost"
```

You need `Settings()` to hand back the **same object** every time.

## 3. The solution

```text
Client A ----\
              >---- Singleton.instance()  --->  [ the one object ]
Client B ----/
```

Roles: the **singleton class** keeps a private reference to its single instance and controls creation, so a second `Singleton()` returns the first one (or raises).

## 4. Step by step

### Version A: control creation with `__new__`

```python
import threading

class Singleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:                  # fast path: already created
            with cls._lock:                        # only one thread may create it
                if cls._instance is None:          # check again inside the lock (double-checked locking)
                    cls._instance = super().__new__(cls)
        return cls._instance

class Config(Singleton):
    def __init__(self):
        if not hasattr(self, "values"):            # __init__ runs on EVERY Config() call, so guard it
            self.values = {}

a, b = Config(), Config()
a.values["mode"] = "prod"
print(a is b, b.values)                            # True {'mode': 'prod'}
```

`__new__` creates the object and `__init__` initializes it. `Config()` calls both every time, so without the `hasattr` guard the second call would wipe the shared state.

### Version B: a decorator

```python
def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton
class Registry:
    def __init__(self):
        self.items = []

print(Registry() is Registry())                    # True
```

### Version C: forbid a second instance (the "strict" style)

```python
class StrictSingleton:
    __instance = None

    def __init__(self):
        if StrictSingleton.__instance is not None:
            raise RuntimeError("This class is a singleton: use get_instance()")
        StrictSingleton.__instance = self

    @classmethod
    def get_instance(cls):
        if cls.__instance is None:
            cls()
        return cls.__instance

s1 = StrictSingleton.get_instance()
s2 = StrictSingleton.get_instance()
print(s1 is s2)                                    # True
try:
    StrictSingleton()
except RuntimeError as e:
    print(e)                                       # This class is a singleton: use get_instance()
```

## 5. The Pythonic way: a module is already a singleton

Python imports a module **once** and caches it, so a module-level object is naturally shared:

```python no-run
# skip
# settings.py
DEBUG = False
DATABASE_URL = "sqlite:///app.db"

# anywhere else
import settings
settings.DEBUG          # the same module object everywhere
```

For most needs this is better than any class trick: no locks, no tricks, easy to read. A module-level instance works too: `logger = Logger()` at the bottom of `logger.py`, then `from logger import logger`.

A lightweight alternative is the **Borg / shared-state** idiom: many objects, one shared `__dict__`:

```python
class Borg:
    _shared = {}
    def __init__(self):
        self.__dict__ = self._shared               # every instance shares the same attributes

x, y = Borg(), Borg()
x.color = "red"
print(y.color, x is y)                             # red False  (different objects, same state)
```

## 6. When to use it (and when not to)

**Use it when** exactly one instance must exist and sharing is the point: configuration, a registry, a pool manager.

**Do not use it** just for convenient global access. Singleton is **global state** in disguise, and global state hurts.

## 7. Pros and cons

| Pros | Cons |
|------|------|
| One shared instance, controlled creation | Hidden dependencies: code silently relies on a global |
| Lazy creation (made on first use) | **Hard to test**: state leaks between tests and you cannot swap in a fake |
| Easy global access | Breaks the Single Responsibility idea (manages its own lifetime *and* does its job) |
| | Threading bugs if creation is not locked |

**Better alternative:** create **one object at the start of the program** and **pass it in** (dependency injection). You still have one instance, but code receives it explicitly and tests can pass a different one. See [composition](../../composition-design/README.md).

## 8. Related patterns

- [Factory Method](factory-method.md) and [Abstract Factory](abstract-factory.md) are often implemented as singletons.
- [Object Pool](object-pool.md) is "a few instances" instead of "exactly one".
- [Flyweight](../structural/flyweight.md) shares many small objects; Singleton shares one.

## 9. Two real-world examples

**Example 1: `logging.getLogger("app")`.** Calling it anywhere in your program returns the *same* logger object for the same name, so all modules write through one configured logger. Python's `logging` does this with a registry (a close cousin of Singleton).

**Example 2: a database connection pool manager.** Opening connections is slow, so the application creates one pool manager at startup. Every request handler asks the *same* manager for a connection. Creating two managers would double the connections and could exceed the database limit. In well-structured code the pool is created in `main()` and injected, rather than reached through a global.

## 10. Common mistakes

- Forgetting `__init__` runs on every call (reset state each time).
- Not locking creation in multi-threaded code.
- Making things singletons "because there is only one at the moment".
- Using them to avoid passing parameters (it hides dependencies).
- Hard to reset between tests: provide a reset hook or avoid the pattern.

## 11. Practice

1. Make a `Counter` singleton with `increment()` and show two names share the count.
2. Prove the `__new__` version is safe with 20 threads creating instances.
3. Rewrite a Singleton `Logger` as a module-level object plus a function parameter, and show how a test can pass a fake logger.

<details>
<summary>Solutions</summary>

**1.**
```python
class Counter(Singleton):
    def __init__(self):
        if not hasattr(self, "n"):
            self.n = 0
    def increment(self):
        self.n += 1
        return self.n
a, b = Counter(), Counter()
a.increment(); b.increment()
print(a.n, a is b)                                 # 2 True
```

**2.**
```python
import threading
seen = set()
def make():
    seen.add(id(Config()))
threads = [threading.Thread(target=make) for _ in range(20)]
for t in threads: t.start()
for t in threads: t.join()
print(len(seen))                                   # 1
```

**3.**
```python
class Logger:
    def __init__(self): self.lines = []
    def log(self, msg): self.lines.append(msg)
logger = Logger()                                  # module-level instance = the singleton

def process(item, log=logger.log):                 # inject; defaults to the shared one
    log(f"processing {item}")

fake = []
process("x", log=fake.append)                      # a test passes a fake
print(fake, logger.lines)                          # ['processing x'] []
```

</details>

## 12. Check yourself

1. What guarantee does a Singleton provide?
2. Why is a module often the best Singleton in Python?
3. Why does the `__new__` version need a `hasattr` check in `__init__`?
4. Why is Singleton called "global state in disguise"?
5. What is the alternative that keeps one instance but is easy to test?

<details>
<summary>Answers</summary>

1. Exactly one instance exists and everyone gets the same one.
2. Modules are executed once and cached in `sys.modules`, so their contents are naturally shared with no extra code.
3. `__init__` runs every time `Config()` is called even though `__new__` returns the same object, so without a guard it would reset the shared state.
4. Any code can reach it from anywhere, so dependencies are hidden, state leaks between parts of the program, and tests cannot easily replace it.
5. Create the single object at startup and inject it into the code that needs it.

</details>

## More examples

Runnable script from your companion repository: [`creationalPattern/singletonPattern.py`](https://github.com/M-Hammad-Faisal/design-patterns-python/blob/master/creationalPattern/singletonPattern.py)

[Family overview](README.md) · [All patterns](../README.md)
