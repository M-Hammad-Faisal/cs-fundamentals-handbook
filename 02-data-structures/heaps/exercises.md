# Heaps and Priority Queues: Exercises

These problems go with the [Heaps and Priority Queues lesson](README.md). Try each one before opening its solution.

## Problems

1. Return the **k-th largest element** in an unsorted list.
2. Return the **k most frequent** elements.
3. **Merge k sorted lists** into one sorted list.
4. Find the **k closest points** to the origin.
5. Implement a **running median** data structure (`add`, `median`).
6. **Last stone weight:** repeatedly smash the two heaviest stones; return what remains.
7. **Task scheduler (simplified):** given tasks with priorities, process them highest priority first, FIFO among equals.
8. Build a **min-heap from scratch** with `push` and `pop`.
9. Implement **heap sort**.
10. **Reorganize string:** rearrange characters so no two adjacent characters are equal, or return `""`.

<details>
<summary>Solutions</summary>

```python
import heapq, itertools
from collections import Counter

# 1
def kth_largest(nums, k):
    h = []
    for x in nums:
        heapq.heappush(h, x)
        if len(h) > k:
            heapq.heappop(h)
    return h[0]

# 2
def top_k_frequent(nums, k):
    return [x for x, _ in heapq.nlargest(k, Counter(nums).items(), key=lambda p: p[1])]

# 3
def merge_k_sorted(lists):
    h = [(lst[0], i, 0) for i, lst in enumerate(lists) if lst]
    heapq.heapify(h)
    out = []
    while h:
        val, i, j = heapq.heappop(h)
        out.append(val)
        if j + 1 < len(lists[i]):
            heapq.heappush(h, (lists[i][j + 1], i, j + 1))
    return out

# 4
def k_closest(points, k):
    return heapq.nsmallest(k, points, key=lambda p: p[0] ** 2 + p[1] ** 2)

# 5
class MedianFinder:
    def __init__(self):
        self.low, self.high = [], []        # low is a max-heap via negation
    def add(self, x):
        heapq.heappush(self.low, -x)
        heapq.heappush(self.high, -heapq.heappop(self.low))
        if len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))
    def median(self):
        if len(self.low) > len(self.high):
            return -self.low[0]
        return (-self.low[0] + self.high[0]) / 2

# 6
def last_stone_weight(stones):
    h = [-s for s in stones]
    heapq.heapify(h)
    while len(h) > 1:
        a, b = -heapq.heappop(h), -heapq.heappop(h)
        if a != b:
            heapq.heappush(h, -(a - b))
    return -h[0] if h else 0

# 7
class TaskQueue:
    def __init__(self):
        self.h, self.c = [], itertools.count()
    def add(self, priority, task):          # higher number = higher priority
        heapq.heappush(self.h, (-priority, next(self.c), task))
    def next(self):
        return heapq.heappop(self.h)[2]

# 8
class MinHeap:
    def __init__(self):
        self.a = []
    def push(self, x):
        self.a.append(x)
        i = len(self.a) - 1
        while i > 0 and self.a[(i - 1) // 2] > self.a[i]:
            p = (i - 1) // 2
            self.a[p], self.a[i] = self.a[i], self.a[p]
            i = p
    def pop(self):
        top, last = self.a[0], self.a.pop()
        if self.a:
            self.a[0] = last
            i, n = 0, len(self.a)
            while True:
                s = i
                for c in (2 * i + 1, 2 * i + 2):
                    if c < n and self.a[c] < self.a[s]:
                        s = c
                if s == i:
                    break
                self.a[i], self.a[s] = self.a[s], self.a[i]
                i = s
        return top

# 9
def heap_sort(a):
    def sift(a, i, n):
        while True:
            big, l, r = i, 2 * i + 1, 2 * i + 2
            if l < n and a[l] > a[big]: big = l
            if r < n and a[r] > a[big]: big = r
            if big == i:
                return
            a[i], a[big] = a[big], a[i]
            i = big
    n = len(a)
    for i in range(n // 2 - 1, -1, -1):
        sift(a, i, n)
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        sift(a, 0, end)
    return a

# 10
def reorganize_string(s):
    h = [(-c, ch) for ch, c in Counter(s).items()]
    heapq.heapify(h)
    out, prev = [], None
    while h:
        c, ch = heapq.heappop(h)
        out.append(ch)
        if prev:
            heapq.heappush(h, prev)
            prev = None
        if c + 1 < 0:
            prev = (c + 1, ch)
    return "".join(out) if len(out) == len(s) else ""
```

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Binary Heaps and Heapsort](01-binary-heaps-and-heapsort.md) · [Priority Queue Applications](02-priority-queue-applications.md)
