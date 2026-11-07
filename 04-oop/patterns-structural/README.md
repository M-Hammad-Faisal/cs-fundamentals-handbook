# Design Patterns II: Structural Patterns

## 1. The idea

**Structural patterns** are about **composing classes and objects into larger structures** while keeping the parts flexible and decoupled. Most are different ways of putting **one object in front of another** (wrapping), so the key to telling them apart is **intent**:

| Pattern | Wraps | Intent |
|---------|-------|--------|
| **Adapter** | One object | Make an incompatible interface match the one clients expect |
| **Decorator** | One object | Add behavior dynamically while keeping the same interface |
| **Proxy** | One object | Control access (lazy, remote, cached, protected) with the same interface |
| **Facade** | Many objects | Provide one simple interface to a complex subsystem |
| **Composite** | Many objects (tree) | Treat single objects and groups uniformly |
| **Bridge** | Two hierarchies | Separate an abstraction from its implementation so both vary independently |
| **Flyweight** | Shared state | Save memory by sharing common immutable data between many objects |

Prerequisites: [composition and delegation](../composition-design/README.md).

## 2. Adapter

**Problem:** you have a class that does what you need but its interface does not match what your code expects (a third-party library, legacy code). **Solution:** write a thin wrapper that translates calls.

```python
class LegacyTemperatureSensor:                       # cannot change: third-party
    def read_fahrenheit(self):
        return 98.6

class CelsiusSensor:                                 # the interface our app expects
    def read(self): raise NotImplementedError

class SensorAdapter(CelsiusSensor):
    def __init__(self, legacy):
        self._legacy = legacy                        # object adapter: composition (preferred)
    def read(self):
        return round((self._legacy.read_fahrenheit() - 32) * 5 / 9, 1)

def alert_if_hot(sensor: CelsiusSensor, limit=37.0):
    return "ALERT" if sensor.read() > limit else "ok"

print(SensorAdapter(LegacyTemperatureSensor()).read(), alert_if_hot(SensorAdapter(LegacyTemperatureSensor())))
# 37.0 ok
```

Two flavors: **object adapter** (holds the adaptee, shown above) and **class adapter** (inherits from the adaptee; needs multiple inheritance). Prefer the object adapter. Adapters are also how you put an **anti-corruption layer** between your domain and an external API: your code speaks your vocabulary, the adapter translates.

**Real examples:** `io.TextIOWrapper` adapts a byte stream to a text stream; a payment-gateway wrapper per vendor; `requests` adapters; ORM database drivers (DB-API as the common interface).

## 3. Decorator

**Intent:** attach additional responsibilities to an object **dynamically**, as an alternative to subclassing. A decorator has the **same interface** as the thing it wraps and delegates to it, adding behavior before or after.

### Object (GoF) version

```python
class Coffee:
    def cost(self): return 2.0
    def description(self): return "coffee"

class MilkDecorator:
    def __init__(self, inner): self.inner = inner
    def cost(self): return self.inner.cost() + 0.5
    def description(self): return self.inner.description() + " + milk"

class SugarDecorator:
    def __init__(self, inner): self.inner = inner
    def cost(self): return self.inner.cost() + 0.2
    def description(self): return self.inner.description() + " + sugar"

order = SugarDecorator(MilkDecorator(Coffee()))     # combine freely, in any order
print(order.description(), order.cost())            # coffee + milk + sugar 2.7
```

Without the pattern you would need `CoffeeWithMilk`, `CoffeeWithMilkAndSugar`, ... (the hierarchy explosion).

### Python's function decorators

Python's `@decorator` syntax is the same idea applied to **functions** (and classes): wrap a callable to add behavior.

```python
import functools, time

def timed(fn):
    @functools.wraps(fn)                             # keep name/docstring of the wrapped function
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        wrapper.last_duration = time.perf_counter() - start
        return result
    return wrapper

def retry(times):                                    # a decorator with arguments = a decorator factory
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return fn(*args, **kwargs)
                except ValueError:
                    if attempt == times:
                        raise
        return wrapper
    return deco

state = {"calls": 0}

@timed
@retry(3)
def flaky():
    state["calls"] += 1
    if state["calls"] < 3:
        raise ValueError("transient")
    return "done"

print(flaky(), state["calls"], flaky.__name__)       # done 3 flaky
```

Decorators stack bottom-up (`@retry` applied first, `@timed` outside it). Standard-library decorators: `functools.lru_cache`, `functools.wraps`, `@property`, `@staticmethod`, `@classmethod`, `@contextmanager`, `@dataclass`, `@singledispatch`.

Class decorators work too: `@dataclass`, or a registry decorator that returns the class unchanged after recording it.

## 4. Proxy

**Intent:** provide a **stand-in** for another object to control access to it. The proxy has the same interface as the real subject, so clients cannot tell the difference.

| Kind | Purpose |
|------|---------|
| **Virtual (lazy) proxy** | Delay creating an expensive object until first use |
| **Protection proxy** | Check permissions before forwarding |
| **Caching proxy** | Remember results |
| **Remote proxy** | Local stand-in for an object elsewhere (RPC stubs) |
| **Logging / smart-reference proxy** | Count, log, or manage lifetime |

```python
class Image:
    def __init__(self, path):
        self.path = path
        print(f"loading {path} from disk (slow)")
    def draw(self): return f"drawing {self.path}"

class LazyImage:                                     # virtual proxy
    def __init__(self, path):
        self.path, self._real = path, None
    def draw(self):
        if self._real is None:
            self._real = Image(self.path)            # created only when first needed
        return self._real.draw()

class SecureImage:                                   # protection proxy
    def __init__(self, image, user_roles):
        self.image, self.roles = image, user_roles
    def draw(self):
        if "viewer" not in self.roles:
            raise PermissionError("not allowed")
        return self.image.draw()

gallery = [LazyImage(f"{i}.png") for i in range(1000)]    # instant: nothing loaded yet
print(gallery[7].draw())                                  # loading 7.png from disk (slow) / drawing 7.png
print(gallery[7].draw())                                  # drawing 7.png (already loaded)
try:
    SecureImage(gallery[1], ["guest"]).draw()
except PermissionError as e:
    print("denied:", e)                                   # denied: not allowed
```

Dynamic proxy with `__getattr__` forwards everything automatically (remember dunders are not forwarded):

```python
class CountingProxy:
    def __init__(self, target):
        self._target, self.calls = target, {}
    def __getattr__(self, name):
        attr = getattr(self._target, name)
        if callable(attr):
            def wrapper(*a, **kw):
                self.calls[name] = self.calls.get(name, 0) + 1
                return attr(*a, **kw)
            return wrapper
        return attr

p = CountingProxy([3, 1, 2])
p.sort(); p.append(9); p.append(10)
print(p.calls)                                       # {'sort': 1, 'append': 2}
```

**Decorator vs Proxy:** structurally identical; intent differs. A decorator **adds features** that the client composes; a proxy **controls access** and usually manages the real object's lifecycle itself.

## 5. Facade

**Intent:** a simple, unified interface to a **complex subsystem**. The facade does not hide the subsystem (power users can still use it); it offers an easy path for common tasks and reduces coupling to many classes.

```python
class VideoDecoder:
    def decode(self, f): return f"frames({f})"
class AudioExtractor:
    def extract(self, f): return f"audio({f})"
class Compressor:
    def compress(self, data, quality): return f"{data}@{quality}"
class Muxer:
    def mux(self, v, a): return f"{v}+{a}"

class VideoConverter:                                # the facade
    def convert(self, filename, quality="high"):
        video = Compressor().compress(VideoDecoder().decode(filename), quality)
        audio = AudioExtractor().extract(filename)
        return Muxer().mux(video, audio)

print(VideoConverter().convert("movie.avi"))         # frames(movie.avi)@high+audio(movie.avi)
```

**Real examples:** `requests.get(url)` (hides sessions, adapters, connection pools, encoding), `subprocess.run`, `shutil.copytree`, `os.makedirs`, a service-layer class that coordinates repositories, emailers and payment gateways for one use case. Facades also form **layer boundaries** in an application.

## 6. Composite

**Intent:** compose objects into **tree structures** and let clients treat individual objects (**leaves**) and compositions (**composites**) **uniformly**.

```python
from abc import ABC, abstractmethod

class FsNode(ABC):
    def __init__(self, name): self.name = name
    @abstractmethod
    def size(self): ...
    @abstractmethod
    def show(self, indent=0): ...

class File(FsNode):
    def __init__(self, name, size): super().__init__(name); self._size = size
    def size(self): return self._size
    def show(self, indent=0): return " " * indent + f"{self.name} ({self._size})"

class Folder(FsNode):
    def __init__(self, name): super().__init__(name); self.children = []
    def add(self, node): self.children.append(node); return self
    def size(self): return sum(c.size() for c in self.children)     # recursion over the tree
    def show(self, indent=0):
        lines = [" " * indent + f"{self.name}/ ({self.size()})"]
        lines += [c.show(indent + 2) for c in self.children]
        return "\n".join(lines)

root = Folder("root").add(File("a.txt", 10)).add(Folder("src").add(File("main.py", 40)).add(File("util.py", 25)))
print(root.show())
# root/ (75)
#   a.txt (10)
#   src/ (65)
#     main.py (40)
#     util.py (25)
print(root.size())            # 75
```

Clients call `size()` on a file or a whole folder tree identically. Typical uses: file systems, GUI widget trees, document object models (HTML DOM), organization charts, expression trees, menus with sub-menus, product bundles with a total price.

## 7. Bridge

**Intent:** decouple an **abstraction** from its **implementation** so the two hierarchies can vary independently, avoiding an M x N class explosion.

```python
from abc import ABC, abstractmethod

class Renderer(ABC):                                 # implementation hierarchy
    @abstractmethod
    def circle(self, r): ...
class SvgRenderer(Renderer):
    def circle(self, r): return f'<circle r="{r}"/>'
class AsciiRenderer(Renderer):
    def circle(self, r): return f"(circle of radius {r})"

class Shape:                                         # abstraction hierarchy, holds an implementation
    def __init__(self, renderer): self.renderer = renderer
class Circle(Shape):
    def __init__(self, renderer, r): super().__init__(renderer); self.r = r
    def draw(self): return self.renderer.circle(self.r)
class BigCircle(Circle):
    def __init__(self, renderer, r): super().__init__(renderer, r * 10)

for renderer in (SvgRenderer(), AsciiRenderer()):
    print(Circle(renderer, 2).draw(), "|", BigCircle(renderer, 2).draw())
# <circle r="2"/> | <circle r="20"/>
# (circle of radius 2) | (circle of radius 20)
```

Shapes x renderers would be 2 x 2 classes without a bridge; with it you add a `Square` or a `CanvasRenderer` independently. Bridge is composition applied at design time: "this class **has** an implementation object". Real examples: database access layers (`Repository` abstraction over different drivers), device drivers, `logging` (Logger over Handlers), UI frameworks (widget over platform backend).

## 8. Flyweight

**Intent:** support **huge numbers of similar objects** by sharing the **intrinsic (immutable, common) state** and passing the **extrinsic (per-use) state** from outside.

```python
class GlyphStyle:                                    # intrinsic state: shared and immutable
    __slots__ = ("font", "size", "bold")
    def __init__(self, font, size, bold):
        self.font, self.size, self.bold = font, size, bold

class StyleFactory:
    _cache = {}
    @classmethod
    def get(cls, font, size, bold):
        key = (font, size, bold)
        if key not in cls._cache:
            cls._cache[key] = GlyphStyle(font, size, bold)
        return cls._cache[key]

text = [("a", StyleFactory.get("Arial", 12, False)) for _ in range(100_000)]   # extrinsic: the character; shared: the style
print(len({id(style) for _, style in text}), len(StyleFactory._cache))         # 1 1
a, b = StyleFactory.get("Arial", 12, False), StyleFactory.get("Arial", 12, False)
print(a is b)                                        # True
```

100,000 characters share **one** style object. Python itself uses flyweights: small integers (-5 to 256), interned strings (`sys.intern`), `None`/`True`/`False`. `functools.lru_cache` on a constructor function and `__slots__` are practical tools. Use when you have very many objects, much of whose state is identical, and memory is a measured problem.

## 9. Choosing among structural patterns

| Situation | Pattern |
|-----------|---------|
| Interface mismatch with a library or legacy code | Adapter |
| Add behavior (logging, caching, retry, auth) without changing a class | Decorator |
| Control access / lazy loading / remote stand-in | Proxy |
| Simplify a subsystem with many parts | Facade |
| Tree where leaves and groups behave alike | Composite |
| Two dimensions of variation | Bridge |
| Millions of near-identical objects | Flyweight |

## 10. Two real-world examples

### Example 1: Wrapping a third-party API (Adapter + Facade + Decorator + Proxy)
A company integrates three shipping carriers with different APIs. An **Adapter** per carrier exposes one `ShippingProvider` interface (`quote`, `book`, `track`). A **Facade** (`ShippingService.ship(order)`) picks a carrier, books, and stores tracking. **Decorators** add cross-cutting features to any provider: `RetryingProvider`, `LoggingProvider`, `CachingProvider` (quotes cached for 10 minutes). A **Proxy** guards the sandbox/production credentials. The business code only sees `ShippingService`.

### Example 2: A document editor
A document is a **Composite** tree: Document -> Pages -> Paragraphs -> Runs of text; `render()` or `word_count()` work uniformly on any node. Character formatting uses **Flyweight** objects (one `Style` shared by thousands of characters). Images use a **Virtual Proxy** (placeholder until scrolled into view). A save command wraps writers in **Decorators** (compression, then encryption). The export subsystem is hidden behind a **Facade** (`doc.export("pdf")`).

## 11. Tips, tricks and pitfalls

- Identify the **intent** (translate / add / control / simplify / uniform tree / two axes / share) before choosing the pattern.
- Use `functools.wraps` in every function decorator so names and docstrings survive.
- Decorators must keep the wrapped object's interface (and signatures) intact.
- Prefer object adapters (composition) over class adapters.
- Forward dunders explicitly in `__getattr__` proxies; they are not looked up through `__getattr__`.
- A facade should not become a god class; keep it a thin coordination layer.
- Composite: decide who owns child management methods (`add`/`remove`) and keep leaf behavior safe.
- Flyweight shared objects **must be immutable**.
- Do not stack many decorators blindly: ordering matters (cache then retry is not the same as retry then cache).

## 12. Check yourself

1. How do Adapter, Decorator and Proxy differ, given that all wrap one object?
2. What does `@functools.wraps` do and why use it?
3. Write the structure of a decorator with arguments.
4. When is Facade better than exposing the subsystem directly? What is its main risk?
5. What does Composite achieve and how is `size()` implemented over a tree?
6. What problem does Bridge solve? Give an M x N example.
7. Which state does Flyweight share and what must be true of it?
8. Name three Python built-ins or standard-library features that implement these patterns.

<details>
<summary>Answers</summary>

1. Adapter changes the interface to match what the client expects; Decorator keeps the interface and adds behavior; Proxy keeps the interface and controls access (lazy, protected, cached, remote).
2. It copies metadata (`__name__`, `__doc__`, `__wrapped__`) from the wrapped function to the wrapper so introspection, debugging and documentation still work.
3. An outer function takes the arguments and returns the real decorator; that decorator takes `fn` and returns `wrapper` (using `@functools.wraps(fn)`); three nested levels: `def retry(n): def deco(fn): def wrapper(*a, **kw): ...`.
4. When most callers only need a few common operations of a complex subsystem: it simplifies use and reduces coupling. Risk: it grows into a god class or hides necessary flexibility.
5. It lets clients treat leaves and groups the same through a common interface. For a folder, `size()` sums the `size()` of its children recursively; for a file it returns its own size.
6. It prevents an M x N explosion of classes when an abstraction (shapes) and its implementation (renderers) vary independently: shapes hold a renderer and delegate to it.
7. Shared intrinsic state (font, color, shared data); it must be immutable. Extrinsic state (position, the character) is supplied per use.
8. `functools.lru_cache`/`wraps`/`@property` (Decorator), `io.TextIOWrapper` (Adapter), `requests.get`/`shutil.copytree` (Facade), `pathlib` or `ast` trees (Composite), interned strings/small ints (Flyweight), `weakref.proxy` (Proxy).

</details>

[Exercises](exercises.md) · [Summary](summary.md)
