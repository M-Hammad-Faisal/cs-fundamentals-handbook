# Heaps and Priority Queues

## 1. The concept

A **heap** is a complete binary tree that satisfies the **heap property**:

- **Min-heap:** every parent is `<=` its children, so the smallest item is at the root.
- **Max-heap:** every parent is `>=` its children, so the largest item is at the root.

A heap is **not fully sorted**; it only guarantees that the root is the extreme value. That weaker guarantee is what makes it cheap to maintain.

A **priority queue** is the abstract idea ("always give me the highest-priority item next"). A heap is the standard way to implement it.

## 2. How it works

Because the tree is **complete** (every level full except possibly the last, filled left to right), it fits in a plain array with no pointers:

```
          1                index:  0  1  2  3  4  5  6
        /   \              value: [1, 3, 2, 7, 4, 5, 9]
       3     2
      / \   / \            parent(i)      = (i - 1) // 2
     7   4 5   9           left_child(i)  = 2 * i + 1
                           right_child(i) = 2 * i + 2
```

### Core operations

**Push (sift up):** append at the end, then swap upward while smaller than the parent. `O(log n)`.

**Pop (sift down):** swap the root with the last element, remove the last, then swap the new root downward with its smaller child until the property holds. `O(log n)`.

**Peek:** read index 0. `O(1)`.

**Heapify:** build a heap from an unordered array in `O(n)` (not `O(n log n)`) by sifting down from the last parent to the root.

```python
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
        if not self.a:
            raise IndexError("pop from empty heap")
        top = self.a[0]
        last = self.a.pop()
        if self.a:
            self.a[0] = last
            self._sift_down(0)
        return top

    def peek(self):
        return self.a[0]

    def _sift_down(self, i):
        n = len(self.a)
        while True:
            smallest = i
            for c in (2 * i + 1, 2 * i + 2):
                if c < n and self.a[c] < self.a[smallest]:
                    smallest = c
            if smallest == i:
                return
            self.a[i], self.a[smallest] = self.a[smallest], self.a[i]
            i = smallest

    def __len__(self):
        return len(self.a)
```

### Complexity

| Operation | Cost |
|-----------|------|
| Peek min/max | `O(1)` |
| Push | `O(log n)` |
| Pop | `O(log n)` |
| Build from array (heapify) | `O(n)` |
| Search arbitrary item | `O(n)` |
| Remove arbitrary item | `O(n)` (find) + `O(log n)` |

## 3. Python's `heapq`

`heapq` provides a **min-heap** on a plain list.

```python
import heapq

h = []
heapq.heappush(h, 5)
heapq.heappush(h, 1)
heapq.heappush(h, 3)
heapq.heappop(h)              # 1
h[0]                          # peek the smallest

heapq.heapify(nums)           # in place, O(n)
heapq.nsmallest(3, nums)      # 3 smallest
heapq.nlargest(3, nums)       # 3 largest
heapq.heappushpop(h, x)       # push then pop, faster than separate calls
```

### Max-heap trick

`heapq` is min-only. Push negated values for a max-heap:

```python
maxh = []
heapq.heappush(maxh, -value)
largest = -heapq.heappop(maxh)
```

### Priorities and tie-breaking

Store `(priority, counter, item)` tuples. The counter breaks ties so Python never tries to compare the items themselves (which may not be comparable).

```python
import itertools
tasks = []
counter = itertools.count()
heapq.heappush(tasks, (priority, next(counter), task))
```

## 4. Classic patterns

### Top K frequent / largest elements

Keep a **min-heap of size K**: for each item, push it, and if the heap grows beyond K, pop the smallest. At the end the heap holds the K largest. Cost `O(n log K)`, better than sorting when `K` is small.

```python
def k_largest(nums, k):
    h = []
    for x in nums:
        heapq.heappush(h, x)
        if len(h) > k:
            heapq.heappop(h)
    return sorted(h, reverse=True)
```

### Merge K sorted lists

```python
def merge_k_sorted(lists):
    h = [(lst[0], i, 0) for i, lst in enumerate(lists) if lst]
    heapq.heapify(h)
    out = []
    while h:
        val, i, j = heapq.heappop(h)
        out.append(val)
        if j + 1 < len(lists[i]):
            heapq.heappush(h, (lists[i][j + 1], i, j + 1))
    return out                     # O(N log K)
```

### Running median with two heaps

A max-heap holds the lower half and a min-heap holds the upper half. The median is at the top of one or the average of both tops.

```python
class MedianFinder:
    def __init__(self):
        self.low = []              # max-heap (negated)
        self.high = []             # min-heap

    def add(self, x):
        heapq.heappush(self.low, -x)
        heapq.heappush(self.high, -heapq.heappop(self.low))
        if len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))

    def median(self):
        if len(self.low) > len(self.high):
            return -self.low[0]
        return (-self.low[0] + self.high[0]) / 2
```

### Heap sort

Build a max-heap, then repeatedly swap the root to the end and sift down. `O(n log n)` time, `O(1)` extra space, not stable.

### Dijkstra's algorithm

A priority queue picks the closest unvisited node each step (see [graphs](../graphs/README.md)).

## 5. Two real-world examples

### Example 1: Task schedulers and job systems

An operating system or job queue must run the most urgent task next while new tasks keep arriving. A heap keyed by priority or deadline gives `O(log n)` insertion and `O(log n)` extraction of the next task. Linux's process schedulers, Celery priority queues, and timer wheels for "run this callback at time T" (Python's `asyncio` keeps scheduled callbacks in a heap) all use this.

### Example 2: "Top 10 trending" and shortest-path routing

A trending-topics service processes millions of events but only needs the top 10. A size-10 min-heap holds the current leaders in `O(n log 10)`, with memory independent of the stream length. Navigation apps run **Dijkstra** with a priority queue to find the fastest route, always expanding the closest unexplored intersection first. Event simulations and merge-sort of huge files (external merge of K sorted chunks) rely on the same structure.

## 6. Tips, tricks and pitfalls

- **Heap is not sorted.** Iterating `h` does not give sorted order. Pop repeatedly or use `sorted`.
- **Python has only a min-heap;** negate numbers for max-heap behavior.
- **Include a tie-breaker** in tuples to avoid comparing uncomparable objects.
- **Heapify is `O(n)`;** do not push `n` items one by one if you already have them all.
- **Top-K with a min-heap of size K,** not a max-heap of size `n`.
- **Updating a priority** is not supported directly. Use "lazy deletion": push the new entry and ignore stale ones when popped.
- **Use `heapq.merge`** to merge sorted iterables lazily.
- **Searching a heap is `O(n)`.** If you need lookups by key, pair the heap with a dict, or use a different structure.

## 7. Check yourself

1. What is the heap property, and how does a heap differ from a sorted array?
2. Why is a heap stored efficiently in an array, and what are the index formulas?
3. Why is `heapify` `O(n)` and not `O(n log n)`?
4. How do you get a max-heap in Python?
5. How do you find the K largest of `n` items in `O(n log K)`?
6. How do two heaps maintain a running median?
7. Why do tuples in a heap often include a counter?

<details>
<summary>Answers</summary>

1. Each parent is `<=` (min-heap) or `>=` (max-heap) its children, so only the root is guaranteed to be the extreme value. A sorted array is fully ordered; a heap is only partially ordered.
2. The tree is complete, so nodes fill the array level by level: parent `(i-1)//2`, children `2i+1` and `2i+2`.
3. Most nodes are near the bottom and sift down very few levels. The sum of work across levels converges to `O(n)`.
4. Push negated values (or wrap items in a class with reversed comparison).
5. Maintain a min-heap of size K; push each item and pop the smallest whenever size exceeds K.
6. A max-heap holds the smaller half and a min-heap the larger half, sizes kept within one. The median is a top or the average of the two tops.
7. To break ties between equal priorities so Python never has to compare the underlying objects, and to keep FIFO order among equals.

</details>
