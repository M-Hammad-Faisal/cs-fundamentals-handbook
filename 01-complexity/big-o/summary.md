# Big-O and Complexity Analysis: One-Page Summary

## Definitions
- **Big-O** `O(f(n))`: upper bound on growth. **Ω**: lower bound. **Θ**: tight bound.
- Drop constants and lower-order terms: `5n² + 100n + 7` is `O(n²)`.

## Growth ladder (best to worst)
`O(1)` < `O(log n)` < `O(n)` < `O(n log n)` < `O(n²)` < `O(n³)` < `O(2ⁿ)` < `O(n!)`

## Fast analysis rules
| Pattern | Cost |
|---------|------|
| One loop over `n` | `O(n)` |
| Nested loops | multiply |
| Sequential blocks | add, keep the largest |
| Halving or doubling per step | `O(log n)` |
| Two different inputs | use `n` and `m`, never both as `n` |
| Recursion | write the recurrence |

## Recurrences to memorize
- `T(n) = T(n/2) + O(1)` → `O(log n)`
- `T(n) = 2T(n/2) + O(n)` → `O(n log n)`
- `T(n) = 2T(n-1) + O(1)` → `O(2ⁿ)`

## Budget guide (about 10⁸ operations per second)
`n ≤ 10` factorial · `n ≤ 20` exponential · `n ≤ 500` cubic · `n ≤ 10⁴` quadratic · `n ≤ 10⁶` `n log n` · `n ≤ 10⁸` linear

## Python traps
- `x in list` is `O(n)`; `x in set/dict` is `O(1)` average.
- `list.insert(0, x)` and `list.pop(0)` are `O(n)`; use `deque`.
- `s += piece` in a loop is quadratic; use `"".join`.
- Slicing copies: `a[i:j]` costs `O(j-i)`.
- `list.append` is `O(1)` **amortized**.

## Remember
- State **time and space** together.
- Worst case unless told otherwise; mention average if it differs.
- Constants and I/O matter in real systems. Profile before optimizing.

[Full chapter](README.md) · [Exercises](exercises.md)

[Lesson](README.md) · [Exercises](exercises.md)
