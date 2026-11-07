# Advanced DP Patterns: State Machines, Trees, Bitmasks and Digits

**Prerequisites:** [DP thinking](01-dp-thinking-and-1d-problems.md), [two sequences and grids](02-dp-on-two-sequences-and-grids.md), [binary trees](../../02-data-structures/trees/01-binary-trees-and-traversals.md), basic bit operations. **You will learn:** four patterns that cover a large share of harder DP problems: **state-machine DP** (stock trading), **DP on trees**, **bitmask DP** (travelling salesman on small inputs), and **digit DP**; plus a field guide to recognizing and choosing DP formulations.

## 1. State-machine DP: stock trading

Model the situation as a few **states** and the legal **moves** between them; keep the best profit for being in each state after each day.

**Best time to buy and sell, unlimited transactions** (you may hold at most one share):

- States: `hold` (own a share) and `free` (own none).
- Each day: from `free` you may stay `free` or buy (`-price` -> `hold`); from `hold` you may stay or sell (`+price` -> `free`).

```python
def max_profit_unlimited(prices):
    free, hold = 0, float("-inf")
    for p in prices:
        free, hold = max(free, hold + p), max(hold, free - p)      # both use the OLD values (tuple assignment)
    return free

def max_profit_one_trade(prices):
    best, lowest = 0, float("inf")
    for p in prices:
        lowest = min(lowest, p)
        best = max(best, p - lowest)                               # sell today after buying at the lowest price so far
    return best

def max_profit_with_cooldown(prices):                              # after selling you must wait one day
    hold, sold, rest = float("-inf"), 0, 0
    for p in prices:
        hold, sold, rest = max(hold, rest - p), hold + p, max(rest, sold)
    return max(sold, rest)

def max_profit_k_transactions(k, prices):
    if not prices:
        return 0
    buy = [float("-inf")] * (k + 1)
    sell = [0] * (k + 1)
    for p in prices:
        for t in range(1, k + 1):
            buy[t] = max(buy[t], sell[t - 1] - p)                   # buying starts transaction t
            sell[t] = max(sell[t], buy[t] + p)                      # selling completes it
    return sell[k]

prices = [7, 1, 5, 3, 6, 4]
print(max_profit_one_trade(prices), max_profit_unlimited(prices))      # 5 7
print(max_profit_with_cooldown([1, 2, 3, 0, 2]))                       # 3
print(max_profit_k_transactions(2, [3, 3, 5, 0, 0, 3, 1, 4]))          # 6
```

Trace of `max_profit_unlimited([7, 1, 5, 3, 6, 4])`: it buys at 1, sells at 5 (+4), buys at 3, sells at 6 (+3): total 7. A state machine turns a messy rule set into three or four lines.

## 2. DP on trees

Trees give a natural recursion; the DP state is **(node, small extra info)**, and children's answers combine into the parent's. This is **post-order** processing.

**House robber III:** houses form a binary tree; robbing a node forbids robbing its parent and children.

```python
class Node:
    def __init__(self, val, left=None, right=None):
        self.val, self.left, self.right = val, left, right

def rob_tree(root):
    def best(node):
        """Return (best if we rob this node, best if we skip it)."""
        if node is None:
            return 0, 0
        rob_left, skip_left = best(node.left)
        rob_right, skip_right = best(node.right)
        rob_here = node.val + skip_left + skip_right                    # robbing here forces skipping both children
        skip_here = max(rob_left, skip_left) + max(rob_right, skip_right)   # skipping lets each child choose freely
        return rob_here, skip_here
    return max(best(root))

#       3
#      / \
#     2   3
#      \   \
#       3   1
tree = Node(3, Node(2, None, Node(3)), Node(3, None, Node(1)))
print(rob_tree(tree))                                                   # 7     (3 + 3 + 1)
```

More tree DPs: the **diameter** and **maximum path sum** of a tree (return the best downward path, update the global best at each node), **tree coloring**, and the **minimum camera cover**.

```python
def max_path_sum(root):
    best = float("-inf")
    def down(node):                                                    # best path that starts at node and goes down
        nonlocal best
        if node is None:
            return 0
        left, right = max(down(node.left), 0), max(down(node.right), 0)     # ignore negative branches
        best = max(best, node.val + left + right)                       # a path bending at this node
        return node.val + max(left, right)
    down(root)
    return best

path_tree = Node(-10, Node(9), Node(20, Node(15), Node(7)))
print(max_path_sum(path_tree))                                         # 42    (15 + 20 + 7)
```

## 3. Bitmask DP: subsets as numbers

When the input is small (about 20 items or fewer), a **subset** can be one integer whose bit `i` says "item `i` is used". The state `dp[mask]` or `dp[mask][last]` covers `2^n` subsets instead of `n!` orderings.

Bit tools:

```python
mask = 0b1010
print(mask & (1 << 1) != 0, mask | (1 << 0), mask & ~(1 << 3), bin(mask ^ 0b1111), bin(mask).count("1"))
# True 11 2 0b101 2      (test bit 1, set bit 0, clear bit 3, flip all 4 bits, count set bits)
```

**Travelling salesman (shortest tour visiting every city once and returning):** brute force tries `(n-1)!` orders; DP over `(set of visited cities, current city)` takes `O(2^n · n²)`.

```python
import itertools

def tsp(dist):
    n = len(dist)
    INF = float("inf")
    dp = [[INF] * n for _ in range(1 << n)]
    dp[1][0] = 0                                                       # start at city 0, visited = {0}
    for mask in range(1 << n):
        for last in range(n):
            if dp[mask][last] == INF or not (mask >> last) & 1:
                continue
            for nxt in range(n):
                if (mask >> nxt) & 1:
                    continue                                           # already visited
                new_mask = mask | (1 << nxt)
                dp[new_mask][nxt] = min(dp[new_mask][nxt], dp[mask][last] + dist[last][nxt])
    full = (1 << n) - 1
    return min(dp[full][last] + dist[last][0] for last in range(1, n))

def tsp_bruteforce(dist):
    n = len(dist)
    return min(sum(dist[a][b] for a, b in zip((0,) + p, p + (0,))) for p in itertools.permutations(range(1, n)))

cities = [[0, 10, 15, 20], [10, 0, 35, 25], [15, 35, 0, 30], [20, 25, 30, 0]]
print(tsp(cities), tsp_bruteforce(cities))                             # 80 80

import random
random.seed(1)
for _ in range(20):
    n = random.randint(3, 7)
    d = [[0 if i == j else random.randint(1, 20) for j in range(n)] for i in range(n)]
    assert tsp(d) == tsp_bruteforce(d)
print("bitmask TSP matched brute force on 20 random instances")        # bitmask TSP matched brute force on 20 random instances
```

Another bitmask classic: **assign `n` tasks to `n` workers at minimum cost**, `dp[mask]` = best cost when the workers in `mask` are taken (the next task is `popcount(mask)`):

```python
def min_assignment_cost(cost):
    n = len(cost)
    dp = [float("inf")] * (1 << n)
    dp[0] = 0
    for mask in range(1 << n):
        task = bin(mask).count("1")                                    # tasks 0..task-1 are already assigned
        if task >= n:
            continue
        for worker in range(n):
            if not (mask >> worker) & 1:
                dp[mask | (1 << worker)] = min(dp[mask | (1 << worker)], dp[mask] + cost[task][worker])
    return dp[(1 << n) - 1]

print(min_assignment_cost([[9, 2, 7], [6, 4, 3], [5, 8, 1]]))          # 9
```

The best assignment gives task 0 to worker 1 (cost 2), task 1 to worker 0 (cost 6) and task 2 to worker 2 (cost 1): total 9. (Taking each task's cheapest worker would pick workers 1, 2, 2, which sends two tasks to worker 2: not allowed. That conflict is why you need the DP rather than row minimums.)

## 4. Digit DP: counting numbers with a property

To count numbers in `[0, N]` with some digit property (no repeated digit, digit sum equals `s`, ...), process the digits of `N` from the left, tracking a few flags, instead of testing each number.

```python
from functools import lru_cache

def count_digit_sum(limit, target):
    """How many integers in [0, limit] have digit sum equal to target?"""
    digits = list(map(int, str(limit)))

    @lru_cache(maxsize=None)
    def go(pos, remaining, tight):
        if remaining < 0:
            return 0
        if pos == len(digits):
            return 1 if remaining == 0 else 0
        top = digits[pos] if tight else 9                              # while "tight", digits are capped by limit's digits
        return sum(go(pos + 1, remaining - d, tight and d == top) for d in range(top + 1))
    return go(0, target, True)

print(count_digit_sum(100, 5), sum(1 for n in range(101) if sum(map(int, str(n))) == 5))      # 6 6
print(count_digit_sum(10**15, 40))                                    # 1666300814835   (16 digits, instant; brute force would take years)
```

The `tight` flag means "so far we have matched the limit's prefix exactly, so the next digit cannot exceed the limit's digit".

## 5. Recognizing DP: a checklist

| Clue in the statement | Likely DP |
|-----------------------|-----------|
| "How many ways...", "number of paths/combinations" | counting DP |
| "Minimum / maximum cost, length, profit" | optimization DP |
| "Is it possible to..." with sums, partitions, segmentation | boolean DP (subset sum, word break) |
| Two strings or sequences | `dp[i][j]` over prefixes |
| Choose items with a limited budget | knapsack family |
| You can only act in certain phases (hold/free, cooldown) | state machine DP |
| A tree | post-order DP with a tuple |
| `n` small (up to about 20) and subsets matter | bitmask DP |
| Count numbers with a digit property up to `N` | digit DP |
| Brute force is exponential but the same sub-inputs repeat | memoize it |

**Escalation ladder:** brute force recursion -> add memoization -> convert to tabulation -> shrink memory. Always start from the recursion; the table follows from it.

## 6. Complexity cheat sheet

| Pattern | Time | Space |
|---------|------|-------|
| 1D DP | `O(n)` to `O(n²)` | `O(n)` or `O(1)` rolling |
| Two sequences | `O(n · m)` | `O(n · m)` or `O(min(n, m))` |
| Knapsack | `O(n · W)` (pseudo-polynomial: `W` is a value, not a size) | `O(W)` |
| Tree DP | `O(n)` | `O(h)` recursion |
| Bitmask DP (TSP) | `O(2^n · n²)` | `O(2^n · n)` |
| Digit DP | `O(digits · states · 10)` | `O(digits · states)` |

## 7. Two real-world examples

**Example 1: Trading and revenue models.** State-machine DPs (own, sold, cooldown) are used to evaluate trading rules and to price inventory policies, where decisions depend on a small "mode".

**Example 2: Logistics.** Delivery routing for a handful of stops uses bitmask DP for the exact optimum; larger fleets use heuristics because `2^n` grows too fast (past about 25 stops you need approximation).

## 8. Common mistakes

- In state-machine DP, updating states one by one so that one update reads another's *new* value (use tuple assignment or temporaries).
- Forgetting to ignore negative branches in tree path-sum problems.
- Bitmask DP with `n` around 25 or more (memory and time explode).
- Pseudo-polynomial confusion: knapsack is `O(nW)`, which is exponential in the number of bits of `W`.
- Digit DP without the `tight` flag (counts numbers above the limit) or with a missing leading-zero state when zeros matter.
- Caching a function whose result depends on mutable global state.

## 9. Practice

1. `max_profit_unlimited([1, 2, 3, 4, 5])` and `max_profit_unlimited([5, 4, 3])`?
2. House robber III on a single node and on a chain of three (`3 -> 4 -> 5`).
3. How many subsets does a set of 20 items have? How many TSP states `(mask, last)` for 15 cities?
4. Use bitmasks to list all subsets of `{a, b, c}`.
5. Count integers from 0 to 99 whose digit sum is 9.
6. Maximum path sum of the tree with root `1`, left `2`, right `3`.
7. Give the state definition for "minimum cost to paint houses so that no two adjacent houses share a color" (3 colors).

<details>
<summary>Solutions</summary>

1. ```python
   print(max_profit_unlimited([1, 2, 3, 4, 5]), max_profit_unlimited([5, 4, 3]))      # 4 0
   ```
2. A single node: its value. A chain `3 -> 4 -> 5` (each the left child): rob 3 and 5 for 8.
   ```python
   print(rob_tree(Node(3)), rob_tree(Node(3, Node(4, Node(5)))))      # 3 8
   ```
3. `2^20 = 1 048 576` subsets; `2^15 · 15 = 491 520` states.
4. ```python
   items = "abc"
   print([[items[i] for i in range(3) if mask >> i & 1] for mask in range(8)])
   # [[], ['a'], ['b'], ['a', 'b'], ['c'], ['a', 'c'], ['b', 'c'], ['a', 'b', 'c']]
   ```
5. ```python
   print(count_digit_sum(99, 9))                      # 10
   ```
6. ```python
   print(max_path_sum(Node(1, Node(2), Node(3))))     # 6
   ```
7. `dp[i][c]` = minimum cost to paint houses `0..i` with house `i` painted color `c`; transition `dp[i][c] = cost[i][c] + min(dp[i-1][other colors])`.
   ```python
   def paint_houses(costs):
       prev = costs[0][:]
       for row in costs[1:]:
           prev = [row[c] + min(prev[o] for o in range(3) if o != c) for c in range(3)]
       return min(prev)
   print(paint_houses([[17, 2, 17], [16, 16, 5], [14, 3, 19]]))      # 10
   ```

</details>

## 10. Check yourself

1. What is the idea of state-machine DP?
2. How does tree DP combine results?
3. What does bit `i` of a mask mean in bitmask DP?
4. When is bitmask DP practical?
5. What does the `tight` flag mean in digit DP?

<details>
<summary>Answers</summary>

1. Track the best value for being in each small mode (hold, free, cooldown) after each step, with allowed transitions between modes.
2. Compute each node from its children's returned results (post-order), often returning a tuple of options.
3. That item `i` is included (visited/used) in the subset.
4. When `n` is small, about 20 or fewer.
5. That all digits chosen so far equal the limit's prefix, so the next digit is capped by the limit's next digit.

</details>

[Back to dynamic programming](README.md) · Previous: [DP on two sequences and grids](02-dp-on-two-sequences-and-grids.md)
