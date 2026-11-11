# Testing in Depth: Exercises

These problems go with the [Testing in Depth lesson](README.md). Try each one before opening its solution.

## Problems

1. Add a parametrized test for `parse_money` covering `"$1,000"`, `".5"` and `"1e2"`. What does your implementation return for each, and are those the results you want?
2. Write a fixture `db` using `sqlite3.connect(":memory:")` that creates a `users` table, yields the connection and closes it afterwards, and a test that inserts and reads a row.
3. Test `send_with_retry` so that `time.sleep` (if you add a back-off) is never really called: how would you do it by injection and by `monkeypatch`?
4. Write a Hypothesis property for `apply_discount`: for any non-negative price and percent in range, the result is at most the price and never negative.
5. Find a property for a function `unique(xs)` that removes duplicates while keeping order.
6. Why is `Mock(spec=Cart)` safer than `Mock()`?

<details>
<summary>Setup: the <code>pricing.py</code> module from the lesson (the solutions import it)</summary>

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

</details>

<details>
<summary>Solutions</summary>

**1.**
```python
# file: test_exercise_1.py
import pytest
from decimal import Decimal
from pricing import parse_money
@pytest.mark.parametrize("text, expected", [("$1,000", "1000.00"), (".5", "0.50"), ("1e2", "100.00")])
def test_more_money_formats(text, expected):
    assert parse_money(text) == Decimal(expected)
```
All three pass: `"1e2"` is accepted as 100 because `Decimal` understands scientific notation. If you do not want that, tighten the parser with a regular expression; the test documents the decision.

**2.**
```python
# file: test_exercise_2.py
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

**3.** By injection: give `send_with_retry` a `sleep=time.sleep` parameter and pass `lambda s: None` in tests. By `monkeypatch`: `monkeypatch.setattr("notifier.time.sleep", lambda s: None)` (the module must `import time`). Injection is simpler and needs no knowledge of the module's imports.

**4.**
```python
# file: test_exercise_4.py
from decimal import Decimal
from hypothesis import given, strategies as st
from pricing import apply_discount
@given(st.decimals(min_value=0, max_value=10**6, places=2), st.integers(0, 100))
def test_discount_bounds(price, percent):
    result = apply_discount(price, percent)
    assert Decimal(0) <= result <= price
```

**5.** For example: the result has no duplicates (`len(set(r)) == len(r)`), every element of `r` is in `xs`, every element of `xs` is in `r`, and the elements appear in the same order as their first occurrence in `xs` (compare with a slow reference implementation).

**6.** `Mock(spec=Cart)` only allows attributes and methods that `Cart` really has, so a misspelt method or a call that no longer exists raises `AttributeError` instead of silently passing.

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Testing in Depth](01-pytest-mocking-and-property-testing.md)
