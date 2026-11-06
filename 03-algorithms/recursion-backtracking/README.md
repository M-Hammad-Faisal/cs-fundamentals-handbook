# Recursion and Backtracking

## 1. The concept

**Recursion** solves a problem by having a function call itself on a smaller version of the same problem. Every recursive solution has two parts:

1. **Base case:** a small input answered directly (this stops the recursion).
2. **Recursive case:** reduce the problem, call yourself, and combine the result.

```python
def factorial(n):
    if n <= 1:                    # base case
        return 1
    return n * factorial(n - 1)   # recursive case
```

### The call stack

Each call gets a **stack frame** holding its arguments and local variables. Calls pile up until a base case returns, then frames unwind.

```
factorial(4)
  4 * factorial(3)
        3 * factorial(2)
              2 * factorial(1)  -> 1
```

Python's default limit is about 1000 frames (`sys.getrecursionlimit()`). Deeper recursion raises `RecursionError`. Python does **not** optimize tail calls, so convert deep recursion to a loop or an explicit stack.

### Thinking recursively

Trust the function: assume it already works for smaller inputs, and only decide how to use that answer for the current one.

| Question | Example (sum of a list) |
|----------|--------------------------|
| What is the smallest input? | Empty list: `0` |
| How do I shrink the input? | Drop the first element |
| How do I combine? | `first + sum(rest)` |

## 2. Analyzing recursion

Write a **recurrence** and solve it.

| Recurrence | Result | Example |
|------------|--------|---------|
| `T(n) = T(n-1) + O(1)` | `O(n)` | factorial, linear recursion |
| `T(n) = T(n/2) + O(1)` | `O(log n)` | binary search |
| `T(n) = 2T(n/2) + O(n)` | `O(n log n)` | merge sort |
| `T(n) = 2T(n-1) + O(1)` | `O(2ⁿ)` | naive subsets, naive Fibonacci |
| `T(n) = T(n-1) + T(n-2)` | `O(φⁿ)` ≈ `O(1.62ⁿ)` | naive Fibonacci |

**Space:** the call stack depth times the memory per frame. A recursion `n` deep uses `O(n)` stack space.

### Overlapping subproblems and memoization

Naive Fibonacci recomputes the same values exponentially often. **Memoization** caches results so each subproblem is solved once.

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)    # O(n)
```

This is the bridge to [dynamic programming](../dynamic-programming/README.md).

## 3. Recursion patterns

### Divide and conquer

Split the problem, solve the parts, merge: merge sort, quick sort, binary search, closest pair of points.

```python
def max_in(a, lo, hi):
    if lo == hi:
        return a[lo]
    mid = (lo + hi) // 2
    return max(max_in(a, lo, mid), max_in(a, mid + 1, hi))
```

### Tree recursion

Trees are recursive by definition: handle `None`, recurse on children, combine (see [trees](../../02-data-structures/trees/README.md)).

### Recursion on strings and arrays

```python
def reverse(s):
    return s if len(s) <= 1 else reverse(s[1:]) + s[0]    # O(n^2) copying; fine to learn

def power(x, n):                                          # fast exponentiation O(log n)
    if n == 0:
        return 1
    half = power(x, n // 2)
    return half * half if n % 2 == 0 else half * half * x
```

### Converting recursion to iteration

Replace the call stack with your own stack.

```python
def dfs_iterative(root):
    out, stack = [], [root]
    while stack:
        node = stack.pop()
        if node:
            out.append(node.val)
            stack.append(node.right)      # push right first so left is processed first
            stack.append(node.left)
    return out
```

## 4. Backtracking

**Backtracking** builds a solution one choice at a time and **undoes** a choice (backtracks) when it leads to a dead end. It explores a tree of decisions, pruning branches that cannot work.

### The template

```python
def backtrack(state, choices):
    if is_solution(state):
        record(state)
        return
    for choice in choices:
        if is_valid(state, choice):       # prune early
            make(state, choice)           # choose
            backtrack(state, next_choices)    # explore
            undo(state, choice)           # un-choose
```

### Subsets (include or exclude each element)

```python
def subsets(nums):
    res, cur = [], []
    def go(i):
        if i == len(nums):
            res.append(cur[:])            # copy the current path
            return
        go(i + 1)                         # exclude nums[i]
        cur.append(nums[i])               # include
        go(i + 1)
        cur.pop()                         # backtrack
    go(0)
    return res                            # 2^n subsets
```

### Permutations

```python
def permutations(nums):
    res = []
    def go(path, remaining):
        if not remaining:
            res.append(path[:])
            return
        for i in range(len(remaining)):
            path.append(remaining[i])
            go(path, remaining[:i] + remaining[i + 1:])
            path.pop()
    go([], nums)
    return res                            # n! permutations
```

### Combination sum (reuse allowed)

```python
def combination_sum(candidates, target):
    res, cur = [], []
    candidates.sort()
    def go(start, remaining):
        if remaining == 0:
            res.append(cur[:])
            return
        for i in range(start, len(candidates)):
            if candidates[i] > remaining:
                break                     # prune: sorted, so the rest are too big
            cur.append(candidates[i])
            go(i, remaining - candidates[i])     # i, not i+1: reuse allowed
            cur.pop()
    go(0, target)
    return res
```

### N-Queens

```python
def solve_n_queens(n):
    res, cols, d1, d2, board = [], set(), set(), set(), []
    def go(r):
        if r == n:
            res.append(["." * c + "Q" + "." * (n - c - 1) for c in board])
            return
        for c in range(n):
            if c in cols or (r - c) in d1 or (r + c) in d2:
                continue                  # prune attacked squares
            cols.add(c); d1.add(r - c); d2.add(r + c); board.append(c)
            go(r + 1)
            cols.remove(c); d1.remove(r - c); d2.remove(r + c); board.pop()
    go(0)
    return res
```

### Word search in a grid

```python
def exist(board, word):
    rows, cols = len(board), len(board[0])
    def go(r, c, i):
        if i == len(word):
            return True
        if not (0 <= r < rows and 0 <= c < cols) or board[r][c] != word[i]:
            return False
        tmp, board[r][c] = board[r][c], "#"          # mark visited
        found = any(go(r + dr, c + dc, i + 1)
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        board[r][c] = tmp                            # restore
        return found
    return any(go(r, c, 0) for r in range(rows) for c in range(cols))
```

### Generate parentheses

```python
def generate_parentheses(n):
    res = []
    def go(cur, open_, close):
        if len(cur) == 2 * n:
            res.append(cur)
            return
        if open_ < n:
            go(cur + "(", open_ + 1, close)
        if close < open_:
            go(cur + ")", open_, close + 1)       # only close if it stays valid
    go("", 0, 0)
    return res
```

### Complexity

Backtracking is usually exponential or factorial in the worst case: subsets `O(2ⁿ · n)`, permutations `O(n! · n)`. **Pruning** and good ordering cut the real work dramatically even when the worst case stays the same.

## 5. Two real-world examples

### Example 1: Sudoku and puzzle solvers, constraint solving

A Sudoku solver fills a cell, checks the row, column and box constraints, recurses to the next cell, and **backtracks** when a dead end appears. The same idea powers configuration solvers (package version resolution in pip and npm tries a version, checks conflicts, and backs off), scheduling tools that place meetings subject to constraints, and regular-expression engines that try alternatives and back up on failure (which is why some regexes suffer "catastrophic backtracking").

### Example 2: File system and organization-chart traversal

Walking a directory tree (`os.walk`, `find`, `du`) is recursion: a directory's size is the sum of its children's sizes, each child being a file or another directory. Rendering a nested comment thread, expanding a JSON document, and traversing an org chart all follow the same "handle this node, recurse on its children" shape. Compilers parse nested expressions with **recursive-descent parsers**.

## 6. Tips, tricks and pitfalls

- **Always write the base case first.** A missing or wrong base case causes infinite recursion and `RecursionError`.
- **Make sure each call moves toward the base case.**
- **Copy before saving a path:** `res.append(cur[:])`, not `res.append(cur)`, or every result aliases the same list.
- **Undo exactly what you did** when backtracking; mismatched undo is the most common backtracking bug.
- **Prune early.** Check validity before recursing, and sort inputs to break out of loops sooner.
- **Avoid duplicates** in subsets/permutations of repeated values by sorting and skipping equal neighbours at the same depth.
- **Memoize overlapping subproblems** (`functools.lru_cache`) to turn exponential into polynomial.
- **Slicing in recursion copies** data (`a[1:]` is `O(n)`); pass indices instead.
- **Convert to iteration** when depth could exceed about 1000.
- **Draw the recursion tree** for a tiny input to see what is called and what repeats.

## 7. Check yourself

1. What are the two essential parts of any recursive function?
2. Why does naive Fibonacci take exponential time and how does memoization fix it?
3. What is the space complexity of a recursion that goes `n` deep?
4. What is backtracking, and what does "pruning" mean?
5. Why must you copy the current path before storing it as a result?
6. How many subsets and permutations does a list of `n` distinct items have?
7. How do you avoid duplicate subsets when the input has repeated values?
8. When should you convert recursion to iteration?

<details>
<summary>Answers</summary>

1. A base case that returns directly, and a recursive case that shrinks the problem and combines results.
2. Each call spawns two calls that recompute the same values. Memoization stores each result, so each value is computed once: `O(n)`.
3. `O(n)` for the call stack (plus whatever each frame allocates).
4. Backtracking builds a solution incrementally and undoes choices that lead to dead ends. Pruning stops exploring a branch as soon as it cannot lead to a valid solution.
5. The path list is mutated as the search continues; storing the same object would make every saved result change or end up empty.
6. `2ⁿ` subsets and `n!` permutations.
7. Sort the input, then skip an element if it equals the previous one at the same recursion depth.
8. When the depth might exceed the recursion limit (about 1000 in Python), or to reduce call overhead.

</details>
