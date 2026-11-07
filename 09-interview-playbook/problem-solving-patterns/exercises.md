# Problem-Solving Patterns: Exercises

For each exercise: **name the pattern first**, state brute-force and optimized complexity, then code it and test with edge cases. The functions from the lesson (`ListNode`, `TreeNode`, `UnionFind`, ...) are available.

1. **Container with most water.** Given heights, pick two lines forming the container holding the most water (`min(h[i], h[j]) * (j - i)`).
2. **Longest repeating character replacement.** Longest substring you can turn into one repeated letter with at most `k` replacements.
3. **Product of array except self** without division, in O(n).
4. **Valid anagram** and **first unique character**: do both with one hash-map idea.
5. **Find the duplicate number** in an array of `n + 1` integers from `1..n` using O(1) extra space and no modification.
6. **Koko eating bananas:** minimum eating speed `k` to finish all piles within `h` hours (`ceil(pile / k)` hours per pile).
7. **Word ladder length** (BFS): the shortest transformation from `begin` to `end` changing one letter at a time through a word list.
8. **Rotting oranges** (multi-source BFS): minutes until all oranges rot (`0` empty, `1` fresh, `2` rotten), or `-1`.
9. **Palindrome partitioning:** all ways to split a string into palindromes (backtracking).
10. **Word break:** can a string be segmented into dictionary words? (DP)
11. **Kth smallest element in a BST** (in-order traversal).
12. **Meeting rooms II without a heap:** compute the minimum rooms using sorted start/end arrays.
13. **Decide the pattern** (and complexity) for: (a) longest subarray with at most 2 zeros; (b) number of provinces in a friend matrix; (c) minimum number of arrows to burst balloons; (d) order of tasks with dependencies; (e) median of a stream.

<details>
<summary>Solutions</summary>

**1. Two pointers, O(n).** Move the pointer at the shorter line inward: the width shrinks, so only a taller line can help.
```python
def max_area(h):
    lo, hi, best = 0, len(h) - 1, 0
    while lo < hi:
        best = max(best, min(h[lo], h[hi]) * (hi - lo))
        if h[lo] < h[hi]: lo += 1
        else: hi -= 1
    return best
assert max_area([1, 8, 6, 2, 5, 4, 8, 3, 7]) == 49
```

**2. Sliding window, O(n).** A window is valid when `window_size - most_frequent_count <= k`.
```python
def character_replacement(s, k):
    counts, left, best, max_count = {}, 0, 0, 0
    for right, ch in enumerate(s):
        counts[ch] = counts.get(ch, 0) + 1
        max_count = max(max_count, counts[ch])
        while (right - left + 1) - max_count > k:
            counts[s[left]] -= 1
            left += 1
        best = max(best, right - left + 1)
    return best
assert character_replacement("AABABBA", 1) == 4 and character_replacement("ABAB", 2) == 4
```

**3. Prefix and suffix products, O(n) time, O(1) extra space (output excluded).**
```python
def product_except_self(nums):
    out, prefix = [1] * len(nums), 1
    for i, x in enumerate(nums):
        out[i] = prefix; prefix *= x
    suffix = 1
    for i in range(len(nums) - 1, -1, -1):
        out[i] *= suffix; suffix *= nums[i]
    return out
assert product_except_self([1, 2, 3, 4]) == [24, 12, 8, 6] and product_except_self([0, 2, 3]) == [6, 0, 0]
```

**4. Hash map / Counter.**
```python
from collections import Counter
def is_anagram(a, b): return Counter(a) == Counter(b)
def first_unique(s):
    counts = Counter(s)
    return next((i for i, ch in enumerate(s) if counts[ch] == 1), -1)
assert is_anagram("listen", "silent") and not is_anagram("a", "b") and first_unique("leetcode") == 0 and first_unique("aabb") == -1
```

**5. Fast and slow pointers (Floyd) treating values as "next" pointers, O(n) time, O(1) space.**
```python
def find_duplicate(nums):
    slow = fast = nums[0]
    while True:
        slow, fast = nums[slow], nums[nums[fast]]
        if slow == fast: break
    slow = nums[0]
    while slow != fast:
        slow, fast = nums[slow], nums[fast]
    return slow
assert find_duplicate([1, 3, 4, 2, 2]) == 2 and find_duplicate([3, 1, 3, 4, 2]) == 3
```

**6. Binary search on the answer.**
```python
import math
def min_eating_speed(piles, h):
    return first_true(1, max(piles), lambda k: sum(math.ceil(p / k) for p in piles) <= h)
assert min_eating_speed([3, 6, 7, 11], 8) == 4 and min_eating_speed([30, 11, 23, 4, 20], 5) == 30
```

**7. BFS over words (state = word).**
```python
from collections import deque
def ladder_length(begin, end, words):
    words = set(words)
    if end not in words: return 0
    queue, seen = deque([(begin, 1)]), {begin}
    while queue:
        word, steps = queue.popleft()
        if word == end: return steps
        for i in range(len(word)):
            for c in "abcdefghijklmnopqrstuvwxyz":
                nxt = word[:i] + c + word[i + 1:]
                if nxt in words and nxt not in seen:
                    seen.add(nxt); queue.append((nxt, steps + 1))
    return 0
assert ladder_length("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]) == 5
assert ladder_length("hit", "cog", ["hot", "dot", "dog", "lot", "log"]) == 0
```

**8. Multi-source BFS (start with all rotten oranges at time 0).**
```python
def oranges_rotting(grid):
    rows, cols = len(grid), len(grid[0])
    queue = deque((r, c, 0) for r in range(rows) for c in range(cols) if grid[r][c] == 2)
    fresh = sum(row.count(1) for row in grid)
    minutes = 0
    while queue:
        r, c, t = queue.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                grid[nr][nc] = 2; fresh -= 1; minutes = t + 1
                queue.append((nr, nc, t + 1))
    return minutes if fresh == 0 else -1
assert oranges_rotting([[2, 1, 1], [1, 1, 0], [0, 1, 1]]) == 4 and oranges_rotting([[2, 1, 1], [0, 1, 1], [1, 0, 1]]) == -1
```

**9. Backtracking with a palindrome check.**
```python
def partition_palindromes(s):
    out = []
    def go(start, path):
        if start == len(s):
            out.append(path[:]); return
        for end in range(start + 1, len(s) + 1):
            piece = s[start:end]
            if piece == piece[::-1]:
                path.append(piece); go(end, path); path.pop()
    go(0, [])
    return out
assert sorted(partition_palindromes("aab")) == [["a", "a", "b"], ["aa", "b"]]
```

**10. DP: `ok[i]` = prefix of length `i` can be segmented.**
```python
def word_break(s, words):
    words, ok = set(words), [True] + [False] * len(s)
    for i in range(1, len(s) + 1):
        ok[i] = any(ok[j] and s[j:i] in words for j in range(i))
    return ok[-1]
assert word_break("leetcode", ["leet", "code"]) and not word_break("catsandog", ["cats", "dog", "sand", "and", "cat"])
```

**11. In-order traversal of a BST is sorted; stop at k.**
```python
def kth_smallest(root, k):
    stack, node = [], root
    while True:
        while node:
            stack.append(node); node = node.left
        node = stack.pop()
        k -= 1
        if k == 0: return node.val
        node = node.right
bst2 = TreeNode(5, TreeNode(3, TreeNode(2), TreeNode(4)), TreeNode(6))
assert kth_smallest(bst2, 1) == 2 and kth_smallest(bst2, 4) == 5
```

**12. Sweep line with two sorted arrays.**
```python
def min_rooms(intervals):
    starts, ends = sorted(s for s, _ in intervals), sorted(e for _, e in intervals)
    rooms = best = j = 0
    for s in starts:
        while ends[j] <= s:
            j += 1; rooms -= 1
        rooms += 1
        best = max(best, rooms)
    return best
assert min_rooms([(0, 30), (5, 10), (15, 20)]) == 2 and min_rooms([(7, 10), (2, 4)]) == 1
```

**13.** (a) Sliding window (count zeros in the window), O(n). (b) Union-find or DFS over the matrix, O(n^2 alpha) / O(n^2). (c) Greedy on intervals sorted by end (minimum arrows = maximum non-overlapping groups). (d) Topological sort (Kahn). (e) Two heaps (running median), O(log n) per insert.

</details>

[Lesson](README.md) · [Summary](summary.md)
