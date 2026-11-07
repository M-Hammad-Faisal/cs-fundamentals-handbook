# Null Object Pattern

**Family:** behavioral (not one of the original GoF 23, but widely used) · **How often you will use it:** often, once you know it · **Difficulty:** easy

## 1. In plain words

A **Null Object** is an object that **does nothing, safely**, used in place of `None` so callers never have to check "is it there?" before using it.

Analogy: a **"do not disturb" automatic reply**. Instead of leaving you wondering whether anyone is listening, there is always a responder that politely does nothing useful.

## 2. The problem

`None` forces a check before every use, and forgetting one causes `AttributeError: 'NoneType' object has no attribute ...`:

```python
def process(items, logger=None):
    for item in items:
        if logger is not None:           # the check is repeated everywhere
            logger.info(f"processing {item}")
```

## 3. The solution

```text
Client ──► AbstractThing ◄── RealThing         (does real work)
                         ◄── NullThing         (same methods, does nothing / returns neutral values)
```

Return the null object instead of `None`; callers just call it.

## 4. Step by step

```python
class Logger:
    def info(self, msg):
        print("LOG:", msg)

class NullLogger:                                       # same interface, does nothing
    def info(self, msg):
        pass

def process(items, logger=None):
    logger = logger or NullLogger()                     # one place decides; the rest is check-free
    for item in items:
        logger.info(f"processing {item}")
    return len(items)

print(process([1, 2]))                                  # 2   (silent)
print(process([1], Logger()))                           # LOG: processing 1   then   1
```

### A user that is not logged in

```python
class User:
    is_authenticated = True
    def __init__(self, name, permissions):
        self.name, self.permissions = name, set(permissions)
    def can(self, action):
        return action in self.permissions

class AnonymousUser:                                    # the null object
    name = "anonymous"
    is_authenticated = False
    def can(self, action):
        return False

def current_user(session):
    return User(*session["user"]) if "user" in session else AnonymousUser()

def render_header(session):
    user = current_user(session)                        # never None
    return f"{user.name} (edit: {user.can('edit')}, logged in: {user.is_authenticated})"

print(render_header({}))                                # anonymous (edit: False, logged in: False)
print(render_header({"user": ("ana", ["edit"])}))       # ana (edit: True, logged in: True)
```

### Neutral return values and empty collections

```python
class NullCart:
    items = ()
    def total(self): return 0
    def __iter__(self): return iter(())
    def __len__(self): return 0

def checkout_summary(cart):
    return f"{len(cart)} items, total {cart.total()}"

print(checkout_summary(NullCart()))                     # 0 items, total 0
```

The simplest null object of all: return an **empty list/dict/tuple** (`[]`) instead of `None` so callers can loop without a check.

## 5. The Pythonic way

- `contextlib.nullcontext()` is a no-op context manager (use `with maybe_lock or nullcontext():`).
- `logging.NullHandler` is the standard null logger handler for libraries.
- An empty `[]`, `()`, `{}`, `""` or `0` is the lightweight null value for collections and numbers.
- `unittest.mock.Mock()` accepts any call and returns another mock (a super null object for tests).
- Django's `AnonymousUser` and many ORMs' "empty" querysets (`Model.objects.none()`).

```python
from contextlib import nullcontext
import threading

def run(lock=None):
    with lock or nullcontext():                         # works with or without a lock
        return "ran"

print(run(), run(threading.Lock()))                     # ran ran
```

## 6. When to use it (and when not to)

**Use it when** "absent" has a natural do-nothing or neutral behavior (no logger, no user, no discount, empty cart, no-op callback), and you are tired of `if x is not None` everywhere.

**Skip it when** absence is an **error** that should be loud (a missing required configuration should raise, not silently continue), or the caller really needs to distinguish "missing" from "present".

## 7. Pros and cons

| Pros | Cons |
|------|------|
| Removes `None` checks and a class of `AttributeError` bugs | Can hide real errors (silent no-ops) |
| Simpler, more uniform client code | Callers cannot easily tell if it is the null object |
| Easy defaults (optional collaborators) | One more class per interface |

## 8. Related patterns

- [Strategy](strategy.md): a "do nothing" strategy is a null object.
- [State](state.md): a terminal state (`Cancelled`) often has null behavior.
- [Proxy](../structural/proxy.md), [Singleton](../creational/singleton.md): a null object is usually a stateless singleton.

## 9. Two real-world examples

**Example 1: Library logging.** A library calls `logger.debug(...)` everywhere; by default it attaches `logging.NullHandler()` so nothing is printed unless the application configures logging. No `if logging_enabled` checks anywhere.

**Example 2: Optional discount.** `order.discount.apply(price)` always works: customers without a coupon get `NoDiscount` whose `apply` returns the price unchanged.

## 10. Common mistakes

- Using a null object where silent failure is dangerous (payment gateway that "does nothing" and reports success).
- Returning `None` from some paths and a null object from others.
- Null objects with state (they should be stateless and shareable).
- Overusing it so real "not found" situations vanish.

## 11. Practice

1. Make a `NoDiscount` strategy and a `Checkout` that works with or without a discount.
2. Write `find_user(name)` returning a `GuestUser` null object, and a `greet(user)` with no `None` check.
3. When is a null object a bad idea? Give an example.

<details>
<summary>Solutions</summary>

**1.**
```python
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
```python
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

## 12. Check yourself

1. What does a null object replace and why?
2. Give two standard-library examples.
3. When should absence be an error instead?
4. Why should null objects be stateless?

<details>
<summary>Answers</summary>

1. It replaces `None` with an object that implements the interface neutrally, removing repeated `is not None` checks.
2. `contextlib.nullcontext`, `logging.NullHandler` (also empty collections).
3. When the missing value indicates a real problem the caller must handle (required config, failed payment): fail loudly.
4. They do nothing and hold no data, so one shared instance can serve everyone safely.

</details>

## More examples

Runnable script (added to your companion repository with this lesson): [`behavioralPattern/nullObjectPattern.py`](https://github.com/M-Hammad-Faisal/design-patterns-python/blob/master/behavioralPattern/nullObjectPattern.py)

[Family overview](README.md) · [All patterns](../README.md)
