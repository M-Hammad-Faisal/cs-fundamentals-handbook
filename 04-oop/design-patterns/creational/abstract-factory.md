# Abstract Factory Pattern

**Family:** creational · **Also called:** kit · **How often you will use it:** occasionally (UI kits, multi-vendor SDKs) · **Difficulty:** medium

## 1. In plain words

An **Abstract Factory** creates a whole **family of related objects** that must match each other, without naming their concrete classes.

Analogy: a **furniture shop's "Modern" and "Victorian" collections**. If you ask the Modern showroom for a chair, a sofa and a table, you get three pieces that go together. You would never get a Victorian chair with a Modern sofa, because each showroom (factory) only makes its own style.

It differs from [Factory Method](factory-method.md): that builds **one product**; an abstract factory builds **several related products** through several `create_...` methods.

## 2. The problem

```python no-run
if theme == "dark":
    button = DarkButton()
    checkbox = DarkCheckbox()
else:
    button = LightButton()
    checkbox = LightCheckbox()
# Easy to mix by mistake: DarkButton() with LightCheckbox() ... and every screen repeats this.
```

## 3. The solution

```text
 AbstractFactory                    AbstractButton    AbstractCheckbox
  + create_button()                       ^                  ^
  + create_checkbox()                 ____|____          ____|____
        ^                            |         |        |         |
   _____|______                  LightButton DarkButton LightCheckbox DarkCheckbox
  |            |
LightFactory  DarkFactory   (each factory creates the matching family)
```

Client code receives **one factory object** and asks it for every component, so the family stays consistent.

## 4. Step by step

```python
from abc import ABC, abstractmethod

# 1. Product interfaces
class Button(ABC):
    @abstractmethod
    def render(self): ...

class Checkbox(ABC):
    @abstractmethod
    def render(self): ...

# 2. Concrete products, per family
class LightButton(Button):
    def render(self): return "light-button"
class LightCheckbox(Checkbox):
    def render(self): return "light-checkbox"
class DarkButton(Button):
    def render(self): return "dark-button"
class DarkCheckbox(Checkbox):
    def render(self): return "dark-checkbox"

# 3. The abstract factory interface
class ThemeFactory(ABC):
    @abstractmethod
    def create_button(self) -> Button: ...
    @abstractmethod
    def create_checkbox(self) -> Checkbox: ...

# 4. One concrete factory per family
class LightFactory(ThemeFactory):
    def create_button(self): return LightButton()
    def create_checkbox(self): return LightCheckbox()

class DarkFactory(ThemeFactory):
    def create_button(self): return DarkButton()
    def create_checkbox(self): return DarkCheckbox()

# 5. Client code depends only on the abstractions
def build_form(factory: ThemeFactory):
    return [factory.create_button().render(), factory.create_checkbox().render()]

print(build_form(LightFactory()))     # ['light-button', 'light-checkbox']
print(build_form(DarkFactory()))      # ['dark-button', 'dark-checkbox']

# 6. Choose the factory once, at the edge of the program
FACTORIES = {"light": LightFactory, "dark": DarkFactory}
def factory_for(theme): return FACTORIES[theme]()
print(build_form(factory_for("dark")))
```

Adding a **new family** (a high-contrast theme) means writing new products and one new factory; no client code changes. Adding a **new product type** (a `Slider`) means editing every factory: that is the pattern's main cost.

## 5. The Pythonic way

Because Python classes are first-class, a "factory" can be a simple object holding classes:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Family:
    button: type
    checkbox: type

LIGHT = Family(LightButton, LightCheckbox)
DARK = Family(DarkButton, DarkCheckbox)

def build_form2(family: Family):
    return [family.button().render(), family.checkbox().render()]

print(build_form2(DARK))              # ['dark-button', 'dark-checkbox']
```

For tests, a "fake family" with simple stand-in classes is easy to pass in.

## 6. When to use it (and when not to)

**Use it when** several objects must be created **together and be compatible** (UI themes, per-platform widgets, per-database connection + cursor + dialect, per-cloud storage + queue clients, test versus production wiring).

**Skip it when** you only create one kind of product (use [Factory Method](factory-method.md)) or families will never vary.

## 7. Pros and cons

| Pros | Cons |
|------|------|
| Guarantees products from one family are used together | Many classes and interfaces |
| Swap the whole family by changing one object | Adding a new *product type* touches every factory |
| Client is isolated from concrete classes | Overkill for small variations |

## 8. Related patterns

- [Factory Method](factory-method.md): each `create_x` in an abstract factory is a factory method.
- [Singleton](singleton.md): a concrete factory is usually created once.
- [Builder](builder.md): one complex object versus a family of simple ones.
- [Bridge](../structural/bridge.md): another way to separate abstraction from platform.

## 9. Two real-world examples

**Example 1: A cross-platform GUI toolkit.** One factory creates native buttons, scrollbars and menus for Windows, another for macOS, another for Linux. The settings screen code calls `factory.create_button()` and works everywhere with a native look.

**Example 2: A database layer for several vendors.** `PostgresFactory` creates a `PostgresConnection`, `PostgresQueryBuilder` and `PostgresDialect`; `MySqlFactory` creates the MySQL set. The data-access code never mixes MySQL quoting with a PostgreSQL connection because both come from one factory.

## 10. Common mistakes

- Using it when [Factory Method](factory-method.md) or a plain function is enough.
- Leaking concrete classes into client code (defeats the point).
- Putting unrelated products in one factory.
- Forgetting that adding product types is expensive.

## 11. Practice

1. Build `WindowsFactory`/`MacFactory` creating `Button` and `Scrollbar`, and a `settings_panel(factory)` function.
2. Add a `HighContrastFactory` family without editing `build_form`.
3. Show a test that passes a fake factory recording what was created.

<details>
<summary>Solutions</summary>

**1.**
```python
class WinButton:    render = lambda self: "win-button"
class WinScrollbar: render = lambda self: "win-scrollbar"
class MacButton:    render = lambda self: "mac-button"
class MacScrollbar: render = lambda self: "mac-scrollbar"
class WindowsFactory:
    def create_button(self): return WinButton()
    def create_scrollbar(self): return WinScrollbar()
class MacFactory:
    def create_button(self): return MacButton()
    def create_scrollbar(self): return MacScrollbar()
def settings_panel(f): return [f.create_button().render(), f.create_scrollbar().render()]
print(settings_panel(WindowsFactory()), settings_panel(MacFactory()))
```

**2.**
```python
class HcButton(Button):
    def render(self): return "hc-button"
class HcCheckbox(Checkbox):
    def render(self): return "hc-checkbox"
class HighContrastFactory(ThemeFactory):
    def create_button(self): return HcButton()
    def create_checkbox(self): return HcCheckbox()
print(build_form(HighContrastFactory()))           # build_form unchanged
```

**3.**
```python
class RecordingFactory(ThemeFactory):
    def __init__(self): self.created = []
    def create_button(self): self.created.append("button"); return LightButton()
    def create_checkbox(self): self.created.append("checkbox"); return LightCheckbox()
rf = RecordingFactory(); build_form(rf); print(rf.created)    # ['button', 'checkbox']
```

</details>

## 12. Check yourself

1. How does Abstract Factory differ from Factory Method?
2. What guarantee does it give the client?
3. What is easy to add and what is hard to add?
4. Give two real examples.

<details>
<summary>Answers</summary>

1. Factory Method creates one product and lets subclasses choose its class; Abstract Factory creates a *family* of related products via several methods.
2. All the objects it creates belong to the same family and are compatible.
3. Easy: a new family (new factory plus products). Hard: a new product type, since every factory must be edited.
4. GUI toolkits with per-platform widgets; database or cloud SDK families (connection + dialect + query builder per vendor).

</details>

## More examples

Runnable script from your companion repository: [`creationalPattern/abstractFactoryPattern.py`](https://github.com/M-Hammad-Faisal/design-patterns-python/blob/master/creationalPattern/abstractFactoryPattern.py)

[Family overview](README.md) · [All patterns](../README.md)
