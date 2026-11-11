# Exceptions, Logging and Testing

## 1. The concept

Real programs fail: files are missing, networks drop, users type nonsense, code has bugs. Three habits separate hobby scripts from reliable software:

| Habit | Question it answers |
|-------|--------------------|
| **Exceptions** | How does the program *signal and handle* failure cleanly? |
| **Logging** | How do you *find out what happened* in production (when you cannot attach a debugger)? |
| **Testing** | How do you *know it works* and keep it working as the code changes? |

## 2. Exceptions

### The mechanics

```python
def parse_age(text):
    try:
        age = int(text)                      # may raise ValueError
    except ValueError:
        print(f"{text!r} is not a number")
        return None
    else:                                    # runs only if the try block did NOT raise
        if age < 0:
            raise ValueError("age cannot be negative")
        return age
    finally:                                 # ALWAYS runs: cleanup goes here
        print("parse finished")

print(parse_age("42"))                       # parse finished  42
print(parse_age("abc"))                      # 'abc' is not a number  parse finished  None
try:
    parse_age("-5")
except ValueError as e:
    print("rejected:", e)                    # parse finished  rejected: age cannot be negative
```

`try` wraps the risky code, `except` handles specific errors, `else` is for code that should run only on success, `finally` always runs (even on `return` or an uncaught exception). Prefer `with` (context managers) for resource cleanup.

### The hierarchy

```text
BaseException
 ├─ KeyboardInterrupt, SystemExit, GeneratorExit        (do not catch these by accident)
 └─ Exception                                           (the base of normal errors)
     ├─ ValueError, TypeError, KeyError, IndexError, AttributeError
     ├─ OSError (FileNotFoundError, PermissionError, ConnectionError, TimeoutError ...)
     ├─ RuntimeError, NotImplementedError, StopIteration
     └─ your own exceptions
```

```python
import json
for text in ('{"a": 1}', '{bad json}', None):
    try:
        print(json.loads(text))
    except json.JSONDecodeError as e:        # more specific first
        print("invalid JSON at position", e.pos)
    except TypeError:
        print("not a string")
# {'a': 1}
# invalid JSON at position 1
# not a string
```

### Rules for catching exceptions

1. **Catch the narrowest exception** you can actually handle. `except Exception:` is almost never right except at a program's outer boundary (a web framework's error handler, a worker loop).
2. **Never write a bare `except:`** (it also catches `KeyboardInterrupt` and `SystemExit`).
3. **Never silently swallow** (`except: pass`). At least log it.
4. **Do not use exceptions for normal control flow** when a simple check is clearer, but do use EAFP ("easier to ask forgiveness than permission") where checking first is racy or verbose: `try: value = d[key] except KeyError: ...`.
5. **Handle where you can do something useful**; let the rest propagate upwards.

### Raising and chaining

```python
class ConfigError(Exception):
    """Raised when the application configuration is invalid."""

def load_port(raw):
    try:
        return int(raw)
    except ValueError as e:
        raise ConfigError(f"PORT must be an integer, got {raw!r}") from e    # keeps the original cause

try:
    load_port("eighty")
except ConfigError as e:
    print(e, "| caused by:", type(e.__cause__).__name__)    # PORT must be an integer, got 'eighty' | caused by: ValueError
```

`raise ... from e` records the cause (shown in the traceback as "The above exception was the direct cause..."); a bare `raise` inside `except` re-raises the same exception; `raise ... from None` hides the cause when it is noise.

### Designing your own exceptions

```python
class AppError(Exception):
    """Base class for all errors raised by this application."""

class ValidationError(AppError):
    def __init__(self, field, message):
        super().__init__(f"{field}: {message}")
        self.field, self.message = field, message

class NotFoundError(AppError):
    pass

def get_user(users, user_id):
    if user_id not in users:
        raise NotFoundError(f"user {user_id} does not exist")
    return users[user_id]

try:
    get_user({}, 7)
except AppError as e:                         # one handler for the whole family
    print(type(e).__name__, "-", e)           # NotFoundError - user 7 does not exist
```

Guidelines: one base class per library/app; name errors for **what went wrong** (`PaymentDeclined`), carry useful data (fields), translate low-level errors (`sqlite3.IntegrityError`) into domain errors at layer boundaries, and document what each function can raise.

### Retry with backoff (a common real-world pattern)

```python
import time

def retry(times, delay=0.0, retry_on=(ConnectionError,)):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return fn(*args, **kwargs)
                except retry_on:
                    if attempt == times:
                        raise                 # out of attempts: let the caller see the real error
                    time.sleep(delay * 2 ** (attempt - 1))      # exponential backoff
        return wrapper
    return decorator

attempts = []

@retry(times=3, delay=0.001)
def flaky():
    attempts.append(1)
    if len(attempts) < 3:
        raise ConnectionError("temporary failure")
    return "ok"

print(flaky(), len(attempts))                 # ok 3
```

Only retry **transient** errors (timeouts, connection resets) and **idempotent** operations (see [DNS and HTTP](../../07-networking/dns-http/README.md)); add jitter and a cap in production; never retry validation errors.

### Context managers and `contextlib`

```python
from contextlib import suppress, contextmanager
import os, tempfile

path = os.path.join(tempfile.mkdtemp(), "data.txt")
with suppress(FileNotFoundError):             # ignore one specific, expected error
    os.remove(path)

@contextmanager
def transaction(log):
    log.append("begin")
    try:
        yield
        log.append("commit")                  # success path
    except Exception:
        log.append("rollback")                # error path
        raise                                 # never hide the error
log = []
try:
    with transaction(log):
        raise ValueError("boom")
except ValueError:
    pass
print(log)                                    # ['begin', 'rollback']
```

Exception groups and notes (3.11+) are in [modern syntax](../modern-syntax/README.md); exceptions in concurrent code in [async](../async-concurrency/README.md).

## 3. Logging

`print` is for programs' output; **logging** is for diagnosing them. It adds **levels**, **timestamps and context**, **destinations** (console, files, remote services), and can be **turned up or down without code changes**.

### Levels

| Level | Use for | Numeric |
|-------|---------|---------|
| `DEBUG` | Detailed diagnostics for developers | 10 |
| `INFO` | Normal events worth recording ("server started", "order 123 created") | 20 |
| `WARNING` | Something unexpected but the program continues | 30 |
| `ERROR` | An operation failed | 40 |
| `CRITICAL` | The program may not be able to continue | 50 |

### The basics

```python
import logging, io

stream = io.StringIO()                                           # capture output so we can show it here
handler = logging.StreamHandler(stream)
handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))

logger = logging.getLogger("shop.checkout")                       # name it after the module: __name__
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)
logger.propagate = False

logger.debug("cart has %d items", 3)                              # lazy formatting: only built if the level is enabled
logger.info("order %s created", "A-1001")
logger.warning("low stock for %s", "pen")
try:
    1 / 0
except ZeroDivisionError:
    logger.exception("failed to compute price")                   # ERROR + the full traceback
print(stream.getvalue().splitlines()[:3])
# ['DEBUG shop.checkout: cart has 3 items', 'INFO shop.checkout: order A-1001 created', 'WARNING shop.checkout: low stock for pen']
print("Traceback" in stream.getvalue(), "ZeroDivisionError" in stream.getvalue())    # True True
```

### How the pieces fit

```text
logger.info("msg")  ->  Logger ("shop.checkout")  ->  Handlers (console, file, HTTP, syslog)  ->  Formatter (text/JSON)
                          │ level + filters                 │ each has its own level
                          └─ propagates to parent loggers ("shop", then root)
```

- **Loggers** form a dot-separated hierarchy by name (`shop.checkout` is a child of `shop`); settings and handlers on a parent apply to children.
- **Handlers** decide where records go; **formatters** decide how they look; **filters** drop or enrich records.
- **Libraries** should only create loggers (`logging.getLogger(__name__)`) and add a `NullHandler`; **applications** configure handlers once at start-up.

### Configuring an application

```python
import logging.config

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "plain": {"format": "%(asctime)s %(levelname)-8s %(name)s: %(message)s"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "plain", "level": "INFO"},
    },
    "loggers": {
        "shop": {"level": "DEBUG", "handlers": ["console"], "propagate": False},
    },
    "root": {"level": "WARNING", "handlers": ["console"]},
}
logging.config.dictConfig(LOGGING)
logging.getLogger("shop.orders").info("configured")             # printed to the console in the plain format
logging.getLogger("shop.orders").debug("hidden: handler level is INFO")
```

In real services configure logging **once**, at the entry point (`main()`), from a dictionary or file, with the level controlled by an environment variable.

### Good logging practice

```python
import logging
log = logging.getLogger(__name__)                               # one logger per module

def charge(order_id, amount):
    log.info("charging order_id=%s amount=%.2f", order_id, amount)    # key=value style is easy to search
    try:
        if amount <= 0:
            raise ValueError("amount must be positive")
    except ValueError:
        log.exception("charge failed order_id=%s", order_id)    # logs the traceback; then re-raise or handle
        raise
```

- Use **lazy `%s` arguments**, not f-strings (`log.info("x=%s", x)`), so formatting is skipped when the level is disabled.
- Log **events with identifiers** (order id, user id, request id), not vague text.
- **Never log secrets**: passwords, tokens, full card numbers, personal data.
- `log.exception` inside an `except` block records the traceback; do not also `print` it.
- Do not log and re-raise at every layer (duplicates); log where you **handle** the error or at the boundary.
- For production, prefer **structured (JSON) logs** with a request/correlation id so tools (ELK, Loki, Datadog, CloudWatch) can filter and aggregate.
- Choose levels honestly; too much `INFO` is noise, too little makes incidents opaque.

```python
import json, logging

class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({"level": record.levelname, "logger": record.name, "message": record.getMessage()})

buf = io.StringIO()
h = logging.StreamHandler(buf); h.setFormatter(JsonFormatter())
jl = logging.getLogger("json.demo"); jl.addHandler(h); jl.setLevel(logging.INFO); jl.propagate = False
jl.info("user logged in")
print(buf.getvalue().strip())            # {"level": "INFO", "logger": "json.demo", "message": "user logged in"}
```

## 4. Testing

A **test** is code that runs your code and checks the result. Automated tests give you **confidence to change code**, catch regressions, document behavior and make refactoring safe. See also [testing object-oriented code](../../04-oop/composition-design/README.md).

### The test pyramid

```text
         /\            few    End-to-end tests   (slow, brittle, test the whole system through the UI/API)
        /  \
       /----\          some   Integration tests  (several components together: code + real database)
      /      \
     /--------\        many   Unit tests         (one function/class, in isolation, milliseconds)
```

Write **many fast unit tests**, a **moderate number of integration tests** and **a few end-to-end tests**.

### `unittest` (standard library) and `pytest` (the community standard)

```python
import unittest

def add(a, b):
    return a + b

class TestAdd(unittest.TestCase):
    def test_adds_numbers(self):
        self.assertEqual(add(2, 3), 5)
    def test_adds_strings(self):
        self.assertEqual(add("a", "b"), "ab")
    def test_wrong_types_raise(self):
        with self.assertRaises(TypeError):
            add(1, "x")

result = unittest.TextTestRunner(verbosity=0).run(unittest.defaultTestLoader.loadTestsFromTestCase(TestAdd))
print(result.wasSuccessful())            # True
```

**pytest** uses plain `assert` statements, finds tests automatically (`test_*.py`, functions named `test_*`) and gives detailed failure output. Run with `pytest -q` (or `python -m pytest`).

```python
# pytest
# test_shopping.py
import pytest

def apply_discount(price, percent):
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    return round(price * (1 - percent / 100), 2)

def test_basic_discount():
    assert apply_discount(100, 20) == 80

def test_zero_and_full_discount():
    assert apply_discount(50, 0) == 50
    assert apply_discount(50, 100) == 0

def test_invalid_percent_raises():
    with pytest.raises(ValueError, match="between 0 and 100"):
        apply_discount(10, 150)

@pytest.mark.parametrize("price, percent, expected", [
    (100, 10, 90),
    (20, 50, 10),
    (0, 25, 0),
])
def test_discount_table(price, percent, expected):               # one test body, many cases
    assert apply_discount(price, percent) == expected
```

### Fixtures: reusable setup and teardown

```python
# pytest
import sqlite3
import pytest

@pytest.fixture
def db():                                    # a fresh in-memory database for each test
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT UNIQUE)")
    yield conn                               # the test runs here
    conn.close()                             # teardown after the test

def add_user(conn, name):
    conn.execute("INSERT INTO users (name) VALUES (?)", (name,))
    return conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

def test_add_user_counts(db):
    assert add_user(db, "ana") == 1
    assert add_user(db, "bo") == 2

def test_duplicate_user_rejected(db):
    add_user(db, "ana")
    with pytest.raises(sqlite3.IntegrityError):
        add_user(db, "ana")

def test_files_with_tmp_path(tmp_path):      # built-in fixture: a unique temporary directory
    f = tmp_path / "out.txt"
    f.write_text("hello")
    assert f.read_text() == "hello"
```

### Test doubles: fakes, stubs, mocks and `monkeypatch`

Test code in **isolation** from slow, unreliable or dangerous things (network, clock, email, payment). Dependency injection ([composition](../../04-oop/composition-design/README.md)) makes this easy.

```python
# pytest
from unittest.mock import Mock
import pytest

class OrderService:
    def __init__(self, gateway, notifier):
        self.gateway, self.notifier = gateway, notifier
    def checkout(self, user, amount):
        receipt = self.gateway.charge(user, amount)
        self.notifier.send(user, f"Paid {amount}: {receipt}")
        return receipt

def test_checkout_charges_and_notifies():
    gateway, notifier = Mock(), Mock()
    gateway.charge.return_value = "R-1"
    service = OrderService(gateway, notifier)

    assert service.checkout("ana", 50) == "R-1"
    gateway.charge.assert_called_once_with("ana", 50)
    notifier.send.assert_called_once_with("ana", "Paid 50: R-1")

def test_checkout_stops_when_payment_fails():
    gateway, notifier = Mock(), Mock()
    gateway.charge.side_effect = RuntimeError("declined")
    with pytest.raises(RuntimeError):
        OrderService(gateway, notifier).checkout("ana", 50)
    notifier.send.assert_not_called()        # nobody is told about a payment that failed

import time

def stamp():
    return time.time()

def test_monkeypatch_replaces_the_clock(monkeypatch):
    monkeypatch.setattr(time, "time", lambda: 1234.0)             # temporarily replaced, restored afterwards
    assert stamp() == 1234.0

def test_logging_is_captured(caplog):
    import logging
    with caplog.at_level(logging.INFO):
        logging.getLogger("demo").info("hello %s", "log")
    assert "hello log" in caplog.text
```

| Double | What it is | Use when |
|--------|-----------|----------|
| **Dummy** | Placeholder never used | A required argument you do not care about |
| **Stub** | Returns canned answers | You need predictable input |
| **Fake** | Working lightweight version (in-memory repository) | You want realistic behavior without the real thing |
| **Mock** | Records calls so you can assert on them | The interaction itself (email sent once) is the behavior |
| **Spy** | Real object that also records calls | Checking calls without replacing behavior |

Prefer **fakes** and **state-based assertions** over heavy mocking; tests tied to internal calls break on every refactor.

### What makes a good test

- **Fast, isolated, deterministic** (no hidden dependence on time, order, network, randomness: inject clocks and seeds).
- **One idea per test**, named for the behavior (`test_checkout_stops_when_payment_fails`).
- **Arrange, Act, Assert** structure.
- Test **behavior through the public interface**, not private details.
- Cover **edge cases**: empty, zero, negative, huge, unicode, duplicate, boundary values, failures.
- A failing test should tell you what is wrong without a debugger.

### Test-driven development (TDD) in one minute

1. **Red:** write a small failing test for the next behavior.
2. **Green:** write the simplest code that makes it pass.
3. **Refactor:** clean up with the tests as a safety net. Repeat.

### Coverage and other tools

- **Coverage** (`pytest --cov=package`) shows which lines tests execute. High coverage does not prove correctness (a test can run a line and assert nothing), but low coverage shows untested risk. Aim for meaningful coverage of important logic, not 100% as a goal.
- **`doctest`** runs examples in docstrings; great for documentation that cannot go stale.
- **Property-based testing** (`hypothesis`) generates many inputs and checks invariants ("sorting twice equals sorting once").
- **Mutation testing**, **linters** (`ruff`), **type checkers** (`mypy`), **pre-commit hooks** and **CI** (run all tests on every push) complete the safety net; see [packaging and tooling](../packaging-tooling/README.md).

```python
import doctest

def double(x):
    """Return twice x.

    >>> double(4)
    8
    >>> double("ab")
    'abab'
    """
    return x * 2

print(doctest.testmod().failed)          # 0   (the examples in the docstring were executed and checked)
```

## 5. Two real-world examples

### Example 1: Production incident, found in minutes
A payment worker occasionally fails at 3 a.m. Because every module uses `logging.getLogger(__name__)`, the logs are JSON with `order_id` and a request id; `log.exception` captured the traceback chain (`ConnectionError` raised `from` a `socket.timeout`). The on-call engineer filters by the order id in the log tool, sees the retry attempts (`attempt=1/3`...), and finds the third-party gateway timing out. A fix adds a longer timeout and a circuit breaker; a regression test reproduces the timeout with a mock that raises `ConnectionError` twice then succeeds. Without structured logs and exception chaining the incident would be guesswork.

### Example 2: Refactoring a pricing module safely
A 600-line pricing function has no tests and is feared by everyone. The team first writes **characterization tests**: feed it 40 real historical orders and assert the existing outputs (`pytest.mark.parametrize`). With that safety net they split the function into small pieces (discounts, tax, shipping), injecting a fake clock and a fake currency-rates service. Each step runs the suite in two seconds; two real bugs surface when edge-case tests (negative quantity, zero-price items) fail. CI blocks merges when tests fail, so the module stays safe to change.

## 6. Tips, tricks and pitfalls

- Catch specific exceptions; never bare `except:`; never `except: pass`.
- Use `raise ... from e` to preserve causes; define a base exception for your package.
- Put cleanup in `with`/`finally`; do not rely on `__del__`.
- Libraries log through loggers and never configure handlers; applications configure logging once at start-up.
- Use `%s`-style lazy arguments in log calls; never log secrets or personal data.
- Log `exception()` where you handle the error, not at every level it passes through.
- Retry only transient, idempotent operations with backoff, jitter and a limit.
- Tests must be deterministic: inject time, randomness and network; avoid sleeping in tests.
- Prefer many small unit tests, fakes over mocks, and behavior over implementation details.
- A flaky test is a bug (in the test or the code): fix or delete it, do not ignore it.
- Run tests in CI on every change; keep the suite fast so people actually run it.
- Reproduce every bug with a failing test **before** fixing it.

## 7. Check yourself

1. What are `try`, `except`, `else` and `finally` each for?
2. Why is `except Exception: pass` dangerous?
3. What does `raise NewError(...) from e` do?
4. Why should a library not configure logging handlers?
5. Why use `log.info("x=%s", x)` instead of an f-string?
6. What does `logger.exception` add?
7. Describe the test pyramid.
8. Fake versus stub versus mock?
9. What does a pytest fixture with `yield` do?
10. Does 100% coverage mean the code is correct?

<details>
<summary>Answers</summary>

1. `try` wraps risky code; `except` handles a specific error; `else` runs only when no exception occurred; `finally` always runs for cleanup.
2. It hides real bugs and failures (including unexpected ones), so problems go unnoticed and are very hard to diagnose.
3. It raises a new, more meaningful exception while recording the original as `__cause__`, so tracebacks show both.
4. The application owns output configuration; library handlers would duplicate or conflict with it. Libraries create loggers and add a `NullHandler` only.
5. Lazy formatting avoids building the message when the level is disabled and keeps messages groupable by template.
6. It logs at ERROR level and appends the current exception's traceback.
7. Many fast unit tests at the base, fewer integration tests in the middle, and a few end-to-end tests at the top.
8. A fake is a lightweight working implementation; a stub returns canned answers; a mock records calls so you can assert on them.
9. Code before `yield` is setup, the yielded value is given to the test, and code after `yield` runs as teardown after the test.
10. No: coverage only shows lines executed, not whether assertions check the right behavior or whether edge cases are covered.

</details>

[Exercises](exercises.md) · [Summary](summary.md)

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

Back to the [part overview](../README.md).
