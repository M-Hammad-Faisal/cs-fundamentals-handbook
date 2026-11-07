# Builder Pattern

**Family:** creational · **How often you will use it:** often (fluent APIs) · **Difficulty:** easy

## 1. In plain words

A **Builder** constructs a **complex object step by step**, and only hands it to you at the end. You choose which steps to run, and the builder checks everything is valid before giving you the finished product.

Analogy: ordering a **burger at a counter**: "bun, patty, no onions, extra cheese, done." You do not receive half a burger after each word; you get the finished burger when you say "done".

## 2. The problem

A constructor with many optional parameters becomes unreadable and error-prone (the "telescoping constructor"):

```python
pizza = Pizza("large", "thick", ("olives", "mushrooms"), True, False, 3, None, "well done")
# What do True, False, 3 and None mean?
```

Or the object needs several steps in a certain order, and must be checked as a whole.

## 3. The solution

```text
Client --calls--> Builder: size() -> crust() -> topping() -> build() --> finished Product
                  (keeps partial state, validates in build())
```

Roles: **Builder** (collects settings with chainable methods), **Product** (the finished object, often immutable), optional **Director** (a helper that knows common recipes such as `margherita()`).

## 4. Step by step

```python
class Pizza:
    def __init__(self, size, crust, toppings, extra_cheese):
        self.size, self.crust = size, crust
        self.toppings, self.extra_cheese = toppings, extra_cheese
    def __repr__(self):
        return f"Pizza({self.size}, {self.crust}, {self.toppings}, cheese={self.extra_cheese})"

class PizzaBuilder:
    def __init__(self):
        self._size, self._crust = "medium", "thin"       # sensible defaults
        self._toppings, self._cheese = [], False

    def size(self, s):
        self._size = s
        return self                                      # returning self allows chaining

    def crust(self, c):
        self._crust = c
        return self

    def topping(self, t):
        self._toppings.append(t)
        return self

    def extra_cheese(self):
        self._cheese = True
        return self

    def build(self):
        if len(self._toppings) > 5:                      # validate the whole object once, here
            raise ValueError("too many toppings")
        return Pizza(self._size, self._crust, tuple(self._toppings), self._cheese)

pizza = (PizzaBuilder().size("large").crust("thick")
         .topping("olives").topping("mushrooms").extra_cheese().build())
print(pizza)          # Pizza(large, thick, ('olives', 'mushrooms'), cheese=True)

# The optional Director: ready-made recipes
class PizzaDirector:
    @staticmethod
    def margherita():
        return PizzaBuilder().size("medium").topping("mozzarella").topping("basil").build()

print(PizzaDirector.margherita())

# Validation lives in build()
try:
    b = PizzaBuilder()
    for t in range(6):
        b.topping(f"t{t}")
    b.build()
except ValueError as e:
    print("rejected:", e)                                # rejected: too many toppings
```

### A real-flavored example: building an HTTP request

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class HttpRequest:
    url: str
    method: str
    headers: tuple
    body: str | None

class RequestBuilder:
    def __init__(self):
        self._url, self._method, self._headers, self._body = None, "GET", {}, None
    def url(self, u):         self._url = u; return self
    def method(self, m):      self._method = m.upper(); return self
    def header(self, k, v):   self._headers[k] = v; return self
    def json_body(self, s):   self._body = s; return self
    def build(self):
        if not self._url:
            raise ValueError("url is required")
        if self._method == "GET" and self._body is not None:
            raise ValueError("GET cannot have a body")
        return HttpRequest(self._url, self._method, tuple(self._headers.items()), self._body)

req = RequestBuilder().url("https://x.test/a").method("post").header("A", "1").json_body("{}").build()
print(req.method, req.headers)                           # POST (('A', '1'),)
```

## 5. The Pythonic way

Python often needs a builder less than other languages:

- **Keyword arguments with defaults**: `Pizza(size="large", extra_cheese=True)` is readable.
- **Dataclasses** with `field(default_factory=list)` and `__post_init__` validation.
- **`dataclasses.replace(obj, size="large")`** to derive variants.
- **Fluent interfaces** (method chaining) in libraries: SQLAlchemy `select(User).where(...).order_by(...)`, `pathlib`, pandas chains.

```python
from dataclasses import dataclass, field

@dataclass
class PizzaSpec:
    size: str = "medium"
    crust: str = "thin"
    toppings: list = field(default_factory=list)
    extra_cheese: bool = False
    def __post_init__(self):
        if len(self.toppings) > 5:
            raise ValueError("too many toppings")

print(PizzaSpec(size="large", toppings=["olives"]))
```

Use a real Builder when construction has **many steps, ordering rules, cross-field validation or an immutable result**.

## 6. When to use it (and when not to)

**Use it when** an object has many optional parts; you want readable creation; the object should be immutable after creation; you build the same thing in different ways (HTML report, PDF report from the same steps).

**Skip it when** a few keyword arguments or a dataclass say it clearly.

## 7. Pros and cons

| Pros | Cons |
|------|------|
| Readable, self-documenting creation | An extra class per product |
| Validate everything in one place before the object exists | Mutable builder state must not leak between builds |
| Immutable products | Overkill for simple objects |
| Same process, different representations | |

## 8. Related patterns

- [Abstract Factory](abstract-factory.md) creates families immediately; Builder creates one complex thing in steps.
- [Prototype](prototype.md) copies; Builder assembles.
- [Composite](../structural/composite.md): builders often assemble composite trees (menus, documents).

## 9. Two real-world examples

**Example 1: Email messages.** `Message.builder().to("a@x.com").subject("Hi").body_html(...).attach("report.pdf").build()`. `build()` checks there is a recipient and subject, sets MIME boundaries and returns an immutable message.

**Example 2: SQL query builders.** `select(User).where(User.age > 18).order_by(User.name).limit(10)` accumulates parts; the SQL string is generated only when executed. The same builder can produce different SQL dialects.

## 10. Common mistakes

- Reusing one builder object for two products without resetting it.
- Returning half-valid objects from `build()`.
- Making the product mutable so validation can be bypassed afterwards.
- Writing a builder when keyword arguments would do.

## 11. Practice

1. Write `QueryBuilder` with `select(*cols)`, `from_(table)`, `where(cond)`, `limit(n)` and `build()` returning a SQL string. Require `from_`.
2. Make a dataclass with `__post_init__` that rejects `limit < 0`.
3. Ensure a builder can be reused safely by resetting state after `build()`.

<details>
<summary>Solutions</summary>

**1.**
```python
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
```python
@dataclass
class Page:
    limit: int = 10
    def __post_init__(self):
        if self.limit < 0: raise ValueError("limit must be >= 0")
try: Page(limit=-1)
except ValueError as e: print(e)
```

**3.**
```python
class ReusableBuilder(PizzaBuilder):
    def build(self):
        pizza = super().build()
        self.__init__()                              # reset to defaults
        return pizza
rb = ReusableBuilder()
print(rb.topping("a").build(), rb.build())            # second pizza has no toppings
```

</details>

## 12. Check yourself

1. What problem does Builder solve?
2. Why does each setter `return self`?
3. Where should validation live?
4. When are keyword arguments or dataclasses enough?
5. What is a Director?

<details>
<summary>Answers</summary>

1. Creating complex objects with many optional parts or required steps without unreadable constructors or half-built objects.
2. So calls can be chained fluently.
3. In `build()`, so the complete object is checked once before it exists.
4. When there are only a few optional fields and no multi-step or cross-field rules.
5. An optional class that knows common recipes and drives a builder through the steps.

</details>

## More examples

Runnable script from your companion repository: [`creationalPattern/builderPattern.py`](https://github.com/M-Hammad-Faisal/design-patterns-python/blob/master/creationalPattern/builderPattern.py)

[Family overview](README.md) · [All patterns](../README.md)
