# Creational Patterns: Exercises

1. Make a thread-safe `Logger` Singleton (via module-level instance) and show that two imports give the same object. Then explain how you would test code that uses it.
2. Write a simple factory `shape_from_dict({"type": "circle", "r": 2})` using a registry, so a new shape is added by decoration (`@register("triangle")`) without editing the factory.
3. Implement an Abstract Factory for `Windows`/`Mac` GUI components (`Button`, `Scrollbar`) and a function that builds a "settings panel" from any factory. Show that you cannot mix families.
4. Build an `HttpRequestBuilder` with `url`, `method`, `header`, `query`, `json_body` and `build()` that validates (URL required, no body on GET) and returns an immutable object (frozen dataclass).
5. Use `dataclasses.replace` as a Prototype to create three `ServerConfig` variants from a base config. Show deep vs shallow copy with a list field.
6. Implement a connection pool with a maximum of 3, `acquire()`/`release()`, a timeout error when exhausted, and a test with 5 threads.
7. Replace this constructor with a better design (name two options):
   `Report(title, rows, header=True, footer=True, landscape=False, font="Arial", size=11, color="black", border=1, margins=(1,1,1,1))`
8. Why would a Singleton for database connections hurt tests, and how do you restructure it?
9. Identify the pattern: (a) `logging.getLogger("a") is logging.getLogger("a")`, (b) `requests.Session().mount(...)` (c) `copy.deepcopy(template)`, (d) `SELECT` built by chaining `.where().order_by()`.

<details>
<summary>Solutions</summary>

**1.**
```python
# logger_module.py   (the module IS the singleton)
import threading
class _Logger:
    def __init__(self): self.lines, self._lock = [], threading.Lock()
    def log(self, msg):
        with self._lock: self.lines.append(msg)
logger = _Logger()
# elsewhere:  from logger_module import logger
import sys, types
m = types.ModuleType("logger_module"); m.logger = _Logger(); sys.modules["logger_module"] = m
from logger_module import logger as a
from logger_module import logger as b
print(a is b)
```
For tests: have functions accept a `logger` parameter (default to the module instance) so tests pass a fake, or reset `logger.lines` in a fixture.

**2.**
```python
import math
SHAPES = {}
def register(name):
    def deco(cls): SHAPES[name] = cls; return cls
    return deco
@register("circle")
class Circle:
    def __init__(self, r): self.r = r
    def area(self): return math.pi * self.r ** 2
@register("rect")
class Rect:
    def __init__(self, w, h): self.w, self.h = w, h
    def area(self): return self.w * self.h
def shape_from_dict(d):
    d = dict(d); kind = d.pop("type")
    return SHAPES[kind](**d)
@register("square")                                       # added later, factory untouched
class Square(Rect):
    def __init__(self, side): super().__init__(side, side)
print(round(shape_from_dict({"type": "circle", "r": 2}).area(), 2), shape_from_dict({"type": "square", "side": 3}).area())
```

**3.**
```python
from abc import ABC, abstractmethod
class GuiFactory(ABC):
    @abstractmethod
    def button(self): ...
    @abstractmethod
    def scrollbar(self): ...
class WinFactory(GuiFactory):
    def button(self): return "win-button"
    def scrollbar(self): return "win-scrollbar"
class MacFactory(GuiFactory):
    def button(self): return "mac-button"
    def scrollbar(self): return "mac-scrollbar"
def settings_panel(f: GuiFactory): return [f.button(), f.scrollbar()]
print(settings_panel(WinFactory()), settings_panel(MacFactory()))
```
The panel receives one factory, so every component comes from the same family.

**4.**
```python
from dataclasses import dataclass, field
@dataclass(frozen=True)
class HttpRequest:
    url: str; method: str; headers: tuple; query: tuple; body: str | None
class HttpRequestBuilder:
    def __init__(self): self._url = None; self._method = "GET"; self._h = {}; self._q = {}; self._body = None
    def url(self, u): self._url = u; return self
    def method(self, m): self._method = m.upper(); return self
    def header(self, k, v): self._h[k] = v; return self
    def query(self, k, v): self._q[k] = v; return self
    def json_body(self, s): self._body = s; return self
    def build(self):
        if not self._url: raise ValueError("url is required")
        if self._method == "GET" and self._body is not None: raise ValueError("GET cannot have a body")
        return HttpRequest(self._url, self._method, tuple(self._h.items()), tuple(self._q.items()), self._body)
req = HttpRequestBuilder().url("https://x.test/a").method("post").header("A", "1").json_body('{"k":1}').build()
print(req.method, req.headers)
try: HttpRequestBuilder().build()
except ValueError as e: print(e)
```

**5.**
```python
from dataclasses import dataclass, field, replace
import copy
@dataclass
class ServerConfig:
    host: str; port: int; tags: list = field(default_factory=list)
base = ServerConfig("0.0.0.0", 80, ["web"])
dev = replace(base, port=8080); prod = replace(base, host="prod.example"); staging = copy.deepcopy(base); staging.tags.append("stg")
print(dev.port, prod.host, base.tags, staging.tags)
dev.tags.append("dev")                       # replace() is SHALLOW: tags list is shared with base
print(base.tags)                             # ['web', 'dev']  (surprise); use deepcopy for independent lists
```

**6.**
```python
import threading, queue
class PoolExhausted(Exception): pass
class Pool:
    def __init__(self, size):
        self._q = queue.Queue()
        for i in range(size): self._q.put(f"conn{i}")
    def acquire(self, timeout=0.5):
        try: return self._q.get(timeout=timeout)
        except queue.Empty: raise PoolExhausted("no connection available") from None
    def release(self, c): self._q.put(c)
pool, out = Pool(3), []
import time
def worker(i):
    try:
        c = pool.acquire(timeout=0.2)
    except PoolExhausted:
        out.append("exhausted"); return
    time.sleep(0.5); out.append(c); pool.release(c)
ts = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
[t.start() for t in ts]; [t.join() for t in ts]
print(sorted(out))     # three connections used, two threads time out
```

**7.** Option 1: group related options into value objects (`PageStyle(font, size, color, border, margins, landscape)`) and pass `Report(title, rows, style=PageStyle(), header=True, footer=True)`. Option 2: a `ReportBuilder` with fluent methods or a frozen dataclass with keyword-only arguments (`def __init__(self, title, rows, *, header=True, ...)`).

**8.** A global connection object leaks state across tests, cannot be swapped for an in-memory fake, and hides the dependency. Create the connection (or pool) once in `main()` and inject it into repositories; tests inject a fake or a per-test database.

**9.** (a) Factory with cache (Singleton-like registry), (b) adapter/strategy composition (transport adapters plugged into a session), (c) Prototype, (d) Builder (fluent).

</details>

[Lesson](README.md) · [Summary](summary.md)
