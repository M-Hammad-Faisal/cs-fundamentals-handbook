# Python Basics 3: Functions

**Prerequisites:** [control flow](02-control-flow.md). **You will learn:** how to define and call functions, parameters and return values, default and keyword arguments, scope, docstrings, recursion and how to design small reusable functions.

## 1. In plain words

A **function** is a **named, reusable block of code** that takes inputs (**parameters**), does a job, and gives back an output (the **return value**). Like a recipe: you give it ingredients, it follows the steps, you get a dish. Functions let you **avoid repeating yourself (DRY)**, **name ideas** so code reads like English, and **test pieces separately**.

## 2. Defining and calling functions

```python
def greet(name):                       # `def` starts a function; `name` is a parameter
    return f"Hello, {name}!"           # `return` sends a value back to the caller

message = greet("Ayesha")              # "Ayesha" is an argument; the returned value is stored
print(message)                         # Hello, Ayesha!

def add(a, b):
    return a + b

print(add(2, 3), add("ab", "cd"))      # 5 abcd   (the same code works for any types that support +)

def say_hi():                          # no parameters
    print("hi")                        # prints, but returns None (nothing)

result = say_hi()
print(result)                          # None
```

**Parameters** are the names in the definition; **arguments** are the actual values you pass. **`print` shows something on screen; `return` hands a value back to the code that called the function.** A function without `return` returns `None`.

### Returning several values

```python
def min_max(numbers):
    return min(numbers), max(numbers)      # returns a tuple

low, high = min_max([4, 9, 2, 7])          # unpack the tuple into two names
print(low, high)                           # 2 9
```

## 3. Arguments in detail

```python
def power(base, exponent=2):               # exponent has a DEFAULT value, so it is optional
    return base ** exponent

print(power(5), power(5, 3), power(exponent=4, base=2))     # 25 125 16   (keyword arguments: order does not matter)

def describe(name, *hobbies, **details):    # *args collects extra positional args; **kwargs extra keyword args
    return name, hobbies, details

print(describe("Ayesha", "chess", "coding", city="Lahore", age=21))
# ('Ayesha', ('chess', 'coding'), {'city': 'Lahore', 'age': 21})

values = [2, 10]
print(power(*values))                       # 1024   (* unpacks a list into positional arguments)
options = {"base": 3, "exponent": 3}
print(power(**options))                     # 27     (** unpacks a dict into keyword arguments)
```

Rules: positional arguments first, then keyword arguments; parameters with defaults go **after** those without. Keyword-only (`def f(a, *, b)`) and positional-only (`def f(a, /, b)`) parameters exist for clearer APIs ([modern syntax](../../08-modern-python/modern-syntax/README.md)).

### The mutable default argument trap

```python
def add_item(item, items=[]):               # DANGER: the default list is created ONCE and shared
    items.append(item)
    return items

print(add_item(1), add_item(2))             # [1, 2] [1, 2]    (surprise: the same list)

def add_item_safe(item, items=None):
    if items is None:
        items = []                          # a fresh list for every call
    items.append(item)
    return items

print(add_item_safe(1), add_item_safe(2))   # [1] [2]
```

## 4. Scope: where do names live?

Variables created **inside** a function are **local**: they exist only while it runs. Names outside are **global**.

```python
rate = 0.1                         # global

def apply_discount(price):
    discounted = price * (1 - rate)    # `rate` is read from the global scope; `discounted` is local
    return discounted

print(apply_discount(200))         # 180.0
# print(discounted)                # NameError: discounted is local to the function

def broken_counter():
    # count += 1                   # UnboundLocalError: assigning makes `count` local, but it has no value yet
    pass

total = 0
def add_to_total(x):
    global total                   # allowed, but avoid: global state makes code hard to test
    total += x
add_to_total(5); add_to_total(3)
print(total)                       # 8
```

Prefer **passing values in as parameters and returning results** over using globals. More: [LEGB scope](../computer-basics/memory-stack-heap.md).

## 5. Docstrings and good function design

```python
def bmi(weight_kg, height_m):
    """Return body-mass index.

    Args:
        weight_kg: weight in kilograms (> 0).
        height_m: height in meters (> 0).

    Raises:
        ValueError: if either value is not positive.
    """
    if weight_kg <= 0 or height_m <= 0:
        raise ValueError("weight and height must be positive")
    return weight_kg / height_m ** 2

print(round(bmi(70, 1.75), 1))                     # 22.9
help(bmi)                                          # prints the docstring
try:
    bmi(-1, 1.8)
except ValueError as error:
    print("error:", error)                         # error: weight and height must be positive
```

Guidelines for good functions:

1. **Do one thing** and name it with a verb (`calculate_tax`, `is_valid_email`, `load_users`).
2. **Short** (usually under ~20 lines); extract helpers when it grows.
3. **No surprises:** do not secretly modify arguments or globals; return results.
4. **Validate** inputs at the boundary and raise clear errors.
5. **Pure when possible:** the same inputs give the same output with no side effects: easy to test.
6. Add a **docstring** and optional [type hints](../../08-modern-python/typing-hints/README.md): `def area(r: float) -> float:`.

### Testing a function

```python
def is_palindrome(text):
    cleaned = [c.lower() for c in text if c.isalnum()]
    return cleaned == cleaned[::-1]

assert is_palindrome("racecar")
assert is_palindrome("A man, a plan, a canal: Panama")
assert not is_palindrome("hello")
assert is_palindrome("")                           # edge case: empty string
print("all tests passed")
```

`assert condition` stops the program with an `AssertionError` if the condition is false: the simplest unit test ([testing](../../08-modern-python/exceptions-logging-testing/README.md)).

## 6. Functions are values

In Python a function is an object: you can store it in a variable, pass it to another function, return it.

```python
def apply_twice(func, value):
    return func(func(value))

def double(x):
    return x * 2

print(apply_twice(double, 5))                      # 20
print(apply_twice(lambda x: x + 3, 1))             # 7     (lambda: a tiny anonymous function)

words = ["banana", "fig", "cherry"]
print(sorted(words, key=len), sorted(words, key=lambda w: w[-1]))      # ['fig', 'banana', 'cherry'] ['banana', 'fig', 'cherry']

def make_multiplier(factor):
    def multiply(x):
        return x * factor                          # remembers `factor`: a closure
    return multiply

triple = make_multiplier(3)
print(triple(7))                                   # 21
```

More in [functional tools](../../08-modern-python/generators-functional/README.md).

## 7. Recursion: a function that calls itself

A recursive function solves a problem by solving a **smaller version** of it, with a **base case** that stops the recursion.

```python
def factorial(n):
    if n <= 1:                                     # base case: no more recursion
        return 1
    return n * factorial(n - 1)                    # recursive case: smaller problem

print(factorial(5))                                # 120   (5 * 4 * 3 * 2 * 1)

def sum_digits(n):
    return n if n < 10 else n % 10 + sum_digits(n // 10)
print(sum_digits(2024))                            # 8

def fib(n):                                        # simple but slow for large n (repeats work)
    return n if n < 2 else fib(n - 1) + fib(n - 2)
print([fib(i) for i in range(10)])                 # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

How a call unfolds (the [call stack](../computer-basics/memory-stack-heap.md)):

```text
factorial(3)
 -> 3 * factorial(2)
          -> 2 * factorial(1)
                   -> 1                 (base case)
          -> 2 * 1 = 2
 -> 3 * 2 = 6
```

Every recursive function needs (1) a **base case**, (2) a call on a **smaller** input. Deep recursion hits Python's limit (~1000): use loops for very deep problems. Details: [recursion and backtracking](../../03-algorithms/recursion-backtracking/README.md).

## 8. Two real-world examples

**Example 1: Validation helpers in a signup form.** `is_valid_email(text)`, `is_strong_password(text)`, `is_available(username)` are tiny functions with clear names. The form handler reads like a checklist: `if not is_valid_email(email): errors.append(...)`. Each helper is tested alone and reused on the signup, profile-update and invite pages.

**Example 2: Tax and discount calculation.** `calculate_total(items, tax_rate=0.17, discount=0)` has defaults for the common case and keyword arguments for clarity: `calculate_total(cart, discount=0.1)`. A bug in rounding is fixed in one place and every receipt, invoice and report is corrected at once.

## 9. Common mistakes

- Using `print` instead of `return` (the result cannot be reused).
- Forgetting `return` (the function returns `None`) or placing code after `return` (never runs).
- Mutable default arguments (`def f(x, items=[])`).
- Changing a global from inside a function without `global` (`UnboundLocalError`) or relying on globals everywhere.
- Calling a function without parentheses (`greet` instead of `greet("x")`).
- Recursion without a base case (`RecursionError`).
- Giant functions doing five things; unclear names (`do_stuff`, `process`).

## 10. Practice

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

## 11. Check yourself

1. What is the difference between a parameter and an argument?
2. `print` versus `return`?
3. What does a function return if it has no `return` statement?
4. What are default and keyword arguments?
5. What is a local variable?
6. What two parts must every recursive function have?

<details>
<summary>Answers</summary>

1. A parameter is the name in the function definition; an argument is the value you pass when calling.
2. `print` displays text; `return` gives a value back to the caller to use.
3. `None`.
4. A default gives a parameter a value if the caller omits it; a keyword argument passes a value by parameter name (`f(base=2)`).
5. A variable created inside a function, visible only during that call.
6. A base case that stops recursion, and a recursive call on a smaller input.

</details>

[Back to Python fundamentals](README.md) · Previous: [control flow](02-control-flow.md) · Next: [strings, lists, dicts and sets](04-strings-lists-dicts-sets.md)
