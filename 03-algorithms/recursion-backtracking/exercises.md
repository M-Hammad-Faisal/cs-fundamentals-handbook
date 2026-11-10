# Recursion and Backtracking: Exercises

## Recursion
1. Compute the **sum of digits** of a non-negative integer recursively.
2. Check whether a string is a **palindrome** recursively.
3. Compute `x ** n` in `O(log n)` using **fast exponentiation**.
4. **Flatten** an arbitrarily nested list (`[1, [2, [3]]]` becomes `[1, 2, 3]`).
5. **Tower of Hanoi:** return the list of moves for `n` disks.

## Backtracking
6. Generate all **subsets** of a list of distinct integers.
7. Generate all **subsets** when the list may contain duplicates (no duplicate subsets).
8. Generate all **permutations** of distinct integers.
9. **Combination sum:** all combinations of candidates (reusable) summing to a target.
10. **Generate parentheses:** all valid strings with `n` pairs.
11. **N-Queens:** count the solutions for `n` queens.
12. **Word search:** does a word exist in a grid using adjacent letters without reuse?
13. **Palindrome partitioning:** all ways to split a string into palindromes.
14. **Letter combinations of a phone number** (`"23"` gives `ad, ae, af, bd, ...`).

<details>
<summary>Solutions</summary>

```python
# 1
def digit_sum(n):
    return n if n < 10 else n % 10 + digit_sum(n // 10)

# 2
def is_palindrome(s, i=0):
    j = len(s) - 1 - i
    return True if i >= j else s[i] == s[j] and is_palindrome(s, i + 1)

# 3
def power(x, n):
    if n == 0:
        return 1
    half = power(x, n // 2)
    return half * half if n % 2 == 0 else half * half * x

# 4
def flatten(a):
    out = []
    for x in a:
        if isinstance(x, list):
            out.extend(flatten(x))
        else:
            out.append(x)
    return out

# 5
def hanoi(n, src="A", aux="B", dst="C"):
    if n == 0:
        return []
    return hanoi(n - 1, src, dst, aux) + [(src, dst)] + hanoi(n - 1, aux, src, dst)

# 6
def subsets(nums):
    res, cur = [], []
    def go(i):
        if i == len(nums):
            res.append(cur[:]); return
        go(i + 1)
        cur.append(nums[i]); go(i + 1); cur.pop()
    go(0)
    return res

# 7
def subsets_with_dup(nums):
    nums.sort()
    res, cur = [], []
    def go(start):
        res.append(cur[:])
        for i in range(start, len(nums)):
            if i > start and nums[i] == nums[i - 1]:
                continue
            cur.append(nums[i]); go(i + 1); cur.pop()
    go(0)
    return res

# 8
def permutations(nums):
    res = []
    def go(path, rest):
        if not rest:
            res.append(path[:]); return
        for i in range(len(rest)):
            path.append(rest[i])
            go(path, rest[:i] + rest[i + 1:])
            path.pop()
    go([], nums)
    return res

# 9
def combination_sum(cands, target):
    cands.sort()
    res, cur = [], []
    def go(start, remaining):
        if remaining == 0:
            res.append(cur[:]); return
        for i in range(start, len(cands)):
            if cands[i] > remaining:
                break
            cur.append(cands[i]); go(i, remaining - cands[i]); cur.pop()
    go(0, target)
    return res

# 10
def generate_parentheses(n):
    res = []
    def go(cur, o, c):
        if len(cur) == 2 * n:
            res.append(cur); return
        if o < n: go(cur + "(", o + 1, c)
        if c < o: go(cur + ")", o, c + 1)
    go("", 0, 0)
    return res

# 11
def total_n_queens(n):
    cols, d1, d2 = set(), set(), set()
    def go(r):
        if r == n:
            return 1
        count = 0
        for c in range(n):
            if c in cols or (r - c) in d1 or (r + c) in d2:
                continue
            cols.add(c); d1.add(r - c); d2.add(r + c)
            count += go(r + 1)
            cols.remove(c); d1.remove(r - c); d2.remove(r + c)
        return count
    return go(0)

# 12
def exist(board, word):
    rows, cols = len(board), len(board[0])
    def go(r, c, i):
        if i == len(word):
            return True
        if not (0 <= r < rows and 0 <= c < cols) or board[r][c] != word[i]:
            return False
        tmp, board[r][c] = board[r][c], "#"
        found = any(go(r + dr, c + dc, i + 1)
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        board[r][c] = tmp
        return found
    return any(go(r, c, 0) for r in range(rows) for c in range(cols))

# 13
def partition_palindromes(s):
    res, cur = [], []
    def go(start):
        if start == len(s):
            res.append(cur[:]); return
        for end in range(start + 1, len(s) + 1):
            piece = s[start:end]
            if piece == piece[::-1]:
                cur.append(piece); go(end); cur.pop()
    go(0)
    return res

# 14
def letter_combinations(digits):
    if not digits:
        return []
    mapping = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl",
               "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}
    res = []
    def go(i, cur):
        if i == len(digits):
            res.append(cur); return
        for ch in mapping[digits[i]]:
            go(i + 1, cur + ch)
    go(0, "")
    return res
```

</details>

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Recursion Fundamentals](01-recursion-fundamentals.md) · [Backtracking](02-backtracking.md)
