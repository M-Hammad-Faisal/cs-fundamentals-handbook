# Greedy Algorithms

## Detailed lesson (start here if you are new)

- [Greedy algorithms in depth](01-greedy-algorithms.md): exchange argument, interval scheduling, knapsack, jump game, and where greedy fails

The rest of this page is the quick reference.

## 1. The concept

A **greedy algorithm** builds a solution step by step, always taking the choice that looks **best right now**, and never reconsidering. It is fast and simple, but it is correct only for problems with the right structure.

For a greedy algorithm to be correct, the problem needs:

1. **Greedy-choice property:** a locally optimal choice can be extended to a globally optimal solution.
2. **Optimal substructure:** what remains after the choice is a smaller problem of the same kind.

> **Greedy vs dynamic programming:** DP considers all choices at each state and keeps the best. Greedy commits to one choice. When greedy works, it is much faster. When it does not, you need DP.

### A failing example

Coin change with coins `{1, 3, 4}` and amount `6`. Greedy (largest coin first) gives `4 + 1 + 1` = 3 coins; the optimum is `3 + 3` = 2 coins. With US coins `{1, 5, 10, 25}` greedy happens to be optimal. The same code is right or wrong depending on the coin system.

## 2. How to prove greedy works

Two standard arguments:

- **Exchange argument:** take any optimal solution and show you can swap in the greedy choice without making it worse.
- **"Greedy stays ahead":** show that after each step the greedy solution is at least as good as any other partial solution.

If you cannot argue either, test against brute force on small inputs before trusting it.

## 3. Classic problems

### Activity selection / meeting rooms

Pick the maximum number of non-overlapping intervals. **Greedy rule: always take the one that ends earliest.**

```python
def max_non_overlapping(intervals):
    count, last_end = 0, float("-inf")
    for s, e in sorted(intervals, key=lambda x: x[1]):
        if s >= last_end:
            count += 1
            last_end = e
    return count                                      # O(n log n)
```

### Minimum number of platforms / rooms

Sort starts and ends separately and sweep (a greedy event ordering).

### Jump game

Can you reach the last index if each value is the maximum jump length?

```python
def can_jump(nums):
    reach = 0
    for i, x in enumerate(nums):
        if i > reach:
            return False
        reach = max(reach, i + x)
    return True                                       # O(n)
```

Minimum jumps to reach the end (greedy level expansion, like BFS):

```python
def min_jumps(nums):
    jumps = cur_end = farthest = 0
    for i in range(len(nums) - 1):
        farthest = max(farthest, i + nums[i])
        if i == cur_end:
            jumps += 1
            cur_end = farthest
    return jumps
```

### Gas station

```python
def can_complete_circuit(gas, cost):
    if sum(gas) < sum(cost):
        return -1
    tank = start = 0
    for i in range(len(gas)):
        tank += gas[i] - cost[i]
        if tank < 0:                  # cannot start from anywhere up to i
            start, tank = i + 1, 0
    return start
```

### Fractional knapsack

Take items by **highest value-per-weight ratio**, splitting the last one if needed. (The 0/1 version needs DP; the fractional version is greedy.)

```python
def fractional_knapsack(items, capacity):         # items: (value, weight)
    total = 0.0
    for v, w in sorted(items, key=lambda x: x[0] / x[1], reverse=True):
        take = min(w, capacity)
        total += v * take / w
        capacity -= take
        if capacity == 0:
            break
    return total
```

### Huffman coding

Build an optimal prefix code: repeatedly merge the two least frequent symbols using a min-heap. Frequent symbols get short codes.

```python
import heapq

def huffman(freqs):                               # freqs: {symbol: count}
    heap = [(f, i, {s: ""}) for i, (s, f) in enumerate(freqs.items())]
    heapq.heapify(heap)
    counter = len(heap)
    while len(heap) > 1:
        f1, _, c1 = heapq.heappop(heap)
        f2, _, c2 = heapq.heappop(heap)
        merged = {s: "0" + code for s, code in c1.items()}
        merged.update({s: "1" + code for s, code in c2.items()})
        heapq.heappush(heap, (f1 + f2, counter, merged))
        counter += 1
    return heap[0][2]
```

### Task scheduling and greedy with sorting

```python
# Minimize total waiting time: shortest job first
def total_wait(durations):
    t = wait = 0
    for d in sorted(durations):
        wait += t
        t += d
    return wait

# Assign cookies: smallest sufficient cookie to the least greedy child
def assign_cookies(children, cookies):
    children.sort(); cookies.sort()
    i = 0
    for c in cookies:
        if i < len(children) and c >= children[i]:
            i += 1
    return i
```

### Graph algorithms that are greedy

- **Dijkstra:** always settle the closest unsettled vertex.
- **Prim / Kruskal:** always add the cheapest edge that keeps the tree valid.

See [graph algorithms](../graph-algorithms/README.md).

## 4. Two real-world examples

### Example 1: Compression with Huffman codes

ZIP/DEFLATE, gzip, PNG and JPEG use Huffman coding. Counting symbol frequencies and greedily merging the rarest two builds the shortest possible prefix code, so common bytes use few bits and rare bytes use more. The greedy choice provably yields the optimal prefix code, which is why a simple algorithm sits at the heart of file compression.

### Example 2: Scheduling and routing

A meeting-room booking system (or a cloud scheduler) picks the job that finishes earliest to fit the most tasks. Operating-system schedulers favour shortest-job-first to lower average waiting time. Network routers forward each packet along the locally cheapest next hop, and Dijkstra's greedy expansion computes the best routes. Change-making in cash registers uses greedy for standard currencies (where it is provably optimal).

## 5. Tips, tricks and pitfalls

- **Sort first.** Most greedy solutions begin with sorting by the right key (end time, ratio, deadline).
- **Choosing the right criterion is the whole problem.** Earliest *start* fails for intervals; earliest *end* works.
- **Test against brute force** on small inputs, and try adversarial cases (the `{1, 3, 4}` coin example).
- **Look for an exchange argument** to justify correctness in interviews.
- **Heaps support dynamic greedy** (always take the current best among changing candidates).
- **Greedy does not work for 0/1 knapsack,** longest path, or general coin change.
- **Tie-breaking can matter;** define it explicitly.
- **If greedy feels too easy,** double check it with a counterexample search.

## 6. Check yourself

1. What two properties must a problem have for greedy to be correct?
2. Why does earliest-end-time work for interval scheduling but earliest-start-time does not?
3. Give a case where greedy coin change fails.
4. How does fractional knapsack differ from 0/1 knapsack in the right algorithm?
5. How does Huffman coding use a greedy choice?
6. What is an exchange argument?

<details>
<summary>Answers</summary>

1. The greedy-choice property and optimal substructure.
2. Taking the interval that ends earliest leaves the most room for the rest. Earliest start could pick a very long interval that blocks many others.
3. Coins `{1, 3, 4}`, amount `6`: greedy gives `4+1+1` (3 coins) but `3+3` (2 coins) is optimal.
4. Fractional knapsack is greedy by value/weight ratio. 0/1 knapsack needs DP because you cannot split items.
5. It repeatedly merges the two least frequent symbols, which provably yields an optimal prefix code.
6. A proof technique: take any optimal solution and show swapping in the greedy choice never makes it worse, so a greedy-first optimal solution exists.

</details>
