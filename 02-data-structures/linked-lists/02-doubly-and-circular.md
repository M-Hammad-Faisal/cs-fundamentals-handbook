# Doubly Linked Lists, Circular Lists and the LRU Cache

**Prerequisites:** [the singly linked list](01-singly-linked-list.md). **You will learn:** why a second pointer (`prev`) makes deletion and reverse traversal easy, how sentinel (dummy) nodes remove edge cases, how circular lists work, and how a **doubly linked list plus a dictionary** builds an `O(1)` **LRU cache**, one of the most common real-world and interview structures.

## 1. In plain words

A singly linked list only knows "who comes next". Its weakness: to delete a node you need the node **before** it, and finding that costs `O(n)`. A **doubly linked list** gives every node **two pointers**: `next` (forward) and `prev` (backward). Like a train where each carriage is coupled to both neighbors, you can walk either way and unhook any carriage you are standing in.

```text
        head                                                           tail
         │                                                              │
         ▼                                                              ▼
 None ◄─ [prev|10|next] ⇄ [prev|20|next] ⇄ [prev|30|next] ⇄ [prev|40|next] ─► None
```

| | Singly | Doubly |
|--|--------|--------|
| Pointers per node | 1 | 2 (more memory) |
| Traverse backward | impossible | `O(n)` easily |
| Delete a given node | `O(n)` (need the previous) | **`O(1)`** |
| Insert before a given node | `O(n)` | **`O(1)`** |
| Delete the last node | `O(n)` | **`O(1)`** (with a tail pointer) |

## 2. A doubly linked list with sentinels

**Sentinel nodes** are two dummy nodes (`head` and `tail`) that never hold data. They guarantee every real node always has a node on both sides, so insert/remove code needs **no special cases** for the ends or an empty list.

```text
 [HEAD sentinel] ⇄ [10] ⇄ [20] ⇄ [30] ⇄ [TAIL sentinel]       an empty list is just  [HEAD] ⇄ [TAIL]
```

```python
class DNode:
    def __init__(self, value=None):
        self.value = value
        self.prev = None
        self.next = None

class DoublyLinkedList:
    def __init__(self):
        self.head = DNode()                  # sentinel
        self.tail = DNode()                  # sentinel
        self.head.next, self.tail.prev = self.tail, self.head
        self._size = 0

    def __len__(self):
        return self._size

    def __iter__(self):                      # forward
        node = self.head.next
        while node is not self.tail:
            yield node.value
            node = node.next

    def reversed(self):                      # backward: only possible because of `prev`
        node = self.tail.prev
        while node is not self.head:
            yield node.value
            node = node.prev

    def __repr__(self):
        return " <-> ".join(map(repr, self)) if self._size else "empty"

    # Insert a new node right BEFORE `node`: 4 pointer assignments, O(1)
    def _insert_before(self, node, value):
        new = DNode(value)
        new.prev, new.next = node.prev, node
        node.prev.next = new
        node.prev = new
        self._size += 1
        return new

    # Unlink a node from the list: 2 pointer assignments, O(1)
    def _unlink(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev
        node.prev = node.next = None
        self._size -= 1
        return node.value

    def append(self, value):                 # O(1): insert before the tail sentinel
        return self._insert_before(self.tail, value)

    def prepend(self, value):                # O(1): insert before the first real node
        return self._insert_before(self.head.next, value)

    def pop(self):                           # O(1) (this was O(n) in the singly linked list)
        if not self._size:
            raise IndexError("pop from empty list")
        return self._unlink(self.tail.prev)

    def pop_front(self):                     # O(1)
        if not self._size:
            raise IndexError("pop from empty list")
        return self._unlink(self.head.next)

    def remove_node(self, node):             # O(1) when you already hold the node
        return self._unlink(node)

d = DoublyLinkedList()
for v in (20, 30, 40):
    d.append(v)
d.prepend(10)
print(d, len(d), list(d.reversed()))         # 10 <-> 20 <-> 30 <-> 40 4 [40, 30, 20, 10]
print(d.pop(), d.pop_front(), d)             # 40 10 20 <-> 30
node_30 = d._insert_before(d.tail, 99)       # keep a handle on a node
print(d.remove_node(node_30), d)             # 99 20 <-> 30
```

### Why `_unlink` is `O(1)`: the trace

```text
Unlink node B:      A ⇄ B ⇄ C

 B.prev.next = B.next      A.next  ──►  C         (A skips B going forward)
 B.next.prev = B.prev      C.prev  ──►  A         (C skips B going backward)

 result:             A ⇄ C            (B has no references left from the list: freed)
```

No walking is needed because B knows both of its neighbors.

## 3. Circular linked lists

In a **circular** list the last node points back to the first, so the chain forms a loop with no `None` end. A pointer can keep moving forever: perfect for things that **repeat in turns**.

```text
        ┌──────────────────────────────┐
        ▼                              │
       [A] ──► [B] ──► [C] ──► [D] ────┘        (last.next = first)
```

```python
class CircularList:
    """A circular singly linked list with a single 'cursor' pointing at the current item."""
    def __init__(self, items=()):
        self.last = None                     # we keep a pointer to the LAST node; last.next is the first
        for x in items:
            self.append(x)

    def append(self, value):
        new = Node2(value)
        if self.last is None:
            new.next = new                   # a single node points to itself
        else:
            new.next = self.last.next        # new points to the first node
            self.last.next = new
        self.last = new

    def rotate(self):                        # advance the "current" position by one: O(1)
        if self.last:
            self.last = self.last.next

    def current(self):
        return self.last.next.value if self.last else None

    def __iter__(self):                      # one full lap
        if self.last is None:
            return
        node = self.last.next
        while True:
            yield node.value
            if node is self.last:
                break
            node = node.next

class Node2:
    def __init__(self, value):
        self.value, self.next = value, None

players = CircularList(["Ana", "Bo", "Cy"])
turns = []
for _ in range(7):                           # round robin: Ana, Bo, Cy, Ana, Bo, Cy, Ana ...
    turns.append(players.current())
    players.rotate()
print(turns, list(players))                  # ['Ana', 'Bo', 'Cy', 'Ana', 'Bo', 'Cy', 'Ana'] ['Bo', 'Cy', 'Ana']
```

**Uses:** round-robin scheduling (the OS gives each process a time slice in turn: [scheduling](../../06-operating-systems/scheduling/README.md)), turn-based games, a music player on repeat, ring buffers, the Josephus problem. **Danger:** loops over a circular list never end unless you stop after one lap.

The **Josephus problem** (people in a circle, every k-th is eliminated) is a classic use:

```python
def josephus(n, k):
    people = list(range(1, n + 1))
    index, order = 0, []
    while people:
        index = (index + k - 1) % len(people)       # moving around a circle with modulo
        order.append(people.pop(index))
    return order
print(josephus(7, 3))                        # [3, 6, 2, 7, 5, 1, 4]
```

## 4. Project: an O(1) LRU cache

**LRU (Least Recently Used) cache:** a fixed-capacity store that, when full, **evicts the item that has not been used for the longest time**. It is everywhere: CPU caches, browsers, CDNs, databases, `functools.lru_cache`.

Requirements: `get(key)` and `put(key, value)` both in **`O(1)`**, and "mark as recently used" on every access.

**Design:** combine two structures.

1. A **dictionary** `key -> node` for `O(1)` lookup.
2. A **doubly linked list** ordering the nodes from **most recently used (front)** to **least recently used (back)**, so moving a node to the front and evicting from the back are both `O(1)` (this is exactly why we need `prev` pointers).

```text
 dict:  { "a": ●, "b": ●, "c": ● }            (each ● points to a node in the list)
 list:  [HEAD] ⇄ (c) ⇄ (a) ⇄ (b) ⇄ [TAIL]      front = most recent, back = least recent
 get("a"): move (a) to the front       put("d") when full: evict (b) from the back
```

```python
class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.nodes = {}                              # key -> DNode  (O(1) lookup)
        self.order = DoublyLinkedList()              # front = most recently used, back = least recently used

    def get(self, key):
        node = self.nodes.get(key)
        if node is None:
            return None
        self._touch(node)                            # mark as most recently used
        return node.value[1]                         # we store (key, value) in each node

    def put(self, key, value):
        node = self.nodes.get(key)
        if node is not None:                         # update an existing key
            node.value = (key, value)
            self._touch(node)
            return
        if len(self.nodes) >= self.capacity:         # full: evict the least recently used (the back)
            evicted_key, _ = self.order.pop()
            del self.nodes[evicted_key]
        self.nodes[key] = self.order.prepend((key, value))

    def _touch(self, node):                          # move a node to the front in O(1)
        self.order.remove_node(node)
        new_node = self.order.prepend(node.value)
        self.nodes[node.value[0]] = new_node

    def keys_by_recency(self):
        return [k for k, _ in self.order]            # most recent first

cache = LRUCache(3)
cache.put("a", 1); cache.put("b", 2); cache.put("c", 3)
print(cache.keys_by_recency())                       # ['c', 'b', 'a']
cache.get("a")                                       # use "a": it becomes the most recent
print(cache.keys_by_recency())                       # ['a', 'c', 'b']
cache.put("d", 4)                                    # cache is full: evicts the least recently used key, "b"
print(cache.keys_by_recency(), cache.get("b"), cache.get("d"))      # ['d', 'a', 'c'] None 4
cache.put("c", 30)                                   # update moves "c" to the front
print(cache.keys_by_recency(), cache.get("c"))       # ['c', 'd', 'a'] 30
```

(Python's `collections.OrderedDict` has `move_to_end` and `popitem(last=False)`, so a production-quality LRU is about ten lines; and `functools.lru_cache` is built in. Writing it by hand shows why the doubly linked list matters.)

```python
from collections import OrderedDict

class LRUCacheShort:
    def __init__(self, capacity):
        self.capacity, self.data = capacity, OrderedDict()
    def get(self, key):
        if key not in self.data: return None
        self.data.move_to_end(key)
        return self.data[key]
    def put(self, key, value):
        self.data[key] = value
        self.data.move_to_end(key)
        if len(self.data) > self.capacity:
            self.data.popitem(last=False)

short = LRUCacheShort(2)
short.put(1, "one"); short.put(2, "two"); short.get(1); short.put(3, "three")
print(list(short.data))                              # [1, 3]   (2 was the least recently used)
```

## 5. Comparison and when to choose which

| Need | Choose |
|------|--------|
| Fast random access, appends | array / `list` |
| Fast queue operations at both ends | `collections.deque` (blocks of arrays, not pointer nodes) |
| Remove/insert in the middle given a node, in `O(1)` | doubly linked list |
| Round-robin / cyclic iteration | circular list |
| Least-recently-used eviction | doubly linked list + dict (or `OrderedDict`) |
| Minimal memory, forward-only | singly linked list |

Python's standard library does **not** include a linked list; `deque` covers most needs. Linked lists are mostly a teaching structure and an ingredient of other structures (LRU caches, hash-table chains, free lists in memory allocators, OS run queues).

## 6. Two real-world examples

**Example 1: Browser history.** Each page visit is a node in a doubly linked list; "Back" follows `prev`, "Forward" follows `next`; visiting a new page after going back **discards** the forward nodes. Both directions in `O(1)` is the whole point.

```python
class BrowserHistory:
    def __init__(self, home):
        self.pages = [home]; self.index = 0
    def visit(self, url):
        self.pages = self.pages[:self.index + 1] + [url]       # drop the forward history
        self.index += 1
    def back(self, steps=1):
        self.index = max(0, self.index - steps); return self.pages[self.index]
    def forward(self, steps=1):
        self.index = min(len(self.pages) - 1, self.index + steps); return self.pages[self.index]
h = BrowserHistory("home"); h.visit("a"); h.visit("b"); h.visit("c")
print(h.back(), h.back(), h.forward(), h.visit("d"), h.forward())          # b a b None d
```

**Example 2: Operating-system scheduling and memory.** A kernel keeps processes waiting to run in a circular or doubly linked ready queue (O(1) removal when a process blocks or exits) and tracks free memory blocks in linked free lists. Linux's `list_head` doubly linked list is embedded in thousands of kernel structures.

## 7. Common mistakes

- Forgetting to update **both** pointers when inserting or removing (leaving a one-way inconsistent link).
- Linking in the wrong order and losing a node.
- Leaving stale `prev`/`next` references on removed nodes (keeps garbage alive and invites bugs).
- Not using sentinels and writing four special cases (empty, head, tail, single).
- An infinite loop on a circular list (stop after one lap or track the start).
- Forgetting to remove the evicted key from the dictionary in an LRU cache.
- Choosing a linked list when a `list` or `deque` would be simpler and faster.

## 8. Practice

1. Add `insert_after(node, value)` and `index_of(value)` to `DoublyLinkedList`.
2. Write `reverse()` for the doubly linked list in `O(n)` by swapping `prev` and `next` on every node.
3. Implement a `Deque` class on top of `DoublyLinkedList` with `push_front`, `push_back`, `pop_front`, `pop_back`, all `O(1)`.
4. Use the circular list to simulate a "hot potato" game (pass the potato `k` times, then eliminate that player, repeat).
5. Extend `LRUCache` to count hits and misses and report the hit ratio for a sequence of requests.
6. Why can't an LRU cache be built efficiently with only a singly linked list?

<details>
<summary>Solutions</summary>

**1.**
```python
def insert_after(self, node, value):
    return self._insert_before(node.next, value)
def index_of(self, value):
    for i, v in enumerate(self):
        if v == value: return i
    return -1
DoublyLinkedList.insert_after, DoublyLinkedList.index_of = insert_after, index_of
d2 = DoublyLinkedList(); first = d2.append(1); d2.append(3); d2.insert_after(first, 2)
print(d2, d2.index_of(3))                              # 1 <-> 2 <-> 3 2
```

**2.**
```python
def reverse(self):
    node = self.head
    while node:
        node.prev, node.next = node.next, node.prev    # swap the two pointers on every node (including sentinels)
        node = node.prev                               # the old next is now in prev
    self.head, self.tail = self.tail, self.head
DoublyLinkedList.reverse = reverse
d3 = DoublyLinkedList()
for v in (1, 2, 3): d3.append(v)
d3.reverse(); print(d3)                                # 3 <-> 2 <-> 1
```

**3.**
```python
class Deque:
    def __init__(self): self._list = DoublyLinkedList()
    def push_front(self, x): self._list.prepend(x)
    def push_back(self, x): self._list.append(x)
    def pop_front(self): return self._list.pop_front()
    def pop_back(self): return self._list.pop()
    def __len__(self): return len(self._list)
q = Deque(); q.push_back(1); q.push_back(2); q.push_front(0)
print(q.pop_front(), q.pop_back(), len(q))              # 0 2 1
```

**4.**
```python
def hot_potato(names, passes):
    circle = list(names); i = 0; out = []
    while len(circle) > 1:
        i = (i + passes) % len(circle)
        out.append(circle.pop(i))
        i %= max(1, len(circle))
    return out, circle[0]
print(hot_potato(["Ana", "Bo", "Cy", "Di", "Ed"], 3))   # (['Di', 'Cy', 'Ed', 'Bo'], 'Ana')
```

**5.**
```python
class CountingLRU(LRUCache):
    hits = misses = 0
    def get(self, key):
        value = super().get(key)
        if value is None: self.misses += 1
        else: self.hits += 1
        return value
c = CountingLRU(2)
c.put(1, "a"); c.put(2, "b")
for k in (1, 2, 3, 1, 2): c.get(k)
print(c.hits, c.misses, c.hits / (c.hits + c.misses))   # 4 1 0.8
```

**6.** Moving a node to the front and evicting from the back both require the **previous** node (to re-link around the node). In a singly linked list finding it is `O(n)`; with `prev` pointers (doubly linked list) it is `O(1)`.

</details>

## 9. Check yourself

1. What advantage does `prev` give?
2. What is a sentinel node and why use one?
3. What is the structure of a circular linked list and a typical use?
4. Why does an LRU cache use both a dictionary and a doubly linked list?
5. What is the order of the four pointer assignments when inserting before a node?

<details>
<summary>Answers</summary>

1. Backward traversal and `O(1)` deletion/insertion around a known node (you do not need to search for the previous node).
2. A dummy node at each end that holds no data; it removes special cases for empty lists and the first/last positions.
3. The last node points to the first, forming a loop; used for round-robin scheduling, turn-taking, ring buffers.
4. The dictionary gives `O(1)` lookup of a node by key; the list keeps recency order and allows `O(1)` move-to-front and evict-from-back.
5. Set the new node's `prev` and `next`, then point the neighbor's `next` to the new node, then the next node's `prev` to the new node: link the new node outward first, then the neighbors inward.

</details>

[Back to linked lists](README.md) · Previous: [singly linked list](01-singly-linked-list.md) · Next: [linked-list techniques](03-linked-list-techniques.md)
