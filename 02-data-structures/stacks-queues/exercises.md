# Stacks and Queues: Exercises

## Problems
1. Check if a string of brackets `()[]{}` is balanced.
2. Implement a **min-stack** supporting `push`, `pop`, `top` and `get_min` in `O(1)`.
3. Implement a queue using two stacks.
4. Evaluate a Reverse Polish Notation expression.
5. **Daily temperatures:** for each day, how many days until a warmer temperature?
6. **Next greater element** for every item in a list.
7. **Sliding window maximum** in `O(n)`.
8. Simplify a Unix path (`/a/./b/../../c/` becomes `/c`).
9. Implement a stack using a single queue.
10. Design a **ring buffer** that overwrites the oldest item when full.

<details>
<summary>Solutions</summary>

```python
from collections import deque

# 1
def is_balanced(s):
    pairs = {")": "(", "]": "[", "}": "{"}
    st = []
    for ch in s:
        if ch in "([{":
            st.append(ch)
        elif ch in pairs:
            if not st or st.pop() != pairs[ch]:
                return False
    return not st

# 2
class MinStack:
    def __init__(self):
        self.st = []                   # (value, current_min)
    def push(self, x):
        m = x if not self.st else min(x, self.st[-1][1])
        self.st.append((x, m))
    def pop(self): return self.st.pop()[0]
    def top(self): return self.st[-1][0]
    def get_min(self): return self.st[-1][1]

# 3
class QueueFromStacks:
    def __init__(self):
        self.inp, self.out = [], []
    def enqueue(self, x): self.inp.append(x)
    def dequeue(self):
        if not self.out:
            while self.inp:
                self.out.append(self.inp.pop())
        return self.out.pop()

# 4
def eval_rpn(tokens):
    st = []
    for t in tokens:
        if t in {"+", "-", "*", "/"}:
            b, a = st.pop(), st.pop()
            st.append({"+": a + b, "-": a - b, "*": a * b,
                       "/": int(a / b)}[t])
        else:
            st.append(int(t))
    return st[0]

# 5
def daily_temperatures(t):
    res, st = [0] * len(t), []
    for i, x in enumerate(t):
        while st and t[st[-1]] < x:
            j = st.pop()
            res[j] = i - j
        st.append(i)
    return res

# 6
def next_greater(nums):
    res, st = [-1] * len(nums), []
    for i, x in enumerate(nums):
        while st and nums[st[-1]] < x:
            res[st.pop()] = x
        st.append(i)
    return res

# 7
def max_sliding_window(nums, k):
    dq, out = deque(), []
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            out.append(nums[dq[0]])
    return out

# 8
def simplify_path(path):
    st = []
    for part in path.split("/"):
        if part == "..":
            if st:
                st.pop()
        elif part and part != ".":
            st.append(part)
    return "/" + "/".join(st)

# 9
class StackFromQueue:
    def __init__(self):
        self.q = deque()
    def push(self, x):
        self.q.append(x)
        for _ in range(len(self.q) - 1):     # rotate so newest is at the front
            self.q.append(self.q.popleft())
    def pop(self): return self.q.popleft()
    def top(self): return self.q[0]

# 10
class RingBuffer:
    def __init__(self, capacity):
        self.buf = [None] * capacity
        self.cap, self.head, self.size = capacity, 0, 0
    def push(self, x):
        tail = (self.head + self.size) % self.cap
        self.buf[tail] = x
        if self.size == self.cap:
            self.head = (self.head + 1) % self.cap
        else:
            self.size += 1
    def pop(self):
        if not self.size:
            raise IndexError("empty")
        x = self.buf[self.head]
        self.head = (self.head + 1) % self.cap
        self.size -= 1
        return x
```

</details>

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Stacks](01-stacks.md) · [Queues, Deques and Priority Queues](02-queues-deques-priority-queues.md) · [Stack and Queue Applications](03-stack-and-queue-applications.md)
