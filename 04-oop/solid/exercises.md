# SOLID: Exercises

1. **SRP:** split this class and explain the reasons to change:
   ```python
   class Employee:
       def __init__(self, name, hours, rate): self.name, self.hours, self.rate = name, hours, rate
       def calculate_pay(self): return self.hours * self.rate
       def report_hours(self): return f"{self.name}: {self.hours}h"
       def save(self, db): db.append((self.name, self.hours, self.rate))
   ```
2. **OCP:** rewrite a shipping cost function (`standard`, `express`, `overnight`) so adding `drone` needs no edit to existing code. Do it once with classes and once with a registry of functions.
3. **LSP:** this subclass violates the contract. Identify the violation, write a test that exposes it, and fix the design:
   ```python
   class FileStore:
       def read(self, name) -> str: ...
   class ReadOnlyStore(FileStore):
       def write(self, name, data): raise PermissionError
   ```
   (the base also defines `write`; callers expect it to work).
4. **ISP:** split `Worker` (`work`, `eat`, `sleep`) so that `Robot` need not implement `eat` and `sleep`. Use `Protocol`.
5. **DIP:** refactor a `WeatherReport` class that calls `requests.get` directly so it can be tested offline. Show the unit test.
6. Name the SOLID principle(s) each smell violates: (a) a 40-line `if/elif` on `type`, (b) a subclass raising `NotImplementedError`, (c) business logic importing `psycopg2`, (d) a class named `OrderManagerHelperUtils`, (e) a function taking a whole `Request` but using only `request.user_id`.
7. Take the `Library` from the [composition lesson](../composition-design/README.md) and list two SOLID improvements you would make.
8. When is DRY harmful? Give an example of "wrong abstraction" duplication removal.
9. Explain "rule of three" and how it relates to OCP and YAGNI.

<details>
<summary>Solutions</summary>

**1.** Reasons to change: pay rules (finance), reporting format (management), persistence (engineering/DB).
```python
class Employee:
    def __init__(self, name, hours, rate): self.name, self.hours, self.rate = name, hours, rate
class PayCalculator:
    def pay(self, e): return e.hours * e.rate
class HoursReport:
    def render(self, e): return f"{e.name}: {e.hours}h"
class EmployeeRepository:
    def __init__(self, db): self.db = db
    def save(self, e): self.db.append((e.name, e.hours, e.rate))
db = []; e = Employee("ana", 40, 25)
print(PayCalculator().pay(e), HoursReport().render(e)); EmployeeRepository(db).save(e); print(db)
```

**2.**
```python
from abc import ABC, abstractmethod
class Shipping(ABC):
    @abstractmethod
    def cost(self, kg): ...
class Standard(Shipping):  cost = lambda self, kg: 5 + kg
class Express(Shipping):   cost = lambda self, kg: 10 + 2 * kg
class Drone(Shipping):     cost = lambda self, kg: 15 + 3 * kg     # added later
print(Drone().cost(2))
# registry of functions
RATES = {"standard": lambda kg: 5 + kg, "express": lambda kg: 10 + 2 * kg}
RATES["overnight"] = lambda kg: 20 + 4 * kg                         # extension without editing the dict's users
def shipping_cost(kind, kg): return RATES[kind](kg)
print(shipping_cost("overnight", 2))
```

**3.** Violation: callers of `FileStore.write` expect success; `ReadOnlyStore` raises (stronger precondition / broken postcondition).
```python
class Reader:
    def read(self, name): raise NotImplementedError
class Writer:
    def write(self, name, data): raise NotImplementedError
class MemStore(Reader, Writer):
    def __init__(self): self.d = {}
    def read(self, name): return self.d[name]
    def write(self, name, data): self.d[name] = data
class ReadOnlyStore(Reader):
    def __init__(self, d): self.d = d
    def read(self, name): return self.d[name]
def archive(w: Writer, data): w.write("x", data)       # only demands the Writer role
archive(MemStore(), "ok"); print(ReadOnlyStore({"a": "1"}).read("a"))
```
A test that calls `store.write(...)` on every `FileStore` subtype fails for `ReadOnlyStore`, exposing the violation.

**4.**
```python
from typing import Protocol
class Workable(Protocol):
    def work(self): ...
class Feedable(Protocol):
    def eat(self): ...
class Human:
    def work(self): return "working"
    def eat(self): return "eating"
class Robot:
    def work(self): return "welding"
def start_shift(w: Workable): return w.work()
def lunch(f: Feedable): return f.eat()
print(start_shift(Robot()), lunch(Human()))
```

**5.**
```python
class WeatherReport:
    def __init__(self, fetch_json):                     # fetch_json(city) -> dict, injected
        self.fetch_json = fetch_json
    def summary(self, city):
        data = self.fetch_json(city)
        return f"{city}: {data['temp']}C, {data['sky']}"
# production: WeatherReport(lambda city: requests.get(f".../{city}").json())
def fake_fetch(city): return {"temp": 21, "sky": "clear"}
assert WeatherReport(fake_fetch).summary("Lahore") == "Lahore: 21C, clear"
print(WeatherReport(fake_fetch).summary("Lahore"))
```

**6.** (a) OCP (and probably SRP); (b) LSP (and ISP); (c) DIP; (d) SRP (low cohesion); (e) ISP (depends on more than it needs) and coupling.

**7.** Examples: SRP (separate loan bookkeeping from `Library` into a `LoanLedger`), DIP/OCP (introduce a `Catalog` interface so books can come from memory or a database), ISP (give `Member` methods `add_loan`/`remove_loan` rather than exposing `_loans`).

**8.** Two functions look the same today (`validate_user` and `validate_product` both check "name not empty") and get merged into one generic validator; later they diverge and every change needs flags and exceptions. Duplication of *knowledge* is the enemy; duplication of *incidental code* is cheaper than the wrong abstraction.

**9.** Tolerate duplication or an `if` the first and second time; when a third variation appears, you know what really varies and can extract the abstraction (OCP) without guessing (YAGNI).

</details>

[Lesson](README.md) · [Summary](summary.md)
