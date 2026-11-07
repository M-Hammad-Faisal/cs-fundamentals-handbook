# Binary Search on the Answer and Other Search Techniques

**Prerequisites:** [linear and binary search](01-linear-and-binary-search.md). **You will learn:** the powerful idea of binary searching not an array but the **answer itself**, with a reusable template and five classic problems; plus **exponential search** (unbounded lists), **interpolation search**, **ternary search** for peaks, and **floating-point binary search**.

## 1. The big idea

Binary search needs one thing: a yes/no question whose answer is **monotonic**: all `False` up to some point, then all `True` (or the reverse). The array is just one example. Any time you can ask *"is `x` big enough?"* and the answer flips from No to Yes exactly once as `x` grows, you can binary-search `x`.

```text
x:        1   2   3   4   5   6   7   8
enough?   N   N   N   N   Y   Y   Y   Y        find the smallest x with "Y"  ->  5
```

## 2. The template: smallest value that works

```python
def smallest_true(lo, hi, is_ok):
    """Smallest x in [lo, hi] with is_ok(x) True; assumes is_ok is False...False True...True.
    Returns hi + 1 if none works."""
    hi += 1
    while lo < hi:
        mid = (lo + hi) // 2
        if is_ok(mid):
            hi = mid                                # mid works: the answer is mid or something smaller
        else:
            lo = mid + 1                            # mid fails: the answer is larger
    return lo

print(smallest_true(1, 8, lambda x: x >= 5))        # 5
print(smallest_true(1, 8, lambda x: x >= 99))       # 9   (nothing works)
```

Solving a problem becomes three steps: (1) **define the range** of possible answers, (2) write `is_ok(x)` (the "feasibility check", usually a simple greedy loop), (3) call the template.

## 3. Classic problem 1: integer square root

Smallest `x` with `x * x > n`, minus one:

```python
def isqrt(n):
    return smallest_true(0, n, lambda x: x * x > n) - 1

print(isqrt(16), isqrt(17), isqrt(0), isqrt(10**18))      # 4 4 0 1000000000
```

## 4. Classic problem 2: shipping packages within D days

Packages (weights in order) must ship within `days`. What is the **minimum ship capacity**?

- Answer range: `max(weights)` (every package must fit) up to `sum(weights)` (everything in one day).
- `is_ok(capacity)`: greedily fill each day; count the days needed; is it `<= days`?
- Bigger capacity never needs more days: **monotonic**.

```python
def ship_within_days(weights, days):
    def feasible(capacity):
        needed, load = 1, 0
        for w in weights:
            if load + w > capacity:                 # does not fit today: start a new day
                needed += 1
                load = 0
            load += w
        return needed <= days
    return smallest_true(max(weights), sum(weights), feasible)

print(ship_within_days([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5))     # 15
print(ship_within_days([3, 2, 2, 4, 1, 4], 3))                  # 6
```

Cost: `O(n log(sum))` instead of trying every capacity.

## 5. Classic problem 3: eating bananas (minimum speed)

Koko eats `k` bananas per hour from one pile at a time (finishing a pile early wastes the rest of the hour). Find the minimum `k` to finish all piles in `h` hours.

```python
import math

def min_eating_speed(piles, h):
    return smallest_true(1, max(piles), lambda k: sum(math.ceil(p / k) for p in piles) <= h)

print(min_eating_speed([3, 6, 7, 11], 8), min_eating_speed([30, 11, 23, 4, 20], 5))      # 4 30
```

## 6. Classic problem 4: split an array to minimize the largest sum

Split `nums` into `m` contiguous parts so that the **largest part sum is as small as possible**.

```python
def split_array(nums, m):
    def feasible(limit):
        parts, current = 1, 0
        for x in nums:
            if current + x > limit:
                parts += 1
                current = 0
            current += x
        return parts <= m
    return smallest_true(max(nums), sum(nums), feasible)

print(split_array([7, 2, 5, 10, 8], 2))             # 18   ([7, 2, 5] and [10, 8])
```

This is also **"painter's partition"** and "allocate books to students": same structure, different story.

## 7. Classic problem 5: placing things as far apart as possible (maximize the minimum)

Place `k` cows in stalls at positions `stalls` so the **smallest gap between any two is as large as possible**. Now we want the **largest** `x` that works, so flip the template: search for the last `True`.

```python
def largest_true(lo, hi, is_ok):
    """Largest x in [lo, hi] with is_ok(x) True; assumes True...True False...False."""
    while lo < hi:
        mid = (lo + hi + 1) // 2                    # round UP so lo = mid always makes progress
        if is_ok(mid):
            lo = mid
        else:
            hi = mid - 1
    return lo

def max_min_distance(stalls, cows):
    stalls = sorted(stalls)
    def feasible(gap):                              # can we place all cows at least `gap` apart?
        placed, last = 1, stalls[0]
        for s in stalls[1:]:
            if s - last >= gap:
                placed += 1
                last = s
        return placed >= cows
    return largest_true(1, stalls[-1] - stalls[0], feasible)

print(max_min_distance([1, 2, 8, 4, 9], 3))         # 3   (cows at 1, 4, 8 or 1, 4, 9)
```

**Remember the rounding rule:** when the update is `lo = mid`, round `mid` **up**; when it is `hi = mid`, round it down. Getting this wrong is the usual cause of infinite loops.

## 8. Binary search on real numbers

For continuous answers, loop a fixed number of times (or until the interval is tiny) instead of until `lo > hi`.

```python
def cube_root(x, iterations=100):
    lo, hi = 0.0, max(1.0, x)
    for _ in range(iterations):                     # 100 halvings gives about 30 digits of precision
        mid = (lo + hi) / 2
        if mid ** 3 < x:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2

print(round(cube_root(27), 6), round(cube_root(2), 6))      # 3.0 1.259921
```

## 9. Other search techniques

### Exponential (galloping) search: when you do not know the length

Double the index until you overshoot, then binary search the last stretch: `O(log i)` where `i` is the answer's position. Useful for infinite or streamed sorted data (and Timsort's "galloping" uses the same trick).

```python
import bisect

def exponential_search(get, target):                # get(i) returns the i-th value or None past the end
    if get(0) == target:
        return 0
    bound = 1
    while get(bound) is not None and get(bound) < target:
        bound *= 2
    lo, hi = bound // 2, bound
    while lo <= hi:
        mid = (lo + hi) // 2
        v = get(mid)
        if v is None or v > target:
            hi = mid - 1
        elif v < target:
            lo = mid + 1
        else:
            return mid
    return -1

stream = list(range(0, 3000, 3))                    # 0, 3, 6, ..., 2997 (length hidden from the search)
look = lambda i: stream[i] if i < len(stream) else None
print(exponential_search(look, 1500), exponential_search(look, 1501))   # 500 -1
```

### Interpolation search: guess where the value should be

If values are roughly **uniformly distributed**, estimate the position by proportion (like opening a phone book near "S" for "Smith"). Average `O(log log n)`, worst case `O(n)`.

```python
def interpolation_search(items, target):
    lo, hi, probes = 0, len(items) - 1, 0
    while lo <= hi and items[lo] <= target <= items[hi]:
        if items[hi] == items[lo]:
            return (lo if items[lo] == target else -1), probes
        pos = lo + (target - items[lo]) * (hi - lo) // (items[hi] - items[lo])
        probes += 1
        if items[pos] == target:
            return pos, probes
        if items[pos] < target:
            lo = pos + 1
        else:
            hi = pos - 1
    return -1, probes

uniform = list(range(0, 1_000_000, 10))
print(interpolation_search(uniform, 777_770))        # (77777, 1)   (one probe for evenly spaced data)
```

### Ternary search: finding the peak of a single-hump function

For a function that rises then falls (unimodal), compare two interior points and discard the third that cannot hold the peak.

```python
def ternary_max(f, lo, hi, iterations=100):
    for _ in range(iterations):
        m1, m2 = lo + (hi - lo) / 3, hi - (hi - lo) / 3
        if f(m1) < f(m2):
            lo = m1                                  # the peak is right of m1
        else:
            hi = m2                                  # the peak is left of m2
    return (lo + hi) / 2

# profit = price * demand with demand falling as price rises: where is the best price?
best_price = ternary_max(lambda p: p * (100 - 2 * p), 0, 50)
print(round(best_price, 3))                          # 25.0
```

For arrays, "find a peak element" is plain binary search comparing `items[mid]` with `items[mid + 1]`:

```python
def find_peak(items):
    lo, hi = 0, len(items) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if items[mid] < items[mid + 1]:
            lo = mid + 1                             # still climbing: a peak lies to the right
        else:
            hi = mid
    return lo

print(find_peak([1, 3, 7, 12, 9, 4, 2]))             # 3
```

## 10. How to recognize a "binary search on the answer" problem

| Clue in the problem statement | Likely shape |
|-------------------------------|--------------|
| "minimum possible maximum" / "maximize the minimum" | search the answer value, greedy feasibility check |
| "smallest capacity / speed / time such that..." | `smallest_true` |
| "largest distance / size such that..." | `largest_true` |
| The answer is within a numeric range and checking one candidate is easy | binary search the range |
| More of the resource never makes things worse | monotonic: it works |

## 11. Two real-world examples

**Example 1: Capacity planning.** "What is the smallest number of servers that handles peak load with 99% of requests under 200 ms?" You can simulate any server count; the answer is monotonic, so you binary search the count instead of simulating them all.

**Example 2: Rate limiting and scheduling.** Finding the minimum batch size or worker count that finishes a job queue before a deadline uses exactly the shipping-packages pattern.

## 12. Common mistakes

- A feasibility function that is **not monotonic** (binary search then gives garbage).
- Wrong search bounds (a lower bound below the true minimum, e.g. `1` instead of `max(weights)`, is fine; one that excludes the answer is not).
- `mid` rounding the wrong way in the `largest_true` direction (infinite loop).
- Using `==` with floats instead of a fixed number of iterations or an epsilon.
- Spending `O(n)` per check when a prefix sum would make it `O(1)`.
- Applying it to a problem where greedy checking is not valid for the feasibility test.

## 13. Practice

1. Use `smallest_true` to find the smallest `x` with `x**2 >= 200`.
2. Why is the shipping problem's answer range `[max(weights), sum(weights)]`?
3. Compute `ship_within_days([5, 5, 5, 5], 2)` and explain.
4. Minimum time for `m` workers to each make bricks: worker `i` needs `times[i]` minutes per brick; find the least time to make `n` bricks with `times = [1, 2, 3]`, `n = 10`.
5. Write `sqrt_float(x)` with 50 iterations and compare against `math.sqrt(2)`.
6. A function with values `[2, 6, 9, 7, 3]` is unimodal; which index does `find_peak` return?

<details>
<summary>Solutions</summary>

1. ```python
   print(smallest_true(0, 200, lambda x: x * x >= 200))       # 15
   ```
2. A smaller capacity cannot even carry the heaviest package; larger than the total is pointless (everything fits in one day).
3. ```python
   print(ship_within_days([5, 5, 5, 5], 2))                   # 10
   ```
   Two days of two packages each need capacity 10; any less would need three days.
4. ```python
   def min_time(times, n):
       return smallest_true(1, min(times) * n, lambda t: sum(t // x for x in times) >= n)
   print(min_time([1, 2, 3], 10))                             # 6   (6//1 + 6//2 + 6//3 = 11 >= 10)
   ```
5. ```python
   def sqrt_float(x):
       lo, hi = 0.0, max(1.0, x)
       for _ in range(50):
           mid = (lo + hi) / 2
           lo, hi = (mid, hi) if mid * mid < x else (lo, mid)
       return (lo + hi) / 2
   import math
   print(abs(sqrt_float(2) - math.sqrt(2)) < 1e-12)           # True
   ```
6. `find_peak([2, 6, 9, 7, 3])` returns `2` (the value 9).

</details>

## 14. Check yourself

1. What property must the feasibility check have?
2. In `largest_true`, why is `mid` rounded up?
3. What are the three steps to solve a "binary search on the answer" problem?
4. When is exponential search useful?
5. When does interpolation search beat binary search?

<details>
<summary>Answers</summary>

1. Monotonic: once it becomes true as the value grows, it stays true (or the reverse).
2. Because `lo = mid` must make progress; rounding down could leave `lo` unchanged forever.
3. Define the range of answers, write the feasibility check, run the search template.
4. When the size is unknown or unbounded (streams, huge files), or the target is near the front.
5. When keys are roughly uniformly distributed: about `O(log log n)` probes.

</details>

[Back to searching](README.md) · Previous: [linear and binary search](01-linear-and-binary-search.md)
