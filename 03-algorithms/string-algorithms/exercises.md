# String Algorithms: Exercises

Try each problem before opening its solution. These are the practice problems of this topic's lessons, collected in one place.

## String Algorithms

1. Compute `z_function("abacaba")` by hand, then check it.
2. Use `prefix_function` to decide whether `"abcabcabc"` is built by repeating a shorter string (hint: `n - pi[-1]` divides `n`).
3. Write `is_rotation(a, b)` using string matching (hint: `b` must occur in `a + a`).
4. In `rabin_karp`, what happens with `mod = 7`? Explain what correctness and speed do.
5. Find the longest palindromic substring of `"abacdfgdcaba"` with `manacher`.
6. How many distinct substrings does `"abab"` have? Use `distinct_substrings` and verify by listing.
7. Write `count_occurrences` for `"mississippi"` and the pattern `"ss"` using the suffix array.

<details>
<summary>Solutions</summary>

1. ```python no-run
   print(z_function("abacaba"))                                  # [0, 0, 1, 0, 3, 0, 1]
   ```
   For example `z[4] = 3`: the suffix `"aba"` matches the first three characters.
2. ```python no-run
   def repeats(s):
       pi = prefix_function(s)
       p = len(s) - pi[-1]
       return p < len(s) and len(s) % p == 0
   print(repeats("abcabcabc"), repeats("abcabcab"), repeats("aaaa"))      # True False True
   ```
3. ```python no-run
   def is_rotation(a, b):
       return len(a) == len(b) and b in a + a
   print(is_rotation("waterbottle", "erbottlewat"), is_rotation("abc", "acb"))       # True False
   ```
4. It is still **correct** (every hash match is verified by comparing characters) but **slower**: with only 7 possible hash values, about 1 in 7 windows collides, so many pointless character comparisons run; the expected `O(n + m)` degrades toward `O(nm)`.
5. ```python no-run
   print(manacher("abacdfgdcaba")[0])                            # aba
   ```
6. ```python no-run
   print(distinct_substrings("abab"), sorted({"abab"[i:j] for i in range(4) for j in range(i + 1, 5)}))
   # 7 ['a', 'ab', 'aba', 'abab', 'b', 'ba', 'bab']
   ```
7. ```python no-run
   t = "mississippi"; sa2 = suffix_array(t)
   print(count_occurrences(t, sa2, "ss"), naive_find_all(t, "ss"))        # 2 [2, 5]
   ```

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [String Algorithms](01-string-matching-and-suffix-structures.md)
