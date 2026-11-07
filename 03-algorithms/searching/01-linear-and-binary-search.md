# Linear Search and Binary Search

**Prerequisites:** [arrays](../../02-data-structures/arrays-strings/01-arrays-and-memory.md), [logarithms](../../00-foundations/math-for-cs/exponents-and-logarithms.md), [loops and loop invariants](../../01-complexity/04-analyzing-loops-and-recursion.md). **You will learn:** linear search, **binary search** step by step (the algorithm everybody gets subtly wrong), the **invariant** that makes it correct, the useful variants (**first/last occurrence, lower bound, insertion point**), the `bisect` module, and how to search rotated arrays and 2D matrices.

## 1. In plain words

**Linear search:** look at every item until you find it, like reading a shelf of books left to right. Always works, even on unsorted data. Cost `O(n)`.

**Binary search:** the "guess my number between 1 and 100" game. If you always guess the **middle** and are told "higher" or "lower", you need at most 7 guesses, because each guess halves the possibilities. It requires the data to be **sorted**.

| Items `n` | Linear search (worst) | Binary search (worst) |
|-----------|-----------------------|-----------------------|
| 100 | 100 | 7 |
| 1 000 000 | 1 000 000 | 20 |
| 1 000 000 000 | 1 000 000 000 | 30 |

## 2. Linear search

```python
def linear_search(items, target):
    for i, value in enumerate(items):
        if value == target:
            return i
    return -1

print(linear_search([4, 9, 2, 7], 2), linear_search([4, 9, 2, 7], 5))      # 2 -1
```

Python spells this `target in items` (membership) and `items.index(target)`; both are `O(n)` on a list. Use a `set` or `dict` for repeated lookups.

## 3. Binary search

Keep a window `[lo, hi]` that **must contain the target if it exists**. Look at the middle; discard the half that cannot contain the target.

```text
find 23 in [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
 lo=0 hi=9  mid=4  value 16  <  23 -> search the right half: lo=5
 lo=5 hi=9  mid=7  value 56  >  23 -> search the left half:  hi=6
 lo=5 hi=6  mid=5  value 23  == 23 -> found at index 5       (3 looks for 10 items)
```

```python
def binary_search(items, target):
    lo, hi = 0, len(items) - 1                   # invariant: if target is present, it lies in items[lo..hi]
    steps = 0
    while lo <= hi:
        steps += 1
        mid = lo + (hi - lo) // 2                # avoids overflow in languages with fixed-size ints
        if items[mid] == target:
            return mid, steps
        if items[mid] < target:
            lo = mid + 1                         # mid itself is ruled out, so skip past it
        else:
            hi = mid - 1
    return -1, steps

data = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
print(binary_search(data, 23))                   # (5, 3)
print(binary_search(data, 2), binary_search(data, 91))         # (0, 3) (9, 4)
print(binary_search(data, 40))                   # (-1, 4)
print(binary_search([], 1))                      # (-1, 0)
```

### Why it is correct: the loop invariant

> At the start of every iteration, if `target` is in the list at all, it is at an index in `[lo, hi]`.

- True at the start (the window is everything).
- Each step keeps it true: if `items[mid] < target`, then everything at or before `mid` is smaller (sorted), so the target must be after `mid`: `lo = mid + 1`. Symmetric for the other side.
- When the loop ends (`lo > hi`) the window is empty, so the target is absent.
- The window shrinks every iteration, so the loop ends, after about `log₂ n` rounds.

### The three classic bugs

```python
def buggy_search(items, target, max_steps=20):      # BUG: "lo = mid" instead of "lo = mid + 1"
    lo, hi = 0, len(items) - 1
    for step in range(max_steps):                    # the cap exists only so this demo ends
        if lo > hi:
            return -1
        mid = (lo + hi) // 2
        if items[mid] == target:
            return mid
        if items[mid] < target:
            lo = mid                                 # mid was already ruled out, but we keep it: no progress
        else:
            hi = mid - 1
    return f"no answer after {max_steps} steps (infinite loop)"

print(buggy_search([1, 3], 3))                       # no answer after 20 steps (infinite loop)
```

With `lo=0, hi=1` we get `mid=0`, `1 < 3`, so `lo` stays 0 forever: the window never shrinks.

- **Off-by-one window updates** (`lo = mid` or `hi = mid` with the wrong loop condition): infinite loops. Always make progress: use `mid + 1` / `mid - 1`, or the half-open style below with matching conditions.
- **Wrong loop condition** (`lo < hi` with inclusive bounds misses the last single candidate).
- **Overflow in `(lo + hi) // 2`** in C/Java (Python integers never overflow, but write `lo + (hi - lo) // 2` anyway: it is the habit that saved the JDK's `binarySearch` bug).

## 4. First and last occurrence, and the insertion point

With **duplicates**, plain binary search returns *some* match. Usually you want a boundary:

- **`lower_bound(x)`**: the first index whose value is `>= x` (where `x` would be inserted to go before its equals).
- **`upper_bound(x)`**: the first index whose value is `> x` (just after the last `x`).

```python
def lower_bound(items, x):
    lo, hi = 0, len(items)                       # half-open window [lo, hi): hi is one past the end
    while lo < hi:
        mid = (lo + hi) // 2
        if items[mid] < x:
            lo = mid + 1                         # mid is too small: answer is to the right
        else:
            hi = mid                             # mid could be the answer: keep it in the window
    return lo

def upper_bound(items, x):
    lo, hi = 0, len(items)
    while lo < hi:
        mid = (lo + hi) // 2
        if items[mid] <= x:
            lo = mid + 1
        else:
            hi = mid
    return lo

nums = [1, 2, 2, 2, 5, 8]
print(lower_bound(nums, 2), upper_bound(nums, 2))          # 1 4     (the 2s occupy indexes 1, 2, 3)
print(lower_bound(nums, 3), upper_bound(nums, 3))          # 4 4     (3 is absent: both give its insertion point)
print(lower_bound(nums, 0), lower_bound(nums, 9))          # 0 6

def count_occurrences(items, x):
    return upper_bound(items, x) - lower_bound(items, x)

def first_and_last(items, x):
    lo = lower_bound(items, x)
    if lo == len(items) or items[lo] != x:
        return (-1, -1)
    return (lo, upper_bound(items, x) - 1)

print(count_occurrences(nums, 2), first_and_last(nums, 2), first_and_last(nums, 3))      # 3 (1, 3) (-1, -1)
```

**The half-open template** (`while lo < hi`, `hi = mid`, `lo = mid + 1`) is the most reliable shape: it answers "**the first position where a condition becomes true**". Memorize it.

### Python's `bisect` does exactly this

```python
import bisect

print(bisect.bisect_left(nums, 2), bisect.bisect_right(nums, 2))        # 1 4   (lower_bound, upper_bound)
bisect.insort(nums, 3)                                                  # insert while keeping the list sorted
print(nums)                                                             # [1, 2, 2, 2, 3, 5, 8]

def grade(score, breakpoints=(60, 70, 80, 90), letters="FDCBA"):
    return letters[bisect.bisect(breakpoints, score)]                   # classic table-lookup use
print([grade(s) for s in (55, 60, 75, 89, 90, 100)])                    # ['F', 'D', 'C', 'B', 'A', 'A']

people = [("Ana", 25), ("Bo", 31), ("Cy", 40)]
print(bisect.bisect_left(people, 30, key=lambda p: p[1]))               # 1   (key= needs Python 3.10+)
```

## 5. Search in a rotated sorted array

A sorted list was rotated, such as `[6, 7, 8, 1, 2, 3, 4, 5]`. At least one half of every window is still sorted; use it to decide which half to keep.

```python
def search_rotated(items, target):
    lo, hi = 0, len(items) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if items[mid] == target:
            return mid
        if items[lo] <= items[mid]:                       # left half is sorted
            if items[lo] <= target < items[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:                                             # right half is sorted
            if items[mid] < target <= items[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1

rotated = [6, 7, 8, 1, 2, 3, 4, 5]
print(search_rotated(rotated, 3), search_rotated(rotated, 7), search_rotated(rotated, 9))      # 5 1 -1

def find_minimum_rotated(items):                          # the rotation point
    lo, hi = 0, len(items) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if items[mid] > items[hi]:
            lo = mid + 1                                  # the minimum is to the right of mid
        else:
            hi = mid
    return items[lo]
print(find_minimum_rotated(rotated))                      # 1
```

## 6. Search in a sorted 2D matrix

Rows sorted left to right, and each row's first value is greater than the previous row's last: treat the grid as one long sorted list.

```python
def search_matrix(matrix, target):
    rows, cols = len(matrix), len(matrix[0])
    lo, hi = 0, rows * cols - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        value = matrix[mid // cols][mid % cols]           # map the flat index back to row, column
        if value == target:
            return True
        if value < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return False

grid = [[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]]
print(search_matrix(grid, 16), search_matrix(grid, 13))   # True False
```

## 7. Measuring: binary search versus linear and hashing

```python
import random, time

n = 1_000_000
big = list(range(0, 2 * n, 2))                            # sorted even numbers
queries = [random.randrange(2 * n) for _ in range(2_000)]

def bench(fn):
    t = time.perf_counter()
    for q in queries:
        fn(q)
    return time.perf_counter() - t

as_set = set(big)
linear = bench(lambda q: q in big)
binary = bench(lambda q: bisect.bisect_left(big, q))
hashed = bench(lambda q: q in as_set)
print(linear > 100 * binary, hashed < binary * 2)         # True True
```

Binary search is thousands of times faster than a scan, and a hash set is faster still for pure membership. **Binary search wins when you need ordered answers** (nearest value, range counts, insertion point) or when you cannot afford the memory of a hash table.

## 8. Two real-world examples

**Example 1: `git bisect`.** A bug appeared somewhere in 1 000 commits. Git binary-searches the history: test the middle commit, mark good/bad, repeat. Ten tests find the culprit.

**Example 2: Autocomplete boundaries and database indexes.** Finding all words starting with "pre" in a sorted list is two binary searches (`lower_bound("pre")` and `lower_bound("prf")`); a database index narrows to the first matching row the same way.

## 9. Common mistakes

- Running binary search on **unsorted** data (silently wrong).
- `lo = mid` or `hi = mid` without a matching loop condition (infinite loop).
- `while lo < hi` combined with inclusive `hi = len - 1` (misses the last item).
- Returning "any match" when you needed the first or last (duplicates).
- Searching a `list` repeatedly with `in` when a `set` or `bisect` would do.
- Comparing with the wrong type or sort order (descending data needs reversed comparisons).

## 10. Practice

1. How many comparisons does binary search need (worst case) for 1000 items? For 1 000 000?
2. Trace `binary_search([1, 3, 5, 7, 9, 11], 9)` and write each `lo`, `hi`, `mid`.
3. What do `lower_bound` and `upper_bound` return on `[2, 4, 4, 6]` for `x = 4` and for `x = 5`?
4. Write `floor_search(items, x)` that returns the largest element `<= x` or `None`.
5. Write `insert_position(items, x)` (where to insert `x` to stay sorted).
6. Given `[3, 4, 5, 1, 2]`, find the minimum with the rotated-array method. Trace it.
7. Why is `lo + (hi - lo) // 2` preferred over `(lo + hi) // 2`?

<details>
<summary>Solutions</summary>

1. `ceil(log₂(1001)) = 10` and `ceil(log₂(1 000 001)) = 20`.
2. `lo=0 hi=5 mid=2 (5 < 9) -> lo=3`; `lo=3 hi=5 mid=4 (9 == 9)` found at index 4.
3. `x = 4`: `lower_bound = 1`, `upper_bound = 3`. `x = 5`: both are 3.
4. ```python
   def floor_search(items, x):
       i = upper_bound(items, x)
       return items[i - 1] if i else None
   print(floor_search([2, 4, 6, 8], 5), floor_search([2, 4, 6, 8], 1))      # 4 None
   ```
5. ```python
   def insert_position(items, x):
       return lower_bound(items, x)
   print(insert_position([1, 3, 5], 4), insert_position([1, 3, 5], 9))      # 2 3
   ```
6. `lo=0 hi=4 mid=2 (5 > 2) -> lo=3`; `lo=3 hi=4 mid=3 (1 <= 2) -> hi=3`; stop: `items[3] = 1`.
   ```python
   print(find_minimum_rotated([3, 4, 5, 1, 2]))          # 1
   ```
7. In fixed-width integer languages `lo + hi` can overflow; `hi - lo` cannot. (Python is safe, but the habit transfers to Java, C and C++.)

</details>

## 11. Check yourself

1. What must be true of the data for binary search to work?
2. What is the loop invariant of binary search?
3. How do you find the first occurrence among duplicates?
4. Why is the half-open template (`hi = mid`, `lo = mid + 1`) reliable?
5. When would you pick a `set` over binary search?

<details>
<summary>Answers</summary>

1. It must be sorted (or at least monotonic with respect to the question you ask).
2. If the target exists, it lies within the current window `[lo, hi]`.
3. Use `lower_bound`: the first index with value `>= x`, then check it equals `x`.
4. Every iteration strictly shrinks the window and the answer always remains inside it.
5. For plain membership tests when order is irrelevant: `O(1)` average.

</details>

[Back to searching](README.md) · Next: [binary search on the answer](02-binary-search-on-the-answer.md)
