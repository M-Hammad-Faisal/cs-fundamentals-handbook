# Sorting: One-Page Summary

## Key facts

### Properties

**Stable** (equal items keep order) · **in place** (`O(1)` extra) · **comparison-based** (`Ω(n log n)` worst case) · **adaptive** (fast on nearly sorted).

### Algorithms

| Algorithm | Avg | Worst | Space | Stable | Notes |
|-----------|-----|-------|-------|--------|-------|
| Bubble / insertion | `O(n²)` | `O(n²)` | `O(1)` | Yes | Insertion is great for small or nearly sorted data |
| Selection | `O(n²)` | `O(n²)` | `O(1)` | No | Fewest swaps |
| Merge | `O(n log n)` | `O(n log n)` | `O(n)` | Yes | External sorting, linked lists |
| Quick | `O(n log n)` | `O(n²)` | `O(log n)` | No | Fast in practice; random pivot |
| Heap | `O(n log n)` | `O(n log n)` | `O(1)` | No | Guaranteed, in place |
| **Timsort** (Python) | `O(n log n)` | `O(n log n)` | `O(n)` | Yes | `O(n)` on sorted input |
| Counting / radix / bucket | `O(n + k)` | | | Yes | Small integer ranges |

### Tricks

- `sorted(x, key=...)`, `list.sort()` (returns `None`), negate numbers to reverse one key.
- **Quickselect** for k-th element in average `O(n)`; heap for top-K.
- **Sort then sweep/two pointers** (intervals, meeting rooms, 3-sum).
- **Dutch flag** 3-way partition in one pass.
- Merge sort counts **inversions**.

## Pitfalls

- `x = a.sort()` gives `None`.
- Mixed types raise `TypeError`.
- Naive quicksort pivots on sorted input.
- Forgetting stability when sorting by several keys.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Sorting Basics and the Elementary Sorts](01-sorting-basics-and-elementary-sorts.md) · [Merge Sort and Quicksort](02-merge-sort-and-quicksort.md) · [Linear-Time Sorts, Timsort and Choosing a Sort](03-linear-time-sorts-and-timsort.md)
