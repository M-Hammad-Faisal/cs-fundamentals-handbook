# Design Patterns: Exercises

Try each problem before opening its solution. These are the practice problems of this topic's lessons, collected in one place.

## Chain of Responsibility Pattern

1. Implement an expense approval chain with limits 100, 1000, 10000.
2. Add a "log everything" handler that logs and always passes on.
3. Write a middleware chain that adds timing and catches exceptions, returning `500`.

<details>
<summary>Solutions</summary>

**1.**
```python no-run
class Approver:
    def __init__(self, name, limit, next_approver=None):
        self.name, self.limit, self.next = name, limit, next_approver
    def approve(self, amount):
        if amount <= self.limit:
            return f"{self.name} approved {amount}"
        if self.next:
            return self.next.approve(amount)
        return f"{amount} needs board approval"
chain = Approver("lead", 100, Approver("manager", 1000, Approver("director", 10000)))
print(chain.approve(50), "|", chain.approve(5000), "|", chain.approve(50000))
```

**2.**
```python no-run
def audit(next_fn, sink):
    def handler(req):
        sink.append(req)
        return next_fn(req)
    return handler
seen = []
app2 = audit(view, seen)
app2({"path": "/z"}); print(seen)
```

**3.**
```python no-run
import time
def timing(next_fn, sink):
    def handler(req):
        t = time.perf_counter()
        try:
            return next_fn(req)
        finally:
            sink.append(time.perf_counter() - t)         # record how long the rest of the chain took
    return handler
def errors(next_fn):
    def handler(req):
        try:
            return next_fn(req)
        except Exception:
            return "500 server error"
    return handler
def boom(req): raise RuntimeError
durations = []
print(errors(timing(boom, durations))({}), errors(timing(view, durations))({"path": "/ok"}), len(durations))
# 500 server error 200 secret page /ok 2
```

</details>

## Command Pattern

1. Implement a `Calculator` with `Add` and `Multiply` commands supporting undo/redo.
2. Add a `MacroCommand` that is undone in reverse.
3. Make a command queue that retries failed commands up to 3 times.

<details>
<summary>Solutions</summary>

**1.**
```python no-run
class Calc:
    def __init__(self): self.value = 0
class Add:
    def __init__(self, c, n): self.c, self.n = c, n
    def execute(self): self.c.value += self.n
    def undo(self): self.c.value -= self.n
class Mul:
    def __init__(self, c, n): self.c, self.n, self.prev = c, n, None
    def execute(self): self.prev = self.c.value; self.c.value *= self.n
    def undo(self): self.c.value = self.prev
calc, hist = Calc(), History()
hist.run(Add(calc, 5)); hist.run(Mul(calc, 3)); print(calc.value)          # 15
hist.undo(); print(calc.value); hist.undo(); print(calc.value); hist.redo(); print(calc.value)   # 5 0 5
```

**2.** See `MacroCommand` in the lesson (its `undo` loops `reversed(self.commands)`).

**3.**
```python no-run
def run_with_retries(command, attempts=3):
    for n in range(1, attempts + 1):
        try:
            return command()
        except Exception:
            if n == attempts:
                raise
tries = []
def flaky():
    tries.append(1)
    if len(tries) < 3: raise RuntimeError
    return "ok"
print(run_with_retries(flaky), len(tries))                                  # ok 3
```

</details>

## Interpreter Pattern

1. Add `Not` and a `Less` operator to the rule engine.
2. Extend the parser to support unary minus (`-x + 3`).
3. Why is `ast.parse` plus a whitelist safer than dynamic evaluation of user text?

<details>
<summary>Solutions</summary>

**1.**
```python no-run
class Not(Expression):
    def __init__(self, operand): self.operand = operand
    def interpret(self, ctx): return not self.operand.interpret(ctx)
class Less(Expression):
    def __init__(self, left, right): self.left, self.right = left, right
    def interpret(self, ctx): return self.left.interpret(ctx) < self.right.interpret(ctx)
r = And(Less(Var("age"), Const(18)), Not(Equals(Var("country"), Const("US"))))
print(r.interpret({"age": 10, "country": "PK"}), r.interpret({"age": 10, "country": "US"}))   # True False
```

**2.**
```python no-run
class Parser2(Parser):
    def factor(self):
        if self.peek() == "-":
            self.take()
            return BinOp("-", Const(0), self.factor())          # -x is 0 - x
        return super().factor()
print(Parser2("-x + 3").expr().interpret({"x": 5}))             # -2
```

**3.** The whitelist only allows node types you handle (constants, names, arithmetic), so anything else (function calls, imports, attribute access) is rejected; dynamic evaluation would run arbitrary code with your program's privileges.

</details>

## Iterator Pattern

1. Write a generator `chunks(path, size)` that yields file contents in blocks.
2. Create an iterable `Range2(start, stop, step)` that supports multiple loops.
3. Show why `list(zip(a, a))` on a one-shot iterator behaves unexpectedly.

<details>
<summary>Solutions</summary>

**1.**
```python no-run
import tempfile, os
def chunks(path, size):
    with open(path, "rb") as f:
        while block := f.read(size):
            yield block
p = os.path.join(tempfile.mkdtemp(), "f.bin"); open(p, "wb").write(b"abcdefghij")
print(list(chunks(p, 4)))                               # [b'abcd', b'efgh', b'ij']
```

**2.**
```python no-run
class Range2:
    def __init__(self, start, stop, step=1): self.start, self.stop, self.step = start, stop, step
    def __iter__(self):
        n = self.start
        while n < self.stop:
            yield n
            n += self.step
r = Range2(0, 10, 3)
print(list(r), list(r))                                 # [0, 3, 6, 9] [0, 3, 6, 9]
```

**3.**
```python no-run
it = iter([1, 2, 3, 4])
print(list(zip(it, it)))                                # [(1, 2), (3, 4)]  (both arguments advance the SAME iterator)
```

</details>

## Mediator Pattern

1. Extend `ChatRoom` with a `leave()` method and a mute list.
2. Build a `SignupForm` mediator: when "type" is "company", show a "company name" field; "Submit" enabled only if email is present and terms accepted.
3. What is the difference between a mediator and an observer subject?

<details>
<summary>Solutions</summary>

**1.**
```python no-run
class ChatRoom2(ChatRoom):
    def __init__(self):
        super().__init__()
        self.muted = set()
    def leave(self, user):
        self.users.pop(user.name, None)
    def mute(self, name): self.muted.add(name)
    def send(self, sender, text, to=None):
        if sender.name in self.muted:
            return
        super().send(sender, text, to)
r = ChatRoom2(); a, b = User("a"), User("b"); r.join(a); r.join(b)
r.mute("a"); a.say("hello"); print(b.inbox)             # []
r.muted.clear(); a.say("hello"); r.leave(b); a.say("x"); print(b.inbox)    # ['a: hello']
```

**2.**
```python no-run
class SignupForm:
    def __init__(self):
        self.type, self.email, self.terms = "person", "", False
        self.company_field_visible, self.submit_enabled = False, False
    def set(self, field, value):
        setattr(self, field, value)
        self._refresh()
    def _refresh(self):                                 # the mediator's rules
        self.company_field_visible = self.type == "company"
        self.submit_enabled = bool(self.email) and self.terms
f = SignupForm(); f.set("type", "company"); f.set("email", "a@x.com"); f.set("terms", True)
print(f.company_field_visible, f.submit_enabled)        # True True
```

**3.** A subject broadcasts its own state changes one-way to observers who react independently; a mediator receives messages from peers, applies coordination rules, and sends targeted messages back (many-to-many routed through one point).

</details>

## Memento Pattern

1. Add `redo()` to the `Editor` (keep a second stack).
2. Implement save points for a game `Player` (`hp`, `inventory` list) and show restoring after dying.
3. Compare snapshot undo with command undo for a 10 MB document.

<details>
<summary>Solutions</summary>

**1.**
```python no-run
class Editor2(Editor):
    def __init__(self, max_history=10):
        super().__init__(max_history)
        self.redo_stack = []
    def type(self, s):
        super().type(s); self.redo_stack.clear()
    def undo(self):
        if self.history:
            self.redo_stack.append(self.doc.save())
            self.doc.restore(self.history.pop())
    def redo(self):
        if self.redo_stack:
            self.history.append(self.doc.save())
            self.doc.restore(self.redo_stack.pop())
e2 = Editor2(); e2.type("a"); e2.type("b"); e2.undo(); print(e2.doc.text); e2.redo(); print(e2.doc.text)   # a ab
```

**2.**
```python no-run
class Player:
    def __init__(self): self.hp, self.inventory = 100, ["sword"]
    def save(self): return copy.deepcopy((self.hp, self.inventory))
    def load(self, s): self.hp, self.inventory = copy.deepcopy(s)
p = Player(); save = p.save()
p.hp = 0; p.inventory.clear()
p.load(save); print(p.hp, p.inventory)                  # 100 ['sword']
```

**3.** A snapshot per edit copies up to 10 MB each time (memory grows quickly); a command stores only "inserted 'x' at 120" and its inverse, a few bytes, but needs a correct `undo` for every action. Hybrid: occasional snapshots plus commands between them.

</details>

## Null Object Pattern

1. Make a `NoDiscount` strategy and a `Checkout` that works with or without a discount.
2. Write `find_user(name)` returning a `GuestUser` null object, and a `greet(user)` with no `None` check.
3. When is a null object a bad idea? Give an example.

<details>
<summary>Solutions</summary>

**1.**
```python no-run
class PercentOff:
    def __init__(self, pct): self.pct = pct
    def apply(self, price): return price * (1 - self.pct / 100)
class NoDiscount:
    def apply(self, price): return price
class Checkout:
    def __init__(self, discount=None):
        self.discount = discount or NoDiscount()
    def total(self, price): return self.discount.apply(price)
print(Checkout().total(100), Checkout(PercentOff(25)).total(100))      # 100 75.0
```

**2.**
```python no-run
USERS = {"ana": "Ana"}
class GuestUser:
    display = "Guest"
class Member:
    def __init__(self, display): self.display = display
def find_user(name):
    return Member(USERS[name]) if name in USERS else GuestUser()
def greet(user): return f"Hello, {user.display}"
print(greet(find_user("ana")), greet(find_user("zed")))                # Hello, Ana Hello, Guest
```

**3.** A null `PaymentGateway.charge()` that returns success without charging would silently lose money; for operations where "nothing happened" must not look like success, raise an explicit error instead.

</details>

## Observer Pattern

1. Build a `Thermostat` that notifies observers only when the temperature crosses a threshold.
2. Add priorities so higher-priority observers are called first.
3. Make `EventEmitter.once(event, handler)` that runs a handler at most one time.

<details>
<summary>Solutions</summary>

**1.**
```python no-run
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
```python no-run
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
```python no-run
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

## State Pattern

1. Model a traffic light with state classes, then with a transition table.
2. Add a `refund` event to the order that is only allowed from `shipped` (table version).
3. Draw (as text) the state diagram of the order table.

<details>
<summary>Solutions</summary>

**1.**
```python no-run
class Light:
    def __init__(self): self.state = Red()
    def next(self): self.state = self.state.next()
class Red:    name = "red";    next = lambda self: Green()
class Green:  name = "green";  next = lambda self: Yellow()
class Yellow: name = "yellow"; next = lambda self: Red()
l = Light(); seq = []
for _ in range(4): seq.append(l.state.name); l.next()
print(seq)                                              # ['red', 'green', 'yellow', 'red']
CYCLE = {"red": "green", "green": "yellow", "yellow": "red"}
s, table_seq = "red", []
for _ in range(4): table_seq.append(s); s = CYCLE[s]
print(table_seq)
```

**2.**
```python no-run
TRANSITIONS[("shipped", "refund")] = "refunded"
o = SimpleOrder()
for e in ("pay", "ship", "refund"): o.handle(e)
print(o.state)                                          # refunded
```

**3.**
```text
pending --pay--> paid --ship--> shipped --refund--> refunded
   |               |
 cancel          cancel
   v               v
cancelled       cancelled
```

</details>

## Strategy Pattern

1. Implement price strategies `Regular`, `Student` (20% off), `Bulk` (10% off for quantity >= 10) as classes and as a dictionary of functions.
2. Implement text compression strategies `NoCompression` and `Reverse` (silly) and a `Sender` that uses either.
3. Replace the ladder in section 2 with a dictionary of strategies and an `unknown method` error.

<details>
<summary>Solutions</summary>

**1.**
```python no-run
class Regular:
    def total(self, price, qty): return price * qty
class Student:
    def total(self, price, qty): return price * qty * 0.8
class Bulk:
    def total(self, price, qty): return price * qty * (0.9 if qty >= 10 else 1)
print(Student().total(10, 2), Bulk().total(10, 10))                # 16.0 90.0
FUNCS = {"regular": lambda p, q: p * q, "student": lambda p, q: p * q * 0.8,
         "bulk": lambda p, q: p * q * (0.9 if q >= 10 else 1)}
print(FUNCS["bulk"](10, 10))
```

**2.**
```python no-run
class NoCompression:
    def pack(self, text): return text
class Reverse:
    def pack(self, text): return text[::-1]
class Sender:
    def __init__(self, strategy): self.strategy = strategy
    def send(self, text): return self.strategy.pack(text)
print(Sender(NoCompression()).send("abc"), Sender(Reverse()).send("abc"))     # abc cba
```

**3.**
```python no-run
RATES = {"standard": lambda w: 5 + w, "express": lambda w: 15 + 2.5 * w, "overnight": lambda w: 30 + 4 * w}
def shipping_cost2(method, weight):
    try:
        return RATES[method](weight)
    except KeyError:
        raise ValueError(f"unknown shipping method {method!r}") from None
print(shipping_cost2("express", 2))                                           # 20.0
```

</details>

## Template Method Pattern

1. Write a `Beverage` template with `boil_water`, `brew`, `pour`, `add_condiments` (hook); implement `Tea` and `Coffee`.
2. Add a hook `should_cache()` to `DataPipeline` that skips `load` when false.
3. Rewrite the pipeline using functions instead of subclasses.

<details>
<summary>Solutions</summary>

**1.**
```python no-run
class Beverage(ABC):
    def prepare(self):
        steps = ["boil water", self.brew(), "pour in cup"]
        if self.wants_condiments():
            steps.append(self.add_condiments())
        return steps
    @abstractmethod
    def brew(self): ...
    @abstractmethod
    def add_condiments(self): ...
    def wants_condiments(self): return True
class Tea(Beverage):
    def brew(self): return "steep tea bag"
    def add_condiments(self): return "add lemon"
class Coffee(Beverage):
    def brew(self): return "drip coffee"
    def add_condiments(self): return "add milk"
    def wants_condiments(self): return False
print(Tea().prepare(), Coffee().prepare())
```

**2.**
```python no-run
class CachedPipeline(DataPipeline):
    def should_cache(self): return True
    def run(self):
        rows = self.transform(self.extract())
        return None if not self.should_cache() else self.load(rows)
class Demo(CachedPipeline, Doubler): pass
print(Demo().run())
```
(Better: add the `should_cache` hook inside `DataPipeline.run` itself so every subclass benefits.)

**3.** `pipeline(extract, transform, load)` shown above; the "steps" are plain functions.

</details>

## Visitor Pattern

1. Add a `Neg` node (unary minus) and update `Evaluator`, `Printer`, `DepthCounter`. Note what you had to edit.
2. Write a visitor that collects all `Num` values in an expression.
3. Implement `simplify` with `singledispatch` that turns `x * 1` and `x + 0` into `x`.

<details>
<summary>Solutions</summary>

**1.**
```python no-run
class Neg:
    def __init__(self, operand): self.operand = operand
    def accept(self, visitor): return visitor.visit_neg(self)
Evaluator.visit_neg = lambda self, n: -n.operand.accept(self)
Printer.visit_neg = lambda self, n: f"-{n.operand.accept(self)}"
DepthCounter.visit_neg = lambda self, n: 1 + n.operand.accept(self)
e2 = Add(Num(1), Neg(Num(5)))
print(e2.accept(Printer()), "=", e2.accept(Evaluator()), "depth", e2.accept(DepthCounter()))   # (1 + -5) = -4 depth 3
```
Adding a node type forced edits to **every visitor**: the visitor trade-off.

**2.**
```python no-run
class NumCollector:
    def __init__(self): self.values = []
    def visit_num(self, n): self.values.append(n.value)
    def visit_add(self, n): n.left.accept(self); n.right.accept(self)
    visit_mul = visit_add
nc = NumCollector(); expr.accept(nc); print(nc.values)                # [2, 3, 4]
```

**3.**
```python no-run
@singledispatch
def simplify(node): return node
@simplify.register
def _(node: Add):
    l, r = simplify(node.left), simplify(node.right)
    if isinstance(r, Num) and r.value == 0: return l
    if isinstance(l, Num) and l.value == 0: return r
    return Add(l, r)
@simplify.register
def _(node: Mul):
    l, r = simplify(node.left), simplify(node.right)
    if isinstance(r, Num) and r.value == 1: return l
    if isinstance(l, Num) and l.value == 1: return r
    return Mul(l, r)
print(Printer().visit_num(Num(7)), simplify(Mul(Add(Num(5), Num(0)), Num(1))).accept(Printer()))   # 7 5
```

</details>

## Abstract Factory Pattern

1. Build `WindowsFactory`/`MacFactory` creating `Button` and `Scrollbar`, and a `settings_panel(factory)` function.
2. Add a `HighContrastFactory` family without editing `build_form`.
3. Show a test that passes a fake factory recording what was created.

<details>
<summary>Solutions</summary>

**1.**
```python no-run
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
```python no-run
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
```python no-run
class RecordingFactory(ThemeFactory):
    def __init__(self): self.created = []
    def create_button(self): self.created.append("button"); return LightButton()
    def create_checkbox(self): self.created.append("checkbox"); return LightCheckbox()
rf = RecordingFactory(); build_form(rf); print(rf.created)    # ['button', 'checkbox']
```

</details>

## Builder Pattern

1. Write `QueryBuilder` with `select(*cols)`, `from_(table)`, `where(cond)`, `limit(n)` and `build()` returning a SQL string. Require `from_`.
2. Make a dataclass with `__post_init__` that rejects `limit < 0`.
3. Ensure a builder can be reused safely by resetting state after `build()`.

<details>
<summary>Solutions</summary>

**1.**
```python no-run
class QueryBuilder:
    def __init__(self):
        self._cols, self._table, self._wheres, self._limit = ["*"], None, [], None
    def select(self, *cols): self._cols = list(cols); return self
    def from_(self, table): self._table = table; return self
    def where(self, cond): self._wheres.append(cond); return self
    def limit(self, n): self._limit = n; return self
    def build(self):
        if not self._table:
            raise ValueError("from_() is required")
        sql = f"SELECT {', '.join(self._cols)} FROM {self._table}"
        if self._wheres: sql += " WHERE " + " AND ".join(self._wheres)
        if self._limit is not None: sql += f" LIMIT {self._limit}"
        return sql
print(QueryBuilder().select("id", "name").from_("users").where("age > 18").limit(5).build())
# SELECT id, name FROM users WHERE age > 18 LIMIT 5
```

**2.**
```python no-run
@dataclass
class Page:
    limit: int = 10
    def __post_init__(self):
        if self.limit < 0: raise ValueError("limit must be >= 0")
try: Page(limit=-1)
except ValueError as e: print(e)
```

**3.**
```python no-run
class ReusableBuilder(PizzaBuilder):
    def build(self):
        pizza = super().build()
        self.__init__()                              # reset to defaults
        return pizza
rb = ReusableBuilder()
print(rb.topping("a").build(), rb.build())            # second pizza has no toppings
```

</details>

## Factory Method Pattern

1. Write `shape_from_dict({"type": "circle", "r": 2})` using a registry decorator `@register("circle")`.
2. Create a factory returning different `Notifier` objects (`email`, `sms`) and raising a helpful error for unknown names.
3. Rewrite `export(data, fmt)` from section 2 using the registry factory.

<details>
<summary>Solutions</summary>

**1.**
```python no-run
import math
SHAPES = {}
def register(name):
    def deco(cls):
        SHAPES[name] = cls
        return cls
    return deco

@register("circle")
class Circle2:
    def __init__(self, r): self.r = r
    def area(self): return math.pi * self.r ** 2

@register("rect")
class Rect2:
    def __init__(self, w, h): self.w, self.h = w, h
    def area(self): return self.w * self.h

def shape_from_dict(d):
    d = dict(d)
    return SHAPES[d.pop("type")](**d)

print(round(shape_from_dict({"type": "circle", "r": 2}).area(), 2), shape_from_dict({"type": "rect", "w": 2, "h": 3}).area())
# 12.57 6
```

**2.**
```python no-run
class EmailNotifier:
    def send(self, to, msg): return f"email {to}: {msg}"
class SmsNotifier:
    def send(self, to, msg): return f"sms {to}: {msg}"
def notifier(kind):
    kinds = {"email": EmailNotifier, "sms": SmsNotifier}
    if kind not in kinds:
        raise ValueError(f"unknown notifier {kind!r}; choose from {sorted(kinds)}")
    return kinds[kind]()
print(notifier("sms").send("a", "hi"))
try:
    notifier("fax")
except ValueError as e:
    print(e)
```

**3.**
```python no-run
def export(data, fmt):
    return Exporter.create(fmt).export(data)       # no if/elif ladder
print(export("x", "pdf"))                          # pdf:x
```

</details>

## Object Pool Pattern

1. Add a `max_uses` limit so each pooled connection is replaced after 3 uses.
2. Add a health check: if `conn.alive` is false when returned, replace it with a new one.
3. Why is a pool of integers a bad idea in Python?

<details>
<summary>Solutions</summary>

**1.**
```python no-run
class ReplacingPool(Pool):
    def __init__(self, size, max_uses=3):
        super().__init__(size)
        self.max_uses, self.uses = max_uses, {}
    @contextmanager
    def acquire(self, timeout=1.0):
        with super().acquire(timeout) as conn:
            yield conn
            self.uses[conn.id] = self.uses.get(conn.id, 0) + 1
rp = ReplacingPool(1)
for _ in range(2):
    with rp.acquire() as c: pass
print(rp.uses)
```
(In production you would close the old connection and put a fresh one back when the count hits `max_uses`.)

**2.**
```python no-run
class HealthyPool(Pool):
    @contextmanager
    def acquire(self, timeout=1.0):
        conn = self._free.get(timeout=timeout)
        try:
            yield conn
        finally:
            self._free.put(conn if getattr(conn, "alive", True) else Connection())
hp = HealthyPool(1)
with hp.acquire() as c:
    c.alive = False
with hp.acquire() as c2:
    print(c2.alive if hasattr(c2, "alive") else "fresh connection")     # fresh connection
```

**3.** Creating a Python `int` is already cheap and ints are immutable, so a pool adds locking overhead and complexity for no gain; pools are for objects that are expensive to create or limited in number.

</details>

## Prototype Pattern

1. Show the shallow-copy bug with a list-of-lists and fix it.
2. Write `__deepcopy__` for a class that holds a large shared `texture` string (do not copy it) and a mutable `stats` dict (copy it).
3. Use `replace` to create three `ServerConfig` variants from one base.

<details>
<summary>Solutions</summary>

**1.**
```python no-run
grid = [[0, 0], [0, 0]]
bad = copy.copy(grid); bad[0][0] = 9
print(grid)                                         # [[9, 0], [0, 0]]  (shared inner list)
grid = [[0, 0], [0, 0]]
good = copy.deepcopy(grid); good[0][0] = 9
print(grid)                                         # [[0, 0], [0, 0]]
```

**2.**
```python no-run
class Sprite:
    def __init__(self, texture, stats):
        self.texture, self.stats = texture, stats
    def __deepcopy__(self, memo):
        return Sprite(self.texture, copy.deepcopy(self.stats, memo))   # share texture, copy stats
a = Sprite("T" * 1000, {"hp": 1})
b = copy.deepcopy(a); b.stats["hp"] = 5
print(a.stats, b.texture is a.texture)              # {'hp': 1} True
```

**3.**
```python no-run
variants = [replace(base, port=p) for p in (81, 82, 83)]
print([v.port for v in variants])                   # [81, 82, 83]
```

</details>

## Singleton Pattern

1. Make a `Counter` singleton with `increment()` and show two names share the count.
2. Prove the `__new__` version is safe with 20 threads creating instances.
3. Rewrite a Singleton `Logger` as a module-level object plus a function parameter, and show how a test can pass a fake logger.

<details>
<summary>Solutions</summary>

**1.**
```python no-run
class Counter(Singleton):
    def __init__(self):
        if not hasattr(self, "n"):
            self.n = 0
    def increment(self):
        self.n += 1
        return self.n
a, b = Counter(), Counter()
a.increment(); b.increment()
print(a.n, a is b)                                 # 2 True
```

**2.**
```python no-run
import threading
seen = set()
def make():
    seen.add(id(Config()))
threads = [threading.Thread(target=make) for _ in range(20)]
for t in threads: t.start()
for t in threads: t.join()
print(len(seen))                                   # 1
```

**3.**
```python no-run
class Logger:
    def __init__(self): self.lines = []
    def log(self, msg): self.lines.append(msg)
logger = Logger()                                  # module-level instance = the singleton

def process(item, log=logger.log):                 # inject; defaults to the shared one
    log(f"processing {item}")

fake = []
process("x", log=fake.append)                      # a test passes a fake
print(fake, logger.lines)                          # ['processing x'] []
```

</details>

## Adapter Pattern

1. Adapt a `LegacyPrinter.print_text(s)` to a `Printer.print(doc)` interface where `doc` has `.title` and `.body`.
2. Write an adapter so an `XmlWeather.get()` returning `"<t>21</t>"` fits `WeatherSource.temperature() -> float`.
3. Why is the object adapter usually better than the class adapter?

<details>
<summary>Solutions</summary>

**1.**
```python no-run
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
```python no-run
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

## Bridge Pattern

1. Add a `Triangle` shape and a `CanvasRenderer` to the example without editing existing shapes or renderers (other than interface additions).
2. Build a `RemoteControl`/`Device` bridge with `Tv` and `Radio` devices and `BasicRemote`/`AdvancedRemote` (with `mute()`).
3. How many classes without Bridge for 6 shapes x 4 renderers? With Bridge?

<details>
<summary>Solutions</summary>

**1.** (renderer interface grows by one method):
```python no-run
class CanvasRenderer(Renderer):
    def circle(self, r): return f"canvas.arc({r})"
    def square(self, side): return f"canvas.rect({side})"
print(Circle(CanvasRenderer(), 1).draw(), Square(CanvasRenderer(), 2).draw())
```

**2.**
```python no-run
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

## Composite Pattern

1. Add `count_files()` and `find(name)` to the `Folder`/`File` classes.
2. Model an organization chart where `Employee` and `Manager` both have `salary_cost()` (a manager includes reports).
3. Write an iterative (non-recursive) traversal using a stack.

<details>
<summary>Solutions</summary>

**1.**
```python no-run
class File2(File):
    def count_files(self): return 1
    def find(self, name): return self if self.name == name else None
class Folder2(Folder):
    def count_files(self): return sum(c.count_files() for c in self.children)
    def find(self, name):
        if self.name == name: return self
        for c in self.children:
            hit = c.find(name)
            if hit: return hit
        return None
r = Folder2("r").add(File2("a", 1)).add(Folder2("d").add(File2("b", 2)))
print(r.count_files(), r.find("b").size())              # 2 2
```

**2.**
```python no-run
class Employee:
    def __init__(self, name, salary): self.name, self.salary = name, salary
    def salary_cost(self): return self.salary
class Manager(Employee):
    def __init__(self, name, salary): super().__init__(name, salary); self.reports = []
    def salary_cost(self): return self.salary + sum(r.salary_cost() for r in self.reports)
boss = Manager("boss", 100); lead = Manager("lead", 80); lead.reports.append(Employee("dev", 60)); boss.reports.append(lead)
print(boss.salary_cost())                               # 240
```

**3.**
```python no-run
def walk(root):
    stack, out = [root], []
    while stack:
        node = stack.pop()
        out.append(node.value)
        stack.extend(reversed(node.children))
    return out
print(walk(Tree("a", Tree("b", Tree("d")), Tree("c"))))  # ['a', 'b', 'd', 'c']
```

</details>

## Decorator Pattern

1. Write `@cache_with_ttl(seconds)` with an injectable clock so expiry is testable.
2. Add a `@validate_positive` decorator that raises `ValueError` if any positive-number argument is `<= 0`.
3. Build a `Text` decorator chain: `Bold(Italic(PlainText("hi")))` giving `<b><i>hi</i></b>`.

<details>
<summary>Solutions</summary>

**1.**
```python no-run
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
```python no-run
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
```python no-run
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

## Facade Pattern

1. Build a `HomeTheater` facade with `watch_movie(title)` and `end_movie()` over `Amplifier`, `Projector`, `Lights`, `Player`. Verify call order.
2. Write a `report(path)` facade that reads a CSV, computes totals and returns text, using three small helper classes.
3. Why shouldn't a facade contain pricing rules?

<details>
<summary>Solutions</summary>

**1.**
```python no-run
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
```python no-run
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

## Flyweight Pattern

1. Build a `Style` flyweight factory keyed by `(font, size, bold)` and 100,000 characters; show only a few `Style` objects exist.
2. Make a flyweight immutable using a `frozen=True` dataclass and show that mutation fails.
3. Why must flyweights be immutable?

<details>
<summary>Solutions</summary>

**1.**
```python no-run
class Style:
    __slots__ = ("font", "size", "bold")
    def __init__(self, font, size, bold): self.font, self.size, self.bold = font, size, bold
class StyleFactory:
    cache = {}
    @classmethod
    def get(cls, font, size, bold):
        return cls.cache.setdefault((font, size, bold), Style(font, size, bold))
chars = [(c, StyleFactory.get("Arial", 12 if i % 10 else 14, i % 7 == 0)) for i, c in enumerate("x" * 100_000)]
print(len(StyleFactory.cache))                          # 4  (a few distinct styles for 100,000 characters)
```

**2.**
```python no-run
from dataclasses import dataclass
@dataclass(frozen=True)
class FrozenStyle:
    font: str
    size: int
s = FrozenStyle("Arial", 12)
try:
    s.size = 20
except Exception as e:
    print(type(e).__name__)                             # FrozenInstanceError
```

**3.** Many objects reference the same flyweight at once; if one changed it, every other user would see the change. Immutability makes sharing safe.

</details>

## Proxy Pattern

1. Build a lazy proxy for a `Database` that connects only when the first `query` runs.
2. Add a rate-limit proxy that allows at most 3 calls, then raises.
3. Make the counting proxy also support `len()`.

<details>
<summary>Solutions</summary>

**1.**
```python no-run
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
```python no-run
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
```python no-run
class CountingProxy2(CountingProxy):
    def __len__(self): return len(self._target)
print(len(CountingProxy2([1, 2, 3])))                   # 3
```

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Design Patterns](exercises.md) · [Design Patterns](summary.md)
