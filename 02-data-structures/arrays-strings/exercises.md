# Arrays and Strings: Exercises

## Warm-up
1. Reverse a list in place without using `reverse()` or slicing.
2. Return the second largest distinct value in a list in `O(n)`.
3. Rotate a list right by `k` positions in `O(n)` time.

## Core
4. **Two sum (unsorted).** Return indices of two numbers adding to a target in `O(n)`.
5. **Remove duplicates from a sorted list in place** and return the new length.
6. **Product of array except self** without using division, in `O(n)`.
7. **Longest substring without repeating characters.**
8. **Valid anagram** and **group anagrams**.
9. **Maximum subarray sum** (Kadane).
10. **Merge two sorted lists** into one sorted list in `O(n + m)`.

## Stretch
11. **Container with most water:** given heights, find two lines that hold the most water (two pointers).
12. **Subarray sum equals k** (prefix sums plus a dictionary).
13. **Longest palindromic substring** in `O(n²)` by expanding around centers.
14. **Spiral order** of a matrix.

<details>
<summary>Solutions</summary>

```python
# 1
def reverse_in_place(a):
    i, j = 0, len(a) - 1
    while i < j:
        a[i], a[j] = a[j], a[i]
        i, j = i + 1, j - 1

# 2
def second_largest(a):
    first = second = float("-inf")
    for x in a:
        if x > first:
            first, second = x, first
        elif first > x > second:
            second = x
    return None if second == float("-inf") else second

# 3 (three reversals)
def rotate_right(a, k):
    n = len(a)
    if n == 0:
        return
    k %= n
    def rev(i, j):
        while i < j:
            a[i], a[j] = a[j], a[i]
            i, j = i + 1, j - 1
    rev(0, n - 1); rev(0, k - 1); rev(k, n - 1)

# 4
def two_sum(nums, target):
    seen = {}
    for i, x in enumerate(nums):
        if target - x in seen:
            return (seen[target - x], i)
        seen[x] = i

# 5
def remove_duplicates(a):
    if not a:
        return 0
    write = 1
    for read in range(1, len(a)):
        if a[read] != a[write - 1]:
            a[write] = a[read]
            write += 1
    return write

# 6
def product_except_self(nums):
    n = len(nums)
    out = [1] * n
    left = 1
    for i in range(n):
        out[i] = left
        left *= nums[i]
    right = 1
    for i in range(n - 1, -1, -1):
        out[i] *= right
        right *= nums[i]
    return out

# 7
def longest_unique_substring(s):
    last, left, best = {}, 0, 0
    for right, ch in enumerate(s):
        if ch in last and last[ch] >= left:
            left = last[ch] + 1
        last[ch] = right
        best = max(best, right - left + 1)
    return best

# 8
from collections import Counter
def is_anagram(a, b):
    return Counter(a) == Counter(b)

def group_anagrams(words):
    g = {}
    for w in words:
        g.setdefault("".join(sorted(w)), []).append(w)
    return list(g.values())

# 9
def max_subarray(nums):
    best = cur = nums[0]
    for x in nums[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best

# 10
def merge_sorted(a, b):
    i = j = 0
    out = []
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out.append(a[i]); i += 1
        else:
            out.append(b[j]); j += 1
    out.extend(a[i:]); out.extend(b[j:])
    return out

# 11
def max_area(h):
    i, j, best = 0, len(h) - 1, 0
    while i < j:
        best = max(best, min(h[i], h[j]) * (j - i))
        if h[i] < h[j]:
            i += 1
        else:
            j -= 1
    return best

# 12
def subarray_sum(nums, k):
    count = total = 0
    seen = {0: 1}
    for x in nums:
        total += x
        count += seen.get(total - k, 0)
        seen[total] = seen.get(total, 0) + 1
    return count

# 13
def longest_palindrome(s):
    best = ""
    for c in range(len(s)):
        for l, r in ((c, c), (c, c + 1)):
            while l >= 0 and r < len(s) and s[l] == s[r]:
                l, r = l - 1, r + 1
            if r - l - 1 > len(best):
                best = s[l + 1:r]
    return best

# 14
def spiral(m):
    out = []
    while m:
        out += m.pop(0)
        m = [list(r) for r in zip(*m)][::-1]
    return out
```

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Arrays](01-arrays-and-memory.md) · [Working with Arrays](02-array-techniques.md) · [Strings in Depth](03-strings-in-depth.md)
