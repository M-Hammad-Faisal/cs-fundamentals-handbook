# Python Fundamentals: Exercises

These problems go with the [Python Fundamentals lesson](README.md). Try each one before opening its solution.

<details>
<summary>Setup code the solutions use (copied from the lessons)</summary>

```python
import unittest
import json
import csv
import os, tempfile
from pathlib import Path
import sys, importlib, tempfile, textwrap

folder = tempfile.mkdtemp()                       # a throwaway folder so these examples can run anywhere
path = os.path.join(folder, "notes.txt")

with open(path, "w", encoding="utf-8") as f:      # "w" = write (creates or overwrites)
    f.write("first line\n")
    f.write("second line\n")
    f.writelines(["third line\n", "fourth line\n"])

with open(path, encoding="utf-8") as f:           # "r" = read (the default)
    whole = f.read()

print(repr(whole[:22]))                           # 'first line\nsecond line\n'

with open(path, encoding="utf-8") as f:
    for line_number, line in enumerate(f, start=1):      # iterate: reads one line at a time (big-file friendly)
        print(line_number, line.rstrip("\n"))

with open(path, "a", encoding="utf-8") as f:      # "a" = append to the end
    f.write("fifth line\n")

with open(path, encoding="utf-8") as f:
    lines = f.read().splitlines()

print(len(lines), lines[-1])                      # 5 fifth line


root = Path(folder)
p = root / "data" / "report.txt"                  # / joins path parts on any operating system
p.parent.mkdir(parents=True, exist_ok=True)       # create the folder (and parents) if missing
p.write_text("hello\n", encoding="utf-8")
print(p.name, p.stem, p.suffix, p.exists(), p.read_text(encoding="utf-8").strip())    # report.txt report .txt True hello
print(sorted(x.name for x in root.rglob("*.txt")))                  # ['notes.txt', 'report.txt']
print(p.stat().st_size, p.is_file(), p.parent.is_dir())             # 6 True True


mod_dir = tempfile.mkdtemp()
Path(mod_dir, "geometry.py").write_text(textwrap.dedent('''
    """Small geometry helpers."""
    import math

    def circle_area(radius):
        return math.pi * radius ** 2

    def rectangle_area(width, height):
        return width * height

    if __name__ == "__main__":          # runs only when executed directly, NOT when imported
        print("running as a script")

'''), encoding="utf-8")

sys.path.insert(0, mod_dir)               # make the folder importable (normally your project folder already is)
geometry = importlib.import_module("geometry")
print(round(geometry.circle_area(2), 2), geometry.rectangle_area(3, 4))      # 12.57 12


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


class BankAccount:
    """A simple bank account that cannot go negative."""

    def __init__(self, owner, balance=0):
        if balance < 0:
            raise ValueError("opening balance cannot be negative")
        self.owner = owner
        self.balance = balance
        self.history = []                          # each object gets its OWN list

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("deposit must be positive")
        self.balance += amount
        self.history.append(("deposit", amount))

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("withdrawal must be positive")
        if amount > self.balance:
            raise ValueError("insufficient funds")
        self.balance -= amount
        self.history.append(("withdraw", amount))

    def __str__(self):
        return f"{self.owner}: balance {self.balance}"

acct = BankAccount("Ayesha", 100)
acct.deposit(50)
acct.withdraw(30)
print(acct)                                        # Ayesha: balance 120
print(acct.history)                                # [('deposit', 50), ('withdraw', 30)]

try:
    acct.withdraw(1000)

except ValueError as error:
    print("rejected:", error)                      # rejected: insufficient funds

other = BankAccount("Bilal")
other.deposit(10)
print(acct.balance, other.balance)                 # 120 10      (independent objects)
```

</details>

## Problems

### Variables, Types and Operators

1. Ask for (simulate) a number of seconds, 4,000, and print it as `HH:MM:SS`.
2. Swap two variables without a third variable (in two different ways).
3. Predict: `5 // 2`, `-5 // 2`, `5 % -2`, `2 ** 3 ** 2`, `not 0 and 1`.
4. Convert 100 degrees Celsius to Fahrenheit and print with one decimal.
5. A rectangle has width 7.5 and height 3.2. Print area and perimeter, each rounded to 2 decimals.
6. Why does `0.1 + 0.2 == 0.3` print `False`?

<details>
<summary>Solutions</summary>

**1.**
```python
seconds = 4000
hours, rest = divmod(seconds, 3600)
minutes, secs = divmod(rest, 60)
print(f"{hours:02d}:{minutes:02d}:{secs:02d}")           # 01:06:40
```

**2.**
```python
a, b = 1, 2
a, b = b, a                       # tuple swap
a = a + b; b = a - b; a = a - b   # arithmetic swap
print(a, b)                       # 1 2   (swapped twice, back to the start)
```

**3.** `2`, `-3`, `-1`, `512` (`**` associates right-to-left: `3 ** 2 = 9`, `2 ** 9`), `1`.
```python
print(5 // 2, -5 // 2, 5 % -2, 2 ** 3 ** 2, not 0 and 1)
```

**4.**
```python
c = 100
print(f"{c * 9 / 5 + 32:.1f}")           # 212.0
```

**5.**
```python
w, h = 7.5, 3.2
print(f"area={w * h:.2f} perimeter={2 * (w + h):.2f}")     # area=24.00 perimeter=21.40
```

**6.** Because 0.1 and 0.2 are stored as slightly inexact binary fractions, their sum is 0.30000000000000004; use `math.isclose` or `Decimal`.

</details>

### Making Decisions and Repeating Things

1. Print the multiplication table of 7 from 1 to 10.
2. Sum all numbers from 1 to 1000 that are divisible by 3 or 5.
3. Given a list, print the second largest value without sorting.
4. Reverse a string using a loop (no slicing).
5. Print a right-aligned triangle of height 5.
6. Count vowels in a sentence.
7. Guess-the-number: given a secret and a list of guesses, print "too low/high/correct" and stop at the right guess.

<details>
<summary>Solutions</summary>

**1.**
```python
for i in range(1, 11):
    print(f"7 x {i:2d} = {7 * i:3d}")
```

**2.**
```python
print(sum(n for n in range(1, 1001) if n % 3 == 0 or n % 5 == 0))      # 234168
```

**3.**
```python
data = [5, 9, 2, 9, 7]
largest = second = float("-inf")
for n in data:
    if n > largest:
        second, largest = largest, n
    elif largest > n > second:
        second = n
print(second)                         # 7
```

**4.**
```python
text, reversed_text = "python", ""
for ch in text:
    reversed_text = ch + reversed_text
print(reversed_text)                  # nohtyp
```

**5.**
```python
for i in range(1, 6):
    print(" " * (5 - i) + "*" * i)
```

**6.**
```python
sentence = "Programming is fun"
print(sum(1 for ch in sentence.lower() if ch in "aeiou"))      # 5
```

**7.**
```python
secret = 42
for guess in [10, 90, 42, 50]:
    if guess < secret:
        print(guess, "too low")
    elif guess > secret:
        print(guess, "too high")
    else:
        print(guess, "correct")
        break
```

</details>

### Functions

1. Write `celsius_to_fahrenheit(c)` and test with `assert`.
2. Write `is_even(n)`, `count_vowels(text)`, and `average(numbers)` (handle an empty list by raising `ValueError`).
3. Write `clamp(value, low=0, high=100)` returning `value` limited to the range.
4. Write `fibonacci(n)` iteratively and recursively; compare their speed for n = 30.
5. Write `compose(f, g)` returning a function that applies `g` then `f`.
6. Write a recursive `power(base, exp)` and a recursive `reverse(text)`.
7. Fix: `def append_to(x, lst=[]): lst.append(x); return lst`.

<details>
<summary>Solutions</summary>

**1.**
```python
def celsius_to_fahrenheit(c):
    return c * 9 / 5 + 32
assert celsius_to_fahrenheit(100) == 212 and celsius_to_fahrenheit(0) == 32
```

**2.**
```python
def is_even(n): return n % 2 == 0
def count_vowels(text): return sum(1 for ch in text.lower() if ch in "aeiou")
def average(numbers):
    if not numbers:
        raise ValueError("cannot average an empty list")
    return sum(numbers) / len(numbers)
assert is_even(4) and count_vowels("Python Rocks") == 2 and average([2, 4]) == 3
```

**3.**
```python
def clamp(value, low=0, high=100):
    return max(low, min(value, high))
assert clamp(150) == 100 and clamp(-5) == 0 and clamp(50) == 50 and clamp(5, 10, 20) == 10
```

**4.**
```python
import time
def fib_iter(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
def fib_rec(n):
    return n if n < 2 else fib_rec(n - 1) + fib_rec(n - 2)
t = time.perf_counter(); fib_iter(30); fast = time.perf_counter() - t
t = time.perf_counter(); fib_rec(30); slow = time.perf_counter() - t
print(fib_iter(30) == fib_rec(30), slow > fast * 100)     # True True  (the recursive one repeats the same work millions of times)
```

**5.**
```python
def compose(f, g):
    return lambda x: f(g(x))
add_one_then_double = compose(lambda x: x * 2, lambda x: x + 1)
print(add_one_then_double(5))                              # 12
```

**6.**
```python
def power_rec(base, exp):
    return 1 if exp == 0 else base * power_rec(base, exp - 1)
def reverse_rec(text):
    return text if len(text) <= 1 else reverse_rec(text[1:]) + text[0]
print(power_rec(2, 10), reverse_rec("python"))             # 1024 nohtyp
```

**7.**
```python
def append_to(x, lst=None):
    if lst is None:
        lst = []
    lst.append(x)
    return lst
```

</details>

### Strings, Lists, Tuples, Dictionaries and Sets

1. Reverse each word in `"python is fun"` but keep the word order.
2. Find the three most common letters in a sentence (ignore spaces and case).
3. Given two lists, return the items that are in both without duplicates; the items in only one.
4. Group a list of words by their first letter into a dictionary of lists.
5. Remove duplicates from a list while preserving order.
6. Check if two strings are anagrams.
7. Rotate a list left by `k` positions with slicing.
8. Given a list of `(name, score)` tuples, print them sorted by score descending, then name.

<details>
<summary>Solutions</summary>

**1.**
```python
print(" ".join(word[::-1] for word in "python is fun".split()))     # nohtyp si nuf
```

**2.**
```python
from collections import Counter
sentence = "Hello World, hello Python"
letters = [c for c in sentence.lower() if c.isalpha()]
print(Counter(letters).most_common(3))               # [('l', 5), ('o', 4), ('h', 3)]
```

**3.**
```python
a, b = [1, 2, 2, 3, 4], [3, 4, 4, 5]
print(sorted(set(a) & set(b)), sorted(set(a) ^ set(b)))        # [3, 4] [1, 2, 5]
```

**4.**
```python
groups = {}
for word in ["apple", "avocado", "banana", "blueberry", "cherry"]:
    groups.setdefault(word[0], []).append(word)
print(groups)       # {'a': ['apple', 'avocado'], 'b': ['banana', 'blueberry'], 'c': ['cherry']}
```

**5.**
```python
items = [3, 1, 3, 2, 1, 4]
print(list(dict.fromkeys(items)))                    # [3, 1, 2, 4]   (dicts keep insertion order)
```

**6.**
```python
def is_anagram(a, b):
    return sorted(a.replace(" ", "").lower()) == sorted(b.replace(" ", "").lower())
print(is_anagram("Listen", "Silent"), is_anagram("abc", "abd"))     # True False
```

**7.**
```python
def rotate_left(items, k):
    k %= len(items) or 1
    return items[k:] + items[:k]
print(rotate_left([1, 2, 3, 4, 5], 2))               # [3, 4, 5, 1, 2]
```

**8.**
```python
scores = [("ana", 90), ("bo", 85), ("cy", 90)]
for name, score in sorted(scores, key=lambda t: (-t[1], t[0])):
    print(name, score)                               # ana 90 / cy 90 / bo 85
```

</details>

### Files, Modules and Handling Errors

1. Write a function that counts the lines, words and characters of a text file.
2. Read a CSV of products and print the total value (`price x qty`).
3. Save a dictionary to JSON and load it back, comparing equality.
4. Write `safe_int(text, default=0)` returning a default when conversion fails.
5. Write a function that reads a file and returns `None` (with a message) if it does not exist.
6. Create a small module `mathutils.py` with `mean` and `median`, and import it.
7. Explain what `finally` guarantees with an example involving a file or lock.

<details>
<summary>Solutions</summary>

**1.**
```python
def file_stats(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    return len(text.splitlines()), len(text.split()), len(text)
print(file_stats(path))                               # (5, 10, 57)
```

**2.**
```python
products = root / "products.csv"
products.write_text("name,price,qty\npen,50,10\nbook,300,2\n", encoding="utf-8")
with open(products, newline="", encoding="utf-8") as f:
    total = sum(float(r["price"]) * int(r["qty"]) for r in csv.DictReader(f))
print(total)                                          # 1100.0
```

**3.**
```python
data = {"a": [1, 2], "b": {"c": True}}
(root / "x.json").write_text(json.dumps(data), encoding="utf-8")
print(json.loads((root / "x.json").read_text(encoding="utf-8")) == data)      # True
```

**4.**
```python
def safe_int(text, default=0):
    try:
        return int(text)
    except (ValueError, TypeError):
        return default
print(safe_int("12"), safe_int("x"), safe_int(None, -1))        # 12 0 -1
```

**5.**
```python
def read_or_none(file_path):
    try:
        with open(file_path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"{file_path} does not exist")
        return None
print(read_or_none(root / "nope.txt"))
```

**6.**
```python
Path(mod_dir, "mathutils.py").write_text('''
def mean(xs): return sum(xs) / len(xs)
def median(xs):
    s = sorted(xs); mid = len(s) // 2
    return s[mid] if len(s) % 2 else (s[mid - 1] + s[mid]) / 2
''', encoding="utf-8")
mathutils = importlib.import_module("mathutils")
print(mathutils.mean([1, 2, 3, 4]), mathutils.median([1, 2, 3, 4]))      # 2.5 2.5
```

**7.** `finally` runs whether the `try` block succeeds, raises or returns, so cleanup is guaranteed:
```python
log = []
def work():
    try:
        log.append("acquire lock")
        raise RuntimeError("boom")
    finally:
        log.append("release lock")        # runs even though an error was raised
try:
    work()
except RuntimeError:
    pass
print(log)                                # ['acquire lock', 'release lock']
```

</details>

### Debugging and Testing Your Code

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

### Classes and Objects, a First Look

1. Write a `Rectangle` class with `width`, `height`, `area()`, `perimeter()` and a nice `__str__`.
2. Write a `Counter` class with `increment()`, `reset()` and a `value` attribute; create two counters and show they are independent.
3. Extend `BankAccount` with a `transfer(other, amount)` method.
4. Write a `Stack` class (a list inside) with `push`, `pop`, `peek` and `is_empty`.
5. Create a `Library` class that holds a list of book titles and can `add`, `remove` and `search` (case-insensitive substring).

<details>
<summary>Solutions</summary>

**1.**
```python
class Rectangle:
    def __init__(self, width, height):
        self.width, self.height = width, height
    def area(self): return self.width * self.height
    def perimeter(self): return 2 * (self.width + self.height)
    def __str__(self): return f"Rectangle({self.width} x {self.height})"
r = Rectangle(3, 4)
print(r, r.area(), r.perimeter())                  # Rectangle(3 x 4) 12 14
```

**2.**
```python
class Counter:
    def __init__(self): self.value = 0
    def increment(self): self.value += 1
    def reset(self): self.value = 0
a, b = Counter(), Counter()
a.increment(); a.increment(); b.increment()
print(a.value, b.value)                            # 2 1
```

**3.**
```python
class BankAccount2(BankAccount):
    def transfer(self, other, amount):
        self.withdraw(amount)                      # raises if there are insufficient funds
        other.deposit(amount)
a, b = BankAccount2("A", 100), BankAccount2("B", 0)
a.transfer(b, 40)
print(a.balance, b.balance)                        # 60 40
```

**4.**
```python
class Stack:
    def __init__(self): self._items = []
    def push(self, x): self._items.append(x)
    def pop(self): return self._items.pop()
    def peek(self): return self._items[-1]
    def is_empty(self): return not self._items
s = Stack(); s.push(1); s.push(2)
print(s.pop(), s.peek(), s.is_empty())             # 2 1 False
```

**5.**
```python
class Library:
    def __init__(self): self.titles = []
    def add(self, title): self.titles.append(title)
    def remove(self, title): self.titles.remove(title)
    def search(self, text): return [t for t in self.titles if text.lower() in t.lower()]
lib = Library(); lib.add("Python Basics"); lib.add("Advanced Python"); lib.add("Cooking")
print(lib.search("python"))                        # ['Python Basics', 'Advanced Python']
```

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Variables, Types and Operators](01-variables-types-operators.md) · [Making Decisions and Repeating Things](02-control-flow.md) · [Functions](03-functions.md) · [Strings, Lists, Tuples, Dictionaries and Sets](04-strings-lists-dicts-sets.md) · [Files, Modules and Handling Errors](05-files-modules-errors.md) · [Debugging and Testing Your Code](06-debugging-and-testing.md) · [Classes and Objects, a First Look](07-classes-first-look.md)
