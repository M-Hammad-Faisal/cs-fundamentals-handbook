# Linked Lists

## Detailed lessons (start here if you are new)

1. [Singly linked list](01-singly-linked-list.md): nodes, operations, traces
2. [Doubly and circular lists](02-doubly-and-circular.md): sentinels, Josephus, LRU cache
3. [Linked list techniques](03-linked-list-techniques.md): dummy node, reversal, Floyd cycle detection, merging

The rest of this page is the quick reference.

## 1. The concept

A **linked list** stores elements in separate **nodes**. Each node holds a value and a **pointer** (reference) to the next node. Nodes can live anywhere in memory; the pointers connect them.

```
head -> [10 | •]-> [20 | •]-> [30 | •]-> None
```

Compared with an array, a linked list trades fast indexing for cheap insertion and deletion once you hold a reference to the right node.

### Types

| Type | Structure | Notes |
|------|-----------|-------|
| **Singly linked** | `node -> next` | Simplest; traverse one way |
| **Doubly linked** | `prev <- node -> next` | Traverse both ways; `O(1)` delete given the node |
| **Circular** | Last node points back to the first | Round-robin schedulers, ring buffers |

## 2. How it works

```python
class Node:
    def __init__(self, value, next=None):
        self.value = value
        self.next = next

class LinkedList:
    def __init__(self):
        self.head = None
        self.size = 0

    def push_front(self, value):            # O(1)
        self.head = Node(value, self.head)
        self.size += 1

    def push_back(self, value):             # O(n) without a tail pointer
        node = Node(value)
        if not self.head:
            self.head = node
        else:
            cur = self.head
            while cur.next:
                cur = cur.next
            cur.next = node
        self.size += 1

    def find(self, value):                  # O(n)
        cur = self.head
        while cur:
            if cur.value == value:
                return cur
            cur = cur.next
        return None

    def delete(self, value):                # O(n)
        dummy = Node(None, self.head)       # dummy node removes head special case
        prev, cur = dummy, self.head
        while cur:
            if cur.value == value:
                prev.next = cur.next
                self.size -= 1
                break
            prev, cur = cur, cur.next
        self.head = dummy.next

    def __iter__(self):
        cur = self.head
        while cur:
            yield cur.value
            cur = cur.next
```

### Complexity

| Operation | Singly | Doubly (with tail) | Array |
|-----------|--------|--------------------|-------|
| Access by index | `O(n)` | `O(n)` | `O(1)` |
| Insert/delete at head | `O(1)` | `O(1)` | `O(n)` |
| Insert at tail | `O(n)` (or `O(1)` with tail pointer) | `O(1)` | `O(1)` amortized |
| Delete a known node | `O(n)` (need previous) | `O(1)` | `O(n)` |
| Search | `O(n)` | `O(n)` | `O(n)` |
| Memory per item | value + 1 pointer | value + 2 pointers | value only |

Linked lists are poor for caching: nodes are scattered, so the CPU cannot prefetch neighbours. In practice arrays often beat linked lists even for operations that look better on paper.

## 3. Essential techniques

### Dummy (sentinel) node

Create a fake node before the head so inserting or deleting at the head needs no special case (used in `delete` above).

### Reverse a list

```python
def reverse(head):
    prev = None
    cur = head
    while cur:
        nxt = cur.next          # remember the rest
        cur.next = prev         # flip the pointer
        prev, cur = cur, nxt
    return prev                 # O(n) time, O(1) space
```

### Slow and fast pointers (Floyd's tortoise and hare)

```python
def middle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow                 # slow is at the middle

def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False                # O(n) time, O(1) space
```

If a cycle exists, the fast pointer eventually laps the slow one. To find where the cycle starts, reset one pointer to the head after they meet, then move both one step at a time; they meet at the cycle start.

### Merge two sorted lists

```python
def merge(a, b):
    dummy = tail = Node(None)
    while a and b:
        if a.value <= b.value:
            tail.next, a = a, a.next
        else:
            tail.next, b = b, b.next
        tail = tail.next
    tail.next = a or b
    return dummy.next
```

### Remove the n-th node from the end

```python
def remove_nth_from_end(head, n):
    dummy = Node(None, head)
    fast = slow = dummy
    for _ in range(n):
        fast = fast.next
    while fast.next:
        fast, slow = fast.next, slow.next
    slow.next = slow.next.next
    return dummy.next
```

### Doubly linked list node (for LRU caches)

```python
class DNode:
    def __init__(self, key=None, value=None):
        self.key, self.value = key, value
        self.prev = self.next = None
```

## 4. Two real-world examples

### Example 1: LRU cache

A least-recently-used cache needs `O(1)` get, put, and evict-oldest. Combine a **hash map** (key to node) with a **doubly linked list** ordered by recency. Accessing a key moves its node to the front in `O(1)` because a doubly linked list can unlink a node it already holds. Evicting removes the tail. Redis-like caches, browser caches and database buffer pools use this idea. (Python's `collections.OrderedDict` implements it internally.)

### Example 2: Undo history and music playlists

A text editor's undo/redo stack and a music player's "previous/next" both walk a sequence in two directions and insert or remove items next to the current position, a natural fit for a doubly linked list. Operating-system **free lists** (tracking free memory blocks) and **hash-table chaining** also use linked nodes because they insert and remove frequently without needing random access.

## 5. Tips, tricks and pitfalls

- **Draw it.** Sketch nodes and arrows; most pointer bugs vanish on paper.
- **Order of pointer updates matters.** Save `next` before overwriting it (see `reverse`).
- **Guard `None`.** Always check `node` and `node.next` before dereferencing.
- **Use a dummy head** to remove edge cases for empty lists and head operations.
- **Fast/slow pointers** solve middle, cycle, and "k-th from end" problems in one pass.
- **Cycles cause infinite loops.** If a traversal hangs, suspect a cycle.
- **Python rarely needs a hand-rolled linked list.** Use `list` or `collections.deque` unless you need `O(1)` splice/delete of known nodes. Know the structure for interviews and for understanding other structures built on it.
- **Recursion on long lists** can hit the recursion limit; prefer iteration.

## 6. Check yourself

1. Why is access by index `O(n)` in a linked list but `O(1)` in an array?
2. Why can a doubly linked list delete a known node in `O(1)` while a singly linked list cannot?
3. How does the slow/fast pointer technique detect a cycle and why is it `O(1)` space?
4. What problem does a dummy head node solve?
5. Why might an array be faster than a linked list in practice despite equal Big-O?
6. Which two structures combine to build an `O(1)` LRU cache, and why?

<details>
<summary>Answers</summary>

1. The array computes the address directly; a linked list must follow pointers from the head.
2. A doubly linked node knows its `prev`, so it can relink neighbours directly. A singly linked list needs the previous node, found by an `O(n)` scan.
3. Fast moves two steps, slow one; inside a cycle fast gains one step per iteration and must meet slow. Only two pointers are stored.
4. It removes the special case for inserting/deleting at the head and for empty lists.
5. Arrays have better cache locality and less per-element overhead; linked nodes are scattered in memory.
6. A hash map for `O(1)` lookup and a doubly linked list for `O(1)` reordering and eviction.

</details>
