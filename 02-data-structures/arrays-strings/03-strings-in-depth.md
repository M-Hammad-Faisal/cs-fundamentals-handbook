# Strings in Depth

**Prerequisites:** [arrays and memory](01-arrays-and-memory.md), [binary and text encoding](../../00-foundations/computer-basics/binary-and-data-representation.md). **You will learn:** what a string really is, why strings are immutable and what that costs, how to slice, search, split and build text efficiently, classic string algorithms (palindromes, anagrams, substring search, KMP), regular expressions basics, and Unicode pitfalls.

## 1. In plain words

A **string** is a **sequence of characters**: an array whose items are letters, digits and symbols. Everything you read from a file, a form, a network or a database starts as text, so string handling is one of the most common jobs in programming.

```text
 s = "python"
 index:    0   1   2   3   4   5
         ┌───┬───┬───┬───┬───┬───┐
         │ p │ y │ t │ h │ o │ n │
         └───┴───┴───┴───┴───┴───┘
 negative: -6  -5  -4  -3  -2  -1
```

## 2. Strings are immutable

In Python (and Java, JavaScript, C#) you **cannot change a string in place**. Methods that look like they modify it **return a new string**.

```python
s = "hello"
try:
    s[0] = "J"                                   # TypeError: 'str' object does not support item assignment
except TypeError as error:
    print("TypeError:", error)

t = "J" + s[1:]                                  # build a NEW string
print(s, t, s is t)                              # hello Jello False
print(s.upper(), s)                              # HELLO hello      (the original is unchanged)
```

Why immutable? Safe to share, usable as dictionary keys (hashable), simpler reasoning. The price: **every "change" copies the string** (`O(n)`), so building a long string by repeated `+=` can be quadratic ([cost sheet](../../01-complexity/07-python-operations-cheat-sheet.md)).

```python
import time

def build_with_plus(n):
    s = ""
    for i in range(n):
        s = s + str(i)                           # a new string each time
    return s

def build_with_join(n):
    return "".join(str(i) for i in range(n))      # collect, then join once: O(total length)

assert build_with_plus(2000) == build_with_join(2000)
t = time.perf_counter(); build_with_join(200_000); print(time.perf_counter() - t < 1)     # True
```

**Rule:** to build text from many pieces, put them in a list and `"".join(pieces)`. For text you need to edit character by character, use a `list` of characters (mutable) and join at the end.

```python
chars = list("hello")
chars[0] = "J"
print("".join(chars))                            # Jello
```

## 3. Indexing and slicing

```python
s = "Hello, World!"
print(s[0], s[7], s[-1], s[-6])                  # H W ! W
print(s[0:5], s[7:], s[:5], s[-6:], s[:])        # Hello World! Hello World! Hello, World!
print(s[::2], s[::-1], s[7:12][::-1])            # Hlo ol! !dlroW ,olleH dlroW
print(len(s), s.index("W"), s[s.index("W"):])    # 13 7 World!
```

The slice `s[start:stop:step]` includes `start` and excludes `stop`; omitted values default to the ends. Out-of-range slices never raise: `"abc"[1:100]` is `"bc"`. A slice always creates a **new** string.

## 4. The string toolbox

```python
text = "  The Quick Brown Fox  "

# Cleaning
print(repr(text.strip()), repr(text.lstrip()), repr(text.rstrip()))    # 'The Quick Brown Fox' 'The Quick Brown Fox  ' '  The Quick Brown Fox'
print(text.lower().strip(), text.upper().strip(), text.title().strip(), "hello world".capitalize(), "Hello".swapcase())

# Searching
s = "banana"
print(s.find("an"), s.rfind("an"), s.find("zz"), s.count("an"), s.index("n"), "nan" in s)     # 1 3 -1 2 2 True
print(s.startswith("ba"), s.endswith("na"), s.startswith(("x", "b")))                         # True True True

# Splitting and joining
csv_line = "ana,31,lahore"
fields = csv_line.split(",")
print(fields, ",".join(fields), "a  b   c".split(), "a-b-c".split("-", 1), "k=v=w".partition("="))
# ['ana', '31', 'lahore'] ana,31,lahore ['a', 'b', 'c'] ['a', 'b-c'] ('k', '=', 'v=w')
print("line1\nline2\n".splitlines(), "tabs\tand spaces".split())     # ['line1', 'line2'] ['tabs', 'and', 'spaces']

# Replacing and translating
print("banana".replace("a", "o"), "banana".replace("a", "o", 2), "a-b_c".translate(str.maketrans("-_", "  ")))    # bonono bonona a b c

# Testing character classes
print("abc".isalpha(), "123".isdigit(), "ab1".isalnum(), "  ".isspace(), "Hello".istitle(), "hello".islower())   # True True True True True True

# Padding and alignment
print("7".zfill(3), "ab".ljust(5, ".") + "|", "ab".rjust(5, ".") + "|", "ab".center(6, "*"))                    # 007 ab...| ...ab| **ab**

# Removing prefixes/suffixes (3.9+)
print("test_data.csv".removesuffix(".csv"), "test_data.csv".removeprefix("test_"))                              # test_data data.csv
```

### Formatting

```python
name, score, ratio = "Ana", 91.456, 0.256
print(f"{name:<6}|{score:>8.1f}|{ratio:.1%}|{1234567:,}|{255:08b}|{255:#x}")     # Ana   |    91.5|25.6%|1,234,567|11111111|0xff
print("%s scored %.1f" % (name, score), "{} scored {:.1f}".format(name, score))  # (older styles still work)
print(f"{name!r} {name=}")                                                       # 'Ana' name='Ana'
```

## 5. Characters and encodings

A string is a sequence of **Unicode code points**; `len` counts characters, not bytes. When saving or sending text you **encode** it into bytes (almost always **UTF-8**), and **decode** when reading.

```python
word = "naïve café 😀"
print(len(word), len(word.encode("utf-8")), [hex(ord(c)) for c in "aï😀"])      # 12 17 ['0x61', '0xef', '0x1f600']
print(word.encode("utf-8")[:8], b"na\xc3\xafve".decode("utf-8"))                # b'na\xc3\xafve c' naïve
print(ord("A"), chr(97), ord("a") - ord("A"), chr(ord("a") + 1))                # 65 a 32 b
print("ABC".casefold() == "abc", "straße".casefold() == "STRASSE".casefold())   # True True  (casefold is the correct case-insensitive comparison)

# Unicode surprises: one visible character can be several code points
import unicodedata
a, b = "é", "é"                                    # "é" as one code point vs "e" + a combining accent
print(a == b, len(a), len(b), unicodedata.normalize("NFC", b) == a)             # False 1 2 True
```

Practical rules: open files with `encoding="utf-8"`; **normalize** (`unicodedata.normalize("NFC", s)`) before comparing user text; use `casefold()` for case-insensitive comparisons; never assume one character equals one byte.

## 6. Classic string algorithms

### Palindrome

```python
def is_palindrome(s):
    cleaned = [c.lower() for c in s if c.isalnum()]
    return cleaned == cleaned[::-1]                       # O(n) time, O(n) space; two pointers gives O(1) space
print(is_palindrome("Was it a car or a cat I saw?"), is_palindrome("Python"))     # True False
```

### Anagrams (same letters, different order)

```python
from collections import Counter

def is_anagram(a, b):
    return Counter(a.replace(" ", "").lower()) == Counter(b.replace(" ", "").lower())   # O(n)
def group_anagrams(words):
    groups = {}
    for w in words:
        groups.setdefault("".join(sorted(w)), []).append(w)                             # the sorted letters are the shared key
    return list(groups.values())
print(is_anagram("Dormitory", "Dirty room"), group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]))
# True [['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]
```

### Character frequency and the first unique character

```python
def first_unique_char(s):
    counts = Counter(s)
    for i, ch in enumerate(s):
        if counts[ch] == 1:
            return i
    return -1
print(first_unique_char("leetcode"), first_unique_char("aabb"), Counter("mississippi").most_common(2))
# 0 -1 [('i', 4), ('s', 4)]
```

### Reverse words, compress, check rotations

```python
def reverse_words(sentence):
    return " ".join(sentence.split()[::-1])
def compress(s):                                           # run-length encoding: "aaabcc" -> "a3b1c2"
    out, i = [], 0
    while i < len(s):
        j = i
        while j < len(s) and s[j] == s[i]:
            j += 1
        out.append(f"{s[i]}{j - i}")
        i = j
    return "".join(out)
def is_rotation(a, b):
    return len(a) == len(b) and b in a + a                 # "erbottlewat" is in "waterbottlewaterbottle"
print(reverse_words("the sky is blue"), compress("aaabcc"), is_rotation("waterbottle", "erbottlewat"))    # blue is sky the a3b1c2 True
```

### Substring search: naive versus KMP

Finding `pattern` (length `m`) inside `text` (length `n`).

```python
def naive_search(text, pattern):
    """O(n * m) worst case: re-compares characters after every mismatch."""
    hits, comparisons = [], 0
    for i in range(len(text) - len(pattern) + 1):
        j = 0
        while j < len(pattern):
            comparisons += 1
            if text[i + j] != pattern[j]:
                break
            j += 1
        if j == len(pattern):
            hits.append(i)
    return hits, comparisons

def build_failure(pattern):
    """failure[i] = length of the longest proper prefix of pattern[:i+1] that is also a suffix of it."""
    failure, k = [0] * len(pattern), 0
    for i in range(1, len(pattern)):
        while k and pattern[i] != pattern[k]:
            k = failure[k - 1]
        if pattern[i] == pattern[k]:
            k += 1
        failure[i] = k
    return failure

def kmp_search(text, pattern):
    """Knuth-Morris-Pratt: O(n + m). Never moves backward in the text."""
    failure, hits, k, comparisons = build_failure(pattern), [], 0, 0
    for i, ch in enumerate(text):
        while k and ch != pattern[k]:
            comparisons += 1
            k = failure[k - 1]                              # reuse what we already matched
        comparisons += 1
        if ch == pattern[k]:
            k += 1
        if k == len(pattern):
            hits.append(i - k + 1)
            k = failure[k - 1]
    return hits, comparisons

text, pattern = "a" * 5000 + "b", "a" * 100 + "b"          # a nasty case for the naive algorithm
print(naive_search(text, pattern)[0] == kmp_search(text, pattern)[0])               # True (same matches)
print(naive_search(text, pattern)[1], kmp_search(text, pattern)[1])                 # 495001 versus 9901 comparisons
print(build_failure("ababaca"), kmp_search("abababcabababa", "ababa")[0])           # [0, 0, 1, 2, 3, 0, 1] [0, 7, 9]
```

Python's built-in `text.find(pattern)` and `pattern in text` use well-tuned algorithms; you rarely write your own, but KMP shows the key idea: **use what you already matched** to avoid re-reading.

## 7. Regular expressions (patterns for text)

A **regular expression (regex)** describes a pattern of text. The `re` module searches, extracts and replaces.

| Pattern | Meaning |
|---------|---------|
| `.` | any one character (except newline) |
| `\d`, `\w`, `\s` | a digit, a word character (letter/digit/_), a whitespace |
| `[abc]`, `[a-z]`, `[^0-9]` | one of the set; a range; anything except digits |
| `*`, `+`, `?`, `{2,4}` | zero or more; one or more; optional; between 2 and 4 repeats |
| `^`, `$` | start / end of the string |
| `(...)` | a **group** to capture |
| `\|` | alternation (or) |
| `\b` | word boundary |

```python
import re

log = "2026-11-07 ERROR user=ayesha ip=203.0.113.9 msg='disk full'"
m = re.search(r"(\d{4})-(\d{2})-(\d{2})", log)
print(m.groups(), m.group(0), m.start())                           # ('2026', '11', '07') 2026-11-07 0
print(re.findall(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", log))             # ['203.0.113.9']    (all IPv4-looking numbers)
print(re.findall(r"(\w+)=(\S+)", log))                             # [('user', 'ayesha'), ('ip', '203.0.113.9'), ('msg', "'disk")]   (\S+ stops at the space: a regex does exactly what you write)
print(re.sub(r"\d", "#", "call 0300-1234567"), re.split(r"[,;]\s*", "a, b;c,  d"))     # call ####-####### ['a', 'b', 'c', 'd']

email = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")                  # compile once if you use a pattern many times
print([bool(email.match(e)) for e in ("a@x.com", "bad@", "no at.com")])                # [True, False, False]

named = re.search(r"(?P<user>\w+)@(?P<domain>[\w.]+)", "write to bob@example.org today")
print(named.group("user"), named.group("domain"))                  # bob example.org
```

Tips: use **raw strings** (`r"..."`) so backslashes are literal; prefer simple string methods (`startswith`, `split`, `in`) when they suffice; **do not parse HTML or validate every email with a regex**; beware **catastrophic backtracking** (`(a+)+b` on a long string of `a`s can take exponential time: a real denial-of-service risk).

## 8. Complexity summary

| Operation | Cost |
|-----------|------|
| `s[i]`, `len(s)` | `O(1)` |
| slice `s[i:j]`, `s + t`, `s * k`, `.upper()`, `.replace()`, `.split()`, `.strip()`, `.find()` | `O(n)` |
| `"".join(parts)` | `O(total length)` |
| `s += t` repeatedly | up to `O(n²)` total |
| comparing `s == t` | `O(min(n, m))` |
| hashing a string | `O(n)` (cached after the first time) |
| `sorted(s)` | `O(n log n)` |
| naive substring search | `O(n · m)`; KMP `O(n + m)` |

## 9. Two real-world examples

**Example 1: Cleaning user input.** A signup form receives `"  Ayesha.Khan@Example.COM "`. The server strips whitespace, lowercases, validates the shape with a simple regex, and stores the normalized value, so `ayesha.khan@example.com` and ` AYESHA.KHAN@EXAMPLE.COM` do not become two accounts. Names go through Unicode normalization so `é` typed two different ways compares equal.

**Example 2: Search and highlighting.** A documentation site searches 50,000 pages for a phrase. A precomputed index finds candidate pages quickly; for highlighting inside a page it uses `str.find`/regex to locate matches and builds the output with `"".join` (never repeated `+=`). Log-analysis tools do the same with regular expressions over gigabytes of text, streaming line by line to keep memory flat ([generators](../../08-modern-python/generators-functional/README.md)).

## 10. Common mistakes

- Trying to modify a string in place (`s[0] = "x"`).
- Building big strings with `+=` in a loop.
- Comparing text case-insensitively with `.lower()` only (use `casefold()`), or without normalizing Unicode.
- Assuming `len(s)` equals the number of bytes or visible symbols.
- Forgetting that `split()` with no arguments collapses whitespace, while `split(" ")` does not.
- Using `==` vs `is` for strings (use `==`).
- Writing a regex when `in`, `startswith` or `split` would do; writing a regex that can backtrack exponentially.
- Forgetting to specify `encoding="utf-8"` when reading/writing files.

## 11. Practice

1. Count vowels, consonants, digits and spaces in a string in one pass.
2. Write `is_anagram` without `Counter` or `sorted` using a 26-slot count array.
3. Find the longest common prefix of a list of words.
4. Implement `title_case(text)` without `str.title` (capitalize each word's first letter).
5. Write a function that checks whether a string has balanced brackets `()[]{}` (hint: a stack).
6. Use `re` to extract all hashtags and mentions from a tweet.
7. Find the first non-repeating character in `O(n)` and the longest substring without repeating characters in `O(n)`.
8. Convert `"snake_case_name"` to `"camelCaseName"` and back.

<details>
<summary>Solutions</summary>

**1.**
```python
def classify(text):
    return {"vowels": sum(c in "aeiouAEIOU" for c in text), "consonants": sum(c.isalpha() and c not in "aeiouAEIOU" for c in text),
            "digits": sum(c.isdigit() for c in text), "spaces": sum(c.isspace() for c in text)}
print(classify("Hello World 2026"))        # {'vowels': 3, 'consonants': 7, 'digits': 4, 'spaces': 2}
```

**2.**
```python
def is_anagram_counts(a, b):
    counts = [0] * 26
    for ch in a.lower():
        if ch.isalpha(): counts[ord(ch) - 97] += 1
    for ch in b.lower():
        if ch.isalpha(): counts[ord(ch) - 97] -= 1
    return not any(counts)
print(is_anagram_counts("Listen", "Silent"), is_anagram_counts("abc", "abd"))       # True False
```

**3.**
```python
def common_prefix(words):
    prefix = words[0]
    for w in words[1:]:
        while not w.startswith(prefix):
            prefix = prefix[:-1]
    return prefix
print(repr(common_prefix(["flower", "flow", "flight"])), repr(common_prefix(["dog", "car"])))     # 'fl' ''
```

**4.**
```python
def title_case(text):
    return " ".join(w[:1].upper() + w[1:].lower() for w in text.split())
print(title_case("the qUICK brown fox"))        # The Quick Brown Fox
```

**5.**
```python
def balanced(s):
    pairs, stack = {")": "(", "]": "[", "}": "{"}, []
    for ch in s:
        if ch in "([{": stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]: return False
    return not stack
print(balanced("{[()]}"), balanced("([)]"), balanced("(("))      # True False False
```

**6.**
```python
tweet = "Loving #python and #algorithms with @ayesha and @bilal!"
print(re.findall(r"#(\w+)", tweet), re.findall(r"@(\w+)", tweet))      # ['python', 'algorithms'] ['ayesha', 'bilal']
```

**7.**
```python
def longest_unique(s):
    last, left, best = {}, 0, 0
    for right, ch in enumerate(s):
        if ch in last and last[ch] >= left:
            left = last[ch] + 1
        last[ch] = right
        best = max(best, right - left + 1)
    return best
print(first_unique_char("loveleetcode"), longest_unique("abcabcbb"), longest_unique("pwwkew"))       # 2 3 3
```

**8.**
```python
def to_camel(snake):
    first, *rest = snake.split("_")
    return first + "".join(w.capitalize() for w in rest)
def to_snake(camel):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", camel).lower()
print(to_camel("snake_case_name"), to_snake("camelCaseName"))      # snakeCaseName camel_case_name
```

</details>

## 12. Check yourself

1. Why can't you change a string in place, and what do you do instead?
2. What is the fastest way to build a string from many pieces?
3. What is the difference between characters and bytes?
4. When would you use `casefold()` instead of `lower()`?
5. What problem does KMP solve and what is its complexity?
6. Name two dangers of regular expressions.

<details>
<summary>Answers</summary>

1. Strings are immutable; create a new string (slicing, methods) or edit a list of characters and join it.
2. Append the pieces to a list and call `"".join(pieces)`.
3. A character is a Unicode code point; bytes are the encoded form (UTF-8 uses 1-4 bytes per character), so `len(s)` and `len(s.encode())` can differ.
4. For correct case-insensitive comparison across languages (for example German `ß`).
5. It finds a pattern in a text in `O(n + m)` by never re-examining matched characters.
6. Catastrophic backtracking (exponential time on crafted input) and using them where simple string methods or a real parser would be clearer/safer.

</details>

[Back to arrays and strings](README.md) · Previous: [array techniques](02-array-techniques.md)
