# State Pattern

**Family:** behavioral · **Also called:** objects for states, state machine · **How often you will use it:** often (workflows) · **Difficulty:** medium

## 1. In plain words

With **State**, an object **changes how it behaves depending on what state it is in**, and each state is its own small object that knows what to do and what state comes next.

Analogy: a **traffic light**. Pressing "next" does a different thing in red, green and yellow, and each colour knows what follows it. Or a **vending machine**: the same "press button" does different things when no coin is inserted, when a coin is in, and when it is out of stock.

## 2. The problem

Behavior depends on a status field, so every method fills with conditionals that must stay consistent:

```python
class Order:
    def ship(self):
        if self.status == "pending":
            raise ValueError("pay first")
        elif self.status == "paid":
            self.status = "shipped"
        elif self.status == "shipped":
            raise ValueError("already shipped")
        elif self.status == "cancelled":
            raise ValueError("cancelled")
    # pay(), cancel(), refund() each repeat the same ladder...
```

## 3. The solution

```text
Context (Order) ──holds──► State (interface: pay, ship, cancel)
                                ▲
              ┌─────────────────┼──────────────┐
          Pending            Paid           Shipped      (each returns the next state)
```

The context **delegates** each action to its current state object; the state decides what happens and which state comes next.

## 4. Step by step

```python
class Order:                                            # the context
    def __init__(self):
        self.state = Pending()
    def pay(self):    self.state = self.state.pay(self)
    def ship(self):   self.state = self.state.ship(self)
    def cancel(self): self.state = self.state.cancel(self)

class State:                                            # default behavior: not allowed
    name = "?"
    def pay(self, order):    raise ValueError(f"cannot pay in state {self.name}")
    def ship(self, order):   raise ValueError(f"cannot ship in state {self.name}")
    def cancel(self, order): raise ValueError(f"cannot cancel in state {self.name}")

class Pending(State):
    name = "pending"
    def pay(self, order):    return Paid()
    def cancel(self, order): return Cancelled()

class Paid(State):
    name = "paid"
    def ship(self, order):   return Shipped()
    def cancel(self, order): return Cancelled()

class Shipped(State):
    name = "shipped"                                    # no actions allowed any more

class Cancelled(State):
    name = "cancelled"

order = Order()
order.pay(); order.ship()
print(order.state.name)                                 # shipped
try:
    order.cancel()
except ValueError as e:
    print(e)                                            # cannot cancel in state shipped

try:
    Order().ship()                                      # cannot ship before paying
except ValueError as e:
    print(e)                                            # cannot ship in state pending
```

### A state with real behavior: a media player

```python
class Player:
    def __init__(self):
        self.state = Stopped()
    def press_play(self):                                # ONE button, behavior depends on the state
        self.state = self.state.press_play()
        return self.state.name

class Stopped:
    name = "stopped"
    def press_play(self): return Playing()
class Playing:
    name = "playing"
    def press_play(self): return Paused()
class Paused:
    name = "paused"
    def press_play(self): return Playing()

p = Player()
print([p.press_play() for _ in range(4)])               # ['playing', 'paused', 'playing', 'paused']
```

## 5. The Pythonic way: a transition table

When states differ only in **which events are legal** and **what comes next**, a dictionary is shorter and easier to audit than a class per state:

```python
TRANSITIONS = {
    ("pending", "pay"): "paid",
    ("pending", "cancel"): "cancelled",
    ("paid", "ship"): "shipped",
    ("paid", "cancel"): "cancelled",
}

class SimpleOrder:
    def __init__(self):
        self.state = "pending"
    def handle(self, event):
        try:
            self.state = TRANSITIONS[(self.state, event)]
        except KeyError:
            raise ValueError(f"cannot {event} in state {self.state}") from None

o = SimpleOrder()
for e in ("pay", "ship"):
    o.handle(e)
print(o.state)                                          # shipped
try:
    o.handle("cancel")
except ValueError as e:
    print(e)                                            # cannot cancel in state shipped
```

Use state classes when each state has **substantial behavior** (different data, different methods); use a table when it is mostly **allowed transitions**. `enum.Enum` is a good way to name states in either style, and libraries such as `transitions` provide full state machines.

## 6. When to use it (and when not to)

**Use it when** an object's behavior depends on its state and changes at runtime; you have large conditionals on a status field: order lifecycles, document workflows (draft, review, published), connections (connecting, open, closed), game characters, parsers, UI modes.

**Skip it when** there are only two or three simple states with trivial behavior; a few `if`s are clearer.

## 7. Pros and cons

| Pros | Cons |
|------|------|
| Removes big conditionals; each state is small and testable | More classes |
| State-specific rules live in one place | Transitions are spread across state classes (harder to see the whole machine) |
| Illegal operations are naturally rejected | Overkill for tiny state machines |

## 8. Related patterns

- [Strategy](strategy.md): same structure; the *client* picks strategies, whereas states *transition themselves*.
- [Flyweight](../structural/flyweight.md): stateless state objects can be shared singletons.
- [Command](command.md) / [Observer](observer.md): state changes often trigger events or commands.

## 9. Two real-world examples

**Example 1: Order lifecycle.** `created -> paid -> packed -> shipped -> delivered`, with `cancelled` and `refunded` branches. "Cancel" is allowed before shipping, refunds only after payment: the rules live in the states.

**Example 2: A TCP connection.** `CLOSED`, `LISTEN`, `SYN_SENT`, `ESTABLISHED`, `FIN_WAIT`... receiving the same packet type means different things in each state. Protocol implementations are state machines.

## 10. Common mistakes

- Scattering state checks (`if self.state == ...`) back into the context.
- Not covering invalid transitions (silently ignoring them).
- Letting states share mutable data inconsistently.
- Using classes where a table would do.

## 11. Practice

1. Model a traffic light with state classes, then with a transition table.
2. Add a `refund` event to the order that is only allowed from `shipped` (table version).
3. Draw (as text) the state diagram of the order table.

<details>
<summary>Solutions</summary>

**1.**
```python
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
```python
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

## 12. Check yourself

1. What does the context delegate to the state object?
2. When is a transition table better than state classes?
3. State versus Strategy?
4. What bug appears when invalid transitions are not handled?

<details>
<summary>Answers</summary>

1. Each action (`pay`, `ship`, ...); the state decides the result and the next state.
2. When states differ mostly in allowed transitions and have little state-specific behavior.
3. Both delegate to an object. With Strategy the client chooses the algorithm and strategies are independent; with State the object switches states itself and states usually know their successors.
4. Illegal actions silently succeed or leave the object inconsistent (for example shipping an unpaid order).

</details>

## More examples

Runnable script (added to your companion repository with this lesson): [`behavioralPattern/statePattern.py`](https://github.com/M-Hammad-Faisal/design-patterns-python/blob/master/behavioralPattern/statePattern.py)

[Family overview](README.md) · [All patterns](../README.md)
