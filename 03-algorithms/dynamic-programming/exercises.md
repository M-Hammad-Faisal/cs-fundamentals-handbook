# Dynamic Programming: Exercises

## 1D
1. **Climbing stairs:** ways to climb `n` steps taking 1 or 2 at a time.
2. **House robber:** maximum loot without robbing adjacent houses.
3. **Coin change:** fewest coins for an amount (`-1` if impossible). Then count the **number of ways**.
4. **Longest increasing subsequence** length in `O(n log n)`.
5. **Word break:** can a string be segmented into dictionary words?
6. **Maximum product subarray.**
7. **Decode ways:** number of ways to decode a digit string (`"12"` = `AB` or `L`).

## 2D
8. **Unique paths** in an `m x n` grid (moves right or down).
9. **Minimum path sum** in a grid.
10. **Longest common subsequence** of two strings.
11. **Edit distance** between two strings.
12. **0/1 knapsack:** best value within a capacity.
13. **Partition equal subset sum.**
14. **Longest palindromic subsequence.**
15. **Best time to buy and sell stock with cooldown.**

<details>
<summary>Solutions</summary>

```python
import bisect

# 1
def climb_stairs(n):
    a, b = 1, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b

# 2
def rob(nums):
    take = skip = 0
    for x in nums:
        take, skip = skip + x, max(take, skip)
    return max(take, skip)

# 3
def coin_change(coins, amount):
    INF = float("inf")
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                dp[a] = min(dp[a], dp[a - c] + 1)
    return -1 if dp[amount] == INF else dp[amount]

def coin_ways(coins, amount):
    dp = [1] + [0] * amount
    for c in coins:                      # coins outer: counts combinations, not orders
        for a in range(c, amount + 1):
            dp[a] += dp[a - c]
    return dp[amount]

# 4
def lis(nums):
    tails = []
    for x in nums:
        i = bisect.bisect_left(tails, x)
        if i == len(tails): tails.append(x)
        else: tails[i] = x
    return len(tails)

# 5
def word_break(s, words):
    words, dp = set(words), [True] + [False] * len(s)
    for i in range(1, len(s) + 1):
        dp[i] = any(dp[j] and s[j:i] in words for j in range(i))
    return dp[-1]

# 6
def max_product(nums):
    best = hi = lo = nums[0]
    for x in nums[1:]:
        cands = (x, hi * x, lo * x)
        hi, lo = max(cands), min(cands)
        best = max(best, hi)
    return best

# 7
def num_decodings(s):
    if not s or s[0] == "0":
        return 0
    a, b = 1, 1                           # ways for prefixes of length i-2, i-1
    for i in range(1, len(s)):
        cur = 0
        if s[i] != "0":
            cur += b
        if 10 <= int(s[i - 1:i + 1]) <= 26:
            cur += a
        a, b = b, cur
    return b

# 8
def unique_paths(m, n):
    row = [1] * n
    for _ in range(1, m):
        for c in range(1, n):
            row[c] += row[c - 1]
    return row[-1]

# 9
def min_path_sum(grid):
    m, n = len(grid), len(grid[0])
    dp = [float("inf")] * n
    dp[0] = 0
    for r in range(m):
        dp[0] += grid[r][0]
        for c in range(1, n):
            dp[c] = min(dp[c], dp[c - 1]) + grid[r][c]
    return dp[-1]

# 10
def lcs(a, b):
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            dp[i][j] = (dp[i-1][j-1] + 1 if a[i-1] == b[j-1]
                        else max(dp[i-1][j], dp[i][j-1]))
    return dp[m][n]

# 11
def edit_distance(a, b):
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1): dp[i][0] = i
    for j in range(n + 1): dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            dp[i][j] = (dp[i-1][j-1] if a[i-1] == b[j-1]
                        else 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]))
    return dp[m][n]

# 12
def knapsack(weights, values, capacity):
    dp = [0] * (capacity + 1)
    for w, v in zip(weights, values):
        for cap in range(capacity, w - 1, -1):
            dp[cap] = max(dp[cap], dp[cap - w] + v)
    return dp[capacity]

# 13
def can_partition(nums):
    total = sum(nums)
    if total % 2:
        return False
    target, dp = total // 2, {0}
    for x in nums:
        dp |= {s + x for s in dp if s + x <= target}
    return target in dp

# 14
def longest_palindromic_subsequence(s):
    return lcs(s, s[::-1])

# 15
def max_profit_cooldown(prices):
    hold, sold, rest = float("-inf"), 0, 0
    for p in prices:
        prev_sold = sold
        sold = hold + p
        hold = max(hold, rest - p)
        rest = max(rest, prev_sold)
    return max(sold, rest)
```

</details>

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Dynamic Programming](01-dp-thinking-and-1d-problems.md) · [DP on Two Sequences, Grids and Knapsack](02-dp-on-two-sequences-and-grids.md) · [Advanced DP Patterns](03-advanced-dp-patterns.md)
