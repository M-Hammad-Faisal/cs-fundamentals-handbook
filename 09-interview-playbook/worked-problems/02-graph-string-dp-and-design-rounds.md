# Worked Problems, Part 2: Graphs, String DP and Design-Pattern Rounds

**Prerequisites:** [ten worked interview problems](01-ten-worked-interview-problems.md) (the clarify-to-test loop and the `check` harness), [graph algorithms](../../03-algorithms/graph-algorithms/README.md), [dynamic programming](../../03-algorithms/dynamic-programming/README.md), [design patterns](../../04-oop/README.md). **You will learn:** six more walkthroughs in the same style, in the three areas interviewers return to most: **graph problems** (shortest path in an unweighted and a weighted graph, cycle detection), **dynamic programming on strings** (edit distance, longest common subsequence, longest palindromic substring), and the **object-oriented design round** (Strategy, Observer, State). Every solution is tested against an independent slow version or a known answer.

The harness again:

```python
import random, heapq, itertools
from collections import deque, defaultdict
random.seed(7)

def check(fast, slow, make_input, trials=300):
    for _ in range(trials):
        args = make_input()
        expected, got = slow(*args), fast(*args)
        assert got == expected, f"input {args}: expected {expected}, got {got}"
    return f"{trials} random tests passed"
```

# Part A: Graphs

## 1. Word Ladder (BFS = shortest path when every step costs 1)

**Problem.** Change `begin` into `end` one letter at a time; every intermediate word must be in a word list. Return the number of words in the shortest sequence, or 0.

**Clarify.** Same length words? Lowercase? Is `begin` in the list? (No need.) Must `end` be in the list? (Yes, else 0.)

**Brute force.** Try all sequences (exponential).

**Reframe.** Words are **nodes**, and two words are **neighbors** if they differ by one letter. "Fewest steps" in an unweighted graph is exactly **breadth-first search**: BFS visits nodes in order of distance.

**Bottleneck.** Finding neighbors by comparing against every word is `O(n)` per word. Instead, generate neighbors by changing each position to each letter (`26 * L` candidates) and checking a set.

```python
from string import ascii_lowercase

def ladder_length(begin, end, words):
    words = set(words)
    if end not in words:
        return 0
    queue = deque([(begin, 1)])
    seen = {begin}
    while queue:
        word, steps = queue.popleft()
        if word == end:
            return steps
        for i in range(len(word)):
            for c in ascii_lowercase:
                nxt = word[:i] + c + word[i + 1:]
                if nxt in words and nxt not in seen:
                    seen.add(nxt)
                    queue.append((nxt, steps + 1))
    return 0

print(ladder_length("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]))       # 5   hit > hot > dot > dog > cog
print(ladder_length("hit", "cog", ["hot", "dot", "dog", "lot", "log"]))              # 0   "cog" is not allowed
```

**Verify** against a Floyd-Warshall style slow solution on small random dictionaries:

```python
def ladder_slow(begin, end, words):
    if end not in set(words):                             # the spec: the end word must be in the list
        return 0
    nodes = [begin] + [w for w in set(words) if w != begin]
    INF = 10**9
    idx = {w: i for i, w in enumerate(nodes)}
    n = len(nodes)
    d = [[INF] * n for _ in range(n)]
    for i in range(n):
        d[i][i] = 0
    for a in nodes:
        for b in nodes:
            if sum(x != y for x, y in zip(a, b)) == 1:
                d[idx[a]][idx[b]] = 1
    for k in range(n):
        for i in range(n):
            for j in range(n):
                d[i][j] = min(d[i][j], d[i][k] + d[k][j])
    best = d[idx[begin]][idx[end]]
    return 0 if best >= INF else best + 1

def make_ladder():
    alphabet = "abc"
    w = lambda: "".join(random.choice(alphabet) for _ in range(3))
    return w(), w(), [w() for _ in range(random.randint(1, 12))]

print(check(ladder_length, ladder_slow, make_ladder))             # 300 random tests passed
```

**Complexity.** `O(N * L * 26)` time for `N` words of length `L`; `O(N * L)` space. **Follow-ups:** return the actual path (store parents); **bidirectional BFS** (search from both ends, meeting in the middle, much faster on large dictionaries); what if letters can also be inserted or deleted?

## 2. Network Delay Time (Dijkstra: weighted shortest path)

**Problem.** `times[i] = (u, v, w)` is a directed edge taking `w` to travel from `u` to `v`. A signal starts at node `k`. How long until all `n` nodes receive it? Return -1 if some node is unreachable.

**Pattern.** Edge weights differ, so BFS is no longer right. With **non-negative** weights, **Dijkstra** with a min-heap finds the earliest arrival at each node. The answer is the **largest** of those earliest times.

```python
def network_delay(times, n, k):
    graph = defaultdict(list)
    for u, v, w in times:
        graph[u].append((v, w))
    dist = {}
    heap = [(0, k)]
    while heap:
        d, node = heapq.heappop(heap)
        if node in dist:
            continue                                      # a shorter path already finalized this node
        dist[node] = d
        for nxt, w in graph[node]:
            if nxt not in dist:
                heapq.heappush(heap, (d + w, nxt))
    return max(dist.values()) if len(dist) == n else -1

print(network_delay([(2, 1, 1), (2, 3, 1), (3, 4, 1)], 4, 2))      # 2
print(network_delay([(1, 2, 1)], 2, 2))                            # -1   node 1 never receives the signal
```

**Verify** with Bellman-Ford (a different algorithm that tolerates any weights):

```python
def network_delay_slow(times, n, k):
    INF = float("inf")
    dist = {i: INF for i in range(1, n + 1)}
    dist[k] = 0
    for _ in range(n - 1):
        for u, v, w in times:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    worst = max(dist.values())
    return -1 if worst == INF else worst

def make_network():
    n = random.randint(1, 6)
    edges = [(random.randint(1, n), random.randint(1, n), random.randint(1, 9)) for _ in range(random.randint(0, 12))]
    return edges, n, random.randint(1, n)

print(check(network_delay, network_delay_slow, make_network))     # 300 random tests passed
```

**Complexity.** `O(E log V)`. **Follow-ups:** why does Dijkstra fail with negative edges (it finalizes a node too early; use Bellman-Ford)? How would you speed it up for one target (A* with a heuristic, stop when the target pops)? See [shortest paths](../../03-algorithms/graph-algorithms/README.md).

## 3. Detect a Cycle in a Directed Graph (DFS with three colors)

**Problem.** Does a directed graph (a build or dependency graph) contain a cycle?

**Idea.** In a DFS, a **cycle exists exactly when you reach a node that is still on the current recursion path**. Mark nodes *unvisited* (0), *in progress* (1) or *done* (2); meeting an in-progress node closes a loop. (Course Schedule in part 1 solved the same question with Kahn's algorithm.)

```python
def has_cycle(n, edges):
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
    state = [0] * n
    def visit(u):
        state[u] = 1
        for v in graph[u]:
            if state[v] == 1 or (state[v] == 0 and visit(v)):
                return True
        state[u] = 2
        return False
    return any(state[u] == 0 and visit(u) for u in range(n))

print(has_cycle(3, [(0, 1), (1, 2), (2, 0)]), has_cycle(3, [(0, 1), (1, 2), (0, 2)]))      # True False

def has_cycle_slow(n, edges):
    reach = [[i == j for j in range(n)] for i in range(n)]       # transitive closure
    for u, v in edges:
        reach[u][v] = True
    for k in range(n):
        for i in range(n):
            for j in range(n):
                reach[i][j] = reach[i][j] or (reach[i][k] and reach[k][j])
    return any(reach[u][v] and reach[v][u] and u != v for u in range(n) for v in range(n)) or any(u == v for u, v in edges)

def make_digraph():
    n = random.randint(1, 6)
    return n, [(random.randrange(n), random.randrange(n)) for _ in range(random.randint(0, 8))]

print(check(has_cycle, has_cycle_slow, make_digraph))             # 300 random tests passed
```

**Complexity.** `O(V + E)`. **Follow-up:** print the cycle (keep the path stack); undirected graphs need a different rule (a visited neighbor that is not your parent).

# Part B: Dynamic programming on strings

**The recipe** (say it aloud): define `dp[i][j]` in words, write the recurrence from the last characters, set the base cases, choose the fill order, then optimize space if asked.

## 4. Edit Distance (Levenshtein)

**Problem.** The minimum number of insertions, deletions and substitutions to turn `a` into `b`.

**State.** `dp[i][j]` = edit distance between the first `i` characters of `a` and the first `j` of `b`.

**Recurrence.** If `a[i-1] == b[j-1]`, no cost: `dp[i-1][j-1]`. Otherwise `1 +` the best of: delete (`dp[i-1][j]`), insert (`dp[i][j-1]`), substitute (`dp[i-1][j-1]`). **Base:** `dp[i][0] = i`, `dp[0][j] = j`.

```python
def edit_distance(a, b):
    prev = list(range(len(b) + 1))                        # row for i = 0
    for i in range(1, len(a) + 1):
        cur = [i] + [0] * len(b)
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                cur[j] = prev[j - 1]
            else:
                cur[j] = 1 + min(prev[j], cur[j - 1], prev[j - 1])
        prev = cur
    return prev[-1]

print(edit_distance("horse", "ros"), edit_distance("intention", "execution"), edit_distance("", "abc"))     # 3 5 3

def edit_slow(a, b):                                      # pure recursion, no memo
    if not a: return len(b)
    if not b: return len(a)
    if a[0] == b[0]: return edit_slow(a[1:], b[1:])
    return 1 + min(edit_slow(a[1:], b), edit_slow(a, b[1:]), edit_slow(a[1:], b[1:]))

def make_pair():
    s = lambda: "".join(random.choice("abc") for _ in range(random.randint(0, 6)))
    return s(), s()

print(check(edit_distance, edit_slow, make_pair))         # 300 random tests passed
```

**Complexity.** `O(len(a) * len(b))` time; `O(len(b))` space with two rows (the full table is needed only to recover the edit script). **Uses:** spell checkers, diff tools, DNA alignment.

## 5. Longest Common Subsequence

**Problem.** The length of the longest sequence of characters appearing in both strings in order (not necessarily adjacent).

**Recurrence.** `dp[i][j]`: if the last characters match, `1 + dp[i-1][j-1]`; else `max(dp[i-1][j], dp[i][j-1])`.

```python
def lcs(a, b):
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            dp[i][j] = dp[i - 1][j - 1] + 1 if a[i - 1] == b[j - 1] else max(dp[i - 1][j], dp[i][j - 1])
    return dp[-1][-1]

print(lcs("abcde", "ace"), lcs("abc", "def"))             # 3 0

def lcs_slow(a, b):                                       # try every subsequence of a
    best = 0
    for mask in range(1 << len(a)):
        sub = [a[i] for i in range(len(a)) if mask >> i & 1]
        it = iter(b)
        if all(ch in it for ch in sub):                   # is `sub` a subsequence of b?
            best = max(best, len(sub))
    return best

print(check(lcs, lcs_slow, lambda: tuple("".join(random.choice("abc") for _ in range(random.randint(0, 7))) for _ in range(2)), trials=200))    # 200 random tests passed
```

**Complexity.** `O(nm)`. **Follow-ups:** recover the subsequence itself (walk the table backward); relate it to edit distance with only insert and delete (`n + m - 2 * LCS`); diff tools are built on this.

## 6. Longest Palindromic Substring (expand around the center)

**Problem.** Return the longest substring that reads the same forward and backward.

**Brute force.** Check every substring: `O(n^3)`. **Better insight:** every palindrome has a **center** (a character or a gap between two). Expand outward from each of the `2n - 1` centers while the ends match: `O(n^2)` with `O(1)` space (simpler than a DP table, and the one to write in an interview).

```python
def longest_palindrome(s):
    best = ""
    for center in range(2 * len(s) - 1):
        lo, hi = center // 2, center // 2 + center % 2
        while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
            lo -= 1; hi += 1
        if hi - lo - 1 > len(best):
            best = s[lo + 1:hi]
    return best

print(longest_palindrome("babad"), longest_palindrome("cbbd"), repr(longest_palindrome("")))     # bab bb ''

def lp_slow_len(s):
    return max((j - i for i in range(len(s)) for j in range(i + 1, len(s) + 1) if s[i:j] == s[i:j][::-1]), default=0)

for _ in range(300):
    t = "".join(random.choice("ab") for _ in range(random.randint(0, 10)))
    r = longest_palindrome(t)
    assert r == r[::-1] and len(r) == lp_slow_len(t) and r in t
print("300 random tests passed")                           # 300 random tests passed
```

(There may be several answers of the same length, so the test checks that the result is a palindrome, appears in the string and has the maximum length. **Manacher's algorithm** does it in `O(n)`: mention it as a follow-up.)

# Part C: The design-pattern round

Here you are graded on **naming responsibilities and extension points**, not on cleverness. Pattern for the answer: *list requirements, name the variations that will change, put each behind an interface, then show how a new requirement is added without editing old code.* See [OOP and design patterns](../../04-oop/README.md).

## 7. Parking Lot Fees (Strategy: swap an algorithm)

**Problem.** Different lots charge differently: hourly, flat per day, or free for the first 30 minutes. Add new pricing rules without touching the lot's code.

**Varying part:** pricing. Put it behind a one-method interface (**Strategy**), and inject it.

```python
from typing import Protocol
from math import ceil

class Pricing(Protocol):
    def fee(self, minutes: int) -> float: ...

class Hourly:
    def __init__(self, rate): self.rate = rate
    def fee(self, minutes): return ceil(minutes / 60) * self.rate

class DailyCap:
    def __init__(self, rate, cap): self.rate, self.cap = rate, cap
    def fee(self, minutes): return min(ceil(minutes / 60) * self.rate, self.cap)

class FreeFirst30(Hourly):
    def fee(self, minutes): return 0 if minutes <= 30 else super().fee(minutes)

class ParkingLot:
    def __init__(self, pricing: Pricing):
        self.pricing = pricing
    def checkout(self, minutes): return self.pricing.fee(minutes)

for p in (Hourly(3), DailyCap(3, 20), FreeFirst30(3)):
    print(type(p).__name__, ParkingLot(p).checkout(25), ParkingLot(p).checkout(600))
# Hourly 3 30
# DailyCap 3 20
# FreeFirst30 0 30
```

A new rule (night rate, EV discount) is a **new class**; `ParkingLot` never changes: the **Open/Closed principle**. **Follow-ups:** combine rules (Decorator or a list of rules), choose the strategy by vehicle type (a factory).

## 8. Notification Hub (Observer: one event, many listeners)

**Problem.** When an order ships, email the customer, update analytics and notify the warehouse, and teams will add more reactions later. The order code must not know who is listening.

```python
class EventBus:
    def __init__(self):
        self.handlers = defaultdict(list)
    def subscribe(self, event, handler):
        self.handlers[event].append(handler)
    def publish(self, event, **data):
        for handler in self.handlers[event]:
            handler(**data)

bus, log = EventBus(), []
bus.subscribe("shipped", lambda order_id, **_: log.append(f"email for {order_id}"))
bus.subscribe("shipped", lambda order_id, **_: log.append(f"analytics for {order_id}"))

def ship(order_id):
    bus.publish("shipped", order_id=order_id)               # the order code knows only the event, not the listeners

ship(42)
print(log)                                                  # ['email for 42', 'analytics for 42']
bus.subscribe("shipped", lambda order_id, **_: log.append(f"warehouse for {order_id}"))
ship(43)
print(log[-3:])                                             # ['email for 43', 'analytics for 43', 'warehouse for 43']
```

**Follow-ups interviewers ask:** what if a handler raises (isolate failures so others still run)? Ordering and asynchronous delivery (queues)? Memory leaks from handlers never unsubscribed? Moving to a message broker when listeners live in other services.

## 9. Vending Machine (State: behaviour depends on the current state)

**Problem.** A machine that is *idle*, *has money* or *dispensing* reacts differently to the same actions (insert coin, select, refund). Avoid a giant `if state == ...` in every method.

```python
class Idle:
    def insert(self, m):  m.credit += 1; m.state = HasMoney(); return "coin accepted"
    def select(self, m):  return "insert a coin first"
    def refund(self, m):  return "nothing to refund"

class HasMoney:
    def insert(self, m):  m.credit += 1; return "coin accepted"
    def select(self, m):
        if m.stock == 0: return "sold out"
        m.stock -= 1; m.credit -= 1
        m.state = HasMoney() if m.credit else Idle()
        return "dispensed"
    def refund(self, m):
        n, m.credit, m.state = m.credit, 0, Idle()
        return f"refunded {n}"

class Machine:
    def __init__(self, stock):
        self.stock, self.credit, self.state = stock, 0, Idle()
    def insert(self): return self.state.insert(self)
    def select(self): return self.state.select(self)
    def refund(self): return self.state.refund(self)

m = Machine(stock=1)
print(m.select(), "|", m.insert(), "|", m.insert(), "|", m.select(), "|", m.refund())
# insert a coin first | coin accepted | coin accepted | dispensed | refunded 1
print(m.insert(), "|", m.select())                          # coin accepted | sold out
```

Each state is a class that knows what each action means *in that state*; adding a "maintenance" state is a new class. **Follow-ups:** draw the state diagram ([UML lesson](../../04-oop/01-uml-and-class-diagrams.md)); the same idea in a TCP connection (`LISTEN`, `ESTABLISHED`, ...).

## 10. Which pattern? A recognition table

| Requirement says | Pattern | Smell it fixes |
|------------------|---------|----------------|
| "swap the algorithm / pricing / sorting rule" | **Strategy** | `if kind == ...` chains |
| "when X happens, several things must react" | **Observer** | the source knowing all its listeners |
| "behaviour depends on the current mode" | **State** | the same `if state` in every method |
| "create objects without naming the class" | **Factory** | `new ConcreteClass` spread everywhere |
| "add features by wrapping" (logging, caching, compression) | **Decorator** | subclass explosion |
| "exactly one shared instance" | **Singleton** (use sparingly) | globals; prefer passing a dependency |
| "make an old interface fit a new one" | **Adapter** | rewriting working third-party code |
| "undo, queue or log operations" | **Command** | actions hard-coded to buttons |

## 11. Common mistakes

- **BFS:** marking nodes as visited when *popped* instead of when *pushed* (duplicates explode the queue); forgetting the start node's distance.
- **Dijkstra:** using it with negative edges; not skipping stale heap entries.
- **Cycle detection:** using a simple visited set in a *directed* graph (a node reached twice by different paths is not a cycle).
- **String DP:** off-by-one between the string index and the table index (`a[i-1]` versus `dp[i]`); forgetting the empty-prefix base case.
- **Design rounds:** coding immediately instead of listing requirements; building a pattern nobody asked for; no answer to "how would you add a new case?".

## 12. Practice

1. In Word Ladder, why do we mark a word `seen` when we enqueue it, not when we dequeue it?
2. Modify `ladder_length` to return the actual shortest path.
3. A grid has walls; find the shortest path from the top-left to the bottom-right corner (4 directions). Which algorithm?
4. Compute `edit_distance("kitten", "sitting")` and say which three operations produce it.
5. Show that `edit_distance` using only insertions and deletions equals `len(a) + len(b) - 2 * lcs(a, b)`.
6. Add a `WeekendSurcharge` pricing to the parking lot without editing `ParkingLot`.
7. Which pattern models "undo" in an editor, and what must each action store?

<details>
<summary>Solutions</summary>

1. Marking on enqueue guarantees each word enters the queue **once**; marking on dequeue lets the same word be queued many times by different neighbors, wasting time and memory (the distances stay correct, but the queue can blow up).
2. ```python
   def ladder_path(begin, end, words):
       words = set(words)
       if end not in words:
           return []
       parent, queue = {begin: None}, deque([begin])
       while queue:
           word = queue.popleft()
           if word == end:
               path = []
               while word is not None:
                   path.append(word); word = parent[word]
               return path[::-1]
           for i in range(len(word)):
               for c in ascii_lowercase:
                   nxt = word[:i] + c + word[i + 1:]
                   if nxt in words and nxt not in parent:
                       parent[nxt] = word
                       queue.append(nxt)
       return []

   print(ladder_path("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]))      # ['hit', 'hot', 'dot', 'dog', 'cog']
   ```
3. **BFS** on the grid: each move costs 1, so BFS gives the shortest path (use A* with Manhattan distance for speed on large grids).
4. ```python
   print(edit_distance("kitten", "sitting"))                # 3
   ```
   Substitute k to s, substitute e to i, insert g at the end.
5. ```python
   def lcs_edit(a, b): return len(a) + len(b) - 2 * lcs(a, b)
   for _ in range(200):
       x, y = make_pair()
       # insert/delete-only distance via DP
       dp = [[0] * (len(y) + 1) for _ in range(len(x) + 1)]
       for i in range(len(x) + 1):
           for j in range(len(y) + 1):
               if i == 0: dp[i][j] = j
               elif j == 0: dp[i][j] = i
               elif x[i-1] == y[j-1]: dp[i][j] = dp[i-1][j-1]
               else: dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1])
       assert dp[-1][-1] == lcs_edit(x, y)
   print("identity holds")                                   # identity holds
   ```
   Intuition: keep the LCS characters, delete everything else from `a`, and insert everything else of `b`.
6. ```python
   class WeekendSurcharge:
       def __init__(self, inner, extra): self.inner, self.extra = inner, extra
       def fee(self, minutes): return self.inner.fee(minutes) + self.extra
   print(ParkingLot(WeekendSurcharge(Hourly(3), 5)).checkout(25))       # 8
   ```
7. **Command**: every action is an object with `do()` and `undo()`; the editor keeps a stack of executed commands, and each command stores what it needs to reverse itself (for example the deleted text and its position).

</details>

## 13. Check yourself

1. Why is BFS correct for shortest paths in an unweighted graph, and what replaces it for weighted graphs?
2. What is the key invariant of Dijkstra's algorithm, and which input breaks it?
3. How does DFS detect a cycle in a directed graph?
4. State the edit-distance recurrence and its base cases.
5. What is the relationship between LCS and edit distance?
6. Why expanding around centers for palindromes, and what is the complexity?
7. Strategy versus State: how do they differ?
8. How do you answer "how would you add a new case?" in a design round?

<details>
<summary>Answers</summary>

1. BFS visits nodes in increasing number of edges from the start, so the first time it reaches a node is by a shortest path; weighted graphs use Dijkstra (non-negative) or Bellman-Ford (any weights).
2. When a node is popped from the heap its distance is final, because all remaining paths are at least as long; negative edges break this.
3. A cycle exists if the DFS meets a node that is still on the current path (an "in progress" node).
4. Equal last characters: `dp[i-1][j-1]`; otherwise `1 + min(delete, insert, substitute)`; `dp[i][0] = i`, `dp[0][j] = j`.
5. With only insertions and deletions the distance is `n + m - 2 * LCS`.
6. Every palindrome has a center (2n-1 choices); expanding is `O(n)` per center, `O(n^2)` total, with constant space.
7. Strategy: the client picks one interchangeable algorithm. State: the object changes its own behavior by switching between state objects as events occur.
8. Show that the new case is a **new class or handler behind an existing interface**, with no edits to the stable code (Open/Closed).

</details>

[Back to worked problems](README.md)
