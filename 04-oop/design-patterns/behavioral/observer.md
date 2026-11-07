# Observer Pattern

**Family:** behavioral · **Also called:** publish/subscribe (pub/sub), listener, event emitter · **How often you will use it:** very often · **Difficulty:** easy to medium

## 1. In plain words

With **Observer**, one object (the **subject** or publisher) keeps a list of others (the **observers** or subscribers) and **notifies all of them automatically** when something happens. The subject does not know or care what the observers do.

Analogy: **subscribing to a YouTube channel**. The creator uploads once; every subscriber gets a notification. The creator does not know who you are or what you do next, and you can unsubscribe any time.

## 2. The problem

When a value changes, many other parts must react, and the changing object ends up knowing about all of them:

```python
class Stock:
    def set_price(self, p):
        self.price = p
        chart.update(p)          # the stock knows about the chart,
        alerts.check(p)          # the alert system,
        logger.write(p)          # the logger... every new reaction edits this method
```

## 3. The solution

```text
Subject ──notifies──► Observer 1 (chart)
 │  subscribe()      ► Observer 2 (alerts)
 │  unsubscribe()    ► Observer 3 (logger)
 └─ emit(event) → calls every registered observer
```

Observers register themselves; the subject only keeps a list of callbacks.

## 4. Step by step

```python
class EventEmitter:
    def __init__(self):
        self._handlers = {}                                   # event name -> list of callbacks

    def subscribe(self, event, handler):
        self._handlers.setdefault(event, []).append(handler)
        return lambda: self._handlers[event].remove(handler)  # returns an "unsubscribe" function

    def emit(self, event, *args):
        for handler in list(self._handlers.get(event, [])):   # iterate a copy: handlers may unsubscribe
            handler(*args)

class Stock:                                                  # the subject
    def __init__(self, symbol, price):
        self.symbol, self._price = symbol, price
        self.events = EventEmitter()

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        old, self._price = self._price, value
        self.events.emit("price_changed", self.symbol, old, value)

log = []
stock = Stock("ACME", 100)
unsubscribe_chart = stock.events.subscribe(
    "price_changed", lambda s, o, n: log.append(f"chart: {s} {o}->{n}"))
stock.events.subscribe(
    "price_changed", lambda s, o, n: n > 120 and log.append(f"alert: {s} spiked to {n}"))

stock.price = 110
stock.price = 130
unsubscribe_chart()                                           # chart stops listening
stock.price = 90
print(log)
# ['chart: ACME 100->110', 'chart: ACME 110->130', 'alert: ACME spiked to 130']
```

### The classic object-oriented form

```python
class Subject:
    def __init__(self): self._observers = []
    def attach(self, o): self._observers.append(o)
    def detach(self, o): self._observers.remove(o)
    def notify(self, data):
        for o in self._observers:
            o.update(data)

class Display:
    def __init__(self, name): self.name, self.seen = name, []
    def update(self, data): self.seen.append(data)

weather = Subject()
d1, d2 = Display("phone"), Display("web")
weather.attach(d1); weather.attach(d2)
weather.notify("rain"); weather.detach(d2); weather.notify("sun")
print(d1.seen, d2.seen)                                       # ['rain', 'sun'] ['rain']
```

### Keeping one failing observer from breaking the others

```python
def safe_emit(handlers, *args):
    errors = []
    for h in handlers:
        try:
            h(*args)
        except Exception as e:                                # isolate failures
            errors.append(type(e).__name__)
    return errors

def broken(x): raise RuntimeError
ok = []
print(safe_emit([broken, ok.append], 5), ok)                   # ['RuntimeError'] [5]
```

## 5. The Pythonic way

- A list of **callables** is enough; no observer base class needed.
- `weakref.WeakMethod` / `WeakSet` stop a long-lived subject from keeping observers alive (memory leaks).
- Real libraries: Django **signals** (`post_save`), **Blinker**, `asyncio` events and queues, `tkinter` bindings, Qt signals/slots, reactive libraries (RxPY).
- Across processes or machines the same idea is **pub/sub messaging**: Redis Pub/Sub, Kafka, RabbitMQ, MQTT.

```python
import weakref

class Listener:
    def on_event(self, x): print("got", x)

class Bus:
    def __init__(self): self._subs = weakref.WeakSet()
    def add(self, obj): self._subs.add(obj)
    def publish(self, x):
        for s in list(self._subs): s.on_event(x)

bus, l = Bus(), Listener()
bus.add(l); bus.publish(1)                                    # got 1
del l                                                         # the bus does not keep it alive
bus.publish(2)                                                # (nothing printed)
```

## 6. When to use it (and when not to)

**Use it when** a change in one object must trigger actions in an unknown or changing set of others: UI events, model-view updates, notifications, cache invalidation, plugin hooks, audit logging.

**Skip it when** only one fixed collaborator needs the call (call it directly), or when the reaction order or transactionality matters and a plain workflow is clearer.

## 7. Pros and cons

| Pros | Cons |
|------|------|
| Subject and observers are loosely coupled | **Memory leaks** when observers never unsubscribe |
| Add/remove listeners at runtime | Notification order is often unspecified |
| Open/Closed: new reactions need no change to the subject | Hard to trace "who reacted to what"; cascades of updates |
| | An exception in one handler can affect the rest unless isolated |

## 8. Related patterns

- [Mediator](mediator.md): a central object coordinates many-to-many communication; Observer is one-to-many broadcasting.
- [Command](command.md): events can carry commands; queues of commands are like deferred observers.
- [Chain of Responsibility](chain-of-responsibility.md): a request is handled by *one* handler in the chain; Observer notifies *all*.
- [Strategy](strategy.md), [State](state.md): may be used inside observers.

## 9. Two real-world examples

**Example 1: Django signals.** Saving a `User` fires `post_save`. One receiver creates a profile, another sends a welcome email, another updates a search index. The `User` model knows none of them.

**Example 2: UI event listeners.** A button's `click` event notifies every registered handler (log analytics, submit the form, play a sound). The button just says "I was clicked".

## 10. Common mistakes

- Forgetting to unsubscribe (leaks) or unsubscribing while iterating (iterate over a copy).
- Observers that change the subject in response, causing loops.
- Long-running observers that block the subject (use a queue or async).
- Exceptions in observers breaking the notification of the rest.
- Depending on the order observers run.

## 11. Practice

1. Build a `Thermostat` that notifies observers only when the temperature crosses a threshold.
2. Add priorities so higher-priority observers are called first.
3. Make `EventEmitter.once(event, handler)` that runs a handler at most one time.

<details>
<summary>Solutions</summary>

**1.**
```python
class Thermostat:
    def __init__(self, threshold):
        self.threshold, self.temp, self.subs = threshold, 20, []
    def subscribe(self, fn): self.subs.append(fn)
    def set_temp(self, t):
        crossed = (self.temp <= self.threshold) != (t <= self.threshold)
        self.temp = t
        if crossed:
            for fn in list(self.subs):
                fn(t)
seen = []
th = Thermostat(25); th.subscribe(seen.append)
th.set_temp(22); th.set_temp(30); th.set_temp(31); th.set_temp(10)
print(seen)                                                   # [30, 10]
```

**2.**
```python
class PriorityEmitter:
    def __init__(self): self.handlers = []
    def subscribe(self, fn, priority=0):
        self.handlers.append((priority, fn))
        self.handlers.sort(key=lambda p: -p[0])
    def emit(self, *a):
        for _, fn in self.handlers: fn(*a)
order = []
pe = PriorityEmitter()
pe.subscribe(lambda: order.append("low"), 1); pe.subscribe(lambda: order.append("high"), 9)
pe.emit(); print(order)                                       # ['high', 'low']
```

**3.**
```python
class OnceEmitter(EventEmitter):
    def once(self, event, handler):
        def wrapper(*a):
            unsubscribe()
            handler(*a)
        unsubscribe = self.subscribe(event, wrapper)
oe, hits = OnceEmitter(), []
oe.once("x", hits.append); oe.emit("x", 1); oe.emit("x", 2)
print(hits)                                                   # [1]
```

</details>

## 12. Check yourself

1. Who knows about whom in Observer?
2. Why iterate over a copy of the handlers list?
3. What causes memory leaks and how do you avoid them?
4. Observer versus Chain of Responsibility?
5. Name two real systems that use it.

<details>
<summary>Answers</summary>

1. The subject knows only that it has callbacks; observers know the subject (they subscribe). The subject does not know what they do.
2. A handler may unsubscribe (or subscribe) during notification; mutating the list while looping would skip or break handlers.
3. A long-lived subject holds references to observers that are never removed; unsubscribe explicitly or use weak references.
4. Observer notifies *every* listener; Chain of Responsibility passes a request until *one* handler takes it.
5. Django signals, GUI event listeners, message brokers like Kafka/Redis pub/sub.

</details>

## More examples

Runnable script (added to your companion repository with this lesson): [`behavioralPattern/observerPattern.py`](https://github.com/M-Hammad-Faisal/design-patterns-python/blob/master/behavioralPattern/observerPattern.py)

[Family overview](README.md) · [All patterns](../README.md)
