# Analyzing Loops and Recursion Step by Step

**Prerequisites:** [Big-O, Omega and Theta](03-big-o-omega-theta.md). **You will learn:** a repeatable method for finding the time complexity of any code: single loops, nested loops, loops with changing bounds, loops that halve or double, sequential blocks, functions that call other functions, and recursion (with recurrences and recursion trees). Twenty worked examples, each verified by instrumented code.

## 1. In plain words

Analyzing an algorithm is detective work with a simple method: **find the part that runs the most times and count how many times it runs as a function of the input size**. This lesson gives you the patterns; with practice you will recognize them at a glance.

## 2. The method (use it every time)

1. **Define `n`** (or `n` and `m`): what is the input size? (length of a list, the number itself, number of rows...)
2. **Find the basic operation** that dominates (usually the innermost statement or a comparison).
3. **Count how often it runs** in terms of `n`: loops multiply, sequential blocks add, recursion gives a recurrence.
4. **Simplify**: drop constants and lower-order terms ([rules](03-big-o-omega-theta.md)).
5. **State the case** (worst case unless told otherwise) and **check** with a counter or the doubling test.

We use a tiny helper to count operations and confirm each analysis:

```python
import math

def count(fn, *args):
    """Run fn(counter, *args); the function calls counter.tick() once per basic operation. Returns the total."""
    class Counter:
        ops = 0
        def tick(self, k=1): self.ops += k
    c = Counter()
    fn(c, *args)
    return c.ops
```

## 3. Single loops

### Example 1: one loop over the input: O(n)

```python
def loop_n(c, n):
    for i in range(n):
        c.tick()                         # the basic operation runs n times

print([count(loop_n, n) for n in (10, 100, 1000)])            # [10, 100, 1000]   -> exactly n: O(n)
```

### Example 2: a loop that does a fixed amount of work per iteration

```python
def loop_const(c, n):
    for i in range(n):
        c.tick(5)                        # 5 operations per iteration

print(count(loop_const, 100))            # 500   -> 5n: still O(n) (constants dropped)
```

### Example 3: a loop with a fixed number of iterations: O(1)

```python
def loop_fixed(c, n):
    for i in range(1000):                # does NOT depend on n
        c.tick()

print([count(loop_fixed, n) for n in (10, 10**6)])            # [1000, 1000]  -> O(1) (a large constant is still a constant)
```

### Example 4: stepping by 2 or by k

```python
def loop_step(c, n):
    for i in range(0, n, 2):             # n/2 iterations
        c.tick()

print(count(loop_step, 1000))            # 500   -> n/2: O(n)
```

### Example 5: the loop counter doubles (or halves): O(log n)

```python
def loop_double(c, n):
    i = 1
    while i < n:
        c.tick()
        i *= 2                           # 1, 2, 4, 8, ... reaches n after log2(n) steps

def loop_halve(c, n):
    while n > 1:
        c.tick()
        n //= 2

print([count(loop_double, n) for n in (8, 1024, 10**6)], [count(loop_halve, n) for n in (8, 1024, 10**6)])
# [3, 10, 20] [3, 10, 19]     -> about log2(n): O(log n)
```

### Example 6: the counter grows by squaring: O(log log n)

```python
def loop_square(c, n):
    i = 2
    while i < n:
        c.tick()
        i = i * i                        # 2, 4, 16, 256, 65536, ...

print([count(loop_square, n) for n in (10, 10**3, 10**9, 10**18)])      # [2, 4, 5, 6]   -> O(log log n): extremely slow growth
```

## 4. Nested loops

### Example 7: independent nested loops multiply: O(n²) or O(n · m)

```python
def nested_same(c, n):
    for i in range(n):
        for j in range(n):
            c.tick()

def nested_different(c, n, m):
    for i in range(n):
        for j in range(m):
            c.tick()

print(count(nested_same, 50), 50 * 50)                         # 2500 2500   -> n²: O(n²)
print(count(nested_different, 30, 7), 30 * 7)                  # 210 210     -> n·m: O(n · m)
```

### Example 8: the inner bound depends on the outer variable: still O(n²)

```python
def triangle(c, n):
    for i in range(n):
        for j in range(i):               # 0, 1, 2, ..., n-1 iterations
            c.tick()

print(count(triangle, 100), 100 * 99 // 2)                     # 4950 4950   -> n(n-1)/2: O(n²) (the 1/2 is a constant)
```

The sum `0 + 1 + ... + (n-1)` was derived in [sums and recurrences](../00-foundations/math-for-cs/sums-and-recurrences.md).

### Example 9: outer loop linear, inner loop logarithmic: O(n log n)

```python
def n_log_n(c, n):
    for i in range(n):
        j = 1
        while j < n:                     # log n iterations
            c.tick()
            j *= 2

print(count(n_log_n, 1024), 1024 * 10)                         # 10240 10240   -> n log n
```

### Example 10: two nested loops where the inner loop does not always run

```python
def conditional_inner(c, n):
    for i in range(n):
        if i % 2 == 0:                   # only half the outer iterations run the inner loop
            for j in range(n):
                c.tick()

print(count(conditional_inner, 100), 50 * 100)                 # 5000 5000   -> n²/2: still O(n²)
```

A common trap: **a loop inside a loop is not always `n²`**. Count what actually runs:

```python
def total_work_is_linear(c, n):
    # Outer loop runs n times, but the inner loop RESETS only when needed:
    j = 0
    for i in range(n):
        while j < n and j <= i:          # j only moves forward overall: total inner steps <= n
            c.tick()
            j += 1

print(count(total_work_is_linear, 1000))                       # 1000   -> O(n), not O(n²) (two pointers / sliding window pattern)
```

## 5. Sequential blocks and function calls

### Example 11: add the blocks, keep the largest

```python
def sequential(c, n):
    for i in range(n):                   # O(n)
        c.tick()
    for i in range(n):                   # O(n²)
        for j in range(n):
            c.tick()
    c.tick(100)                          # O(1)

print(count(sequential, 100), 100 + 100 * 100 + 100)           # 10200 10200   -> n² + n + 100: O(n²)
```

### Example 12: count what called functions cost

```python
def helper_linear(c, items):             # O(len(items))
    for x in items:
        c.tick()

def caller(c, n):
    for i in range(n):                   # n iterations ...
        helper_linear(c, range(n))       # ... each calling an O(n) helper: O(n²) total

print(count(caller, 50), 50 * 50)                              # 2500 2500
```

Hidden costs: calling `sorted(x)` is `O(n log n)`, `x in my_list` is `O(n)`, `my_list.insert(0, v)` is `O(n)`, slicing `a[i:j]` is `O(j - i)`, `s + t` on strings is `O(len(s) + len(t))` ([cheat sheet](07-python-operations-cheat-sheet.md)). **A loop with a hidden `O(n)` call inside is quadratic.**

```python
def slow_unique(items):                  # looks like one loop, is O(n²): `in` on a list scans it
    seen = []
    for x in items:
        if x not in seen:
            seen.append(x)
    return seen

def fast_unique(items):                  # O(n): `in` on a set is O(1) average
    seen, out = set(), []
    for x in items:
        if x not in seen:
            seen.add(x); out.append(x)
    return out

import random
data = [random.randrange(2000) for _ in range(20_000)]
assert slow_unique(data) == fast_unique(data)
```

### Example 13: two inputs

```python
def two_inputs(c, a, b):
    for x in a:                          # |a| iterations
        c.tick()
    for y in b:                          # |b| iterations
        c.tick()

def common_items_quadratic(c, a, b):
    for x in a:
        for y in b:
            c.tick()

print(count(two_inputs, range(30), range(20)), count(common_items_quadratic, range(30), range(20)))   # 50 600
# O(n + m) versus O(n · m)
```

## 6. Recursion

For a recursive function, write a **recurrence** `T(n)` (the cost for size `n`) from the code, then solve it ([methods](../00-foundations/math-for-cs/sums-and-recurrences.md)).

### Example 14: linear recursion `T(n) = T(n-1) + 1`: O(n)

```python
def countdown(c, n):
    if n == 0:
        return
    c.tick()
    countdown(c, n - 1)                  # one call on size n-1, O(1) extra work

print(count(countdown, 500))             # 500 -> O(n)  (and O(n) stack depth!)
```

### Example 15: `T(n) = T(n/2) + 1`: O(log n) (binary search)

```python
def binary_search_rec(c, items, target, lo, hi):
    if lo > hi:
        return -1
    c.tick()
    mid = (lo + hi) // 2
    if items[mid] == target:
        return mid
    if items[mid] < target:
        return binary_search_rec(c, items, target, mid + 1, hi)
    return binary_search_rec(c, items, target, lo, mid - 1)

data = list(range(1_000_000))
print(count(binary_search_rec, data, -1, 0, len(data) - 1))           # 19 -> about log2(n) for a million items
```

### Example 16: `T(n) = 2T(n/2) + n`: O(n log n) (merge sort)

```python
def merge_sort(c, items):
    if len(items) <= 1:
        return items
    mid = len(items) // 2
    left, right = merge_sort(c, items[:mid]), merge_sort(c, items[mid:])      # two half-size subproblems
    merged, i, j = [], 0, 0
    while i < len(left) and j < len(right):                                    # merging costs about n
        c.tick()
        if left[i] <= right[j]:
            merged.append(left[i]); i += 1
        else:
            merged.append(right[j]); j += 1
    return merged + left[i:] + right[j:]

for n in (1000, 10_000):
    ops = count(merge_sort, random.sample(range(n * 10), n))
    print(n, ops, round(n * math.log2(n)))                                     # comparisons stay just under n log2 n
```

Recursion-tree view: `log2(n)` levels, each costing about `n`:

```text
level 0:  n                       -> work n
level 1:  n/2   n/2               -> work n
level 2:  n/4 n/4 n/4 n/4         -> work n
 ...       (log2 n levels)        => total n log n
```

### Example 17: `T(n) = T(n-1) + n`: O(n²) (selection-sort style)

```python
def sum_pass(c, n):
    if n == 0:
        return
    for i in range(n):                   # O(n) work ...
        c.tick()
    sum_pass(c, n - 1)                   # ... then recurse on n-1

print(count(sum_pass, 100), 100 * 101 // 2)                    # 5050 5050 -> n(n+1)/2: O(n²)
```

### Example 18: two recursive calls on `n-1`: `T(n) = 2T(n-1) + 1` = O(2ⁿ)

```python
def all_subsets_count(c, n):
    if n == 0:
        c.tick()
        return
    all_subsets_count(c, n - 1)          # include the item
    all_subsets_count(c, n - 1)          # exclude the item

print([count(all_subsets_count, n) for n in (5, 10, 15)])      # [32, 1024, 32768] -> 2^n: exponential
```

### Example 19: naive Fibonacci: `T(n) = T(n-1) + T(n-2) + 1` is about O(1.6ⁿ)

```python
def fib_calls(c, n):
    c.tick()
    if n < 2:
        return n
    return fib_calls(c, n - 1) + fib_calls(c, n - 2)

print([count(fib_calls, n) for n in (10, 15, 20, 25)])         # [177, 1973, 21891, 242785]   (each +5 multiplies by about 11)
```

With **memoization** the same recursion is `O(n)`: the work is cached ([dynamic programming](../03-algorithms/dynamic-programming/README.md)).

```python
def fib_memo_calls(n):
    cache, calls = {}, [0]
    def fib(k):
        calls[0] += 1
        if k < 2: return k
        if k not in cache:
            cache[k] = fib(k - 1) + fib(k - 2)
        return cache[k]
    fib(n)
    return calls[0]
print([fib_memo_calls(n) for n in (10, 20, 30, 40)])           # [19, 39, 59, 79] -> about 2n: O(n)
```

### Example 20: Euclid's algorithm: O(log min(a, b))

```python
def gcd_steps(c, a, b):
    while b:
        c.tick()
        a, b = b, a % b

print(count(gcd_steps, 10 ** 18 + 1, 10 ** 12 + 7), count(gcd_steps, 1071, 462))      # 10 3   (a handful of steps even for 10^18-sized numbers)
```

## 7. A cheat sheet of patterns

| Code pattern | Complexity |
|--------------|-----------|
| Statements with no loops | `O(1)` |
| `for` over `n` items | `O(n)` |
| Loop where the counter doubles/halves | `O(log n)` |
| Two nested loops over `n` | `O(n²)` |
| Triangular nested loops (`j < i`) | `O(n²)` |
| Loop of `n` with a halving inner loop | `O(n log n)` |
| Loops over different inputs | `O(n + m)` or `O(n · m)` |
| Two pointers moving only forward | `O(n)` |
| Loop with a hidden `O(n)` call (`in list`, slice, `insert(0)`) | `O(n²)` |
| `T(n) = T(n-1) + 1` | `O(n)` |
| `T(n) = T(n/2) + 1` | `O(log n)` |
| `T(n) = 2T(n/2) + n` | `O(n log n)` |
| `T(n) = T(n-1) + n` | `O(n²)` |
| `T(n) = 2T(n-1) + 1` | `O(2ⁿ)` |

## 8. Two real-world examples

**Example 1: Auditing a slow endpoint.** A "recommendations" function takes 8 s with 20,000 products. The code has a loop over products; inside it, `if related not in already_listed` (a list) and `sorted(candidates)`. Counting: loop `n` times x (`in` on a list `O(n)`) = `O(n²)`, plus sorting inside the loop `O(n log n)` x `n` = `O(n² log n)`. Moving `sorted` outside the loop and replacing the list with a set makes it `O(n log n)` overall: 8 s becomes about 60 ms.

**Example 2: Predicting recursion depth.** A recursive directory walk is `T(n) = T(n-1) + 1` on a very deep tree (a chain of 5,000 nested folders). The analysis shows `O(n)` stack depth, which exceeds Python's limit of about 1,000 frames; the team rewrites it with an explicit stack (iterative DFS). Complexity analysis covers space as well as time ([space complexity](05-space-complexity.md)).

## 9. Common mistakes

- Multiplying loops that are *sequential* (they add), or adding loops that are *nested* (they multiply).
- Assuming "nested loop means `n²`" without checking the bounds (two pointers can make it `O(n)`).
- Forgetting the cost of operations *inside* the loop (slicing, `in` on a list, string concatenation, `sorted`).
- Treating a recursive function with two calls as `O(n)` (two calls on `n-1` is exponential; two calls on `n/2` is linear or `n log n` depending on the extra work).
- Using `n` for everything when the input has several sizes (`rows x columns`, `|V| + |E|`).
- Ignoring input that is a number (`for i in range(n)` is `O(n)` in the *value* `n`, but `O(2^bits)` in the input *size*: relevant for number-theory algorithms).

## 10. Practice

Find the time complexity of each (assume `n = len(items)`), then verify with the counter.

1. ```python
   for i in range(n):
       for j in range(0, n, 3): ...
   ```
2. ```python
   i = n
   while i > 0:
       for j in range(n): ...
       i //= 2
   ```
3. ```python
   for i in range(n):
       for j in range(i, n): ...
   ```
4. ```python
   def f(n): return 1 if n <= 1 else f(n // 2) + f(n // 2) + n
   ```
5. ```python
   def g(n): return 0 if n == 0 else g(n - 1) + g(n - 1)
   ```
6. ```python no-run
   total = 0
   for x in items:
       total += sum(items)        # sum is O(n)
   ```
7. A function takes two lists `a` (size `n`) and `b` (size `m`), sorts both, then merges them in one pass. What is the cost?

<details>
<summary>Solutions</summary>

**1.** `n x n/3` = `O(n²)`.

**2.** `log n` outer iterations x `n` inner = `O(n log n)`.
```python
def p2(c, n):
    i = n
    while i > 0:
        for j in range(n): c.tick()
        i //= 2
print(count(p2, 1024), 1024 * 11)         # 11264 11264
```

**3.** `n + (n-1) + ... + 1 = n(n+1)/2`: `O(n²)`.

**4.** `T(n) = 2T(n/2) + n`: `O(n log n)` (same as merge sort).

**5.** `T(n) = 2T(n-1) + 1`: `O(2ⁿ)`.

**6.** `n` iterations x `O(n)`: `O(n²)` (the `sum` is hidden work).

**7.** Sorting costs `O(n log n + m log m)`; merging costs `O(n + m)`; total `O(n log n + m log m)`.

</details>

## 11. Check yourself

1. What is the first step of analyzing code?
2. What is the complexity of a loop whose counter doubles each time?
3. How does a nested loop with a triangular inner bound count?
4. Why is `T(n) = 2T(n/2) + n` equal to `O(n log n)`?
5. Why is the naive recursive Fibonacci exponential, and how does memoization fix it?
6. Why can a single loop be quadratic?

<details>
<summary>Answers</summary>

1. Define the input size(s) and find the dominant operation.
2. `O(log n)`.
3. `0 + 1 + ... + (n-1) = n(n-1)/2`, which is `O(n²)`.
4. There are about `log2 n` levels in the recursion tree and each level does about `n` work.
5. It recomputes the same subproblems exponentially many times; memoization stores each result so each subproblem is solved once, giving `O(n)`.
6. If the body contains a hidden `O(n)` operation (like `x in a_list` or slicing), the total is `n x n`.

</details>

[Back to complexity](README.md) · Previous: [Big-O, Omega and Theta](03-big-o-omega-theta.md) · Next: [space complexity](05-space-complexity.md)
