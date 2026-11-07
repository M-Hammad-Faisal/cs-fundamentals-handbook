# Sorting

## Detailed lessons (start here if you are new)

1. [Sorting basics and elementary sorts](01-sorting-basics-and-elementary-sorts.md): vocabulary, stability, bubble, selection, insertion
2. [Merge sort and quicksort](02-merge-sort-and-quicksort.md): divide and conquer, pivots, quickselect, inversions
3. [Linear-time sorts and Timsort](03-linear-time-sorts-and-timsort.md): counting, radix, bucket, choosing a sort

The rest of this page is the quick reference.

## 1. The concept

**Sorting** arranges items in a defined order. It matters far beyond "show a sorted list": sorted data enables binary search, fast duplicate detection, merging, grouping, and many other algorithms.

### Properties to know

| Property | Meaning |
|----------|---------|
| **Stable** | Equal items keep their original relative order |
| **In place** | Uses `O(1)` (or `O(log n)`) extra memory |
| **Comparison-based** | Decides order only by comparing pairs; cannot beat `O(n log n)` in the worst case |
| **Adaptive** | Runs faster on nearly sorted input |

Stability matters when you sort by one field after another (sort by name, then stably by department).

## 2. The simple sorts: `O(n²)`

### Bubble sort

Repeatedly swap adjacent out-of-order pairs; the largest item "bubbles" to the end each pass.

```python
def bubble_sort(a):
    n = len(a)
    for i in range(n):
        swapped = False
        for j in range(n - 1 - i):
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
        if not swapped:             # already sorted: stop early
            break
    return a
```

### Selection sort

Find the minimum of the unsorted part and put it next. Always `O(n²)` but does at most `n - 1` swaps (useful when writes are expensive).

```python
def selection_sort(a):
    for i in range(len(a)):
        m = min(range(i, len(a)), key=a.__getitem__)
        a[i], a[m] = a[m], a[i]
    return a
```

### Insertion sort

Build a sorted prefix by inserting each next item into place, like sorting playing cards in your hand. Excellent on small or nearly sorted data.

```python
def insertion_sort(a):
    for i in range(1, len(a)):
        key, j = a[i], i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a
```

## 3. The efficient sorts: `O(n log n)`

### Merge sort (divide and conquer)

Split in half, sort each half recursively, merge the two sorted halves.

```python
def merge_sort(a):
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    left, right = merge_sort(a[:mid]), merge_sort(a[mid:])
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:             # <= keeps it stable
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    out.extend(left[i:]); out.extend(right[j:])
    return out
```

Recurrence `T(n) = 2T(n/2) + O(n)` gives `O(n log n)` in **every** case. It needs `O(n)` extra space. It is stable and the basis of **external sorting** (data larger than RAM).

### Quick sort

Choose a **pivot**, partition into smaller and larger items, recurse on both sides.

```python
import random

def quick_sort(a, lo=0, hi=None):
    if hi is None:
        hi = len(a) - 1
    if lo < hi:
        p = partition(a, lo, hi)
        quick_sort(a, lo, p - 1)
        quick_sort(a, p + 1, hi)
    return a

def partition(a, lo, hi):
    r = random.randint(lo, hi)              # random pivot avoids the worst case
    a[r], a[hi] = a[hi], a[r]
    pivot, i = a[hi], lo
    for j in range(lo, hi):
        if a[j] < pivot:
            a[i], a[j] = a[j], a[i]
            i += 1
    a[i], a[hi] = a[hi], a[i]
    return i
```

Average `O(n log n)`, worst `O(n²)` (bad pivots on sorted input with a naive pivot). In place, **not stable**, and usually the fastest in practice because of cache-friendly access. Handle many duplicates with 3-way partitioning.

### Heap sort

Build a max-heap, then repeatedly move the maximum to the end. `O(n log n)` always, `O(1)` extra space, not stable. See [heaps](../../02-data-structures/heaps/README.md).

### Timsort: what Python actually uses

`list.sort()` and `sorted()` use **Timsort**: a hybrid of merge sort and insertion sort that detects existing sorted "runs" in the data and merges them. It is stable, `O(n log n)` worst case, and `O(n)` on already sorted data.

```python
sorted(items, key=lambda p: p.age)                # new list
items.sort(key=lambda p: (p.dept, -p.salary))     # in place, multi-key
sorted(words, key=str.lower, reverse=True)
```

## 4. Non-comparison sorts: beating `n log n`

They exploit the structure of the keys instead of comparing.

### Counting sort

For integers in a small range `0..k`: count occurrences, then rebuild. `O(n + k)`.

```python
def counting_sort(a, k):
    counts = [0] * (k + 1)
    for x in a:
        counts[x] += 1
    out = []
    for value, c in enumerate(counts):
        out.extend([value] * c)
    return out
```

### Radix sort

Sort by each digit using a stable sort, least significant digit first. `O(d * (n + b))` for `d` digits in base `b`.

### Bucket sort

Distribute values into buckets by range, sort each bucket, concatenate. Great for uniformly distributed floats.

## 5. Comparison table

| Algorithm | Best | Average | Worst | Space | Stable |
|-----------|------|---------|-------|-------|--------|
| Bubble | `O(n)` | `O(n²)` | `O(n²)` | `O(1)` | Yes |
| Selection | `O(n²)` | `O(n²)` | `O(n²)` | `O(1)` | No |
| Insertion | `O(n)` | `O(n²)` | `O(n²)` | `O(1)` | Yes |
| Merge | `O(n log n)` | `O(n log n)` | `O(n log n)` | `O(n)` | Yes |
| Quick | `O(n log n)` | `O(n log n)` | `O(n²)` | `O(log n)` | No |
| Heap | `O(n log n)` | `O(n log n)` | `O(n log n)` | `O(1)` | No |
| Timsort | `O(n)` | `O(n log n)` | `O(n log n)` | `O(n)` | Yes |
| Counting | `O(n + k)` | `O(n + k)` | `O(n + k)` | `O(k)` | Yes |
| Radix | `O(d(n + b))` | same | same | `O(n + b)` | Yes |

## 6. Useful related techniques

### Quickselect: k-th smallest in average `O(n)`

```python
def quickselect(a, k):                  # k is 0-based
    lo, hi = 0, len(a) - 1
    while True:
        p = partition(a, lo, hi)
        if p == k:
            return a[p]
        if p < k:
            lo = p + 1
        else:
            hi = p - 1
```

### Sort by custom keys

```python
people.sort(key=lambda p: (p["dept"], -p["salary"], p["name"]))
```

Negate numbers to reverse one field while keeping others ascending.

### Merge intervals (sort, then sweep)

```python
def merge_intervals(intervals):
    out = []
    for s, e in sorted(intervals):
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out
```

### Dutch national flag (3-way partition)

```python
def sort_colors(a):                     # values 0, 1, 2 in one pass, O(1) space
    lo, mid, hi = 0, 0, len(a) - 1
    while mid <= hi:
        if a[mid] == 0:
            a[lo], a[mid] = a[mid], a[lo]; lo += 1; mid += 1
        elif a[mid] == 1:
            mid += 1
        else:
            a[mid], a[hi] = a[hi], a[mid]; hi -= 1
    return a
```

## 7. Two real-world examples

### Example 1: Database query execution

`ORDER BY`, `GROUP BY`, `DISTINCT`, and sort-merge joins all rely on sorting. When a result set does not fit in memory, the database performs an **external merge sort**: sort chunks that fit in RAM, write them to disk as runs, then merge the runs. Indexes (B-trees) keep data pre-sorted so `ORDER BY` can skip the sort entirely, which is one reason indexes speed up queries.

### Example 2: Leaderboards and log processing

A game leaderboard sorts scores, but only needs the **top 100** of millions: a heap or quickselect beats a full sort. Distributed systems like MapReduce and Spark sort huge datasets by sorting partitions locally and merging. Log analysis often sorts events by timestamp across many servers, then sweeps through them once, which is why stable sorting by timestamp then by source matters.

## 8. Tips, tricks and pitfalls

- **Use the built-in sort.** `sorted` and `list.sort` (Timsort) beat hand-written code. Write your own only to show you understand it.
- **`key=` beats `cmp`.** The key function runs once per element; in Python 3 use `functools.cmp_to_key` only if you truly need a comparator.
- **Stability enables multi-pass sorting:** sort by the least significant key first, then the next.
- **Pick the sort by constraints:** small `n` or nearly sorted → insertion; guaranteed `O(n log n)` and stability → merge; tight memory → heap or quick; small integer range → counting.
- **Random pivots** (or median-of-three) avoid quicksort's worst case.
- **Only need the top K or the median?** Use a heap or quickselect, not a full sort.
- **`list.sort()` returns `None`.** `x = a.sort()` is a classic bug.
- **Mixed types do not sort** in Python 3 (`TypeError`).
- **Sorting is the fix for many `O(n²)` problems:** sort, then two pointers or a single sweep.

## 9. Check yourself

1. What does "stable" mean and when does it matter?
2. Why can no comparison sort beat `O(n log n)` in the worst case?
3. Why is quicksort often faster than merge sort in practice despite a worse worst case?
4. Which sorts are best for nearly sorted data, and why?
5. When can you sort in `O(n)`?
6. What algorithm does Python use, and what are its guarantees?
7. How do you find the k-th smallest element without fully sorting?
8. How do you sort by department ascending and salary descending?

<details>
<summary>Answers</summary>

1. Equal elements keep their original relative order. It matters for multi-key sorting and when the records carry other data.
2. There are `n!` orderings, and each comparison gives one bit, so you need at least `log₂(n!)` which is `Θ(n log n)` comparisons.
3. Quicksort works in place with sequential, cache-friendly memory access and small constants; random pivots make the worst case very unlikely.
4. Insertion sort and Timsort: they exploit existing order (`O(n)` on sorted input).
5. When keys are small integers or have bounded structure: counting, radix, or bucket sort.
6. Timsort: stable, `O(n log n)` worst case, `O(n)` on sorted data, `O(n)` extra space.
7. Quickselect (average `O(n)`) or a size-k heap (`O(n log k)`).
8. `items.sort(key=lambda p: (p.dept, -p.salary))`.

</details>
