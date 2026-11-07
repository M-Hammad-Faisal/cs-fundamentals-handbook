# Backtracking

**Prerequisites:** [recursion fundamentals](01-recursion-fundamentals.md), [DFS on trees and graphs](../../02-data-structures/graphs/01-graph-basics-bfs-dfs.md). **You will learn:** the **choose, explore, un-choose** pattern, a reusable template, and its classic applications: **subsets, permutations, combinations, combination sum, N-Queens, word search and Sudoku**, plus **pruning**, the trick that makes exponential searches practical.

## 1. In plain words

Solving a maze: at every fork you pick a path; if it dead-ends you **walk back to the last fork and try another path**. That walking back is **backtracking**. It is a depth-first search through the space of *choices*, abandoning a partial solution the moment it cannot possibly work.

The pattern in three verbs:

```text
choose   -> make one choice and add it to the partial solution
explore  -> recurse to make the remaining choices
un-choose-> remove the choice (undo) and try the next option
```

## 2. The template

```python
def backtrack(partial, choices):
    if is_complete(partial):
        record(partial)                  # found a full solution
        return
    for choice in choices_available(partial):
        if not is_valid(partial, choice):
            continue                     # PRUNE: skip choices that cannot lead to a solution
        partial.append(choice)           # choose
        backtrack(partial, choices)      # explore
        partial.pop()                    # un-choose (restore the state)
```

The **un-choose** step is what makes it backtracking: it restores the state so the next option starts from a clean slate.

## 3. Subsets (the power set)

For each item there are two choices: **take it or skip it**. `n` items give `2^n` subsets.

```text
                     []
          take 1 /        \ skip 1
              [1]          []
       take 2/ \skip 2  take 2/ \skip 2
         [1,2] [1]       [2]   []        ... and so on for 3
```

```python
def subsets(items):
    result, current = [], []
    def go(i):
        if i == len(items):
            result.append(current[:])           # copy: current keeps changing
            return
        current.append(items[i]); go(i + 1); current.pop()      # take items[i]
        go(i + 1)                                               # skip items[i]
    go(0)
    return result

print(subsets([1, 2, 3]))
# [[1, 2, 3], [1, 2], [1, 3], [1], [2, 3], [2], [3], []]
print(len(subsets(list(range(10)))))            # 1024
```

Always store `current[:]` (a copy), not `current` (a reference that later changes).

## 4. Permutations

Orderings of `n` distinct items: `n!` of them. At each position, choose any item not yet used.

```python
def permutations(items):
    result, current, used = [], [], [False] * len(items)
    def go():
        if len(current) == len(items):
            result.append(current[:])
            return
        for i in range(len(items)):
            if used[i]:
                continue
            used[i] = True; current.append(items[i])     # choose
            go()                                          # explore
            current.pop(); used[i] = False                # un-choose
    go()
    return result

print(permutations([1, 2, 3]))
# [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]
print(len(permutations(list(range(7)))))         # 5040
```

With **duplicates** (`[1, 1, 2]`), sort first and skip a value if the same value just before it is unused (otherwise you get repeats):

```python
def unique_permutations(items):
    items = sorted(items)
    result, current, used = [], [], [False] * len(items)
    def go():
        if len(current) == len(items):
            result.append(current[:]); return
        for i in range(len(items)):
            if used[i] or (i > 0 and items[i] == items[i - 1] and not used[i - 1]):
                continue                                  # skip duplicate branches
            used[i] = True; current.append(items[i]); go(); current.pop(); used[i] = False
    go()
    return result

print(unique_permutations([1, 1, 2]))            # [[1, 1, 2], [1, 2, 1], [2, 1, 1]]
```

## 5. Combinations (choose k of n)

Order does not matter, so only consider items **after** the last chosen one.

```python
def combinations(n, k):
    result, current = [], []
    def go(start):
        if len(current) == k:
            result.append(current[:]); return
        for x in range(start, n + 1):
            current.append(x); go(x + 1); current.pop()
    go(1)
    return result

print(combinations(4, 2))                        # [[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]
```

### Pruning: stop early when it is hopeless

If fewer items remain than are still needed, no completion exists:

```python
def combinations_pruned(n, k, stats):
    result, current = [], []
    def go(start):
        stats["calls"] += 1
        if len(current) == k:
            result.append(current[:]); return
        for x in range(start, n - (k - len(current)) + 2):      # leave enough items to finish
            current.append(x); go(x + 1); current.pop()
    go(1)
    return result

def combinations_plain(n, k, stats):
    result, current = [], []
    def go(start):
        stats["calls"] += 1
        if len(current) == k:
            result.append(current[:]); return
        for x in range(start, n + 1):
            current.append(x); go(x + 1); current.pop()
    go(1)
    return result

a, b = {"calls": 0}, {"calls": 0}
assert combinations_pruned(20, 15, a) == combinations_plain(20, 15, b)
print(a["calls"], b["calls"])                    # 54264 1042380    (same answers, about 19x fewer calls)
```

## 6. Combination sum (reuse allowed) and subset sum

Find combinations of numbers adding to a target. Sort, and **prune** when the running total exceeds the target.

```python
def combination_sum(candidates, target):
    candidates = sorted(candidates)
    result, current = [], []
    def go(start, remaining):
        if remaining == 0:
            result.append(current[:]); return
        for i in range(start, len(candidates)):
            if candidates[i] > remaining:
                break                                    # sorted: every later number is too big as well
            current.append(candidates[i])
            go(i, remaining - candidates[i])             # i, not i + 1: the same number may be reused
            current.pop()
    go(0, target)
    return result

print(combination_sum([2, 3, 6, 7], 7))          # [[2, 2, 3], [7]]
print(combination_sum([2, 3, 5], 8))             # [[2, 2, 2, 2], [2, 3, 3], [3, 5]]
```

## 7. N-Queens

Place `n` queens on an `n x n` board so none attack each other (no shared row, column or diagonal). Place one queen **per row**; for each row try every column and prune those that are attacked.

```python
def solve_n_queens(n):
    solutions = []
    cols, diag1, diag2 = set(), set(), set()            # attacked columns and the two diagonal directions
    placement = []
    def go(row):
        if row == n:
            solutions.append(placement[:]); return
        for col in range(n):
            if col in cols or (row - col) in diag1 or (row + col) in diag2:
                continue                                 # attacked: prune
            cols.add(col); diag1.add(row - col); diag2.add(row + col); placement.append(col)
            go(row + 1)
            placement.pop(); cols.remove(col); diag1.remove(row - col); diag2.remove(row + col)
    go(0)
    return solutions

def show(solution):
    for col in solution:
        print(" ".join("Q" if c == col else "." for c in range(len(solution))))

print([len(solve_n_queens(n)) for n in range(1, 9)])      # [1, 0, 0, 2, 10, 4, 40, 92]
show(solve_n_queens(6)[0])
# . Q . . . .
# . . . Q . .
# . . . . . Q
# Q . . . . .
# . . Q . . .
# . . . . Q .
```

The three sets answer "is this square attacked?" in `O(1)`: two squares share a `\` diagonal when `row - col` is equal and a `/` diagonal when `row + col` is equal. Without pruning there are `n^n` boards (16 million for `n = 8`); with it the search visits only about 2,057 partial boards.

## 8. Word search in a grid

Does the word appear as a path of adjacent letters (no cell reused)?

```python
def word_exists(board, word):
    rows, cols = len(board), len(board[0])
    def go(r, c, i):
        if i == len(word):
            return True
        if not (0 <= r < rows and 0 <= c < cols) or board[r][c] != word[i]:
            return False                                  # off the board or wrong letter: prune
        saved, board[r][c] = board[r][c], "#"             # choose: mark visited
        found = any(go(r + dr, c + dc, i + 1) for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        board[r][c] = saved                               # un-choose: restore the letter
        return found
    return any(go(r, c, 0) for r in range(rows) for c in range(cols))

grid = [list("ABCE"), list("SFCS"), list("ADEE")]
print(word_exists(grid, "ABCCED"), word_exists(grid, "SEE"), word_exists(grid, "ABCB"))      # True True False
```

## 9. Sudoku

Fill the empty cells (`0`) so every row, column and 3x3 box contains 1-9. Try each digit in the first empty cell; if the rest cannot be completed, undo and try the next digit.

```python
def solve_sudoku(board):
    def ok(r, c, d):
        if d in board[r] or any(board[i][c] == d for i in range(9)):
            return False
        br, bc = 3 * (r // 3), 3 * (c // 3)
        return all(board[i][j] != d for i in range(br, br + 3) for j in range(bc, bc + 3))

    def go():
        for r in range(9):
            for c in range(9):
                if board[r][c] == 0:
                    for d in range(1, 10):
                        if ok(r, c, d):
                            board[r][c] = d               # choose
                            if go():
                                return True               # explore
                            board[r][c] = 0               # un-choose
                    return False                          # no digit fits here: backtrack
        return True                                       # no empty cell left: solved
    return go()

puzzle = [
    [5,3,0,0,7,0,0,0,0], [6,0,0,1,9,5,0,0,0], [0,9,8,0,0,0,0,6,0],
    [8,0,0,0,6,0,0,0,3], [4,0,0,8,0,3,0,0,1], [7,0,0,0,2,0,0,0,6],
    [0,6,0,0,0,0,2,8,0], [0,0,0,4,1,9,0,0,5], [0,0,0,0,8,0,0,7,9],
]
print(solve_sudoku(puzzle))                               # True
print(puzzle[0], puzzle[8])                               # [5, 3, 4, 6, 7, 8, 9, 1, 2] [3, 4, 5, 2, 8, 6, 1, 7, 9]
```

## 10. Generating valid parentheses

Build strings of `n` pairs where parentheses are balanced: only add `(` if you have some left, and `)` only if it would not close more than were opened. Invalid prefixes are never generated.

```python
def generate_parentheses(n):
    result = []
    def go(current, opened, closed):
        if len(current) == 2 * n:
            result.append(current); return
        if opened < n:
            go(current + "(", opened + 1, closed)
        if closed < opened:
            go(current + ")", opened, closed + 1)
    go("", 0, 0)
    return result

print(generate_parentheses(3))
# ['((()))', '(()())', '(())()', '()(())', '()()()']
print(len(generate_parentheses(8)))                      # 1430
```

## 11. Cost and when backtracking fits

| Problem | Search space | Notes |
|---------|--------------|-------|
| Subsets | `2^n` | cannot be faster: that many answers |
| Permutations | `n!` | 10! = 3.6 million, 15! is impossible |
| N-Queens | `n!` upper bound, far less with pruning | prune early |
| Sudoku | huge without pruning | constraints cut it dramatically |

Backtracking is the tool for **"find all" / "find any" / "does a solution exist"** when there is no better structure. If subproblems **repeat**, memoize and you have [dynamic programming](../dynamic-programming/README.md); if you only need the optimum and a local choice is provably safe, a [greedy](../greedy/README.md) algorithm is faster.

## 12. Two real-world examples

**Example 1: Constraint solvers.** Timetable and exam schedulers, seating plans and puzzle solvers assign values one variable at a time and backtrack on conflicts (with smarter ordering and pruning, this is how SAT and CSP solvers began).

**Example 2: Regex engines and package resolvers.** A regex matcher tries an alternative and backtracks if the rest fails; `pip` and `npm` dependency resolvers try versions and backtrack when constraints conflict.

## 13. Common mistakes

- Forgetting the **un-choose** step (state leaks into other branches).
- Appending the shared `current` list instead of a **copy** (`current[:]`).
- Not pruning (technically correct, impractically slow).
- Duplicate results with repeated input values (sort and skip duplicates).
- Recursion depth for large `n` (backtracking depth is usually small, equal to the number of decisions).
- Mixing up "reuse allowed" (`go(i, ...)`) versus "each once" (`go(i + 1, ...)`).

## 14. Practice

1. How many subsets does a 12-item list have? How many permutations of 5 items?
2. Print all strings of length 3 over `"ab"` using backtracking.
3. Modify `combination_sum` so each candidate can be used **at most once** (candidates may include duplicates; return unique combinations).
4. How many ways to place 4 queens? List them as column positions per row.
5. Write `partition_palindromes(s)` returning all ways to split `s` into palindromes (`"aab"` gives `[["a","a","b"],["aa","b"]]`).
6. Write `letter_combinations(digits)` for a phone keypad (`"23"` gives `ad ae af bd be bf cd ce cf`).
7. Why does N-Queens place one queen per row instead of trying every cell?

<details>
<summary>Solutions</summary>

1. `2^12 = 4096` subsets; `5! = 120` permutations.
2. ```python
   def strings(n, alphabet="ab"):
       out = []
       def go(cur):
           if len(cur) == n: out.append(cur); return
           for ch in alphabet: go(cur + ch)
       go("")
       return out
   print(strings(3))                                 # ['aaa', 'aab', 'aba', 'abb', 'baa', 'bab', 'bba', 'bbb']
   ```
3. ```python
   def combination_sum_once(candidates, target):
       candidates = sorted(candidates)
       result, current = [], []
       def go(start, remaining):
           if remaining == 0:
               result.append(current[:]); return
           for i in range(start, len(candidates)):
               if i > start and candidates[i] == candidates[i - 1]:
                   continue                              # skip duplicates at the same level
               if candidates[i] > remaining:
                   break
               current.append(candidates[i]); go(i + 1, remaining - candidates[i]); current.pop()
       go(0, target)
       return result
   print(combination_sum_once([10, 1, 2, 7, 6, 1, 5], 8))      # [[1, 1, 6], [1, 2, 5], [1, 7], [2, 6]]
   ```
4. Two ways: `[1, 3, 0, 2]` and `[2, 0, 3, 1]`.
   ```python
   print(solve_n_queens(4))                          # [[1, 3, 0, 2], [2, 0, 3, 1]]
   ```
5. ```python
   def partition_palindromes(s):
       result, current = [], []
       def go(start):
           if start == len(s):
               result.append(current[:]); return
           for end in range(start + 1, len(s) + 1):
               piece = s[start:end]
               if piece == piece[::-1]:
                   current.append(piece); go(end); current.pop()
       go(0)
       return result
   print(partition_palindromes("aab"))               # [['a', 'a', 'b'], ['aa', 'b']]
   ```
6. ```python
   def letter_combinations(digits):
       keys = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl", "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}
       if not digits: return []
       out = []
       def go(i, cur):
           if i == len(digits): out.append(cur); return
           for ch in keys[digits[i]]: go(i + 1, cur + ch)
       go(0, "")
       return out
   print(letter_combinations("23"))                  # ['ad', 'ae', 'af', 'bd', 'be', 'bf', 'cd', 'ce', 'cf']
   ```
7. Two queens in the same row attack each other, so each row has exactly one queen; fixing the row removes `n` choices per step and shrinks the search from `(n²)` cells per decision to `n` columns.

</details>

## 15. Check yourself

1. What are the three steps of backtracking?
2. Why must you undo a choice?
3. What does pruning do?
4. How many subsets and permutations do `n` items have?
5. How do you avoid duplicate results when the input has repeated values?
6. How is backtracking different from dynamic programming?

<details>
<summary>Answers</summary>

1. Choose, explore (recurse), un-choose.
2. So the next alternative starts from the same state as this one did.
3. It abandons partial solutions that cannot lead to a valid answer, cutting off whole branches.
4. `2^n` and `n!`.
5. Sort the input and skip a value equal to the previous one at the same decision level.
6. Backtracking enumerates choices (possibly repeating work); DP stores answers of overlapping subproblems to avoid recomputation.

</details>

[Back to recursion and backtracking](README.md) · Previous: [recursion fundamentals](01-recursion-fundamentals.md)
