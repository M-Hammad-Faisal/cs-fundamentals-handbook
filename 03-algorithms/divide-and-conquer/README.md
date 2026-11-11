# Divide and Conquer

Split a problem into independent smaller copies, solve them recursively, combine the answers.

## Detailed lessons

- [Divide and conquer](01-divide-and-conquer.md): the pattern, recurrences and the Master theorem (with a numeric check), maximum subarray, Karatsuba multiplication, closest pair of points, majority element, and how it differs from dynamic programming

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

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

Back to [algorithms](../README.md).
