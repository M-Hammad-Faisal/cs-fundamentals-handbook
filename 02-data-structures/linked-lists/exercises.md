# Linked Lists: Exercises

Use this node for all problems:

```python
class Node:
    def __init__(self, value, next=None):
        self.value = value
        self.next = next
```

Helper functions for testing:

```python
def build(values):
    dummy = tail = Node(None)
    for v in values:
        tail.next = Node(v)
        tail = tail.next
    return dummy.next

def to_list(head):
    out = []
    while head:
        out.append(head.value)
        head = head.next
    return out
```

## Problems
1. Reverse a singly linked list iteratively, then recursively.
2. Find the middle node (return the second middle for even length).
3. Detect a cycle; then return the node where the cycle starts.
4. Merge two sorted linked lists.
5. Remove the n-th node from the end in one pass.
6. Check whether a linked list is a palindrome in `O(n)` time and `O(1)` space.
7. Remove all nodes with a given value.
8. Add two numbers stored as reversed digit lists (`2->4->3` + `5->6->4` = `7->0->8`).
9. Implement an LRU cache with `get` and `put` in `O(1)`.

<details>
<summary>Solutions</summary>

```python
# 1
def reverse_iter(head):
    prev = None
    while head:
        head.next, prev, head = prev, head, head.next
    return prev

def reverse_rec(head):
    if not head or not head.next:
        return head
    new_head = reverse_rec(head.next)
    head.next.next = head
    head.next = None
    return new_head

# 2
def middle(head):
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    return slow

# 3
def cycle_start(head):
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow is fast:
            slow = head
            while slow is not fast:
                slow, fast = slow.next, fast.next
            return slow
    return None

# 4
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

# 5
def remove_nth_from_end(head, n):
    dummy = Node(None, head)
    fast = slow = dummy
    for _ in range(n):
        fast = fast.next
    while fast.next:
        fast, slow = fast.next, slow.next
    slow.next = slow.next.next
    return dummy.next

# 6
def is_palindrome(head):
    if not head or not head.next:
        return True
    slow = fast = head
    while fast.next and fast.next.next:
        slow, fast = slow.next, fast.next.next
    second = reverse_iter(slow.next)       # reverse second half
    a, b = head, second
    ok = True
    while b:
        if a.value != b.value:
            ok = False
            break
        a, b = a.next, b.next
    slow.next = reverse_iter(second)       # restore the list
    return ok

# 7
def remove_all(head, target):
    dummy = Node(None, head)
    cur = dummy
    while cur.next:
        if cur.next.value == target:
            cur.next = cur.next.next
        else:
            cur = cur.next
    return dummy.next

# 8
def add_two_numbers(a, b):
    dummy = tail = Node(None)
    carry = 0
    while a or b or carry:
        s = carry + (a.value if a else 0) + (b.value if b else 0)
        carry, digit = divmod(s, 10)
        tail.next = Node(digit)
        tail = tail.next
        a = a.next if a else None
        b = b.next if b else None
    return dummy.next

# 9
class DNode:
    def __init__(self, key=None, value=None):
        self.key, self.value = key, value
        self.prev = self.next = None

class LRUCache:
    def __init__(self, capacity):
        self.cap = capacity
        self.map = {}
        self.head, self.tail = DNode(), DNode()   # sentinels
        self.head.next, self.tail.prev = self.tail, self.head

    def _remove(self, node):
        node.prev.next, node.next.prev = node.next, node.prev

    def _add_front(self, node):
        node.next, node.prev = self.head.next, self.head
        self.head.next.prev = node
        self.head.next = node

    def get(self, key):
        if key not in self.map:
            return -1
        node = self.map[key]
        self._remove(node)
        self._add_front(node)
        return node.value

    def put(self, key, value):
        if key in self.map:
            self._remove(self.map[key])
        node = DNode(key, value)
        self.map[key] = node
        self._add_front(node)
        if len(self.map) > self.cap:
            lru = self.tail.prev
            self._remove(lru)
            del self.map[lru.key]
```

</details>

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [The Singly Linked List, Built from Scratch](01-singly-linked-list.md) · [Doubly Linked Lists, Circular Lists and the LRU Cache](02-doubly-and-circular.md) · [Linked-List Techniques and Classic Problems](03-linked-list-techniques.md)
