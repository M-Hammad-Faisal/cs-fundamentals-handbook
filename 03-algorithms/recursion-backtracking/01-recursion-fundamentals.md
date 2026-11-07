# Recursion Fundamentals

**Prerequisites:** [Python functions](../../00-foundations/python-fundamentals/README.md), [stack and heap memory](../../00-foundations/computer-basics/memory-stack-heap.md), [stacks](../../02-data-structures/stacks-queues/01-stacks.md). **You will learn:** what recursion is, the two things every recursive function needs (a **base case** and a **smaller subproblem**), how the **call stack** works, how to trace and design recursive functions, the classic examples, the cost of naive recursion (Fibonacci), **memoization**, **tail recursion** (and why Python does not optimize it), and how to convert recursion to loops.

## 1. In plain words

**Recursion** is solving a problem by solving a **smaller copy of the same problem**, until the problem is so small the answer is obvious.

Analogy: Russian nesting dolls. To find the smallest doll, open the doll: if there is another doll inside, "find the smallest doll in *that* one"; if there is none, you are holding it.

Every recursive function needs:

1. **Base case:** an input so small the answer is immediate (stops the recursion).
2. **Recursive case:** reduce the input toward the base case and call yourself.

Forget the base case or fail to shrink the input and you get infinite recursion (`RecursionError` in Python).

## 2. First example: countdown and factorial

```python
def countdown(n):
    if n == 0:                      # base case
        print("liftoff")
        return
    print(n)
    countdown(n - 1)                # smaller subproblem

countdown(3)                        # prints 3, 2, 1, liftoff

def factorial(n):
    if n <= 1:                      # base case: 0! = 1! = 1
        return 1
    return n * factorial(n - 1)     # n! = n * (n-1)!

print(factorial(5), factorial(0), factorial(10))    # 120 1 3628800
```

## 3. How the call stack works

Each call gets its own **stack frame** holding its parameters and local variables. Frames pile up on the way **down** and unwind on the way **up**.

```text
factorial(3)
 └ 3 * factorial(2)
        └ 2 * factorial(1)
               └ returns 1                 base case reached
        └ returns 2 * 1 = 2
 └ returns 3 * 2 = 6
```

Stack (top at right): `[f(3)]` -> `[f(3), f(2)]` -> `[f(3), f(2), f(1)]` -> then frames pop as results flow back up.

You can watch it:

```python
def factorial_traced(n, depth=0):
    indent = "  " * depth
    print(f"{indent}factorial({n})")
    result = 1 if n <= 1 else n * factorial_traced(n - 1, depth + 1)
    print(f"{indent}-> {result}")
    return result

factorial_traced(3)
# factorial(3)
#   factorial(2)
#     factorial(1)
#     -> 1
#   -> 2
# -> 6
```

Python limits the depth (about 1000 frames by default):

```python
import sys
print(sys.getrecursionlimit())                      # 1000   (default)

def depth(n):
    return 0 if n == 0 else 1 + depth(n - 1)

print(depth(500))                                   # 500
try:
    depth(100_000)
except RecursionError as e:
    print("RecursionError:", str(e)[:40])           # RecursionError: maximum recursion depth exceeded
```

## 4. A recipe for writing recursive functions

1. **Define the meaning** in one sentence: "`sum_list(xs)` returns the sum of the list."
2. **Find the base case(s):** the smallest inputs (empty list, `n == 0`).
3. **Assume the function already works** for smaller inputs (the *leap of faith*).
4. **Express the answer** for the current input using those smaller answers.
5. **Check** that each call moves toward a base case.

```python
def sum_list(xs):
    if not xs:                                      # base: the empty list sums to 0
        return 0
    return xs[0] + sum_list(xs[1:])                 # first item + sum of the rest

def reverse(s):
    if len(s) <= 1:
        return s
    return reverse(s[1:]) + s[0]                    # reverse the rest, then add the first character at the end

def is_palindrome(s):
    if len(s) <= 1:
        return True
    return s[0] == s[-1] and is_palindrome(s[1:-1])

def power(base, exp):                               # fast exponentiation: O(log exp) instead of O(exp)
    if exp == 0:
        return 1
    half = power(base, exp // 2)
    return half * half if exp % 2 == 0 else half * half * base

def gcd(a, b):                                      # Euclid's algorithm (about 2300 years old)
    return a if b == 0 else gcd(b, a % b)

print(sum_list([3, 1, 4, 1, 5]), reverse("python"), is_palindrome("racecar"), is_palindrome("abca"))
# 14 nohtyp True False
print(power(2, 10), power(3, 5), gcd(48, 18))       # 1024 243 6
```

Note: slicing like `xs[1:]` copies the list, so `sum_list` is `O(n²)` overall; pass an index instead for efficiency.

```python
def sum_from(xs, i=0):
    return 0 if i == len(xs) else xs[i] + sum_from(xs, i + 1)
print(sum_from(list(range(100))))                   # 4950
```

## 5. Recursion on structures

Data that is defined in terms of itself (nested lists, trees, folders) is naturally recursive.

```python
def flatten(nested):
    result = []
    for item in nested:
        if isinstance(item, list):
            result.extend(flatten(item))            # a nested list is a smaller instance of the same problem
        else:
            result.append(item)
    return result

def max_depth(nested):
    depths = [max_depth(x) for x in nested if isinstance(x, list)]
    return 1 + max(depths, default=0)

print(flatten([1, [2, [3, 4]], 5, [[6]]]))          # [1, 2, 3, 4, 5, 6]
print(max_depth([1, [2, [3, 4]], 5]))               # 3

import os
def total_size(path):
    if os.path.isfile(path):
        return os.path.getsize(path)
    return sum(total_size(os.path.join(path, name)) for name in os.listdir(path))
```

([Trees](../../02-data-structures/trees/01-binary-trees-and-traversals.md) are the classic recursive structure.)

## 6. Two recursive calls: Fibonacci and the explosion

```python
calls = 0
def fib(n):
    global calls
    calls += 1
    return n if n < 2 else fib(n - 1) + fib(n - 2)

print(fib(10), calls)                               # 55 177
calls = 0; fib(20); print(calls)                    # 21891
calls = 0; fib(25); print(calls)                    # 242785
```

The call count grows about **1.6 times for every step of `n`** (`O(2^n)`, more precisely `O(φⁿ)`). The reason: the same subproblems are solved over and over.

```text
                   fib(5)
                /          \
           fib(4)          fib(3)
          /     \          /    \
      fib(3)   fib(2)   fib(2)  fib(1)
      /   \
  fib(2) fib(1)           fib(3) is computed twice, fib(2) three times...
```

## 7. Fix 1: memoization (remember answers)

Store each result the first time; reuse it afterwards.

```python
def fib_memo(n, memo=None):
    memo = {} if memo is None else memo
    if n in memo:
        return memo[n]
    memo[n] = n if n < 2 else fib_memo(n - 1, memo) + fib_memo(n - 2, memo)
    return memo[n]

print(fib_memo(80))                                 # 23416728348467685

from functools import lru_cache
@lru_cache(maxsize=None)
def fib_cached(n):
    return n if n < 2 else fib_cached(n - 1) + fib_cached(n - 2)
print(fib_cached(90), fib_cached.cache_info().misses)     # 2880067194370816120 91
```

Now each `n` is computed once: **`O(n)`** time and space. This is the doorway to [dynamic programming](../dynamic-programming/README.md).

## 8. Fix 2: do it with a loop

```python
def fib_iter(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
print(fib_iter(80), fib_iter(80) == fib_memo(80))   # 23416728348467685 True
```

`O(n)` time, `O(1)` space, no recursion limit.

## 9. Tail recursion and why Python does not optimize it

A call is a **tail call** when it is the last thing the function does (nothing is waiting to be multiplied or added). Some languages (Scheme, Scala for self-calls, Haskell, Rust sometimes) reuse the frame, so deep tail recursion uses constant stack. **Python does not**: a tail-recursive function still hits the limit.

```python
def factorial_tail(n, acc=1):                       # accumulator carries the partial result
    return acc if n <= 1 else factorial_tail(n - 1, acc * n)

print(factorial_tail(5))                            # 120
try:
    factorial_tail(5000)
except RecursionError:
    print("still a RecursionError in Python")       # still a RecursionError in Python
```

The Pythonic fix is a loop:

```python
def factorial_loop(n):
    result = 1
    for k in range(2, n + 1):
        result *= k
    return result
print(len(str(factorial_loop(1000))))               # 2568   (digits in 1000!)
```

## 10. Converting recursion to iteration with an explicit stack

Any recursion can become a loop plus your own stack. This avoids the recursion limit.

```python
def flatten_iterative(nested):
    result, stack = [], [iter(nested)]
    while stack:
        for item in stack[-1]:
            if isinstance(item, list):
                stack.append(iter(item))            # descend: push a new iterator
                break
            result.append(item)
        else:
            stack.pop()                             # this level is exhausted: go back up
    return result

deep = current = []
for _ in range(5000):                               # 5000 levels deep: recursion would fail
    nxt = []
    current.append(nxt)
    current = nxt
current.append(42)
print(flatten_iterative(deep))                      # [42]
```

## 11. Recursion versus iteration: when to use which

| Use recursion when | Use a loop when |
|--------------------|-----------------|
| The data is recursive (trees, nested structures) | A simple count or accumulate suffices |
| Divide and conquer (merge sort, binary search) | Depth could be huge (over about 1000) |
| Backtracking and search ([next lesson](02-backtracking.md)) | Performance and memory are tight |
| The recursive definition is the clearest one | The loop is equally clear |

## 12. Two real-world examples

**Example 1: File system walkers.** `find`, `du`, antivirus scanners and `os.walk` descend into folders recursively: a folder is a list of files and smaller folders.

**Example 2: Parsers and compilers.** Expressions like `(1 + (2 * 3))` are parsed by functions that call each other recursively, mirroring the nested structure of the grammar (the JSON parser inside Python is recursive for nested objects).

## 13. Common mistakes

- Missing or unreachable **base case** (infinite recursion).
- Not making the problem smaller each call.
- Exponential blow-up from overlapping subproblems (fix with memoization).
- Mutable default arguments (`def f(x, memo={})` shares one dict across all calls).
- Deep recursion on big inputs; use iteration or an explicit stack (or `sys.setrecursionlimit` with great care: too high a limit crashes the interpreter).
- Copying with slices in each call (hidden `O(n²)`).

## 14. Practice

1. Write `count_down_up(n)` that prints `n..1` then `1..n` using recursion.
2. Write `sum_digits(n)` recursively: `sum_digits(1234) == 10`.
3. Write `fib_pairs(n)` that returns `(fib(n), fib(n+1))` in `O(n)` without a dict.
4. How many calls does `fib(6)` make? (Count them with the counter.)
5. Write `binary_string(n)` returning the binary digits of `n` recursively.
6. Write `count_paths(rows, cols)` for a grid, moving only right or down. Why is naive recursion slow? Fix it with `lru_cache`.
7. Write `hanoi(n, src, dst, spare)` that returns the list of moves for the Tower of Hanoi.

<details>
<summary>Solutions</summary>

1. ```python
   def count_down_up(n):
       if n == 0: return
       print(n, end=" ")
       count_down_up(n - 1)
       print(n, end=" ")
   count_down_up(3); print()                         # 3 2 1 1 2 3
   ```
2. ```python
   def sum_digits(n):
       return n if n < 10 else n % 10 + sum_digits(n // 10)
   print(sum_digits(1234))                           # 10
   ```
3. ```python
   def fib_pair(n):
       if n == 0: return (0, 1)
       a, b = fib_pair(n - 1)
       return (b, a + b)
   print(fib_pair(10)[0])                            # 55
   ```
4. ```python
   calls = 0; fib(6); print(calls)                   # 25
   ```
5. ```python
   def binary_string(n):
       return str(n) if n < 2 else binary_string(n // 2) + str(n % 2)
   print(binary_string(10), binary_string(0))        # 1010 0
   ```
6. ```python
   from functools import lru_cache
   @lru_cache(maxsize=None)
   def count_paths(rows, cols):
       if rows == 1 or cols == 1:
           return 1
       return count_paths(rows - 1, cols) + count_paths(rows, cols - 1)
   print(count_paths(3, 3), count_paths(18, 18))     # 6 2333606220
   ```
   Naive recursion recomputes the same `(rows, cols)` subproblems exponentially many times.
7. ```python
   def hanoi(n, src, dst, spare):
       if n == 0: return []
       return hanoi(n - 1, src, spare, dst) + [(src, dst)] + hanoi(n - 1, spare, dst, src)
   print(hanoi(2, "A", "C", "B"), len(hanoi(10, "A", "C", "B")))      # [('A', 'B'), ('A', 'C'), ('B', 'C')] 1023
   ```

</details>

## 15. Check yourself

1. What two parts must a recursive function have?
2. What lives on the call stack for each call?
3. Why is naive recursive Fibonacci exponential?
4. What is memoization?
5. Does Python optimize tail recursion?
6. How do you avoid `RecursionError` on deep structures?

<details>
<summary>Answers</summary>

1. A base case and a recursive case that moves toward it.
2. A stack frame: parameters, local variables, and where to return.
3. It recomputes the same subproblems many times; the call tree doubles roughly at each level.
4. Caching results of calls by their arguments so each is computed once.
5. No; use a loop.
6. Use a loop with an explicit stack (or restructure the algorithm).

</details>

[Back to recursion and backtracking](README.md) · Next: [backtracking](02-backtracking.md)
