# Working with Arrays: Essential Techniques

**Prerequisites:** [arrays and memory](01-arrays-and-memory.md), [control flow](../../00-foundations/python-fundamentals/02-control-flow.md). **You will learn:** the core techniques for solving array problems: traversal patterns, in-place updates, two pointers, sliding windows, prefix sums, Kadane's maximum subarray, sorting-based tricks, rotation, 2D grid walks and binary search on sorted arrays. Each technique has a trace, code and the complexity.

## 1. In plain words

Most array problems are solved by a **small set of reusable ideas**. Learn these ten and you can solve a surprising share of interview and real-world problems. The general strategy: **do one pass instead of many**, **use a second index to avoid nested loops**, and **precompute totals so you never add the same numbers twice**.

## 2. Technique 1: traversal patterns

```python
nums = [4, 8, 15, 16, 23, 42]

for x in nums:                         # by value (when you do not need the position)
    pass
for i in range(len(nums)):             # by index (when you need to modify or look at neighbors)
    pass
for i, x in enumerate(nums):           # both
    pass
for i in range(len(nums) - 1, -1, -1): # backwards (safe when deleting or shifting)
    pass
for a, b in zip(nums, nums[1:]):       # neighbors: (4, 8), (8, 15), ...
    pass

print(sum(b - a for a, b in zip(nums, nums[1:])), nums[-1] - nums[0])        # 38 38   (differences telescope)
print([nums[i] for i in range(0, len(nums), 2)], nums[::2], nums[::-1])      # [4, 15, 23] [4, 15, 23] [42, 23, 16, 15, 8, 4]
```

**Rule:** never add or remove items of a list while looping over it with `for x in the_list`; build a new list or loop over a copy.

```python
nums2 = [1, 2, 3, 4, 5, 6]
wrong = nums2[:]
for x in wrong:
    if x % 2 == 0:
        wrong.remove(x)                # BUG: removing while iterating skips items
print(wrong)                           # [1, 3, 5]  (looks right by luck here)
tricky = [2, 4, 6, 8]
for x in tricky[:]:                    # iterate over a COPY
    if x % 2 == 0:
        tricky.remove(x)
print(tricky)                          # []
buggy = [2, 4, 6, 8]
for x in buggy:
    if x % 2 == 0:
        buggy.remove(x)
print(buggy)                           # [4, 8]   <- the bug: items were skipped
```

## 3. Technique 2: in-place updates and swapping

```python
def reverse_in_place(items):
    lo, hi = 0, len(items) - 1
    while lo < hi:
        items[lo], items[hi] = items[hi], items[lo]      # swap with tuple assignment
        lo, hi = lo + 1, hi - 1
    return items

def move_zeros_to_end(items):
    """Stable, in place: the write pointer collects non-zero items; the rest become zeros."""
    write = 0
    for read in range(len(items)):
        if items[read] != 0:
            items[write] = items[read]
            write += 1
    for i in range(write, len(items)):
        items[i] = 0
    return items

print(reverse_in_place([1, 2, 3, 4, 5]), move_zeros_to_end([0, 1, 0, 3, 12]))      # [5, 4, 3, 2, 1] [1, 3, 12, 0, 0]
```

Trace of `move_zeros_to_end([0, 1, 0, 3, 12])`:

| read | item | action | array after |
|------|------|--------|-------------|
| 0 | 0 | skip | `[0, 1, 0, 3, 12]` write=0 |
| 1 | 1 | `items[0] = 1`, write=1 | `[1, 1, 0, 3, 12]` |
| 2 | 0 | skip | |
| 3 | 3 | `items[1] = 3`, write=2 | `[1, 3, 0, 3, 12]` |
| 4 | 12 | `items[2] = 12`, write=3 | `[1, 3, 12, 3, 12]` |
| fill | | positions 3, 4 become 0 | `[1, 3, 12, 0, 0]` |

`O(n)` time, `O(1)` space.

## 4. Technique 3: two pointers

Use **two indexes** that move through the array according to a rule, replacing a nested loop (`O(n²)`) with one pass (`O(n)`).

### Opposite ends, moving inward (works on sorted arrays)

```python
def pair_with_sum(sorted_nums, target):
    lo, hi = 0, len(sorted_nums) - 1
    while lo < hi:
        total = sorted_nums[lo] + sorted_nums[hi]
        if total == target:
            return (sorted_nums[lo], sorted_nums[hi])
        if total < target:
            lo += 1                      # need a bigger sum: the left item is too small for any partner
        else:
            hi -= 1                      # need a smaller sum: the right item is too big
    return None

print(pair_with_sum([1, 3, 4, 6, 9, 11], 15), pair_with_sum([1, 3, 4], 100))     # (4, 11) None
```

Why it is correct: if `nums[lo] + nums[hi]` is too small, **no pair containing `nums[lo]` can work** (the largest possible partner is already `nums[hi]`), so we safely discard `lo`. Each step discards one item: at most `n` steps.

### Same direction (slow and fast pointers)

```python
def remove_duplicates_sorted(nums):
    """Keep one copy of each value in a sorted list, in place. Returns the new length."""
    if not nums:
        return 0
    slow = 0
    for fast in range(1, len(nums)):
        if nums[fast] != nums[slow]:
            slow += 1
            nums[slow] = nums[fast]
    return slow + 1

data = [1, 1, 2, 2, 2, 3, 4, 4]
k = remove_duplicates_sorted(data)
print(k, data[:k])                       # 4 [1, 2, 3, 4]

def is_palindrome(text):
    chars = [c.lower() for c in text if c.isalnum()]
    lo, hi = 0, len(chars) - 1
    while lo < hi:
        if chars[lo] != chars[hi]:
            return False
        lo, hi = lo + 1, hi - 1
    return True
print(is_palindrome("A man, a plan, a canal: Panama"), is_palindrome("hello"))   # True False
```

### Merging two sorted arrays

```python
def merge_sorted(a, b):
    i = j = 0
    out = []
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out.append(a[i]); i += 1
        else:
            out.append(b[j]); j += 1
    out.extend(a[i:]); out.extend(b[j:])          # one of these is empty
    return out
print(merge_sorted([1, 4, 9], [2, 3, 10, 11]))   # [1, 2, 3, 4, 9, 10, 11]
```

This `O(n + m)` merge is the heart of **merge sort** ([sorting](../../03-algorithms/sorting/README.md)).

## 5. Technique 4: sliding window

For problems about **contiguous subarrays** ("the best run of 3 days", "the longest stretch without repeats"), keep a **window** `[left, right]` and **slide** it, updating the answer incrementally instead of recomputing from scratch.

```python
def max_sum_of_k(nums, k):
    """Fixed-size window: best total of k consecutive items. O(n) instead of O(n*k)."""
    window = sum(nums[:k])
    best = window
    for right in range(k, len(nums)):
        window += nums[right] - nums[right - k]       # add the new item, drop the old one
        best = max(best, window)
    return best

print(max_sum_of_k([2, 1, 5, 1, 3, 2], 3))            # 9   (5 + 1 + 3)

def shortest_subarray_at_least(nums, target):
    """Variable-size window: the shortest run (positive numbers) whose sum is at least target."""
    left = total = 0
    best = float("inf")
    for right, x in enumerate(nums):
        total += x
        while total >= target:                         # shrink while still valid
            best = min(best, right - left + 1)
            total -= nums[left]
            left += 1
    return 0 if best == float("inf") else best

print(shortest_subarray_at_least([2, 3, 1, 2, 4, 3], 7))     # 2   ([4, 3])
```

Window trace for `max_sum_of_k([2, 1, 5, 1, 3, 2], 3)`:

```text
[2 1 5] 1 3 2     sum = 8
 2 [1 5 1] 3 2    sum = 8 - 2 + 1 = 7
 2 1 [5 1 3] 2    sum = 7 - 1 + 3 = 9   <- best
 2 1 5 [1 3 2]    sum = 9 - 5 + 2 = 6
```

## 6. Technique 5: prefix sums (precompute totals)

If you will ask **many range-sum questions** on the same array, precompute the running totals once. Then any range sum is a subtraction (`O(1)`).

```text
nums:    [3, 1, 4, 1, 5, 9]
prefix:  [0, 3, 4, 8, 9, 14, 23]          prefix[i] = sum of the first i items
sum(nums[l..r]) = prefix[r + 1] - prefix[l]
sum(nums[2..4]) = prefix[5] - prefix[2] = 14 - 4 = 10     (4 + 1 + 5)
```

```python
class RangeSum:
    def __init__(self, nums):
        self.prefix = [0]
        for x in nums:
            self.prefix.append(self.prefix[-1] + x)
    def sum(self, left, right):                       # inclusive range
        return self.prefix[right + 1] - self.prefix[left]

rs = RangeSum([3, 1, 4, 1, 5, 9])
print(rs.prefix, rs.sum(2, 4), rs.sum(0, 5))          # [0, 3, 4, 8, 9, 14, 23] 10 23

# Cost: O(n) to build, then O(1) per query. 1,000,000 queries on 1,000,000 numbers:
#   naive: up to 10^12 additions     prefix sums: about 2 x 10^6 operations
import itertools
print(list(itertools.accumulate([3, 1, 4, 1, 5, 9])))  # [3, 4, 8, 9, 14, 23]   (the standard library builds running totals)
```

**Prefix sums + dictionary** solve "how many subarrays sum to `k`":

```python
from collections import defaultdict

def count_subarrays_with_sum(nums, k):
    count, running = 0, 0
    seen = defaultdict(int)
    seen[0] = 1                                        # the empty prefix
    for x in nums:
        running += x
        count += seen[running - k]                     # earlier prefixes that leave exactly k in between
        seen[running] += 1
    return count
print(count_subarrays_with_sum([1, 2, 3, -2, 2], 3))   # 4   ([1,2], [3], [2,3,-2], [3,-2,2])
```

## 7. Technique 6: Kadane's algorithm (maximum subarray)

**Problem:** find the contiguous subarray with the largest sum (numbers may be negative). The brute force checks every subarray (`O(n²)` or `O(n³)`). **Kadane's idea:** at each position, either **extend** the best subarray ending at the previous position or **start fresh** here.

```python
def max_subarray(nums):
    best = current = nums[0]
    for x in nums[1:]:
        current = max(x, current + x)                  # extend, or restart at x if the running sum is hurting us
        best = max(best, current)
    return best

print(max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]))   # 6   (the subarray [4, -1, 2, 1])
```

| x | current = max(x, current + x) | best |
|---|-------------------------------|------|
| -2 | -2 | -2 |
| 1 | max(1, -1) = 1 | 1 |
| -3 | max(-3, -2) = -2 | 1 |
| 4 | max(4, 2) = 4 | 4 |
| -1 | max(-1, 3) = 3 | 4 |
| 2 | max(2, 5) = 5 | 5 |
| 1 | max(1, 6) = 6 | 6 |
| -5 | max(-5, 1) = 1 | 6 |
| 4 | max(4, 5) = 5 | 6 |

`O(n)` time, `O(1)` space. (This is a tiny dynamic program: `current` is "the best answer ending here".)

## 8. Technique 7: sort first

Sorting (`O(n log n)`) often turns a hard problem into an easy one: duplicates become adjacent, pairs can use two pointers, intervals can be merged in one sweep, the median is the middle item.

```python
def has_duplicates(nums):                              # O(n log n), O(1) extra with an in-place sort
    ordered = sorted(nums)
    return any(a == b for a, b in zip(ordered, ordered[1:]))

def merge_intervals(intervals):
    out = []
    for start, end in sorted(intervals):               # sort by start, then sweep
        if out and start <= out[-1][1]:
            out[-1][1] = max(out[-1][1], end)
        else:
            out.append([start, end])
    return out

def median(nums):
    s = sorted(nums); mid = len(s) // 2
    return s[mid] if len(s) % 2 else (s[mid - 1] + s[mid]) / 2

print(has_duplicates([3, 1, 4, 1]), merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]]), median([5, 3, 1, 4]))
# True [[1, 6], [8, 10], [15, 18]] 3.5
```

## 9. Technique 8: rotation and reversal tricks

```python
def rotate_right(nums, k):
    """Rotate in place using three reversals: O(n) time, O(1) space."""
    n = len(nums)
    k %= n
    def reverse(lo, hi):
        while lo < hi:
            nums[lo], nums[hi] = nums[hi], nums[lo]
            lo, hi = lo + 1, hi - 1
    reverse(0, n - 1)           # [7,6,5,4,3,2,1]
    reverse(0, k - 1)           # [5,6,7,4,3,2,1]
    reverse(k, n - 1)           # [5,6,7,1,2,3,4]
    return nums

print(rotate_right([1, 2, 3, 4, 5, 6, 7], 3))          # [5, 6, 7, 1, 2, 3, 4]
```

## 10. Technique 9: 2D grids

```python
grid = [[1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]]
rows, cols = len(grid), len(grid[0])

row_sums = [sum(row) for row in grid]
col_sums = [sum(grid[r][c] for r in range(rows)) for c in range(cols)]
diagonal = sum(grid[i][i] for i in range(min(rows, cols)))
print(row_sums, col_sums, diagonal)                    # [6, 15, 24] [12, 15, 18] 15

rotated = [list(row) for row in zip(*grid[::-1])]      # rotate 90 degrees clockwise
print(rotated)                                         # [[7, 4, 1], [8, 5, 2], [9, 6, 3]]

def spiral(matrix):
    out = []
    while matrix:
        out += matrix.pop(0)                            # take the top row
        matrix = [list(r) for r in zip(*matrix)][::-1]  # rotate the rest counter-clockwise
    return out
print(spiral([[1, 2, 3], [4, 5, 6], [7, 8, 9]]))       # [1, 2, 3, 6, 9, 8, 7, 4, 5]

# Neighbors of a cell (a pattern used in flood fill, game of life, shortest path on a grid)
def neighbors(r, c, rows, cols):
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols:           # stay inside the grid
            yield nr, nc
print(sorted(neighbors(0, 0, 3, 3)), len(list(neighbors(1, 1, 3, 3))))           # [(0, 1), (1, 0)] 4
```

## 11. Technique 10: binary search on a sorted array

If the array is **sorted**, you can find an item (or the insertion point) in `O(log n)` by halving the range ([searching](../../03-algorithms/searching/README.md)).

```python
import bisect

def binary_search(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

data = [1, 3, 5, 7, 9, 11]
print(binary_search(data, 7), binary_search(data, 4), bisect.bisect_left(data, 4), bisect.bisect_right(data, 7))     # 3 -1 2 4
```

## 12. Choosing the technique

| The problem says... | Try |
|---------------------|-----|
| "sorted array", "pair/triple with sum", "palindrome" | two pointers |
| "contiguous subarray/substring of length k or with property" | sliding window |
| "sum of range", "many queries", "subarray sum equals k" | prefix sums (+ hash map) |
| "maximum subarray sum" | Kadane |
| "duplicates", "intervals", "median", "closest" | sort first |
| "in place", "O(1) space" | write/read pointers, swaps, reversals |
| "find in sorted data", "first position where..." | binary search |
| "grid", "matrix" | row/column loops, directions, flat index math |

## 13. Two real-world examples

**Example 1: Stock analysis.** "Best day to buy and sell" is a one-pass scan keeping the lowest price so far; "best 30-day period" is a sliding window; "average over any date range" uses prefix sums so a dashboard answers thousands of range queries instantly.

```python
def best_profit(prices):
    lowest, profit = float("inf"), 0
    for price in prices:
        lowest = min(lowest, price)
        profit = max(profit, price - lowest)
    return profit
print(best_profit([7, 1, 5, 3, 6, 4]))                  # 5   (buy at 1, sell at 6)
```

**Example 2: Game of Life and image filters.** A blur filter averages each pixel with its eight neighbors; Conway's Game of Life counts live neighbors in a 2D grid. Both are nested loops over a 2D array using the neighbor-direction pattern, and both must write results to a **new** grid (or the updates would corrupt later calculations).

## 14. Common mistakes

- Off-by-one in window or pointer updates (`<` vs `<=`, `right - left + 1`).
- Using two pointers on **unsorted** data where order does not justify discarding items.
- Recomputing a sum inside a loop (use a window or prefix sums).
- Mutating while iterating.
- Forgetting empty and single-element inputs.
- Assuming Kadane works when you must return the subarray (track start and end indexes) or when all numbers are negative (this version handles it; initializing `best = 0` would not).
- Slicing inside a loop (`nums[i:]` copies).

## 15. Practice

1. Find the second largest distinct value in one pass.
2. Given a sorted array, return the squares of its items in sorted order in `O(n)` (two pointers from both ends).
3. Longest run of consecutive `1`s in a binary array.
4. Given prices, compute the maximum profit allowing as many buy/sell pairs as you like (but holding at most one share).
5. Use prefix sums to answer "how many even numbers are in `nums[l..r]`?" in `O(1)` per query.
6. Find the product of all items except self without division.
7. Rotate a matrix 90 degrees in place (hint: transpose, then reverse each row).

<details>
<summary>Solutions</summary>

**1.**
```python
def second_largest(nums):
    first = second = float("-inf")
    for x in nums:
        if x > first:
            first, second = x, first
        elif first > x > second:
            second = x
    return second
print(second_largest([5, 9, 2, 9, 7]))                 # 7
```

**2.**
```python
def sorted_squares(nums):
    out = [0] * len(nums)
    lo, hi = 0, len(nums) - 1
    for pos in range(len(nums) - 1, -1, -1):
        if abs(nums[lo]) > abs(nums[hi]):
            out[pos] = nums[lo] ** 2; lo += 1
        else:
            out[pos] = nums[hi] ** 2; hi -= 1
    return out
print(sorted_squares([-4, -1, 0, 3, 10]))              # [0, 1, 9, 16, 100]
```

**3.**
```python
def longest_ones(bits):
    best = run = 0
    for b in bits:
        run = run + 1 if b == 1 else 0
        best = max(best, run)
    return best
print(longest_ones([1, 1, 0, 1, 1, 1]))                # 3
```

**4.**
```python
def max_profit_many(prices):
    return sum(max(0, b - a) for a, b in zip(prices, prices[1:]))     # collect every upward step
print(max_profit_many([7, 1, 5, 3, 6, 4]))             # 7   (1->5 gains 4, 3->6 gains 3)
```

**5.**
```python
def build_even_prefix(nums):
    prefix = [0]
    for x in nums:
        prefix.append(prefix[-1] + (x % 2 == 0))
    return prefix
evens = build_even_prefix([2, 3, 4, 6, 7])
print(evens[5] - evens[1])                              # 2   (items 3, 4, 6, 7 contain 4 and 6)
```

**6.**
```python
def product_except_self(nums):
    out, prefix = [1] * len(nums), 1
    for i, x in enumerate(nums):
        out[i] = prefix; prefix *= x
    suffix = 1
    for i in range(len(nums) - 1, -1, -1):
        out[i] *= suffix; suffix *= nums[i]
    return out
print(product_except_self([1, 2, 3, 4]))               # [24, 12, 8, 6]
```

**7.**
```python
def rotate_matrix(m):
    n = len(m)
    for i in range(n):
        for j in range(i + 1, n):
            m[i][j], m[j][i] = m[j][i], m[i][j]        # transpose in place
    for row in m:
        row.reverse()                                  # then reverse each row
    return m
print(rotate_matrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]]))   # [[7, 4, 1], [8, 5, 2], [9, 6, 3]]
```

</details>

## 16. Check yourself

1. Why do two pointers work on a sorted array?
2. When use a sliding window?
3. What does a prefix sum array let you do, and at what cost?
4. What is Kadane's key idea?
5. How do you rotate an array in place in `O(n)` time and `O(1)` space?
6. Why shouldn't you remove items from a list while looping over it?

<details>
<summary>Answers</summary>

1. Order lets you discard one end each step (too small or too big), so each item is considered once.
2. For contiguous subarray/substring problems with a size or condition: move the window instead of recomputing.
3. Answer any range-sum query in `O(1)` after an `O(n)` precomputation.
4. At each position either extend the best subarray ending before it or start a new one; keep the best seen.
5. Reverse the whole array, then reverse the first `k` items and the remaining items.
6. The list shifts under the loop, so some items are skipped.

</details>

[Back to arrays and strings](README.md) · Previous: [arrays and memory](01-arrays-and-memory.md) · Next: [strings in depth](03-strings-in-depth.md)
