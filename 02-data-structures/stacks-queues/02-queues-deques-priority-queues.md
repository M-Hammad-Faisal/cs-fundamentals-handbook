# Queues, Deques and Priority Queues

**Prerequisites:** [stacks](01-stacks.md), [linked lists](../linked-lists/02-doubly-and-circular.md), [amortized analysis](../../01-complexity/06-cases-and-amortized-analysis.md). **You will learn:** the FIFO queue and why a plain list is a poor queue, how to implement queues with a circular buffer and with linked nodes, Python's `deque` and `queue` module, double-ended queues, **priority queues** (with `heapq`), and the producer-consumer pattern.

## 1. In plain words

A **queue** is a line of people. **First In, First Out (FIFO)**: the person who joined first is served first. Items join at the **back** (**enqueue**) and leave from the **front** (**dequeue**).

```text
 enqueue ─►  back                          front  ─► dequeue
            ┌─────┬─────┬─────┬─────┐
            │  D  │  C  │  B  │  A  │       A joined first, so A leaves first
            └─────┴─────┴─────┴─────┘
```

Queues are fair and ordered: print jobs, customer tickets, web requests, messages, tasks waiting for a worker, breadth-first search.

| Operation | Meaning | Target cost |
|-----------|---------|-------------|
| `enqueue(x)` / `put` | add to the back | `O(1)` |
| `dequeue()` / `get` | remove from the front | `O(1)` |
| `peek()` / `front` | look at the front item | `O(1)` |
| `is_empty()`, `len` | | `O(1)` |

## 2. Why a plain list makes a bad queue

`list.append(x)` is `O(1)`, but `list.pop(0)` shifts every remaining item (`O(n)`), so a queue of `n` items costs `O(n²)` overall:

```python
import time
from collections import deque

def drain_list(n):
    q = list(range(n))
    while q:
        q.pop(0)                                    # O(n) each: shifts all the rest

def drain_deque(n):
    q = deque(range(n))
    while q:
        q.popleft()                                 # O(1) each

n = 40_000
t = time.perf_counter(); drain_list(n); slow = time.perf_counter() - t
t = time.perf_counter(); drain_deque(n); fast = time.perf_counter() - t
print(slow > fast * 5)                              # True: quadratic versus linear
```

## 3. Implementation 1: a linked-list queue

Keep a `head` (front) and `tail` (back) pointer: enqueue at the tail, dequeue at the head: both `O(1)`.

```python
class LinkedQueue:
    class _Node:
        __slots__ = ("value", "next")
        def __init__(self, value):
            self.value, self.next = value, None

    def __init__(self):
        self._head = self._tail = None
        self._size = 0

    def enqueue(self, value):                       # O(1)
        node = self._Node(value)
        if self._tail:
            self._tail.next = node
        else:
            self._head = node                       # first item: head and tail are the same node
        self._tail = node
        self._size += 1

    def dequeue(self):                              # O(1)
        if not self._head:
            raise IndexError("dequeue from empty queue")
        node = self._head
        self._head = node.next
        if not self._head:
            self._tail = None                       # the queue became empty
        self._size -= 1
        return node.value

    def peek(self):
        if not self._head:
            raise IndexError("peek at empty queue")
        return self._head.value

    def __len__(self):
        return self._size

q = LinkedQueue()
for name in ("Ana", "Bo", "Cy"):
    q.enqueue(name)
print(q.peek(), q.dequeue(), q.dequeue(), len(q))   # Ana Ana Bo 1
q.enqueue("Di")
print(q.dequeue(), q.dequeue(), len(q))             # Cy Di 0
```

## 4. Implementation 2: a circular buffer (ring buffer)

A fixed-size array where the front and back indexes **wrap around** with modulo. No shifting and no pointers: great for bounded buffers (audio, network packets, logs of the last N events).

```text
 capacity 5, array indexes 0..4          front moves right as items are removed, back moves right as items are added
  [ . . C D E ]   front=2, size=3        enqueue(F): back wraps:  [ F . C D E ]   (index (2+3) % 5 = 0)
```

```python
class RingBufferQueue:
    def __init__(self, capacity):
        self._data = [None] * capacity
        self._front = 0
        self._size = 0

    def enqueue(self, value):                       # O(1)
        if self._size == len(self._data):
            raise OverflowError("queue is full")
        back = (self._front + self._size) % len(self._data)       # wrap around with modulo
        self._data[back] = value
        self._size += 1

    def dequeue(self):                              # O(1)
        if self._size == 0:
            raise IndexError("queue is empty")
        value = self._data[self._front]
        self._data[self._front] = None
        self._front = (self._front + 1) % len(self._data)
        self._size -= 1
        return value

    def __len__(self):
        return self._size

    def contents(self):
        return [self._data[(self._front + i) % len(self._data)] for i in range(self._size)]

rb = RingBufferQueue(4)
for x in "abcd":
    rb.enqueue(x)
print(rb.contents(), rb.dequeue(), rb.dequeue())    # ['a', 'b', 'c', 'd'] a b
rb.enqueue("e"); rb.enqueue("f")                    # these wrap around to the start of the array
print(rb.contents(), rb._data)                      # ['c', 'd', 'e', 'f'] ['e', 'f', 'c', 'd']
try:
    rb.enqueue("g")
except OverflowError as error:
    print("OverflowError:", error)                  # OverflowError: queue is full
```

A **bounded** queue gives natural **back-pressure**: when full, producers must wait or drop items.

## 5. Python's built-in queues

### `collections.deque`: the everyday queue

```python
from collections import deque

q = deque()
q.append("a"); q.append("b"); q.append("c")        # enqueue at the right
print(q.popleft(), q, len(q))                       # a deque(['b', 'c']) 2     (dequeue at the left)
q.appendleft("z")                                   # also works at the other end
print(q)                                            # deque(['z', 'b', 'c'])
print(q.pop(), q)                                   # c deque(['z', 'b'])      (pop() removes from the right end)
recent = deque(maxlen=3)                            # a bounded deque keeps only the newest 3 items
for x in range(6):
    recent.append(x)
print(list(recent))                                 # [3, 4, 5]
```

### The thread-safe `queue.Queue` (for producer-consumer programs)

```python
import queue, threading

jobs = queue.Queue(maxsize=3)                       # a bounded, thread-safe FIFO queue
results = []

def producer():
    for i in range(6):
        jobs.put(i)                                 # blocks when the queue is full: back-pressure
    jobs.put(None)                                  # a sentinel meaning "no more work"

def consumer():
    while (item := jobs.get()) is not None:         # blocks when empty
        results.append(item * item)
        jobs.task_done()

t1, t2 = threading.Thread(target=producer), threading.Thread(target=consumer)
t1.start(); t2.start(); t1.join(); t2.join()
print(results)                                      # [0, 1, 4, 9, 16, 25]   (processed in the order produced: FIFO)
```

`queue.Queue` handles the locking for you ([concurrency](../../06-operating-systems/concurrency-deadlocks/README.md)); `asyncio.Queue` is the async counterpart ([async](../../08-modern-python/async-concurrency/README.md)).

## 6. Deques: double-ended queues

A **deque** ("deck") allows adding and removing at **both ends** in `O(1)`. It can act as a stack, a queue or both.

| Operation | Meaning | Cost |
|-----------|---------|------|
| `append(x)` / `appendleft(x)` | add at the right / left | `O(1)` |
| `pop()` / `popleft()` | remove from the right / left | `O(1)` |
| `d[0]`, `d[-1]` | peek at the ends | `O(1)` |
| `d[i]` (middle) | index | `O(n)` |
| `rotate(k)` | rotate right by k | `O(k)` |

CPython implements `deque` as a doubly linked list of **blocks** (small arrays): fast at the ends and cache friendlier than one node per item. Uses: BFS, sliding windows, undo with a size limit, palindromes (compare both ends), work-stealing schedulers.

```python
def is_palindrome_deque(text):
    d = deque(c.lower() for c in text if c.isalnum())
    while len(d) > 1:
        if d.popleft() != d.pop():                   # compare the two ends
            return False
    return True
print(is_palindrome_deque("Never odd or even"), is_palindrome_deque("queue"))      # True False

d = deque([1, 2, 3, 4, 5])
d.rotate(2)
print(list(d))                                       # [4, 5, 1, 2, 3]
```

## 7. Priority queues: the most important item leaves first

A **priority queue** serves the item with the **highest priority** (or lowest number) first, regardless of arrival order: an emergency room, not a deli counter.

| Implementation | enqueue | dequeue-min | Notes |
|----------------|---------|-------------|-------|
| Unsorted list | `O(1)` | `O(n)` (scan for the min) | simple |
| Sorted list | `O(n)` (insert in place) | `O(1)` | |
| **Binary heap** | **`O(log n)`** | **`O(log n)`** | the standard choice ([heaps](../heaps/README.md)) |

Python provides a binary min-heap in `heapq`:

```python
import heapq

pq = []
heapq.heappush(pq, (2, "write report"))              # tuples compare by priority first
heapq.heappush(pq, (1, "fix outage"))
heapq.heappush(pq, (3, "water plants"))
heapq.heappush(pq, (1, "call customer"))
order = []
while pq:
    priority, task = heapq.heappop(pq)               # smallest priority number first
    order.append((priority, task))
print(order)
# [(1, 'call customer'), (1, 'fix outage'), (2, 'write report'), (3, 'water plants')]
```

Notes: items with equal priority compare their next element (here the strings, so ties are alphabetical, not FIFO). For stable FIFO among equals add a counter: `(priority, counter, task)`. For a **max**-heap, push negated priorities. `queue.PriorityQueue` is the thread-safe version.

```python
import itertools

class TaskQueue:
    """A priority queue that is first-come-first-served among equal priorities."""
    def __init__(self):
        self._heap, self._counter = [], itertools.count()
    def add(self, task, priority=0):
        heapq.heappush(self._heap, (priority, next(self._counter), task))
    def next(self):
        return heapq.heappop(self._heap)[2]
    def __len__(self):
        return len(self._heap)

tasks = TaskQueue()
tasks.add("email", 2); tasks.add("deploy", 1); tasks.add("backup", 2); tasks.add("hotfix", 0)
print([tasks.next() for _ in range(len(tasks))])     # ['hotfix', 'deploy', 'email', 'backup']
```

## 8. Two queues from one structure: a queue from two stacks

```python
class QueueFromStacks:
    """Amortized O(1): items move from `inbox` to `outbox` only when the outbox is empty."""
    def __init__(self):
        self.inbox, self.outbox = [], []
    def enqueue(self, x):
        self.inbox.append(x)
    def dequeue(self):
        if not self.outbox:
            while self.inbox:
                self.outbox.append(self.inbox.pop())    # reversing a stack turns LIFO into FIFO
        return self.outbox.pop()

qs = QueueFromStacks()
for x in (1, 2, 3):
    qs.enqueue(x)
print(qs.dequeue(), qs.dequeue(), qs.dequeue())         # 1 2 3
```

## 9. Queues in algorithms: breadth-first search

BFS explores a graph **level by level** using a queue, and so finds the **shortest path in an unweighted graph**.

```python
from collections import deque

def bfs_shortest_path(graph, start, goal):
    queue = deque([[start]])                              # a queue of paths
    seen = {start}
    while queue:
        path = queue.popleft()                            # FIFO: the oldest, shortest paths first
        node = path[-1]
        if node == goal:
            return path
        for neighbor in graph[node]:
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(path + [neighbor])
    return None

graph = {"A": ["B", "C"], "B": ["D"], "C": ["D", "E"], "D": ["F"], "E": ["F"], "F": []}
print(bfs_shortest_path(graph, "A", "F"), bfs_shortest_path(graph, "F", "A"))      # ['A', 'B', 'D', 'F'] None
```

More: [graphs](../graphs/README.md) and [BFS in the patterns chapter](../../09-interview-playbook/problem-solving-patterns/README.md).

## 10. Choosing the right structure

| Need | Use |
|------|-----|
| Last in, first out | stack (`list`) |
| First in, first out | `collections.deque` (`append` + `popleft`) |
| Both ends | `deque` |
| Bounded history / "last N items" | `deque(maxlen=N)` or a ring buffer |
| Always get the min/max next | `heapq` (priority queue) |
| Threads exchanging work | `queue.Queue` / `PriorityQueue` |
| Async tasks | `asyncio.Queue` |
| Distributed work across machines | a message queue (RabbitMQ, SQS, Kafka) ([system design](../../09-interview-playbook/system-design-basics/README.md)) |

## 11. Two real-world examples

**Example 1: A web server's request queue.** Requests arrive faster than workers can handle them during a spike; they wait in a queue and are served first-in-first-out. A **bounded** queue protects the server: when full it rejects new requests (HTTP 503) instead of exhausting memory. Real systems add **priority** (health checks first) and **timeouts** (drop requests that waited too long).

**Example 2: Print jobs and the operating system's scheduler.** The print spooler is a FIFO queue of documents. The OS keeps a **ready queue** of processes waiting for the CPU; a round-robin scheduler dequeues the front process, runs it for a time slice and enqueues it at the back ([scheduling](../../06-operating-systems/scheduling/README.md)). Priority-based schedulers use priority queues.

## 12. Common mistakes

- Using `list.pop(0)` for a queue (`O(n)`); use `deque.popleft()`.
- Dequeuing from an empty queue without checking.
- Forgetting to handle the "queue became empty" case in the linked version (tail must reset).
- Unbounded queues that grow without limit when producers outpace consumers.
- Assuming a heap preserves insertion order among equal priorities (add a counter).
- Forgetting that `heapq` is a **min**-heap.
- Sharing a plain `deque`/`list` between threads without synchronization (`queue.Queue` is the safe choice for producer-consumer).

## 13. Practice

1. Simulate a bank with one teller: customers arrive at given times with service durations; compute each customer's waiting time using a queue.
2. Implement a `Stack` using two queues (or one queue) and compare costs.
3. Print the last 5 lines of a text (like `tail`) using a bounded `deque`.
4. Use a priority queue to merge `k` sorted lists.
5. Implement a ring buffer of the most recent 100 temperature readings with a moving average.
6. Process tasks by priority but let tasks with the same priority run FIFO.
7. Use a deque to solve the sliding-window maximum problem in `O(n)`.

<details>
<summary>Solutions</summary>

**1.**
```python
def bank_waits(customers):                           # customers: list of (arrival_time, service_time), sorted by arrival
    waits, free_at = [], 0
    q = deque(customers)
    while q:
        arrival, service = q.popleft()
        start = max(arrival, free_at)
        waits.append(start - arrival)
        free_at = start + service
    return waits
print(bank_waits([(0, 5), (1, 3), (2, 2), (10, 1)]))        # [0, 4, 6, 0]
```

**2.**
```python
class StackFromOneQueue:
    def __init__(self): self.q = deque()
    def push(self, x):                                # O(n): rotate so the newest item is at the front
        self.q.append(x)
        for _ in range(len(self.q) - 1):
            self.q.append(self.q.popleft())
    def pop(self): return self.q.popleft()            # O(1)
s = StackFromOneQueue()
for x in (1, 2, 3): s.push(x)
print(s.pop(), s.pop(), s.pop())                      # 3 2 1
```

**3.**
```python
def tail(lines, n=5):
    last = deque(maxlen=n)
    for line in lines:
        last.append(line)
    return list(last)
print(tail((f"line {i}" for i in range(1, 21)), 3))   # ['line 18', 'line 19', 'line 20']
```

**4.**
```python
def merge_k(lists):
    heap = [(lst[0], i, 0) for i, lst in enumerate(lists) if lst]
    heapq.heapify(heap)
    out = []
    while heap:
        value, i, j = heapq.heappop(heap)
        out.append(value)
        if j + 1 < len(lists[i]):
            heapq.heappush(heap, (lists[i][j + 1], i, j + 1))
    return out
print(merge_k([[1, 4, 7], [2, 5], [3, 6, 9]]))        # [1, 2, 3, 4, 5, 6, 7, 9]
```

**5.**
```python
class MovingAverage:
    def __init__(self, size):
        self.window, self.total = deque(maxlen=size), 0.0
    def add(self, x):
        if len(self.window) == self.window.maxlen:
            self.total -= self.window[0]               # the oldest value is about to be dropped
        self.window.append(x)
        self.total += x
        return self.total / len(self.window)
ma = MovingAverage(3)
print([round(ma.add(x), 2) for x in (10, 20, 30, 40, 50)])        # [10.0, 15.0, 20.0, 30.0, 40.0]
```

**6.** See `TaskQueue` above: the counter in `(priority, counter, task)` preserves arrival order among equals.

**7.**
```python
def sliding_window_max(nums, k):
    dq, out = deque(), []                              # dq holds INDEXES whose values are in decreasing order
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:
            dq.pop()                                   # smaller items can never be a maximum again
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()                               # the front index left the window
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out
print(sliding_window_max([1, 3, -1, -3, 5, 3, 6, 7], 3))          # [3, 3, 5, 5, 6, 7]
```

</details>

## 14. Check yourself

1. What does FIFO mean?
2. Why is `list.pop(0)` a poor dequeue?
3. How does a circular buffer avoid shifting?
4. What is the difference between a queue, a deque and a priority queue?
5. How do you get FIFO behavior among equal priorities in a heap?
6. Which algorithm uses a queue to find shortest paths?

<details>
<summary>Answers</summary>

1. First In, First Out: the item that arrived first leaves first.
2. It shifts every remaining item left, making each dequeue `O(n)`.
3. The front and back indexes wrap around with modulo, so items stay in place and only indexes move.
4. A queue serves in arrival order from one end; a deque allows adds/removes at both ends; a priority queue serves the highest-priority item first.
5. Store a counter as the second tuple element: `(priority, counter, item)`.
6. Breadth-first search.

</details>

[Back to stacks and queues](README.md) · Previous: [stacks](01-stacks.md) · Next: [stack and queue applications](03-stack-and-queue-applications.md)
