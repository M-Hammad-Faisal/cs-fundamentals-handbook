# Searching

## Detailed lessons

1. [Linear and binary search](01-linear-and-binary-search.md): invariants, boundaries, `bisect`, rotated arrays, matrices
2. [Binary search on the answer](02-binary-search-on-the-answer.md): feasibility templates, classic problems, other searches

The rest of this page is the quick reference.

## 1. The concept

**Searching** finds an item, or its position, in a collection. The right method depends on how the data is organized.

| Data | Method | Time |
|------|--------|------|
| Unordered list | Linear search | `O(n)` |
| Sorted array | Binary search | `O(log n)` |
| Hash table | Hash lookup | `O(1)` average |
| BST / B-tree | Tree descent | `O(log n)` |
| Graph | BFS / DFS | `O(V + E)` |

## 2. Linear search

Check items one by one until found.

```python
def linear_search(a, target):
    for i, x in enumerate(a):
        if x == target:
            return i
    return -1                   # O(n) worst case
```

Use it when the data is unsorted, tiny, or you search only once (sorting first would cost more).

## 3. Binary search

On a **sorted** array, compare with the middle and discard half each step.

```python
def binary_search(a, target):
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2          # avoids overflow in fixed-width languages
        if a[mid] == target:
            return mid
        if a[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1                              # O(log n) time, O(1) space
```

A million items takes about 20 comparisons; a billion about 30.

### Leftmost and rightmost occurrence

```python
def lower_bound(a, target):                # first index with a[i] >= target
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo

def upper_bound(a, target):                # first index with a[i] > target
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] <= target:
            lo = mid + 1
        else:
            hi = mid
    return lo

# count of target = upper_bound(a, t) - lower_bound(a, t)
```

These match `bisect.bisect_left` and `bisect.bisect_right` in Python's standard library:

```python no-run
import bisect
bisect.bisect_left(a, x)            # lower_bound
bisect.bisect_right(a, x)           # upper_bound
bisect.insort(a, x)                 # insert keeping sorted (O(n) due to shifting)
```

### The half-open template (fewer off-by-one bugs)

Use the invariant `answer in [lo, hi)`, loop `while lo < hi`, and set either `lo = mid + 1` or `hi = mid`. This one template handles most variants.

## 4. Binary search on the answer

You can binary search not just on arrays but on **any monotonic yes/no condition**: "is the answer at least `x`?" flips from false to true exactly once.

### Smallest capacity that ships all packages within D days

```python
def ship_within_days(weights, days):
    def feasible(cap):
        d, load = 1, 0
        for w in weights:
            if load + w > cap:
                d, load = d + 1, 0
            load += w
        return d <= days

    lo, hi = max(weights), sum(weights)
    while lo < hi:
        mid = (lo + hi) // 2
        if feasible(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo
```

### Integer square root

```python
def isqrt(n):
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if mid * mid <= n:
            lo = mid
        else:
            hi = mid - 1
    return lo
```

Note `mid = (lo + hi + 1) // 2` when you move `lo = mid` to avoid an infinite loop.

## 5. Variants

### Rotated sorted array

```python
def search_rotated(a, target):
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if a[mid] == target:
            return mid
        if a[lo] <= a[mid]:                          # left half is sorted
            if a[lo] <= target < a[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:                                        # right half is sorted
            if a[mid] < target <= a[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1
```

### Peak element

```python
def find_peak(a):
    lo, hi = 0, len(a) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < a[mid + 1]:
            lo = mid + 1            # a peak exists to the right
        else:
            hi = mid
    return lo
```

### Search a sorted 2D matrix

Treat an `m x n` matrix with sorted rows and the first element of each row greater than the last of the previous as one array of length `m*n`; index `i` maps to `matrix[i // n][i % n]`.

### Exponential (galloping) search

For unbounded or very large sorted data: double the index until you overshoot, then binary search that range. `O(log n)`; useful when the size is unknown.

### Interpolation search

Estimate the position from the value (like finding "Smith" near the end of a phone book). `O(log log n)` on uniformly distributed data, `O(n)` worst case.

## 6. Searching in other structures

- **Hash table:** `O(1)` average for exact match ([hash tables](../../02-data-structures/hash-tables/README.md)).
- **BST / B-tree:** descend left or right ([trees](../../02-data-structures/trees/README.md)).
- **Trie:** prefix search in `O(L)` ([tries](../../02-data-structures/tries/README.md)).
- **Graphs:** BFS/DFS ([graphs](../../02-data-structures/graphs/README.md)).
- **String search:** naive `O(n*m)`; **KMP**, **Rabin-Karp** and **Boyer-Moore** run in about `O(n + m)`. Python's `in` on strings is well optimized.

## 7. Two real-world examples

### Example 1: Database index lookups and `git bisect`

A B-tree index lets a database find one row among hundreds of millions by repeatedly narrowing the key range, the same halving idea as binary search, with high fan-out per node. **`git bisect`** applies binary search to your commit history: given a "good" and a "bad" commit, it tests the middle commit, then halves the range, finding the commit that introduced a bug among 1,000 commits in about 10 tests. Any "find the first version where X broke" problem is binary search on a monotonic condition.

### Example 2: Capacity planning and rate tuning

"What is the minimum number of servers that keeps 99% of requests under 200 ms?" Performance rises monotonically with capacity, so you can binary search the answer by running a simulation or load test at the midpoint. The same applies to finding the smallest timeout, batch size, or memory limit that satisfies a requirement. It turns a hard optimization into about 20 cheap yes/no checks.

## 8. Tips, tricks and pitfalls

- **Binary search needs sorted data** (or a monotonic predicate). Sorting first costs `O(n log n)`; only worth it for many searches.
- **Off-by-one errors** are the main bug. Pick one template (`lo < hi` with half-open ranges) and use it consistently.
- **Infinite loops** happen when `mid` can equal `lo` and you assign `lo = mid`; use the upper mid.
- **Use `bisect`** in real code; it is correct and fast.
- **Duplicates:** decide whether you want any match, the first, or the last, and use `lower_bound`/`upper_bound`.
- **Overflow:** `(lo + hi) // 2` is safe in Python (big integers) but overflows in C/Java; use `lo + (hi - lo) // 2` there.
- **Floating-point binary search:** loop a fixed number of times (such as 100) instead of comparing floats for equality.
- **Think "search on the answer"** whenever a problem asks for a minimum or maximum value that satisfies a condition, and checking one candidate is easy.

## 9. Check yourself

1. Why is binary search `O(log n)`?
2. What are the preconditions for binary search?
3. How do you find the first and last position of a value in a sorted array with duplicates?
4. What does "binary search on the answer" mean? Give an example.
5. How do you search a rotated sorted array in `O(log n)`?
6. What is the difference between `bisect_left` and `bisect_right`?
7. Why might you prefer linear search for a one-off search on unsorted data?

<details>
<summary>Answers</summary>

1. Each comparison discards half of the remaining items, so about `log₂ n` steps remain until one is left.
2. The data must be sorted (or the predicate monotonic) and support `O(1)` random access.
3. Use `lower_bound` for the first index and `upper_bound - 1` for the last; they differ in whether equal values go left or right.
4. Binary search a numeric range of candidate answers using a monotonic feasibility check, e.g. the minimum ship capacity that meets a deadline.
5. At each step one half is sorted; check whether the target lies within the sorted half to decide which half to keep.
6. `bisect_left` returns the first insertion point (before equal items); `bisect_right` returns the point after all equal items.
7. Sorting costs `O(n log n)`, more than one `O(n)` scan; binary search only pays off when you search many times.

</details>

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

Back to the [part overview](../README.md).
