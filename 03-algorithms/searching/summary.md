# Searching: One-Page Summary

## Key facts

### Choose by data shape

| Data | Method | Time |
|------|--------|------|
| Unsorted | Linear | `O(n)` |
| Sorted array | Binary | `O(log n)` |
| Hash table | Hash lookup | `O(1)` average |
| BST / B-tree | Descent | `O(log n)` |
| Graph | BFS / DFS | `O(V + E)` |

### Binary search

- Needs **sorted** data or a **monotonic predicate** and random access.
- Template (half-open): `lo, hi = 0, n`; `while lo < hi`; `mid = (lo+hi)//2`; either `lo = mid + 1` or `hi = mid`.
- `bisect_left` = first `>= x`; `bisect_right` = first `> x`. Count = right - left.
- Use the upper mid `(lo+hi+1)//2` when assigning `lo = mid`.

### Patterns

- **Search on the answer:** min capacity, min speed, split array, sqrt (monotonic feasibility check).
- **Rotated array:** one half is always sorted.
- **Peak element:** move toward the larger neighbour.
- **2D matrix:** flatten the index (`i // n`, `i % n`).
- **Galloping search** for unknown size; **interpolation** for uniform data.
- String search: KMP, Rabin-Karp, Boyer-Moore.

## Pitfalls

- Off-by-one and infinite loops.
- Using it on unsorted data.
- Duplicates: decide first/last/any match.
- Float equality: loop a fixed number of times.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Linear Search and Binary Search](01-linear-and-binary-search.md) · [Binary Search on the Answer and Other Search Techniques](02-binary-search-on-the-answer.md)
