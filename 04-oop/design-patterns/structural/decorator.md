# Decorator Pattern

**Family:** structural · **Also called:** wrapper · **How often you will use it:** very often (Python's `@decorator` syntax) · **Difficulty:** easy to medium

## 1. In plain words

A **Decorator** wraps an object (or function) to **add behavior**, while keeping the same interface, so the wrapped thing can be used exactly as before. You can stack several.

Analogy: **dressing for the weather**. You are still you, but you add a jacket, then a raincoat. Each layer adds something and can be added or removed independently.

## 2. The problem

Adding every combination of features by subclassing explodes the number of classes:

```python
class Coffee: ...
class CoffeeWithMilk(Coffee): ...
class CoffeeWithSugar(Coffee): ...
class CoffeeWithMilkAndSugar(Coffee): ...     # and then caramel, soy, ...: 2^n classes
```

## 3. The solution

```text
Client ──► Component interface
               ▲
     ┌─────────┴───────────┐
 Concrete Component    Decorator ──wraps──► Component
                       ├─ MilkDecorator
                       └─ SugarDecorator
```

Each decorator has the same interface as what it wraps, calls the wrapped object, and adds its own behavior before or after.

## 4. Step by step

### The object version (the original GoF form)

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

order = SugarDecorator(MilkDecorator(Coffee()))      # combine freely, any order, any number
print(order.description(), order.cost())             # coffee + milk + sugar 2.7
```

### Notification channels (stacking behavior)

```python
class Notifier:
    def send(self, msg):
        return [f"email: {msg}"]

class NotifierDecorator(Notifier):
    def __init__(self, inner):
        self.inner = inner

class SmsDecorator(NotifierDecorator):
    def send(self, msg):
        return self.inner.send(msg) + [f"sms: {msg}"]

class SlackDecorator(NotifierDecorator):
    def send(self, msg):
        return self.inner.send(msg) + [f"slack: {msg}"]

print(SlackDecorator(SmsDecorator(Notifier())).send("server down"))
# ['email: server down', 'sms: server down', 'slack: server down']
```

### Python's function decorators (the same idea for functions)

```python
import functools, time

def timed(fn):
    @functools.wraps(fn)                              # keeps the original name and docstring
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        wrapper.last_duration = time.perf_counter() - start
        return result
    return wrapper

def retry(times):                                     # decorator WITH arguments = a factory returning a decorator
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return fn(*args, **kwargs)
                except ValueError:
                    if attempt == times:
                        raise
        return wrapper
    return decorator

state = {"calls": 0}

@timed
@retry(3)
def flaky():
    state["calls"] += 1
    if state["calls"] < 3:
        raise ValueError("temporary")
    return "done"

print(flaky(), state["calls"], flaky.__name__)         # done 3 flaky
```

`@timed` above `@retry(3)` means `flaky = timed(retry(3)(flaky))`: decorators apply bottom-up, so `retry` is the inner layer.

### A decorator with state: counting calls

```python
def count_calls(fn):
    @functools.wraps(fn)
    def wrapper(*a, **kw):
        wrapper.calls += 1
        return fn(*a, **kw)
    wrapper.calls = 0
    return wrapper

@count_calls
def hello(): return "hi"

hello(); hello()
print(hello.calls)                                     # 2
```

## 5. The Pythonic way

- `@decorator` syntax is the pattern built into the language: `functools.lru_cache`, `functools.wraps`, `@property`, `@staticmethod`, `@classmethod`, `@contextmanager`, `@dataclass`, `@singledispatch`.
- **Class decorators** modify or register a class (`@dataclass`).
- Always use `functools.wraps` so names and docstrings survive.
- For typed code, preserve signatures with `ParamSpec` (see [type hints](../../../08-modern-python/typing-hints/README.md)).

```python
@functools.lru_cache(maxsize=None)
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)
print(fib(60), fib.cache_info().hits > 0)               # 1548008755920 True
```

## 6. When to use it (and when not to)

**Use it when** you want to add responsibilities dynamically and combine them (logging, caching, retries, authentication, validation, encryption, compression); when subclassing would explode into too many classes; when behavior is cross-cutting.

**Skip it when** the behavior is core to the class (put it inside), or the wrapper order becomes confusing.

## 7. Pros and cons

| Pros | Cons |
|------|------|
| Add features without changing existing code (Open/Closed) | Many small objects/wrappers; stack traces get deeper |
| Combine behaviors freely at runtime | Order matters and can be subtle |
| Avoids class explosion | Identity changes (the wrapped object is not the original) |

## 8. Related patterns

- [Adapter](adapter.md): changes the interface; Decorator keeps it.
- [Proxy](proxy.md): same shape; intent is *controlling access*, not adding features.
- [Composite](composite.md): also recursive wrapping, but for trees.
- [Strategy](../behavioral/strategy.md) changes the guts of an object; Decorator changes its skin.
- [Chain of Responsibility](../behavioral/chain-of-responsibility.md): decorators also form a chain.

## 9. Two real-world examples

**Example 1: Web framework decorators.** `@login_required` before a Django view wraps it: if the user is not logged in, redirect; otherwise call the view. `@cache_page(60)` caches the response. Stack them in any order to compose behavior.

**Example 2: I/O streams.** `io.BufferedReader(io.FileIO(path))` and `gzip.GzipFile(fileobj=...)` wrap a lower-level stream and add buffering or compression while exposing the same `read()` interface.

## 10. Common mistakes

- Forgetting `functools.wraps` (loses `__name__`, breaks debugging and introspection).
- Wrong stacking order (cache then retry is not the same as retry then cache).
- Decorators that change the function's signature or return type unexpectedly.
- Swallowing exceptions inside a decorator.

## 11. Practice

1. Write `@cache_with_ttl(seconds)` with an injectable clock so expiry is testable.
2. Add a `@validate_positive` decorator that raises `ValueError` if any positive-number argument is `<= 0`.
3. Build a `Text` decorator chain: `Bold(Italic(PlainText("hi")))` giving `<b><i>hi</i></b>`.

<details>
<summary>Solutions</summary>

**1.**
```python
def cache_with_ttl(seconds, clock=time.monotonic):
    def decorator(fn):
        store = {}
        @functools.wraps(fn)
        def wrapper(*args):
            now = clock()
            if args in store and now - store[args][1] < seconds:
                return store[args][0]
            value = fn(*args)
            store[args] = (value, now)
            return value
        return wrapper
    return decorator

t, calls = [0], []
@cache_with_ttl(10, clock=lambda: t[0])
def slow(x):
    calls.append(x)
    return x * 2
slow(2); slow(2); t[0] = 11; slow(2)
print(calls)                                            # [2, 2]
```

**2.**
```python
def validate_positive(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        for v in list(args) + list(kwargs.values()):
            if isinstance(v, (int, float)) and v <= 0:
                raise ValueError("arguments must be positive")
        return fn(*args, **kwargs)
    return wrapper

@validate_positive
def area(w, h): return w * h
print(area(2, 3))
try: area(-1, 3)
except ValueError as e: print(e)
```

**3.**
```python
class PlainText:
    def __init__(self, s): self.s = s
    def render(self): return self.s
class Bold:
    def __init__(self, inner): self.inner = inner
    def render(self): return f"<b>{self.inner.render()}</b>"
class Italic:
    def __init__(self, inner): self.inner = inner
    def render(self): return f"<i>{self.inner.render()}</i>"
print(Bold(Italic(PlainText("hi"))).render())          # <b><i>hi</i></b>
```

</details>

## 12. Check yourself

1. What does a decorator keep the same, and what does it add?
2. What does `@functools.wraps` do?
3. In what order do stacked `@a @b def f` apply?
4. Decorator versus Proxy versus Adapter?
5. Why does a decorator with arguments need three nested functions?

<details>
<summary>Answers</summary>

1. It keeps the interface and adds behavior before or after delegating to the wrapped object.
2. Copies the wrapped function's name, docstring and attributes onto the wrapper so introspection and debugging still work.
3. Bottom-up: `f = a(b(f))`; `b` is applied first (inner), `a` outermost.
4. Decorator adds features (same interface); Proxy controls access (same interface); Adapter changes the interface.
5. The outer function takes the decorator's arguments, the middle takes the function, the inner is the wrapper that runs on each call.

</details>

## More examples

Runnable script from your companion repository: [`structuralPattern/decoratorPattern.py`](https://github.com/M-Hammad-Faisal/design-patterns-python/blob/master/structuralPattern/decoratorPattern.py)

[Family overview](README.md) · [All patterns](../README.md)
