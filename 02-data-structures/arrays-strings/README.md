# Arrays and Strings

## Detailed lessons

1. [Arrays and memory](01-arrays-and-memory.md): addresses, static vs dynamic arrays, how `list` grows
2. [Array techniques](02-array-techniques.md): two pointers, sliding window, prefix sums, Kadane, binary search
3. [Strings in depth](03-strings-in-depth.md): immutability, Unicode, anagrams, KMP, regex

The rest of this page is the quick reference.

## 1. The concept

An **array** stores elements in **contiguous memory**, so the element at index `i` lives at `base_address + i * element_size`. That arithmetic is why indexing is `O(1)`: the computer jumps straight to the address with no searching.

A **string** is a sequence of characters, conceptually an array of characters. In Python, strings are **immutable**: you cannot change a character in place, you build a new string.

### Static vs dynamic arrays

| Kind | Size | Example |
|------|------|---------|
| **Static array** | Fixed at creation | C arrays, `array.array`, NumPy arrays |
| **Dynamic array** | Grows automatically | Python `list`, Java `ArrayList`, C++ `vector` |

A dynamic array keeps spare capacity. When full, it allocates a bigger block (CPython grows by about 12.5%, plus a small constant), copies the elements, and frees the old block. Resizes are rare, so appending is **amortized `O(1)`**.

Python's `list` stores *pointers* to objects, not the objects themselves. That is why a list can hold mixed types, and why it uses more memory than a packed C array. For large numeric data use `array.array` or NumPy.

## 2. How it works

```
index:    0     1     2     3     4
value:  [ 10 ] [ 20 ] [ 30 ] [ 40 ] [ 50 ]
address: 1000  1008  1016  1024  1032     (8 bytes each)
```

### Complexity of core operations

| Operation | Cost | Why |
|-----------|------|-----|
| Read/write `a[i]` | `O(1)` | Address arithmetic |
| Append at end | `O(1)` amortized | Spare capacity |
| Insert/delete at index `i` | `O(n)` | Shift elements after `i` |
| Insert/delete at front | `O(n)` | Shift everything |
| Search unsorted | `O(n)` | Scan |
| Search sorted | `O(log n)` | Binary search |
| Slice `a[i:j]` | `O(j - i)` | Copies |

### Pseudocode: insert at index

```
insert(arr, index, value):
    ensure capacity (grow if full)
    for k from len(arr) down to index + 1:
        arr[k] = arr[k - 1]        # shift right
    arr[index] = value
    len = len + 1
```

### Python essentials

```python
a = [3, 1, 4, 1, 5]
a.append(9)            # O(1) amortized
a.insert(0, 7)         # O(n)
a.pop()                # O(1) from the end
a.pop(0)               # O(n) from the front
a.sort()               # O(n log n), in place, stable
b = sorted(a, reverse=True)

a[1:4]                 # slice (copy)
a[::-1]                # reversed copy
[x * 2 for x in a]     # list comprehension
```

## 3. Core techniques

### Two pointers

Use two indices moving through the array to avoid nested loops.

```python
def is_palindrome(s):
    i, j = 0, len(s) - 1
    while i < j:
        if s[i] != s[j]:
            return False
        i += 1
        j -= 1
    return True                     # O(n) time, O(1) space

def two_sum_sorted(nums, target):   # nums sorted ascending
    i, j = 0, len(nums) - 1
    while i < j:
        s = nums[i] + nums[j]
        if s == target:
            return (i, j)
        if s < target:
            i += 1
        else:
            j -= 1
    return None                     # O(n)
```

### Sliding window

Maintain a window `[left, right]` and update a running value instead of recomputing.

```python
def max_sum_window(nums, k):
    window = sum(nums[:k])
    best = window
    for right in range(k, len(nums)):
        window += nums[right] - nums[right - k]   # add new, drop old
        best = max(best, window)
    return best                                   # O(n)

def longest_unique_substring(s):
    last = {}                  # char -> most recent index
    left = best = 0
    for right, ch in enumerate(s):
        if ch in last and last[ch] >= left:
            left = last[ch] + 1
        last[ch] = right
        best = max(best, right - left + 1)
    return best                                   # O(n)
```

### Prefix sums

Precompute cumulative sums so any range sum is `O(1)`.

```python
def build_prefix(nums):
    prefix = [0]
    for x in nums:
        prefix.append(prefix[-1] + x)
    return prefix

def range_sum(prefix, i, j):        # sum of nums[i..j] inclusive
    return prefix[j + 1] - prefix[i]
```

### In-place modification

```python
def move_zeros_to_end(nums):
    write = 0
    for x in nums:
        if x != 0:
            nums[write] = x
            write += 1
    for i in range(write, len(nums)):
        nums[i] = 0                  # O(n) time, O(1) space
```

### Kadane's algorithm: maximum subarray

```python
def max_subarray(nums):
    best = cur = nums[0]
    for x in nums[1:]:
        cur = max(x, cur + x)        # extend or restart
        best = max(best, cur)
    return best                      # O(n)
```

## 4. Strings

### Immutability and building strings

```python no-run
# Slow: may copy the whole string each time -> O(n^2)
s = ""
for word in words:
    s += word

# Fast: O(n)
s = "".join(words)
```

### Common operations and their costs

| Operation | Cost |
|-----------|------|
| `len(s)`, `s[i]` | `O(1)` |
| `s + t` | `O(len(s) + len(t))` |
| `s[i:j]` | `O(j - i)` |
| `t in s` | `O(n * m)` worst case; usually fast |
| `s.split()`, `s.join(...)` | `O(n)` |
| `s.lower()`, `s.replace(...)` | `O(n)` |

### Anagram check with counting

```python
from collections import Counter

def is_anagram(a, b):
    return Counter(a) == Counter(b)       # O(n)

def group_anagrams(words):
    groups = {}
    for w in words:
        key = "".join(sorted(w))          # canonical form
        groups.setdefault(key, []).append(w)
    return list(groups.values())          # O(n * k log k)
```

### Unicode note

Python 3 strings are Unicode. `len("é")` can be 1 or 2 depending on whether it is a single code point or `e` plus a combining accent. Normalize with `unicodedata.normalize("NFC", s)` before comparing user text.

## 5. Two real-world examples

### Example 1: Video frame buffers and sensor streams

Cameras and sensors write fixed-size blocks into contiguous arrays. Contiguity gives `O(1)` indexing and excellent **cache locality**: the CPU loads neighbouring bytes together, so scanning an array is far faster than chasing pointers in a linked structure. This is why image processing, game engines and NumPy all rely on packed arrays.

### Example 2: Rolling averages for monitoring dashboards

A metrics system shows "average requests per second over the last 5 minutes". Recomputing from scratch every second costs `O(window)`. A **sliding window** (or prefix sums) updates the value in `O(1)` per new data point, which is why real-time dashboards stay cheap even with thousands of metrics.

## 6. Tips, tricks and pitfalls

- **Off-by-one errors** are the top bug. Decide whether ranges are inclusive or exclusive and stay consistent. Python slices are half-open: `a[i:j]` excludes `j`.
- **Do not modify a list while iterating over it.** Iterate over a copy or build a new list.
- **Shallow copies:** `b = a` shares the same list; `a[:]`/`a.copy()` copies one level; nested lists need `copy.deepcopy`.
- **`[[0] * m] * n` is a bug.** It repeats the *same* inner list `n` times. Use `[[0] * m for _ in range(n)]`.
- **Prefer `deque` for queues.** Popping from the front of a list is `O(n)`.
- **Sort first** to unlock two pointers, binary search, or grouping.
- **Use a set or dict** to replace an inner search loop and cut `O(n²)` to `O(n)`.
- **Slicing in loops copies.** `a[1:]` inside recursion makes recursion `O(n²)`; pass indices instead.
- **Edge cases to always test:** empty input, one element, all equal, negatives, duplicates, very large input.

## 7. Check yourself

1. Why is array indexing `O(1)` but inserting at the front `O(n)`?
2. Why is `list.append` amortized `O(1)`?
3. What is the bug in `grid = [[0] * 3] * 3`?
4. When do two pointers work, and what do they usually require about the input?
5. How does a prefix-sum array answer range-sum queries, and what is the build cost?
6. Why is repeated `s += x` slow, and what is the fix?
7. Describe Kadane's algorithm in one sentence.

<details>
<summary>Answers</summary>

1. Indexing is address arithmetic. Inserting at the front shifts every existing element one slot.
2. Spare capacity makes most appends a single write; resizes are rare and geometric, so total copying is linear over `n` appends.
3. All three rows are the same list object, so changing one row changes all. Use a comprehension.
4. They work when the structure lets you decide which pointer to move, usually a sorted array or a window with monotonic behavior.
5. Build in `O(n)`, then any range sum is `prefix[j+1] - prefix[i]` in `O(1)`.
6. Strings are immutable, so each `+=` may copy everything built so far. Collect parts and `"".join` them.
7. At each element, either extend the current subarray or restart from this element, whichever is larger, and track the best seen.

</details>

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

Back to the [part overview](../README.md).
