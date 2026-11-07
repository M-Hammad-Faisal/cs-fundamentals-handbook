# Design Patterns III: Behavioral Patterns

## 1. The idea

**Behavioral patterns** deal with **how objects communicate and divide responsibility**: who does what, who is told what, and how algorithms or workflows can be swapped without rewriting the callers. They replace tangled conditionals and tight coupling with small collaborating objects.

| Pattern | Problem it solves |
|---------|-------------------|
| **Strategy** | Swap an algorithm at runtime |
| **Observer** | Notify many dependents when something changes |
| **Command** | Turn a request into an object (queue, log, undo) |
| **State** | Behavior changes with internal state, without giant `if` blocks |
| **Template Method** | Fixed skeleton, variable steps |
| **Iterator** | Traverse a collection without exposing its structure |
| **Chain of Responsibility** | Pass a request along handlers until one handles it |
| **Mediator** | Centralize communication between many objects |
| **Memento** | Capture and restore state (undo/snapshots) |
| **Visitor** | Add operations to a class hierarchy without editing it |
| **Null Object** | Replace `None` checks with a do-nothing object |

Prerequisites: [polymorphism](../polymorphism-dunder/README.md) and [composition](../composition-design/README.md).

## 2. Strategy

**Intent:** define a family of interchangeable algorithms, encapsulate each, and let the client choose one at runtime.

```python
from abc import ABC, abstractmethod

class ShippingStrategy(ABC):
    @abstractmethod
    def cost(self, weight_kg): ...

class Standard(ShippingStrategy):
    def cost(self, weight_kg): return 5 + 1.0 * weight_kg
class Express(ShippingStrategy):
    def cost(self, weight_kg): return 15 + 2.5 * weight_kg

class Order:
    def __init__(self, weight_kg, strategy):
        self.weight_kg, self.strategy = weight_kg, strategy
    def shipping(self):
        return self.strategy.cost(self.weight_kg)

order = Order(2, Standard())
print(order.shipping())                  # 7.0
order.strategy = Express()               # swap at runtime
print(order.shipping())                  # 20.0
```

**Pythonic version: a strategy is just a function.** If the strategy has no state, pass a callable:

```python
def standard(kg): return 5 + kg
def express(kg): return 15 + 2.5 * kg

def shipping_cost(weight, strategy=standard):
    return strategy(weight)

print(shipping_cost(2), shipping_cost(2, express), shipping_cost(2, lambda kg: 0))   # 7 20.0 0
```

Built-in strategies: `sorted(items, key=...)`, `max(..., key=...)`, `logging` formatters, and `functools.partial`. Strategy removes `if method == "x"` ladders and satisfies the Open/Closed Principle ([SOLID](../solid/README.md)).

## 3. Observer

**Intent:** when one object (the **subject**/publisher) changes, **all registered observers** (subscribers) are notified automatically, without the subject knowing who they are.

```python
class EventEmitter:
    def __init__(self):
        self._handlers = {}
    def subscribe(self, event, handler):
        self._handlers.setdefault(event, []).append(handler)
        return lambda: self._handlers[event].remove(handler)      # returns an unsubscribe function
    def emit(self, event, *args):
        for handler in list(self._handlers.get(event, [])):       # copy: handlers may unsubscribe while iterating
            handler(*args)

class Stock:
    def __init__(self, symbol, price):
        self.symbol, self._price, self.events = symbol, price, EventEmitter()
    @property
    def price(self): return self._price
    @price.setter
    def price(self, value):
        old, self._price = self._price, value
        self.events.emit("price_changed", self.symbol, old, value)

log = []
stock = Stock("ACME", 100)
unsubscribe = stock.events.subscribe("price_changed", lambda s, o, n: log.append(f"chart: {s} {o}->{n}"))
stock.events.subscribe("price_changed", lambda s, o, n: n > 120 and log.append(f"alert: {s} spiked"))
stock.price = 110
stock.price = 130
unsubscribe()
stock.price = 90                                                  # chart no longer notified
print(log)
# ['chart: ACME 100->110', 'chart: ACME 110->130', 'alert: ACME spiked']
```

Variations: **pub/sub** with a message broker between publisher and subscribers (Redis, Kafka, RabbitMQ), **signals** (Django `post_save`, Blinker), UI event listeners, reactive streams. Pitfalls: **memory leaks** (a long-lived subject keeps observers alive: unsubscribe or use `weakref`), unpredictable **ordering**, **cascading** updates, and exceptions in one handler affecting others (decide whether to isolate them).

## 4. Command

**Intent:** encapsulate a request as an **object** so you can parameterize, **queue**, **log** and **undo** operations.

```python
class TextEditor:
    def __init__(self): self.text = ""

class InsertCommand:
    def __init__(self, editor, s): self.editor, self.s = editor, s
    def execute(self): self.editor.text += self.s
    def undo(self): self.editor.text = self.editor.text[:-len(self.s)]

class DeleteLastCommand:
    def __init__(self, editor, n): self.editor, self.n, self.removed = editor, n, ""
    def execute(self):
        self.removed = self.editor.text[-self.n:]
        self.editor.text = self.editor.text[:-self.n]
    def undo(self): self.editor.text += self.removed

class History:
    def __init__(self): self._done, self._undone = [], []
    def run(self, cmd):
        cmd.execute(); self._done.append(cmd); self._undone.clear()
    def undo(self):
        if self._done:
            cmd = self._done.pop(); cmd.undo(); self._undone.append(cmd)
    def redo(self):
        if self._undone:
            cmd = self._undone.pop(); cmd.execute(); self._done.append(cmd)

ed, hist = TextEditor(), History()
hist.run(InsertCommand(ed, "Hello"))
hist.run(InsertCommand(ed, " world"))
hist.run(DeleteLastCommand(ed, 3))
print(repr(ed.text))          # 'Hello wo'
hist.undo(); print(repr(ed.text))     # 'Hello world'
hist.undo(); print(repr(ed.text))     # 'Hello'
hist.redo(); print(repr(ed.text))     # 'Hello world'
```

Uses: undo/redo, **task queues** (Celery tasks are serialized commands), macros, transaction logs, job schedulers, GUI actions bound to menu items and shortcuts, **event sourcing**. In Python simple commands are often `functools.partial(func, args)` or closures.

## 5. State

**Intent:** let an object **alter its behavior when its internal state changes**; it appears to change class. Each state is an object that handles the same operations in its own way, replacing large `if state == ...` ladders.

```python
class Order:
    def __init__(self):
        self.state = Pending()
    def pay(self):    self.state = self.state.pay(self)
    def ship(self):   self.state = self.state.ship(self)
    def cancel(self): self.state = self.state.cancel(self)

class State:
    name = "?"
    def pay(self, order):    raise ValueError(f"cannot pay in state {self.name}")
    def ship(self, order):   raise ValueError(f"cannot ship in state {self.name}")
    def cancel(self, order): raise ValueError(f"cannot cancel in state {self.name}")

class Pending(State):
    name = "pending"
    def pay(self, order): return Paid()
    def cancel(self, order): return Cancelled()
class Paid(State):
    name = "paid"
    def ship(self, order): return Shipped()
    def cancel(self, order): return Cancelled()
class Shipped(State):
    name = "shipped"
class Cancelled(State):
    name = "cancelled"

o = Order()
o.pay(); o.ship()
print(o.state.name)                     # shipped
try:
    o.cancel()
except ValueError as e:
    print(e)                            # cannot cancel in state shipped
```

State machines model order lifecycles, TCP connections, document workflows (draft, review, published), game character behavior, and parsers. For simple cases a **transition table** (dict of `(state, event) -> new_state`) is clearer than classes; the pattern pays off when each state has substantial behavior.

## 6. Template Method

**Intent:** define the **skeleton of an algorithm** in a base class and let subclasses override specific steps without changing the structure.

```python
from abc import ABC, abstractmethod

class ReportGenerator(ABC):
    def generate(self, data):                       # the template: fixed order
        rows = self.collect(data)
        body = self.format(rows)
        return self.header() + body + self.footer()
    @abstractmethod
    def collect(self, data): ...
    @abstractmethod
    def format(self, rows): ...
    def header(self): return ""                     # optional hooks with defaults
    def footer(self): return ""

class CsvReport(ReportGenerator):
    def collect(self, data): return [(k, v) for k, v in sorted(data.items())]
    def format(self, rows): return "\n".join(f"{k},{v}" for k, v in rows)
    def header(self): return "key,value\n"

print(CsvReport().generate({"b": 2, "a": 1}))
# key,value
# a,1
# b,2
```

"Hollywood principle": *don't call us, we'll call you*. Frameworks use it everywhere: `unittest.TestCase.setUp/tearDown`, Django class-based views (`get_queryset`, `get_context_data`), `threading.Thread.run`. Its cost is coupling to inheritance; the Strategy pattern gets the same flexibility through composition (you can combine both).

## 7. Iterator

**Intent:** traverse a collection's elements **without exposing its internal representation**. In Python this pattern is built into the language (`__iter__`/`__next__`, `for`, generators); see [polymorphism and the data model](../polymorphism-dunder/README.md).

```python
class Tree:
    def __init__(self, value, left=None, right=None):
        self.value, self.left, self.right = value, left, right
    def __iter__(self):                              # in-order traversal as a generator
        if self.left:
            yield from self.left
        yield self.value
        if self.right:
            yield from self.right

t = Tree(4, Tree(2, Tree(1), Tree(3)), Tree(6, Tree(5), Tree(7)))
print(list(t), sum(t), max(t))                       # [1, 2, 3, 4, 5, 6, 7] 28 7

def batched(iterable, n):                            # a reusable lazy iterator utility
    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) == n:
            yield batch
            batch = []
    if batch:
        yield batch

print(list(batched(range(7), 3)))                    # [[0, 1, 2], [3, 4, 5], [6]]
```

You can offer several traversals (`in_order()`, `level_order()`) as separate generator methods without changing the tree's structure.

## 8. Chain of Responsibility

**Intent:** pass a request along a **chain of handlers**; each decides to handle it or pass it on. Decouples the sender from receivers and lets you reorder or add handlers.

```python
class Handler:
    def __init__(self, next_handler=None):
        self.next = next_handler
    def handle(self, request):
        if self.can_handle(request):
            return self.process(request)
        if self.next:
            return self.next.handle(request)
        return f"no handler for {request!r}"
    def can_handle(self, request): raise NotImplementedError
    def process(self, request): raise NotImplementedError

class AuthHandler(Handler):
    def can_handle(self, r): return not r.get("user")
    def process(self, r): return "401 unauthenticated"
class RateLimitHandler(Handler):
    def can_handle(self, r): return r.get("calls", 0) > 100
    def process(self, r): return "429 too many requests"
class AppHandler(Handler):
    def can_handle(self, r): return True
    def process(self, r): return f"200 hello {r['user']}"

chain = AuthHandler(RateLimitHandler(AppHandler()))
print(chain.handle({}), "|", chain.handle({"user": "ana", "calls": 500}), "|", chain.handle({"user": "ana", "calls": 3}))
# 401 unauthenticated | 429 too many requests | 200 hello ana
```

This is how **middleware** works (Django, Express, ASGI/WSGI stacks, logging filters), exception propagation through the call stack, and approval workflows ("manager, then director, then VP"). Each link either handles the request, or calls the next; the order of the chain is configuration.

## 9. Mediator

**Intent:** replace many-to-many direct connections between objects with a **central coordinator**, so components talk only to the mediator.

```python
class ChatRoom:                                      # the mediator
    def __init__(self):
        self.users = {}
    def join(self, user):
        self.users[user.name] = user
        user.room = self
    def send(self, sender, text, to=None):
        targets = [self.users[to]] if to else [u for n, u in self.users.items() if n != sender.name]
        for u in targets:
            u.receive(sender.name, text)

class User:
    def __init__(self, name):
        self.name, self.inbox, self.room = name, [], None
    def say(self, text, to=None):
        self.room.send(self, text, to)
    def receive(self, sender, text):
        self.inbox.append(f"{sender}: {text}")

room = ChatRoom()
ana, bo, cy = User("ana"), User("bo"), User("cy")
for u in (ana, bo, cy):
    room.join(u)
ana.say("hi all"); bo.say("psst", to="cy")
print(bo.inbox, cy.inbox)                            # ['ana: hi all'] ['ana: hi all', 'bo: psst']
```

Users never reference each other, so adding a participant touches only the room. Examples: air traffic control, GUI dialogs where widgets enable/disable each other through a dialog controller, event buses, message brokers. Risk: the mediator can grow into a god object.

## 10. Memento

**Intent:** capture an object's internal state in a **snapshot** so it can be restored later, without violating encapsulation.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Snapshot:                                      # the memento: opaque, immutable
    text: str
    cursor: int

class Document:
    def __init__(self):
        self.text, self.cursor = "", 0
    def type(self, s):
        self.text = self.text[:self.cursor] + s + self.text[self.cursor:]
        self.cursor += len(s)
    def save(self): return Snapshot(self.text, self.cursor)
    def restore(self, snap): self.text, self.cursor = snap.text, snap.cursor

doc, checkpoints = Document(), []
doc.type("hello"); checkpoints.append(doc.save())
doc.type(" world"); checkpoints.append(doc.save())
doc.type("!!!")
doc.restore(checkpoints[0])
print(doc.text, doc.cursor)                          # hello 5
```

Uses: undo stacks, editor checkpoints, game saves, database savepoints and transactions, "dry run then rollback". Mementos can be memory heavy; store diffs (as Command's `undo` does) or limit history.

## 11. Visitor

**Intent:** separate **operations** from the **object structure** they work on, so you can add new operations without modifying the classes. Useful for stable class hierarchies (like syntax trees) where you keep adding operations.

```python
class Num:
    def __init__(self, v): self.v = v
    def accept(self, visitor): return visitor.visit_num(self)
class Add:
    def __init__(self, l, r): self.l, self.r = l, r
    def accept(self, visitor): return visitor.visit_add(self)
class Mul:
    def __init__(self, l, r): self.l, self.r = l, r
    def accept(self, visitor): return visitor.visit_mul(self)

class Evaluator:
    def visit_num(self, n): return n.v
    def visit_add(self, n): return n.l.accept(self) + n.r.accept(self)
    def visit_mul(self, n): return n.l.accept(self) * n.r.accept(self)

class Printer:
    def visit_num(self, n): return str(n.v)
    def visit_add(self, n): return f"({n.l.accept(self)} + {n.r.accept(self)})"
    def visit_mul(self, n): return f"{n.l.accept(self)} * {n.r.accept(self)}"

expr = Mul(Add(Num(2), Num(3)), Num(4))
print(expr.accept(Printer()), "=", expr.accept(Evaluator()))     # (2 + 3) * 4 = 20
```

Adding a new operation (`ComplexityCounter`, `Optimizer`) needs **no change** to `Num/Add/Mul`; adding a new node type requires editing every visitor (the trade-off). Python alternatives: `functools.singledispatch` (dispatch on type without `accept` methods), `match` statements, and `ast.NodeVisitor` in the standard library (which dispatches to `visit_ClassName`).

```python
from functools import singledispatch

@singledispatch
def evaluate(node): raise TypeError(type(node).__name__)

@evaluate.register
def _(node: Num): return node.v
@evaluate.register
def _(node: Add): return evaluate(node.l) + evaluate(node.r)
@evaluate.register
def _(node: Mul): return evaluate(node.l) * evaluate(node.r)

print(evaluate(expr))                                # 20
```

## 12. Null Object

**Intent:** provide an object with **neutral, do-nothing behavior** instead of `None`, so callers never need `if x is not None` checks.

```python
class Logger:
    def info(self, msg): print("LOG:", msg)

class NullLogger:
    def info(self, msg): pass                       # does nothing, safely

def process(items, logger=None):
    logger = logger or NullLogger()                 # callers may omit the logger
    for item in items:
        logger.info(f"processing {item}")
    return len(items)

print(process([1, 2]))                              # 2   (no output)
print(process([1], Logger()))                       # LOG: processing 1  then 1
```

Real uses: `logging.NullHandler`, `contextlib.nullcontext`, `unittest.mock`, empty iterators/collections instead of `None`, Django's `AnonymousUser`. Do not hide real errors with null objects; use them where "nothing happens" is a valid behavior.

## 13. Choosing among behavioral patterns

| Situation | Pattern |
|-----------|---------|
| Several interchangeable algorithms | Strategy (or just pass a function) |
| One-to-many notification | Observer / pub-sub |
| Undo/redo, queues, logging requests | Command (+ Memento for snapshots) |
| Behavior depends on lifecycle state | State (or a transition table) |
| Same algorithm skeleton, different steps | Template Method |
| Traverse without exposing structure | Iterator (generators) |
| Request passes through filters/middleware | Chain of Responsibility |
| Many peers talking to each other | Mediator |
| Add operations to a stable hierarchy | Visitor / `singledispatch` |
| Avoid `None` checks | Null Object |

## 14. Two real-world examples

### Example 1: A web framework request pipeline
A request flows through **Chain of Responsibility** middleware (security headers, authentication, session loading, rate limiting) until a view handles it. The view runs in a **Template Method** (`dispatch` calls `get`/`post`). Authorization uses **Strategy** (pluggable permission classes). Saving a model fires **Observer** signals (`post_save`) that update caches and send emails without the model knowing. Background work is queued as **Commands** (serialized task name plus arguments) for workers to run later, with retries.

### Example 2: A trading or e-commerce order engine
An order is a **State** machine (`created -> paid -> packed -> shipped -> delivered`, with `cancelled` and `refunded` branches). Each state change emits events (**Observer**) consumed by inventory, accounting and notification services. Discount and tax rules are **Strategies** chosen per region. Every user action is recorded as a **Command** in an append-only log, so any order can be rebuilt (event sourcing) or reversed (compensating commands). Snapshots (**Memento**) speed up rebuilding long histories.

## 15. Tips, tricks and pitfalls

- In Python, first ask whether a **function**, **generator**, **decorator** or **dictionary** replaces the pattern's classes.
- Strategy: pass callables for stateless algorithms; classes when they hold configuration.
- Observer: always provide **unsubscribe**; beware leaks, ordering and exceptions in handlers.
- Command: make commands small and reversible (`execute`/`undo`), store everything needed to undo.
- State: if states only differ in a few transitions, a transition table is simpler than a class per state.
- Template Method couples through inheritance; prefer Strategy when the variation should change at runtime.
- Visitor makes new operations easy and new node types hard; choose it only for stable hierarchies.
- Do not let a Mediator or an event bus turn into a hidden global dependency graph; keep event names and payloads documented.
- Patterns combine: Command + Memento (undo), Chain + Strategy (middleware with pluggable rules), State + Observer (workflow events).

## 16. Check yourself

1. What is the difference between Strategy and State?
2. How does Observer decouple a subject from its listeners and what are its risks?
3. How does Command make undo possible?
4. When would you replace State classes with a transition table?
5. Template Method versus Strategy?
6. Why is the Iterator pattern "built in" to Python?
7. Explain Chain of Responsibility with a middleware example.
8. What does Mediator reduce and what is its main risk?
9. What is the trade-off of Visitor?
10. Why use a Null Object instead of `None`?

<details>
<summary>Answers</summary>

1. Both delegate behavior to an object. Strategy: the **client** picks an interchangeable algorithm and the strategies usually do not know each other. State: the object **changes its own behavior** as its state changes, and states typically trigger transitions to other states.
2. The subject only knows a list of callables or an interface and calls them; it does not know their concrete classes. Risks: memory leaks if observers are never removed, unpredictable ordering, cascading updates, and failures in one handler affecting others.
3. Each command stores what it needs and implements `undo` as the inverse of `execute`; a history stack of executed commands lets you pop and undo, and a second stack allows redo.
4. When states differ only in which events are legal and what the next state is, with little state-specific behavior: a dictionary mapping `(state, event)` to the next state is shorter and easier to audit.
5. Template Method fixes an algorithm's skeleton in a base class and varies steps through subclassing (compile-time, inheritance). Strategy injects the varying algorithm as an object or function (runtime, composition).
6. Because `for`, comprehensions, `sum`, `list` and unpacking all use `__iter__`/`__next__`, and generators (`yield`) create iterators with no boilerplate.
7. Each middleware examines the request and either responds (for example 401 for missing auth) or passes it to the next; handlers can be added, removed or reordered without changing the others.
8. It reduces many-to-many dependencies to many-to-one (components talk only to the mediator). Risk: the mediator becomes a complex god object holding all the logic.
9. Adding new operations is easy (a new visitor, no edits to node classes) but adding a new node type forces changes in every visitor.
10. Callers can call methods without `None` checks, removing conditionals and a class of `AttributeError` bugs; the object's neutral behavior is the right default.

</details>

[Exercises](exercises.md) · [Summary](summary.md)
