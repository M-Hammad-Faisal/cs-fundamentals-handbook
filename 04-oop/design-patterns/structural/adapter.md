# Adapter Pattern

**Family:** structural · **Also called:** wrapper · **How often you will use it:** very often · **Difficulty:** easy

## 1. In plain words

An **Adapter** sits between two pieces of code whose interfaces do not match and **translates** between them, so neither has to change.

Analogy: a **travel plug adapter**. Your laptop has a UK plug, the wall has a US socket. The adapter changes the shape; the laptop and the wall stay exactly as they are.

## 2. The problem

You depend on a class you cannot (or should not) change, perhaps a third-party library or legacy code, and its methods do not look like what your application expects:

```python no-run
sensor = LegacyThermometer()
temperature = sensor.read_fahrenheit()   # your app expects sensor.read() in Celsius
```

Editing the library is not an option; scattering conversions through your code is messy.

## 3. The solution

```text
Client ──► Target interface ◄── Adapter ──holds──► Adaptee (the incompatible class)
          read() -> celsius      read(): calls adaptee.read_fahrenheit() and converts
```

Roles: **Target** (what the client expects), **Adaptee** (what you have), **Adapter** (implements the target by delegating to the adaptee), **Client** (uses the target and never knows about the adaptee).

## 4. Step by step

```python
class LegacyTemperatureSensor:                        # the adaptee: cannot change it
    def read_fahrenheit(self):
        return 98.6

class CelsiusSensor:                                  # the target interface our app expects
    def read(self):
        raise NotImplementedError

class SensorAdapter(CelsiusSensor):                   # the adapter (object adapter: composition)
    def __init__(self, legacy):
        self._legacy = legacy
    def read(self):
        return round((self._legacy.read_fahrenheit() - 32) * 5 / 9, 1)

def alert_if_hot(sensor: CelsiusSensor, limit=37.0):  # client: only knows the target
    return "ALERT" if sensor.read() > limit else "ok"

adapter = SensorAdapter(LegacyTemperatureSensor())
print(adapter.read(), alert_if_hot(adapter))          # 37.0 ok
```

### Adapting method names and data shapes

```python
class OldLogger:
    def write_line(self, level_number, text):
        self.last = (level_number, text)

class LoggerAdapter:
    LEVELS = {"DEBUG": 0, "INFO": 1, "ERROR": 2}
    def __init__(self, old):
        self._old = old
    def log(self, level, message):                    # new-style call: log("ERROR", "boom")
        self._old.write_line(self.LEVELS[level], message)

old = OldLogger()
LoggerAdapter(old).log("ERROR", "boom")
print(old.last)                                       # (2, 'boom')
```

### Two flavors

- **Object adapter** (shown above): holds an instance of the adaptee. Preferred: flexible, works with subclasses of the adaptee.
- **Class adapter**: inherits from both target and adaptee (multiple inheritance). Less flexible, couples tightly.

```python
class ClassAdapter(LegacyTemperatureSensor, CelsiusSensor):     # class adapter
    def read(self):
        return round((self.read_fahrenheit() - 32) * 5 / 9, 1)
print(ClassAdapter().read())                                    # 37.0
```

## 5. The Pythonic way

- A **function** can be an adapter: `adapted = lambda x: legacy_call(to_old_format(x))`.
- `functools.partial` adapts a function's signature.
- Duck typing means an adapter often only needs to provide the *methods* the client calls (no formal base class).
- At the system boundary, an adapter is your **anti-corruption layer**: it converts an external API's vocabulary into your domain's.

```python
legacy_total = lambda cents_list: sum(cents_list)             # old API works in cents
total_dollars = lambda prices: legacy_total([int(p * 100) for p in prices]) / 100
print(total_dollars([1.50, 2.25]))                            # 3.75
```

## 6. When to use it (and when not to)

**Use it when** integrating third-party libraries, legacy code or several vendors behind one interface (payment gateways, storage backends); when you want your core code to depend on *your* interface, not a vendor's.

**Skip it when** you control both sides (just change one), or the mismatch is a one-line conversion in one place.

## 7. Pros and cons

| Pros | Cons |
|------|------|
| Reuse incompatible code without changing it | One more layer to maintain |
| Isolates vendor details (easy to swap vendors) | Can hide missing features or leak abstractions |
| Single place for conversions | Too many adapters signals a messy design |

## 8. Related patterns

- [Decorator](decorator.md): same interface, adds behavior. Adapter: different interface, same behavior.
- [Facade](facade.md): simplifies many classes; Adapter converts one.
- [Proxy](proxy.md): same interface, controls access.
- [Bridge](bridge.md): designed up front to separate abstraction from implementation; Adapter fixes a mismatch after the fact.

## 9. Two real-world examples

**Example 1: `io.TextIOWrapper`.** It wraps a *byte* stream (like a socket or file opened in binary) and presents the *text* stream interface (`read()` returns `str`), converting encodings. Code written for text streams works with it.

**Example 2: Shipping carriers.** An e-commerce site integrates UPS, FedEx and a local courier, each with a different API. One adapter per carrier implements `ShippingProvider.quote()/book()/track()`; the checkout code uses only that interface, so adding a carrier means adding an adapter.

## 10. Common mistakes

- Putting business logic in the adapter (it should only translate).
- Adapting too much, so the adapter becomes a second library.
- Leaking the adaptee's types and exceptions through the adapter.
- Using class adapters (inheritance) when composition would do.

## 11. Practice

1. Adapt a `LegacyPrinter.print_text(s)` to a `Printer.print(doc)` interface where `doc` has `.title` and `.body`.
2. Write an adapter so an `XmlWeather.get()` returning `"<t>21</t>"` fits `WeatherSource.temperature() -> float`.
3. Why is the object adapter usually better than the class adapter?

<details>
<summary>Solutions</summary>

**1.**
```python
class LegacyPrinter:
    def print_text(self, s): return f"PRINTED: {s}"
class DocPrinter:
    def __init__(self, legacy): self._l = legacy
    def print(self, doc): return self._l.print_text(f"{doc.title}\n{doc.body}")
class Doc:
    def __init__(self, t, b): self.title, self.body = t, b
print(DocPrinter(LegacyPrinter()).print(Doc("T", "B")))
```

**2.**
```python
import re
class XmlWeather:
    def get(self): return "<t>21</t>"
class WeatherAdapter:
    def __init__(self, src): self.src = src
    def temperature(self): return float(re.search(r"<t>(.*?)</t>", self.src.get()).group(1))
print(WeatherAdapter(XmlWeather()).temperature())       # 21.0
```

**3.** It uses composition: it works with the adaptee *and any subclass*, does not inherit unwanted methods, avoids multiple-inheritance complexity, and the adaptee can be swapped at runtime.

</details>

## 12. Check yourself

1. What problem does an Adapter solve?
2. Name the four roles.
3. Adapter versus Decorator versus Facade?
4. What is an anti-corruption layer?

<details>
<summary>Answers</summary>

1. Making an incompatible interface match the one the client expects, without changing either side.
2. Client, Target, Adaptee, Adapter.
3. Adapter changes the interface; Decorator keeps the interface and adds behavior; Facade provides a simpler interface over several classes.
4. An adapter layer at the boundary with an external system that translates its model and vocabulary into your domain's, protecting your code from external changes.

</details>

## More examples

Runnable script from your companion repository: [`structuralPattern/adapterPattern.py`](https://github.com/M-Hammad-Faisal/design-patterns-python/blob/master/structuralPattern/adapterPattern.py)

[Family overview](README.md) · [All patterns](../README.md)
