# Divide and Conquer: Exercises

These problems go with the [Divide and Conquer lesson](README.md). Try each one before opening its solution.

<details>
<summary>Setup code the solutions use (copied from the lessons)</summary>

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

def count_mults(x, y, trick):
    if x < 10 or y < 10:
        return 1
    m = max(len(str(x)), len(str(y))) // 2
    base = 10 ** m
    x1, x0 = divmod(x, base); y1, y0 = divmod(y, base)
    parts = [(x1, y1), (x0, y0), (x1 + x0, y1 + y0)] if trick else [(x1, y1), (x0, y0), (x1, y0), (x0, y1)]
    return sum(count_mults(a, b, trick) for a, b in parts)
```

</details>

## Problems

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

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Divide and Conquer](01-divide-and-conquer.md)
