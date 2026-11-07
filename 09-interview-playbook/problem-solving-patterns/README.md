# Problem-Solving Patterns for Coding Interviews

## 1. The concept

Interview problems look endless, but they are built from a **small set of patterns**. Strong candidates do not memorize 500 solutions; they **recognize the shape** of a problem ("sorted array and a target: two pointers", "contiguous subarray: sliding window or prefix sums", "shortest path in an unweighted grid: BFS") and apply a template. This chapter gives you the **method** for attacking any problem, then **16 patterns** with templates, complexity and tested code. The [exercises](exercises.md) drill them with 13 more problems, and [system design](../system-design-basics/README.md) covers the other big interview round.

Prerequisites: [Big-O](../../01-complexity/big-o/README.md), [data structures](../../02-data-structures/arrays-strings/README.md) and [algorithms](../../03-algorithms/sorting/README.md). This chapter is where they come together.

## 2. A method for any problem: UMPIRE

| Step | What you do | Out loud, say... |
|------|-------------|------------------|
| **U**nderstand | Restate the problem; ask about input size, types, duplicates, negatives, empty input, sorted or not, memory limits | "So the input is a list of ints, possibly empty. Can it contain negatives? Do I return indices or values?" |
| **M**atch | Which pattern does this smell like? | "A sorted array with a target pair suggests two pointers." |
| **P**lan | Describe the approach and complexity **before** coding; start with brute force, then improve | "Brute force is O(n^2). With a hash map I can do O(n) time and O(n) space." |
| **I**mplement | Write clean code with meaningful names; talk while you write | "I'll keep a map from value to index." |
| **R**eview | Trace through an example and **edge cases** by hand | "For `[]`, we return immediately. For duplicates..." |
| **E**valuate | State time and space complexity, then discuss trade-offs and improvements | "O(n) time, O(n) space; if memory mattered I'd sort and use two pointers." |

### Habits that separate strong candidates

1. **Clarify before coding.** Two minutes of questions prevents ten minutes of wrong code.
2. **Brute force first, then optimize.** A correct slow solution beats a half-finished clever one. State the bottleneck ("the inner loop re-scans the array") and which pattern removes it.
3. **Think aloud.** The interviewer is grading your reasoning, not only the final code.
4. **Use examples.** Work a small example by hand; it often reveals the algorithm.
5. **Name the invariant.** "The window always contains no duplicates"; "everything left of `i` is processed."
6. **Test your own code** with a normal case, an empty/single-element case, duplicates, extremes (large, negative, all same).
7. **Know complexity cold** (time and space, average vs worst).
8. **Do not panic when stuck.** Say what you know, try a smaller example, ask for a hint. Interviewers want to see how you recover.

### Constraint-to-complexity cheat sheet

| Input size `n` | Likely target complexity | Typical approaches |
|----------------|--------------------------|--------------------|
| n <= 10 | O(n!) | permutations, brute-force backtracking |
| n <= 20 | O(2^n) | subsets, bitmask DP, backtracking |
| n <= 100 | O(n^3) | triple loops, Floyd-Warshall |
| n <= 1,000 | O(n^2) | double loops, simple DP tables |
| n <= 100,000 | O(n log n) | sorting, heaps, binary search, divide and conquer |
| n <= 1,000,000 | O(n) | hash maps, two pointers, sliding window, prefix sums |
| n up to 10^9 or more | O(log n) / O(1) | binary search, math |

(Python handles roughly 10^7 simple operations per second, so n = 10^5 with O(n^2) is too slow, n = 10^5 with O(n log n) is fine.)

## 3. Pattern 1: Two pointers

**Recognize:** sorted array/string, pairs/triples summing to a target, palindromes, merging, removing in place.
**Idea:** two indices move toward each other (or in the same direction), using order to discard options. **Time O(n), space O(1).**

```python
def two_sum_sorted(nums, target):
    """Indices of two numbers in a SORTED list that add up to target."""
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        s = nums[lo] + nums[hi]
        if s == target:
            return [lo, hi]
        if s < target:
            lo += 1                      # need a bigger sum: move the left pointer right
        else:
            hi -= 1                      # need a smaller sum: move the right pointer left
    return []

def is_palindrome(s):
    cleaned = [c.lower() for c in s if c.isalnum()]
    lo, hi = 0, len(cleaned) - 1
    while lo < hi:
        if cleaned[lo] != cleaned[hi]:
            return False
        lo, hi = lo + 1, hi - 1
    return True

def remove_duplicates_in_place(nums):
    """Same-direction pointers: write index trails the read index. Returns the new length."""
    if not nums:
        return 0
    write = 1
    for read in range(1, len(nums)):
        if nums[read] != nums[write - 1]:
            nums[write] = nums[read]
            write += 1
    return write

def three_sum(nums):
    """All unique triplets summing to zero: sort, fix one, two-pointer the rest. O(n^2)."""
    nums, out = sorted(nums), []
    for i, a in enumerate(nums):
        if i and a == nums[i - 1]:
            continue                                     # skip duplicate anchors
        lo, hi = i + 1, len(nums) - 1
        while lo < hi:
            s = a + nums[lo] + nums[hi]
            if s < 0: lo += 1
            elif s > 0: hi -= 1
            else:
                out.append([a, nums[lo], nums[hi]])
                lo, hi = lo + 1, hi - 1
                while lo < hi and nums[lo] == nums[lo - 1]:
                    lo += 1
    return out

assert two_sum_sorted([1, 3, 4, 6, 9], 10) == [0, 4] or two_sum_sorted([1, 3, 4, 6, 9], 10) == [2, 3]
assert is_palindrome("A man, a plan, a canal: Panama") and not is_palindrome("hello")
data = [1, 1, 2, 2, 2, 3]
assert remove_duplicates_in_place(data) == 3 and data[:3] == [1, 2, 3]
assert three_sum([-1, 0, 1, 2, -1, -4]) == [[-1, -1, 2], [-1, 0, 1]]
print("two pointers ok")
```

## 4. Pattern 2: Sliding window

**Recognize:** longest/shortest/best **contiguous** subarray or substring with a property (at most k distinct, sum >= target, no repeats).
**Idea:** keep a window `[left, right]`; expand `right`; shrink `left` while the window is invalid; update the answer. Each element enters and leaves once: **O(n)**.

```python
def longest_unique_substring(s):
    """Length of the longest substring without repeating characters."""
    last_seen, left, best = {}, 0, 0
    for right, ch in enumerate(s):
        if ch in last_seen and last_seen[ch] >= left:
            left = last_seen[ch] + 1                     # jump the left edge past the previous occurrence
        last_seen[ch] = right
        best = max(best, right - left + 1)
    return best

def max_sum_subarray_k(nums, k):
    """Fixed-size window: maximum sum of any k consecutive elements."""
    window = sum(nums[:k])
    best = window
    for i in range(k, len(nums)):
        window += nums[i] - nums[i - k]                  # slide: add the new element, drop the old one
        best = max(best, window)
    return best

def min_subarray_len(target, nums):
    """Variable-size window: shortest subarray with sum >= target (positive numbers)."""
    left = total = 0
    best = float("inf")
    for right, x in enumerate(nums):
        total += x
        while total >= target:                           # shrink while still valid
            best = min(best, right - left + 1)
            total -= nums[left]
            left += 1
    return 0 if best == float("inf") else best

def longest_k_distinct(s, k):
    from collections import defaultdict
    counts, left, best = defaultdict(int), 0, 0
    for right, ch in enumerate(s):
        counts[ch] += 1
        while len(counts) > k:
            counts[s[left]] -= 1
            if counts[s[left]] == 0:
                del counts[s[left]]
            left += 1
        best = max(best, right - left + 1)
    return best

assert longest_unique_substring("abcabcbb") == 3 and longest_unique_substring("") == 0
assert max_sum_subarray_k([2, 1, 5, 1, 3, 2], 3) == 9
assert min_subarray_len(7, [2, 3, 1, 2, 4, 3]) == 2 and min_subarray_len(100, [1, 2]) == 0
assert longest_k_distinct("eceba", 2) == 3
print("sliding window ok")
```

## 5. Pattern 3: Prefix sums and hash maps

**Recognize:** range sums, "subarray with sum k", counting pairs, frequency questions, "have I seen this before?", grouping.
**Idea:** precompute cumulative totals so any range sum is a subtraction; use a dictionary for O(1) lookup of complements, counts and first positions.

```python
from collections import defaultdict, Counter

def two_sum(nums, target):
    """Hash map: value -> index. One pass, O(n) time and space."""
    seen = {}
    for i, x in enumerate(nums):
        if target - x in seen:
            return [seen[target - x], i]
        seen[x] = i
    return []

def subarray_sum_equals_k(nums, k):
    """Count subarrays with sum k (works with negatives). prefix[j] - prefix[i] == k."""
    count, prefix, seen = 0, 0, defaultdict(int)
    seen[0] = 1                                          # the empty prefix
    for x in nums:
        prefix += x
        count += seen[prefix - k]                        # how many earlier prefixes make a subarray of sum k?
        seen[prefix] += 1
    return count

class RangeSum:
    """O(n) build, O(1) per query."""
    def __init__(self, nums):
        self.prefix = [0]
        for x in nums:
            self.prefix.append(self.prefix[-1] + x)
    def query(self, i, j):                               # sum of nums[i..j] inclusive
        return self.prefix[j + 1] - self.prefix[i]

def group_anagrams(words):
    groups = defaultdict(list)
    for w in words:
        groups["".join(sorted(w))].append(w)             # the sorted letters are the canonical key
    return list(groups.values())

def top_k_frequent(nums, k):
    return [x for x, _ in Counter(nums).most_common(k)]

assert two_sum([2, 7, 11, 15], 9) == [0, 1]
assert subarray_sum_equals_k([1, 1, 1], 2) == 2 and subarray_sum_equals_k([1, -1, 0], 0) == 3
assert RangeSum([3, 1, 4, 1, 5]).query(1, 3) == 6
assert sorted(map(sorted, group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]))) == [["ate", "eat", "tea"], ["bat"], ["nat", "tan"]]
assert top_k_frequent([1, 1, 1, 2, 2, 3], 2) == [1, 2]
print("prefix sums and hashing ok")
```

## 6. Pattern 4: Fast and slow pointers (linked lists, cycles)

**Recognize:** cycle detection, middle of a linked list, "k-th from the end", detecting repeated values with O(1) memory.
**Idea:** one pointer moves 1 step, another 2 steps; if there is a cycle they meet; when the fast one finishes, the slow one is at the middle.

```python
class ListNode:
    def __init__(self, val, next=None):
        self.val, self.next = val, next

def build(values):
    head = None
    for v in reversed(values):
        head = ListNode(v, head)
    return head

def to_list(head):
    out = []
    while head:
        out.append(head.val); head = head.next
    return out

def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow is fast:
            return True
    return False

def middle(head):
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    return slow

def reverse(head):
    prev = None
    while head:
        head.next, prev, head = prev, head, head.next
    return prev

def nth_from_end(head, n):
    lead = head
    for _ in range(n):
        lead = lead.next                                 # lead is n steps ahead
    follow = head
    while lead:
        lead, follow = lead.next, follow.next
    return follow.val

a = build([1, 2, 3, 4, 5])
assert middle(a).val == 3 and nth_from_end(a, 2) == 4 and to_list(reverse(build([1, 2, 3]))) == [3, 2, 1]
loop = build([1, 2, 3]); loop.next.next.next = loop      # 3 points back to 1
assert has_cycle(loop) and not has_cycle(build([1, 2, 3]))
print("fast and slow ok")
```

## 7. Pattern 5: Binary search (including "binary search on the answer")

**Recognize:** sorted data; or a **monotonic yes/no question** over a numeric range ("is capacity C enough?"): minimize the largest, maximize the smallest.
**Idea:** halve the search space each step: **O(log n)** checks.

```python
def binary_search(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target: return mid
        if nums[mid] < target: lo = mid + 1
        else: hi = mid - 1
    return -1

def first_true(lo, hi, ok):
    """Smallest x in [lo, hi] with ok(x) True, assuming ok is False...False True...True."""
    while lo < hi:
        mid = (lo + hi) // 2
        if ok(mid):
            hi = mid                                     # mid might be the answer: keep it
        else:
            lo = mid + 1
    return lo

def ship_within_days(weights, days):
    """Minimum ship capacity so all packages ship in order within `days`."""
    def feasible(capacity):
        need, load = 1, 0
        for w in weights:
            if load + w > capacity:
                need, load = need + 1, 0
            load += w
        return need <= days
    return first_true(max(weights), sum(weights), feasible)

def search_rotated(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target: return mid
        if nums[lo] <= nums[mid]:                        # left half is sorted
            if nums[lo] <= target < nums[mid]: hi = mid - 1
            else: lo = mid + 1
        else:                                            # right half is sorted
            if nums[mid] < target <= nums[hi]: lo = mid + 1
            else: hi = mid - 1
    return -1

def my_sqrt(x):
    return first_true(0, x + 1, lambda m: m * m > x) - 1

assert binary_search([1, 3, 5, 7, 9], 7) == 3 and binary_search([1, 3], 2) == -1
assert ship_within_days([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5) == 15
assert search_rotated([4, 5, 6, 7, 0, 1, 2], 0) == 4 and search_rotated([4, 5, 6, 7, 0, 1, 2], 3) == -1
assert my_sqrt(8) == 2 and my_sqrt(16) == 4
print("binary search ok")
```

## 8. Pattern 6: BFS and DFS (graphs, grids, trees)

**Recognize:** connectivity, shortest path in an **unweighted** graph/grid (BFS), exploring all possibilities/components (DFS), level-order traversal, "number of islands".
**BFS** uses a queue and finds the fewest steps. **DFS** uses recursion or a stack and explores deeply. Both are **O(V + E)**.

```python
from collections import deque

def shortest_path_grid(grid, start, goal):
    """BFS on a grid of 0 (open) and 1 (wall); returns steps or -1."""
    rows, cols = len(grid), len(grid[0])
    queue, seen = deque([(start, 0)]), {start}
    while queue:
        (r, c), dist = queue.popleft()
        if (r, c) == goal:
            return dist
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0 and (nr, nc) not in seen:
                seen.add((nr, nc))                       # mark when ENQUEUED, not when dequeued
                queue.append(((nr, nc), dist + 1))
    return -1

def num_islands(grid):
    rows, cols = len(grid), len(grid[0])
    seen, count = set(), 0
    def dfs(r, c):
        if not (0 <= r < rows and 0 <= c < cols) or grid[r][c] != "1" or (r, c) in seen:
            return
        seen.add((r, c))
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            dfs(r + dr, c + dc)
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1" and (r, c) not in seen:
                count += 1
                dfs(r, c)
    return count

class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val, self.left, self.right = val, left, right

def level_order(root):
    out, queue = [], deque([root] if root else [])
    while queue:
        level = []
        for _ in range(len(queue)):                      # process one level at a time
            node = queue.popleft()
            level.append(node.val)
            queue.extend(n for n in (node.left, node.right) if n)
        out.append(level)
    return out

def max_depth(root):
    return 0 if not root else 1 + max(max_depth(root.left), max_depth(root.right))

def has_path_sum(root, target):
    if not root:
        return False
    if not root.left and not root.right:
        return root.val == target
    return has_path_sum(root.left, target - root.val) or has_path_sum(root.right, target - root.val)

maze = [[0, 0, 0], [1, 1, 0], [0, 0, 0]]
assert shortest_path_grid(maze, (0, 0), (2, 0)) == 6 and shortest_path_grid([[0, 1], [1, 0]], (0, 0), (1, 1)) == -1
assert num_islands([list("11000"), list("11000"), list("00100"), list("00011")]) == 3
tree = TreeNode(3, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))
assert level_order(tree) == [[3], [9, 20], [15, 7]] and max_depth(tree) == 3 and has_path_sum(tree, 30)
print("bfs and dfs ok")
```

## 9. Pattern 7: Backtracking

**Recognize:** "generate all" subsets, permutations, combinations, N-Queens, sudoku, word search, partitions.
**Idea:** build a candidate step by step; **choose, explore, un-choose**; prune invalid branches early. Cost is exponential, so check constraints first.

```python
def subsets(nums):
    out = []
    def go(start, path):
        out.append(path[:])                              # every path is a valid subset
        for i in range(start, len(nums)):
            path.append(nums[i])                         # choose
            go(i + 1, path)                              # explore
            path.pop()                                   # un-choose
    go(0, [])
    return out

def permutations(nums):
    out, used = [], [False] * len(nums)
    def go(path):
        if len(path) == len(nums):
            out.append(path[:]); return
        for i, x in enumerate(nums):
            if not used[i]:
                used[i] = True; path.append(x)
                go(path)
                path.pop(); used[i] = False
    go([])
    return out

def combination_sum(candidates, target):
    """Numbers may be reused; all unique combinations that sum to target."""
    out = []
    def go(start, path, remaining):
        if remaining == 0:
            out.append(path[:]); return
        for i in range(start, len(candidates)):
            if candidates[i] > remaining:
                continue                                 # prune
            path.append(candidates[i])
            go(i, path, remaining - candidates[i])       # i, not i+1: reuse allowed
            path.pop()
    go(0, [], target)
    return out

def n_queens_count(n):
    cols, d1, d2 = set(), set(), set()
    def go(r):
        if r == n:
            return 1
        total = 0
        for c in range(n):
            if c in cols or r - c in d1 or r + c in d2:
                continue                                 # attacked: prune
            cols.add(c); d1.add(r - c); d2.add(r + c)
            total += go(r + 1)
            cols.remove(c); d1.remove(r - c); d2.remove(r + c)
        return total
    return go(0)

assert sorted(subsets([1, 2, 3])) == sorted([[], [1], [2], [3], [1, 2], [1, 3], [2, 3], [1, 2, 3]])
assert len(permutations([1, 2, 3])) == 6 and [1, 3, 2] in permutations([1, 2, 3])
assert sorted(combination_sum([2, 3, 6, 7], 7)) == [[2, 2, 3], [7]]
assert n_queens_count(6) == 4 and n_queens_count(8) == 92
print("backtracking ok")
```

## 10. Pattern 8: Dynamic programming

**Recognize:** "count the ways", "minimum/maximum cost", "is it possible", overlapping subproblems and optimal substructure (knapsack, coins, paths, subsequences, partitions).
**Recipe:** (1) define the **state** in words, (2) write the **recurrence**, (3) set **base cases**, (4) choose the **order** (bottom-up) or memoize (top-down), (5) read the answer, (6) optimize space if only the last row/value is needed. See [dynamic programming](../../03-algorithms/dynamic-programming/README.md).

```python
from functools import lru_cache

def coin_change(coins, amount):
    """Fewest coins to make `amount`, or -1. dp[a] = 1 + min(dp[a - c])."""
    INF = float("inf")
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and dp[a - c] + 1 < dp[a]:
                dp[a] = dp[a - c] + 1
    return -1 if dp[amount] == INF else dp[amount]

def climb_stairs(n):
    a, b = 1, 1                                          # ways(n) = ways(n-1) + ways(n-2): only two values needed
    for _ in range(n - 1):
        a, b = b, a + b
    return b

def house_robber(nums):
    take, skip = 0, 0
    for x in nums:
        take, skip = skip + x, max(take, skip)
    return max(take, skip)

def lis_length(nums):
    """Longest increasing subsequence in O(n log n) with patience sorting."""
    import bisect
    tails = []
    for x in nums:
        i = bisect.bisect_left(tails, x)
        if i == len(tails): tails.append(x)
        else: tails[i] = x
    return len(tails)

def lcs(a, b):
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            dp[i][j] = dp[i - 1][j - 1] + 1 if a[i - 1] == b[j - 1] else max(dp[i - 1][j], dp[i][j - 1])
    return dp[-1][-1]

def can_partition(nums):
    """Can the numbers be split into two equal-sum subsets? (0/1 knapsack feasibility)"""
    total = sum(nums)
    if total % 2:
        return False
    reachable = {0}
    for x in nums:
        reachable |= {r + x for r in reachable}
    return total // 2 in reachable

def unique_paths(m, n):
    row = [1] * n
    for _ in range(m - 1):
        for j in range(1, n):
            row[j] += row[j - 1]
    return row[-1]

assert coin_change([1, 2, 5], 11) == 3 and coin_change([2], 3) == -1
assert climb_stairs(10) == 89 and house_robber([2, 7, 9, 3, 1]) == 12
assert lis_length([10, 9, 2, 5, 3, 7, 101, 18]) == 4 and lcs("abcde", "ace") == 3
assert can_partition([1, 5, 11, 5]) and not can_partition([1, 2, 5]) and unique_paths(3, 7) == 28
print("dynamic programming ok")
```

## 11. Pattern 9: Heaps (top-k, streaming, merging)

**Recognize:** k largest/smallest, k-th element, merge k sorted lists, running median, scheduling by priority.
**Idea:** a heap gives the min (or max) in O(1) and updates in O(log n); a **size-k min-heap** tracks the top k in O(n log k).

```python
import heapq

def k_largest(nums, k):
    heap = []
    for x in nums:
        heapq.heappush(heap, x)
        if len(heap) > k:
            heapq.heappop(heap)                          # drop the smallest: the heap keeps the k largest
    return sorted(heap, reverse=True)

def kth_largest(nums, k):
    return heapq.nlargest(k, nums)[-1]

def merge_k_sorted(lists):
    heap = [(lst[0], i, 0) for i, lst in enumerate(lists) if lst]
    heapq.heapify(heap)
    out = []
    while heap:
        val, i, j = heapq.heappop(heap)
        out.append(val)
        if j + 1 < len(lists[i]):
            heapq.heappush(heap, (lists[i][j + 1], i, j + 1))
    return out

class RunningMedian:
    """Two heaps: a max-heap for the lower half, a min-heap for the upper half."""
    def __init__(self):
        self.low, self.high = [], []                     # low stores negatives (max-heap trick)
    def add(self, x):
        heapq.heappush(self.low, -x)
        heapq.heappush(self.high, -heapq.heappop(self.low))
        if len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))
    def median(self):
        if len(self.low) > len(self.high):
            return -self.low[0]
        return (-self.low[0] + self.high[0]) / 2

def min_meeting_rooms(intervals):
    ends, rooms = [], 0
    for start, end in sorted(intervals):
        if ends and ends[0] <= start:
            heapq.heapreplace(ends, end)                 # reuse the room that frees up first
        else:
            heapq.heappush(ends, end)
    return len(ends)

assert k_largest([3, 1, 5, 12, 2, 11], 3) == [12, 11, 5] and kth_largest([3, 2, 1, 5, 6, 4], 2) == 5
assert merge_k_sorted([[1, 4, 7], [2, 5], [3, 6, 9]]) == [1, 2, 3, 4, 5, 6, 7, 9]
rm = RunningMedian()
medians = []
for x in (5, 15, 1, 3):
    rm.add(x); medians.append(rm.median())
assert medians == [5, 10, 5, 4]
assert min_meeting_rooms([(0, 30), (5, 10), (15, 20)]) == 2
print("heaps ok")
```

## 12. Pattern 10: Stacks and monotonic stacks

**Recognize:** matching brackets, undo, expression evaluation, "next greater/smaller element", daily temperatures, largest rectangle.
**Idea:** a stack holds unfinished business; a **monotonic stack** keeps its items sorted so each element is pushed and popped once: **O(n)**.

```python
def valid_parentheses(s):
    pairs, stack = {")": "(", "]": "[", "}": "{"}, []
    for ch in s:
        if ch in "([{":
            stack.append(ch)
        elif not stack or stack.pop() != pairs.get(ch):
            return False
    return not stack

def next_greater(nums):
    """For each element, the next larger element to its right (or -1)."""
    out, stack = [-1] * len(nums), []                    # stack of indices with decreasing values
    for i, x in enumerate(nums):
        while stack and nums[stack[-1]] < x:
            out[stack.pop()] = x
        stack.append(i)
    return out

def daily_temperatures(temps):
    out, stack = [0] * len(temps), []
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            j = stack.pop()
            out[j] = i - j
        stack.append(i)
    return out

def largest_rectangle(heights):
    stack, best = [], 0
    for i, h in enumerate(heights + [0]):                # a sentinel 0 flushes the stack
        start = i
        while stack and stack[-1][1] > h:
            idx, height = stack.pop()
            best = max(best, height * (i - idx))
            start = idx
        stack.append((start, h))
    return best

def eval_rpn(tokens):
    stack = []
    for t in tokens:
        if t in "+-*/":
            b, a = stack.pop(), stack.pop()
            stack.append({"+": a + b, "-": a - b, "*": a * b, "/": int(a / b)}[t])
        else:
            stack.append(int(t))
    return stack[0]

assert valid_parentheses("{[()]}") and not valid_parentheses("(]") and not valid_parentheses("((")
assert next_greater([2, 1, 2, 4, 3]) == [4, 2, 4, -1, -1]
assert daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]) == [1, 1, 4, 2, 1, 1, 0, 0]
assert largest_rectangle([2, 1, 5, 6, 2, 3]) == 10
assert eval_rpn(["2", "1", "+", "3", "*"]) == 9
print("stacks ok")
```

## 13. Pattern 11: Intervals

**Recognize:** meetings, schedules, merging ranges, overlaps, insertions.
**Idea:** **sort by start**, then sweep, comparing each interval with the last merged one.

```python
def merge_intervals(intervals):
    out = []
    for start, end in sorted(intervals):
        if out and start <= out[-1][1]:
            out[-1][1] = max(out[-1][1], end)            # overlaps: extend the previous interval
        else:
            out.append([start, end])
    return out

def can_attend_all(intervals):
    ordered = sorted(intervals)
    return all(ordered[i][1] <= ordered[i + 1][0] for i in range(len(ordered) - 1))

def insert_interval(intervals, new):
    out, i = [], 0
    while i < len(intervals) and intervals[i][1] < new[0]:
        out.append(intervals[i]); i += 1                 # entirely before
    while i < len(intervals) and intervals[i][0] <= new[1]:
        new = [min(new[0], intervals[i][0]), max(new[1], intervals[i][1])]; i += 1     # overlapping: absorb
    out.append(new)
    out.extend(intervals[i:])                            # entirely after
    return out

assert merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]]) == [[1, 6], [8, 10], [15, 18]]
assert can_attend_all([(0, 5), (5, 10)]) and not can_attend_all([(0, 5), (4, 8)])
assert insert_interval([[1, 3], [6, 9]], [2, 5]) == [[1, 5], [6, 9]]
print("intervals ok")
```

## 14. Pattern 12: Union-Find (disjoint sets)

**Recognize:** dynamic connectivity, "are these connected?", number of components, grouping, cycle detection in undirected graphs, Kruskal's MST.
**Idea:** each set is a tree with a representative; `find` follows parents (with path compression), `union` links roots (by size). Near **O(1)** amortized per operation.

```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n
        self.components = n
    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]      # path compression (halving)
            x = self.parent[x]
        return x
    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False                                      # already connected
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]
        self.components -= 1
        return True

def count_components(n, edges):
    uf = UnionFind(n)
    for a, b in edges:
        uf.union(a, b)
    return uf.components

def redundant_connection(edges):
    uf = UnionFind(len(edges) + 1)
    for a, b in edges:
        if not uf.union(a, b):
            return [a, b]                                     # this edge closes a cycle

assert count_components(5, [(0, 1), (1, 2), (3, 4)]) == 2
assert redundant_connection([[1, 2], [1, 3], [2, 3]]) == [2, 3]
print("union-find ok")
```

## 15. Pattern 13: Topological sort (dependencies)

**Recognize:** prerequisites, build order, task scheduling, detecting cycles in a directed graph.
**Idea (Kahn's algorithm):** repeatedly take nodes with **in-degree 0**; if you cannot take all nodes, there is a cycle. **O(V + E)**.

```python
from collections import deque, defaultdict

def course_order(n, prerequisites):
    """Return one valid order of courses 0..n-1 or [] if impossible. prerequisites = [(course, needs)]."""
    graph, indegree = defaultdict(list), [0] * n
    for course, needs in prerequisites:
        graph[needs].append(course)
        indegree[course] += 1
    queue = deque(i for i in range(n) if indegree[i] == 0)
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for nxt in graph[node]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                queue.append(nxt)
    return order if len(order) == n else []

assert course_order(4, [(1, 0), (2, 0), (3, 1), (3, 2)])[0] == 0 and len(course_order(4, [(1, 0), (2, 0), (3, 1), (3, 2)])) == 4
assert course_order(2, [(0, 1), (1, 0)]) == []
print("topological sort ok")
```

## 16. Pattern 14: Trees and recursion

**Recognize:** anything on binary trees/BSTs (depth, validity, ancestors, paths, serialization).
**Idea:** solve for a node using answers from its children (**post-order**) or pass information down (**pre-order**). Remember BST in-order is sorted.

```python
def is_valid_bst(root, lo=float("-inf"), hi=float("inf")):
    if not root:
        return True
    if not lo < root.val < hi:
        return False
    return is_valid_bst(root.left, lo, root.val) and is_valid_bst(root.right, root.val, hi)

def lowest_common_ancestor(root, p, q):
    if not root or root.val in (p, q):
        return root
    left, right = lowest_common_ancestor(root.left, p, q), lowest_common_ancestor(root.right, p, q)
    return root if left and right else left or right

def diameter(root):
    best = 0
    def depth(node):
        nonlocal best
        if not node:
            return 0
        l, r = depth(node.left), depth(node.right)
        best = max(best, l + r)                               # the longest path through this node
        return 1 + max(l, r)
    depth(root)
    return best

def invert(root):
    if root:
        root.left, root.right = invert(root.right), invert(root.left)
    return root

bst = TreeNode(5, TreeNode(3, TreeNode(2), TreeNode(4)), TreeNode(8, TreeNode(7), TreeNode(9)))
assert is_valid_bst(bst) and not is_valid_bst(TreeNode(5, TreeNode(6), TreeNode(7)))
assert lowest_common_ancestor(bst, 2, 4).val == 3 and lowest_common_ancestor(bst, 2, 9).val == 5
assert diameter(bst) == 4
assert level_order(invert(TreeNode(1, TreeNode(2), TreeNode(3)))) == [[1], [3, 2]]
print("trees ok")
```

## 17. Pattern 15: Greedy

**Recognize:** "maximum number of non-overlapping...", "minimum number of ...", where a **locally best choice is provably globally best**. Always justify with an exchange argument or a counterexample check. See [greedy algorithms](../../03-algorithms/greedy/README.md).

```python
def max_non_overlapping(intervals):
    """Classic activity selection: always take the interval that ends earliest."""
    count, last_end = 0, float("-inf")
    for start, end in sorted(intervals, key=lambda iv: iv[1]):
        if start >= last_end:
            count += 1
            last_end = end
    return count

def can_jump(nums):
    reach = 0
    for i, x in enumerate(nums):
        if i > reach:
            return False
        reach = max(reach, i + x)
    return True

def min_jumps(nums):
    jumps = cur_end = farthest = 0
    for i in range(len(nums) - 1):
        farthest = max(farthest, i + nums[i])
        if i == cur_end:
            jumps += 1
            cur_end = farthest
    return jumps

def gas_station(gas, cost):
    if sum(gas) < sum(cost):
        return -1
    start = tank = 0
    for i in range(len(gas)):
        tank += gas[i] - cost[i]
        if tank < 0:
            start, tank = i + 1, 0                            # cannot start at or before i
    return start

assert max_non_overlapping([(1, 3), (2, 4), (3, 5), (0, 6), (5, 7)]) == 3
assert can_jump([2, 3, 1, 1, 4]) and not can_jump([3, 2, 1, 0, 4]) and min_jumps([2, 3, 1, 1, 4]) == 2
assert gas_station([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]) == 3
print("greedy ok")
```

## 18. Pattern 16: Bit manipulation and math tricks

**Recognize:** "find the single number", powers of two, counting bits, subsets via masks, XOR properties.
**Facts:** `x ^ x = 0`, `x ^ 0 = x`; `x & (x - 1)` clears the lowest set bit; `x & -x` isolates it; `1 << k` is `2**k`.

```python
def single_number(nums):
    result = 0
    for x in nums:
        result ^= x                                       # pairs cancel out
    return result

def is_power_of_two(n):
    return n > 0 and n & (n - 1) == 0

def count_bits(n):
    count = 0
    while n:
        n &= n - 1                                        # remove the lowest set bit each time
        count += 1
    return count

def subsets_bitmask(nums):
    return [[nums[i] for i in range(len(nums)) if mask >> i & 1] for mask in range(1 << len(nums))]

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

assert single_number([4, 1, 2, 1, 2]) == 4 and is_power_of_two(64) and not is_power_of_two(12)
assert count_bits(255) == 8 and len(subsets_bitmask([1, 2, 3])) == 8 and gcd(84, 36) == 12
print("bits and math ok")
```

## 19. Choosing the pattern: a decision guide

```text
Input is sorted (or can be)?            -> two pointers, binary search
Contiguous subarray/substring?          -> sliding window, prefix sums
"Have I seen this?" / counting / pairs  -> hash map / set
Shortest path, fewest steps (unweighted)-> BFS
Explore all / components / tree walk    -> DFS (recursion)
Generate all combos/permutations        -> backtracking
Optimal / count ways, overlapping subproblems -> dynamic programming
Top-k / k-th / streaming / merge k      -> heap
Next greater / matching brackets        -> (monotonic) stack
Overlapping ranges                      -> sort + sweep
Dynamic connectivity / groups           -> union-find
Dependencies / ordering                 -> topological sort
Locally best is globally best           -> greedy (prove it!)
Cycle or middle of a linked list        -> fast and slow pointers
Single odd one out / subsets / parity   -> bit manipulation
```

## 20. Two real-world examples

### Example 1: Deduplicating and deadline-checking in production code
An engineer building an alerting service needs "merge overlapping maintenance windows" (intervals), "count distinct users in the last 5 minutes" (sliding window + hash set), and "find the slowest 10 requests" (size-10 heap). None of this needs a library or a clever trick: it is the same patterns practiced for interviews, applied to real streams of data with the right complexity.

### Example 2: Dependency resolution in a build tool
A build system must order tasks (`compile` before `test` before `package`), detect circular dependencies, and find which tasks can run in parallel. That is **topological sort** (Kahn's algorithm); the "which can run now" frontier is exactly the in-degree-0 queue, and a leftover node means a cycle to report. Package managers like pip and npm solve their resolution problems with the same graph ideas.

## 21. Tips, tricks and pitfalls

- Identify the pattern from the **constraints and keywords** (sorted, contiguous, shortest, all, k-th, dependencies).
- Say the brute-force complexity first, then name the inefficiency your pattern removes.
- Off-by-one errors live at boundaries: use small examples and check `lo`/`hi`, window edges, and "inclusive vs exclusive".
- Mutating while iterating, shared mutable defaults and forgetting to copy `path` in backtracking (`path[:]`) are the most common Python bugs.
- Mark BFS nodes **visited when enqueued** to avoid duplicates and blow-ups.
- For recursion on big inputs, mind Python's recursion limit (`sys.setrecursionlimit` or iterate).
- Greedy needs a proof or a failing counterexample search; when unsure, use DP.
- State space and time complexity out loud, including hidden costs (`in list`, slicing, sorting).
- Write the function signature, examples and edge cases first; code second.
- Practice **deliberately**: after each problem, name the pattern and write its template from memory.

## 22. Check yourself

1. What does UMPIRE stand for and why clarify before coding?
2. What input sizes suggest O(n^2) versus O(n log n) targets?
3. Which pattern for: pair summing to a target in a sorted array; longest substring without repeats; shortest path in a grid; all subsets; k-th largest; matching brackets; merge overlapping meetings; are two nodes connected?
4. Why is BFS (not DFS) used for fewest steps in an unweighted graph?
5. What is the three-step rhythm of backtracking?
6. What are the steps to design a DP solution?
7. Why does a size-k min-heap find the k largest elements in O(n log k)?
8. When is greedy safe?

<details>
<summary>Answers</summary>

1. Understand, Match, Plan, Implement, Review, Evaluate. Clarifying avoids solving the wrong problem and reveals constraints (size, duplicates, ordering) that determine the right pattern.
2. n up to about 1,000 allows O(n^2); n up to about 100,000 needs O(n log n) or better; n around a million needs O(n).
3. Two pointers; sliding window; BFS; backtracking; heap (or `heapq.nlargest`); stack; sort + sweep (intervals); union-find (or BFS/DFS).
4. BFS explores level by level, so the first time it reaches a node is via the fewest edges; DFS may reach it through a longer path first.
5. Choose, explore (recurse), un-choose (undo the choice).
6. Define the state in words, write the recurrence, set base cases, pick the evaluation order (bottom-up or memoized top-down), read the answer, then optimize space if possible.
7. The heap holds only k items, so each of the n elements costs O(log k) to push/pop, giving O(n log k) overall.
8. When a locally optimal choice can be shown (by an exchange argument or proof) to be part of some globally optimal solution; otherwise use DP or search.

</details>

[Exercises](exercises.md) · [Summary](summary.md)
