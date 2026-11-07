# Stacks: Last In, First Out

**Prerequisites:** [arrays and memory](../arrays-strings/01-arrays-and-memory.md), [linked lists](../linked-lists/01-singly-linked-list.md), [the call stack](../../00-foundations/computer-basics/memory-stack-heap.md). **You will learn:** what a stack is, its operations and rule, how to implement it with an array and with a linked list, how Python's `list` and `deque` act as stacks, and the classic problems stacks solve (reversal, matching brackets, undo, backtracking, a min-stack).

## 1. In plain words

A **stack** is a collection with one rule: **the last item you put in is the first one you take out** (**LIFO**: Last In, First Out). You can only touch the **top**.

Analogy: a **stack of plates**. You add a clean plate on top, you take a plate from the top. You never pull one out of the middle. Or the **Back button** in a browser: the page you visited most recently is the first one you go back to.

```text
         push(30)             pop() -> 30
   ┌────┐             ┌────┐              ┌────┐
   │ 30 │ ◄ top       │ 20 │ ◄ top        │ 20 │ ◄ top
   │ 20 │             │ 10 │              │ 10 │
   │ 10 │             └────┘              └────┘
   └────┘
```

### The operations (all `O(1)`)

| Operation | Meaning |
|-----------|---------|
| `push(x)` | put `x` on top |
| `pop()` | remove and return the top item (error if empty) |
| `peek()` / `top()` | look at the top without removing it |
| `is_empty()` | is the stack empty? |
| `size()` / `len` | how many items |

## 2. Implementation 1: backed by an array (Python list)

Pushing and popping at the **end** of a Python list is `O(1)` (amortized), so a list is a perfect stack: the **end of the list is the top**.

```python
class Stack:
    def __init__(self):
        self._items = []                         # the end of the list is the top of the stack

    def push(self, item):                        # O(1) amortized
        self._items.append(item)

    def pop(self):                               # O(1)
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self):                              # O(1)
        if not self._items:
            raise IndexError("peek at empty stack")
        return self._items[-1]

    def is_empty(self):
        return not self._items

    def __len__(self):
        return len(self._items)

    def __repr__(self):
        return f"Stack({self._items}) <- top"

s = Stack()
for x in (10, 20, 30):
    s.push(x)
print(s, s.peek(), len(s))                       # Stack([10, 20, 30]) <- top 30 3
print(s.pop(), s.pop(), s, s.is_empty())         # 30 20 Stack([10]) <- top False
s.pop()
try:
    s.pop()
except IndexError as error:
    print("IndexError:", error)                  # IndexError: pop from empty stack
```

(Do **not** use `list.pop(0)` / `insert(0, x)` for a stack: those are `O(n)`.) In everyday Python you just use a plain list: `stack.append(x)`, `stack.pop()`, `stack[-1]`.

## 3. Implementation 2: backed by a linked list

The **head** of a singly linked list is the top: push = prepend, pop = remove the head: both `O(1)` with **no resizing** at all.

```python
class LinkedStack:
    class _Node:
        __slots__ = ("value", "next")
        def __init__(self, value, next):
            self.value, self.next = value, next

    def __init__(self):
        self._top = None
        self._size = 0

    def push(self, value):
        self._top = self._Node(value, self._top)    # the new node points at the old top
        self._size += 1

    def pop(self):
        if self._top is None:
            raise IndexError("pop from empty stack")
        node = self._top
        self._top = node.next                       # move the top down
        self._size -= 1
        return node.value

    def peek(self):
        if self._top is None:
            raise IndexError("peek at empty stack")
        return self._top.value

    def __len__(self):
        return self._size

ls = LinkedStack()
for ch in "abc":
    ls.push(ch)
print(ls.peek(), ls.pop(), ls.pop(), len(ls))      # c c b 1
```

| | Array-backed | Linked-list-backed |
|--|--------------|--------------------|
| push/pop | `O(1)` amortized (rare resize) | `O(1)` worst case |
| Memory | compact, cache-friendly | extra pointer per item |
| Usually chosen | **yes** (simpler and faster in Python) | when a hard worst-case bound matters |

## 4. A bounded stack and stack overflow

A stack with a fixed capacity raises **stack overflow** when full: this is exactly what happens when recursion goes too deep ([call stack](../../00-foundations/computer-basics/memory-stack-heap.md)).

```python
class BoundedStack(Stack):
    def __init__(self, capacity):
        super().__init__()
        self.capacity = capacity
    def push(self, item):
        if len(self) >= self.capacity:
            raise OverflowError("stack overflow")
        super().push(item)

b = BoundedStack(2)
b.push(1); b.push(2)
try:
    b.push(3)
except OverflowError as error:
    print("OverflowError:", error)               # OverflowError: stack overflow
```

## 5. Classic stack problems

### Reversal

```python
def reverse_string(text):
    s = Stack()
    for ch in text:
        s.push(ch)
    return "".join(s.pop() for _ in range(len(s)))     # popping returns items in reverse order

print(reverse_string("stack"))                          # kcats
```

### Balanced brackets

For `"{[()]}"` every closer must match the **most recent unmatched opener**: exactly what a stack remembers.

```text
 input: ( [ { } ] )
 ( push (   stack: (
 [ push [   stack: ( [
 { push {   stack: ( [ {
 } pop {  ✓   stack: ( [
 ] pop [  ✓   stack: (
 ) pop (  ✓   stack: (empty)  -> balanced
```

```python
def is_balanced(text):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in text:
        if ch in "([{":
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False                         # a closer with no matching opener
    return not stack                                 # leftover openers mean unbalanced

for case in ("{[()]}", "([)]", "((", ")(", "", "a(b[c]d)e"):
    print(repr(case), is_balanced(case))
# '{[()]}' True / '([)]' False / '((' False / ')(' False / '' True / 'a(b[c]d)e' True
```

### Undo and redo

```python
class TextEditor:
    def __init__(self):
        self.text = ""
        self.undo_stack, self.redo_stack = [], []
    def type(self, s):
        self.undo_stack.append(self.text)            # remember the state BEFORE the change
        self.redo_stack.clear()                      # a new action invalidates "redo"
        self.text += s
    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.text)
            self.text = self.undo_stack.pop()
    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.text)
            self.text = self.redo_stack.pop()

ed = TextEditor()
ed.type("Hello"); ed.type(" world"); ed.type("!")
print(ed.text)                                       # Hello world!
ed.undo(); ed.undo()
print(ed.text)                                       # Hello
ed.redo()
print(ed.text)                                       # Hello world
ed.type("?")                                         # a new edit clears redo history
ed.redo()
print(ed.text)                                       # Hello world?
```

### Depth-first search (an explicit stack instead of recursion)

```python
def dfs_iterative(graph, start):
    visited, stack, order = set(), [start], []
    while stack:
        node = stack.pop()                           # LIFO: explore the most recently discovered node first
        if node in visited:
            continue
        visited.add(node)
        order.append(node)
        stack.extend(reversed(graph[node]))          # reversed so the first neighbor is processed first
    return order

graph = {"A": ["B", "C"], "B": ["D"], "C": ["D", "E"], "D": [], "E": []}
print(dfs_iterative(graph, "A"))                     # ['A', 'B', 'D', 'C', 'E']
```

This is how you avoid `RecursionError` on deep structures: the explicit stack lives on the heap and can grow far larger than the call stack ([graph traversals](../graphs/README.md)).

### Backtracking (maze solving)

When you hit a dead end you **pop** back to the last choice point: a stack naturally records the path.

```python
def solve_maze(maze, start, goal):
    stack = [(start, [start])]                       # (position, path so far)
    seen = {start}
    while stack:
        (r, c), path = stack.pop()
        if (r, c) == goal:
            return path
        for dr, dc in ((1, 0), (0, 1), (-1, 0), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(maze) and 0 <= nc < len(maze[0]) and maze[nr][nc] == 0 and (nr, nc) not in seen:
                seen.add((nr, nc))
                stack.append(((nr, nc), path + [(nr, nc)]))
    return None

maze = [[0, 0, 1],
        [1, 0, 1],
        [1, 0, 0]]
print(solve_maze(maze, (0, 0), (2, 2)))              # [(0, 0), (0, 1), (1, 1), (2, 1), (2, 2)]
```

## 6. The min-stack: get the minimum in O(1)

**Problem:** a stack that also supports `get_min()` in `O(1)`. **Idea:** store, with every item, the minimum **so far** (the minimum of everything at or below it).

```python
class MinStack:
    def __init__(self):
        self._stack = []                             # pairs of (value, minimum so far)

    def push(self, x):
        current_min = x if not self._stack else min(x, self._stack[-1][1])
        self._stack.append((x, current_min))

    def pop(self):
        return self._stack.pop()[0]

    def top(self):
        return self._stack[-1][0]

    def get_min(self):
        return self._stack[-1][1]                    # O(1): the answer is stored with the top item

m = MinStack()
for x in (5, 3, 7, 2, 8):
    m.push(x)
print(m.get_min(), m.pop(), m.pop(), m.get_min(), m.pop(), m.get_min())      # 2 8 2 3 7 3
```

Without the extra data, the minimum would require scanning the whole stack (`O(n)`).

## 7. Stacks in the Python ecosystem

| Where | Stack idea |
|-------|-----------|
| **The call stack** | function calls push frames; returns pop them (and tracebacks are stack dumps) |
| `list` | `append` / `pop` / `[-1]` |
| `collections.deque` | `append` / `pop` (also `O(1)`) |
| `queue.LifoQueue` | a thread-safe stack |
| Expression evaluation | operands/operators stacks ([applications](03-stack-and-queue-applications.md)) |
| Undo/redo, browser history | state stacks |
| Parsers and compilers | track nesting (brackets, tags) |
| DFS, backtracking | path stacks |

```python
from queue import LifoQueue
lifo = LifoQueue()
lifo.put("first"); lifo.put("second")
print(lifo.get(), lifo.get())                        # second first
```

## 8. Two real-world examples

**Example 1: The call stack and tracebacks.** Every function call pushes a frame holding its variables and return address; returning pops it. A traceback prints that stack from the bottom up. "Stack overflow" is a call stack that grew too large (infinite recursion): the website of that name takes its name from this error.

**Example 2: Checking HTML or code for matching tags and brackets.** An editor highlights the matching `)` for your `(`, and a linter reports "unexpected `}`": both push openers and pop on closers. The same idea validates XML/HTML nesting and underlies parsers for programming languages and expression evaluators.

## 9. Common mistakes

- Popping from an empty stack (check `is_empty()` or handle `IndexError`).
- Using `list.pop(0)` / `insert(0, x)` (that is a queue operation and `O(n)`).
- Forgetting to check that the stack is empty at the end when matching brackets.
- Mixing up which end is the top (be consistent).
- Using recursion where depth may exceed the limit; use an explicit stack.
- Storing mutable objects and then modifying them while they are on the stack (surprising aliasing).

## 10. Practice

1. Evaluate a postfix expression such as `"3 4 + 2 *"` with a stack.
2. Reverse the words in a sentence using a stack (keep the letters in each word).
3. Convert a decimal number to binary using a stack of remainders.
4. Check that HTML-like tags are nested correctly: `<a><b></b></a>` valid, `<a><b></a></b>` invalid.
5. Implement a `MaxStack` that supports `get_max()` in `O(1)`.
6. Remove adjacent duplicate characters repeatedly (`"abbaca"` becomes `"ca"`).
7. Implement a stack using two queues (and note the cost).

<details>
<summary>Solutions</summary>

**1.**
```python
def eval_postfix(expression):
    stack = []
    for token in expression.split():
        if token in "+-*/":
            b, a = stack.pop(), stack.pop()               # the right operand was pushed last
            stack.append({"+": a + b, "-": a - b, "*": a * b, "/": a / b}[token])
        else:
            stack.append(float(token))
    return stack.pop()
print(eval_postfix("3 4 + 2 *"), eval_postfix("5 1 2 + 4 * + 3 -"))      # 14.0 14.0
```

**2.**
```python
def reverse_words(sentence):
    stack = sentence.split()
    return " ".join(stack.pop() for _ in range(len(stack)))
print(reverse_words("the quick brown fox"))              # fox brown quick the
```

**3.**
```python
def to_binary(n):
    stack = []
    while n > 0:
        stack.append(n % 2); n //= 2
    return "".join(str(stack.pop()) for _ in range(len(stack))) or "0"
print(to_binary(45), to_binary(0))                       # 101101 0
```

**4.**
```python
import re
def tags_balanced(html):
    stack = []
    for closing, name in re.findall(r"<(/?)(\w+)>", html):
        if not closing:
            stack.append(name)
        elif not stack or stack.pop() != name:
            return False
    return not stack
print(tags_balanced("<a><b></b></a>"), tags_balanced("<a><b></a></b>"))      # True False
```

**5.**
```python
class MaxStack:
    def __init__(self): self._s = []
    def push(self, x): self._s.append((x, x if not self._s else max(x, self._s[-1][1])))
    def pop(self): return self._s.pop()[0]
    def get_max(self): return self._s[-1][1]
ms = MaxStack()
for x in (2, 9, 4): ms.push(x)
print(ms.get_max(), ms.pop(), ms.pop(), ms.get_max())    # 9 4 9 2
```

**6.**
```python
def remove_duplicates(s):
    stack = []
    for ch in s:
        if stack and stack[-1] == ch:
            stack.pop()
        else:
            stack.append(ch)
    return "".join(stack)
print(remove_duplicates("abbaca"))                       # ca
```

**7.**
```python
from collections import deque
class StackFromQueues:
    def __init__(self): self.q = deque()
    def push(self, x):                                  # O(n): rotate the new item to the front of the queue
        self.q.append(x)
        for _ in range(len(self.q) - 1):
            self.q.append(self.q.popleft())
    def pop(self): return self.q.popleft()              # O(1)
sq = StackFromQueues()
for x in (1, 2, 3): sq.push(x)
print(sq.pop(), sq.pop(), sq.pop())                     # 3 2 1
```

</details>

## 11. Check yourself

1. What does LIFO mean, with an everyday example?
2. What are the stack operations and their cost?
3. Why is a Python `list` a good stack, and which end is the top?
4. How does a stack check balanced brackets?
5. How can a stack provide the minimum in `O(1)`?
6. How does an explicit stack avoid `RecursionError`?

<details>
<summary>Answers</summary>

1. Last In, First Out: the most recently added item leaves first (a stack of plates, the browser Back button).
2. `push`, `pop`, `peek`, `is_empty`, `size`: all `O(1)`.
3. `append` and `pop` at the end are `O(1)` amortized; the end of the list is the top.
4. Push each opener; for each closer pop and compare with the matching opener; at the end the stack must be empty.
5. Store the minimum-so-far alongside each pushed item.
6. It keeps the pending work on the heap (a growable list) instead of the limited call stack.

</details>

[Back to stacks and queues](README.md) · Next: [queues, deques and priority queues](02-queues-deques-priority-queues.md)
