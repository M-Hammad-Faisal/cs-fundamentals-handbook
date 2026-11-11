# Divide and Conquer: One-Page Summary

## Quick reference

| Algorithm | Recurrence | Cost |
|-----------|-----------|------|
| Binary search | `T(n) = T(n/2) + 1` | `O(log n)` |
| Merge sort | `T(n) = 2T(n/2) + n` | `O(n log n)` |
| Karatsuba multiplication | `T(n) = 3T(n/2) + n` | `O(n^1.585)` |
| Strassen matrix multiplication | `T(n) = 7T(n/2) + n^2` | `O(n^2.807)` |
| Closest pair of points | `T(n) = 2T(n/2) + n log n` (simple) | `O(n log^2 n)`, `O(n log n)` tuned |
| Fast Fourier transform | `T(n) = 2T(n/2) + n` | `O(n log n)` |

**Master theorem** for `T(n) = aT(n/b) + n^d` with `c = log_b a`: `d < c` gives `n^c`; `d = c` gives `n^d log n`; `d > c` gives `n^d`.

Related: [sorting](../sorting/02-merge-sort-and-quicksort.md), [binary search](../searching/01-linear-and-binary-search.md), [dynamic programming](../dynamic-programming/README.md) (for overlapping subproblems), [number theory](../number-theory/01-number-theory-for-programmers.md).

## Questions worth remembering

- **What are the three steps of divide and conquer?** Divide into smaller copies of the problem, conquer them recursively (base case directly), combine the answers.
- **What does the Master theorem say for `T(n) = 2T(n/2) + n`?** `a = 2, b = 2, d = 1`: balanced, so `Θ(n log n)`.
- **How does Karatsuba reduce four multiplications to three?** It computes the cross terms `x1*y0 + x0*y1` as `(x1 + x0)(y1 + y0) - x1*y1 - x0*y0`, reusing two products it already needs.
- **What are the three possible locations of the best slice in the maximum-subarray problem?** Entirely in the left half, entirely in the right half, or crossing the middle.
- **How do you decide between divide and conquer and dynamic programming?** If subproblems are independent, plain divide and conquer; if the same subproblems recur in different branches, cache them (dynamic programming).
- **Why are divide-and-conquer algorithms easy to parallelize?** The subproblems are independent, so they can be solved on different cores or machines and merged.

Practice problems with solutions are in the **Practice** section of each lesson.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Divide and Conquer](01-divide-and-conquer.md)
