# Python Basics 1: Variables, Types and Operators

**Prerequisites:** [setup](../setup/README.md) (Python installed). **You will learn:** how to store values in variables, the basic data types, how to do arithmetic and comparisons, read input, and format output.

## 1. In plain words

A **program** is a list of instructions. Most instructions work with **values** (numbers, text, true/false). A **variable** is a **name** you give to a value so you can use it later, like a label on a jar. Python figures out each value's **type** automatically.

You can try everything below in the Python **REPL** (type `python` in a terminal) or in a `.py` file run with `python file.py`.

## 2. Variables and assignment

```python
age = 20                      # the name `age` now refers to the number 20
name = "Ayesha"               # text values are called strings
height = 1.68                 # decimal numbers are floats
is_student = True             # True/False values are booleans

print(name, age, height, is_student)          # Ayesha 20 1.68 True

age = age + 1                 # variables can be updated: take the old value, add 1, store it back
print(age)                    # 21

x = y = 0                     # several names for one value
a, b = 3, 4                   # assign two at once
a, b = b, a                   # swap in one line
print(a, b)                   # 4 3
```

**Naming rules:** letters, digits and underscores; cannot start with a digit; case-sensitive (`Age` and `age` differ); cannot be a keyword (`if`, `for`, `class`...). **Style:** `snake_case` for variables and functions (`total_price`), `UPPER_CASE` for constants (`MAX_USERS`), descriptive names (`days_until_exam`, not `d`).

## 3. The basic types

| Type | Meaning | Examples | Check with |
|------|---------|----------|-----------|
| `int` | whole numbers (any size) | `42`, `-7`, `10**30` | `type(42)` |
| `float` | decimal numbers (approximate) | `3.14`, `-0.5`, `2e3` (= 2000.0) | `type(3.14)` |
| `str` | text | `"hello"`, `'hi'`, `"""multi-line"""` | `type("a")` |
| `bool` | truth values | `True`, `False` | `type(True)` |
| `NoneType` | "no value" | `None` | `type(None)` |
| `list`, `tuple`, `dict`, `set` | collections | covered in [lesson 4](04-strings-lists-dicts-sets.md) | |

```python
print(type(42), type(3.14), type("hi"), type(True), type(None))
# <class 'int'> <class 'float'> <class 'str'> <class 'bool'> <class 'NoneType'>

print(10 ** 30)                                   # 1000000000000000000000000000000   (ints never overflow in Python)
print(isinstance(5, int), isinstance(5, (int, float)), isinstance(True, int))      # True True True  (bool is a kind of int!)
```

### Converting between types (casting)

```python
print(int("42") + 1, float("3.5"), str(99) + " bottles", int(7.9), int(-7.9), round(7.5), round(8.5))
# 43 3.5 99 bottles 7 -7 8 8    (int() truncates toward zero; round() sends .5 to the even number)
print(bool(0), bool(""), bool([]), bool(None), bool("0"), bool(-1))     # False False False False True True
try:
    int("hello")
except ValueError as error:
    print("ValueError:", error)                    # ValueError: invalid literal for int() with base 10: 'hello'
```

**Truthiness:** `0`, `0.0`, `""`, `[]`, `{}`, `()`, `set()` and `None` count as `False` in conditions; everything else is `True`.

## 4. Operators

### Arithmetic

| Operator | Meaning | Example | Result |
|----------|---------|---------|--------|
| `+` `-` `*` | add, subtract, multiply | `7 * 3` | `21` |
| `/` | true division (always a float) | `7 / 2` | `3.5` |
| `//` | floor division (rounds down) | `7 // 2`, `-7 // 2` | `3`, `-4` |
| `%` | remainder (modulo) | `7 % 3` | `1` |
| `**` | power | `2 ** 10` | `1024` |

```python
print(7 + 3, 7 - 3, 7 * 3, 7 / 2, 7 // 2, 7 % 3, 2 ** 10)       # 10 4 21 3.5 3 1 1024
print(-7 // 2, -7 % 3, divmod(17, 5), abs(-4), 10 / 5)           # -4 2 (3, 2) 4 2.0

# Order of operations: ** first, then * / // %, then + -, parentheses override
print(2 + 3 * 4, (2 + 3) * 4, -2 ** 2, (-2) ** 2)                # 14 20 -4 4

# Shorthand assignment
count = 10
count += 5; count -= 3; count *= 2; count //= 4; count **= 2
print(count)                                                     # 36   (10 -> 15 -> 12 -> 24 -> 6 -> 36)
```

Useful: `%` finds even/odd (`n % 2 == 0`), wraps around (clock: `(hour + 5) % 12`), and checks divisibility (`n % 7 == 0`).

### Comparison and logical operators

Comparisons give a bool: `==` (equal), `!=`, `<`, `>`, `<=`, `>=`. Combine with `and`, `or`, `not` ([logic](../math-for-cs/logic-sets-proofs.md)).

```python
age = 20
print(age >= 18, age == 20, age != 20, 10 < age < 30)             # True True False True   (chained comparison)
has_id, is_member = True, False
print(age >= 18 and has_id, is_member or age > 60, not is_member)  # True False True
print("a" < "b", "apple" < "banana", "Z" < "a", [1, 2] < [1, 3])    # True True True True

# Common bug: = assigns, == compares
x = 5            # assignment
print(x == 5)    # comparison -> True

# `is` checks identity (the same object); use it for None
print(None is None, [] is [], [] == [])                           # True False True
```

### Strings and operators

```python
print("ab" + "cd", "ab" * 3, "x" in "text", "abc" == "abc")      # abcd ababab True True
print("5" + "5", 5 + 5)                                          # 55 10    (strings concatenate, numbers add)
```

## 5. Input and output

```python
# print() writes to the screen; it accepts several values and options
print("Hello", "world", sep=", ", end="!\n")                      # Hello, world!
print("a", "b", "c", sep="-")                                     # a-b-c

# input() reads a line of text from the user and ALWAYS returns a string
# name = input("Your name: ")              # (interactive: skipped in this tested example)
# age = int(input("Your age: "))           # convert when you need a number
```

### Formatting output with f-strings

An **f-string** (`f"..."`) puts values inside text with `{}`, and a **format spec** after `:` controls the look.

```python
name, score, price = "Ayesha", 91.456, 1234567.891
print(f"{name} scored {score}")                  # Ayesha scored 91.456
print(f"{score:.1f}%")                           # 91.5%        one decimal place
print(f"{price:,.2f}")                           # 1,234,567.89 thousands separators
print(f"{42:05d} {42:x} {42:b}")                 # 00042 2a 101010   zero-padded, hex, binary
print(f"|{name:<10}|{name:^10}|{name:>10}|")     # |Ayesha    |  Ayesha  |    Ayesha|
print(f"{2 + 3 = }")                             # 2 + 3 = 5      handy for debugging
print(f"{0.256:.1%}")                            # 25.6%
```

## 6. Comments and style

```python
# A comment starts with # and is ignored by Python. Explain WHY, not WHAT.
tax_rate = 0.17          # Pakistan standard GST (an example of a useful "why" comment)

"""A triple-quoted string at the top of a function or file is a docstring:
documentation that tools and help() can read."""
```

Good habits: descriptive names, 4-space indentation (Python *requires* consistent indentation to define blocks), lines under about 88 characters, one statement per line.

## 7. Putting it together: a small program

```python
# Tip calculator
bill = 2450.00
tip_percent = 15
people = 4

tip = bill * tip_percent / 100
total = bill + tip
per_person = total / people

print(f"Bill: {bill:,.2f}")                      # Bill: 2,450.00
print(f"Tip ({tip_percent}%): {tip:,.2f}")       # Tip (15%): 367.50
print(f"Total: {total:,.2f}")                    # Total: 2,817.50
print(f"Each of {people} pays: {per_person:,.2f}")     # Each of 4 pays: 704.38
```

## 8. Two real-world examples

**Example 1: Unit conversion.** A weather app converts Celsius to Fahrenheit with `f = c * 9 / 5 + 32`. It reads text from a form (always a string), converts it with `float(...)`, calculates, and formats with `f"{f:.1f}"`. Every line uses variables, types, operators and formatting from this lesson.

**Example 2: Splitting a bill or computing a grade.** Divide a total among people with `//` and `%` to handle remainders (`divmod(total_cents, people)` gives each share and the leftover cents). Money is calculated in integer cents to avoid float errors ([why](../computer-basics/binary-and-data-representation.md)).

```python
total_cents, people = 10001, 3
share, remainder = divmod(total_cents, people)
print(share, remainder)          # 3333 2    (two people pay one cent more)
```

## 9. Common mistakes

- Using `=` where `==` is intended (`if x = 5` is a syntax error).
- Forgetting `input()` returns a string (`"5" + "3"` is `"53"`).
- Integer vs float surprises: `7 / 2` is `3.5` but `7 // 2` is `3`.
- Comparing floats with `==` ([floating point](../computer-basics/binary-and-data-representation.md)).
- Indenting inconsistently (mixing tabs and spaces) or forgetting the colon after `if`/`for`/`def`.
- Misspelling a variable name (`NameError: name 'totl' is not defined`).
- Reassigning a built-in name (`list = [1,2]` breaks `list()` later; avoid naming variables `list`, `str`, `sum`, `max`).

## 10. Practice

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

## 11. Check yourself

1. What is a variable in Python?
2. Name five basic types.
3. Difference between `/`, `//` and `%`?
4. What does `input()` return?
5. What is the difference between `=` and `==`?
6. What are the falsy values?

<details>
<summary>Answers</summary>

1. A name that refers to a value (object) in memory.
2. `int`, `float`, `str`, `bool`, `NoneType` (plus `list`, `dict`, `tuple`, `set`).
3. `/` true division (float), `//` floor division, `%` remainder.
4. A string, always.
5. `=` assigns a value to a name; `==` compares two values for equality.
6. `False`, `None`, `0`, `0.0`, `""`, `[]`, `{}`, `()`, `set()`.

</details>

[Back to Python fundamentals](README.md) · Next: [control flow](02-control-flow.md)
