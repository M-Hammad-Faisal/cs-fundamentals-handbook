# Python Basics 2: Making Decisions and Repeating Things

**Prerequisites:** [variables, types and operators](01-variables-types-operators.md). **You will learn:** `if/elif/else`, `for` and `while` loops, `break`/`continue`, `range`, nested loops, and the patterns (counting, accumulating, searching) that every program uses.

## 1. In plain words

Programs need to **choose** (do this *if* that is true) and **repeat** (do this for every item, or until something happens). These two ideas, **conditionals** and **loops**, together with sequence (one step after another), are all of programming. Python marks blocks of code with a **colon** and **indentation** (4 spaces).

## 2. Conditionals: `if`, `elif`, `else`

```python
score = 72

if score >= 90:
    grade = "A"
elif score >= 80:                  # checked only if the earlier conditions were false
    grade = "B"
elif score >= 70:
    grade = "C"
else:                              # runs if nothing above matched
    grade = "F"
print(grade)                       # C
```

Rules: conditions are tested **top to bottom** and **only the first true branch runs**; `elif` and `else` are optional; indentation defines what belongs to each branch.

```python
age, has_ticket = 17, True

if age >= 18 and has_ticket:
    print("enter")
elif has_ticket:
    print("ticket valid but too young")        # ticket valid but too young
else:
    print("no ticket")

# One-line conditional expression ("ternary")
status = "adult" if age >= 18 else "minor"
print(status)                                  # minor

# Check membership and emptiness idiomatically
fruits = ["apple", "pear"]
if "pear" in fruits:
    print("have pear")                         # have pear
if not fruits:                                 # empty list is falsy
    print("nothing")
```

### `match` (Python 3.10+) for many cases

```python
def describe(command):
    match command.split():
        case ["go", direction]:
            return f"going {direction}"
        case ["quit"]:
            return "bye"
        case _:
            return "unknown command"
print(describe("go north"), describe("quit"), describe("dance"))      # going north bye unknown command
```

More in [modern syntax](../../08-modern-python/modern-syntax/README.md).

## 3. `for` loops: repeat for each item

```python
for letter in "abc":                 # iterate over a string
    print(letter, end=" ")           # a b c
print()

for fruit in ["apple", "pear"]:      # iterate over a list
    print(fruit.upper())             # APPLE / PEAR

for i in range(5):                   # range(5) is 0, 1, 2, 3, 4
    print(i, end=" ")                # 0 1 2 3 4
print()

print(list(range(2, 10, 3)), list(range(5, 0, -1)))     # [2, 5, 8] [5, 4, 3, 2, 1]    range(start, stop, step): stop is excluded
```

Useful helpers:

```python
names = ["ana", "bo", "cy"]
for index, name in enumerate(names, start=1):          # index and item together
    print(index, name)                                  # 1 ana / 2 bo / 3 cy

ages = [30, 25, 41]
for name, age in zip(names, ages):                     # walk two lists in parallel
    print(f"{name} is {age}")

for key, value in {"a": 1, "b": 2}.items():            # dictionary keys and values
    print(key, value)
```

## 4. `while` loops: repeat until a condition changes

```python
count = 3
while count > 0:
    print(count, end=" ")            # 3 2 1
    count -= 1                       # change something, or the loop never ends!
print("liftoff")

# Loop until the user gives valid input (simulated with a list of attempts)
attempts = iter(["abc", "-5", "42"])
while True:
    text = next(attempts)
    if text.lstrip("-").isdigit() and int(text) > 0:
        value = int(text)
        break                        # leave the loop immediately
    print(f"{text!r} is not a positive number, try again")
print("got", value)                  # got 42
```

**Choose:** `for` when you know what to loop over (a collection or a count); `while` when you repeat **until something happens** (user input, convergence, a game ending). Beware **infinite loops** (forgetting to update the condition): stop with `Ctrl+C`.

### `break`, `continue` and `else`

```python
for n in range(10):
    if n % 2 == 0:
        continue                     # skip the rest of this iteration
    if n > 7:
        break                        # leave the loop entirely
    print(n, end=" ")                # 1 3 5 7
print()

# for/else: the else block runs only if the loop finished WITHOUT break
for n in range(2, 10):
    if n * n == 49:
        print("found", n)
        break
else:
    print("no square root of 49 below 10")      # (found 7 is printed, so this else is skipped)
```

## 5. Nested loops

A loop inside a loop: the inner loop runs completely for every step of the outer loop. Total iterations = outer x inner.

```python
for row in range(1, 4):
    for col in range(1, 4):
        print(row * col, end="\t")
    print()
# 1  2  3
# 2  4  6
# 3  6  9

# A triangle of stars
for i in range(1, 5):
    print("*" * i)
# * / ** / *** / ****
```

Nested loops over `n` items cost `n x n` steps: fine for 1,000 items (a million steps), not for a million ([Big-O](../../01-complexity/big-o/README.md)).

## 6. The patterns every program uses

### Counting and accumulating

```python
numbers = [4, 8, 15, 16, 23, 42]

total = 0
for n in numbers:
    total += n                       # accumulate
print(total, total / len(numbers))   # 108 18.0

evens = 0
for n in numbers:
    if n % 2 == 0:
        evens += 1                   # count the items that match
print(evens)                         # 4
```

### Finding the maximum and searching

```python
best = numbers[0]
for n in numbers[1:]:
    if n > best:
        best = n
print(best, max(numbers))            # 42 42

target, position = 16, -1
for index, n in enumerate(numbers):
    if n == target:
        position = index
        break
print(position)                      # 3
```

### Building a new list (filter and transform)

```python
squares_of_evens = []
for n in numbers:
    if n % 2 == 0:
        squares_of_evens.append(n * n)
print(squares_of_evens)                                 # [16, 64, 256, 1764]

# The same with a list comprehension (shorter; see lesson 4 and the generators chapter)
print([n * n for n in numbers if n % 2 == 0])           # [16, 64, 256, 1764]
```

### Classic small programs

```python
def is_prime(n):
    if n < 2:
        return False
    for d in range(2, int(n ** 0.5) + 1):         # only test up to the square root
        if n % d == 0:
            return False
    return True

print([n for n in range(2, 30) if is_prime(n)])            # [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]

def fizzbuzz(n):
    out = []
    for i in range(1, n + 1):
        if i % 15 == 0: out.append("FizzBuzz")
        elif i % 3 == 0: out.append("Fizz")
        elif i % 5 == 0: out.append("Buzz")
        else: out.append(str(i))
    return out
print(fizzbuzz(15))
# ['1', '2', 'Fizz', '4', 'Buzz', 'Fizz', '7', '8', 'Fizz', 'Buzz', '11', 'Fizz', '13', '14', 'FizzBuzz']

def collatz_steps(n):
    steps = 0
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
    return steps
print(collatz_steps(27))                                    # 111
```

## 7. Two real-world examples

**Example 1: Processing orders.** An online shop loops over every order (`for order in orders`), checks conditions (`if order.paid and not order.shipped`), accumulates totals, and counts late deliveries. Almost every business report is a loop with an `if` and an accumulator.

**Example 2: A retry loop.** A script that calls an unreliable service uses `while attempts < 3:` try the call, `break` on success, otherwise wait and try again. Loop-until-success is a pattern in networking, file locking and user input validation.

```python
import random
random.seed(3)
attempts, succeeded = 0, False
while attempts < 5 and not succeeded:
    attempts += 1
    succeeded = random.random() < 0.5          # pretend this is a network call
print(attempts, succeeded)
```

## 8. Common mistakes

- Missing colon or wrong indentation (`IndentationError`).
- Off-by-one errors: `range(n)` goes `0..n-1`; `range(1, n + 1)` goes `1..n`.
- Infinite `while` loops (forgot to change the loop variable).
- Changing a list while looping over it (build a new list or iterate over a copy).
- Using `=` in a condition; forgetting that `elif` is only reached if earlier tests were false.
- Writing `if x == 1 or 2:` (always true) instead of `if x == 1 or x == 2:` or `if x in (1, 2):`.
- Modifying the loop variable inside a `for` loop expecting to change the iteration.

## 9. Practice

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

## 10. Check yourself

1. How does Python know which lines belong to an `if` block?
2. What does `range(2, 10, 3)` produce?
3. When use `for` and when `while`?
4. What do `break` and `continue` do?
5. How many times does the body of two nested loops over 10 and 20 items run?
6. What is the accumulator pattern?

<details>
<summary>Answers</summary>

1. By the colon and the indentation (4 spaces) of the following lines.
2. `2, 5, 8`.
3. `for` to iterate over a collection or a known count; `while` to repeat until a condition changes.
4. `break` exits the loop; `continue` skips to the next iteration.
5. 10 x 20 = 200.
6. Start with an initial value (0, `[]`, ...) and update it in each iteration to build a total, count or collection.

</details>

[Back to Python fundamentals](README.md) · Previous: [variables, types and operators](01-variables-types-operators.md) · Next: [functions](03-functions.md)
