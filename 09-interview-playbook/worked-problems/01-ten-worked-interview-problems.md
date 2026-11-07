# Ten Worked Interview Problems (with the Thinking, Not Just the Code)

**Prerequisites:** [problem-solving patterns](../problem-solving-patterns/README.md), the [algorithms](../../03-algorithms/README.md) and [data structures](../../02-data-structures/README.md) parts. **You will learn:** how to walk through a problem the way a strong candidate does: **clarify, work an example, state the brute force, find the bottleneck, apply a pattern, code it, analyze it, test it**. Ten classic problems, one for each major pattern, each with its reasoning, a verified solution that is **randomly tested against a brute-force version**, the complexity, and the follow-up questions interviewers ask next.

## 0. The loop to follow every time

```text
1. CLARIFY    inputs, ranges, duplicates, empty input, negatives, sorted?, what to return if impossible?
2. EXAMPLE    work a small case by hand; invent an edge case
3. BRUTE FORCE say the obvious solution out loud and its complexity (it is a valid start!)
4. BOTTLENECK where is the wasted work? repeated scans? sorting? recomputation?
5. PATTERN    which tool removes it? (hash map, two pointers, window, stack, heap, binary search, BFS/DFS, DP...)
6. CODE       clean, named variables, handle edge cases
7. ANALYZE    time and space, best/worst case
8. TEST       walk the example, then edge cases (empty, one item, duplicates, all equal, huge)
```

Silence is the enemy: **narrate your reasoning**. Interviewers grade the process as much as the answer. Below, each problem is written in that order.

A tiny harness we will reuse to compare a fast solution with a slow, obviously-correct one on random inputs:

```python
import random
random.seed(2026)

def check(fast, slow, make_input, trials=500):
    """Run both on many random inputs; any mismatch raises with the failing input."""
    for _ in range(trials):
        args = make_input()
        expected, got = slow(*args), fast(*args)
        assert got == expected, f"input {args}: expected {expected}, got {got}"
    return f"{trials} random tests passed"
```

## 1. Two Sum (hash map)

**Problem.** Given a list of integers and a target, return the indexes of two different elements that add to the target (exactly one solution exists).

**Clarify.** Can an element be used twice? (No.) Negatives? (Yes.) Return order? (Any.)

**Brute force.** Try every pair: `O(n^2)` time, `O(1)` space.

**Bottleneck.** For each `x` we search the rest of the list for `target - x`: a *lookup*. Lookups are what a hash map is for.

**Idea.** Walk the list once; before storing `x`, ask "have I already seen `target - x`?"

```python
def two_sum(nums, target):
    seen = {}                                            # value -> index
    for i, x in enumerate(nums):
        if target - x in seen:
            return sorted((seen[target - x], i))
        seen[x] = i
    return None

def two_sum_slow(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return None

print(two_sum([2, 7, 11, 15], 9), two_sum([3, 3], 6), two_sum([1, 2], 10))      # [0, 1] [0, 1] None

def agrees(nums, target):                            # compare by VALIDITY: several correct answers may exist
    a, b = two_sum(nums, target), two_sum_slow(nums, target)
    return (a is None) == (b is None) and (a is None or (a[0] != a[1] and nums[a[0]] + nums[a[1]] == target))

print(check(lambda n, t: agrees(n, t), lambda n, t: True,
            lambda: ([random.randint(-9, 9) for _ in range(random.randint(0, 8))], random.randint(-10, 10))))
# 500 random tests passed
```

**Complexity.** `O(n)` time, `O(n)` space (the classic time-for-space trade).

**Follow-ups.** *Input sorted?* Two pointers from both ends: `O(n)` time, `O(1)` space. *Return all pairs?* Track counts. *Three sum?* Sort, fix one, two-pointer the rest: `O(n^2)`.

## 2. Longest Substring Without Repeating Characters (sliding window)

**Problem.** Length of the longest substring of `s` with all distinct characters.

**Brute force.** Check every substring for duplicates: `O(n^3)` (or `O(n^2)` with a set).

**Bottleneck.** When we extend a substring we re-examine characters we already know are unique.

**Idea.** Keep a **window** `[left, right]` with no duplicates. Move `right` forward; if `s[right]` is already inside the window, move `left` just past its previous position. Each character enters and leaves once.

```python
def longest_unique(s):
    last_seen, left, best = {}, 0, 0
    for right, ch in enumerate(s):
        if ch in last_seen and last_seen[ch] >= left:    # the duplicate is inside the current window
            left = last_seen[ch] + 1                     # shrink the window past it
        last_seen[ch] = right
        best = max(best, right - left + 1)
    return best

def longest_unique_slow(s):
    return max((len(set(s[i:j])) == j - i and j - i for i in range(len(s)) for j in range(i + 1, len(s) + 1)), default=0) or 0

print(longest_unique("abcabcbb"), longest_unique("bbbbb"), longest_unique("pwwkew"), longest_unique(""))      # 3 1 3 0
print(check(longest_unique, longest_unique_slow, lambda: ("".join(random.choice("abcd") for _ in range(random.randint(0, 12))),)))
# 500 random tests passed
```

Trace on `"abcabcbb"`: window grows to `abc` (3); at the second `a` the left edge jumps past the first `a`, giving `bca`; the best stays 3.

**Complexity.** `O(n)` time, `O(min(n, alphabet))` space.

**Follow-ups.** At most `k` distinct characters? Keep a count map and shrink while distinct `> k`. Return the substring itself? Remember the best `left`.

## 3. Merge Intervals (sort first)

**Problem.** Merge all overlapping intervals: `[[1,3],[2,6],[8,10],[15,18]]` becomes `[[1,6],[8,10],[15,18]]`.

**Brute force.** Repeatedly compare every pair and merge until nothing changes: `O(n^2)` or worse.

**Bottleneck.** Overlaps are hard to find in random order.

**Idea.** **Sort by start**; then any overlap is with the *last merged* interval, so one pass suffices.

```python
def merge_intervals(intervals):
    merged = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:            # overlaps the previous interval: extend it
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged

print(merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]]))        # [[1, 6], [8, 10], [15, 18]]
print(merge_intervals([[1, 4], [4, 5]]), merge_intervals([]), merge_intervals([[1, 4], [2, 3]]))      # [[1, 5]] [] [[1, 4]]
```

A brute force is awkward here, so test the *property* that matters instead: the merged output covers exactly the same integer points, is sorted, and has no overlaps.

```python
def covers_same_points(intervals):
    out = merge_intervals([list(i) for i in intervals])
    points_in = {p for s, e in intervals for p in range(s, e + 1)}
    points_out = {p for s, e in out for p in range(s, e + 1)}
    sorted_ok = all(out[i][1] < out[i + 1][0] for i in range(len(out) - 1))      # strictly separated, so no overlaps remain
    return points_in == points_out and sorted_ok

def random_intervals():
    result = []
    for _ in range(random.randint(0, 6)):
        s = random.randint(0, 12); result.append((s, s + random.randint(0, 5)))
    return (result,)
print(check(lambda iv: covers_same_points(iv), lambda iv: True, random_intervals))             # 500 random tests passed
```

**Complexity.** `O(n log n)` for the sort, `O(n)` for the pass. **Follow-ups.** Insert one interval into a sorted list in `O(n)`; minimum meeting rooms (heap of end times, see [priority queues](../../02-data-structures/heaps/02-priority-queue-applications.md)); do touching intervals `[1,4],[4,5]` merge? (Clarify: here yes, `start <= end`.)

## 4. Valid Parentheses (stack)

**Problem.** Given a string of `()[]{}`, decide if brackets are properly nested and closed.

**Brute force.** Repeatedly delete `()`, `[]`, `{}` until nothing changes; valid if the string becomes empty: `O(n^2)`.

**Idea.** The most recently opened bracket must be the next one closed: **last in, first out**, i.e. a [stack](../../02-data-structures/stacks-queues/01-stacks.md).

```python
def is_valid(s):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in s:
        if ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False                             # a closer with nothing (or the wrong thing) to match
        else:
            stack.append(ch)
    return not stack                                     # leftovers are unclosed openers

def is_valid_slow(s):
    while True:
        t = s.replace("()", "").replace("[]", "").replace("{}", "")
        if t == s:
            return s == ""
        s = t

print(is_valid("()[]{}"), is_valid("([{}])"), is_valid("(]"), is_valid("(("), is_valid(""))      # True True False False True
print(check(is_valid, is_valid_slow, lambda: ("".join(random.choice("()[]{}") for _ in range(random.randint(0, 10))),)))
# 500 random tests passed
```

**Complexity.** `O(n)` time, `O(n)` space. **Follow-ups.** Minimum insertions to make it valid (count unmatched closers and leftover openers); longest valid parentheses (stack of indexes or DP); generate all valid combinations of `n` pairs ([backtracking](../../03-algorithms/recursion-backtracking/02-backtracking.md)).

## 5. Top K Frequent Elements (heap / counting)

**Problem.** Return the `k` most frequent values in a list.

**Brute force.** Count, then sort all distinct values by count: `O(n log n)`.

**Bottleneck.** We sort *everything* to keep only `k`.

**Idea.** Count with a hash map, then keep only the best `k` with a size-`k` [min-heap](../../02-data-structures/heaps/02-priority-queue-applications.md) (`O(n log k)`), or use **bucket sort by frequency** for `O(n)`.

```python
from collections import Counter
import heapq

def top_k_frequent(nums, k):
    counts = Counter(nums)
    return heapq.nlargest(k, counts, key=lambda v: (counts[v], -v))      # tie-break by smaller value for determinism

def top_k_buckets(nums, k):                                              # O(n): index = frequency
    counts = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for value, c in counts.items():
        buckets[c].append(value)
    result = []
    for c in range(len(buckets) - 1, 0, -1):
        for value in sorted(buckets[c]):
            result.append(value)
            if len(result) == k:
                return result
    return result

def top_k_slow(nums, k):
    counts = Counter(nums)
    return sorted(counts, key=lambda v: (-counts[v], v))[:k]

print(top_k_frequent([1, 1, 1, 2, 2, 3], 2), top_k_buckets([1, 1, 1, 2, 2, 3], 2))      # [1, 2] [1, 2]
mk = lambda: ([random.randint(0, 5) for _ in range(random.randint(1, 15))], random.randint(1, 4))
print(check(top_k_frequent, top_k_slow, mk), check(top_k_buckets, top_k_slow, mk))
# 500 random tests passed 500 random tests passed
```

**Complexity.** Heap `O(n log k)`, buckets `O(n)` time, `O(n)` space. **Follow-ups.** Top-k in a **stream** too large for memory (count-min sketch plus a heap); k-th largest element (quickselect, `O(n)` average).

## 6. Number of Islands (graph search on a grid)

**Problem.** Count groups of connected `1`s (up, down, left, right) in a grid of `0`/`1`.

**Idea.** Each unvisited `1` starts a new island; flood it with BFS/DFS so its cells are not counted again. A grid is an implicit [graph](../../02-data-structures/graphs/01-graph-basics-bfs-dfs.md).

```python
from collections import deque

def num_islands(grid):
    if not grid:
        return 0
    rows, cols = len(grid), len(grid[0])
    seen, islands = set(), 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1 and (r, c) not in seen:
                islands += 1                              # a new island: explore all of it
                queue = deque([(r, c)])
                seen.add((r, c))
                while queue:
                    x, y = queue.popleft()
                    for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                        if 0 <= nx < rows and 0 <= ny < cols and grid[nx][ny] == 1 and (nx, ny) not in seen:
                            seen.add((nx, ny)); queue.append((nx, ny))
    return islands

def num_islands_uf(grid):                                 # an independent method: union-find (see the graphs lesson)
    if not grid:
        return 0
    rows, cols = len(grid), len(grid[0])
    parent = {}
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for r in range(rows):
        for c in range(cols):
            if grid[r][c]:
                parent[(r, c)] = (r, c)
    for (r, c) in list(parent):
        for nb in ((r + 1, c), (r, c + 1)):
            if nb in parent:
                parent[find((r, c))] = find(nb)
    return len({find(p) for p in parent})

grid = [[1, 1, 0, 0, 0], [1, 1, 0, 0, 0], [0, 0, 1, 0, 0], [0, 0, 0, 1, 1]]
print(num_islands(grid), num_islands([[0, 0], [0, 0]]), num_islands([[1]]), num_islands([]))      # 3 0 1 0
def rand_grid():
    width = random.randint(1, 5)
    return ([[random.randint(0, 1) for _ in range(width)] for _ in range(random.randint(1, 5))],)

print(check(num_islands, num_islands_uf, rand_grid))     # 500 random tests passed
```

Two completely different algorithms (BFS and union-find) agreeing on 500 random grids is strong evidence both are right.

**Complexity.** `O(rows * cols)` time and space. **Follow-ups.** Largest island area; islands as cells are added one at a time (union-find, `O(alpha)` per update); diagonal connectivity (8 directions); islands in a wrap-around (toroidal) grid.

## 7. Course Schedule (topological sort)

**Problem.** `n` courses, prerequisites `[a, b]` meaning "take `b` before `a`". Can you finish all courses? Return an order.

**Idea.** Courses and prerequisites form a directed graph; a valid order exists exactly when the graph has **no cycle**. [Kahn's algorithm](../../02-data-structures/graphs/02-graph-algorithms.md): repeatedly take courses with no remaining prerequisites.

```python
from collections import deque, defaultdict

def course_order(n, prerequisites):
    graph, indegree = defaultdict(list), [0] * n
    for course, before in prerequisites:
        graph[before].append(course)
        indegree[course] += 1
    queue = deque(c for c in range(n) if indegree[c] == 0)
    order = []
    while queue:
        c = queue.popleft()
        order.append(c)
        for nxt in graph[c]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)
    return order if len(order) == n else []               # fewer than n means a cycle

def is_valid_order(n, prerequisites, order):
    if sorted(order) != list(range(n)):
        return False
    position = {c: i for i, c in enumerate(order)}
    return all(position[before] < position[course] for course, before in prerequisites)

def has_cycle_slow(n, prerequisites):                     # DFS colouring: an independent cycle check
    graph = defaultdict(list)
    for course, before in prerequisites:
        graph[before].append(course)
    state = {}
    def dfs(u):
        state[u] = 1
        for v in graph[u]:
            if state.get(v) == 1 or (v not in state and dfs(v)):
                return True
        state[u] = 2
        return False
    return any(u not in state and dfs(u) for u in range(n))

print(course_order(4, [[1, 0], [2, 0], [3, 1], [3, 2]]), course_order(2, [[1, 0], [0, 1]]))      # [0, 1, 2, 3] []
def random_dag_or_not():
    n = random.randint(1, 6)
    return (n, [[random.randrange(n), random.randrange(n)] for _ in range(random.randint(0, 7))])
for _ in range(500):
    n, pre = random_dag_or_not()
    order = course_order(n, pre)
    assert (order == []) == has_cycle_slow(n, pre)        # an empty answer exactly when a cycle exists
    assert order == [] or is_valid_order(n, pre, order)   # and any returned order really satisfies every prerequisite
print("500 random tests passed")                          # 500 random tests passed
```

**Complexity.** `O(V + E)`. **Follow-ups.** Return *all* valid orders (backtracking); parallel semesters (longest path in the DAG = minimum number of terms); detect *which* courses form the cycle ([SCC](../../03-algorithms/graph-algorithms/02-connectivity-scc-and-flow.md)).

## 8. Coin Change (dynamic programming)

**Problem.** Fewest coins to make `amount` from given denominations (unlimited supply), or `-1`.

**Brute force.** Try all combinations (exponential). **Greedy?** Fails for `{4, 3, 1}` and 6 ([greedy lesson](../../03-algorithms/greedy/01-greedy-algorithms.md)).

**Bottleneck.** The same sub-amounts are solved repeatedly: overlapping subproblems with optimal substructure: [DP](../../03-algorithms/dynamic-programming/01-dp-thinking-and-1d-problems.md).

**Idea.** `dp[a]` = fewest coins for amount `a`; `dp[a] = 1 + min(dp[a - c])` over coins `c`.

```python
def coin_change(coins, amount):
    INF = float("inf")
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                dp[a] = min(dp[a], dp[a - c] + 1)
    return dp[amount] if dp[amount] != INF else -1

def coin_change_slow(coins, amount):                      # plain recursion without a memo: fine for tiny amounts
    if amount == 0:
        return 0
    results = [coin_change_slow(coins, amount - c) for c in coins if c <= amount]
    results = [r for r in results if r != -1]
    return min(results) + 1 if results else -1

print(coin_change([1, 2, 5], 11), coin_change([4, 3, 1], 6), coin_change([2], 3), coin_change([1], 0))      # 3 2 -1 0
print(check(coin_change, coin_change_slow, lambda: (random.sample(range(1, 8), random.randint(1, 3)), random.randint(0, 14))))
# 500 random tests passed
```

**Complexity.** `O(amount * len(coins))` time, `O(amount)` space. **Follow-ups.** Count the *ways* (loop order: coins outside); reconstruct the coins used (store the choice); coin change with limited supply (0/1 knapsack style).

## 9. LRU Cache (design problem)

**Problem.** Design a cache with `get(key)` and `put(key, value)` in `O(1)`, evicting the **least recently used** item when full.

**Idea.** Two needs: find by key in `O(1)` (hash map) and know/modify recency order in `O(1)` (a **doubly linked list** moving items to the front). Python's `OrderedDict` bundles both; interviewers often want you to build the pair yourself ([linked lists lesson](../../02-data-structures/linked-lists/02-doubly-and-circular.md)).

```python
class Node:
    def __init__(self, key=None, value=None):
        self.key, self.value, self.prev, self.next = key, value, None, None

class LRUCache:
    def __init__(self, capacity):
        self.capacity, self.map = capacity, {}
        self.head, self.tail = Node(), Node()              # sentinels: most recent right after head, least recent right before tail
        self.head.next, self.tail.prev = self.tail, self.head

    def _remove(self, node):
        node.prev.next, node.next.prev = node.next, node.prev
    def _add_front(self, node):
        node.prev, node.next = self.head, self.head.next
        self.head.next.prev = node
        self.head.next = node

    def get(self, key):
        if key not in self.map:
            return -1
        node = self.map[key]
        self._remove(node); self._add_front(node)          # touched: now the most recently used
        return node.value

    def put(self, key, value):
        if key in self.map:
            node = self.map[key]
            node.value = value
            self._remove(node); self._add_front(node)
            return
        if len(self.map) == self.capacity:
            lru = self.tail.prev                           # the least recently used
            self._remove(lru)
            del self.map[lru.key]
        node = Node(key, value)
        self.map[key] = node
        self._add_front(node)

from collections import OrderedDict
class LRUReference:                                        # the trusted version for random testing
    def __init__(self, capacity): self.capacity, self.data = capacity, OrderedDict()
    def get(self, key):
        if key not in self.data: return -1
        self.data.move_to_end(key); return self.data[key]
    def put(self, key, value):
        self.data[key] = value; self.data.move_to_end(key)
        if len(self.data) > self.capacity: self.data.popitem(last=False)

cache = LRUCache(2)
cache.put(1, 1); cache.put(2, 2)
print(cache.get(1))                                        # 1
cache.put(3, 3)                                            # evicts key 2 (least recently used)
print(cache.get(2), cache.get(3), cache.get(1))            # -1 3 1

for _ in range(300):
    cap = random.randint(1, 4)
    mine, ref = LRUCache(cap), LRUReference(cap)
    for _ in range(40):
        key = random.randint(0, 5)
        if random.random() < 0.5:
            val = random.randint(0, 99); mine.put(key, val); ref.put(key, val)
        else:
            assert mine.get(key) == ref.get(key)
print("LRU matched the reference on 300 random operation sequences")        # LRU matched the reference on 300 random operation sequences
```

**Complexity.** `O(1)` per operation, `O(capacity)` space. **Follow-ups.** Thread safety (a lock, or sharded caches); TTL expiry ([key-value store](../../05-databases/nosql/01-nosql-lab.md)); LFU (least *frequently* used); distributed cache and consistent hashing.

## 10. Search in a Rotated Sorted Array (binary search variant)

**Problem.** A sorted array of distinct numbers was rotated at an unknown pivot (`[4,5,6,7,0,1,2]`). Find a target's index in `O(log n)`.

**Brute force.** Linear scan, `O(n)`; the requirement says `O(log n)`, so binary search must apply despite the rotation.

**Idea.** At any midpoint, **at least one half is sorted**. Decide which half is sorted, check whether the target lies in that sorted half, and discard the other. Details in the [binary search lesson](../../03-algorithms/searching/01-linear-and-binary-search.md).

```python
def search_rotated(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[lo] <= nums[mid]:                          # the left half is sorted
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:                                              # the right half is sorted
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1

def rotated_case():
    n = random.randint(0, 9)
    base = sorted(random.sample(range(30), n))
    k = random.randint(0, n) if n else 0
    return (base[k:] + base[:k], random.randint(0, 30))

print(search_rotated([4, 5, 6, 7, 0, 1, 2], 0), search_rotated([4, 5, 6, 7, 0, 1, 2], 3), search_rotated([1], 1), search_rotated([], 5))      # 4 -1 0 -1
print(check(search_rotated, lambda nums, t: nums.index(t) if t in nums else -1, rotated_case))     # 500 random tests passed
```

**Complexity.** `O(log n)` time, `O(1)` space. **Follow-ups.** Find the minimum (the rotation point); duplicates allowed (worst case degrades to `O(n)` because `nums[lo] == nums[mid]` tells you nothing); search in a rotated array that is also huge or streamed.

## 11. Pattern recognition cheat sheet

| Clue in the problem | Reach for | Problems above |
|---------------------|-----------|----------------|
| "find a pair/complement", count frequencies, "seen before?" | hash map / set | 1, 5 |
| contiguous subarray/substring with a condition, "longest/shortest window" | sliding window, two pointers | 2 |
| intervals, schedules, "overlap" | sort by start (or end), then sweep; heap for rooms | 3 |
| matching/nesting, "undo", next greater element | stack / monotonic stack | 4 |
| "top k", "k-th", streaming extremes | heap or quickselect | 5 |
| grid or network connectivity, shortest path in an unweighted graph | BFS/DFS, union-find | 6 |
| dependencies, ordering, "can all be completed" | topological sort | 7 |
| "minimum/maximum/number of ways", overlapping subproblems | dynamic programming | 8 |
| "design a structure with O(1) operations" | hash map + linked list/heap/array | 9 |
| sorted (or rotated/monotonic) data, "minimum x such that..." | binary search (also on the answer) | 10 |

## 12. How to practice (timed)

1. Pick a problem. **Set 25 minutes.** First 5: clarify and work examples aloud (or write them). Next 15: solve and code. Last 5: test and analyze.
2. If stuck for 10 minutes with no direction, **read the pattern name only** (not the solution), then retry. Peeking at the whole solution trains recognition, not recall.
3. After solving, **write the brute force and a random tester** (as above). Finding your own bug is the best test of understanding.
4. Re-solve each problem **after 1 day, 1 week and 1 month** (the [spaced schedule](../../revision/schedule.md)).
5. Practice **explaining**: record yourself solving, or pair with a friend and swap interviewer and candidate roles.
6. Keep a log: problem, pattern, mistake made, the fix. Review it before real interviews.

## 13. Common interview mistakes

- Starting to code before clarifying inputs and constraints.
- Jumping to the optimal solution without stating the brute force (you lose the chance to show your reasoning and to have a fallback).
- Not testing: no walk-through of the example, no empty or single-element case.
- Silent coding: the interviewer cannot help you or give credit for thinking.
- Off-by-one errors in windows and binary search bounds (trace a tiny example).
- Mutating the input when it was not allowed, or ignoring duplicates and negatives.
- Claiming a complexity without justification (name the loop and what it iterates over).
- Giving up the simple correct solution for a clever fragile one.

## 14. Practice

1. Apply the loop to **"Best Time to Buy and Sell Stock"** (one buy and one sell, maximize profit): brute force, bottleneck, one-pass solution, complexity.
2. Which pattern solves **"minimum window substring"** and what changes compared with problem 2?
3. Write the brute force and a random test for `search_rotated` yourself (already shown); then extend the tester to include repeated values and explain which inputs now break the solution.
4. Solve **"group anagrams"** (hash map keyed by sorted letters) and test it.
5. For **"Daily Temperatures"** (days until a warmer day), which structure, and why `O(n)` despite the nested `while`?
6. Choose the data structure for an **"autocomplete for a phone book"**: and the one for **"detect duplicate files by content"**.

<details>
<summary>Solutions</summary>

1. Brute force: all (buy, sell) pairs, `O(n^2)`. Bottleneck: for each sell day we scan all earlier days for the minimum. Fix: track the **lowest price so far** while scanning.
   ```python
   def max_profit(prices):
       lowest, best = float("inf"), 0
       for p in prices:
           lowest = min(lowest, p)
           best = max(best, p - lowest)
       return best
   print(max_profit([7, 1, 5, 3, 6, 4]), max_profit([7, 6, 4, 3, 1]))      # 5 0
   ```
   `O(n)` time, `O(1)` space.
2. A sliding window with counts; the difference is the window must **contain** all required characters (shrink while still valid, to minimize), instead of **avoiding** duplicates.
3. With repeated values `nums[lo] == nums[mid]` can occur on both sides, so you cannot tell which half is sorted: the standard fix is `lo += 1` in that case (worst case `O(n)`), e.g. `[1,1,1,1,0,1]` breaks the distinct-values version.
4. ```python
   from collections import defaultdict
   def group_anagrams(words):
       groups = defaultdict(list)
       for w in words:
           groups["".join(sorted(w))].append(w)
       return sorted(sorted(g) for g in groups.values())
   print(group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]))      # [['ate', 'eat', 'tea'], ['bat'], ['nat', 'tan']]
   ```
5. A **monotonic stack** of indexes of days still waiting for a warmer day; each index is pushed once and popped at most once, so the total work is `O(n)`; the inner `while` does not restart for each item ([stack applications](../../02-data-structures/stacks-queues/03-stack-and-queue-applications.md)).
6. A **trie** for prefix autocomplete ([tries](../../02-data-structures/tries/01-tries.md)); a **hash map of content hashes** (SHA-256 of the file) to group duplicates.

</details>

## 15. Check yourself

1. What are the eight steps of the interview loop?
2. Why state the brute force first?
3. Name the pattern for: (a) pair summing to a target, (b) longest substring with a property, (c) overlapping meetings, (d) ordering with dependencies, (e) fewest coins.
4. Why test against a brute force with random inputs?
5. What is the signal that a problem wants binary search even though the data is not sorted?
6. What do interviewers listen for besides a correct answer?

<details>
<summary>Answers</summary>

1. Clarify, example, brute force, bottleneck, pattern, code, analyze, test.
2. It is a correct baseline, shows you understand the problem, exposes the bottleneck to attack, and gives you a fallback and a tester.
3. (a) hash map, (b) sliding window, (c) sort then sweep (or heap), (d) topological sort, (e) dynamic programming.
4. It finds edge-case bugs automatically and proves your clever solution matches an obviously correct one.
5. The data (or the answer space) is monotonic (a yes/no property flips once), such as a rotated sorted array or "smallest capacity that works".
6. Clear communication, structured reasoning, handling of edge cases, complexity analysis, testing habits and how you respond to hints.

</details>

[Back to the interview playbook](../problem-solving-patterns/README.md)
