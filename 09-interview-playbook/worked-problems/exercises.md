# Worked Problems: Exercises

Try each problem before opening its solution. These are the practice problems of this topic's lessons, collected in one place.

## Ten Worked Interview Problems

1. Apply the loop to **"Best Time to Buy and Sell Stock"** (one buy and one sell, maximize profit): brute force, bottleneck, one-pass solution, complexity.
2. Which pattern solves **"minimum window substring"** and what changes compared with problem 2?
3. Write the brute force and a random test for `search_rotated` yourself (already shown); then extend the tester to include repeated values and explain which inputs now break the solution.
4. Solve **"group anagrams"** (hash map keyed by sorted letters) and test it.
5. For **"Daily Temperatures"** (days until a warmer day), which structure, and why `O(n)` despite the nested `while`?
6. Choose the data structure for an **"autocomplete for a phone book"**: and the one for **"detect duplicate files by content"**.

<details>
<summary>Solutions</summary>

1. Brute force: all (buy, sell) pairs, `O(n^2)`. Bottleneck: for each sell day we scan all earlier days for the minimum. Fix: track the **lowest price so far** while scanning.
   ```python no-run
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
4. ```python no-run
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

## Worked Problems, Part 2

1. In Word Ladder, why do we mark a word `seen` when we enqueue it, not when we dequeue it?
2. Modify `ladder_length` to return the actual shortest path.
3. A grid has walls; find the shortest path from the top-left to the bottom-right corner (4 directions). Which algorithm?
4. Compute `edit_distance("kitten", "sitting")` and say which three operations produce it.
5. Show that `edit_distance` using only insertions and deletions equals `len(a) + len(b) - 2 * lcs(a, b)`.
6. Add a `WeekendSurcharge` pricing to the parking lot without editing `ParkingLot`.
7. Which pattern models "undo" in an editor, and what must each action store?

<details>
<summary>Solutions</summary>

1. Marking on enqueue guarantees each word enters the queue **once**; marking on dequeue lets the same word be queued many times by different neighbors, wasting time and memory (the distances stay correct, but the queue can blow up).
2. ```python no-run
   def ladder_path(begin, end, words):
       words = set(words)
       if end not in words:
           return []
       parent, queue = {begin: None}, deque([begin])
       while queue:
           word = queue.popleft()
           if word == end:
               path = []
               while word is not None:
                   path.append(word); word = parent[word]
               return path[::-1]
           for i in range(len(word)):
               for c in ascii_lowercase:
                   nxt = word[:i] + c + word[i + 1:]
                   if nxt in words and nxt not in parent:
                       parent[nxt] = word
                       queue.append(nxt)
       return []

   print(ladder_path("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]))      # ['hit', 'hot', 'dot', 'dog', 'cog']
   ```
3. **BFS** on the grid: each move costs 1, so BFS gives the shortest path (use A* with Manhattan distance for speed on large grids).
4. ```python no-run
   print(edit_distance("kitten", "sitting"))                # 3
   ```
   Substitute k to s, substitute e to i, insert g at the end.
5. ```python no-run
   def lcs_edit(a, b): return len(a) + len(b) - 2 * lcs(a, b)
   for _ in range(200):
       x, y = make_pair()
       # insert/delete-only distance via DP
       dp = [[0] * (len(y) + 1) for _ in range(len(x) + 1)]
       for i in range(len(x) + 1):
           for j in range(len(y) + 1):
               if i == 0: dp[i][j] = j
               elif j == 0: dp[i][j] = i
               elif x[i-1] == y[j-1]: dp[i][j] = dp[i-1][j-1]
               else: dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1])
       assert dp[-1][-1] == lcs_edit(x, y)
   print("identity holds")                                   # identity holds
   ```
   Intuition: keep the LCS characters, delete everything else from `a`, and insert everything else of `b`.
6. ```python no-run
   class WeekendSurcharge:
       def __init__(self, inner, extra): self.inner, self.extra = inner, extra
       def fee(self, minutes): return self.inner.fee(minutes) + self.extra
   print(ParkingLot(WeekendSurcharge(Hourly(3), 5)).checkout(25))       # 8
   ```
7. **Command**: every action is an object with `do()` and `undo()`; the editor keeps a stack of executed commands, and each command stores what it needs to reverse itself (for example the deleted text and its position).

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Ten Worked Interview Problems](01-ten-worked-interview-problems.md) · [Worked Problems, Part 2](02-graph-string-dp-and-design-rounds.md)
