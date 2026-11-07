# The Singly Linked List, Built from Scratch

**Prerequisites:** [classes first look](../../00-foundations/python-fundamentals/07-classes-first-look.md), [references and memory](../../00-foundations/computer-basics/memory-stack-heap.md), [arrays and memory](../arrays-strings/01-arrays-and-memory.md). **You will learn:** what a linked list is, how nodes and pointers work, how to implement every operation (append, prepend, insert, delete, search, traverse) with traces and complexity, and when a linked list beats an array (and when it does not).

## 1. In plain words

An array keeps items in neighboring boxes. A **linked list** keeps each item in a **separate box (a node)** anywhere in memory, and each box holds **a pointer (reference) to the next box**. You find an item by **following the chain** from the first box.

Analogy: a **treasure hunt**. Each clue (node) tells you its prize (the value) and where to find the next clue (the pointer). You can only start at the first clue and follow them one by one. Adding a new clue in the middle means rewriting just one note, not moving every clue.

```text
 head
  │
  ▼
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ 10 │  ●──┼──►│ 20 │  ●──┼──►│ 30 │  ●──┼──►│ 40 │ None│
└──────────┘   └──────────┘   └──────────┘   └──────────┘
 value next     value next     value next     value next (None marks the end)
```

- A **node** = a value + a `next` pointer.
- The **head** is a pointer to the first node (the only entry point). An empty list has `head = None`.
- The last node's `next` is `None`.

## 2. Arrays versus linked lists (the big picture)

| | Array / Python list | Singly linked list |
|--|---------------------|--------------------|
| Memory layout | contiguous block | scattered nodes joined by pointers |
| Access `i`-th item | `O(1)` | `O(n)` (walk from the head) |
| Insert/delete at the **front** | `O(n)` (shift) | **`O(1)`** (change the head) |
| Insert/delete in the middle, **given the node** | `O(n)` (shift) | **`O(1)`** (re-link) |
| Search by value | `O(n)` | `O(n)` |
| Memory per item | just the value (or a pointer) | value **plus a pointer** (extra 8+ bytes), plus object overhead |
| Cache friendliness | excellent | poor (nodes are scattered) |

In practice **arrays win for most jobs** (cache locality and `O(1)` indexing). Linked lists matter because they teach pointers (the foundation for trees and graphs), power structures like queues, LRU caches and hash-table chains, and shine when you insert and delete a lot at known positions.

## 3. The node

```python
class Node:
    def __init__(self, value, next=None):
        self.value = value
        self.next = next            # a reference to another Node, or None

a = Node(10)
b = Node(20)
c = Node(30)
a.next = b                          # link: a -> b
b.next = c                          # link: b -> c
print(a.value, a.next.value, a.next.next.value, a.next.next.next)       # 10 20 30 None
```

## 4. The list class

Operations we will implement:

```python
class LinkedList:
    def __init__(self):
        self.head = None
        self._size = 0

    # --- reading ---------------------------------------------------------------------
    def __len__(self):
        return self._size                                   # O(1): we keep a counter

    def __iter__(self):                                     # O(n) to consume: walk the chain
        node = self.head
        while node:
            yield node.value
            node = node.next

    def __repr__(self):
        return " -> ".join(map(repr, self)) + " -> None" if self.head else "empty"

    def get(self, index):                                   # O(n): must walk `index` steps
        if not 0 <= index < self._size:
            raise IndexError("index out of range")
        node = self.head
        for _ in range(index):
            node = node.next
        return node.value

    def find(self, value):                                  # O(n): returns the index or -1
        node, index = self.head, 0
        while node:
            if node.value == value:
                return index
            node, index = node.next, index + 1
        return -1

    # --- adding ----------------------------------------------------------------------
    def prepend(self, value):                               # O(1): new node becomes the head
        self.head = Node(value, self.head)
        self._size += 1

    def append(self, value):                                # O(n): walk to the last node
        new = Node(value)
        if not self.head:
            self.head = new
        else:
            node = self.head
            while node.next:
                node = node.next
            node.next = new
        self._size += 1

    def insert(self, index, value):                         # O(n) to find the spot, O(1) to link
        if not 0 <= index <= self._size:
            raise IndexError("index out of range")
        if index == 0:
            return self.prepend(value)
        node = self.head
        for _ in range(index - 1):                          # stop at the node BEFORE the insertion point
            node = node.next
        node.next = Node(value, node.next)
        self._size += 1

    # --- removing --------------------------------------------------------------------
    def remove(self, value):                                # O(n): find, then re-link around it
        if not self.head:
            raise ValueError(f"{value!r} not in list")
        if self.head.value == value:
            self.head = self.head.next
            self._size -= 1
            return
        node = self.head
        while node.next and node.next.value != value:
            node = node.next
        if not node.next:
            raise ValueError(f"{value!r} not in list")
        node.next = node.next.next                          # skip over the removed node
        self._size -= 1

    def pop_front(self):                                    # O(1)
        if not self.head:
            raise IndexError("pop from empty list")
        value = self.head.value
        self.head = self.head.next
        self._size -= 1
        return value

lst = LinkedList()
for v in (20, 30, 40):
    lst.append(v)
lst.prepend(10)
print(lst, len(lst))                                        # 10 -> 20 -> 30 -> 40 -> None 4
lst.insert(2, 25)
print(lst)                                                  # 10 -> 20 -> 25 -> 30 -> 40 -> None
lst.remove(30)
print(lst, lst.get(2), lst.find(40), lst.find(99), list(lst))
# 10 -> 20 -> 25 -> 40 -> None 25 3 -1 [10, 20, 25, 40]
print(lst.pop_front(), lst, len(lst))                       # 10 20 -> 25 -> 40 -> None 3
```

## 5. Following the pointers: traces

### Prepend (add at the front): 1 pointer change

```text
Before:   head ─► [20] ─► [30] ─► None

new = Node(10, next=head)          new ─► [10] ─► [20] ─► [30]
head = new

After:    head ─► [10] ─► [20] ─► [30] ─► None          (no existing node moved)
```

### Insert in the middle (after finding the previous node): 2 pointer changes

```text
Insert 25 after node 20:      [10] ─► [20] ────────► [30]
                                          ╲          ╱
                                           [25] ────╯

 step 1: new.next = prev.next        (25 points to 30)
 step 2: prev.next = new             (20 points to 25)
 order matters: if you did step 2 first, the link to 30 would be lost!
```

### Remove: skip over a node

```text
Remove 30:       [10] ─► [20] ─► [25] ─► [30] ─► [40]
 prev = node 25;  prev.next = prev.next.next

                 [10] ─► [20] ─► [25] ──────────► [40]        (node 30 is no longer referenced: garbage collected)
```

Edge cases that cause most bugs: **empty list**, **single node**, **removing the head**, **inserting at the end**, **index equal to the size**. Always test these.

```python
edge = LinkedList()
edge.prepend(1); edge.remove(1)
print(edge, len(edge))                                      # empty 0
try:
    edge.remove(1)
except ValueError as error:
    print("ValueError:", error)                             # ValueError: 1 not in list
```

## 6. Making `append` O(1): keep a tail pointer

Walking to the end every time is wasteful. Store a `tail` pointer and appending becomes constant time:

```python
class LinkedListWithTail(LinkedList):
    def __init__(self):
        super().__init__()
        self.tail = None

    def append(self, value):                                # O(1)
        new = Node(value)
        if not self.head:
            self.head = self.tail = new
        else:
            self.tail.next = new
            self.tail = new
        self._size += 1

    def prepend(self, value):
        super().prepend(value)
        if self._size == 1:
            self.tail = self.head

    def pop_front(self):
        value = super().pop_front()
        if self._size == 0:
            self.tail = None
        return value

fast = LinkedListWithTail()
for i in range(1, 6):
    fast.append(i)
fast.prepend(0)
print(fast, fast.tail.value)                                # 0 -> 1 -> 2 -> 3 -> 4 -> 5 -> None 5
```

Removing the **last** node is still `O(n)` in a singly linked list (you need the node before it); that is one reason doubly linked lists exist ([next lesson](02-doubly-and-circular.md)).

## 7. Complexity summary

| Operation | Singly linked (head only) | With tail pointer |
|-----------|---------------------------|-------------------|
| Access by index | `O(n)` | `O(n)` |
| Search by value | `O(n)` | `O(n)` |
| Insert at front | `O(1)` | `O(1)` |
| Insert at end | `O(n)` | `O(1)` |
| Insert after a known node | `O(1)` | `O(1)` |
| Delete at front | `O(1)` | `O(1)` |
| Delete after a known node | `O(1)` | `O(1)` |
| Delete at end / by value | `O(n)` | `O(n)` |
| Space | `O(n)` (value + pointer per item) | `O(n)` |

## 8. Measuring the difference with arrays

```python
import time

def build_list_front_inserts(n):
    items = []
    for i in range(n):
        items.insert(0, i)                                  # Python list: O(n) per insert -> O(n²) total
    return items

def build_linked_front_inserts(n):
    lst = LinkedList()
    for i in range(n):
        lst.prepend(i)                                      # O(1) per insert -> O(n) total
    return lst

n = 20_000
t = time.perf_counter(); build_list_front_inserts(n); array_time = time.perf_counter() - t
t = time.perf_counter(); build_linked_front_inserts(n); linked_time = time.perf_counter() - t
print(array_time > 0 and linked_time > 0)                   # True
# For front inserts the linked list scales linearly while the list scales quadratically
# (note: CPython's list.insert(0, x) is a very fast C memmove, so Python-level linked lists only win for large n)

# Random access goes the other way
big_list, big_linked = list(range(20_000)), LinkedList()
for i in range(20_000):
    big_linked.append(i)
t = time.perf_counter(); [big_list[10_000] for _ in range(200)]; array_access = time.perf_counter() - t
t = time.perf_counter(); [big_linked.get(10_000) for _ in range(200)]; linked_access = time.perf_counter() - t
print(linked_access > array_access * 100)                   # True: walking 10,000 nodes each time versus one address calculation
```

## 9. Two real-world examples

**Example 1: Undo history and browser "back" lists.** Each state keeps a pointer to the previous one; going back is following a link, adding a new state is creating a node. No shifting of thousands of old states is needed.

**Example 2: Chaining in hash tables.** When two keys hash to the same slot, many hash tables store the colliding entries as a small linked list in that slot (separate chaining): inserting is `O(1)` at the head ([hash tables](../hash-tables/README.md)). Operating systems keep free memory blocks, ready queues and file-system chains as linked lists too.

## 10. Common mistakes

- Losing the rest of the list by overwriting `next` in the wrong order (link the new node forward **first**).
- Not handling `head is None` (empty list) or removing the head.
- Infinite loops: a cycle in the list (a node's `next` pointing backward) makes `while node:` run forever.
- Off-by-one when walking to index `i` (stop at `i - 1` to insert at `i`).
- Forgetting to update `size` or `tail`.
- Assuming `lst[i]` is cheap: it is `O(n)`.
- Using a linked list "because insertion is O(1)" when you actually need random access (a list is better).

## 11. Practice

1. Add `__getitem__` and `__contains__` to `LinkedList`; what are their costs?
2. Write `insert_sorted(value)` that keeps the list sorted.
3. Write `to_list()` and `from_list(values)` helpers (class method).
4. Implement `remove_all(value)` that deletes every node equal to `value` in one pass.
5. Count nodes recursively (and explain the stack cost).
6. Implement `LinkedList.last()` returning the last value without a tail pointer.
7. Given the head only, how do you delete a node when you are given only a reference to that node (not the previous one)? (Hint: copy the next node's value into it.)

<details>
<summary>Solutions</summary>

**1.**
```python
def __getitem__(self, index): return self.get(index)                 # O(n)
def __contains__(self, value): return self.find(value) != -1         # O(n)
LinkedList.__getitem__, LinkedList.__contains__ = __getitem__, __contains__
x = LinkedList(); [x.append(i) for i in (3, 5, 8)]
print(x[1], 5 in x, 9 in x)                                          # 5 True False
```

**2.**
```python
def insert_sorted(self, value):
    if not self.head or value <= self.head.value:
        return self.prepend(value)
    node = self.head
    while node.next and node.next.value < value:
        node = node.next
    node.next = Node(value, node.next)
    self._size += 1
LinkedList.insert_sorted = insert_sorted
s = LinkedList()
for v in (5, 1, 4, 2, 3): s.insert_sorted(v)
print(s)                                                             # 1 -> 2 -> 3 -> 4 -> 5 -> None
```

**3.**
```python
@classmethod
def from_list(cls, values):
    lst = cls()
    for v in values: lst.append(v)
    return lst
LinkedList.from_list = from_list
LinkedList.to_list = lambda self: list(self)
print(LinkedList.from_list([1, 2, 3]).to_list())                     # [1, 2, 3]
```

**4.**
```python
def remove_all(self, value):
    dummy = Node(None, self.head)                  # a dummy node avoids special-casing the head
    node = dummy
    while node.next:
        if node.next.value == value:
            node.next = node.next.next; self._size -= 1
        else:
            node = node.next
    self.head = dummy.next
LinkedList.remove_all = remove_all
r = LinkedList.from_list([1, 2, 1, 3, 1])
r.remove_all(1); print(r)                                            # 2 -> 3 -> None
```

**5.**
```python
def count_nodes(node): return 0 if node is None else 1 + count_nodes(node.next)
print(count_nodes(LinkedList.from_list([1, 2, 3, 4]).head))          # 4   (uses O(n) call-stack space: recursion depth n)
```

**6.**
```python
def last(self):
    if not self.head: raise IndexError("empty list")
    node = self.head
    while node.next: node = node.next
    return node.value
LinkedList.last = last
print(LinkedList.from_list([7, 8, 9]).last())                        # 9
```

**7.**
```python
def delete_node(node):                              # works for any node except the last one
    node.value = node.next.value                    # copy the next value in ...
    node.next = node.next.next                      # ... and unlink the next node
chain = LinkedList.from_list([1, 2, 3, 4])
target = chain.head.next                            # the node holding 2
delete_node(target); print(chain)                   # 1 -> 3 -> 4 -> None
```

</details>

## 12. Check yourself

1. What does a node contain?
2. Why is inserting at the front `O(1)` but at index `i` `O(n)`?
3. Why is reading the `i`-th item `O(n)`?
4. What are the first edge cases to test?
5. Why do arrays usually outperform linked lists in practice?

<details>
<summary>Answers</summary>

1. A value and a reference to the next node (or `None`).
2. At the front you only change the head pointer; at index `i` you must first walk `i` nodes to reach the insertion point (the linking itself is `O(1)`).
3. There is no address formula: you must follow `next` pointers from the head `i` times.
4. Empty list, single node, head removal, insertion at the end.
5. Contiguous memory is cache friendly and indexable in `O(1)`; nodes are scattered and carry extra pointer overhead.

</details>

[Back to linked lists](README.md) · Next: [doubly and circular linked lists](02-doubly-and-circular.md)
