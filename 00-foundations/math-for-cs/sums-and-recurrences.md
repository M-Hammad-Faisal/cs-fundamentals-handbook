# Sequences, Sums and Recurrences

**Prerequisites:** [exponents and logarithms](exponents-and-logarithms.md), [induction](logic-sets-proofs.md). **You will learn:** the sums that appear when you count loop iterations, the closed forms worth memorizing, what a **recurrence relation** is, and how to solve the recurrences behind recursive algorithms (Fibonacci, binary search, merge sort).

## 1. In plain words

To find how long an algorithm takes you often **add up how much work each iteration does**. If the loops are nested, that is a **sum**. If the algorithm calls itself on smaller inputs, the cost is described by a **recurrence** ("the cost for `n` equals the cost for `n/2` plus a little extra"). This lesson gives you the formulas and the habit of solving both.

## 2. Summation notation

`sum_{i=1}^{n} f(i)` means "add up `f(i)` for `i = 1, 2, ..., n`". It is a `for` loop that accumulates:

```python
n = 5
total = 0
for i in range(1, n + 1):
    total += i * i               # sum of i^2 for i = 1..n
print(total, sum(i * i for i in range(1, n + 1)))           # 55 55
```

## 3. The sums to memorize

| Sum | Closed form | Growth |
|-----|-------------|--------|
| `1 + 2 + ... + n` (arithmetic) | `n(n+1)/2` | `n^2` |
| `1 + 1 + ... + 1` (n times) | `n` | `n` |
| `1^2 + 2^2 + ... + n^2` | `n(n+1)(2n+1)/6` | `n^3` |
| `1 + 2 + 4 + ... + 2^k` (geometric, ratio 2) | `2^(k+1) - 1` | `2^k` |
| `1 + 1/2 + 1/4 + ... ` (ratio 1/2) | approaches `2` | constant |
| `1 + 1/2 + 1/3 + ... + 1/n` (harmonic) | about `ln n` | `log n` |

```python
import math

n = 100
assert sum(range(1, n + 1)) == n * (n + 1) // 2 == 5050                       # Gauss's trick: pair the ends
assert sum(i * i for i in range(1, n + 1)) == n * (n + 1) * (2 * n + 1) // 6
assert sum(2 ** i for i in range(0, 11)) == 2 ** 11 - 1 == 2047               # powers of two add up to just under the next one
print(round(sum(1 / i for i in range(1, 1001)), 3), round(math.log(1000), 3))     # 7.485 6.908   (harmonic ~ ln n)
```

**Gauss's story:** asked to add 1 to 100, young Gauss paired `1 + 100`, `2 + 99`, ... 50 pairs each making 101, so `50 x 101 = 5050`. In general `n/2` pairs of `n + 1`: `n(n+1)/2`.

### Why this matters: counting loop iterations

```python
def count_pairs(n):
    """Nested loop where the inner loop depends on the outer one."""
    steps = 0
    for i in range(n):
        for j in range(i):                  # runs 0, 1, 2, ..., n-1 times
            steps += 1
    return steps

for n in (10, 100, 1000):
    print(n, count_pairs(n), n * (n - 1) // 2)       # equals 0+1+...+(n-1) = n(n-1)/2  -> O(n^2)
# 10 45 45 / 100 4950 4950 / 1000 499500 499500
```

Reading the code: the inner loop does 0, then 1, then 2, ... iterations, so the total is `n(n-1)/2`, which is **O(n^2)**. (Many "double loops" are quadratic even when the inner loop shrinks: dropping the `1/2` factor does not change the growth class.)

```python
def doubling_loop(n):
    steps, i = 0, 1
    while i < n:
        steps += 1
        i *= 2                              # i doubles each time: 1, 2, 4, 8, ...
    return steps

print([doubling_loop(n) for n in (8, 1024, 10 ** 6)])        # [3, 10, 20]   -> log2(n): the loop is O(log n)
```

## 4. Sequences

A **sequence** is an ordered list of numbers `a0, a1, a2, ...`.

- **Arithmetic sequence:** each term adds a constant (`3, 7, 11, 15...` adds 4): `a_n = a_0 + n x d`.
- **Geometric sequence:** each term multiplies by a constant (`3, 6, 12, 24...`): `a_n = a_0 x r^n`.
- **Recursive sequence:** each term is defined from earlier ones (Fibonacci: `F(n) = F(n-1) + F(n-2)`).

```python
def arithmetic(a0, d, n): return [a0 + i * d for i in range(n)]
def geometric(a0, r, n): return [a0 * r ** i for i in range(n)]
print(arithmetic(3, 4, 5), geometric(3, 2, 5))               # [3, 7, 11, 15, 19] [3, 6, 12, 24, 48]

def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
print([fib(i) for i in range(12)])                           # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
```

## 5. Recurrence relations

A **recurrence** defines a quantity in terms of itself for smaller inputs, plus **base cases**. They are the natural way to describe **recursive algorithms**: `T(n)` = "time to solve a problem of size n".

| Recurrence | Meaning | Algorithm | Solution |
|------------|---------|-----------|----------|
| `T(n) = T(n-1) + 1` | do O(1) work, then recurse on `n-1` | recursive countdown, linear recursion | `O(n)` |
| `T(n) = T(n-1) + n` | do O(n) work, then recurse on `n-1` | selection sort | `O(n^2)` |
| `T(n) = T(n/2) + 1` | O(1) work, recurse on half | **binary search** | `O(log n)` |
| `T(n) = T(n/2) + n` | O(n) work, recurse on one half | quickselect (average) | `O(n)` |
| `T(n) = 2 T(n/2) + n` | split into two halves, O(n) to combine | **merge sort**, quicksort (average) | `O(n log n)` |
| `T(n) = 2 T(n-1) + 1` | two recursive calls on `n-1` | Tower of Hanoi | `O(2^n)` |
| `T(n) = T(n-1) + T(n-2)` | two recursive calls | naive Fibonacci | about `O(1.6^n)` |

### Method 1: unroll (expand) the recurrence

Take `T(n) = T(n/2) + 1` (binary search):

```text
T(n) = T(n/2) + 1
     = (T(n/4) + 1) + 1          = T(n/4) + 2
     = T(n/8) + 3
     ...
     = T(n / 2^k) + k           we stop when n / 2^k = 1, i.e. k = log2(n)
     = T(1) + log2(n)           = O(log n)
```

Merge sort `T(n) = 2T(n/2) + n`: at each **level** of the recursion tree the total work is `n` (many small merges add up to n), and there are `log2(n)` levels: total `n log n`.

```text
Level 0:                  [ n ]                         work: n
Level 1:           [ n/2 ]      [ n/2 ]                 work: n/2 + n/2 = n
Level 2:        [n/4] [n/4]  [n/4] [n/4]                work: n
  ...                                                   (log2 n levels) 
Total = n x log2(n)
```

### Verifying a recurrence by counting operations

```python
def count_calls_halving(n):
    """T(n) = T(n/2) + 1: how many calls until n reaches 1?"""
    if n <= 1:
        return 1
    return 1 + count_calls_halving(n // 2)

def merge_sort_comparisons(items):
    """Counts comparisons made by merge sort: roughly n log2 n."""
    if len(items) <= 1:
        return items, 0
    mid = len(items) // 2
    left, c1 = merge_sort_comparisons(items[:mid])
    right, c2 = merge_sort_comparisons(items[mid:])
    merged, i, j, c3 = [], 0, 0, 0
    while i < len(left) and j < len(right):
        c3 += 1
        if left[i] <= right[j]:
            merged.append(left[i]); i += 1
        else:
            merged.append(right[j]); j += 1
    merged += left[i:] + right[j:]
    return merged, c1 + c2 + c3

import math, random
print([count_calls_halving(n) for n in (8, 1024, 10 ** 6)])                      # [4, 11, 20]   (about log2 n + 1)
for n in (1000, 10_000, 100_000):
    data = random.sample(range(n * 10), n)
    _, comparisons = merge_sort_comparisons(data)
    print(n, comparisons, round(n * math.log2(n)))                               # comparisons stay just under n log2 n
```

### Method 2: guess and check by induction

Guess a closed form from small cases, then prove it. Tower of Hanoi: `T(1) = 1`, `T(n) = 2T(n-1) + 1`. Compute: 1, 3, 7, 15, 31 ... guess `T(n) = 2^n - 1`. Check: `2(2^(n-1) - 1) + 1 = 2^n - 1`. ✓ (Moving 64 disks takes `2^64 - 1` moves: about 585 billion years at one move per second.)

```python
def hanoi(n, source="A", target="C", spare="B", moves=None):
    moves = [] if moves is None else moves
    if n == 0:
        return moves
    hanoi(n - 1, source, spare, target, moves)       # move n-1 disks out of the way
    moves.append((source, target))                   # move the biggest disk
    hanoi(n - 1, spare, target, source, moves)       # move the n-1 disks on top of it
    return moves

print([len(hanoi(n)) for n in range(1, 8)], [2 ** n - 1 for n in range(1, 8)])
# [1, 3, 7, 15, 31, 63, 127] [1, 3, 7, 15, 31, 63, 127]
```

### Method 3: the Master Theorem (a shortcut)

For recurrences of the form `T(n) = a T(n/b) + f(n)` (split into `a` subproblems of size `n/b`, extra work `f(n)` to split/combine), compare `f(n)` with `n^(log_b a)`:

| Case | When | Result | Intuition |
|------|------|--------|-----------|
| 1 | `f(n)` grows **slower** than `n^(log_b a)` | `T(n) = O(n^(log_b a))` | the leaves of the recursion tree dominate |
| 2 | `f(n)` grows **the same** | `T(n) = O(n^(log_b a) x log n)` | every level costs the same: multiply by the number of levels |
| 3 | `f(n)` grows **faster** | `T(n) = O(f(n))` | the top (root) work dominates |

Examples: binary search `T(n) = T(n/2) + 1`: a=1, b=2, `n^0 = 1`, f = 1 is the same: Case 2: `O(log n)`. Merge sort `2T(n/2) + n`: a=2, b=2, `n^1 = n`, f = n same: Case 2: `O(n log n)`. Karatsuba multiplication `3T(n/2) + n`: a=3, b=2, `n^1.58`, f smaller: Case 1: `O(n^1.58)`.

## 6. Two real-world examples

**Example 1: Predicting running time before you run it.** A team's report generator has a nested loop where the inner loop runs up to the outer index. The sum `0 + 1 + ... + (n-1) = n(n-1)/2` shows it is quadratic: fine for 1,000 rows (500,000 steps) but 10 billion steps for 100,000 rows. Doing the math first told them to restructure before it hit production.

**Example 2: Why recursion trees explain sorting speed.** Merge sort splits a list in half until single items (about `log2 n` levels) and each level merges `n` items in total. The recurrence `T(n) = 2T(n/2) + n` gives `n log n`. For one million items that is about 20 million steps, versus 10^12 for a quadratic sort: the difference between a second and a day.

## 7. Common mistakes

- Dropping the base case when writing a recurrence.
- Treating `T(n) = 2T(n-1)` (exponential) like `T(n) = 2T(n/2)` (n log n or linear): dividing the input size is what saves you.
- Counting loop iterations as `n x n` when the inner bound shrinks (the exact total is `n(n-1)/2`; same big-O class, different constant).
- Forgetting that doubling or halving in a loop gives `log n`, not `n`.
- Assuming a closed form without checking small cases or proving it.

## 8. Practice

1. Find the exact number of iterations: `for i in range(n): for j in range(i, n):`.
2. Solve by unrolling: `T(n) = T(n-1) + 5`, `T(0) = 1`.
3. What does `T(n) = 2T(n/2) + 1` solve to? (tree traversal)
4. Use the Master Theorem for `T(n) = 4T(n/2) + n`.
5. Count how many times `print` runs: `i = n; while i >= 1: print(i); i //= 3`.
6. Prove by induction that `Fibonacci(n) < 2^n` for `n >= 1`.

<details>
<summary>Solutions</summary>

**1.** `n + (n-1) + ... + 1 = n(n+1)/2`.
```python
def f(n):
    steps = 0
    for i in range(n):
        for j in range(i, n):
            steps += 1
    return steps
print(f(10), 10 * 11 // 2)              # 55 55
```

**2.** `T(n) = T(n-1) + 5 = T(n-2) + 10 = ... = T(0) + 5n = 5n + 1`: `O(n)`.

**3.** a=2, b=2, `n^(log2 2) = n`, f = 1 is smaller: Case 1: `O(n)` (visiting every node once).

**4.** a=4, b=2, `n^2`; f = n grows slower: Case 1: `O(n^2)`.

**5.** The loop runs `floor(log3(n)) + 1` times: `O(log n)`.
```python
def runs(n):
    count, i = 0, n
    while i >= 1:
        count += 1; i //= 3
    return count
print(runs(1), runs(9), runs(10 ** 6), math.floor(math.log(10 ** 6, 3)) + 1)    # 1 3 13 13
```

**6.** Base: F(1) = 1 < 2, F(2) = 1 < 4. Step: assume F(k) < 2^k and F(k-1) < 2^(k-1); then F(k+1) = F(k) + F(k-1) < 2^k + 2^(k-1) < 2^k + 2^k = 2^(k+1). ✓

</details>

## 9. Check yourself

1. What is `1 + 2 + ... + n`, and what Big-O does it give?
2. What does a loop that doubles its counter cost?
3. What does `T(n) = T(n/2) + 1` describe, and what is its solution?
4. Why is merge sort `O(n log n)` in terms of its recursion tree?
5. What are the three cases of the Master Theorem in words?

<details>
<summary>Answers</summary>

1. `n(n+1)/2`, which is `O(n^2)`.
2. `O(log n)` iterations.
3. Binary search: constant work plus a recursive call on half the input; `O(log n)`.
4. There are about log2(n) levels, and the total work per level is n (all the merges at that level), so n log n.
5. If the leaves dominate: `n^(log_b a)`; if every level costs the same: `n^(log_b a) x log n`; if the root dominates: `f(n)`.

</details>

[Back to math](README.md) · Previous: [counting and probability](counting-and-probability.md)
