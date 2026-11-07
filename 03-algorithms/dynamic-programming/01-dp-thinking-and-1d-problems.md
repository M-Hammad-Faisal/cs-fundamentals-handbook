# Dynamic Programming: Thinking and 1D Problems

**Prerequisites:** [recursion fundamentals](../recursion-backtracking/01-recursion-fundamentals.md) (especially memoization and the Fibonacci explosion), [greedy](../greedy/01-greedy-algorithms.md) (to know when DP is needed instead). **You will learn:** what dynamic programming is, its two required properties, the two implementation styles (**top-down memoization** and **bottom-up tabulation**), a five-step method for designing a DP, and worked 1D problems: **climbing stairs, house robber, coin change, longest increasing subsequence, word break, decode ways, maximum subarray**.

## 1. In plain words

**Dynamic programming (DP)** is "recursion that remembers". When a problem breaks into subproblems that **overlap** (the same subproblem appears again and again), solve each subproblem **once**, store the answer, and reuse it.

Analogy: you are writing the sum `1+1+1+1+1+1+1+1`. Someone asks "and if I add one more?" You do not recount from the start; you remember the previous total `8` and answer `9` instantly. DP is that memory, applied systematically.

Two properties a problem needs:

1. **Overlapping subproblems:** the recursion revisits the same inputs (Fibonacci did).
2. **Optimal substructure:** the best answer to the big problem is built from best answers to smaller ones.

(Compare: no overlap but independent halves is plain divide and conquer, e.g. merge sort; a provably safe local choice means [greedy](../greedy/01-greedy-algorithms.md).)

## 2. Two ways to write a DP

**Top-down (memoization):** write the natural recursion, add a cache. Easy to derive; only computes states actually needed; limited by recursion depth.

**Bottom-up (tabulation):** fill a table from the smallest subproblem upward with loops. No recursion, usually faster, and often allows reducing memory.

```python
from functools import lru_cache

# Top-down
@lru_cache(maxsize=None)
def fib_top(n):
    return n if n < 2 else fib_top(n - 1) + fib_top(n - 2)

# Bottom-up with a table
def fib_table(n):
    dp = [0, 1] + [0] * (n - 1)
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]

# Bottom-up with O(1) memory: we only ever look back two steps
def fib_rolling(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

print(fib_top(60), fib_table(60), fib_rolling(60))      # 1548008755920 1548008755920 1548008755920
```

## 3. The five-step method

1. **State:** what small set of numbers identifies a subproblem? ("`dp[i]` = the answer for the first `i` items.")
2. **Meaning:** write one precise sentence for what `dp[i]` stores.
3. **Transition:** how does `dp[i]` depend on smaller states? (the recurrence)
4. **Base cases:** the smallest states with obvious answers.
5. **Order and answer:** fill in an order where dependencies are ready; which cell is the final answer?

Then add memory optimization if only a few previous states are needed.

## 4. Climbing stairs

You can climb 1 or 2 steps at a time. How many ways to reach step `n`?

- State: `dp[i]` = number of ways to reach step `i`.
- Transition: the last move was a 1-step from `i - 1` or a 2-step from `i - 2`: `dp[i] = dp[i-1] + dp[i-2]`.
- Base: `dp[0] = 1` (do nothing), `dp[1] = 1`.

```python
def climb_stairs(n):
    a, b = 1, 1                                       # ways to reach steps 0 and 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b if n >= 1 else 1

print([climb_stairs(n) for n in range(1, 9)])         # [1, 2, 3, 5, 8, 13, 21, 34]
```

(The same recurrence as Fibonacci in disguise. Recognizing familiar recurrences in new stories is half the skill.)

## 5. House robber

Houses in a row hold money `nums[i]`; you cannot rob two adjacent houses. Maximize the loot.

- State: `dp[i]` = best total using the first `i` houses.
- Transition: skip house `i` (`dp[i-1]`) or rob it (`dp[i-2] + nums[i]`): take the max.

```python
def house_robber(nums):
    prev2, prev1 = 0, 0                               # best for i-2 and i-1 houses
    for money in nums:
        prev2, prev1 = prev1, max(prev1, prev2 + money)
    return prev1

print(house_robber([2, 7, 9, 3, 1]), house_robber([1, 2, 3, 1]), house_robber([]))      # 12 4 0
```

Trace on `[2, 7, 9, 3, 1]`: after house 1 → 2; house 2 → max(2, 7) = 7; house 3 → max(7, 2+9) = 11; house 4 → max(11, 7+3) = 11; house 5 → max(11, 11+1) = 12.

## 6. Coin change (fewest coins)

Coins of given values (unlimited supply); find the **minimum number of coins** for `amount`. This is where [greedy fails](../greedy/01-greedy-algorithms.md) for `{4, 3, 1}`.

- State: `dp[a]` = fewest coins to make amount `a`.
- Transition: try every coin `c`: `dp[a] = 1 + min(dp[a - c])`.
- Base: `dp[0] = 0`.

```python
def coin_change(coins, amount):
    INF = float("inf")
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
    return dp[amount] if dp[amount] != INF else -1

print(coin_change([1, 2, 5], 11), coin_change([4, 3, 1], 6), coin_change([2], 3))      # 3 2 -1

def count_ways(coins, amount):                         # how many COMBINATIONS make the amount?
    ways = [1] + [0] * amount
    for c in coins:                                    # coin loop OUTSIDE: each combination is counted once, not as permutations
        for a in range(c, amount + 1):
            ways[a] += ways[a - c]
    return ways[amount]

print(count_ways([1, 2, 5], 5), count_ways([2], 3))    # 4 0
```

Cost: `O(amount × number of coins)`. The loop order matters: coins outside counts combinations (`2+1+1+1` equals `1+2+1+1`); amount outside would count orderings.

## 7. Maximum subarray (Kadane) as a DP

`dp[i]` = best sum of a subarray **ending at** `i`: either extend the previous one or start fresh.

```python
def max_subarray(nums):
    best = current = nums[0]
    for x in nums[1:]:
        current = max(x, current + x)                  # extend or restart
        best = max(best, current)
    return best

print(max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]), max_subarray([-3, -1, -2]))      # 6 -1
```

## 8. Longest increasing subsequence (LIS)

Find the longest subsequence (not necessarily adjacent) that is strictly increasing.

- State: `dp[i]` = length of the longest increasing subsequence **ending at** `i`.
- Transition: `dp[i] = 1 + max(dp[j])` over earlier `j` with `nums[j] < nums[i]`.

```python
def lis_quadratic(nums):
    if not nums:
        return 0
    dp = [1] * len(nums)
    for i in range(len(nums)):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)

import bisect
def lis_fast(nums):                                    # O(n log n): "patience sorting"
    tails = []                                         # tails[k] = smallest tail of any increasing subsequence of length k+1
    for x in nums:
        i = bisect.bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)

data = [10, 9, 2, 5, 3, 7, 101, 18]
print(lis_quadratic(data), lis_fast(data))             # 4 4     (e.g. 2, 3, 7, 18)
```

## 9. Word break

Can the string `s` be split into dictionary words?

- State: `dp[i]` = can the first `i` characters be segmented?
- Transition: `dp[i]` is true if some `j < i` has `dp[j]` true and `s[j:i]` is a word.

```python
def word_break(s, words):
    words = set(words)
    dp = [True] + [False] * len(s)
    for i in range(1, len(s) + 1):
        for j in range(i):
            if dp[j] and s[j:i] in words:
                dp[i] = True
                break
    return dp[len(s)]

print(word_break("leetcode", ["leet", "code"]), word_break("catsandog", ["cats", "dog", "sand", "and", "cat"]))      # True False
```

## 10. Decode ways

A message of digits maps `1 -> A ... 26 -> Z`. In how many ways can `"226"` be decoded (`BZ`, `VF`, `BBF`)?

```python
def decode_ways(s):
    if not s or s[0] == "0":
        return 0
    prev2, prev1 = 1, 1                                # ways for the prefixes of length i-2 and i-1
    for i in range(1, len(s)):
        current = 0
        if s[i] != "0":
            current += prev1                           # decode the single digit s[i]
        if 10 <= int(s[i - 1:i + 1]) <= 26:
            current += prev2                           # decode the two-digit number
        prev2, prev1 = prev1, current
    return prev1

print(decode_ways("226"), decode_ways("06"), decode_ways("12"), decode_ways("2101"))      # 3 0 2 1
```

## 11. Choosing states: a common pattern table

| The problem asks about... | Typical state |
|---------------------------|---------------|
| a sequence prefix | `dp[i]` = answer for the first `i` items |
| a sequence ending at a position | `dp[i]` = best ending exactly at `i` |
| an amount or capacity | `dp[a]` = best for amount `a` |
| two sequences | `dp[i][j]` for prefixes of each ([next lesson](02-dp-on-two-sequences-and-grids.md)) |
| a grid | `dp[r][c]` |
| subsets of a small set | bitmask `dp[mask]` |

## 12. Two real-world examples

**Example 1: Spell correctors and diff tools.** Edit distance and longest common subsequence (next lesson) power `diff`, `git`, autocorrect and DNA alignment.

**Example 2: Resource planning.** Coin-change style DPs price items into the cheapest combination of bundles; text editors use word-break style DPs to wrap lines and segment languages without spaces.

## 13. Common mistakes

- Defining the state vaguely (write the exact sentence for `dp[i]`).
- Wrong base case or wrong initial values (use `inf` for minimization, `0` or `-inf` for maximization).
- Wrong **loop order** (coins versus amount changes combinations vs permutations).
- Off-by-one with `dp[i]` meaning "first `i` items" versus "item `i`".
- Using DP when a simple greedy or formula exists (over-engineering), or greedy when DP is required.
- Forgetting that a rolling-array optimization changes which states you can still read.

## 14. Practice

1. Tribonacci: `T(n) = T(n-1) + T(n-2) + T(n-3)` with `T(0)=0, T(1)=T(2)=1`. Compute `T(25)` with a rolling DP.
2. Min cost climbing stairs: `cost = [10, 15, 20]`; you pay when stepping **off** a stair, may start at index 0 or 1, and must go past the last index.
3. How many ways to make 10 from coins `[1, 5, 10]`?
4. Longest increasing subsequence length for `[0, 8, 4, 12, 2, 10, 6, 14, 1, 9]`.
5. House robber II: houses in a **circle** (first and last are adjacent).
6. Perfect squares: the least number of perfect squares that sum to `n` (12 gives 3 = 4+4+4).
7. State the DP for "partition equal subset sum": can the numbers be split into two subsets of equal sum?

<details>
<summary>Solutions</summary>

1. ```python
   def tribonacci(n):
       a, b, c = 0, 1, 1
       if n == 0: return 0
       for _ in range(n - 2):
           a, b, c = b, c, a + b + c
       return c
   print(tribonacci(25))                              # 1389537
   ```
2. ```python
   def min_cost_climbing(cost):
       a, b = 0, 0                                    # cheapest cost to stand on the previous two stairs
       for i in range(2, len(cost) + 1):
           a, b = b, min(b + cost[i - 1], a + cost[i - 2])
       return b
   print(min_cost_climbing([10, 15, 20]))             # 15
   ```
3. ```python
   print(count_ways([1, 5, 10], 10))                  # 4
   ```
4. ```python
   print(lis_fast([0, 8, 4, 12, 2, 10, 6, 14, 1, 9]))      # 4   (for example 0, 2, 6, 9)
   ```
5. ```python
   def house_robber_circle(nums):
       if len(nums) == 1: return nums[0]
       return max(house_robber(nums[1:]), house_robber(nums[:-1]))      # exclude the first house, or exclude the last
   print(house_robber_circle([2, 3, 2]), house_robber_circle([1, 2, 3, 1]))      # 3 4
   ```
6. ```python
   def num_squares(n):
       dp = [0] + [float("inf")] * n
       for i in range(1, n + 1):
           j = 1
           while j * j <= i:
               dp[i] = min(dp[i], dp[i - j * j] + 1)
               j += 1
       return dp[n]
   print(num_squares(12), num_squares(13))            # 3 2
   ```
7. If the total is odd, answer no. Otherwise `dp[s]` = "can some subset sum to `s`", target `total / 2`; update `dp[s] |= dp[s - x]` for `s` from high to low for each number `x`.
   ```python
   def can_partition(nums):
       total = sum(nums)
       if total % 2: return False
       target, dp = total // 2, [True] + [False] * (total // 2)
       for x in nums:
           for s in range(target, x - 1, -1):         # backwards so each number is used once
               dp[s] = dp[s] or dp[s - x]
       return dp[target]
   print(can_partition([1, 5, 11, 5]), can_partition([1, 2, 3, 5]))      # True False
   ```

</details>

## 15. Check yourself

1. What two properties make a problem suitable for DP?
2. What is the difference between memoization and tabulation?
3. What are the five steps for designing a DP?
4. Why can coin-change use DP but not greedy?
5. Why does loop order matter in "count the ways"?

<details>
<summary>Answers</summary>

1. Overlapping subproblems and optimal substructure.
2. Memoization is top-down recursion with a cache; tabulation fills a table bottom-up with loops.
3. State, meaning, transition, base cases, order and answer.
4. A locally best coin can block the optimum (coins `{4, 3, 1}`), so every sub-amount must be considered.
5. With coins in the outer loop each combination is counted once; with the amount outside, different orderings are counted separately.

</details>

[Back to dynamic programming](README.md) · Next: [DP on two sequences and grids](02-dp-on-two-sequences-and-grids.md)
