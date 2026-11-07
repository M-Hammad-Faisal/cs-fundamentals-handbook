# Binary Heaps and Heapsort

**Prerequisites:** [binary trees](../trees/01-binary-trees-and-traversals.md) (especially the array layout), [queues and priority queues](../stacks-queues/02-queues-deques-priority-queues.md). **You will learn:** what a heap is, how **sift-up** and **sift-down** work step by step, why `heapify` is `O(n)`, how to build a heap yourself, and **heapsort**.

## 1. In plain words

A hospital emergency room does not serve patients first-come-first-served; it serves the **most urgent** next. A **priority queue** does that, and a **heap** is the standard way to build one: finding the most urgent item is `O(1)`, and adding or removing is `O(log n)`.

A **min-heap** obeys one rule:

> Every parent is **less than or equal to** both its children.

(A **max-heap** flips it.) The smallest item is therefore always at the **root**. Unlike a BST, siblings are *not* ordered and the whole thing is not sorted; the heap keeps just enough order to find the minimum fast.

```text
          2                 array:  [2, 5, 3, 9, 6, 4]
        /   \                index:   0  1  2  3  4  5
       5     3
      / \   /               children of i:  2i+1 and 2i+2
     9   6 4                parent of i:    (i-1)//2
```

A heap is a **complete** binary tree (every level full except possibly the last, filled left to right), so it fits in a plain list with no pointers.

## 2. The two repair moves

**Push (sift-up):** put the new item at the end (the next free spot), then swap it with its parent while it is smaller.

```text
push 1 into [2, 5, 3, 9, 6, 4]
 [2, 5, 3, 9, 6, 4, 1]     1 at index 6, parent index 2 (value 3): 1 < 3, swap
 [2, 5, 1, 9, 6, 4, 3]     now parent index 0 (value 2): 1 < 2, swap
 [1, 5, 2, 9, 6, 4, 3]     reached the root: done
```

**Pop (sift-down):** remove the root (the minimum). Move the **last** item to the root to keep the tree complete, then swap it with its **smaller child** while it is larger than a child.

```text
pop from [1, 5, 2, 9, 6, 4, 3]
 take 1 out, move last (3) to root:  [3, 5, 2, 9, 6, 4]
 children of 3 are 5 and 2; smaller is 2 < 3, swap:  [2, 5, 3, 9, 6, 4]
 children of 3 (index 2) are 4 only (index 5): 3 < 4, stop
```

Each move follows one path of length at most the height, about `log₂ n`: **`O(log n)`**.

## 3. Implementation

```python
class MinHeap:
    def __init__(self, items=()):
        self.data = list(items)
        for i in range(len(self.data) // 2 - 1, -1, -1):      # heapify: sift down every non-leaf, bottom up
            self._sift_down(i)

    def __len__(self):
        return len(self.data)

    def peek(self):
        return self.data[0]                                   # O(1): the minimum is always at the root

    def push(self, item):
        self.data.append(item)
        self._sift_up(len(self.data) - 1)

    def pop(self):
        data = self.data
        data[0], data[-1] = data[-1], data[0]                 # move the minimum to the end ...
        smallest = data.pop()                                 # ... and remove it
        if data:
            self._sift_down(0)
        return smallest

    def _sift_up(self, i):
        data = self.data
        while i > 0:
            parent = (i - 1) // 2
            if data[i] >= data[parent]:
                break
            data[i], data[parent] = data[parent], data[i]
            i = parent

    def _sift_down(self, i):
        data, n = self.data, len(self.data)
        while True:
            left, right, smallest = 2 * i + 1, 2 * i + 2, i
            if left < n and data[left] < data[smallest]:
                smallest = left
            if right < n and data[right] < data[smallest]:
                smallest = right
            if smallest == i:
                return
            data[i], data[smallest] = data[smallest], data[i]
            i = smallest

h = MinHeap([2, 5, 3, 9, 6, 4])
h.push(1)
print(h.data, h.peek())                                       # [1, 5, 2, 9, 6, 4, 3] 1
print(h.pop(), h.data)                                        # 1 [2, 5, 3, 9, 6, 4]
print([h.pop() for _ in range(len(h))])                       # [2, 3, 4, 5, 6, 9]   (popping everything gives sorted order)
```

## 4. Why heapify is `O(n)`, not `O(n log n)`

Building a heap by pushing `n` items one by one costs `O(n log n)`. **Heapify** is smarter: start at the last non-leaf and sift each node *down*. Half the nodes are leaves (cost 0), a quarter can sink at most 1 level, an eighth at most 2... the total is `n/4·1 + n/8·2 + n/16·3 + ... < n`. So **`O(n)`**.

```python
import random

def count_swaps_heapify(values):
    data, swaps = list(values), 0
    n = len(data)
    for start in range(n // 2 - 1, -1, -1):
        i = start
        while True:
            left, right, smallest = 2 * i + 1, 2 * i + 2, i
            if left < n and data[left] < data[smallest]: smallest = left
            if right < n and data[right] < data[smallest]: smallest = right
            if smallest == i: break
            data[i], data[smallest] = data[smallest], data[i]; swaps += 1; i = smallest
    return swaps

random.seed(2)
for n in (1_000, 10_000, 100_000):
    sample = random.sample(range(n * 10), n)
    print(n, count_swaps_heapify(sample) / n)       # 1000 0.733 / 10000 0.7445 / 100000 0.74254: about 0.74 swaps per element however large n gets
```

## 5. Python's `heapq`

Python ships a fast min-heap on top of a plain list.

```python
import heapq

nums = [5, 1, 8, 3, 2]
heapq.heapify(nums)                       # O(n), in place
heapq.heappush(nums, 0)
print(heapq.heappop(nums), nums[0])       # 0 1
print(heapq.nsmallest(2, [7, 3, 9, 1]), heapq.nlargest(2, [7, 3, 9, 1]))     # [1, 3] [9, 7]

# there is no max-heap: store negated values
maxheap = []
for x in [4, 9, 2]:
    heapq.heappush(maxheap, -x)
print(-heapq.heappop(maxheap))            # 9

# items with priorities: tuples compare element by element
tasks = []
heapq.heappush(tasks, (2, "write report"))
heapq.heappush(tasks, (1, "fix outage"))
print(heapq.heappop(tasks))               # (1, 'fix outage')
```

Check that your own heap is as correct as `heapq`:

```python
random.seed(9)
values = [random.randint(0, 100) for _ in range(500)]
mine, theirs = MinHeap(values), values[:]
heapq.heapify(theirs)
print([mine.pop() for _ in range(500)] == [heapq.heappop(theirs) for _ in range(500)])      # True
```

## 6. Heapsort

Idea: put everything in a heap, then repeatedly take the minimum. The in-place version uses a **max-heap**, swapping the biggest to the end of the array and shrinking the heap by one.

```python
def heapsort(arr):
    n = len(arr)

    def sift_down_max(i, size):
        while True:
            left, right, largest = 2 * i + 1, 2 * i + 2, i
            if left < size and arr[left] > arr[largest]: largest = left
            if right < size and arr[right] > arr[largest]: largest = right
            if largest == i: return
            arr[i], arr[largest] = arr[largest], arr[i]
            i = largest

    for i in range(n // 2 - 1, -1, -1):          # phase 1: build a max-heap in O(n)
        sift_down_max(i, n)
    for end in range(n - 1, 0, -1):              # phase 2: move the max to the end, repair the rest
        arr[0], arr[end] = arr[end], arr[0]
        sift_down_max(0, end)
    return arr

print(heapsort([5, 2, 9, 1, 5, 6]))              # [1, 2, 5, 5, 6, 9]
print(heapsort([]), heapsort([1]))               # [] [1]
data = random.sample(range(1000), 300)
print(heapsort(data[:]) == sorted(data))         # True
```

| Property | Heapsort |
|----------|----------|
| Time | `O(n log n)` in **every** case |
| Extra space | `O(1)` (in place) |
| Stable? | **No** |
| In practice | slower than quicksort/timsort (poor cache behavior), but a safe worst-case guarantee |

## 7. Heap versus the alternatives

| Structure | Peek min | Push | Pop min | Search arbitrary |
|-----------|----------|------|---------|------------------|
| Unsorted list | `O(n)` | `O(1)` | `O(n)` | `O(n)` |
| Sorted list | `O(1)` | `O(n)` | `O(1)` (from the right end) or `O(n)` | `O(log n)` |
| **Binary heap** | **`O(1)`** | **`O(log n)`** | **`O(log n)`** | `O(n)` |
| Balanced BST | `O(log n)` | `O(log n)` | `O(log n)` | `O(log n)` |

A heap is the right tool when you only ever need the **extreme** item.

## 8. Two real-world examples

**Example 1: Operating-system schedulers.** The scheduler must repeatedly pick the runnable process with the best priority or the earliest deadline: a heap gives the next process in `O(log n)` even with thousands of processes.

**Example 2: Timers and event simulation.** Game engines and network simulators keep upcoming events in a min-heap keyed by time; pop the earliest, run it, push new events it creates.

## 9. Common mistakes

- Thinking a heap is sorted (only the root is guaranteed).
- Using `heapq` with a max-heap expectation (it is min only; negate values).
- Pushing items that cannot be compared (`(1, {})` vs `(1, {})` raises `TypeError`); add a tie-breaking counter.
- Indexing from 1 versus 0: with 0-based arrays the children of `i` are `2i+1`, `2i+2`.
- Sifting down against the *larger* child in a min-heap.
- Mutating a priority in place (the heap does not notice).

## 10. Practice

1. Is `[1, 3, 2, 7, 4, 5]` a valid min-heap? What about `[1, 3, 2, 7, 2, 5]`?
2. Insert 4, 7, 1, 3 one by one into an empty min-heap and write the array after each push.
3. Pop twice from `[1, 3, 2, 7, 4, 5]` and write the array after each pop.
4. What is the index of the parent of index 9? The children of index 4?
5. Write `is_min_heap(arr)`.
6. Implement `MinHeap.replace(item)` that pops the minimum and pushes `item` in one sift.

<details>
<summary>Solutions</summary>

1. First: yes. Second: no, because index 4 holds 2, which is smaller than its parent at index 1 (value 3).
2. `[4]`, then `[4, 7]`, then push 1: `[1, 7, 4]`, then push 3: `[1, 3, 4, 7]`.
3. First pop: move 5 to root: `[5, 3, 2, 7, 4]` then sift: `[2, 3, 5, 7, 4]`. Second pop: move 4 to root: `[4, 3, 5, 7]` then sift: `[3, 4, 5, 7]`.
4. Parent `(9-1)//2 = 4`; children of 4: `9` and `10`.
5. ```python
   def is_min_heap(arr):
       return all(arr[(i - 1) // 2] <= arr[i] for i in range(1, len(arr)))
   print(is_min_heap([1, 3, 2, 7, 4, 5]), is_min_heap([1, 3, 2, 7, 2, 5]))      # True False
   ```
6. ```python
   def replace(self, item):
       smallest = self.data[0]
       self.data[0] = item
       self._sift_down(0)
       return smallest
   MinHeap.replace = replace
   h2 = MinHeap([1, 3, 2]); print(h2.replace(10), h2.data)                      # 1 [2, 3, 10]
   ```

</details>

## 11. Check yourself

1. State the min-heap rule.
2. Why can a heap live in an array?
3. What do sift-up and sift-down do, and when is each used?
4. Why is heapify `O(n)`?
5. What are heapsort's time, space and stability?

<details>
<summary>Answers</summary>

1. Every parent is less than or equal to its children.
2. It is a complete tree, so positions follow a fixed formula (`2i+1`, `2i+2`, `(i-1)//2`).
3. Sift-up repairs after a push (new item at the end); sift-down repairs after a pop (last item placed at the root).
4. Most nodes are near the bottom and sink only a short way: the sum converges to about `n`.
5. `O(n log n)` always, `O(1)` extra space, not stable.

</details>

[Back to heaps](README.md) · Next: [priority queue applications](02-priority-queue-applications.md)
