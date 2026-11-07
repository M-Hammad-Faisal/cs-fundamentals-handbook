# Proxy Pattern

**Family:** structural · **Also called:** surrogate, stand-in · **How often you will use it:** often (lazy loading, caching, access control) · **Difficulty:** medium

## 1. In plain words

A **Proxy** is a **stand-in** for another object. It has the **same interface**, so callers cannot tell the difference, but it **controls access** to the real object: it may delay creating it, check permissions, cache results, log calls, or talk to a remote machine.

Analogy: a **receptionist** (or a bank cheque). You deal with the receptionist; they decide whether and when to bring in the manager, and may answer simple questions themselves.

## 2. The problem

The real object is expensive, remote, sensitive, or needs extra handling every time, and you do not want every caller to deal with that:

```python
gallery = [Image(f"{i}.png") for i in range(1000)]   # loads 1000 big files from disk, even if you only show 3
```

## 3. The solution

```text
Client ──► Subject interface ◄──┬── RealSubject (does the work)
                                └── Proxy ──holds──► RealSubject
                                    (checks / delays / caches, then forwards)
```

## 4. Step by step

### Virtual proxy: lazy creation

```python
class Image:                                           # the real subject
    def __init__(self, path):
        self.path = path
        print(f"loading {path} from disk (slow)")
    def draw(self):
        return f"drawing {self.path}"

class LazyImage:                                       # the proxy: same interface (draw)
    def __init__(self, path):
        self.path, self._real = path, None
    def draw(self):
        if self._real is None:
            self._real = Image(self.path)              # created only on first use
        return self._real.draw()

gallery = [LazyImage(f"{i}.png") for i in range(1000)]   # instant: nothing loaded yet
print(gallery[7].draw())     # loading 7.png from disk (slow) / drawing 7.png
print(gallery[7].draw())     # drawing 7.png  (already loaded; no second load)
```

### Protection proxy: access control

```python
class SecureImage:
    def __init__(self, image, roles):
        self.image, self.roles = image, roles
    def draw(self):
        if "viewer" not in self.roles:
            raise PermissionError("not allowed")
        return self.image.draw()

print(SecureImage(gallery[1], ["viewer"]).draw())
try:
    SecureImage(gallery[1], ["guest"]).draw()
except PermissionError as e:
    print("denied:", e)                                 # denied: not allowed
```

### Caching proxy

```python
class WeatherService:
    def forecast(self, city):
        return f"sunny in {city}"

class CachingWeather:
    def __init__(self, real):
        self.real, self.cache, self.real_calls = real, {}, 0
    def forecast(self, city):
        if city not in self.cache:
            self.real_calls += 1
            self.cache[city] = self.real.forecast(city)
        return self.cache[city]

w = CachingWeather(WeatherService())
w.forecast("Lahore"); w.forecast("Lahore"); w.forecast("Karachi")
print(w.real_calls)                                     # 2
```

### A generic logging/counting proxy with `__getattr__`

```python
class CountingProxy:
    def __init__(self, target):
        self._target, self.calls = target, {}
    def __getattr__(self, name):                        # called for names the proxy itself lacks
        attr = getattr(self._target, name)
        if callable(attr):
            def wrapper(*a, **kw):
                self.calls[name] = self.calls.get(name, 0) + 1
                return attr(*a, **kw)
            return wrapper
        return attr

p = CountingProxy([3, 1, 2])
p.sort(); p.append(9); p.append(10)
print(p.calls)                                          # {'sort': 1, 'append': 2}
```

Note: special methods such as `len(p)` are **not** forwarded by `__getattr__`; define them explicitly (`__len__`) if needed.

## 5. The Pythonic way

- `@property` and `functools.cached_property` are lazy proxies for attributes.
- `weakref.proxy(obj)` is a built-in proxy that does not keep `obj` alive.
- `unittest.mock.Mock`/`MagicMock` are recording proxies.
- ORMs return **lazy** proxies: `user.orders` hits the database only when you iterate it.
- Remote procedure call stubs (gRPC, XML-RPC clients) are remote proxies.

```python
from functools import cached_property

class Report:
    @cached_property
    def data(self):                                     # computed on first access only
        print("computing...")
        return [1, 2, 3]

r = Report(); r.data; r.data                            # prints "computing..." once
```

## 6. When to use it (and when not to)

| Kind | Use it to |
|------|-----------|
| **Virtual** | Delay creating something expensive until needed |
| **Protection** | Check permissions before forwarding |
| **Caching** | Remember results of expensive calls |
| **Remote** | Look like a local object while calling another machine |
| **Logging / smart reference** | Count, log or manage the lifetime of calls |

**Skip it when** simply calling the real object is fine or one `if` in the caller is clearer.

## 7. Pros and cons

| Pros | Cons |
|------|------|
| Add control without changing the real class or its clients | An extra layer; slight overhead |
| Lazy loading saves startup time and memory | Responses may be delayed by the proxy's own work |
| Works transparently (same interface) | Debugging "which object am I really talking to?" |

## 8. Related patterns

- [Decorator](decorator.md): same structure; *adds features* (the client chooses). Proxy *controls access* (and often creates the real object itself).
- [Adapter](adapter.md): changes the interface; Proxy keeps it.
- [Facade](facade.md): new simplified interface; Proxy keeps the original.

## 9. Two real-world examples

**Example 1: ORM lazy loading.** `order.customer` does not query the database until you read it; the ORM returns a proxy object that fetches the row on first access. You get the same attribute interface but pay only when needed.

**Example 2: API gateway / client SDK.** `payment_api.charge(...)` looks like a local call but a proxy serializes the request, sends it over the network, retries on timeouts and checks credentials: a remote proxy plus protection and logging.

## 10. Common mistakes

- Forgetting to forward some methods (the proxy no longer matches the interface).
- Assuming `__getattr__` forwards dunder methods (it does not).
- Caching mutable results that callers then modify.
- Using a proxy where a [decorator](decorator.md) was intended (confused intent makes code hard to read).

## 11. Practice

1. Build a lazy proxy for a `Database` that connects only when the first `query` runs.
2. Add a rate-limit proxy that allows at most 3 calls, then raises.
3. Make the counting proxy also support `len()`.

<details>
<summary>Solutions</summary>

**1.**
```python
class Database:
    def __init__(self): print("connecting...")
    def query(self, sql): return f"result of {sql}"
class LazyDatabase:
    def __init__(self): self._db = None
    def query(self, sql):
        if self._db is None:
            self._db = Database()
        return self._db.query(sql)
db = LazyDatabase()                                     # no connection yet
print(db.query("SELECT 1"))                             # connecting... / result of SELECT 1
```

**2.**
```python
class RateLimited:
    def __init__(self, target, limit): self.target, self.limit, self.n = target, limit, 0
    def query(self, sql):
        if self.n >= self.limit: raise RuntimeError("rate limit exceeded")
        self.n += 1
        return self.target.query(sql)
rl = RateLimited(LazyDatabase(), 3)
for i in range(3): rl.query("x")
try: rl.query("x")
except RuntimeError as e: print(e)
```

**3.**
```python
class CountingProxy2(CountingProxy):
    def __len__(self): return len(self._target)
print(len(CountingProxy2([1, 2, 3])))                   # 3
```

</details>

## 12. Check yourself

1. What stays the same between a proxy and the real object?
2. Name four kinds of proxy.
3. How do Proxy and Decorator differ if they look alike?
4. Why does `len(proxy)` fail with a pure `__getattr__` proxy?

<details>
<summary>Answers</summary>

1. The interface.
2. Virtual (lazy), protection, caching, remote (also logging/smart reference).
3. Intent: a proxy controls access to the object (and usually manages its lifecycle); a decorator adds behavior that the client chooses to stack.
4. Python looks up special methods on the type, not through instance `__getattr__`, so `__len__` must be defined on the proxy class.

</details>

## More examples

Runnable script (added to your companion repository with this lesson): [`structuralPattern/proxyPattern.py`](https://github.com/M-Hammad-Faisal/design-patterns-python/blob/master/structuralPattern/proxyPattern.py)

[Family overview](README.md) · [All patterns](../README.md)
