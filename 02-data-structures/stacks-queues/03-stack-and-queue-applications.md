# Stack and Queue Applications

**Prerequisites:** [stacks](01-stacks.md), [queues and deques](02-queues-deques-priority-queues.md). **You will learn:** how stacks and queues power real programs: evaluating arithmetic expressions (infix to postfix with the shunting-yard algorithm), the **monotonic stack** (next greater element, daily temperatures, largest rectangle), the **monotonic deque** (sliding-window maximum), simulations, and when to choose a stack versus a queue.

## 1. In plain words

Stacks and queues look trivial, but a few clever ideas built on them solve problems that otherwise need nested loops:

- A **stack** remembers *unfinished business* in reverse order (open brackets, pending operators, the path back).
- A **queue** processes items **in the order they arrived** (fairness, level-by-level exploration, streaming).
- A **monotonic** stack or deque keeps its contents sorted as you go, so each item is pushed and popped **at most once**: **`O(n)`** instead of `O(n²)`.

## 2. Evaluating arithmetic expressions

Humans write **infix** expressions (`3 + 4 * 2`) where **precedence** and **parentheses** matter. Computers prefer **postfix** (**Reverse Polish Notation, RPN**): operators come after their operands (`3 4 2 * +`), so no parentheses or precedence rules are needed: a stack alone evaluates it.

| Infix | Postfix |
|-------|---------|
| `3 + 4` | `3 4 +` |
| `3 + 4 * 2` | `3 4 2 * +` |
| `(3 + 4) * 2` | `3 4 + 2 *` |

### Evaluating postfix with one stack

```text
Evaluate  3 4 2 * +        stack (top on the right)
 3        push 3             [3]
 4        push 4             [3, 4]
 2        push 2             [3, 4, 2]
 *        pop 2, 4 -> 4*2=8  [3, 8]
 +        pop 8, 3 -> 3+8=11 [11]        answer: 11
```

```python
import operator

OPERATIONS = {"+": operator.add, "-": operator.sub, "*": operator.mul,
              "/": operator.truediv, "^": operator.pow}      # functions, so only the needed one runs

def eval_postfix(tokens):
    stack = []
    for token in tokens:
        if token in OPERATIONS:
            right, left = stack.pop(), stack.pop()            # the right operand was pushed last
            stack.append(OPERATIONS[token](left, right))
        else:
            stack.append(float(token))
    return stack.pop()

print(eval_postfix("3 4 2 * +".split()), eval_postfix("3 4 + 2 *".split()), eval_postfix("2 3 ^ 1 -".split()))      # 11.0 14.0 7.0
```

### Converting infix to postfix: the shunting-yard algorithm (Dijkstra)

Scan tokens; send **numbers** straight to the output; keep **operators** on a stack and pop them when a lower-or-equal precedence operator arrives; handle parentheses.

```python
PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2, "^": 3}
RIGHT_ASSOCIATIVE = {"^"}                                      # 2^3^2 means 2^(3^2)

def tokenize(expression):
    import re
    return re.findall(r"\d+\.?\d*|[-+*/^()]", expression)

def to_postfix(expression):
    output, operators = [], []
    for token in tokenize(expression):
        if token not in PRECEDENCE and token not in "()":
            output.append(token)                               # a number
        elif token in PRECEDENCE:
            while (operators and operators[-1] != "(" and
                   (PRECEDENCE[operators[-1]] > PRECEDENCE[token] or
                    (PRECEDENCE[operators[-1]] == PRECEDENCE[token] and token not in RIGHT_ASSOCIATIVE))):
                output.append(operators.pop())                 # the stacked operator binds at least as tightly: emit it first
            operators.append(token)
        elif token == "(":
            operators.append(token)
        else:                                                  # ")": pop until the matching "("
            while operators and operators[-1] != "(":
                output.append(operators.pop())
            operators.pop()                                    # discard the "("
    while operators:
        output.append(operators.pop())
    return output

def calculate(expression):
    return eval_postfix(to_postfix(expression))

print(to_postfix("3 + 4 * 2"), to_postfix("(3 + 4) * 2"))      # ['3', '4', '2', '*', '+'] ['3', '4', '+', '2', '*']
print(calculate("3 + 4 * 2 / ( 1 - 5 ) ^ 2 ^ 3"), calculate("(1 + 2) * (3 + 4)"), calculate("10 / 4 - 1"))      # 3.0001220703125 21.0 1.5
```

This is the core of every calculator, spreadsheet formula engine and many compilers (a **parser** turns text into a structure that a stack machine can execute: the same way Python's own bytecode works with a value stack: see [bytecode](../../00-foundations/computer-basics/how-computers-work.md)).

## 3. The monotonic stack

**Idea:** keep a stack whose values are always sorted (increasing or decreasing). When a new item arrives, **pop everything that can no longer be the answer** for anyone, answering their question as you pop. Every element is pushed once and popped once: **`O(n)`**.

### Next greater element

For each number, find the next number to its right that is larger (or `-1`).

```text
nums = [2, 1, 2, 4, 3]       stack holds INDEXES of numbers still waiting for their answer (decreasing values)

 x=2  stack [0]
 x=1  1 < 2: wait.            stack [0, 1]
 x=2  2 > 1: answer for idx 1 is 2;  2 == 2 not greater: stop;  stack [0, 2]
 x=4  4 > 2: answer for idx 2 is 4;  4 > 2: answer for idx 0 is 4;  stack [3]
 x=3  3 < 4: wait.            stack [3, 4]
 end: indexes 3 and 4 never found a greater number: -1
 result: [4, 2, 4, -1, -1]
```

```python
def next_greater(nums):
    answer = [-1] * len(nums)
    stack = []                                       # indexes of items still waiting for a greater number
    for i, x in enumerate(nums):
        while stack and nums[stack[-1]] < x:
            answer[stack.pop()] = x                  # x is the next greater value for that waiting item
        stack.append(i)
    return answer

print(next_greater([2, 1, 2, 4, 3]), next_greater([5, 4, 3]), next_greater([1, 2, 3]))      # [4, 2, 4, -1, -1] [-1, -1, -1] [2, 3, -1]
```

### Daily temperatures: how many days until it is warmer?

```python
def daily_temperatures(temps):
    wait = [0] * len(temps)
    stack = []
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            j = stack.pop()
            wait[j] = i - j                          # days between the colder day j and the warmer day i
        stack.append(i)
    return wait

print(daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]))      # [1, 1, 4, 2, 1, 1, 0, 0]
```

### Stock span and previous smaller values

The same pattern in the other direction answers "how many consecutive days before today had a price at most today's?":

```python
def stock_spans(prices):
    spans, stack = [], []                            # stack of (price, span) with decreasing prices
    for price in prices:
        span = 1
        while stack and stack[-1][0] <= price:
            span += stack.pop()[1]                   # absorb the span of every smaller-or-equal day
        stack.append((price, span))
        spans.append(span)
    return spans
print(stock_spans([100, 80, 60, 70, 60, 75, 85]))    # [1, 1, 1, 2, 1, 4, 6]
```

### Largest rectangle in a histogram

Given bar heights, find the area of the largest rectangle. A stack of **increasing** heights lets us finish a rectangle the moment a shorter bar appears.

```python
def largest_rectangle(heights):
    stack, best = [], 0                              # stack of (start_index, height) with increasing heights
    for i, h in enumerate(heights + [0]):            # a final 0 flushes the stack
        start = i
        while stack and stack[-1][1] > h:
            index, height = stack.pop()              # this bar cannot extend further right
            best = max(best, height * (i - index))
            start = index                            # the current bar can extend back to where that bar began
        stack.append((start, h))
    return best

print(largest_rectangle([2, 1, 5, 6, 2, 3]), largest_rectangle([2, 4]), largest_rectangle([1, 1, 1, 1]))     # 10 4 4
```

(Here the best is the 5-and-6 bars at height 5: width 2, area 10.)

### Trapping rain water

```python
def trap_rain_water(heights):
    stack, water = [], 0                             # stack of indexes with decreasing heights
    for i, h in enumerate(heights):
        while stack and heights[stack[-1]] < h:
            bottom = heights[stack.pop()]
            if not stack:
                break
            width = i - stack[-1] - 1
            water += (min(heights[stack[-1]], h) - bottom) * width
        stack.append(i)
    return water
print(trap_rain_water([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]))     # 6
```

## 4. The monotonic deque: sliding-window maximum

For every window of size `k`, report the maximum. The brute force scans each window (`O(n·k)`). A **deque of indexes with decreasing values** keeps the current maximum at the front: smaller items behind a larger newcomer can never be maximum again, so they are discarded.

```python
from collections import deque

def sliding_window_max(nums, k):
    dq, result = deque(), []                         # indexes; their values decrease from front to back
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:
            dq.pop()                                 # these cannot be the max while x is in the window
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()                             # the front index slid out of the window
        if i >= k - 1:
            result.append(nums[dq[0]])               # the front is the maximum of the current window
    return result

print(sliding_window_max([1, 3, -1, -3, 5, 3, 6, 7], 3))         # [3, 3, 5, 5, 6, 7]
```

```text
nums = [1, 3, -1, -3, 5, 3, 6, 7], k = 3
window [1  3 -1]  deque of values: 3 -1        max 3
window [3 -1 -3]  deque: 3 -1 -3               max 3
window [-1 -3 5]  5 evicts the smaller ones:   max 5
```

Each index is added and removed at most once: `O(n)` total.

## 5. Simulations with queues

### Round-robin scheduling (the OS idea)

```python
def round_robin(burst_times, quantum):
    """Each process runs for `quantum` units, then goes to the back of the line if unfinished."""
    queue = deque((f"P{i + 1}", t) for i, t in enumerate(burst_times))
    clock, finish = 0, {}
    while queue:
        name, remaining = queue.popleft()
        run = min(quantum, remaining)
        clock += run
        if remaining > run:
            queue.append((name, remaining - run))        # back of the line
        else:
            finish[name] = clock
    return finish
print(round_robin([5, 3, 8], 2))                         # {'P2': 9, 'P1': 12, 'P3': 16}
```

(See [CPU scheduling](../../06-operating-systems/scheduling/README.md) for the full story.)

### The Josephus problem with a deque

```python
def josephus_deque(n, k):
    circle = deque(range(1, n + 1))
    eliminated = []
    while circle:
        circle.rotate(-(k - 1))                          # move the k-1 safe people to the back
        eliminated.append(circle.popleft())              # the next person is out
    return eliminated
print(josephus_deque(7, 3))                              # [3, 6, 2, 7, 5, 1, 4]
```

### Level-order tree traversal

```python
class Node:
    def __init__(self, val, left=None, right=None):
        self.val, self.left, self.right = val, left, right

def level_order(root):
    levels, queue = [], deque([root] if root else [])
    while queue:
        level = []
        for _ in range(len(queue)):                      # exactly the nodes of the current level
            node = queue.popleft()
            level.append(node.val)
            queue.extend(child for child in (node.left, node.right) if child)
        levels.append(level)
    return levels
tree = Node(1, Node(2, Node(4), Node(5)), Node(3, None, Node(6)))
print(level_order(tree))                                 # [[1], [2, 3], [4, 5, 6]]
```

## 6. Stack or queue? A decision guide

| Question | Stack (LIFO) | Queue (FIFO) |
|----------|--------------|--------------|
| Which item is processed next? | the **newest** | the **oldest** |
| Typical use | nesting, undo, backtracking, parsing, DFS, call stack | fairness, scheduling, buffering, BFS, streaming |
| Graph search it gives | depth-first | breadth-first (shortest paths in unweighted graphs) |
| Real-life picture | plates, Back button | line at a counter |
| Python tool | `list` | `collections.deque` |

Same problem, different data structure, different behavior: swap the stack in DFS for a queue and you get BFS:

```python
def traverse(graph, start, use_stack):
    frontier, seen, order = deque([start]), {start}, []
    while frontier:
        node = frontier.pop() if use_stack else frontier.popleft()      # the ONLY difference
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in seen:
                seen.add(neighbor)
                frontier.append(neighbor)
    return order

g = {"A": ["B", "C"], "B": ["D", "E"], "C": ["F"], "D": [], "E": [], "F": []}
print(traverse(g, "A", use_stack=True), traverse(g, "A", use_stack=False))
# ['A', 'C', 'F', 'B', 'E', 'D'] (depth-first style)   ['A', 'B', 'C', 'D', 'E', 'F'] (breadth-first, level by level)
```

## 7. Two real-world examples

**Example 1: Spreadsheet formulas.** When you type `=(B2+C2)*0.17` the spreadsheet tokenizes it, converts it to postfix with a shunting-yard parser and evaluates it with a stack for every row. The same machinery underlies calculators, SQL expression evaluators and the bytecode interpreter inside Python and Java.

**Example 2: Real-time analytics dashboards.** "Highest CPU in the last 5 minutes" recomputed every second over a stream: the monotonic deque keeps the maximum of the sliding window in `O(1)` per new sample instead of rescanning 300 values each second, which matters when monitoring thousands of servers.

## 8. Common mistakes

- Evaluating postfix operands in the wrong order (`left - right` needs the **right** operand popped first).
- Getting operator **associativity** wrong (`2^3^2`, and left-associative `-` and `/`).
- Forgetting the sentinel that flushes the stack at the end (histogram).
- Storing values instead of **indexes** in monotonic stacks when you need distances or window checks.
- Using `<` instead of `<=` (or the reverse) and mishandling equal values.
- Using a list as a queue (`pop(0)`); use `deque`.
- Believing the nested `while` inside a `for` makes it `O(n²)`: each element is popped at most once, so the total is `O(n)`.

## 9. Practice

1. Evaluate `"5 1 2 + 4 * + 3 -"` by hand with a stack, then with `eval_postfix`.
2. Convert `a + b * (c - d)` style expressions with single-digit numbers: `"1 + 2 * (3 - 1)"` to postfix and evaluate it.
3. Find, for each element, the next **smaller** element to the right.
4. Compute the **maximal rectangle area** of `[6, 2, 5, 4, 5, 1, 6]`.
5. Given a string with brackets and numbers like `"3[ab2[c]]"`, decode it (`"3[ab2[c]]"` becomes `"abccabccabcc"`).
6. Implement a stack-based **undo** for a drawing program where shapes are added and removed.
7. Use a deque to compute the minimum of every window of size `k`.

<details>
<summary>Solutions</summary>

**1.** Stack trace: push 5, 1, 2; `+` gives 3; push 4; `*` gives 12; `+` gives 5 + 12 = 17; push 3; `-` gives 14. `eval_postfix("5 1 2 + 4 * + 3 -".split())` is `14.0`.

**2.**
```python
print(to_postfix("1 + 2 * ( 3 - 1 )"), calculate("1 + 2 * ( 3 - 1 )"))      # ['1', '2', '3', '1', '-', '*', '+'] 5.0
```

**3.**
```python
def next_smaller(nums):
    answer, stack = [-1] * len(nums), []
    for i, x in enumerate(nums):
        while stack and nums[stack[-1]] > x:
            answer[stack.pop()] = x
        stack.append(i)
    return answer
print(next_smaller([4, 8, 5, 2, 25]))                    # [2, 5, 2, -1, -1]
```

**4.** `largest_rectangle([6, 2, 5, 4, 5, 1, 6])` returns `12` (height 4 across the bars 5, 4, 5 and the 2 before: width 3 x 4 = 12).

**5.**
```python
def decode(s):
    count_stack, string_stack = [], []
    current, number = "", 0
    for ch in s:
        if ch.isdigit():
            number = number * 10 + int(ch)
        elif ch == "[":
            count_stack.append(number); string_stack.append(current)       # save the outer state
            current, number = "", 0
        elif ch == "]":
            current = string_stack.pop() + current * count_stack.pop()     # repeat and attach to the outer string
        else:
            current += ch
    return current
print(decode("3[ab2[c]]"), decode("2[x]y"))              # abccabccabcc xxy
```

**6.**
```python
class Canvas:
    def __init__(self): self.shapes, self.history = [], []
    def add(self, shape):
        self.shapes.append(shape); self.history.append(("add", shape))
    def remove(self, shape):
        self.shapes.remove(shape); self.history.append(("remove", shape))
    def undo(self):
        action, shape = self.history.pop()
        if action == "add": self.shapes.remove(shape)
        else: self.shapes.append(shape)
c = Canvas(); c.add("circle"); c.add("square"); c.remove("circle")
c.undo(); print(c.shapes)                                # ['square', 'circle']
c.undo(); print(c.shapes)                                # ['circle']
```

**7.**
```python
def sliding_window_min(nums, k):
    dq, out = deque(), []
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] >= x: dq.pop()
        dq.append(i)
        if dq[0] <= i - k: dq.popleft()
        if i >= k - 1: out.append(nums[dq[0]])
    return out
print(sliding_window_min([4, 2, 12, 11, -5, 7, 8], 3))   # [2, 2, -5, -5, -5]
```

</details>

## 10. Check yourself

1. Why does postfix notation need no parentheses?
2. What does the shunting-yard algorithm do?
3. What is a monotonic stack and why is it `O(n)`?
4. How does a monotonic deque give the sliding-window maximum?
5. What is the only difference between iterative DFS and BFS?
6. Which structure does the OS ready queue resemble?

<details>
<summary>Answers</summary>

1. The order of operators and operands already encodes precedence, so a stack can evaluate it left to right.
2. It converts an infix expression to postfix using an operator stack and precedence rules.
3. A stack whose items stay sorted; each element is pushed once and popped at most once, so the total work is linear.
4. It keeps indexes in decreasing value order; smaller items behind a larger newcomer are discarded, expired indexes leave from the front, and the front is the current maximum.
5. DFS takes the newest frontier item (a stack); BFS takes the oldest (a queue).
6. A FIFO queue (round-robin ready queue), with priorities in priority-based schedulers.

</details>

[Back to stacks and queues](README.md) · Previous: [queues, deques and priority queues](02-queues-deques-priority-queues.md)
