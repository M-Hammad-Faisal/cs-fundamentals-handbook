# Recursion and Backtracking: One-Page Summary

## Recursion
- **Base case** + **recursive case** that shrinks the problem. Trust the function for smaller inputs.
- Each call adds a **stack frame**; depth `n` costs `O(n)` space. Python limit about 1000 (`RecursionError`); no tail-call optimization.
- Recurrences: `T(n)=T(n-1)+O(1)` → `O(n)` · `T(n/2)+O(1)` → `O(log n)` · `2T(n/2)+O(n)` → `O(n log n)` · `2T(n-1)+O(1)` → `O(2ⁿ)`.
- **Memoize** (`lru_cache`) overlapping subproblems.
- Convert to iteration with an explicit stack for deep recursion.

## Backtracking template
```
if solution: record; return
for choice in choices:
    if valid: choose → recurse → undo
```
- **Prune early**; sort input to break early.
- **Copy** the path when saving (`cur[:]`).
- **Undo exactly** what you did.
- Skip equal neighbours at the same depth to avoid duplicates.

## Counts to remember
Subsets `2ⁿ` · permutations `n!` · combinations `C(n, k)` · N-Queens uses column + diagonal sets.

## Classic problems
Subsets, permutations, combination sum, N-Queens, word search, generate parentheses, palindrome partitioning, Sudoku, Tower of Hanoi.

## Pitfalls
- Missing base case, or not progressing toward it.
- Mutating shared state without undoing it.
- Slicing in recursion (`O(n)` copy per call).
- Exponential blow-up without memoization.

[Lesson](README.md) · [Exercises](exercises.md)
