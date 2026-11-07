# Python Basics 6: Debugging and Testing Your Code

**Prerequisites:** [files, modules and errors](05-files-modules-errors.md). **You will learn:** how to read error messages, find bugs systematically (print debugging, `pdb`, rubber-ducking), and write simple automated tests with `assert`, `unittest` and `pytest`.

## 1. In plain words

Every programmer writes bugs; professionals are the ones who **find and fix them quickly** and **write tests so they stay fixed**. Two skills matter most:

- **Debugging:** finding *why* the program does the wrong thing.
- **Testing:** writing code that checks your code automatically.

## 2. Three kinds of errors

| Kind | When | Example | How you find it |
|------|------|---------|-----------------|
| **Syntax error** | before the program runs | missing colon, unbalanced bracket | Python tells you the line immediately |
| **Runtime error (exception)** | while running | `1 / 0`, wrong key, wrong type | traceback shows where |
| **Logic error** | the program runs but gives wrong answers | uses `+` instead of `-` | tests, comparing with expected values, debugging |

Logic errors are the hardest because Python cannot know what you *meant*.

## 3. Read the error message (traceback) carefully

```python
import traceback

def average(numbers):
    return sum(numbers) / len(numbers)

def report(scores):
    return f"average: {average(scores)}"

try:
    report([])                                  # empty list: len is 0
except ZeroDivisionError:
    print(traceback.format_exc())
# Traceback (most recent call last):
#   File "...", line N, in <module>        <- where it started
#     report([])
#   File "...", line N, in report          <- the middle call
#     return f"average: {average(scores)}"
#   File "...", line N, in average         <- where the error happened
#     return sum(numbers) / len(numbers)
# ZeroDivisionError: division by zero      <- WHAT happened (read this line FIRST)
```

How to read it: **start at the bottom** (the error type and message), then look at the line just above (where it happened), then walk upward to see who called it. The cause is often *one level above* the failing line (here: `report` passed an empty list).

Common messages and likely causes:

| Message | Usually means |
|---------|---------------|
| `NameError: name 'x' is not defined` | typo in a name, or used before assigning |
| `TypeError: unsupported operand type(s)` | mixing types (`"5" + 3`) |
| `IndexError: list index out of range` | index is `>= len(list)` |
| `KeyError: 'name'` | the dictionary lacks that key |
| `AttributeError: 'NoneType' object has no attribute 'x'` | a function returned `None` (forgot `return`?) |
| `IndentationError` | inconsistent indentation |
| `ModuleNotFoundError` | package not installed (or wrong virtual environment) |
| `RecursionError` | recursion without a base case |

## 4. A systematic debugging method

1. **Reproduce** the bug reliably with the smallest input that fails.
2. **Read** the error and traceback.
3. **Form a hypothesis** ("I think `total` is wrong because the loop skips the last item").
4. **Test the hypothesis**: print the value, step through, or add an assert.
5. **Fix** the cause (not the symptom), then **re-run** and add a **test** so it cannot return.
6. **Explain it to a rubber duck** (or a friend): describing the problem out loud often reveals the mistake.

### Print debugging (simple and effective)

```python
def buggy_total(prices, discount):
    total = 0
    for price in prices:
        total += price
        print(f"DEBUG price={price!r} total so far={total!r}")      # show what is really happening
    return total - discount

print(buggy_total([10, 20, 30], 5))
# DEBUG price=10 total so far=10
# DEBUG price=20 total so far=30
# DEBUG price=30 total so far=60
# 55
```

Use `repr` (the `!r` format) to see exact values (`'5'` vs `5`). Remove debug prints afterward, or use the [`logging` module](../../08-modern-python/exceptions-logging-testing/README.md), which can be turned on and off.

### Asserts: make assumptions explicit

```python
def percentage(part, whole):
    assert whole > 0, "whole must be positive"           # fails loudly if the assumption is wrong
    assert 0 <= part <= whole, f"part {part} out of range"
    return part / whole * 100

print(percentage(25, 200))                               # 12.5
try:
    percentage(5, 0)
except AssertionError as error:
    print("assertion failed:", error)                    # assertion failed: whole must be positive
```

Use `assert` for **bugs in your own code** (impossible situations); use `raise ValueError` for **bad input from users**.

### The debugger (`pdb`) and IDE debuggers

`breakpoint()` pauses the program and opens an interactive prompt where you can inspect variables and step line by line:

```text
def f(x):
    breakpoint()          # execution stops here
    return x * 2

(Pdb) p x            print the variable x
(Pdb) n              execute the next line
(Pdb) s              step INTO a function call
(Pdb) c              continue running
(Pdb) l              list the code around the current line
(Pdb) q              quit
```

IDEs (VS Code, PyCharm, WebStorm) offer the same with a click: set a **breakpoint** by clicking next to a line number, run in debug mode, inspect the **variables panel**, step over/into/out, and use **conditional breakpoints** ("stop only when `i == 99`"). Learning one debugger well pays off for your whole career.

### Binary search for bugs

If a long program breaks and you do not know where: add a check halfway; decide whether the bug is before or after it; repeat. In version-controlled code the same idea is `git bisect`.

## 5. Testing: let the computer check your code

A **test** runs your function with known inputs and checks the output. Benefits: you find bugs early, you can change code without fear (re-run the tests), and tests document how code should behave.

### Level 1: plain asserts

```python
def is_leap_year(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

assert is_leap_year(2024)
assert not is_leap_year(2023)
assert not is_leap_year(1900)           # divisible by 100 but not by 400
assert is_leap_year(2000)               # divisible by 400
print("leap year tests passed")
```

### Level 2: `unittest` (built in)

```python
import unittest

def fizzbuzz(n):
    if n % 15 == 0: return "FizzBuzz"
    if n % 3 == 0: return "Fizz"
    if n % 5 == 0: return "Buzz"
    return str(n)

class TestFizzBuzz(unittest.TestCase):
    def test_multiples_of_three(self):
        self.assertEqual(fizzbuzz(9), "Fizz")

    def test_multiples_of_five(self):
        self.assertEqual(fizzbuzz(10), "Buzz")

    def test_multiples_of_both(self):
        self.assertEqual(fizzbuzz(30), "FizzBuzz")

    def test_other_numbers_become_strings(self):
        self.assertEqual(fizzbuzz(7), "7")

result = unittest.TextTestRunner(verbosity=0).run(unittest.defaultTestLoader.loadTestsFromTestCase(TestFizzBuzz))
print(result.wasSuccessful(), result.testsRun)          # True 4
```

(In a project you put tests in `test_*.py` and run `python -m unittest`.)

### Level 3: `pytest` (the community favorite)

`pytest` uses plain `assert` and discovers tests automatically. Install it (`pip install pytest`), put this in `test_discount.py`, run `pytest -q`:

```python
# pytest
import pytest

def discount(price, percent):
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    return round(price * (1 - percent / 100), 2)

def test_ten_percent():
    assert discount(200, 10) == 180

def test_zero_percent_changes_nothing():
    assert discount(99.5, 0) == 99.5

def test_invalid_percent():
    with pytest.raises(ValueError):
        discount(100, 150)

@pytest.mark.parametrize("price, percent, expected", [(100, 50, 50), (80, 25, 60), (0, 10, 0)])
def test_many_cases(price, percent, expected):
    assert discount(price, percent) == expected
```

See [exceptions, logging and testing](../../08-modern-python/exceptions-logging-testing/README.md) for fixtures, mocking and the test pyramid.

### What to test

- The **normal case** (typical inputs).
- **Edge cases:** empty input, zero, one item, negative numbers, maximum values, duplicates, very long strings, `None`.
- **Error cases:** invalid input should raise the expected exception.
- **Bugs you fixed:** write a test that fails before the fix and passes after (a **regression test**).

### Test-driven development (TDD) in a nutshell

1. **Red:** write a failing test for the next small feature.
2. **Green:** write the simplest code that passes.
3. **Refactor:** clean up while the tests stay green.

## 6. A full worked example: find and fix a bug

```python
def find_max(numbers):
    best = 0                              # BUG: wrong when all numbers are negative
    for n in numbers:
        if n > best:
            best = n
    return best

# 1. Reproduce
print(find_max([3, 9, 2]))                # 9   (works)
print(find_max([-5, -2, -9]))             # 0   (wrong! the answer should be -2)

# 2. Hypothesis: `best` starts at 0, which is larger than every negative number.
# 3. Fix: start from the first element (and handle an empty list explicitly).
def find_max_fixed(numbers):
    if not numbers:
        raise ValueError("find_max_fixed() needs at least one number")
    best = numbers[0]
    for n in numbers[1:]:
        if n > best:
            best = n
    return best

# 4. Regression tests: they would have caught the bug
assert find_max_fixed([3, 9, 2]) == 9
assert find_max_fixed([-5, -2, -9]) == -2
assert find_max_fixed([7]) == 7
try:
    find_max_fixed([])
except ValueError:
    print("empty list rejected; tests pass")
```

## 7. Two real-world examples

**Example 1: The mystery `NoneType` crash.** A web page crashes with `AttributeError: 'NoneType' object has no attribute 'email'`. The traceback shows `user.email` failing; one level up, `find_user(id)` returns `None` when no row matches. The fix is to handle the missing user (return a 404), and a regression test calls the page with an unknown id so it never crashes again.

**Example 2: A pricing bug caught by tests.** A developer refactors a tax function. The existing tests (including the edge cases "price 0" and "tax-exempt item") fail immediately, pointing at the line where rounding changed. Without tests the bug would have shipped and customers would have been over-charged.

## 8. Common mistakes

- Changing code randomly hoping it works instead of forming a hypothesis.
- Fixing the symptom (catching an exception) but not the cause.
- Leaving debug `print`s in production code.
- Testing only the "happy path".
- Tests that depend on each other, random numbers, today's date or the network (flaky tests).
- Not re-running tests after changes.
- Ignoring warnings and the first lines of tracebacks.

## 9. Practice

1. The function below should return the average of positive numbers only but gives wrong results. Debug it and write tests.
   ```python
   def avg_positive(nums):
       total = 0
       for n in nums:
           if n > 0:
               total += n
       return total / len(nums)
   ```
2. Write `is_palindrome` and at least six tests (including empty string and punctuation).
3. Use `breakpoint()` (or an IDE) to step through `fizzbuzz` for `n = 15` and note each variable.
4. Write a `unittest` class for a `clamp(value, low, high)` function.
5. Create a regression test for the `find_max` bug in the example.

<details>
<summary>Solutions</summary>

**1.** The divisor should be the count of *positive* numbers, not `len(nums)`; also handle "no positives".
```python
def avg_positive(nums):
    positives = [n for n in nums if n > 0]
    if not positives:
        raise ValueError("no positive numbers")
    return sum(positives) / len(positives)

assert avg_positive([2, 4, -10]) == 3
assert avg_positive([5]) == 5
try:
    avg_positive([-1, 0])
except ValueError:
    pass
```

**2.**
```python
def is_palindrome(text):
    cleaned = [c.lower() for c in text if c.isalnum()]
    return cleaned == cleaned[::-1]

for text, expected in [("racecar", True), ("hello", False), ("", True), ("A man, a plan, a canal: Panama", True), ("ab", False), ("!!", True)]:
    assert is_palindrome(text) is expected, text
```

**3.** In the debugger, `n = 15`: `n % 15 == 0` is True on the first check so it returns `"FizzBuzz"` immediately; the later checks are never reached.

**4.**
```python
def clamp(value, low, high):
    return max(low, min(value, high))

class TestClamp(unittest.TestCase):
    def test_inside(self): self.assertEqual(clamp(5, 0, 10), 5)
    def test_below(self): self.assertEqual(clamp(-1, 0, 10), 0)
    def test_above(self): self.assertEqual(clamp(99, 0, 10), 10)
    def test_edges(self):
        self.assertEqual(clamp(0, 0, 10), 0)
        self.assertEqual(clamp(10, 0, 10), 10)

print(unittest.TextTestRunner(verbosity=0).run(unittest.defaultTestLoader.loadTestsFromTestCase(TestClamp)).wasSuccessful())
```

**5.**
```python
assert find_max_fixed([-5, -2, -9]) == -2      # fails against the original find_max, passes after the fix
```

</details>

## 10. Check yourself

1. What are the three kinds of errors?
2. Which part of a traceback do you read first?
3. What is the difference between `assert` and `raise ValueError`?
4. What is a regression test?
5. What are the steps of a systematic debugging method?
6. Name three edge cases worth testing for most functions.

<details>
<summary>Answers</summary>

1. Syntax errors, runtime errors (exceptions) and logic errors.
2. The last line (the error type and message), then the line above it where it happened.
3. `assert` checks assumptions about your own code (bugs); `raise ValueError` reports invalid input that callers should handle.
4. A test that fails when a previously fixed bug returns.
5. Reproduce, read the error, hypothesize, test the hypothesis, fix the cause, re-run and add a test.
6. Empty input, a single item, zero/negative values (also `None`, duplicates, very large values).

</details>

[Back to Python fundamentals](README.md) · Previous: [files, modules and errors](05-files-modules-errors.md) · Next: [classes: a first look](07-classes-first-look.md)
