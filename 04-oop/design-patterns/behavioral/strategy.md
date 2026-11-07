# Strategy Pattern

**Family:** behavioral · **Also called:** policy · **How often you will use it:** very often · **Difficulty:** easy

## 1. In plain words

A **Strategy** is an **interchangeable way of doing one job**. You define several algorithms behind the same interface and let the program (or user) pick which one to use, even while it runs.

Analogy: **getting to the airport**. The goal is the same; you choose a strategy (taxi, bus, train, bike) depending on cost, time and traffic. The trip planner does not change when you switch.

## 2. The problem

One class contains a growing `if/elif` ladder choosing between algorithms:

```python
def shipping_cost(method, weight):
    if method == "standard":
        return 5 + weight
    elif method == "express":
        return 15 + 2.5 * weight
    elif method == "overnight":
        return 30 + 4 * weight          # every new method edits this function
```

## 3. The solution

```text
Context ──holds──► Strategy interface: cost(weight)
(Order)                  ▲
                 ┌───────┼────────┐
            Standard   Express  Overnight
```

The **context** delegates the varying part to a strategy object; swapping the object swaps the behavior.

## 4. Step by step

```python
from abc import ABC, abstractmethod

class ShippingStrategy(ABC):
    @abstractmethod
    def cost(self, weight_kg): ...

class Standard(ShippingStrategy):
    def cost(self, weight_kg): return 5 + 1.0 * weight_kg

class Express(ShippingStrategy):
    def cost(self, weight_kg): return 15 + 2.5 * weight_kg

class Order:                                            # the context
    def __init__(self, weight_kg, strategy):
        self.weight_kg, self.strategy = weight_kg, strategy
    def shipping(self):
        return self.strategy.cost(self.weight_kg)

order = Order(2, Standard())
print(order.shipping())                                 # 7.0
order.strategy = Express()                              # swap behavior at runtime
print(order.shipping())                                 # 20.0

class Overnight(ShippingStrategy):                      # a new option: no existing code edited
    def cost(self, weight_kg): return 30 + 4 * weight_kg
print(Order(2, Overnight()).shipping())                 # 38
```

### Strategies with their own configuration

```python
class PercentDiscount:
    def __init__(self, percent): self.percent = percent
    def apply(self, price): return price * (1 - self.percent / 100)

class FlatDiscount:
    def __init__(self, amount): self.amount = amount
    def apply(self, price): return max(0, price - self.amount)

def checkout(price, discount):
    return discount.apply(price)

print(checkout(100, PercentDiscount(20)), checkout(100, FlatDiscount(15)))   # 80.0 85
```

## 5. The Pythonic way: a strategy is often just a function

If the algorithm has no state, pass a function:

```python
def standard(kg): return 5 + kg
def express(kg): return 15 + 2.5 * kg

def shipping_cost(weight, strategy=standard):
    return strategy(weight)

print(shipping_cost(2), shipping_cost(2, express), shipping_cost(2, lambda kg: 0))   # 7 20.0 0

STRATEGIES = {"standard": standard, "express": express}       # choose by name from config
print(STRATEGIES["express"](4))                                # 25.0
```

You already use Strategy every time you pass `key=` to `sorted`, `min`, `max`:

```python
words = ["banana", "fig", "cherry"]
print(sorted(words, key=len), sorted(words, key=str.lower, reverse=True))
# ['fig', 'banana', 'cherry'] ['fig', 'cherry', 'banana']
```

## 6. When to use it (and when not to)

**Use it when** you have several ways to do the same thing (pricing, sorting, compression, authentication, retry policies, validation rules); you want to choose at runtime or by configuration; you want to remove a conditional ladder.

**Skip it when** there are only two stable options (`if` is fine), or the variation never changes.

## 7. Pros and cons

| Pros | Cons |
|------|------|
| Add algorithms without editing the context (Open/Closed) | More objects/functions |
| Swap at runtime; easy to test each strategy alone | Clients must know the differences to choose |
| Removes conditionals | For tiny variations a function parameter is simpler |

## 8. Related patterns

- [State](state.md): same structure, but states change themselves and know each other; strategies are chosen by the client.
- [Template Method](template-method.md): varies steps by inheritance; Strategy varies the whole algorithm by composition.
- [Decorator](../structural/decorator.md): wraps to add; Strategy replaces.
- [Bridge](../structural/bridge.md): a structural cousin that separates two hierarchies.

## 9. Two real-world examples

**Example 1: Payment methods.** Checkout holds a `PaymentStrategy` (card, wallet, bank transfer). Adding "buy now pay later" is one new class; the checkout flow does not change.

**Example 2: Sort keys and compression.** `sorted(users, key=lambda u: u.age)` swaps the comparison strategy; `zipfile.ZipFile(..., compression=ZIP_DEFLATED)` picks a compression strategy.

## 10. Common mistakes

- Strategies that need so much of the context's data that they depend on its internals (pass what they need as arguments).
- A strategy per tiny `if` (over-engineering).
- Letting the client choose a strategy that is invalid in the current situation without checking.

## 11. Practice

1. Implement price strategies `Regular`, `Student` (20% off), `Bulk` (10% off for quantity >= 10) as classes and as a dictionary of functions.
2. Implement text compression strategies `NoCompression` and `Reverse` (silly) and a `Sender` that uses either.
3. Replace the ladder in section 2 with a dictionary of strategies and an `unknown method` error.

<details>
<summary>Solutions</summary>

**1.**
```python
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
```python
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
```python
RATES = {"standard": lambda w: 5 + w, "express": lambda w: 15 + 2.5 * w, "overnight": lambda w: 30 + 4 * w}
def shipping_cost2(method, weight):
    try:
        return RATES[method](weight)
    except KeyError:
        raise ValueError(f"unknown shipping method {method!r}") from None
print(shipping_cost2("express", 2))                                           # 20.0
```

</details>

## 12. Check yourself

1. What does Strategy replace?
2. What is the Pythonic form of a stateless strategy?
3. Strategy versus State?
4. Give two places you already use Strategy in Python.

<details>
<summary>Answers</summary>

1. A conditional ladder choosing between algorithms; the algorithms become interchangeable objects.
2. A plain function (or lambda) passed in.
3. Both delegate to an interchangeable object; with Strategy the client picks the algorithm, with State the object switches behavior itself as its state changes.
4. `sorted(..., key=...)`, `min/max(..., key=...)`; compression and hashing options.

</details>

## More examples

Runnable script (added to your companion repository with this lesson): [`behavioralPattern/strategyPattern.py`](https://github.com/M-Hammad-Faisal/design-patterns-python/blob/master/behavioralPattern/strategyPattern.py)

[Family overview](README.md) · [All patterns](../README.md)
