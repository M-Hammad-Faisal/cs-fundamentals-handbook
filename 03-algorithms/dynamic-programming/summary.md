# Dynamic Programming: One-Page Summary

## When to use
- **Optimal substructure** + **overlapping subproblems**.
- Clues: "minimum/maximum", "number of ways", "possible?", "longest/shortest", decisions depending on earlier choices.

## Styles
| Top-down | Bottom-up |
|----------|-----------|
| Recursion + cache (`lru_cache`) | Fill table small → large |
| Computes only needed states | No recursion limit; easy space optimization |

## Recipe
1. State (what does `dp[...]` mean?) 2. Recurrence 3. Base cases 4. Order 5. Answer + space optimization.
Complexity = **#states × work per state**.

## Classics and recurrences
| Problem | Recurrence |
|---------|-----------|
| Climb stairs / Fibonacci | `dp[i] = dp[i-1] + dp[i-2]` |
| House robber | `dp[i] = max(dp[i-1], dp[i-2] + x)` |
| Coin change (min) | `dp[a] = min(dp[a-c] + 1)` |
| LIS | `O(n²)` DP or `O(n log n)` tails + bisect |
| Grid paths | `dp[r][c] = dp[r-1][c] + dp[r][c-1]` |
| LCS | match: `1 + dp[i-1][j-1]`; else `max(dp[i-1][j], dp[i][j-1])` |
| Edit distance | match: `dp[i-1][j-1]`; else `1 + min(del, ins, replace)` |
| 0/1 knapsack | `dp[w] = max(dp[w], dp[w-wt] + val)`, capacity **downward** |
| Unbounded knapsack / coin ways | capacity **upward** |

## Shapes
Interval DP · bitmask DP · digit DP · tree DP · state-machine DP (stocks).

## Tips
- Brute-force recursion → find repeats → memoize.
- Keep only needed rows to cut space.
- Reconstruct solutions with parent pointers.
- Use hashable (tuple) state for `lru_cache`.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Dynamic Programming](01-dp-thinking-and-1d-problems.md) · [DP on Two Sequences, Grids and Knapsack](02-dp-on-two-sequences-and-grids.md) · [Advanced DP Patterns](03-advanced-dp-patterns.md)
