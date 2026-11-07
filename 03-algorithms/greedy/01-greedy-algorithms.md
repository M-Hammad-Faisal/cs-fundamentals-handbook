# Greedy Algorithms

**Prerequisites:** [sorting](../sorting/01-sorting-basics-and-elementary-sorts.md), [heaps](../../02-data-structures/heaps/02-priority-queue-applications.md), [backtracking](../recursion-backtracking/02-backtracking.md) (to appreciate what greedy saves). **You will learn:** the greedy idea, how to **prove** a greedy choice is safe (the **exchange argument**), the classic problems (**interval scheduling, fractional knapsack, minimum platforms, jump game, gas station, task scheduling**), and, just as important, the problems where greedy **fails** and you need [dynamic programming](../dynamic-programming/README.md).

## 1. In plain words

A **greedy algorithm** builds a solution step by step, always taking the option that looks **best right now**, and **never reconsiders**. No backtracking, no table of subproblems: usually a sort followed by one pass, so it is fast and simple.

Analogy: making change with coins; you grab the biggest coin that fits, again and again. That works for euros and dollars, but, as we will see, not for every coin system. The central question is therefore always: **is the locally best choice also globally best?**

| Greedy works when... | Which means |
|----------------------|-------------|
| **Greedy-choice property** | some optimal solution starts with the greedy choice |
| **Optimal substructure** | after the choice, what remains is a smaller instance of the same problem |

## 2. Example 1: interval scheduling (activity selection)

You have a meeting room and a list of requests `(start, end)`. Accept the **maximum number** of non-overlapping meetings.

Candidate greedy rules: earliest start? shortest meeting? fewest conflicts? **Earliest finish time** is the winner: finishing early leaves the most room for everything else.

```python
def max_meetings(intervals):
    chosen, last_end = [], float("-inf")
    for start, end in sorted(intervals, key=lambda iv: iv[1]):       # sort by END time
        if start >= last_end:                                         # compatible with the last chosen meeting
            chosen.append((start, end))
            last_end = end
    return chosen

meetings = [(1, 4), (3, 5), (0, 6), (5, 7), (3, 9), (5, 9), (6, 10), (8, 11), (8, 12), (2, 14), (12, 16)]
print(max_meetings(meetings))                     # [(1, 4), (5, 7), (8, 11), (12, 16)]
```

**Why it is correct (exchange argument).** Suppose an optimal schedule `O` starts with a meeting `m` that is **not** the earliest-finishing one, `g`. Swap `m` for `g`: `g` ends no later than `m`, so it cannot collide with the second meeting of `O`. The schedule stays valid with the same size, so *some* optimal schedule contains the greedy choice. Repeat for the remaining problem.

**Cost:** `O(n log n)` for the sort, `O(n)` for the pass.

A broken rule for contrast:

```python
def shortest_first(intervals):                     # tempting but WRONG
    chosen, taken = [], []
    for start, end in sorted(intervals, key=lambda iv: iv[1] - iv[0]):
        if all(end <= s or start >= e for s, e in taken):
            taken.append((start, end))
    return len(taken)

trap = [(0, 5), (4, 7), (6, 11)]                   # the short middle meeting blocks both long ones
print(shortest_first(trap), len(max_meetings(trap)))      # 1 2
```

## 3. Example 2: fractional knapsack

A thief has a bag of capacity `W` and items with `(value, weight)`; items **can be split**. Take the best **value per kilogram** first.

```python
def fractional_knapsack(items, capacity):
    total, plan = 0.0, []
    for value, weight in sorted(items, key=lambda it: it[0] / it[1], reverse=True):
        take = min(weight, capacity)                  # a whole item or whatever still fits
        total += value * take / weight
        plan.append((value, weight, take))
        capacity -= take
        if capacity == 0:
            break
    return total, plan

items = [(60, 10), (100, 20), (120, 30)]              # (value, weight)
print(fractional_knapsack(items, 50))                 # (240.0, [(60, 10, 10), (100, 20, 20), (120, 30, 20)])
```

The same greedy is **wrong for the 0/1 knapsack** (items cannot be split). With the same items and capacity 50, greedy takes the first two for value 160, but the best is items 2 and 3 for **220**. That problem needs [dynamic programming](../dynamic-programming/README.md).

## 4. Example 3: minimum number of platforms (meeting rooms)

Given arrival and departure times, how many platforms are needed? Sort the events and sweep: arrivals add one, departures remove one; the answer is the peak.

```python
def min_platforms(arrivals, departures):
    arr, dep = sorted(arrivals), sorted(departures)
    platforms = best = i = j = 0
    while i < len(arr):
        if arr[i] <= dep[j]:                          # a train arrives before the earliest one leaves
            platforms += 1; i += 1
            best = max(best, platforms)
        else:
            platforms -= 1; j += 1
    return best

print(min_platforms([900, 940, 950, 1100, 1500, 1800], [910, 1200, 1120, 1130, 1900, 2000]))      # 3
```

## 5. Example 4: jump game

`nums[i]` is the maximum jump length from `i`. Can you reach the last index? Track the **farthest reachable** position.

```python
def can_reach_end(nums):
    farthest = 0
    for i, jump in enumerate(nums):
        if i > farthest:
            return False                              # we are stuck before reaching index i
        farthest = max(farthest, i + jump)
    return True

def min_jumps(nums):                                  # fewest jumps: BFS in disguise, still greedy
    jumps = current_end = farthest = 0
    for i in range(len(nums) - 1):
        farthest = max(farthest, i + nums[i])
        if i == current_end:                          # we must jump now: take the one that reaches farthest
            jumps += 1
            current_end = farthest
    return jumps

print(can_reach_end([2, 3, 1, 1, 4]), can_reach_end([3, 2, 1, 0, 4]))      # True False
print(min_jumps([2, 3, 1, 1, 4]), min_jumps([2, 3, 0, 1, 4]))              # 2 2
```

## 6. Example 5: gas station

Stations on a circular road; `gas[i]` is the fuel you gain at station `i`, `cost[i]` the fuel to drive to the next. Which start lets you complete the loop (if any)?

Insight: if the total gas is at least the total cost, a solution exists; and if you run out between `s` and `k`, no station in between can be a start, so try `k + 1`.

```python
def gas_station(gas, cost):
    if sum(gas) < sum(cost):
        return -1
    start = tank = 0
    for i in range(len(gas)):
        tank += gas[i] - cost[i]
        if tank < 0:                                  # cannot get past i from the current start
            start, tank = i + 1, 0
    return start

print(gas_station([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]), gas_station([2, 3, 4], [3, 4, 3]))      # 3 -1
```

## 7. Example 6: task scheduling with deadlines and rest (heap + greedy)

Run CPU tasks (letters) so identical tasks are separated by at least `n` idle-or-other slots; minimize total time. Always run the **most frequent** remaining task whose cooldown is over.

```python
import heapq
from collections import Counter, deque

def least_interval(tasks, n):
    heap = [-c for c in Counter(tasks).values()]      # max-heap of remaining counts
    heapq.heapify(heap)
    time, cooling = 0, deque()                        # (time when available again, remaining count)
    while heap or cooling:
        time += 1
        if heap:
            remaining = heapq.heappop(heap) + 1       # run the most frequent task once
            if remaining:
                cooling.append((time + n, remaining))
        if cooling and cooling[0][0] == time:
            heapq.heappush(heap, cooling.popleft()[1])
    return time

print(least_interval(list("AAABBB"), 2), least_interval(list("AAABBB"), 0), least_interval(list("AAAAAABCDEFG"), 2))      # 8 6 16
```

## 8. More greedy staples

```python
def coin_change_greedy(amount, coins):
    used = []
    for coin in sorted(coins, reverse=True):
        while amount >= coin:
            amount -= coin
            used.append(coin)
    return used if amount == 0 else None

print(coin_change_greedy(63, [25, 10, 5, 1]))         # [25, 25, 10, 1, 1, 1]
print(coin_change_greedy(6, [4, 3, 1]))               # [4, 1, 1]       <- 3 coins, but 3 + 3 uses only 2!
```

The second line is the classic **greedy failure**: with coins `{4, 3, 1}` the greedy answer for 6 uses three coins while the optimum is two (`3 + 3`). Whether greedy change works depends on the coin system; for real-world currencies (1, 5, 10, 25, ...) it happens to work, in general you need DP.

Other well-known greedy algorithms you have already met: **Dijkstra** and **Prim** (take the cheapest edge/vertex next), **Kruskal** (cheapest edge that makes no cycle), **Huffman coding** (merge the two least frequent), all in the [data structures part](../../02-data-structures/README.md).

## 9. How to decide: greedy, DP or backtracking?

| Ask yourself | If yes |
|--------------|--------|
| Can I find a rule and **prove** it with an exchange argument or invariant? | greedy |
| Do the same subproblems recur, and the best answer combines their best answers? | dynamic programming |
| Do I have to explore all possibilities (all solutions, or constraints interact)? | backtracking |
| Small counterexample breaks my rule (like coins `{4,3,1}`)? | not greedy |

A practical test: **write a brute force, compare it with your greedy on many small random inputs**. One mismatch kills the greedy rule.

```python
import random, itertools

def best_meetings_bruteforce(intervals):
    best = 0
    for r in range(len(intervals) + 1):
        for combo in itertools.combinations(intervals, r):
            ok = all(a[1] <= b[0] or b[1] <= a[0] for a, b in itertools.combinations(combo, 2))
            if ok:
                best = max(best, r)
    return best

random.seed(11)
for _ in range(300):
    ivs = []
    for _ in range(random.randint(1, 7)):
        s = random.randint(0, 10)
        ivs.append((s, s + random.randint(1, 5)))
    assert len(max_meetings(ivs)) == best_meetings_bruteforce(ivs)
print("earliest-finish greedy matched brute force on 300 random cases")     # earliest-finish greedy matched brute force on 300 random cases
```

## 10. Two real-world examples

**Example 1: Compression and networking.** Huffman coding (greedy merging of rare symbols) underlies ZIP/JPEG/PNG; Dijkstra's greedy settling underlies route planning and OSPF routing.

**Example 2: Scheduling resources.** Conference-room booking, CPU run queues (shortest job first minimizes average waiting time, another greedy result), and cloud bin-packing heuristics all use greedy rules because they are fast and, often, provably good or near-optimal.

## 11. Common mistakes

- Choosing a plausible rule without proving it (or testing it) and trusting it.
- Sorting by the wrong key (end time, not start time or duration, for interval scheduling).
- Using greedy for 0/1 knapsack or arbitrary coin systems.
- Forgetting ties and equal keys in the comparison.
- Mutating shared input when you sorted in place.
- Assuming "greedy gives a decent answer" equals "greedy is correct" in problems that demand the exact optimum.

## 12. Practice

1. Which meetings does earliest-finish pick from `[(0, 3), (2, 4), (3, 5), (4, 6)]`?
2. Fractional knapsack: capacity 10, items `(value, weight)` = `(10, 5), (6, 2), (12, 6)`. Best value?
3. Show an input where "pick the earliest *start*" fails for interval scheduling.
4. `can_reach_end([1, 1, 0, 1])`: trace `farthest`.
5. Minimum arrows to burst balloons given as intervals (an arrow at `x` bursts all balloons with `start <= x <= end`): write `min_arrows` (hint: sort by end).
6. Assign cookies: children have greed factors `g`, cookies have sizes `s`; maximize satisfied children (a child is satisfied if `size >= greed`).
7. Find coins where greedy fails other than `{4, 3, 1}`.

<details>
<summary>Solutions</summary>

1. `(0, 3)`, then `(3, 5)`: total 2 meetings (`(2, 4)` overlaps; `(4, 6)` overlaps `(3, 5)`).
   ```python
   print(max_meetings([(0, 3), (2, 4), (3, 5), (4, 6)]))      # [(0, 3), (3, 5)]
   ```
2. Ratios: 2, 3, 2; take `(6, 2)` fully (6), then 5 more units of the best remaining ratio 2: `(10, 5)` fully (10) for 7 weight, then 3 units of `(12, 6)` gives 6. Total `6 + 10 + 3 * 2 = 22` (weight `2 + 5 + 3 = 10`).
   ```python
   print(fractional_knapsack([(10, 5), (6, 2), (12, 6)], 10)[0])      # 22.0
   ```
3. `[(0, 100), (1, 2), (3, 4)]`: earliest start picks the huge meeting (1 total) but the best is 2.
4. `farthest` goes 1, 2, 2; at `i = 3` we have `3 > 2`, so it returns `False`.
   ```python
   print(can_reach_end([1, 1, 0, 1]))                          # False
   ```
5. ```python
   def min_arrows(balloons):
       arrows, last = 0, float("-inf")
       for start, end in sorted(balloons, key=lambda b: b[1]):
           if start > last:                                    # not hit by the previous arrow
               arrows += 1
               last = end
       return arrows
   print(min_arrows([(10, 16), (2, 8), (1, 6), (7, 12)]))      # 2
   ```
6. ```python
   def assign_cookies(greed, sizes):
       greed, sizes = sorted(greed), sorted(sizes)
       child = 0
       for cookie in sizes:                                    # give the smallest cookie that satisfies the least greedy child
           if child < len(greed) and cookie >= greed[child]:
               child += 1
       return child
   print(assign_cookies([1, 2, 3], [1, 1]), assign_cookies([1, 2], [1, 2, 3]))      # 1 2
   ```
7. `{1, 15, 25}` for amount 30: greedy takes `25 + 1 * 5` (6 coins) while `15 + 15` uses 2.
   ```python
   print(coin_change_greedy(30, [1, 15, 25]))                  # [25, 1, 1, 1, 1, 1]
   ```

</details>

## 13. Check yourself

1. What does it mean to be "greedy"?
2. What two properties make a greedy algorithm correct?
3. Which key do you sort by for maximum non-overlapping intervals?
4. Why does greedy fail for the 0/1 knapsack?
5. How can you test a greedy rule quickly?

<details>
<summary>Answers</summary>

1. Always pick the best-looking option at the moment and never undo it.
2. The greedy-choice property (some optimal solution uses it) and optimal substructure.
3. The end time (earliest finish first).
4. Items cannot be split, so a high value-per-weight item can block a better combination; you must consider combinations (DP).
5. Compare against a brute-force solver on many small random inputs.

</details>

[Back to greedy](README.md)
