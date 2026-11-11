# Testing in Depth: pytest, Fixtures, Mocking and Property-Based Testing

**Prerequisites:** [Python fundamentals: debugging and testing](../../00-foundations/python-fundamentals/06-debugging-and-testing.md), [exceptions, logging and testing](../exceptions-logging-testing/README.md), [decorators and functions](../../00-foundations/python-fundamentals/03-functions.md). **You will learn:** how to write fast, readable tests with **pytest** (plain `assert`, parametrization, fixtures, temporary files, marks), how to **isolate** code with `unittest.mock` and `monkeypatch` (and when to inject dependencies instead), how **property-based testing** with **Hypothesis** finds bugs you would never think to test for, how to read **coverage**, and how to design a test suite that stays useful. The lesson uses third-party packages (`pip install pytest hypothesis pytest-cov`); every example file was run for real and the outputs shown are the actual ones.

## 1. In plain words

A test is a small program that runs your code and **checks the result**. Tests let you change code without fear: if you break something, a test fails in seconds instead of a customer finding it in weeks. A good suite is **fast** (so you run it constantly), **deterministic** (same result every time), **independent** (tests do not depend on each other) and **readable** (a failing test name tells you what broke).

Shape of a test, the **arrange-act-assert** pattern:

1. **Arrange:** set up inputs and objects.
2. **Act:** call the code under test.
3. **Assert:** check the outcome.

## 2. pytest basics

pytest finds files named `test_*.py`, functions named `test_*` and runs them. You write a plain `assert`; when it fails, pytest **rewrites the assertion** to show you the values involved. Here is a small module and its tests.

```python
# file: pricing.py
from decimal import Decimal, ROUND_HALF_UP

def parse_money(text: str) -> Decimal:
    """'$12.50' -> Decimal('12.50'); raises ValueError for anything that is not money."""
    cleaned = text.strip().lstrip("$").replace(",", "")
    try:
        value = Decimal(cleaned)
    except Exception:
        raise ValueError(f"not a money amount: {text!r}") from None
    if value < 0:
        raise ValueError("money cannot be negative")
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def apply_discount(price: Decimal, percent: int) -> Decimal:
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    return (price * (100 - percent) / 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
```

```python
# file: test_pricing.py
from decimal import Decimal
import pytest
from pricing import apply_discount, parse_money

def test_parse_simple_amount():
    assert parse_money("$12.50") == Decimal("12.50")

@pytest.mark.parametrize("text, expected", [          # one test function, many cases
    ("$1,234.5", "1234.50"),
    ("  7  ", "7.00"),
    ("0.005", "0.01"),                                 # rounds half up
    ("$0", "0.00"),
])
def test_parse_variants(text, expected):
    assert parse_money(text) == Decimal(expected)

@pytest.mark.parametrize("bad", ["", "abc", "$-5", "12.3.4"])
def test_parse_rejects_bad_input(bad):
    with pytest.raises(ValueError):                    # the test passes only if this exception is raised
        parse_money(bad)

def test_error_message_names_the_input():
    with pytest.raises(ValueError, match="not a money amount: 'abc'"):     # match= checks the message (a regex)
        parse_money("abc")

def test_discount():
    assert apply_discount(Decimal("80.00"), 25) == Decimal("60.00")

@pytest.mark.parametrize("percent", [-1, 101])
def test_discount_rejects_out_of_range(percent):
    with pytest.raises(ValueError):
        apply_discount(Decimal("10"), percent)
```

Run them from the project folder:

```text
$ pytest -q
.............                                                            [100%]
13 passed in 0.48s
```

Thirteen tests from six functions: `parametrize` turns one function into one test per row, and each shows up individually (for example `test_parse_variants[0.005-0.01]`). When an assertion fails, pytest explains it. If we deliberately expect `61.00`:

```text
    def test_discount_wrong_expectation():
>       assert apply_discount(Decimal("80.00"), 25) == Decimal("61.00")
E       AssertionError: assert Decimal('60.00') == Decimal('61.00')
E        +  where Decimal('60.00') = apply_discount(Decimal('80.00'), 25)
E        +    where Decimal('80.00') = Decimal('80.00')
E        +  and   Decimal('61.00') = Decimal('61.00')
```

Useful command-line options: `pytest -x` (stop at the first failure), `pytest -k discount` (run tests whose name matches), `pytest tests/test_pricing.py::test_discount` (one test), `pytest -v` (verbose), `pytest --lf` (rerun only the last failures), `pytest -s` (show `print` output), `pytest --pdb` (drop into the debugger on failure).

## 3. Fixtures: reusable setup and teardown

A **fixture** is a function that provides something a test needs. A test **asks** for it by naming it as a parameter; pytest builds it and passes it in (**dependency injection**). Fixtures can use other fixtures, can clean up after themselves with `yield`, and several are built in (`tmp_path` gives a fresh temporary directory, `monkeypatch`, `capsys`, `caplog`).

```python
# file: cart.py
class Cart:
    def __init__(self):
        self.items = {}                       # name -> (unit_price_cents, quantity)

    def add(self, name, price_cents, qty=1):
        if qty < 1:
            raise ValueError("quantity must be at least 1")
        old_price, old_qty = self.items.get(name, (price_cents, 0))
        self.items[name] = (price_cents, old_qty + qty)

    def total_cents(self):
        return sum(price * qty for price, qty in self.items.values())
```

```python
# file: test_cart.py
import pytest
from cart import Cart

@pytest.fixture
def cart():
    return Cart()                              # a fresh cart for every test that asks for it

@pytest.fixture
def full_cart(cart):                           # fixtures can use other fixtures
    cart.add("pen", 150, 2)
    cart.add("book", 1200)
    return cart

def test_empty_cart_is_free(cart):
    assert cart.total_cents() == 0

def test_total(full_cart):
    assert full_cart.total_cents() == 1500

def test_adding_same_item_increases_quantity(cart):
    cart.add("pen", 150)
    cart.add("pen", 150, 3)
    assert cart.items["pen"] == (150, 4)

def test_rejects_zero_quantity(cart):
    with pytest.raises(ValueError):
        cart.add("pen", 150, 0)

def test_report_file(tmp_path, full_cart):     # tmp_path: a built-in fixture giving a fresh temporary directory
    report = tmp_path / "total.txt"
    report.write_text(str(full_cart.total_cents()))
    assert report.read_text() == "1500"

@pytest.fixture
def resource():
    log = ["open"]
    yield log                                  # the test runs here
    log.append("closed")                       # teardown: runs even if the test failed
    assert log == ["open", "used", "closed"]

def test_uses_resource(resource):
    resource.append("used")

@pytest.mark.skip(reason="demonstration")
def test_skipped():
    assert False

@pytest.mark.xfail(reason="known bug", strict=True)     # expected to fail; strict=True flags it if it unexpectedly passes
def test_known_bug():
    assert 0.1 + 0.2 == 0.3
```

```text
$ pytest -q -rsx test_pricing.py test_cart.py
...................sx                                                    [100%]
=========================== short test summary info ============================
SKIPPED [1] test_cart.py:44: demonstration
XFAIL test_cart.py::test_known_bug - known bug
19 passed, 1 skipped, 1 xfailed in 0.48s
```

**Scope:** a fixture runs once per test by default; `@pytest.fixture(scope="module")` or `"session"` shares an expensive one (a database connection) across many tests, trading isolation for speed. Put shared fixtures in a file named **`conftest.py`**, which pytest loads automatically for tests in that folder. **Marks** label tests (`@pytest.mark.slow`) so you can select or skip groups (`pytest -m "not slow"`).

## 4. Isolating code: inject first, mock second

Real code talks to clocks, networks, files and databases. Tests need those parts to be **fast and predictable**. Two tools:

1. **Dependency injection (best):** pass the dependency in, so the test passes a simple fake. No patching, no magic.
2. **Mocking:** replace the real object temporarily with a `Mock` that records how it was used and returns what you tell it.

```python
# file: notifier.py
import os
from datetime import datetime

def greeting(now=None):
    now = now or datetime.now()               # injectable: tests can pass a time in
    return "Good morning" if now.hour < 12 else "Good afternoon"

def send_with_retry(client, message, attempts=3):
    for n in range(attempts):
        try:
            return client.send(message)
        except TimeoutError:
            if n == attempts - 1:
                raise

def api_url():
    return os.environ.get("API_URL", "https://api.example.com")
```

```python
# file: test_notifier.py
from datetime import datetime
from unittest.mock import Mock, patch
import pytest
import notifier

def test_greeting_with_injected_time():            # best: pass the dependency in, no mocking needed
    assert notifier.greeting(datetime(2026, 1, 1, 9)) == "Good morning"
    assert notifier.greeting(datetime(2026, 1, 1, 15)) == "Good afternoon"

def test_greeting_with_patched_clock():            # when you cannot inject: patch where the name is LOOKED UP
    with patch("notifier.datetime") as fake:
        fake.now.return_value = datetime(2026, 1, 1, 8)
        assert notifier.greeting() == "Good morning"

def test_retry_succeeds_after_timeouts():
    client = Mock()
    client.send.side_effect = [TimeoutError, TimeoutError, "delivered"]    # fail twice, then succeed
    assert notifier.send_with_retry(client, "hi") == "delivered"
    assert client.send.call_count == 3
    client.send.assert_called_with("hi")

def test_retry_gives_up():
    client = Mock()
    client.send.side_effect = TimeoutError
    with pytest.raises(TimeoutError):
        notifier.send_with_retry(client, "hi", attempts=2)
    assert client.send.call_count == 2

def test_env_var(monkeypatch):                      # monkeypatch undoes itself after the test
    monkeypatch.setenv("API_URL", "http://localhost:9999")
    assert notifier.api_url() == "http://localhost:9999"

def test_env_default(monkeypatch):
    monkeypatch.delenv("API_URL", raising=False)
    assert notifier.api_url() == "https://api.example.com"
```

Mocking rules of thumb:

- **Patch where the name is used, not where it is defined** (`patch("notifier.datetime")`, because `notifier` looked up `datetime` in its own namespace).
- A `Mock` accepts **any** attribute and call, so a typo passes silently. Use `Mock(spec=RealClass)` or `create_autospec` so calls that do not match the real interface fail.
- `side_effect` with a list returns or raises each item in turn (great for simulating flaky services); with an exception it raises it.
- Assert on **behaviour that matters** (the request sent, the result returned), not on every internal call, or the tests break whenever you refactor.
- Mock the **boundaries** of your system (HTTP, clock, email), not your own pure functions. Too many mocks means you are testing the mocks.

## 5. Property-based testing with Hypothesis

Example-based tests check the cases you thought of. **Property-based tests** state a rule that must hold for **all** inputs, and the library (Hypothesis) generates hundreds of inputs, including nasty edge cases, then **shrinks** a failure to the smallest counterexample. Properties worth looking for: **round trips** (`decode(encode(x)) == x`), **idempotence** (`sort(sort(x)) == sort(x)`), **invariants** (length preserved, output sorted), and comparison with a **slow, obviously correct** version.

```python
# file: test_sorting.py
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_sorting_properties(xs):
    ys = sorted(xs)
    assert len(ys) == len(xs)                         # nothing lost or added
    assert all(a <= b for a, b in zip(ys, ys[1:]))    # actually ordered
    assert sorted(ys) == ys                           # idempotent
```

Now a more interesting example: **run-length encoding** (compress `"aaabb"` as `"3a2b"`). Here is a first draft, with a round-trip property test:

```python
# first draft of rle.py (has a bug)
def encode(s: str) -> str:
    out, i = [], 0
    while i < len(s):
        j = i
        while j < len(s) and s[j] == s[i]:
            j += 1
        out.append(f"{j - i}{s[i]}")
        i = j
    return "".join(out)

def decode(s: str) -> str:
    out, count = [], ""
    for ch in s:
        if ch.isdigit():
            count += ch
        else:
            out.append(ch * int(count))
            count = ""
    return "".join(out)
```

```python
# file: test_properties.py
from hypothesis import given, strategies as st
from rle import decode, encode

@given(st.text())
def test_rle_round_trip(s):
    assert decode(encode(s)) == s
```

A hand-written example test such as `decode(encode("aaabb")) == "aaabb"` would pass. Hypothesis fails it at once (abridged output):

```text
AssertionError: assert '' == '0'
Failing test case: test_rle_round_trip(
    s='0',
)
```

The smallest failing input is the single character `'0'`: it is encoded as `"10"` (one zero), and `decode` cannot tell that the `0` is data and not part of a count. (The same run also found a second failure with a Unicode digit, `'²'`, which `isdigit()` accepts but `int()` rejects: another bug no one would think to test by hand.) The fix is an unambiguous format: write each run as `<count>:<char>`.

```python
# file: rle.py
def encode(s: str) -> str:
    """'aaab' -> '3:a1:b'. Every run is written as <count>:<char>, so digits in the data cannot be confused with counts."""
    out, i = [], 0
    while i < len(s):
        j = i
        while j < len(s) and s[j] == s[i]:
            j += 1
        out.append(f"{j - i}:{s[i]}")
        i = j
    return "".join(out)

def decode(s: str) -> str:
    out, i = [], 0
    while i < len(s):
        colon = s.index(":", i)
        out.append(s[colon + 1] * int(s[i:colon]))
        i = colon + 2
    return "".join(out)
```

```text
$ pytest -q test_properties.py test_sorting.py
..                                                                       [100%]
2 passed in 0.62s
```

Hypothesis remembers failures it has found (in a `.hypothesis` folder) and replays them first next time; keep it out of version control but keep the **specific example** as a normal regression test with `@example("0")` on the property or as its own test. Control with `@settings(max_examples=500)`, build custom data with `st.builds`, `st.one_of`, `st.sampled_from`, and filter with `assume()` sparingly.

## 6. Measuring coverage

**Coverage** tells you which lines your tests ran: `pip install pytest-cov`, then `pytest --cov=pricing --cov=cart --cov-report=term-missing`.

```text
Name         Stmts   Miss  Cover   Missing
------------------------------------------
cart.py         10      0   100%
pricing.py      14      0   100%
------------------------------------------
TOTAL           24      0   100%
```

Use coverage to **find untested code** (the `Missing` column lists line numbers), not as a goal in itself: a test with no assertions gives 100 percent coverage and proves nothing. **Mutation testing** (`mutmut`) goes further by changing your code (turning `<` into `<=`) and checking that a test notices. Branch coverage (`--cov-branch`) is stricter than line coverage.

## 7. Designing a good test suite

- **Test behaviour, not implementation:** what the function promises, so refactoring does not break tests.
- **The test pyramid:** many fast **unit** tests, fewer **integration** tests (several parts together, a real test database), a handful of slow **end-to-end** tests.
- **One reason to fail:** a test name like `test_rejects_negative_quantity` tells you what broke without opening the file.
- **Test the edges:** empty input, one item, maximum size, wrong types, boundaries (0, 1, 100, 101).
- **Make tests deterministic:** control time, randomness (seed it), ordering; do not depend on the network or on test execution order.
- **Fix flaky tests immediately** (tests that sometimes fail for no reason): they teach everyone to ignore failures.
- **Test-driven development (TDD):** write a failing test, make it pass with the simplest code, refactor; the test captures the requirement before the code exists. When you find a bug, **first write a test that reproduces it**, then fix it, so it can never return.
- Run tests in **continuous integration** on every push (see [CI and workflow](../engineering-workflow/01-ci-docker-pre-commit-and-publishing.md)).

## 8. Common mistakes

- Tests that depend on each other or on execution order (shared global state).
- Asserting too little (`assert result`) or too much (every internal call).
- Over-mocking: tests pass while the real integration is broken. Include at least some tests against real components (an in-memory SQLite or a test container).
- Patching the wrong name (`patch("datetime.datetime")` instead of where it is imported).
- Catching exceptions in tests and `pass`ing, so the test can never fail; use `pytest.raises`.
- Using real time (`time.sleep`) or the real clock in tests, making them slow or flaky.
- Chasing 100 percent coverage with meaningless tests.
- Not running the tests automatically.

## 9. Two real-world examples

**Example 1: The parser that Hypothesis broke.** A team wrote a date-range parser with 40 hand-written test cases. Adding one property ("parsing the printed form of any valid range gives back the same range") immediately found a crash on ranges crossing a leap day and another on empty strings that no one had listed. Both became permanent regression tests.

**Example 2: The slow suite.** A project's 40-minute test run was skipped by developers. Profiling showed most time went to tests that created a real database for every test. Switching to a session-scoped database with a transaction rolled back after each test (a fixture with `yield`) brought it to 3 minutes, and people started running it before every commit.

## 10. Practice

1. Add a parametrized test for `parse_money` covering `"$1,000"`, `".5"` and `"1e2"`. What does your implementation return for each, and are those the results you want?
2. Write a fixture `db` using `sqlite3.connect(":memory:")` that creates a `users` table, yields the connection and closes it afterwards, and a test that inserts and reads a row.
3. Test `send_with_retry` so that `time.sleep` (if you add a back-off) is never really called: how would you do it by injection and by `monkeypatch`?
4. Write a Hypothesis property for `apply_discount`: for any non-negative price and percent in range, the result is at most the price and never negative.
5. Find a property for a function `unique(xs)` that removes duplicates while keeping order.
6. Why is `Mock(spec=Cart)` safer than `Mock()`?

<details>
<summary>Solutions</summary>

1. ```python
   import pytest
   from decimal import Decimal
   from pricing import parse_money
   @pytest.mark.parametrize("text, expected", [("$1,000", "1000.00"), (".5", "0.50"), ("1e2", "100.00")])
   def test_more_money_formats(text, expected):
       assert parse_money(text) == Decimal(expected)
   ```
   All three pass: `"1e2"` is accepted as 100 because `Decimal` understands scientific notation. If you do not want that, tighten the parser with a regular expression; the test documents the decision.
2. ```python
   import sqlite3, pytest
   @pytest.fixture
   def db():
       conn = sqlite3.connect(":memory:")
       conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
       yield conn
       conn.close()
   def test_insert_and_read(db):
       db.execute("INSERT INTO users (name) VALUES (?)", ("ada",))
       assert db.execute("SELECT name FROM users").fetchone() == ("ada",)
   ```
3. By injection: give `send_with_retry` a `sleep=time.sleep` parameter and pass `lambda s: None` in tests. By `monkeypatch`: `monkeypatch.setattr("notifier.time.sleep", lambda s: None)` (the module must `import time`). Injection is simpler and needs no knowledge of the module's imports.
4. ```python
   from decimal import Decimal
   from hypothesis import given, strategies as st
   from pricing import apply_discount
   @given(st.decimals(min_value=0, max_value=10**6, places=2), st.integers(0, 100))
   def test_discount_bounds(price, percent):
       result = apply_discount(price, percent)
       assert Decimal(0) <= result <= price
   ```
5. For example: the result has no duplicates (`len(set(r)) == len(r)`), every element of `r` is in `xs`, every element of `xs` is in `r`, and the elements appear in the same order as their first occurrence in `xs` (compare with a slow reference implementation).
6. `Mock(spec=Cart)` only allows attributes and methods that `Cart` really has, so a misspelt method or a call that no longer exists raises `AttributeError` instead of silently passing.

</details>

## 11. Check yourself

1. What is the arrange-act-assert pattern?
2. What do `parametrize` and fixtures each give you?
3. Why prefer dependency injection over patching?
4. Where should you patch a name, and why?
5. What is a property-based test and what is shrinking?
6. What does 100 percent line coverage prove, and what does it not?
7. What makes a test suite useful over time?

<details>
<summary>Answers</summary>

1. Set up inputs, call the code under test, then check the result.
2. `parametrize` runs one test body over many input rows as separate tests; fixtures supply (and clean up) the objects tests need, injected by parameter name.
3. A fake passed as an argument needs no patching magic, keeps tests readable and keeps the code more modular.
4. Where the name is looked up (the module under test), because that is the reference being replaced.
5. A test that states a rule holding for all inputs, with generated inputs; shrinking reduces a failing input to the smallest one that still fails.
6. It proves every line ran at least once; it does not prove assertions were meaningful or that logic is correct.
7. Fast, deterministic, independent, behaviour-focused tests, run automatically on every change, with flaky tests fixed immediately.

</details>

[Back to Modern Python](../README.md)
