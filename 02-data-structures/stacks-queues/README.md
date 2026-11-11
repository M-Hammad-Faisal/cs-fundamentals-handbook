# Stacks and Queues

## Detailed lessons

1. [Stacks](01-stacks.md): array and linked stacks, brackets, undo/redo, DFS
2. [Queues, deques and priority queues](02-queues-deques-priority-queues.md): ring buffer, `deque`, `heapq`, BFS
3. [Stack and queue applications](03-stack-and-queue-applications.md): shunting-yard, monotonic stack and deque, simulations

The rest of this page is the quick reference.

## 1. The concept

Both are **restricted-access sequences**: you only touch the ends, which gives a clear contract and `O(1)` operations.

| Structure | Rule | Mnemonic | Core operations |
|-----------|------|----------|-----------------|
| **Stack** | Last in, first out (**LIFO**) | A stack of plates | `push`, `pop`, `peek` |
| **Queue** | First in, first out (**FIFO**) | A line at a bank | `enqueue`, `dequeue`, `peek` |
| **Deque** | Add/remove at both ends | A double-ended line | `append`, `appendleft`, `pop`, `popleft` |
| **Priority queue** | Highest priority leaves first | An emergency room | `push`, `pop_min` (see [heaps](../heaps/README.md)) |

## 2. How it works in Python

### Stack: use a list

```python
stack = []
stack.append(1)       # push, O(1) amortized
stack.append(2)
stack[-1]             # peek -> 2
stack.pop()           # pop  -> 2, O(1)
```

### Queue: use `collections.deque`

```python
from collections import deque

q = deque()
q.append("a")         # enqueue, O(1)
q.append("b")
q.popleft()           # dequeue -> "a", O(1)
```

Never use `list.pop(0)` for a queue: it is `O(n)`. `deque` is a doubly linked list of blocks, so both ends are `O(1)`.

For multithreading use `queue.Queue` (thread-safe, blocking), `queue.LifoQueue`, or `queue.PriorityQueue`.

### Hand-built versions (for understanding)

```python
class Stack:
    def __init__(self):
        self._items = []
    def push(self, x): self._items.append(x)
    def pop(self):
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items.pop()
    def peek(self): return self._items[-1]
    def is_empty(self): return not self._items
    def __len__(self): return len(self._items)

class Queue:
    def __init__(self):
        self._items = deque()
    def enqueue(self, x): self._items.append(x)
    def dequeue(self):
        if not self._items:
            raise IndexError("dequeue from empty queue")
        return self._items.popleft()
    def __len__(self): return len(self._items)
```

### Complexity

| Operation | Stack (list) | Queue (deque) |
|-----------|--------------|---------------|
| Push / enqueue | `O(1)` amortized | `O(1)` |
| Pop / dequeue | `O(1)` | `O(1)` |
| Peek | `O(1)` | `O(1)` |
| Search | `O(n)` | `O(n)` |

### Circular buffer (ring buffer)

A fixed-size queue stored in an array with `head` and `tail` indices that wrap around using modulo. It never reallocates, which is ideal for streaming data and bounded buffers.

```python
class RingBuffer:
    def __init__(self, capacity):
        self.buf = [None] * capacity
        self.cap, self.head, self.size = capacity, 0, 0

    def push(self, x):
        tail = (self.head + self.size) % self.cap
        self.buf[tail] = x
        if self.size == self.cap:
            self.head = (self.head + 1) % self.cap   # overwrite oldest
        else:
            self.size += 1

    def pop(self):
        if self.size == 0:
            raise IndexError("empty")
        x = self.buf[self.head]
        self.head = (self.head + 1) % self.cap
        self.size -= 1
        return x
```

## 3. Classic patterns

### Balanced brackets (stack)

```python
def is_balanced(s):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in s:
        if ch in "([{":
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack            # O(n)
```

### Monotonic stack: next greater element

Keep the stack in decreasing order so each element is pushed and popped once.

```python
def next_greater(nums):
    res = [-1] * len(nums)
    stack = []                       # indices with unresolved answers
    for i, x in enumerate(nums):
        while stack and nums[stack[-1]] < x:
            res[stack.pop()] = x
        stack.append(i)
    return res                       # O(n)
```

### Evaluate postfix (reverse Polish) expressions

```python
def eval_rpn(tokens):
    stack = []
    for t in tokens:
        if t in {"+", "-", "*", "/"}:
            b, a = stack.pop(), stack.pop()
            stack.append({"+": a + b, "-": a - b, "*": a * b,
                          "/": int(a / b)}[t])
        else:
            stack.append(int(t))
    return stack[0]
```

### Queue via BFS: shortest path in a grid

```python
def shortest_path(grid, start, goal):
    rows, cols = len(grid), len(grid[0])
    q = deque([(start, 0)])
    seen = {start}
    while q:
        (r, c), d = q.popleft()
        if (r, c) == goal:
            return d
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if (0 <= nr < rows and 0 <= nc < cols
                    and grid[nr][nc] == 0 and (nr, nc) not in seen):
                seen.add((nr, nc))
                q.append(((nr, nc), d + 1))
    return -1
```

### Sliding window maximum (monotonic deque)

```python
def max_sliding_window(nums, k):
    dq, out = deque(), []             # dq holds indices, values decreasing
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out                        # O(n)
```

### Two stacks make a queue

Push to an `in` stack; when `out` is empty, pour `in` into `out`. Each element moves at most twice, so operations are amortized `O(1)`.

## 4. Two real-world examples

### Example 1: Undo/redo and the browser back button

Every action pushed onto an **undo stack** is popped in reverse order to undo it, and moved to a **redo stack**. The browser back button works the same way: each page visited is pushed, and "back" pops. The **call stack** that runs your programs is also a stack: each function call pushes a frame; returning pops it. A stack overflow is that stack running out of space.

### Example 2: Job queues and message brokers

When a web request triggers slow work (sending emails, resizing images), the app puts a job on a **queue** (Celery, RabbitMQ, SQS, Kafka) and returns immediately. Workers take jobs in order, which smooths traffic spikes and decouples the producer from the consumer. Print spoolers, CPU run queues and call-centre waiting lines are the same FIFO idea. Priority queues serve urgent jobs first.

## 5. Tips, tricks and pitfalls

- **Recursion is an implicit stack.** Any recursive algorithm can become iterative with an explicit stack, avoiding recursion-limit errors (DFS is the classic example).
- **BFS uses a queue; DFS uses a stack.** BFS finds shortest paths in unweighted graphs.
- **Use `deque`, not `list`, for queues.** `pop(0)` is `O(n)`.
- **Guard empty structures** before `pop`/`peek`.
- **Monotonic stack/deque** turns many "next greater" and "window maximum" problems from `O(n²)` into `O(n)`.
- **Thread safety:** `deque` appends/pops are atomic in CPython, but use `queue.Queue` when you need blocking and timeouts.
- **Bounded queues give back-pressure.** An unbounded queue can eat all memory under overload.

## 6. Check yourself

1. Why is `list.pop(0)` a bad queue operation and what replaces it?
2. How does a stack detect balanced brackets?
3. What does a monotonic stack buy you, and why is it still `O(n)`?
4. Why does BFS use a queue and DFS a stack?
5. How do two stacks implement a queue, and what is the amortized cost?
6. What is the call stack, and what is a stack overflow?
7. Why use a bounded queue in a production job system?

<details>
<summary>Answers</summary>

1. It shifts all remaining elements (`O(n)`). Use `collections.deque.popleft()`, which is `O(1)`.
2. Push openers; on a closer, pop and check that it matches; at the end the stack must be empty.
3. It answers "next greater/smaller" questions in one pass. Each index is pushed once and popped once, so total work is linear.
4. BFS explores level by level (first discovered, first processed: FIFO). DFS goes deep and backtracks (most recent, first processed: LIFO).
5. Push onto `in`; on dequeue, if `out` is empty move everything from `in` to `out`, then pop `out`. Each element moves at most once between stacks, so amortized `O(1)`.
6. The call stack stores a frame per active function call. Too many nested calls exhaust it: stack overflow (`RecursionError` in Python).
7. It limits memory use and applies back-pressure, rejecting or slowing producers when consumers fall behind.

</details>

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

Back to the [part overview](../README.md).
