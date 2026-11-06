# Searching: Exercises

## Problems
1. Implement iterative **binary search** returning the index or `-1`.
2. Find the **first and last position** of a target in a sorted array with duplicates.
3. Return the index where a target **would be inserted** to keep the array sorted.
4. Compute the **integer square root** without `math.sqrt`.
5. **Search in a rotated sorted array** (no duplicates).
6. Find the **minimum in a rotated sorted array**.
7. Find a **peak element** (greater than its neighbours) in `O(log n)`.
8. **Koko eating bananas:** the minimum eating speed `k` to finish all piles within `h` hours.
9. **Split array largest sum:** split into `m` subarrays minimizing the largest subarray sum.
10. Search a sorted **2D matrix** (rows sorted, each row's first value greater than the previous row's last).
11. Find the **median of two sorted arrays** in `O(log(min(m, n)))` (stretch).

<details>
<summary>Solutions</summary>

```python
import bisect

# 1
def binary_search(a, target):
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if a[mid] == target: return mid
        if a[mid] < target: lo = mid + 1
        else: hi = mid - 1
    return -1

# 2
def search_range(a, target):
    lo = bisect.bisect_left(a, target)
    if lo == len(a) or a[lo] != target:
        return [-1, -1]
    return [lo, bisect.bisect_right(a, target) - 1]

# 3
def search_insert(a, target):
    return bisect.bisect_left(a, target)

# 4
def isqrt(n):
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if mid * mid <= n: lo = mid
        else: hi = mid - 1
    return lo

# 5
def search_rotated(a, target):
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if a[mid] == target:
            return mid
        if a[lo] <= a[mid]:
            if a[lo] <= target < a[mid]: hi = mid - 1
            else: lo = mid + 1
        else:
            if a[mid] < target <= a[hi]: lo = mid + 1
            else: hi = mid - 1
    return -1

# 6
def find_min_rotated(a):
    lo, hi = 0, len(a) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] > a[hi]: lo = mid + 1
        else: hi = mid
    return a[lo]

# 7
def find_peak(a):
    lo, hi = 0, len(a) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < a[mid + 1]: lo = mid + 1
        else: hi = mid
    return lo

# 8
def min_eating_speed(piles, h):
    lo, hi = 1, max(piles)
    while lo < hi:
        mid = (lo + hi) // 2
        if sum((p + mid - 1) // mid for p in piles) <= h:
            hi = mid
        else:
            lo = mid + 1
    return lo

# 9
def split_array(nums, m):
    def parts_needed(limit):
        parts, cur = 1, 0
        for x in nums:
            if cur + x > limit:
                parts, cur = parts + 1, 0
            cur += x
        return parts
    lo, hi = max(nums), sum(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if parts_needed(mid) <= m: hi = mid
        else: lo = mid + 1
    return lo

# 10
def search_matrix(matrix, target):
    if not matrix: return False
    m, n = len(matrix), len(matrix[0])
    lo, hi = 0, m * n - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        v = matrix[mid // n][mid % n]
        if v == target: return True
        if v < target: lo = mid + 1
        else: hi = mid - 1
    return False

# 11
def median_two_sorted(a, b):
    if len(a) > len(b):
        a, b = b, a
    m, n = len(a), len(b)
    lo, hi, half = 0, m, (m + n + 1) // 2
    while lo <= hi:
        i = (lo + hi) // 2
        j = half - i
        a_left = a[i - 1] if i > 0 else float("-inf")
        a_right = a[i] if i < m else float("inf")
        b_left = b[j - 1] if j > 0 else float("-inf")
        b_right = b[j] if j < n else float("inf")
        if a_left <= b_right and b_left <= a_right:
            if (m + n) % 2:
                return max(a_left, b_left)
            return (max(a_left, b_left) + min(a_right, b_right)) / 2
        if a_left > b_right: hi = i - 1
        else: lo = i + 1
```

</details>
