# Sorting: Exercises

## Problems
1. Implement **insertion sort**, **merge sort** and **quick sort** from scratch.
2. **Merge intervals:** merge all overlapping intervals.
3. **Sort colors** (0, 1, 2) in one pass with `O(1)` space.
4. Find the **k-th largest** element in average `O(n)`.
5. **Largest number:** arrange non-negative integers so their concatenation is largest.
6. **Meeting rooms:** can a person attend all meetings? What is the minimum number of rooms needed?
7. Count **inversions** in an array (pairs `i < j` with `a[i] > a[j]`) in `O(n log n)`.
8. Sort a list of people by department ascending, then salary descending, then name.
9. **Sort an array by frequency**; ties by smaller value first.
10. Check whether two strings are anagrams using **counting sort** (lowercase letters only).

<details>
<summary>Solutions</summary>

```python
import random
from collections import Counter
from functools import cmp_to_key

# 1
def insertion_sort(a):
    for i in range(1, len(a)):
        key, j = a[i], i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]; j -= 1
        a[j + 1] = key
    return a

def merge_sort(a):
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    l, r = merge_sort(a[:mid]), merge_sort(a[mid:])
    out, i, j = [], 0, 0
    while i < len(l) and j < len(r):
        if l[i] <= r[j]:
            out.append(l[i]); i += 1
        else:
            out.append(r[j]); j += 1
    return out + l[i:] + r[j:]

def partition(a, lo, hi):
    r = random.randint(lo, hi)
    a[r], a[hi] = a[hi], a[r]
    pivot, i = a[hi], lo
    for j in range(lo, hi):
        if a[j] < pivot:
            a[i], a[j] = a[j], a[i]; i += 1
    a[i], a[hi] = a[hi], a[i]
    return i

def quick_sort(a, lo=0, hi=None):
    if hi is None:
        hi = len(a) - 1
    if lo < hi:
        p = partition(a, lo, hi)
        quick_sort(a, lo, p - 1)
        quick_sort(a, p + 1, hi)
    return a

# 2
def merge_intervals(intervals):
    out = []
    for s, e in sorted(intervals):
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out

# 3
def sort_colors(a):
    lo, mid, hi = 0, 0, len(a) - 1
    while mid <= hi:
        if a[mid] == 0:
            a[lo], a[mid] = a[mid], a[lo]; lo += 1; mid += 1
        elif a[mid] == 1:
            mid += 1
        else:
            a[mid], a[hi] = a[hi], a[mid]; hi -= 1
    return a

# 4
def kth_largest(a, k):
    a = a[:]
    target = len(a) - k
    lo, hi = 0, len(a) - 1
    while True:
        p = partition(a, lo, hi)
        if p == target:
            return a[p]
        if p < target:
            lo = p + 1
        else:
            hi = p - 1

# 5
def largest_number(nums):
    strs = sorted(map(str, nums),
                  key=cmp_to_key(lambda x, y: -1 if x + y > y + x else 1))
    result = "".join(strs)
    return "0" if result[0] == "0" else result

# 6
def can_attend(meetings):
    meetings = sorted(meetings)
    return all(meetings[i][1] <= meetings[i + 1][0] for i in range(len(meetings) - 1))

def min_rooms(meetings):
    starts = sorted(s for s, _ in meetings)
    ends = sorted(e for _, e in meetings)
    rooms = best = j = 0
    for s in starts:
        while ends[j] <= s:
            j += 1; rooms -= 1
        rooms += 1
        best = max(best, rooms)
    return best

# 7
def count_inversions(a):
    def sort(arr):
        if len(arr) <= 1:
            return arr, 0
        mid = len(arr) // 2
        l, x = sort(arr[:mid])
        r, y = sort(arr[mid:])
        out, i, j, cross = [], 0, 0, 0
        while i < len(l) and j < len(r):
            if l[i] <= r[j]:
                out.append(l[i]); i += 1
            else:
                out.append(r[j]); j += 1
                cross += len(l) - i
        out += l[i:] + r[j:]
        return out, x + y + cross
    return sort(a)[1]

# 8
def sort_people(people):
    return sorted(people, key=lambda p: (p["dept"], -p["salary"], p["name"]))

# 9
def sort_by_frequency(nums):
    c = Counter(nums)
    return sorted(nums, key=lambda x: (c[x], x))

# 10
def is_anagram(a, b):
    if len(a) != len(b):
        return False
    counts = [0] * 26
    for x, y in zip(a, b):
        counts[ord(x) - 97] += 1
        counts[ord(y) - 97] -= 1
    return not any(counts)
```

</details>

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Sorting Basics and the Elementary Sorts](01-sorting-basics-and-elementary-sorts.md) · [Merge Sort and Quicksort](02-merge-sort-and-quicksort.md) · [Linear-Time Sorts, Timsort and Choosing a Sort](03-linear-time-sorts-and-timsort.md)
