# String Algorithms: Exercises

These problems go with the [String Algorithms lesson](README.md). Try each one before opening its solution.

<details>
<summary>Setup code the solutions use (copied from the lessons)</summary>

```python
def naive_find_all(text, pattern):
    return [i for i in range(len(text) - len(pattern) + 1) if text[i:i + len(pattern)] == pattern]

def z_function(s):
    n = len(s)
    z = [0] * n
    l = r = 0                                                    # [l, r) is the rightmost segment that matches a prefix
    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])                          # reuse: inside the window, copy a known value (capped by the window)
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1                                            # extend the match character by character
        if i + z[i] > r:
            l, r = i, i + z[i]                                   # a new rightmost window
    return z

def prefix_function(s):
    pi = [0] * len(s)
    k = 0
    for i in range(1, len(s)):
        while k and s[i] != s[k]:
            k = pi[k - 1]                                        # fall back to the next shorter border
        if s[i] == s[k]:
            k += 1
        pi[i] = k
    return pi

def manacher(s):
    t = "#" + "#".join(s) + "#"
    n = len(t)
    radius = [0] * n                                             # radius[i]: palindrome centered at i spans t[i-radius : i+radius+1]
    center = right = 0                                           # the palindrome reaching farthest to the right
    for i in range(n):
        if i < right:
            radius[i] = min(right - i, radius[2 * center - i])   # the mirror position's radius, capped by the window
        while i - radius[i] - 1 >= 0 and i + radius[i] + 1 < n and t[i - radius[i] - 1] == t[i + radius[i] + 1]:
            radius[i] += 1
        if i + radius[i] > right:
            center, right = i, i + radius[i]
    best = max(range(n), key=lambda i: radius[i])
    start = (best - radius[best]) // 2                           # map back to the original string
    return s[start:start + radius[best]], radius

def suffix_array(s):
    return sorted(range(len(s)), key=lambda i: s[i:])           # simple: O(n^2 log n) worst case, fine for learning and moderate n

def count_occurrences(text, sa, pattern):
    def bound(strict):
        lo, hi = 0, len(sa)
        while lo < hi:
            mid = (lo + hi) // 2
            piece = text[sa[mid]:sa[mid] + len(pattern)]
            if piece < pattern or (strict and piece == pattern):
                lo = mid + 1
            else:
                hi = mid
        return lo
    return bound(True) - bound(False)

def lcp_array(s, sa):
    n = len(s)
    rank = [0] * n
    for i, start in enumerate(sa):
        rank[start] = i
    lcp, k = [0] * n, 0
    for i in range(n):                                           # process suffixes in text order: the LCP can drop by at most 1 each step
        if rank[i] == 0:
            k = 0
            continue
        j = sa[rank[i] - 1]
        while i + k < n and j + k < n and s[i + k] == s[j + k]:
            k += 1
        lcp[rank[i]] = k
        if k:
            k -= 1
    return lcp

def distinct_substrings(s):
    sa = suffix_array(s)
    lcp = lcp_array(s, sa)
    n = len(s)
    return n * (n + 1) // 2 - sum(lcp)                           # all substrings minus the repeats counted by the LCP
```

</details>

## Problems

1. Compute `z_function("abacaba")` by hand, then check it.
2. Use `prefix_function` to decide whether `"abcabcabc"` is built by repeating a shorter string (hint: `n - pi[-1]` divides `n`).
3. Write `is_rotation(a, b)` using string matching (hint: `b` must occur in `a + a`).
4. In `rabin_karp`, what happens with `mod = 7`? Explain what correctness and speed do.
5. Find the longest palindromic substring of `"abacdfgdcaba"` with `manacher`.
6. How many distinct substrings does `"abab"` have? Use `distinct_substrings` and verify by listing.
7. Write `count_occurrences` for `"mississippi"` and the pattern `"ss"` using the suffix array.

<details>
<summary>Solutions</summary>

1. ```python
   print(z_function("abacaba"))                                  # [0, 0, 1, 0, 3, 0, 1]
   ```
   For example `z[4] = 3`: the suffix `"aba"` matches the first three characters.
2. ```python
   def repeats(s):
       pi = prefix_function(s)
       p = len(s) - pi[-1]
       return p < len(s) and len(s) % p == 0
   print(repeats("abcabcabc"), repeats("abcabcab"), repeats("aaaa"))      # True False True
   ```
3. ```python
   def is_rotation(a, b):
       return len(a) == len(b) and b in a + a
   print(is_rotation("waterbottle", "erbottlewat"), is_rotation("abc", "acb"))       # True False
   ```
4. It is still **correct** (every hash match is verified by comparing characters) but **slower**: with only 7 possible hash values, about 1 in 7 windows collides, so many pointless character comparisons run; the expected `O(n + m)` degrades toward `O(nm)`.
5. ```python
   print(manacher("abacdfgdcaba")[0])                            # aba
   ```
6. ```python
   print(distinct_substrings("abab"), sorted({"abab"[i:j] for i in range(4) for j in range(i + 1, 5)}))
   # 7 ['a', 'ab', 'aba', 'abab', 'b', 'ba', 'bab']
   ```
7. ```python
   t = "mississippi"; sa2 = suffix_array(t)
   print(count_occurrences(t, sa2, "ss"), naive_find_all(t, "ss"))        # 2 [2, 5]
   ```

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [String Algorithms](01-string-matching-and-suffix-structures.md)
