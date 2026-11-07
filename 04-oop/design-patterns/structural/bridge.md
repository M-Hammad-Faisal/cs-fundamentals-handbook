# Bridge Pattern

**Family:** structural · **How often you will use it:** occasionally · **Difficulty:** medium (the idea is simple, the name is confusing)

## 1. In plain words

A **Bridge** splits a design into **two separate hierarchies** (what something *is* versus how it is *done*) and connects them with a reference, so each side can grow independently.

Analogy: a **TV remote and the TV**. Remotes (basic, advanced) and TVs (Sony, LG) vary independently. Any remote works with any TV because they talk through a standard connection; you do not build "BasicSonyRemote", "AdvancedSonyRemote", "BasicLgRemote"...

## 2. The problem

Two dimensions of variation produce a class for every combination:

```text
Shape: Circle, Square          Renderer: SVG, ASCII
=> SvgCircle, AsciiCircle, SvgSquare, AsciiSquare   (2 x 2 = 4 classes; add a renderer and it is 6)
```

With 5 shapes and 4 renderers you would write 20 classes.

## 3. The solution

```text
Abstraction ──holds──► Implementor (interface)
   ▲                         ▲
RefinedAbstraction     ┌─────┴─────┐
(Circle, Square)   SvgRenderer  AsciiRenderer
```

The **abstraction** (what you do: draw shapes) **delegates** the low-level work to an **implementor** (how: SVG or ASCII). You get 5 + 4 classes instead of 5 x 4.

## 4. Step by step

```python
from abc import ABC, abstractmethod

class Renderer(ABC):                                    # the implementation hierarchy
    @abstractmethod
    def circle(self, r): ...
    @abstractmethod
    def square(self, side): ...

class SvgRenderer(Renderer):
    def circle(self, r): return f'<circle r="{r}"/>'
    def square(self, side): return f'<rect width="{side}" height="{side}"/>'

class AsciiRenderer(Renderer):
    def circle(self, r): return f"(circle of radius {r})"
    def square(self, side): return f"[square of side {side}]"

class Shape:                                            # the abstraction hierarchy
    def __init__(self, renderer: Renderer):
        self.renderer = renderer                        # <- the "bridge"

class Circle(Shape):
    def __init__(self, renderer, r):
        super().__init__(renderer)
        self.r = r
    def draw(self):
        return self.renderer.circle(self.r)

class Square(Shape):
    def __init__(self, renderer, side):
        super().__init__(renderer)
        self.side = side
    def draw(self):
        return self.renderer.square(self.side)

for renderer in (SvgRenderer(), AsciiRenderer()):
    print(Circle(renderer, 2).draw(), "|", Square(renderer, 3).draw())
# <circle r="2"/> | <rect width="3" height="3"/>
# (circle of radius 2) | [square of side 3]
```

Add a `CanvasRenderer` and every shape works with it; add a `Triangle` and every renderer can draw it (once the renderer interface gains `triangle`).

### Another example: messages and delivery channels

```python
class Channel(ABC):
    @abstractmethod
    def deliver(self, text): ...

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

print(Alert(Email()).send("disk full"), "|", Report(Sms()).send("daily summary"))
# EMAIL: ALERT disk full | SMS: REPORT daily summary
```

## 5. The Pythonic way

Bridge is "composition over inheritance" applied at design time. In Python you often skip the formal ABC and pass any object (duck typing) or even a function:

```python
class Notifier:
    def __init__(self, send_fn):                        # the implementor is just a callable
        self.send_fn = send_fn
    def alert(self, text):
        return self.send_fn("ALERT " + text)

print(Notifier(lambda t: f"SMS: {t}").alert("up"))      # SMS: ALERT up
```

Examples in the standard library: `logging` (a `Logger` abstraction over interchangeable `Handler` implementations), DB-API drivers behind an ORM, `pathlib` (`PurePath` abstraction over `PosixPath`/`WindowsPath` flavors).

## 6. When to use it (and when not to)

**Use it when** you see two independent dimensions (platform x feature, shape x renderer, message x channel, device x remote); when you want to swap the implementation at runtime; when inheritance would multiply classes.

**Skip it when** there is only one dimension (plain [Strategy](../behavioral/strategy.md) or inheritance is enough).

## 7. Pros and cons

| Pros | Cons |
|------|------|
| Avoids M x N class explosion | More up-front design and indirection |
| Both hierarchies evolve independently | Overkill when only one dimension varies |
| Swap implementations at runtime | Hard to see the structure if poorly named |

## 8. Related patterns

- [Adapter](adapter.md): fixes a mismatch after the fact; Bridge is designed in advance.
- [Strategy](../behavioral/strategy.md): same shape (delegate to an interchangeable object), different intent: Strategy swaps an algorithm; Bridge separates a whole implementation layer.
- [Abstract Factory](../creational/abstract-factory.md): can create the right implementor for a bridge.

## 9. Two real-world examples

**Example 1: UI toolkit over native platforms.** `Window`, `Dialog` abstractions hold a `PlatformImplementation` (Windows, macOS, Linux). New window types and new platforms are added independently.

**Example 2: A `Repository` over different storage engines.** `UserRepository` and `OrderRepository` (abstractions) delegate to a `Storage` implementor (Postgres, SQLite, in-memory for tests); swapping storage does not touch the repositories.

## 10. Common mistakes

- Using Bridge when only one axis varies.
- Making the implementor interface mirror the abstraction exactly (then there is no separation).
- Putting platform details in the abstraction.

## 11. Practice

1. Add a `Triangle` shape and a `CanvasRenderer` to the example without editing existing shapes or renderers (other than interface additions).
2. Build a `RemoteControl`/`Device` bridge with `Tv` and `Radio` devices and `BasicRemote`/`AdvancedRemote` (with `mute()`).
3. How many classes without Bridge for 6 shapes x 4 renderers? With Bridge?

<details>
<summary>Solutions</summary>

**1.** (renderer interface grows by one method):
```python
class CanvasRenderer(Renderer):
    def circle(self, r): return f"canvas.arc({r})"
    def square(self, side): return f"canvas.rect({side})"
print(Circle(CanvasRenderer(), 1).draw(), Square(CanvasRenderer(), 2).draw())
```

**2.**
```python
class Device:
    def __init__(self): self.volume = 10
class Tv(Device):    name = "TV"
class Radio(Device): name = "Radio"
class BasicRemote:
    def __init__(self, device): self.device = device
    def volume_up(self): self.device.volume += 1; return f"{self.device.name} volume {self.device.volume}"
class AdvancedRemote(BasicRemote):
    def mute(self): self.device.volume = 0; return f"{self.device.name} muted"
print(BasicRemote(Tv()).volume_up(), AdvancedRemote(Radio()).mute())
```

**3.** Without Bridge: 6 x 4 = 24 concrete classes. With Bridge: 6 shapes + 4 renderers = 10.

</details>

## 12. Check yourself

1. What two hierarchies does Bridge separate?
2. How does it prevent class explosion?
3. How does Bridge differ from Adapter?
4. Which dimension is the "bridge" reference?

<details>
<summary>Answers</summary>

1. The abstraction (what the client uses) and the implementation (how the work is done).
2. By composing one hierarchy with another via a reference, so M abstractions and N implementations need M + N classes, not M x N.
3. Adapter is applied afterwards to make incompatible things fit; Bridge is designed up front to let both sides vary.
4. The field in the abstraction that references the implementor (`self.renderer`).

</details>

## More examples

Runnable script (added to your companion repository with this lesson): [`structuralPattern/bridgePattern.py`](https://github.com/M-Hammad-Faisal/design-patterns-python/blob/master/structuralPattern/bridgePattern.py)

[Family overview](README.md) · [All patterns](../README.md)
