# Divide and Conquer

**Prerequisites:** [recursion fundamentals](../recursion-backtracking/01-recursion-fundamentals.md), [merge sort and quicksort](../sorting/02-merge-sort-and-quicksort.md), [sums and recurrences](../../00-foundations/math-for-cs/sums-and-recurrences.md), [analyzing recursion](../../01-complexity/04-analyzing-loops-and-recursion.md). **You will learn:** the **divide, conquer, combine** pattern; how to turn an algorithm into a **recurrence** and solve it with the **Master theorem**; four worked examples (**maximum subarray, Karatsuba multiplication, closest pair of points, majority element**); how it differs from **dynamic programming**; and when it parallelizes well. Every algorithm is checked against a simple brute-force version on random input.

## 1. In plain words

To sort a huge pile of exam papers, split the pile in two, give each half to a helper, and merge the two sorted results. Each helper does the same thing with a smaller pile, until a pile has one paper (already sorted). That is **divide and conquer**:

1. **Divide** the problem into smaller copies of the *same* problem.
2. **Conquer** each part recursively (a tiny part is solved directly: the **base case**).
3. **Combine** the partial answers into the answer for the whole.

You already met it in [merge sort](../sorting/02-merge-sort-and-quicksort.md) (easy divide, hard combine), [quicksort](../sorting/02-merge-sort-and-quicksort.md) (hard divide, free combine), [binary search](../searching/01-linear-and-binary-search.md) (only one half is needed) and [fast exponentiation](../number-theory/01-number-theory-for-programmers.md) (`a^n` from `a^(n/2)`).

```text
            problem of size n
           /                 \
  half of size n/2      half of size n/2        <- divide
        |                     |
     solve                 solve                <- conquer (recursion)
           \                 /
            combine two answers                 <- combine
```

## 2. Recurrences and the Master theorem

The cost of a divide-and-conquer algorithm is a **recurrence**: split into `a` subproblems of size `n/b`, plus `f(n)` work to divide and combine.

```text
T(n) = a * T(n / b) + f(n)
```

Examples: merge sort `T(n) = 2T(n/2) + n`; binary search `T(n) = T(n/2) + 1`; naive multiplication of big numbers `T(n) = 4T(n/2) + n`.

Picture the **recursion tree**: level `k` has `a^k` subproblems each of size `n / b^k`. Compare the work at the top (the combine step) with the work at the bottom (the many tiny leaves):

- Leaves dominate when `a` is large (lots of subproblems).
- The top dominates when `f(n)` is large.
- They balance when `f(n) = n^(log_b a)`; then every level costs about the same and you pay a `log n` factor for the number of levels.

**Master theorem** for `f(n) = n^d` (a polynomial), with `c = log_b a`:

| Case | Condition | Result | Example |
|------|-----------|--------|---------|
| Leaves win | `d < c` | `Θ(n^c)` | `T(n) = 4T(n/2) + n` gives `Θ(n²)`; Karatsuba `3T(n/2) + n` gives `Θ(n^1.585)` |
| Balanced | `d = c` | `Θ(n^d log n)` | merge sort `2T(n/2) + n` gives `Θ(n log n)` |
| Top wins | `d > c` | `Θ(n^d)` | `T(n) = 2T(n/2) + n²` gives `Θ(n²)` |

```python
import math

def master(a, b, d):
    """Solve T(n) = a*T(n/b) + n^d and describe the growth."""
    c = math.log(a, b)
    if abs(d - c) < 1e-9:
        return f"Theta(n^{d:g} log n)"
    if d < c:
        return f"Theta(n^{c:.3f})"
    return f"Theta(n^{d:g})"

print(master(2, 2, 1))        # Theta(n^1 log n)     merge sort
print(master(1, 2, 0))        # Theta(n^0 log n)     binary search: Theta(log n)
print(master(4, 2, 1))        # Theta(n^2.000)       schoolbook big-number multiplication
print(master(3, 2, 1))        # Theta(n^1.585)       Karatsuba
print(master(2, 2, 2))        # Theta(n^2)           the top level dominates
print(master(7, 2, 2))        # Theta(n^2.807)       Strassen matrix multiplication
```

Do not trust the formula blindly: **count the work** of a real recursion and see the growth.

```python
def cost(n, a, b, d, base=1):
    """Total work of T(n) = a*T(n/b) + n^d, summing the real recursion (n a power of b)."""
    if n <= base:
        return 1
    return a * cost(n // b, a, b, d, base) + n ** d

for n in (2 ** 6, 2 ** 8, 2 ** 10):
    merge = cost(n, 2, 2, 1)
    school = cost(n, 4, 2, 1)
    kara = cost(n, 3, 2, 1)
    print(n, round(merge / (n * math.log2(n)), 2), round(school / n ** 2, 2), round(kara / n ** 1.585, 2))
# 64 1.17 1.98 2.82
# 256 1.12 2.0 2.92
# 1024 1.1 2.0 2.96
```

Each ratio settles toward a constant (about 1.1, 2.0 and 3.0; Karatsuba's creeps up slowly), which is exactly what `Θ` means: merge sort grows like `n log n`, schoolbook multiplication like `n²`, Karatsuba like `n^1.585`.

(If your recurrence does not fit the form, for example subproblems of unequal sizes, fall back to drawing the recursion tree or the **Akra-Bazzi** generalization.)

## 3. Example 1: maximum subarray

**Problem.** Find the contiguous slice of a list with the largest sum.

**Divide and conquer idea.** The best slice lies entirely in the left half, entirely in the right half, or **crosses the middle**. Solve the halves recursively; compute the best crossing slice by growing outward from the middle in `O(n)`. Take the best of the three.

```python
def max_subarray_dc(nums, lo=0, hi=None):
    if hi is None:
        hi = len(nums) - 1
    if lo == hi:
        return nums[lo]                                    # base case: one element
    mid = (lo + hi) // 2
    left_best = max_subarray_dc(nums, lo, mid)
    right_best = max_subarray_dc(nums, mid + 1, hi)

    total, best_left = 0, float("-inf")                    # best slice ending exactly at mid, extending left
    for i in range(mid, lo - 1, -1):
        total += nums[i]
        best_left = max(best_left, total)
    total, best_right = 0, float("-inf")                   # best slice starting at mid + 1, extending right
    for i in range(mid + 1, hi + 1):
        total += nums[i]
        best_right = max(best_right, total)
    return max(left_best, right_best, best_left + best_right)      # combine

def max_subarray_brute(nums):
    return max(sum(nums[i:j]) for i in range(len(nums)) for j in range(i + 1, len(nums) + 1))

print(max_subarray_dc([-2, 1, -3, 4, -1, 2, 1, -5, 4]))   # 6     the slice [4, -1, 2, 1]
print(max_subarray_dc([-3, -1, -2]), max_subarray_dc([5]))  # -1 5

import random
random.seed(11)
for _ in range(500):
    data = [random.randint(-9, 9) for _ in range(random.randint(1, 12))]
    assert max_subarray_dc(data) == max_subarray_brute(data)
print("max subarray matched brute force on 500 random lists")      # max subarray matched brute force on 500 random lists
```

**Cost.** `T(n) = 2T(n/2) + n`, so `Θ(n log n)`. (Kadane's one-pass [DP](../dynamic-programming/01-dp-thinking-and-1d-problems.md) does it in `Θ(n)`: divide and conquer is not always the fastest, but it is a clean way to *derive* a solution and it parallelizes.)

## 4. Example 2: Karatsuba multiplication

**Problem.** Multiply two `n`-digit numbers. The schoolbook method does `n²` single-digit multiplications.

**Idea.** Split each number into a high and a low half: `x = x1 * B + x0`, `y = y1 * B + y0` (`B = 10^m`). Then

```text
x * y = x1*y1 * B^2  +  (x1*y0 + x0*y1) * B  +  x0*y0
```

needs **four** half-size products. **Karatsuba's trick** (1960) gets the middle term from **one** extra product:

```text
x1*y0 + x0*y1 = (x1 + x0)(y1 + y0) - x1*y1 - x0*y0
```

So only **three** half-size multiplications: `T(n) = 3T(n/2) + n = Θ(n^1.585)` instead of `Θ(n²)`.

```python
def karatsuba(x, y):
    if x < 10 or y < 10:
        return x * y                                       # base case: a single digit
    m = max(len(str(x)), len(str(y))) // 2
    base = 10 ** m
    x1, x0 = divmod(x, base)                               # x = x1 * base + x0
    y1, y0 = divmod(y, base)
    high = karatsuba(x1, y1)
    low = karatsuba(x0, y0)
    middle = karatsuba(x1 + x0, y1 + y0) - high - low       # the trick: ONE multiplication gives the cross terms
    return high * base * base + middle * base + low

print(karatsuba(1234, 5678), 1234 * 5678)                  # 7006652 7006652
random.seed(12)
for _ in range(300):
    a, b = random.randint(0, 10 ** 30), random.randint(0, 10 ** 30)
    assert karatsuba(a, b) == a * b
print("Karatsuba matched Python's * on 300 random 30-digit pairs")      # Karatsuba matched Python's * on 300 random 30-digit pairs
```

Count the single-digit multiplications to see the saving:

```python
def count_mults(x, y, trick):
    if x < 10 or y < 10:
        return 1
    m = max(len(str(x)), len(str(y))) // 2
    base = 10 ** m
    x1, x0 = divmod(x, base); y1, y0 = divmod(y, base)
    parts = [(x1, y1), (x0, y0), (x1 + x0, y1 + y0)] if trick else [(x1, y1), (x0, y0), (x1, y0), (x0, y1)]
    return sum(count_mults(a, b, trick) for a, b in parts)

n_digits = 64
x = y = int("9" * n_digits)
print(count_mults(x, y, trick=False), count_mults(x, y, trick=True))        # 4096 1815
```

For 64-digit numbers the four-product version performs 4096 digit multiplications and Karatsuba 1815, a 2.3x saving that grows with size. (The ideal count is `3^6 = 729` for 64 = 2^6 digits, but `x1 + x0` can carry into one extra digit, so the real sub-products are slightly larger than half-size; the saving still compounds as numbers grow.) Python's built-in `int` multiplication uses Karatsuba for big numbers, and faster FFT-based methods exist for huge ones. The same idea of "trade one multiplication for several additions" gives **Strassen's** matrix multiplication (`7` instead of `8` half-size products: `Θ(n^2.807)`).

## 5. Example 3: closest pair of points

**Problem.** Given `n` points in the plane, find the two closest. Brute force checks all pairs: `Θ(n²)`.

**Idea.** Sort the points by `x`; split at the middle line. The closest pair is in the left half, in the right half, or **straddles** the line. Let `δ` be the best of the two halves. A straddling pair must have both points within `δ` of the dividing line, and, remarkably, in that strip each point needs to be compared with only the next few points when the strip is sorted by `y` (a packing argument: at most 6 candidates fit in a `δ x 2δ` box without violating `δ`).

```python
import math

def closest_pair(points):
    pts = sorted(points)                                   # sort by x once

    def solve(lo, hi):                                     # closest distance among pts[lo:hi]
        n = hi - lo
        if n <= 3:                                         # base case: brute force
            return min((math.dist(pts[i], pts[j]) for i in range(lo, hi) for j in range(i + 1, hi)), default=float("inf"))
        mid = (lo + hi) // 2
        mid_x = pts[mid][0]
        delta = min(solve(lo, mid), solve(mid, hi))        # conquer both halves
        strip = sorted((p for p in pts[lo:hi] if abs(p[0] - mid_x) < delta), key=lambda p: p[1])
        best = delta
        for i in range(len(strip)):                        # combine: only nearby points in the strip matter
            for j in range(i + 1, len(strip)):
                if strip[j][1] - strip[i][1] >= best:
                    break                                   # too far apart vertically: later points are even farther
                best = min(best, math.dist(strip[i], strip[j]))
        return best

    return solve(0, len(pts))

def closest_pair_brute(points):
    return min(math.dist(a, b) for i, a in enumerate(points) for b in points[i + 1:])

sample = [(2, 3), (12, 30), (40, 50), (5, 1), (12, 10), (3, 4)]
print(round(closest_pair(sample), 4), round(closest_pair_brute(sample), 4))      # 1.4142 1.4142    the pair (2, 3) and (3, 4)
random.seed(13)
for _ in range(300):
    pts = list({(random.randint(0, 50), random.randint(0, 50)) for _ in range(random.randint(2, 25))})
    if len(pts) >= 2:
        assert abs(closest_pair(pts) - closest_pair_brute(pts)) < 1e-9
print("closest pair matched brute force on 300 random point sets")      # closest pair matched brute force on 300 random point sets
```

(Sorting the strip inside every call makes this version `O(n log² n)`; keeping the points merge-sorted by `y` through the recursion gets the textbook `O(n log n)`.)

Speed difference on 2000 random points:

```python
import time
random.seed(14)
many = list({(random.random(), random.random()) for _ in range(2000)})
t = time.perf_counter(); fast = closest_pair(many); fast_time = time.perf_counter() - t
t = time.perf_counter(); slow = closest_pair_brute(many); slow_time = time.perf_counter() - t
print(abs(fast - slow) < 1e-12, fast_time < slow_time)       # True True
```

Real uses: collision detection in games, clustering, air-traffic proximity alerts, and as a building block in computational geometry.

## 6. Example 4: majority element

**Problem.** Find the element that appears more than `n/2` times (if there is one).

**Idea.** If `x` is the majority of the whole list, it must be the majority of at least one half. So find each half's candidate, then **count** both candidates over the whole range and keep the one that wins.

```python
def majority_dc(nums, lo=0, hi=None):
    if hi is None:
        hi = len(nums)
    if hi - lo == 1:
        return nums[lo]
    mid = (lo + hi) // 2
    left, right = majority_dc(nums, lo, mid), majority_dc(nums, mid, hi)
    if left == right:
        return left
    left_count = sum(1 for i in range(lo, hi) if nums[i] == left)       # combine: count both candidates over the whole range
    right_count = sum(1 for i in range(lo, hi) if nums[i] == right)
    return left if left_count > right_count else right

def majority_brute(nums):
    from collections import Counter
    value, count = Counter(nums).most_common(1)[0]
    return value if count > len(nums) // 2 else None

print(majority_dc([2, 2, 1, 1, 1, 2, 2]), majority_dc([3, 2, 3]), majority_dc([7]))       # 2 3 7
random.seed(15)
for _ in range(500):
    data = [random.randint(0, 2) for _ in range(random.randint(1, 15))]
    expected = majority_brute(data)
    if expected is not None:                                                # the problem guarantees a majority exists
        assert majority_dc(data) == expected
print("majority element matched the counter on 500 random lists")         # majority element matched the counter on 500 random lists
```

`T(n) = 2T(n/2) + n`, so `Θ(n log n)`. (The Boyer-Moore voting algorithm does it in `Θ(n)` and `O(1)` space; the point here is the divide-and-conquer reasoning: a claim about the whole must hold for a part.)

## 7. Divide and conquer versus dynamic programming

Both break a problem into subproblems. The difference is whether subproblems **overlap**:

| | Divide and conquer | Dynamic programming |
|---|--------------------|---------------------|
| Subproblems | independent (each solved once, no overlap) | overlapping (same subproblem needed many times) |
| Tool | plain recursion | recursion + cache, or a table |
| Examples | merge sort, closest pair, Karatsuba | Fibonacci, edit distance, knapsack |
| If you misuse it | works fine | naive recursion explodes (`fib(40)` makes 300 million calls) |

A quick test: draw the recursion tree. If the same inputs appear in different branches, memoize (that is [DP](../dynamic-programming/01-dp-thinking-and-1d-problems.md)); if every node is different, plain divide and conquer is right.

## 8. Practical points

- **Base cases matter for speed.** Recursing down to size 1 is wasteful: real implementations switch to a simple method below a threshold (Timsort uses insertion sort under about 32 to 64 items; Python's big-int multiplication switches between schoolbook and Karatsuba by size).
- **Parallelism.** The conquer steps are independent, so they can run on different cores or machines. This is the idea of **MapReduce** (map = divide and solve, reduce = combine), parallel merge sort, and the way large sums and sorts are distributed in data processing frameworks.
- **Cache behavior.** Recursion that works on contiguous halves is cache-friendly (merge sort, FFT), which is why divide and conquer shows up in high-performance libraries.
- **Recursion depth** is only `log n` for balanced splits, so it is safe; unbalanced splits (quicksort with a bad pivot) can reach depth `n`.
- **Space.** The combine step often needs extra memory (merge sort's `O(n)` buffer).

## 9. Two real-world examples

**Example 1: Distributed sorting and analytics.** To sort a terabyte, split it across machines, sort each chunk in parallel, and merge the sorted chunks: divide and conquer at cluster scale. The Hadoop and Spark "shuffle" and "merge" phases follow this shape.

**Example 2: Signal processing.** The **Fast Fourier Transform** splits a signal into even- and odd-indexed samples, transforms each half and combines them with `T(n) = 2T(n/2) + n = Θ(n log n)` instead of `n²`. It is behind audio compression, image filters, Wi-Fi and 5G radio, and fast polynomial multiplication.

## 10. Common mistakes

- Splitting into unequal or overlapping parts without checking the recurrence.
- Forgetting the base case, or making it too deep (recursing to size 1 when a loop is faster below a threshold).
- Doing `O(n)` copying in every call (slicing lists) and accidentally getting an extra `log n` or worse; pass indexes instead.
- Using it where subproblems overlap (use DP).
- Misapplying the Master theorem (it needs equal-sized subproblems and a polynomial `f(n)`).
- Forgetting the combine step when it is the expensive part (merge, closest-pair strip, cross-sum).

## 11. Practice

1. Use `master` to classify: `T(n) = 2T(n/2) + 1`, `T(n) = 4T(n/2) + n²`, `T(n) = 8T(n/2) + n²`.
2. Write the recurrence for binary search and for merge sort and solve each.
3. Write a divide-and-conquer function that finds both the **minimum and maximum** of a list. How many comparisons does it use for `n = 8`?
4. Implement **power(x, n)** by divide and conquer and state its recurrence.
5. How many digit multiplications does the schoolbook method need for two 32-digit numbers? And Karatsuba (use `count_mults`)?
6. Write `count_inversions` by modifying merge sort (count, during the merge, how many left items each right item jumps over) and verify it on `[2, 4, 1, 3, 5]` (answer 3).
7. Why does the closest-pair strip check only a few neighbors per point?

<details>
<summary>Solutions</summary>

1. ```python
   print(master(2, 2, 0), master(4, 2, 2), master(8, 2, 2))
   # Theta(n^1.000)   Theta(n^2 log n)   Theta(n^3.000)
   ```
   `2T(n/2) + 1` is `Θ(n)` (leaves win); `4T(n/2) + n²` balances to `Θ(n² log n)`; `8T(n/2) + n²` is `Θ(n³)` (leaves win).
2. Binary search: `T(n) = T(n/2) + 1`, so `Θ(log n)` (`a = 1, b = 2, d = 0`, balanced case). Merge sort: `T(n) = 2T(n/2) + n`, so `Θ(n log n)`.
3. ```python
   def min_max(nums, lo=0, hi=None):
       if hi is None: hi = len(nums) - 1
       if lo == hi: return nums[lo], nums[lo], 0
       if hi == lo + 1:
           a, b = nums[lo], nums[hi]
           return (a, b, 1) if a < b else (b, a, 1)
       mid = (lo + hi) // 2
       lmin, lmax, lc = min_max(nums, lo, mid)
       rmin, rmax, rc = min_max(nums, mid + 1, hi)
       return min(lmin, rmin), max(lmax, rmax), lc + rc + 2
   print(min_max([5, 2, 9, 1, 7, 3, 8, 4]))                        # (1, 9, 10)
   ```
   For `n = 8` this uses 10 comparisons, fewer than the 14 of the naive two-pass method (`2(n - 1)`); in general `3n/2 - 2`.
4. ```python
   def power(x, n):
       if n == 0: return 1
       half = power(x, n // 2)
       return half * half if n % 2 == 0 else half * half * x
   print(power(3, 13))                                              # 1594323
   ```
   `T(n) = T(n/2) + 1`, so `Θ(log n)` multiplications.
5. ```python
   big = int("9" * 32)
   print(count_mults(big, big, False), count_mults(big, big, True))      # 1024 601
   ```
6. ```python
   def count_inversions(a):
       if len(a) <= 1: return a, 0
       mid = len(a) // 2
       left, x = count_inversions(a[:mid]); right, y = count_inversions(a[mid:])
       merged, i, j, cross = [], 0, 0, 0
       while i < len(left) and j < len(right):
           if left[i] <= right[j]: merged.append(left[i]); i += 1
           else: merged.append(right[j]); j += 1; cross += len(left) - i
       return merged + left[i:] + right[j:], x + y + cross
   print(count_inversions([2, 4, 1, 3, 5])[1])                      # 3
   ```
7. Inside the `δ`-wide strip, points are at least `δ` apart on each side of the line, so only a constant number of points (at most 6) can fit in the `δ x 2δ` window above a given point; anything farther up is at least `δ` away and cannot improve the best distance.

</details>

## 12. Check yourself

1. What are the three steps of divide and conquer?
2. What does the Master theorem say for `T(n) = 2T(n/2) + n`?
3. How does Karatsuba reduce four multiplications to three?
4. What are the three possible locations of the best slice in the maximum-subarray problem?
5. How do you decide between divide and conquer and dynamic programming?
6. Why are divide-and-conquer algorithms easy to parallelize?

<details>
<summary>Answers</summary>

1. Divide into smaller copies of the problem, conquer them recursively (base case directly), combine the answers.
2. `a = 2, b = 2, d = 1`: balanced, so `Θ(n log n)`.
3. It computes the cross terms `x1*y0 + x0*y1` as `(x1 + x0)(y1 + y0) - x1*y1 - x0*y0`, reusing two products it already needs.
4. Entirely in the left half, entirely in the right half, or crossing the middle.
5. If subproblems are independent, plain divide and conquer; if the same subproblems recur in different branches, cache them (dynamic programming).
6. The subproblems are independent, so they can be solved on different cores or machines and merged.

</details>

[Back to algorithms](../README.md)
