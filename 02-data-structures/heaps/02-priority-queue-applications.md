# Priority Queue Applications

**Prerequisites:** [binary heaps](01-binary-heaps-and-heapsort.md). **You will learn:** the patterns where heaps shine: **top-k**, the **running median** (two heaps), **merging k sorted lists**, **meeting rooms**, **task scheduling**, **Dijkstra's shortest path** and **Huffman coding**.

## 1. Pattern 1: top-k with a small heap

To find the `k` largest of `n` items you do not need to sort everything (`O(n log n)`). Keep a **min-heap of size k**: the root is the smallest of the current top-k, so any new item bigger than the root replaces it. Cost: `O(n log k)`, memory `O(k)`, and it works on **streams** too big for memory.

```python
import heapq

def top_k(stream, k):
    heap = []
    for x in stream:
        if len(heap) < k:
            heapq.heappush(heap, x)
        elif x > heap[0]:
            heapq.heapreplace(heap, x)               # pop the smallest and push x in one step
    return sorted(heap, reverse=True)

print(top_k([4, 9, 1, 7, 3, 8, 2, 6], 3))            # [9, 8, 7]

def top_k_frequent(words, k):
    from collections import Counter
    counts = Counter(words)
    return heapq.nlargest(k, counts, key=counts.get)

print(top_k_frequent("the cat and the dog and the bird".split(), 2))      # ['the', 'and']
```

(`heapq.nlargest(k, data)` does the same thing for you.)

## 2. Pattern 2: the running median with two heaps

Keep the **lower half** in a max-heap and the **upper half** in a min-heap. The median is at the top of one (or the average of both tops). Balance them so their sizes differ by at most 1.

```text
lower half (max-heap)   upper half (min-heap)
   [1, 2, 3]  top 3        [5, 8, 9]  top 5      median = (3 + 5) / 2 = 4
```

```python
class RunningMedian:
    def __init__(self):
        self.low = []        # max-heap (store negatives)
        self.high = []       # min-heap

    def add(self, x):
        heapq.heappush(self.low, -x)
        heapq.heappush(self.high, -heapq.heappop(self.low))     # move the largest of "low" to "high"
        if len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high)) # keep low the same size or one bigger

    def median(self):
        if len(self.low) > len(self.high):
            return -self.low[0]
        return (-self.low[0] + self.high[0]) / 2

rm = RunningMedian()
for x in [5, 15, 1, 3, 8, 7]:
    rm.add(x)
    print(rm.median(), end=" ")                          # 5 10.0 5 4.0 5 6.0
print()
```

Add is `O(log n)`, median `O(1)`. (Sorting every time would be `O(n log n)` per query.)

## 3. Pattern 3: merging k sorted lists

Put the first element of every list in a heap (tagged with where it came from); repeatedly pop the smallest and push the next element from the same list. Total `O(N log k)` for `N` elements.

```python
def merge_k_sorted(lists):
    heap = [(lst[0], i, 0) for i, lst in enumerate(lists) if lst]
    heapq.heapify(heap)
    merged = []
    while heap:
        value, which, pos = heapq.heappop(heap)
        merged.append(value)
        if pos + 1 < len(lists[which]):
            heapq.heappush(heap, (lists[which][pos + 1], which, pos + 1))
    return merged

print(merge_k_sorted([[1, 4, 7], [2, 5, 8], [0, 3, 6, 9]]))      # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
print(list(heapq.merge([1, 4], [2, 3], [0])))                    # [0, 1, 2, 3, 4]   (the standard-library version)
```

This is the merge step of **external sorting** (sorting files bigger than RAM) and of database LSM trees.

## 4. Pattern 4: sweeping events (meeting rooms)

How many rooms are needed for meetings `(start, end)`? Sort by start; keep a min-heap of **end times** of rooms in use. If the earliest-ending room is free before the next meeting starts, reuse it.

```python
def min_meeting_rooms(meetings):
    rooms = []                                       # heap of end times
    for start, end in sorted(meetings):
        if rooms and rooms[0] <= start:
            heapq.heapreplace(rooms, end)            # reuse the room that frees up first
        else:
            heapq.heappush(rooms, end)               # need a new room
    return len(rooms)

print(min_meeting_rooms([(0, 30), (5, 10), (15, 20)]))           # 2
print(min_meeting_rooms([(7, 10), (2, 4)]))                      # 1
```

## 5. Pattern 5: scheduling with priorities and a tie-breaker

Tuples compare element by element, so equal priorities fall through to the next element, which may not be comparable. Add an increasing **counter** to keep first-in-first-out among equals.

```python
import itertools

class TaskScheduler:
    def __init__(self):
        self._heap, self._counter = [], itertools.count()

    def add(self, priority, task):
        heapq.heappush(self._heap, (priority, next(self._counter), task))

    def next_task(self):
        return heapq.heappop(self._heap)[2]

s = TaskScheduler()
s.add(2, {"name": "report"}); s.add(1, {"name": "outage"}); s.add(2, {"name": "email"})
print([s.next_task()["name"] for _ in range(3)])                 # ['outage', 'report', 'email']
```

## 6. Pattern 6: Dijkstra's shortest path

Find the cheapest route from a start node to every other node in a graph with **non-negative edge weights**. Greedy idea: always settle the closest unsettled node next, which is exactly what a min-heap hands you. (More in [graphs](../graphs/README.md).)

```python
def dijkstra(graph, start):
    dist = {start: 0}
    heap = [(0, start)]
    while heap:
        d, node = heapq.heappop(heap)
        if d > dist.get(node, float("inf")):
            continue                                  # stale entry: a better route was already found
        for neighbor, weight in graph[node]:
            new_d = d + weight
            if new_d < dist.get(neighbor, float("inf")):
                dist[neighbor] = new_d
                heapq.heappush(heap, (new_d, neighbor))
    return dist

roads = {
    "A": [("B", 4), ("C", 1)],
    "B": [("D", 1)],
    "C": [("B", 2), ("D", 5)],
    "D": [],
}
print(dijkstra(roads, "A"))                           # {'A': 0, 'B': 3, 'C': 1, 'D': 4}
```

Trace: from A, C costs 1 and B costs 4. Pop C (1): B improves to 3, D is 6. Pop B (3): D improves to 4. Result: A to D costs 4 via A-C-B-D. Time `O((V + E) log V)`. Heaps do not support "decrease key", so we push duplicates and skip stale ones (**lazy deletion**).

## 7. Pattern 7: Huffman coding (compression)

Give frequent symbols short bit codes and rare ones long codes. Repeatedly merge the **two least frequent** nodes into one; the resulting tree gives each symbol a code (left = 0, right = 1).

```python
import itertools
from collections import Counter

def huffman_codes(text):
    counter = itertools.count()
    heap = [(freq, next(counter), symbol) for symbol, freq in Counter(text).items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        f1, _, left = heapq.heappop(heap)
        f2, _, right = heapq.heappop(heap)
        heapq.heappush(heap, (f1 + f2, next(counter), (left, right)))     # merged node
    codes = {}
    def walk(node, prefix):
        if isinstance(node, tuple):
            walk(node[0], prefix + "0"); walk(node[1], prefix + "1")
        else:
            codes[node] = prefix or "0"
    walk(heap[0][2], "")
    return codes

text = "abracadabra"
codes = huffman_codes(text)
encoded = "".join(codes[ch] for ch in text)
print(sorted(codes.items(), key=lambda kv: (len(kv[1]), kv[0])))
print(len(encoded), "bits instead of", 8 * len(text))
# [('a', '0'), ('b', '110'), ('c', '100'), ('d', '101'), ('r', '111')]
# 23 bits instead of 88
```

ZIP, PNG and JPEG all use Huffman-style coding as one of their steps.

## 8. Two real-world examples

**Example 1: Leaderboards and trending lists.** "Top 10 searches this hour" over a firehose of events is the top-k pattern: a size-10 heap and almost no memory.

**Example 2: Navigation.** Maps compute routes with Dijkstra (or A*, which adds a heuristic to the same heap loop).

## 9. Common mistakes

- Using a max-heap for "k largest" (you want a **min**-heap of size `k`).
- Forgetting the tie-breaker counter when priorities can be equal.
- Expecting `decrease-key`: use lazy deletion by pushing duplicates.
- Letting the heap grow unbounded in a stream (cap it at `k`).
- Using Dijkstra with **negative** weights (it can give wrong answers; use Bellman-Ford).
- Using a heap when a plain `sorted()` once would be simpler.

## 10. Practice

1. Find the 3rd largest number in `[3, 2, 1, 5, 6, 4]` using a heap of size 3.
2. Keep the running median of `[2, 3, 4]` and write the three medians.
3. Merge `[[1, 5], [2, 3], [4]]`.
4. How many rooms for `[(1, 5), (2, 6), (7, 9)]`?
5. Why does Dijkstra fail with negative edges?
6. Write `k_closest_points(points, k)` returning the `k` points nearest the origin.

<details>
<summary>Solutions</summary>

1. ```python
   print(top_k([3, 2, 1, 5, 6, 4], 3)[-1])                  # 4
   ```
2. `2`, `2.5`, `3`.
3. `[1, 2, 3, 4, 5]`.
4. 2 (the first two overlap; the third can reuse a room).
5. It assumes a settled node can never be improved later; a negative edge could make a longer path cheaper afterwards.
6. ```python
   def k_closest_points(points, k):
       return heapq.nsmallest(k, points, key=lambda p: p[0] ** 2 + p[1] ** 2)
   print(k_closest_points([(1, 3), (-2, 2), (5, 8), (0, 1)], 2))      # [(0, 1), (-2, 2)]
   ```

</details>

## 11. Check yourself

1. Why is a *min*-heap used to keep the *largest* k items?
2. How do two heaps give a running median?
3. What is the cost of merging `k` sorted lists totaling `N` items?
4. Why add a counter to heap entries?
5. What is lazy deletion?

<details>
<summary>Answers</summary>

1. Its root is the smallest of the kept items, which is the first candidate to be kicked out.
2. A max-heap holds the lower half and a min-heap the upper half; the median sits at the tops.
3. `O(N log k)`.
4. To break priority ties without comparing the (possibly uncomparable) payloads and to keep first-in-first-out order.
5. Instead of updating an entry, push a new one and ignore outdated ones when popped.

</details>

[Back to heaps](README.md) · Previous: [binary heaps and heapsort](01-binary-heaps-and-heapsort.md)
