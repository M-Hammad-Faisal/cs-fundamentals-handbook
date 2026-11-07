# String Algorithms: Matching, Palindromes and Suffix Arrays

**Prerequisites:** [strings in depth](../../02-data-structures/arrays-strings/03-strings-in-depth.md) (including KMP), [hash functions](../../02-data-structures/hash-tables/01-hash-functions-and-collisions.md), [number theory](../number-theory/01-number-theory-for-programmers.md) (modular arithmetic), [sorting](../sorting/02-merge-sort-and-quicksort.md). **You will learn:** how to find a pattern in a text faster than the naive double loop: **Rabin-Karp** (rolling hash), the **Z-function**, and a recap of **KMP's prefix function**; how to find the longest palindrome in linear time (**Manacher**); and how **suffix arrays** answer "longest repeated substring", "count distinct substrings" and "does this pattern occur?" Every algorithm is verified against the naive version on random inputs.

## 1. The problem and the naive solution

**Pattern matching:** find every position where a pattern `P` (length `m`) occurs in a text `T` (length `n`).

```python
def naive_find_all(text, pattern):
    return [i for i in range(len(text) - len(pattern) + 1) if text[i:i + len(pattern)] == pattern]

print(naive_find_all("abracadabra", "abra"))                     # [0, 7]
print(naive_find_all("aaaaaa", "aa"))                            # [0, 1, 2, 3, 4]     overlapping matches count
```

Cost `O(n * m)` worst case (try `text = "a" * 1_000_000`, `pattern = "a" * 500_000 + "b"`). The algorithms below get it to `O(n + m)`.

We will test every algorithm against this one:

```python
import random

def random_text(n, alphabet="ab"):
    return "".join(random.choice(alphabet) for _ in range(n))
random.seed(3)
```

## 2. Rabin-Karp: matching with a rolling hash

**Idea:** compare **hashes** instead of strings. If `hash(window) == hash(pattern)`, check the characters (hashes can collide). The trick that makes it fast: the hash of the next window is computed from the previous one in `O(1)`, a **rolling hash**.

Treat the string as a number in base `B`: `hash("abc") = a*B^2 + b*B + c (mod M)`. Sliding the window one step to the right means **remove the leftmost character's contribution, shift, add the new character**:

```text
window "abc" -> "bcd":   hash = (hash - a * B^(m-1)) * B + d     (all mod M)
```

```python
def rabin_karp(text, pattern, base=256, mod=1_000_000_007):
    n, m = len(text), len(pattern)
    if m > n:
        return []
    high = pow(base, m - 1, mod)                                 # weight of the leftmost character
    p_hash = w_hash = 0
    for i in range(m):                                           # hash of the pattern and of the first window
        p_hash = (p_hash * base + ord(pattern[i])) % mod
        w_hash = (w_hash * base + ord(text[i])) % mod
    matches = []
    for i in range(n - m + 1):
        if p_hash == w_hash and text[i:i + m] == pattern:        # verify: a hash match might be a collision
            matches.append(i)
        if i < n - m:
            w_hash = ((w_hash - ord(text[i]) * high) * base + ord(text[i + m])) % mod     # roll the window
    return matches

print(rabin_karp("abracadabra", "abra"))                         # [0, 7]
for _ in range(500):
    t, pat = random_text(random.randint(0, 40)), random_text(random.randint(1, 5))
    assert rabin_karp(t, pat) == naive_find_all(t, pat)
print("Rabin-Karp matched the naive search on 500 random cases")  # Rabin-Karp matched the naive search on 500 random cases
```

**Cost:** `O(n + m)` expected (each window costs `O(1)` plus a verification only on hash matches), worst case `O(n * m)` if many collisions occur (with a large random modulus that is vanishingly unlikely). Hash collisions cannot cause wrong answers here because we verify.

**Where it shines: searching for many patterns at once.** Put the hashes of all (same-length) patterns in a set and check each window with one lookup:

```python
def find_any_of(text, patterns, base=256, mod=1_000_000_007):
    m = len(patterns[0])                                         # all patterns have the same length m
    wanted = {}
    for pat in patterns:
        h = 0
        for ch in pat:
            h = (h * base + ord(ch)) % mod
        wanted.setdefault(h, set()).add(pat)
    high, w_hash, found = pow(base, m - 1, mod), 0, []
    for i, ch in enumerate(text):
        w_hash = (w_hash * base + ord(ch)) % mod if i < m else ((w_hash - ord(text[i - m]) * high) * base + ord(ch)) % mod
        if i >= m - 1 and text[i - m + 1:i + 1] in wanted.get(w_hash, ()):
            found.append((i - m + 1, text[i - m + 1:i + 1]))
    return found

print(find_any_of("the quick brown fox jumps over the lazy dog", ["over", "lazy", "jump", "quic"]))
# [(4, 'quic'), (20, 'jump'), (26, 'over'), (35, 'lazy')]
```

Used for plagiarism detection (matching many text fragments), the rsync file-sync algorithm (a rolling checksum to find unchanged blocks) and finding duplicate content.

### Rolling hash for substrings: `longest repeated substring` by binary search

A rolling hash plus binary search on the length answers "is there a substring of length `L` that appears twice?" in `O(n)`, monotonic in `L`, so binary search finds the longest:

```python
def has_repeat(text, length, base=256, mod=(1 << 61) - 1):
    if length == 0:
        return True
    high, h, seen = pow(base, length - 1, mod), 0, {}
    for i, ch in enumerate(text):
        if i < length:
            h = (h * base + ord(ch)) % mod
        else:
            h = ((h - ord(text[i - length]) * high) * base + ord(ch)) % mod
        if i >= length - 1:
            start = i - length + 1
            if h in seen and text[seen[h]:seen[h] + length] == text[start:start + length]:
                return True
            seen.setdefault(h, start)
    return False

def longest_repeated_substring(text):
    lo, hi = 0, len(text) - 1                                    # the longest repeat is shorter than the text
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if has_repeat(text, mid):
            lo = mid
        else:
            hi = mid - 1
    return lo

print(longest_repeated_substring("banana"), longest_repeated_substring("abcdef"), longest_repeated_substring("abcabcabcabc"))      # 3 0 9
```

(`banana` repeats `ana`; `abcabcabcabc` repeats `abcabcabc` at offsets 0 and 3.)

## 3. The Z-function: how much matches the start?

For a string `s`, `z[i]` is the length of the longest common prefix of `s` and the suffix starting at `i`. It looks like a puzzle but gives linear-time matching and many other tools.

```text
s = "aabxaab"
i:    0  1  2  3  4  5  6
z:    -  1  0  0  3  1  0       z[4] = 3: the suffix "aab" matches the first three characters
```

**Computing it in `O(n)`** uses a window `[l, r)` that remembers the farthest-reaching match found so far; inside that window the answer for `i` is already known from earlier values:

```python
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

print(z_function("aabxaab"))                                     # [0, 1, 0, 0, 3, 1, 0]
print(z_function("aaaaa"))                                       # [0, 4, 3, 2, 1]
```

Each character is compared as part of an extension at most once beyond `r`, and `r` only moves forward, so the total work is `O(n)`.

**Pattern matching with Z:** build `pattern + "#" + text` (a separator that occurs in neither) and report every `i` where `z[i] == len(pattern)`:

```python
def z_find_all(text, pattern):
    combined = pattern + "\x00" + text                            # \x00 never appears in normal text
    z = z_function(combined)
    m = len(pattern)
    return [i - m - 1 for i in range(m + 1, len(combined)) if z[i] == m]

print(z_find_all("abracadabra", "abra"))                         # [0, 7]
for _ in range(500):
    t, pat = random_text(random.randint(0, 40)), random_text(random.randint(1, 5))
    assert z_find_all(t, pat) == naive_find_all(t, pat)
print("Z-function search matched the naive search on 500 random cases")      # Z-function search matched the naive search on 500 random cases
```

**More uses of Z:** the shortest repeating period of a string (`period p` if `z[p] == n - p` and `p` divides `n`), counting distinct substrings, string compression checks.

```python
def smallest_period(s):
    z = z_function(s)
    n = len(s)
    for p in range(1, n):
        if n % p == 0 and z[p] == n - p:
            return s[:p]
    return s

print(smallest_period("abcabcabc"), smallest_period("aaaa"), smallest_period("abcd"), smallest_period("abababab"))      # abc a abcd ab
```

## 4. KMP's prefix function (recap and comparison)

The [KMP algorithm](../../02-data-structures/arrays-strings/03-strings-in-depth.md) uses the **prefix function** `pi[i]`: the length of the longest proper prefix of `s[:i+1]` that is also a suffix of it. It is the cousin of the Z-function (each can be converted into the other) and gives the same `O(n + m)` matching.

```python
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

print(prefix_function("aabaaab"))                                # [0, 1, 0, 1, 2, 2, 3]
print(prefix_function("abcabcd"))                                # [0, 0, 0, 1, 2, 3, 0]
```

| Algorithm | Time | Extra memory | Strength |
|-----------|------|--------------|----------|
| Naive | `O(nm)` worst | `O(1)` | simplest; fine for small inputs |
| **Rabin-Karp** | `O(n + m)` expected | `O(1)` | many patterns, 2D matching, simple |
| **KMP / Z** | `O(n + m)` guaranteed | `O(m)` / `O(n + m)` | deterministic, streaming (KMP) |
| **Aho-Corasick** | `O(n + total pattern length + matches)` | `O(sum of patterns)` | many different-length patterns (a trie plus KMP-style failure links; used by `grep -F`, antivirus signatures) |
| Python's `in` / `str.find` | fast in practice | | a tuned mix (two-way/Boyer-Moore-Horspool style); use it unless you need the structure above |

## 5. Manacher's algorithm: all palindromes in linear time

The [dynamic-programming lesson](../dynamic-programming/02-dp-on-two-sequences-and-grids.md) found the longest palindromic substring in `O(n^2)` by expanding around each center. **Manacher's algorithm** does it in `O(n)` by reusing mirrored information, the same trick as the Z-function.

First transform the string so every palindrome has odd length: insert a separator between characters (`"abba" -> "#a#b#b#a#"`). Then `radius[i]` is how far a palindrome centered at `i` extends; keep the window of the rightmost palindrome and use its mirror:

```python
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

def longest_palindrome_naive(s):
    best = ""
    for center in range(len(s)):
        for lo, hi in ((center, center), (center, center + 1)):
            while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
                lo -= 1; hi += 1
            best = max(best, s[lo + 1:hi], key=len)
    return best

print(manacher("babad")[0], manacher("cbbd")[0], manacher("forgeeksskeegfor")[0])        # bab bb geeksskeeg
for _ in range(500):
    s = random_text(random.randint(1, 30), "abc")
    assert len(manacher(s)[0]) == len(longest_palindrome_naive(s))
print("Manacher matched the naive longest palindrome length on 500 random cases")       # Manacher matched the naive longest palindrome length on 500 random cases

def count_palindromic_substrings(s):                            # the radii also count ALL palindromic substrings
    _, radius = manacher(s)
    return sum((r + 1) // 2 for r in radius)

print(count_palindromic_substrings("aaa"), count_palindromic_substrings("abc"), count_palindromic_substrings("abba"))     # 6 3 6
```

## 6. Suffix arrays: sorting all suffixes

A **suffix array** lists the starting positions of all suffixes of `s` **in sorted order**. It is a compact cousin of the **suffix tree**, a structure behind fast substring search in large texts (genomes, code search).

```text
s = "banana"
suffixes:  0 banana   1 anana   2 nana   3 ana   4 na   5 a
sorted:    5 a   3 ana   1 anana   0 banana   4 na   2 nana
suffix array = [5, 3, 1, 0, 4, 2]
```

**Why it helps:** every substring is a prefix of some suffix, and suffixes that start with the same text are **adjacent** in sorted order. So substring search becomes **binary search** over the array.

```python
def suffix_array(s):
    return sorted(range(len(s)), key=lambda i: s[i:])           # simple: O(n^2 log n) worst case, fine for learning and moderate n

sa = suffix_array("banana")
print(sa, [("banana"[i:]) for i in sa])                          # [5, 3, 1, 0, 4, 2] ['a', 'ana', 'anana', 'banana', 'na', 'nana']

def contains(text, sa, pattern):
    lo, hi = 0, len(sa)
    while lo < hi:                                               # binary search for the first suffix >= pattern
        mid = (lo + hi) // 2
        if text[sa[mid]:sa[mid] + len(pattern)] < pattern:
            lo = mid + 1
        else:
            hi = mid
    return lo < len(sa) and text[sa[lo]:sa[lo] + len(pattern)] == pattern

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

text = "banana"
print(contains(text, sa, "nan"), contains(text, sa, "nab"), count_occurrences(text, sa, "ana"), count_occurrences(text, sa, "a"))
# True False 2 3
```

After one preprocessing pass, **each query takes `O(m log n)`** regardless of how many queries you make, whereas the naive search costs `O(nm)` every time. Ideal for "index a big text once, query it many times."

### The LCP array: where adjacent suffixes agree

`lcp[i]` is the length of the longest common prefix of the suffixes at `sa[i-1]` and `sa[i]`. **Kasai's algorithm** builds it in `O(n)`:

```python
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

lcp = lcp_array("banana", sa)
print(lcp)                                                       # [0, 1, 3, 0, 0, 2]
```

Reading it: the suffixes `a`/`ana` share 1 character; `ana`/`anana` share 3 (`ana`); `na`/`nana` share 2.

**Applications of suffix array + LCP:**

```python
def longest_repeated_via_sa(s):
    sa = suffix_array(s)
    lcp = lcp_array(s, sa)
    best = max(range(len(s)), key=lambda i: lcp[i])
    return s[sa[best]:sa[best] + lcp[best]]                      # the largest LCP is the longest repeated substring

def distinct_substrings(s):
    sa = suffix_array(s)
    lcp = lcp_array(s, sa)
    n = len(s)
    return n * (n + 1) // 2 - sum(lcp)                           # all substrings minus the repeats counted by the LCP

print(longest_repeated_via_sa("banana"), longest_repeated_via_sa("mississippi"))        # ana issi
print(distinct_substrings("banana"), len({"banana"[i:j] for i in range(6) for j in range(i + 1, 7)}))          # 15 15
print(distinct_substrings("aaaa"), distinct_substrings("abcd"))                          # 4 10
```

(Production implementations build the suffix array in `O(n log n)` by prefix doubling or `O(n)` with SA-IS; the simple sort above is plenty for learning and for moderate text sizes. In bioinformatics, suffix arrays and the closely related **Burrows-Wheeler transform / FM-index** align DNA reads against genomes of billions of letters.)

## 7. Choosing the right tool

| Task | Tool |
|------|------|
| One pattern, once, normal sizes | Python's `in` / `str.find` / `re` |
| One pattern, guaranteed linear time or streaming | KMP |
| Many equal-length patterns, or rolling checksums | Rabin-Karp |
| Prefix/period/border questions | Z-function or prefix function |
| Longest palindrome, count palindromes | Manacher |
| Many different-length patterns | Aho-Corasick (or a [trie](../../02-data-structures/tries/01-tries.md)) |
| Index a big text for many queries; repeats, distinct substrings | suffix array + LCP (or suffix tree / automaton) |
| Prefix autocomplete | [trie](../../02-data-structures/tries/01-tries.md) |
| Fuzzy / approximate matching | [edit distance](../dynamic-programming/02-dp-on-two-sequences-and-grids.md) |

## 8. Two real-world examples

**Example 1: Plagiarism and duplicate detection.** Documents are cut into overlapping fixed-length chunks ("shingles"), each hashed with a rolling hash; matching hashes (verified) reveal copied passages in near-linear time even across millions of documents. `rsync` and backup tools use a rolling checksum to spot which blocks of a file changed.

**Example 2: DNA read alignment and code search.** A genome (3 billion letters) is indexed once with a suffix-array-style structure; each short read is then located by binary search in a few microseconds. The same index idea underlies fast substring search in large code bases and logs.

## 9. Common mistakes

- Using a rolling hash and trusting a hash match without verifying (collisions give false positives).
- Forgetting that `(a - b) % m` needs a non-negative result in languages other than Python.
- A small modulus or a poor base (many collisions): use a large prime modulus (or `2^61 - 1`) and a random base against adversarial input.
- Forgetting a separator that does not occur in the text when concatenating `pattern + sep + text` for Z-function matching.
- Counting overlapping matches wrongly (`"aaaa".count("aa")` is 2, not 3; use the algorithms above for overlapping matches).
- Building suffix arrays by slicing for very large texts (the slices copy `O(n^2)` memory; use a real construction).
- Off-by-one when mapping Manacher's transformed indices back to the original string.

## 10. Practice

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

## 11. Check yourself

1. How does a rolling hash update in O(1)?
2. Why must Rabin-Karp verify hash matches?
3. What does `z[i]` mean and how is the whole array computed in linear time?
4. How does Manacher avoid recomputing palindrome radii?
5. What is a suffix array and how does it speed up substring queries?
6. What does the LCP array tell you?

<details>
<summary>Answers</summary>

1. Subtract the leaving character's contribution (`char * base^(m-1)`), multiply by the base, add the entering character, all modulo `M`.
2. Different strings can have equal hashes (collisions), so a match must be confirmed character by character.
3. The length of the longest common prefix between the string and the suffix starting at `i`; a window `[l, r)` of the farthest match lets each `z[i]` start from a known value and only extend forward.
4. Inside the current rightmost palindrome, a position's radius is at least the mirror position's radius (capped by the window), so it starts from that value and only extends outward.
5. The sorted list of suffix start positions; since every substring is a prefix of a suffix and equal prefixes are adjacent, binary search finds a pattern in `O(m log n)` per query after one preprocessing pass.
6. For adjacent sorted suffixes, how many leading characters they share: the maximum is the longest repeated substring, and `n(n+1)/2 - sum(lcp)` counts distinct substrings.

</details>

[Back to algorithms](../README.md)
