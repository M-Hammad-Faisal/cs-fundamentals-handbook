# Dynamic Programming

## Detailed lessons

1. [DP thinking and 1D problems](01-dp-thinking-and-1d-problems.md): memoization vs tabulation, the five-step method, stairs, robber, coins, LIS
2. [DP on two sequences and grids](02-dp-on-two-sequences-and-grids.md): LCS, edit distance, knapsack, grid paths, reconstruction
3. [Advanced DP patterns](03-advanced-dp-patterns.md): state machines, tree DP, bitmask DP, digit DP

The rest of this page is the quick reference.

## 1. The concept

**Dynamic programming (DP)** solves a problem by breaking it into **overlapping subproblems**, solving each one **once**, and reusing the stored answers. It turns many exponential recursions into polynomial time.

A problem is a DP candidate when it has:

1. **Optimal substructure:** the best answer is built from best answers to smaller subproblems.
2. **Overlapping subproblems:** the same subproblem is needed many times.

(If subproblems do not overlap, plain divide and conquer works. If a locally best choice is always safe, a [greedy](../greedy/README.md) algorithm may suffice.)

### Two styles

| Style | How | Pros |
|-------|-----|------|
| **Top-down (memoization)** | Write the recursion, cache results | Easy to derive; computes only needed states |
| **Bottom-up (tabulation)** | Fill a table from small to large | No recursion limit; enables space optimization |

```python
from functools import lru_cache

# Top-down
@lru_cache(maxsize=None)
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)

# Bottom-up, O(n) time, O(1) space
def fib_iter(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
```

## 2. The five-step recipe

1. **Define the state.** What do the parameters of a subproblem mean? (`dp[i]` = best answer for the first `i` items.)
2. **Write the recurrence.** How does a state depend on smaller states?
3. **Set the base cases.**
4. **Decide the order.** Bottom-up must fill dependencies first.
5. **Find the answer** (a specific cell, or the best across cells) and **optimize space** if possible.

Complexity is usually *(number of states) × (work per state)*.

## 3. 1D DP

### Climbing stairs (`dp[i]` = ways to reach step `i`)

```python
def climb_stairs(n):
    a, b = 1, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b
```

### House robber (no two adjacent houses)

`dp[i] = max(dp[i-1], dp[i-2] + nums[i])`

```python
def rob(nums):
    take, skip = 0, 0
    for x in nums:
        take, skip = skip + x, max(take, skip)
    return max(take, skip)
```

### Coin change (fewest coins to make an amount)

`dp[a] = min(dp[a - c] + 1)` over coins `c`.

```python
def coin_change(coins, amount):
    INF = float("inf")
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                dp[a] = min(dp[a], dp[a - c] + 1)
    return -1 if dp[amount] == INF else dp[amount]    # O(amount * len(coins))
```

### Longest increasing subsequence

`O(n²)` DP, then the `O(n log n)` version using binary search over "tails":

```python
import bisect

def lis(nums):
    tails = []
    for x in nums:
        i = bisect.bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)
```

### Word break

```python
def word_break(s, words):
    words, dp = set(words), [True] + [False] * len(s)
    for i in range(1, len(s) + 1):
        dp[i] = any(dp[j] and s[j:i] in words for j in range(i))
    return dp[-1]
```

## 4. 2D DP

### Grid paths

`dp[r][c] = dp[r-1][c] + dp[r][c-1]`

```python
def unique_paths(m, n):
    row = [1] * n
    for _ in range(1, m):
        for c in range(1, n):
            row[c] += row[c - 1]
    return row[-1]
```

### Longest common subsequence (LCS)

`dp[i][j]` = LCS of `a[:i]` and `b[:j]`. If the last characters match, `1 + dp[i-1][j-1]`, otherwise `max(dp[i-1][j], dp[i][j-1])`.

```python
def lcs(a, b):
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]                                  # O(m * n)
```

### Edit distance (Levenshtein)

Minimum insertions, deletions, and substitutions to turn `a` into `b`.

```python
def edit_distance(a, b):
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1): dp[i][0] = i
    for j in range(n + 1): dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j],      # delete
                                   dp[i][j - 1],      # insert
                                   dp[i - 1][j - 1])  # replace
    return dp[m][n]
```

### 0/1 Knapsack

Pick items (each at most once) to maximize value within a weight limit. `dp[w]` = best value with capacity `w`. Iterate capacity **downward** so each item is used once.

```python
def knapsack(weights, values, capacity):
    dp = [0] * (capacity + 1)
    for w, v in zip(weights, values):
        for cap in range(capacity, w - 1, -1):
            dp[cap] = max(dp[cap], dp[cap - w] + v)
    return dp[capacity]                              # O(n * capacity)
```

Iterating capacity **upward** instead gives the *unbounded* knapsack (items reusable), which is the shape of coin change.

### Partition equal subset sum

```python
def can_partition(nums):
    total = sum(nums)
    if total % 2:
        return False
    target, dp = total // 2, {0}
    for x in nums:
        dp |= {s + x for s in dp if s + x <= target}
    return target in dp
```

## 5. Other DP shapes

| Shape | State | Examples |
|-------|-------|----------|
| **Interval DP** | `dp[i][j]` over a range | Matrix chain multiplication, burst balloons |
| **Bitmask DP** | `dp[mask]` over subsets | Travelling salesman (`O(2ⁿ n²)`) |
| **Digit DP** | Position, tight bound, remainder | Count numbers with a property up to `N` |
| **DP on trees** | `dp[node]` combines children | Max independent set, tree diameter |
| **State machine DP** | `dp[i][state]` | Buy/sell stock with cooldown |
| **Probability / expected value** | Expected result per state | Dice games |

### Stock trading with cooldown (state machine)

```python
def max_profit_cooldown(prices):
    hold, sold, rest = float("-inf"), 0, 0
    for p in prices:
        prev_sold = sold
        sold = hold + p
        hold = max(hold, rest - p)
        rest = max(rest, prev_sold)
    return max(sold, rest)
```

### Reconstructing the solution

DP tables give the *value*. To recover the actual items or path, store a parent/choice pointer per cell (or walk the table backward and re-derive each decision).

## 6. Two real-world examples

### Example 1: Diff tools, spell-checkers and DNA alignment

`git diff` and file-comparison tools use **LCS** (and the faster Myers algorithm) to find the smallest set of line additions and deletions between two versions. Spell-checkers and "did you mean?" suggestions rank candidates by **edit distance**. Bioinformatics aligns DNA and protein sequences with DP algorithms such as Needleman-Wunsch and Smith-Waterman. The pattern is the same: compare two sequences by building a table of best partial answers.

### Example 2: Resource allocation and routing

Choosing which projects to fund within a budget, which items to load into a container of fixed capacity, or which ads to show within a daily budget is **knapsack**-style DP. Network routing protocols (Bellman-Ford in distance-vector routing) compute shortest paths by DP. Text justification in word processors, segmentation of Chinese or Japanese text into words, and Viterbi decoding in speech recognition all rely on DP to pick the best split from exponentially many options.

## 7. Tips, tricks and pitfalls

- **Start with brute-force recursion,** identify repeated subproblems, then add memoization. Convert to a table afterwards if you want.
- **Define the state precisely** in words before coding. Most DP bugs are unclear state definitions.
- **Check base cases and boundaries** (empty string, zero capacity, one item).
- **Optimize space** by keeping only the rows you still need (`dp[i]` depends only on `dp[i-1]`).
- **Iteration order matters** in 1D knapsack: downward for 0/1, upward for unbounded.
- **`@lru_cache` needs hashable arguments.** Use tuples, not lists, for state.
- **Recursion depth:** deep memoized recursion can hit the limit; use bottom-up for large `n`.
- **Do not confuse with greedy:** if you cannot prove a local choice is safe, use DP.
- **Count the states and the transition cost** to state the complexity quickly in an interview.
- **Typical clues:** "minimum/maximum", "number of ways", "is it possible", "longest/shortest", and choices that depend on earlier choices.

## 8. Check yourself

1. What two properties make a problem suitable for DP?
2. What is the difference between memoization and tabulation?
3. What is the state and recurrence for coin change?
4. Why does 0/1 knapsack iterate capacity downward in the 1D version?
5. What is the time complexity of LCS and how can you reduce its space?
6. How do you reconstruct the actual solution, not just its value?
7. How does DP differ from greedy and from plain divide and conquer?

<details>
<summary>Answers</summary>

1. Optimal substructure and overlapping subproblems.
2. Memoization is top-down recursion with a cache; tabulation fills a table bottom-up. Same states, different order and style.
3. State `dp[a]` = fewest coins for amount `a`; recurrence `dp[a] = min(dp[a - c] + 1)` over coins `c <= a`, with `dp[0] = 0`.
4. Going downward ensures `dp[cap - w]` still reflects the state *before* the current item, so each item is used at most once.
5. `O(m * n)` time; keep only two rows (or one) to get `O(min(m, n))` space if you need only the length.
6. Store the choice made at each state (parent pointers), or backtrack through the table re-deriving which option produced each value.
7. Divide and conquer has independent subproblems; DP's subproblems overlap, so results are cached. Greedy makes one irrevocable locally best choice, while DP considers all options for each state.

</details>

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

Back to the [part overview](../README.md).
