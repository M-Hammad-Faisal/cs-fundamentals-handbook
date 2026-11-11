# Facade Pattern

**Family:** structural · **How often you will use it:** very often · **Difficulty:** easy

## 1. In plain words

A **Facade** is **one simple entry point in front of a complicated system**. Callers use the simple method; the facade coordinates the many pieces behind it.

Analogy: a **hotel concierge**. You say "dinner for two at 8, and a taxi". The concierge calls the restaurant, the taxi company and the front desk. You never deal with all of them.

## 2. The problem

Doing one common task requires knowing and calling many classes in the right order:

```python no-run
decoder = VideoDecoder(); video = decoder.decode("movie.avi")
video = Compressor().compress(video, quality="high")
audio = AudioExtractor().extract("movie.avi")
result = Muxer().mux(video, audio)       # every caller repeats this recipe
```

## 3. The solution

```text
Client ──► Facade.convert(file) ──► VideoDecoder
                                 ├► Compressor
                                 ├► AudioExtractor
                                 └► Muxer      (the subsystem stays available to experts)
```

The facade does **not** hide or replace the subsystem; it offers an easy path for common jobs.

## 4. Step by step

```python
class VideoDecoder:
    def decode(self, f): return f"frames({f})"

class AudioExtractor:
    def extract(self, f): return f"audio({f})"

class Compressor:
    def compress(self, data, quality): return f"{data}@{quality}"

class Muxer:
    def mux(self, video, audio): return f"{video}+{audio}"

class VideoConverter:                                   # the facade
    def convert(self, filename, quality="high"):
        video = Compressor().compress(VideoDecoder().decode(filename), quality)
        audio = AudioExtractor().extract(filename)
        return Muxer().mux(video, audio)

print(VideoConverter().convert("movie.avi"))            # frames(movie.avi)@high+audio(movie.avi)
print(VideoConverter().convert("clip.mp4", "low"))      # frames(clip.mp4)@low+audio(clip.mp4)
```

### A "service layer" facade for a use case

```python
class Inventory:
    def __init__(self): self.stock = {"pen": 5}
    def reserve(self, sku, qty):
        if self.stock.get(sku, 0) < qty:
            raise ValueError(f"not enough {sku}")
        self.stock[sku] -= qty

class Payments:
    def charge(self, user, amount): return f"charged {user} {amount}"

class Shipping:
    def book(self, user, sku): return f"shipping {sku} to {user}"

class CheckoutFacade:
    def __init__(self, inventory, payments, shipping):
        self.inventory, self.payments, self.shipping = inventory, payments, shipping
    def buy(self, user, sku, qty, price):
        self.inventory.reserve(sku, qty)                # step 1
        receipt = self.payments.charge(user, price * qty)    # step 2
        label = self.shipping.book(user, sku)           # step 3
        return receipt, label

shop = CheckoutFacade(Inventory(), Payments(), Shipping())
print(shop.buy("ana", "pen", 2, 3))                     # ('charged ana 6', 'shipping pen to ana')
```

## 5. The Pythonic way

Facades are everywhere in Python's standard library and ecosystem:

- `requests.get(url)` hides sessions, adapters, connection pools, redirects and encoding.
- `shutil.copytree`, `subprocess.run`, `os.makedirs(exist_ok=True)` wrap several lower-level steps.
- A module with a few well-named functions is itself a facade over its internals (`__all__` lists the public API).

```python
import shutil, tempfile, os
src = tempfile.mkdtemp(); open(os.path.join(src, "a.txt"), "w").write("hi")
dst = os.path.join(tempfile.mkdtemp(), "copy")
shutil.copytree(src, dst)                               # one call: walk, create, copy, preserve
print(os.listdir(dst))                                  # ['a.txt']
```

## 6. When to use it (and when not to)

**Use it when** a subsystem is complex and most callers need only a few common operations; to define a clean boundary between layers; to reduce coupling to many classes.

**Skip it when** the subsystem is already simple, or callers genuinely need the fine-grained control (do not wall it off).

## 7. Pros and cons

| Pros | Cons |
|------|------|
| Simple, readable API for common tasks | Can grow into a god class that does everything |
| Lower coupling between client and subsystem | Can hide features callers need |
| A natural place for orchestration and transactions | One more layer to maintain |

## 8. Related patterns

- [Adapter](adapter.md): converts one interface; Facade simplifies many.
- [Mediator](../behavioral/mediator.md): coordinates objects that talk to each other (two-way); Facade is one-way, client to subsystem.
- [Abstract Factory](../creational/abstract-factory.md) can sit behind a facade.
- [Singleton](../creational/singleton.md): a facade is often created once.

## 9. Two real-world examples

**Example 1: `requests.get(url)`.** Underneath: build a `Request`, prepare it, pick an adapter, open a pooled connection, handle TLS, follow redirects, decode the body. You write one line.

**Example 2: A deployment script.** `deploy(app)` runs tests, builds an image, pushes it, updates the manifest and waits for health checks. Developers call `deploy`; the many tools stay available for debugging.

## 10. Common mistakes

- Letting the facade accumulate business logic (it should *coordinate*, not decide).
- Making the facade the only way in (power users still need direct access).
- A facade per class (that is just a wrapper).
- Creating one giant facade for the whole application.

## 11. Practice

1. Build a `HomeTheater` facade with `watch_movie(title)` and `end_movie()` over `Amplifier`, `Projector`, `Lights`, `Player`. Verify call order.
2. Write a `report(path)` facade that reads a CSV, computes totals and returns text, using three small helper classes.
3. Why shouldn't a facade contain pricing rules?

<details>
<summary>Solutions</summary>

**1.**
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
h = HomeTheater(); h.watch_movie("Up"); h.end_movie()
print(log)
```

**2.**
```python
import csv, io
class Reader:
    def rows(self, text): return list(csv.DictReader(io.StringIO(text)))
class Totals:
    def total(self, rows): return sum(float(r["amount"]) for r in rows)
class Formatter:
    def render(self, total): return f"TOTAL: {total:.2f}"
class ReportFacade:
    def report(self, text): return Formatter().render(Totals().total(Reader().rows(text)))
print(ReportFacade().report("name,amount\na,1.5\nb,2.25"))     # TOTAL: 3.75
```

**3.** Pricing rules are business decisions that change independently; putting them in the facade mixes coordination with domain logic, makes it a god class, and makes the rules hard to reuse and test. Keep rules in their own class and let the facade call it.

</details>

## 12. Check yourself

1. What does a Facade give clients?
2. Does it replace the subsystem?
3. What is its main risk?
4. Name two Python facades.

<details>
<summary>Answers</summary>

1. A simple, unified interface to a complex subsystem for common tasks.
2. No; the subsystem remains accessible for advanced use.
3. Growing into a god class that contains logic and becomes a bottleneck for change.
4. `requests.get`, `shutil.copytree`, `subprocess.run`.

</details>

## More examples

Runnable script (added to your companion repository with this lesson): [`structuralPattern/facadePattern.py`](https://github.com/M-Hammad-Faisal/design-patterns-python/blob/master/structuralPattern/facadePattern.py)

[Family overview](README.md) · [All patterns](../README.md)
