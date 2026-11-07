# Merge Sort and Quicksort

**Prerequisites:** [elementary sorts](01-sorting-basics-and-elementary-sorts.md), [recursion and recurrences](../../01-complexity/04-analyzing-loops-and-recursion.md). **You will learn:** the **divide and conquer** idea, **merge sort** (guaranteed `O(n log n)`, stable), **quicksort** (fastest in practice, in place), how pivots are chosen, why quicksort can degrade to `O(n²)`, and how to measure the difference.

## 1. In plain words: divide and conquer

Sorting 1000 cards is hard; sorting 1 card is trivial. **Divide and conquer** splits a big problem into smaller copies of itself, solves those (recursively), and combines the answers.

- **Merge sort:** the *splitting is easy* (cut in half) and the *combining is the work* (merge two sorted halves).
- **Quicksort:** the *splitting is the work* (partition around a pivot) and the *combining is free*.

## 2. Merge sort

```text
[38, 27, 43, 3]
 split:   [38, 27]        [43, 3]
 split:   [38] [27]       [43] [3]          single items are sorted
 merge:   [27, 38]        [3, 43]
 merge:   [3, 27, 38, 43]
```

**Merging** two sorted lists: keep a pointer in each; repeatedly take the smaller front item.

```text
[27, 38]  [3, 43]   take 3   -> [3]
[27, 38]  [43]      take 27  -> [3, 27]
[38]      [43]      take 38  -> [3, 27, 38]
[]        [43]      take 43  -> [3, 27, 38, 43]
```

```python
def merge(left, right, stats):
    result, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        stats["comparisons"] += 1
        if left[i] <= right[j]:                  # <= takes from the left on ties: that keeps the sort STABLE
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])                      # one side ran out: append the rest of the other
    result.extend(right[j:])
    return result

def merge_sort(a, stats=None):
    stats = stats if stats is not None else {"comparisons": 0}
    if len(a) <= 1:
        return list(a)
    mid = len(a) // 2
    return merge(merge_sort(a[:mid], stats), merge_sort(a[mid:], stats), stats)

print(merge_sort([38, 27, 43, 3, 9, 82, 10]))            # [3, 9, 10, 27, 38, 43, 82]
print(merge_sort([]), merge_sort([5]))                   # [] [5]
```

**Why `O(n log n)`:** the list is halved `log₂ n` times (the recursion depth), and each level of the recursion merges a total of `n` items. So `n` work per level times `log n` levels. Recurrence: `T(n) = 2T(n/2) + n`.

```python
import random

random.seed(1)
for n in (1_000, 10_000, 100_000):
    stats = {"comparisons": 0}
    merge_sort(random.sample(range(n * 10), n), stats)
    print(n, stats["comparisons"], round(stats["comparisons"] / (n * __import__("math").log2(n)), 2))
# 1000 8715 0.87
# 10000 120377 0.91
# 100000 1535940 0.92
```

The comparison count tracks `n log₂ n` (the ratio stays near 0.9), not `n²`: multiplying `n` by 10 multiplies work by about 13, not 100.

**Properties:** time `O(n log n)` in **every** case; space `O(n)` extra; **stable**. It is also ideal for **linked lists** and **data too large for memory** (sort chunks, then merge: *external sorting*).

## 3. Quicksort

**Idea:** pick a **pivot**; rearrange so everything smaller is on its left and everything larger is on its right (**partition**). The pivot is now in its final place. Recursively sort the two sides.

```text
[7, 2, 9, 4, 3, 8]   pivot = 7
 smaller: [2, 4, 3]   pivot: 7   larger: [9, 8]
 sort each side:  [2, 3, 4]  7  [8, 9]   ->  [2, 3, 4, 7, 8, 9]
```

### Simple version (easy to read, extra memory)

```python
def quicksort_simple(a):
    if len(a) <= 1:
        return list(a)
    pivot = a[len(a) // 2]
    smaller = [x for x in a if x < pivot]
    equal = [x for x in a if x == pivot]
    larger = [x for x in a if x > pivot]
    return quicksort_simple(smaller) + equal + quicksort_simple(larger)

print(quicksort_simple([7, 2, 9, 4, 3, 8, 7]))           # [2, 3, 4, 7, 7, 8, 9]
```

### In-place version with Lomuto partition

```python
def quicksort(a, lo=0, hi=None, stats=None):
    a = a if hi is not None else list(a)                 # copy once at the top-level call
    hi = len(a) - 1 if hi is None else hi
    stats = stats if stats is not None else {"comparisons": 0}
    if lo < hi:
        p = partition(a, lo, hi, stats)
        quicksort(a, lo, p - 1, stats)
        quicksort(a, p + 1, hi, stats)
    return a

def partition(a, lo, hi, stats):
    mid = (lo + hi) // 2                                  # use the middle element as pivot: safe on sorted input
    a[mid], a[hi] = a[hi], a[mid]                         # park it at the end so the loop below can ignore it
    pivot, boundary = a[hi], lo                           # boundary: everything before it is < pivot
    for i in range(lo, hi):
        stats["comparisons"] += 1
        if a[i] < pivot:
            a[i], a[boundary] = a[boundary], a[i]
            boundary += 1
    a[boundary], a[hi] = a[hi], a[boundary]               # put the pivot between the two parts
    return boundary

print(quicksort([7, 2, 9, 4, 3, 8, 7]))                  # [2, 3, 4, 7, 7, 8, 9]
```

Partition trace on `[7, 2, 9, 4, 3, 8]` when the pivot is already parked at the end (8), boundary starts at 0:

```text
i=0: 7 < 8  swap with boundary(0): [7,2,9,4,3,8] boundary=1
i=1: 2 < 8  swap with boundary(1): [7,2,9,4,3,8] boundary=2
i=2: 9 >= 8 nothing
i=3: 4 < 8  swap with index 2:     [7,2,4,9,3,8] boundary=3
i=4: 3 < 8  swap with index 3:     [7,2,4,3,9,8] boundary=4
finally swap pivot into index 4:   [7,2,4,3,8,9]   pivot 8 is in its final position
```

### Cost: it depends on the pivots

- **Good pivots** (near the median): each level splits roughly in half, depth `log n`, total **`O(n log n)`**.
- **Bad pivots** (always the smallest or largest): one side is empty, depth `n`, total **`O(n²)`**. A naive "last element" pivot on an already-sorted list does exactly this.

Defenses: pick a **random** pivot, or the **median of three** (first, middle, last), or the **introsort** hybrid (C++ `std::sort`: quicksort that switches to heapsort if recursion gets too deep).

## 4. Seeing the difference

```python
import sys
sys.setrecursionlimit(10_000)

def quicksort_naive_last(a, stats):
    if len(a) <= 1:
        return list(a)
    pivot, rest = a[-1], a[:-1]
    stats["comparisons"] += len(rest)
    return (quicksort_naive_last([x for x in rest if x < pivot], stats) + [pivot] +
            quicksort_naive_last([x for x in rest if x >= pivot], stats))

def quicksort_random(a, stats):
    if len(a) <= 1:
        return list(a)
    pivot = a[random.randrange(len(a))]
    stats["comparisons"] += len(a)
    return (quicksort_random([x for x in a if x < pivot], stats) + [x for x in a if x == pivot] +
            quicksort_random([x for x in a if x > pivot], stats))

n = 800
random.seed(3)
for label, data in [("random", random.sample(range(10_000), n)), ("already sorted", list(range(n)))]:
    s1, s2 = {"comparisons": 0}, {"comparisons": 0}
    quicksort_naive_last(data, s1); quicksort_random(data, s2)
    print(f"{label:15} naive-last={s1['comparisons']:7}  random-pivot={s2['comparisons']:6}")
# random          naive-last=   8161  random-pivot=   8292
# already sorted  naive-last= 319600  random-pivot=   8477
```

On sorted input the naive pivot does about `n²/2` comparisons (319 600 for 800 items) while the random pivot stays near `n log n` (about 8500).

## 5. Comparison

| | Merge sort | Quicksort | Heapsort |
|---|-----------|-----------|----------|
| Time (best / average) | `O(n log n)` | `O(n log n)` | `O(n log n)` |
| Time (worst) | `O(n log n)` | `O(n²)` (rare with good pivots) | `O(n log n)` |
| Extra space | `O(n)` | `O(log n)` stack | `O(1)` |
| Stable | **yes** | no | no |
| Cache behavior | good (sequential) | **excellent** | poor |
| Best for | linked lists, external sorting, need stability | general in-memory arrays | guaranteed worst case, tiny memory |

## 6. Related: quickselect (the k-th smallest without a full sort)

If you only need the median or the 5th smallest, partition once and recurse into **only one side**: average `O(n)`.

```python
def quickselect(a, k):                                   # k-th smallest, 0-based
    a = list(a)
    while True:
        pivot = random.choice(a)
        smaller = [x for x in a if x < pivot]
        equal = [x for x in a if x == pivot]
        if k < len(smaller):
            a = smaller
        elif k < len(smaller) + len(equal):
            return pivot
        else:
            k -= len(smaller) + len(equal)
            a = [x for x in a if x > pivot]

data = [9, 1, 8, 2, 7, 3, 6, 4, 5]
print(quickselect(data, 0), quickselect(data, 4), quickselect(data, 8))      # 1 5 9
```

## 7. Counting inversions with merge sort (a classic)

During the merge, every time a right-half item is taken **before** remaining left-half items, it forms an inversion with each of them.

```python
def count_inversions(a):
    if len(a) <= 1:
        return list(a), 0
    mid = len(a) // 2
    left, x = count_inversions(a[:mid])
    right, y = count_inversions(a[mid:])
    merged, i, j, cross = [], 0, 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i]); i += 1
        else:
            merged.append(right[j]); j += 1
            cross += len(left) - i                        # right[j] jumped over every remaining left item
    merged += left[i:] + right[j:]
    return merged, x + y + cross

print(count_inversions([2, 4, 1, 3, 5])[1], count_inversions([5, 4, 3, 2, 1])[1])      # 3 10
```

## 8. Two real-world examples

**Example 1: Sorting a file larger than RAM.** Read and sort chunks that fit in memory, write each to disk, then do a **k-way merge** of the chunks (the merge step of merge sort, using a [heap](../../02-data-structures/heaps/02-priority-queue-applications.md)). Databases and `sort` on Unix work this way.

**Example 2: Standard libraries.** C++ `std::sort` is introsort (quicksort + heapsort + insertion sort); Python and Java (for objects) use Timsort (a merge-sort/insertion-sort hybrid); Go uses pattern-defeating quicksort.

## 9. Common mistakes

- Merge sort that copies slices at every level without realizing the `O(n)` extra space.
- Using `<` instead of `<=` in merge (breaks stability).
- Quicksort with a fixed first/last pivot on sorted or nearly sorted data.
- Not handling duplicates (a partition that sends all equal items to one side degrades to `O(n²)`; use three-way partition or the `equal` list).
- Recursion depth on adversarial input (always recurse into the smaller side first, or use iteration).
- Forgetting the base case (`len <= 1`).

## 10. Practice

1. Merge `[1, 4, 9]` and `[2, 3, 10]` by hand. How many comparisons?
2. What is the recursion depth of merge sort on 1024 items?
3. Quicksort with last-element pivot is given `[1, 2, 3, 4]`. What happens?
4. Which sort would you choose for sorting a linked list? Why?
5. Write `merge_sort_desc`.
6. Use `quickselect` to find the median of `[7, 1, 5, 3, 9]`.
7. Why does quicksort usually beat merge sort in practice despite the worse worst case?

<details>
<summary>Solutions</summary>

1. Result `[1, 2, 3, 4, 9, 10]`; comparisons: 1v2, 4v2, 4v3, 4v10, 9v10 = **5** (then `[10]` is appended).
2. `log₂ 1024 = 10` levels of splitting.
3. Each pivot is the maximum, so every partition has an empty right side: `n` levels, about `n²/2` comparisons.
4. Merge sort: it needs only sequential access, merges linked lists in `O(1)` extra space, and is stable.
5. ```python
   def merge_sort_desc(a):
       if len(a) <= 1: return list(a)
       mid = len(a) // 2
       left, right = merge_sort_desc(a[:mid]), merge_sort_desc(a[mid:])
       out, i, j = [], 0, 0
       while i < len(left) and j < len(right):
           if left[i] >= right[j]: out.append(left[i]); i += 1
           else: out.append(right[j]); j += 1
       return out + left[i:] + right[j:]
   print(merge_sort_desc([3, 1, 4, 1, 5]))               # [5, 4, 3, 1, 1]
   ```
6. ```python
   print(quickselect([7, 1, 5, 3, 9], 2))                # 5
   ```
7. It works in place on contiguous memory (cache friendly), has small constants, and with random pivots the worst case is astronomically unlikely.

</details>

## 11. Check yourself

1. What are the divide, conquer and combine steps of merge sort?
2. Why is merge sort `O(n log n)` in every case?
3. What makes quicksort degrade to `O(n²)`?
4. Name three ways to choose a better pivot.
5. Which is stable: merge sort or quicksort?
6. What is quickselect for?

<details>
<summary>Answers</summary>

1. Divide: split in half. Conquer: sort each half recursively. Combine: merge the sorted halves.
2. Always `log n` levels of splitting and `n` work of merging per level.
3. Consistently unbalanced partitions (e.g. a sorted input with a fixed end pivot).
4. Random pivot, median of three, introsort fallback to heapsort (also three-way partitioning for duplicates).
5. Merge sort (with `<=`).
6. Finding the k-th smallest (median, percentiles) in average `O(n)` without a full sort.

</details>

[Back to sorting](README.md) · Previous: [elementary sorts](01-sorting-basics-and-elementary-sorts.md) · Next: [linear-time sorts and Timsort](03-linear-time-sorts-and-timsort.md)
