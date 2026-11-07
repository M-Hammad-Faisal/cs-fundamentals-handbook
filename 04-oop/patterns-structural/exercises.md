# Structural Patterns: Exercises

1. **Adapter:** adapt a class `LegacyLogger.write_line(level_int, text)` to the interface `log(level: str, message: str)` that your app uses (map `"DEBUG"` to 0, `"INFO"` to 1, `"ERROR"` to 2).
2. **Decorator (function):** write `@cache_with_ttl(seconds)` that caches results per arguments and expires them. Inject the clock so you can test expiry.
3. **Decorator (object):** build a `Notifier` chain: an email notifier, optionally wrapped by SMS and Slack decorators, so `send()` notifies on every configured channel.
4. **Proxy:** write a caching proxy for a slow `WeatherService.forecast(city)` that counts how many real calls were made.
5. **Facade:** create a `HomeTheater` facade over `Amplifier`, `Projector`, `Lights`, `Player` with `watch_movie(title)` and `end_movie()`, and verify the call order.
6. **Composite:** model a menu with items and submenus; implement `total_price()`, `print_menu()` and `find(name)` that work on any node.
7. **Bridge:** separate message types (`Alert`, `Report`) from delivery channels (`Email`, `Sms`) so every combination works without extra classes.
8. **Flyweight:** build a forest of 50,000 trees where the species data is shared and only `(x, y)` is per tree; verify sharing with `id`.
9. Which pattern is each: (a) `functools.lru_cache`, (b) `shutil.copytree`, (c) a class holding a list of children of its own type, (d) a wrapper translating XML responses to your JSON model, (e) an object created lazily on first method call.
10. Why does ordering matter for `@cache` then `@retry` versus `@retry` then `@cache` on a flaky function?

<details>
<summary>Solutions</summary>

**1.**
```python
class LegacyLogger:
    def __init__(self): self.lines = []
    def write_line(self, level, text): self.lines.append((level, text))
class LoggerAdapter:
    LEVELS = {"DEBUG": 0, "INFO": 1, "ERROR": 2}
    def __init__(self, legacy): self._l = legacy
    def log(self, level, message): self._l.write_line(self.LEVELS[level], message)
legacy = LegacyLogger(); LoggerAdapter(legacy).log("ERROR", "boom"); print(legacy.lines)    # [(2, 'boom')]
```

**2.**
```python
import functools, time
def cache_with_ttl(seconds, clock=time.monotonic):
    def deco(fn):
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
    return deco
t = [0]
calls = []
@cache_with_ttl(10, clock=lambda: t[0])
def slow(x): calls.append(x); return x * 2
slow(2); slow(2); t[0] = 11; slow(2)
print(calls)               # [2, 2]  (second call cached, third after expiry)
```

**3.**
```python
class Notifier:
    def send(self, msg): return ["email:" + msg]
class NotifierDecorator(Notifier):
    def __init__(self, inner): self.inner = inner
class SmsDecorator(NotifierDecorator):
    def send(self, msg): return self.inner.send(msg) + ["sms:" + msg]
class SlackDecorator(NotifierDecorator):
    def send(self, msg): return self.inner.send(msg) + ["slack:" + msg]
print(SlackDecorator(SmsDecorator(Notifier())).send("down"))   # ['email:down', 'sms:down', 'slack:down']
```

**4.**
```python
class WeatherService:
    def forecast(self, city): return f"sunny in {city}"
class CachingWeather:
    def __init__(self, real): self.real, self.cache, self.real_calls = real, {}, 0
    def forecast(self, city):
        if city not in self.cache:
            self.real_calls += 1
            self.cache[city] = self.real.forecast(city)
        return self.cache[city]
w = CachingWeather(WeatherService()); w.forecast("A"); w.forecast("A"); w.forecast("B"); print(w.real_calls)   # 2
```

**5.**
```python
log = []
class Amplifier:
    def on(self): log.append("amp on")
    def off(self): log.append("amp off")
class Projector:
    def on(self): log.append("projector on")
    def off(self): log.append("projector off")
class Lights:
    def dim(self): log.append("lights dim")
    def bright(self): log.append("lights bright")
class Player:
    def play(self, t): log.append(f"play {t}")
    def stop(self): log.append("stop")
class HomeTheater:
    def __init__(self): self.amp, self.proj, self.lights, self.player = Amplifier(), Projector(), Lights(), Player()
    def watch_movie(self, title):
        self.lights.dim(); self.proj.on(); self.amp.on(); self.player.play(title)
    def end_movie(self):
        self.player.stop(); self.amp.off(); self.proj.off(); self.lights.bright()
h = HomeTheater(); h.watch_movie("Up"); h.end_movie(); print(log)
```

**6.**
```python
class MenuNode:
    def __init__(self, name): self.name = name
class Item(MenuNode):
    def __init__(self, name, price): super().__init__(name); self.price = price
    def total_price(self): return self.price
    def print_menu(self, i=0): return " " * i + f"{self.name} ${self.price}"
    def find(self, name): return self if self.name == name else None
class Menu(MenuNode):
    def __init__(self, name): super().__init__(name); self.children = []
    def add(self, n): self.children.append(n); return self
    def total_price(self): return sum(c.total_price() for c in self.children)
    def print_menu(self, i=0): return "\n".join([" " * i + self.name + ":"] + [c.print_menu(i + 2) for c in self.children])
    def find(self, name):
        if self.name == name: return self
        for c in self.children:
            r = c.find(name)
            if r: return r
m = Menu("Lunch").add(Item("soup", 4)).add(Menu("Mains").add(Item("pasta", 9)).add(Item("steak", 15)))
print(m.print_menu()); print(m.total_price(), m.find("pasta").price)
```

**7.**
```python
class Channel:
    def deliver(self, text): raise NotImplementedError
class Email(Channel):
    def deliver(self, text): return f"EMAIL: {text}"
class Sms(Channel):
    def deliver(self, text): return f"SMS: {text}"
class Message:
    def __init__(self, channel): self.channel = channel
class Alert(Message):
    def send(self, text): return self.channel.deliver("ALERT " + text)
class Report(Message):
    def send(self, text): return self.channel.deliver("REPORT " + text)
print(Alert(Email()).send("disk"), "|", Report(Sms()).send("daily"))
```

**8.**
```python
class Species:
    __slots__ = ("name", "texture")
    def __init__(self, name, texture): self.name, self.texture = name, texture
class SpeciesFactory:
    cache = {}
    @classmethod
    def get(cls, name):
        if name not in cls.cache: cls.cache[name] = Species(name, f"{name}.png")
        return cls.cache[name]
class Tree:
    __slots__ = ("x", "y", "species")
    def __init__(self, x, y, species): self.x, self.y, self.species = x, y, species
forest = [Tree(i % 500, i // 500, SpeciesFactory.get(("oak", "pine", "fir")[i % 3])) for i in range(50_000)]
print(len({id(t.species) for t in forest}))      # 3 shared species objects for 50,000 trees
```

**9.** (a) Decorator (with caching), (b) Facade, (c) Composite, (d) Adapter, (e) Virtual proxy.

**10.** `@cache` outermost with `@retry` inside: a successful result is cached, failures are retried and never cached. `@retry` outermost with `@cache` inside: exceptions are not cached, so each retry calls the function again; but if a bad value is returned and cached, the retry returns the same bad value. Order determines what is cached and what gets retried.

</details>

[Lesson](README.md) · [Summary](summary.md)
