# DP on Two Sequences, Grids and Knapsack

**Prerequisites:** [DP thinking and 1D problems](01-dp-thinking-and-1d-problems.md). **You will learn:** two-dimensional DP: **longest common subsequence (LCS)**, **edit distance**, the **0/1 knapsack**, **grid paths**, **longest palindromic substring/subsequence**; how to **reconstruct the actual answer** (not only its value); and how to shrink memory.

## 1. From one dimension to two

When a problem involves **two** changing things (a position in string A *and* a position in string B; a row *and* a column; an item index *and* a remaining capacity), the state has two numbers, so the table is 2D: `dp[i][j]`.

The recipe is unchanged: define the state, write the transition, set base cases, choose a fill order, read the answer.

## 2. Longest common subsequence (LCS)

A **subsequence** keeps order but may skip characters (`"ace"` is a subsequence of `"abcde"`). Find the longest subsequence shared by two strings.

- State: `dp[i][j]` = LCS length of the first `i` characters of `a` and the first `j` of `b`.
- Transition: if `a[i-1] == b[j-1]` the match extends the diagonal: `dp[i][j] = dp[i-1][j-1] + 1`; otherwise drop a character from one string: `max(dp[i-1][j], dp[i][j-1])`.
- Base: row and column 0 are 0 (an empty string shares nothing).

```text
a = "ABCB", b = "BDCB"
      ""  B  D  C  B
  ""   0  0  0  0  0
  A    0  0  0  0  0
  B    0  1  1  1  1
  C    0  1  1  2  2
  B    0  1  1  2  3      LCS length 3 ("BCB")
```

```python
def lcs_length(a, b):
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]      # build rows separately (never [[0]*n]*m)
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp, dp[len(a)][len(b)]

def lcs_string(a, b):
    dp, _ = lcs_length(a, b)
    i, j, chars = len(a), len(b), []
    while i > 0 and j > 0:                                    # walk back through the table
        if a[i - 1] == b[j - 1]:
            chars.append(a[i - 1]); i -= 1; j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return "".join(reversed(chars))

print(lcs_length("ABCB", "BDCB")[1], lcs_string("ABCB", "BDCB"))             # 3 BCB
print(lcs_length("AGGTAB", "GXTXAYB")[1], lcs_string("AGGTAB", "GXTXAYB"))   # 4 GTAB
```

**Cost:** `O(len(a) · len(b))` time and space. Used by `diff` and Git to show what changed between two versions of a file, and in DNA sequence comparison.

## 3. Edit distance (Levenshtein)

The minimum number of single-character **insertions, deletions and substitutions** to turn `a` into `b`.

- State: `dp[i][j]` = edit distance between `a[:i]` and `b[:j]`.
- Transition: if the last characters are equal, it costs nothing: `dp[i-1][j-1]`; else `1 + min(` delete `dp[i-1][j]`, insert `dp[i][j-1]`, substitute `dp[i-1][j-1]``)`.
- Base: `dp[i][0] = i` (delete everything), `dp[0][j] = j` (insert everything).

```python
def edit_distance(a, b):
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        dp[i][0] = i
    for j in range(len(b) + 1):
        dp[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
    return dp[len(a)][len(b)]

print(edit_distance("kitten", "sitting"), edit_distance("horse", "ros"), edit_distance("", "abc"), edit_distance("same", "same"))
# 3 3 3 0
```

`kitten -> sitting`: substitute `k->s`, substitute `e->i`, insert `g`: 3 edits.

**Reconstructing the edit script:**

```python
def edit_script(a, b):
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1): dp[i][0] = i
    for j in range(m + 1): dp[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            dp[i][j] = dp[i - 1][j - 1] if a[i - 1] == b[j - 1] else 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
    i, j, steps = n, m, []
    while i > 0 or j > 0:
        if i > 0 and j > 0 and a[i - 1] == b[j - 1]:
            i, j = i - 1, j - 1
        elif i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + 1:
            steps.append(f"replace {a[i - 1]!r} with {b[j - 1]!r}"); i, j = i - 1, j - 1
        elif i > 0 and dp[i][j] == dp[i - 1][j] + 1:
            steps.append(f"delete {a[i - 1]!r}"); i -= 1
        else:
            steps.append(f"insert {b[j - 1]!r}"); j -= 1
    return steps[::-1]

print(edit_script("kitten", "sitting"))
# ["replace 'k' with 's'", "replace 'e' with 'i'", "insert 'g'"]
```

**Memory trick:** each row depends only on the previous row, so keep two rows (`O(min(n, m))` space) when you need only the number:

```python
def edit_distance_two_rows(a, b):
    previous = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        current = [i] + [0] * len(b)
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                current[j] = previous[j - 1]
            else:
                current[j] = 1 + min(previous[j], current[j - 1], previous[j - 1])
        previous = current
    return previous[-1]

print(edit_distance_two_rows("kitten", "sitting"), edit_distance_two_rows("intention", "execution"))      # 3 5
```

## 4. Grid paths

**Unique paths:** moves only right or down from the top-left to the bottom-right.

```python
def unique_paths(rows, cols):
    dp = [[1] * cols for _ in range(rows)]                    # first row and first column have exactly one way
    for r in range(1, rows):
        for c in range(1, cols):
            dp[r][c] = dp[r - 1][c] + dp[r][c - 1]            # arrive from above or from the left
    return dp[-1][-1]

def min_path_sum(grid):
    rows, cols = len(grid), len(grid[0])
    dp = [[0] * cols for _ in range(rows)]
    dp[0][0] = grid[0][0]
    for c in range(1, cols): dp[0][c] = dp[0][c - 1] + grid[0][c]
    for r in range(1, rows): dp[r][0] = dp[r - 1][0] + grid[r][0]
    for r in range(1, rows):
        for c in range(1, cols):
            dp[r][c] = grid[r][c] + min(dp[r - 1][c], dp[r][c - 1])
    return dp[-1][-1]

def unique_paths_obstacles(grid):                             # 1 = blocked cell
    rows, cols = len(grid), len(grid[0])
    dp = [[0] * cols for _ in range(rows)]
    dp[0][0] = 0 if grid[0][0] else 1
    for r in range(rows):
        for c in range(cols):
            if grid[r][c]:
                dp[r][c] = 0
            elif (r, c) != (0, 0):
                dp[r][c] = (dp[r - 1][c] if r else 0) + (dp[r][c - 1] if c else 0)
    return dp[-1][-1]

print(unique_paths(3, 7), unique_paths(3, 3))                 # 28 6
print(min_path_sum([[1, 3, 1], [1, 5, 1], [4, 2, 1]]))        # 7       (1 -> 3 -> 1 -> 1 -> 1)
print(unique_paths_obstacles([[0, 0, 0], [0, 1, 0], [0, 0, 0]]))     # 2
```

## 5. The 0/1 knapsack

Items have `(weight, value)`; each can be taken **once** or not at all; capacity `W`. Maximize total value. (Greedy by ratio fails here, as shown in the [greedy lesson](../greedy/01-greedy-algorithms.md).)

- State: `dp[i][w]` = best value using the first `i` items with capacity `w`.
- Transition: skip item `i` (`dp[i-1][w]`) or take it if it fits (`dp[i-1][w - weight] + value`).

```python
def knapsack(items, capacity):
    n = len(items)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i, (weight, value) in enumerate(items, start=1):
        for w in range(capacity + 1):
            dp[i][w] = dp[i - 1][w]                           # skip
            if weight <= w:
                dp[i][w] = max(dp[i][w], dp[i - 1][w - weight] + value)       # take
    chosen, w = [], capacity
    for i in range(n, 0, -1):                                 # reconstruct which items were taken
        if dp[i][w] != dp[i - 1][w]:
            chosen.append(i - 1)
            w -= items[i - 1][0]
    return dp[n][capacity], sorted(chosen)

items = [(10, 60), (20, 100), (30, 120)]                      # (weight, value)
print(knapsack(items, 50))                                    # (220, [1, 2])      (the greedy answer would be 160)
```

**One-row version:** loop the capacity **backwards** so each item is used once:

```python
def knapsack_1d(items, capacity):
    dp = [0] * (capacity + 1)
    for weight, value in items:
        for w in range(capacity, weight - 1, -1):             # backwards: dp[w - weight] still holds the previous item's row
            dp[w] = max(dp[w], dp[w - weight] + value)
    return dp[capacity]

print(knapsack_1d(items, 50))                                 # 220
```

(Looping forwards would let an item be reused: that is the **unbounded** knapsack, the same as coin change.)

## 6. Palindromes

**Longest palindromic substring**: expand around every center (`O(n²)`, no table needed):

```python
def longest_palindrome(s):
    best = ""
    for center in range(len(s)):
        for lo, hi in ((center, center), (center, center + 1)):       # odd-length and even-length palindromes
            while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
                lo -= 1; hi += 1
            if hi - lo - 1 > len(best):
                best = s[lo + 1:hi]
    return best

print(longest_palindrome("babad"), longest_palindrome("cbbd"), longest_palindrome("a"))      # bab bb a
```

**Longest palindromic subsequence** reduces to LCS of the string and its reverse:

```python
def longest_palindromic_subsequence(s):
    return lcs_length(s, s[::-1])[1]

print(longest_palindromic_subsequence("bbbab"), longest_palindromic_subsequence("cbbd"))      # 4 2
```

## 7. Interval and "matrix chain" style DP (preview)

Some DPs are over **ranges** `dp[i][j]` = best for the substring/segment `i..j`, filled by increasing length. Example: **minimum cost to cut a rope**, **burst balloons**, **matrix chain multiplication**.

```python
def matrix_chain_cost(dims):
    """dims = [10, 30, 5, 60] means matrices 10x30, 30x5, 5x60. Fewest scalar multiplications."""
    n = len(dims) - 1
    dp = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):                            # shorter ranges first
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = min(dp[i][k] + dp[k + 1][j] + dims[i] * dims[k + 1] * dims[j + 1]
                           for k in range(i, j))              # try every split point
    return dp[0][n - 1]

print(matrix_chain_cost([10, 30, 5, 60]))                     # 4500    ((A x B) x C = 1500 + 3000)
```

## 8. Debugging a DP

- Print the **table** for a tiny input and compare with a hand computation.
- Compare with **brute force** on random small inputs.
- Check the **base row and column** first: most bugs hide there.
- Ask: does the cell I read already hold its final value when I read it?

```python
import random, itertools

def lcs_bruteforce(a, b):
    best = 0
    for r in range(len(a) + 1):
        for idx in itertools.combinations(range(len(a)), r):
            sub = "".join(a[i] for i in idx)
            it = iter(b)
            if all(ch in it for ch in sub):                   # is `sub` a subsequence of b?
                best = max(best, r)
    return best

random.seed(21)
for _ in range(200):
    a = "".join(random.choice("abc") for _ in range(random.randint(0, 8)))
    b = "".join(random.choice("abc") for _ in range(random.randint(0, 8)))
    assert lcs_length(a, b)[1] == lcs_bruteforce(a, b)
print("LCS DP matched brute force on 200 random pairs")       # LCS DP matched brute force on 200 random pairs
```

## 9. Two real-world examples

**Example 1: `diff` and version control.** Comparing two files line by line is LCS on lines; the lines not in the LCS are the additions and deletions you see in a pull request.

**Example 2: Spell check and DNA.** Suggesting "kitten" for "sitting" uses edit distance; the Needleman-Wunsch and Smith-Waterman algorithms that align genomes are the same DP with weighted costs.

## 10. Common mistakes

- Building the table with `[[0] * m] * n` (all rows alias one list).
- Off-by-one between string index `i - 1` and table index `i`.
- Forgetting base rows and columns (edit distance needs `dp[i][0] = i`).
- Forward capacity loop in 1D 0/1 knapsack (accidentally allows reuse).
- Returning the value when the question wants the *solution* (keep parent pointers or walk the table back).
- Memory blow-up on large inputs; keep only the previous row when possible.

## 11. Practice

1. Fill the LCS table by hand for `"AB"` and `"BA"`.
2. What is the edit distance between `"flaw"` and `"lawn"`?
3. 0/1 knapsack: capacity 8, items `(weight, value)`: `(3, 30), (4, 50), (5, 60)`. Best value?
4. Unique paths in a 4x4 grid? (use a formula check: `C(6, 3)`).
5. Write `is_subsequence(s, t)` with two pointers.
6. Write `longest_common_substring(a, b)` (contiguous). Hint: `dp[i][j] = dp[i-1][j-1] + 1` only on a match, else 0.
7. Write `min_deletions_to_palindrome(s)` using LPS.

<details>
<summary>Solutions</summary>

1. Rows `""`, `A`, `B` and columns `""`, `B`, `A`: `dp[A][B]=0, dp[A][A]=1, dp[B][B]=1, dp[B][A]=1`. LCS length 1.
2. ```python
   print(edit_distance("flaw", "lawn"))               # 2   (delete 'f', insert 'n')
   ```
3. ```python
   print(knapsack([(3, 30), (4, 50), (5, 60)], 8))    # (90, [0, 2])    (weights 3 + 5 = 8 for value 90)
   ```
4. `C(6, 3) = 20`.
   ```python
   print(unique_paths(4, 4))                          # 20
   ```
5. ```python
   def is_subsequence(s, t):
       it = iter(t)
       return all(ch in it for ch in s)               # `in` on an iterator consumes it, enforcing order
   print(is_subsequence("ace", "abcde"), is_subsequence("aec", "abcde"))      # True False
   ```
6. ```python
   def longest_common_substring(a, b):
       best = 0
       dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
       for i in range(1, len(a) + 1):
           for j in range(1, len(b) + 1):
               if a[i - 1] == b[j - 1]:
                   dp[i][j] = dp[i - 1][j - 1] + 1
                   best = max(best, dp[i][j])
       return best
   print(longest_common_substring("abcdxyz", "xyzabcd"))      # 4
   ```
7. ```python
   def min_deletions_to_palindrome(s):
       return len(s) - longest_palindromic_subsequence(s)
   print(min_deletions_to_palindrome("abcba"), min_deletions_to_palindrome("abca"))      # 0 1
   ```

</details>

## 12. Check yourself

1. What does `dp[i][j]` mean in LCS and edit distance?
2. What are the three operations in edit distance?
3. Why must the 1D knapsack loop run backwards over capacity?
4. How do you recover the actual LCS string, not just its length?
5. When can you reduce a 2D DP table to two rows?

<details>
<summary>Answers</summary>

1. Answer for the first `i` characters of one string and the first `j` of the other.
2. Insert, delete, substitute (each cost 1).
3. So each item is counted once; a forward loop would let the same item be added repeatedly.
4. Walk the table from the bottom-right corner, following the matches and the larger neighbor.
5. When `dp[i][...]` depends only on row `i - 1` (and earlier cells of row `i`).

</details>

[Back to dynamic programming](README.md) · Previous: [DP thinking and 1D problems](01-dp-thinking-and-1d-problems.md)
