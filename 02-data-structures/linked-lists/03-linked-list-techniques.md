# Linked-List Techniques and Classic Problems

**Prerequisites:** [singly linked list](01-singly-linked-list.md), [fast and slow pointers pattern](../../09-interview-playbook/problem-solving-patterns/README.md). **You will learn:** the handful of techniques behind almost every linked-list problem: the dummy node, pointer rewiring, reversal, fast and slow pointers, merging, the "n-th from the end" trick and cycle handling, each traced step by step with tests.

## 1. In plain words

Linked-list problems look scary because **you rewire pointers with no safety net**: one wrong assignment loses part of the list. The cure is a small set of habits:

1. **Draw the nodes and arrows** before coding.
2. **Use a dummy (sentinel) node** so the head needs no special case.
3. **Save `next` before overwriting it.**
4. **Think "what do I point to now?"** for each pointer, in a safe order.
5. **Test** with empty, one-node, two-node lists.

Helpers used throughout (build a list from values; read it back):

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val, self.next = val, next

def build(values):
    dummy = tail = ListNode()
    for v in values:
        tail.next = ListNode(v)
        tail = tail.next
    return dummy.next

def to_list(head):
    out = []
    while head:
        out.append(head.val)
        head = head.next
    return out

print(to_list(build([1, 2, 3])), to_list(build([])), to_list(build([7])))          # [1, 2, 3] [] [7]
```

## 2. Technique 1: the dummy node

A **dummy node** sits before the real head. Operations that may change the head (delete the first node, insert at the start, merge) then work uniformly, and you return `dummy.next`.

```python
def remove_value(head, target):
    """Remove every node with value `target`. The head may be removed: the dummy handles it."""
    dummy = ListNode(0, head)
    node = dummy
    while node.next:
        if node.next.val == target:
            node.next = node.next.next            # unlink
        else:
            node = node.next
    return dummy.next

print(to_list(remove_value(build([1, 2, 6, 3, 6]), 6)), to_list(remove_value(build([6, 6, 6]), 6)), to_list(remove_value(build([]), 1)))
# [1, 2, 3] [] []
```

Without the dummy you would write separate code for "the head must be removed" (and loop while the new head also matches).

## 3. Technique 2: reversing a list

### Iterative: three pointers (`prev`, `current`, `next`)

```text
Goal: 1 -> 2 -> 3 -> None   becomes   3 -> 2 -> 1 -> None

 prev=None  cur=1:  save nxt=2;  cur.next = prev (1 -> None);  prev = 1;  cur = 2
 prev=1     cur=2:  save nxt=3;  cur.next = prev (2 -> 1);     prev = 2;  cur = 3
 prev=2     cur=3:  save nxt=None; cur.next = prev (3 -> 2);   prev = 3;  cur = None
 return prev  (the new head: 3)
```

```python
def reverse(head):
    prev = None
    current = head
    while current:
        nxt = current.next          # 1. remember the rest of the list
        current.next = prev         # 2. point this node backward
        prev = current              # 3. move prev forward
        current = nxt               # 4. move current forward
    return prev

print(to_list(reverse(build([1, 2, 3, 4, 5]))), to_list(reverse(build([1]))), to_list(reverse(None)))      # [5, 4, 3, 2, 1] [1] []
```

`O(n)` time, `O(1)` space.

### Recursive (elegant, but `O(n)` stack)

```python
def reverse_recursive(head):
    if head is None or head.next is None:
        return head                            # base case: empty or single node
    new_head = reverse_recursive(head.next)    # reverse the rest first
    head.next.next = head                      # the node after head now points back at head
    head.next = None                           # head becomes the tail
    return new_head

print(to_list(reverse_recursive(build([1, 2, 3, 4]))))      # [4, 3, 2, 1]
```

### Reverse only a section (positions `left` to `right`)

```python
def reverse_between(head, left, right):
    dummy = ListNode(0, head)
    before = dummy
    for _ in range(left - 1):
        before = before.next                    # the node just before the section
    prev, current = None, before.next
    for _ in range(right - left + 1):
        nxt = current.next
        current.next = prev
        prev, current = current, nxt
    before.next.next = current                  # the old section head now points past the section
    before.next = prev                          # the old section tail becomes the new section head
    return dummy.next

print(to_list(reverse_between(build([1, 2, 3, 4, 5]), 2, 4)))          # [1, 4, 3, 2, 5]
```

## 4. Technique 3: fast and slow pointers

Two pointers move at **different speeds** (slow: 1 step, fast: 2 steps). When fast reaches the end, slow is at the middle; if the list loops, fast eventually catches slow.

### Middle of the list

```python
def middle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow

print(middle(build([1, 2, 3, 4, 5])).val, middle(build([1, 2, 3, 4])).val)        # 3 3   (for an even length, the second middle)
```

```text
[1] → [2] → [3] → [4] → [5]
 s,f
        s     f
              s            f(end)        slow is at 3, the middle
```

### Detecting a cycle (Floyd's tortoise and hare)

```python
def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow is fast:                        # they can only meet inside a cycle
            return True
    return False

def cycle_start(head):
    """Find the node where the cycle begins (or None)."""
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow is fast:
            slow = head                          # restart one pointer from the head
            while slow is not fast:              # both now move 1 step: they meet at the cycle entrance
                slow, fast = slow.next, fast.next
            return slow
    return None

ring = build([1, 2, 3, 4, 5])
tail = ring
while tail.next:
    tail = tail.next
tail.next = ring.next.next                      # 5 points back to 3: cycle 3 -> 4 -> 5 -> 3
print(has_cycle(ring), cycle_start(ring).val, has_cycle(build([1, 2, 3])), cycle_start(build([1, 2, 3])))     # True 3 False None
```

Why it works: inside a cycle the gap between fast and slow shrinks by 1 each step, so fast must land exactly on slow. `O(n)` time, `O(1)` space (a set of visited nodes would use `O(n)` space).

### Palindrome list: find the middle, reverse the second half, compare

```python
def is_palindrome_list(head):
    if not head or not head.next:
        return True
    slow = fast = head
    while fast.next and fast.next.next:        # find the end of the first half
        slow, fast = slow.next, fast.next.next
    second = reverse(slow.next)                # reverse the second half
    first, other, ok = head, second, True
    while other:
        if first.val != other.val:
            ok = False
            break
        first, other = first.next, other.next
    slow.next = reverse(second)                # restore the list (be polite to the caller)
    return ok

print(is_palindrome_list(build([1, 2, 3, 2, 1])), is_palindrome_list(build([1, 2, 2, 1])), is_palindrome_list(build([1, 2, 3])))    # True True False
```

## 5. Technique 4: the n-th node from the end (two pointers with a gap)

Move a lead pointer `n` steps ahead, then move both until the lead reaches the end: the follower is exactly `n` from the end. One pass, `O(1)` space.

```python
def remove_nth_from_end(head, n):
    dummy = ListNode(0, head)
    lead = follow = dummy
    for _ in range(n + 1):                     # lead is n+1 steps ahead, so follow stops just BEFORE the target
        lead = lead.next
    while lead:
        lead, follow = lead.next, follow.next
    follow.next = follow.next.next             # unlink the target
    return dummy.next

print(to_list(remove_nth_from_end(build([1, 2, 3, 4, 5]), 2)), to_list(remove_nth_from_end(build([1]), 1)))     # [1, 2, 3, 5] []
```

## 6. Technique 5: merging sorted lists

```python
def merge_two_sorted(a, b):
    dummy = tail = ListNode()
    while a and b:
        if a.val <= b.val:
            tail.next, a = a, a.next            # reuse the node: no new allocation
        else:
            tail.next, b = b, b.next
        tail = tail.next
    tail.next = a or b                          # attach whichever list still has nodes
    return dummy.next

print(to_list(merge_two_sorted(build([1, 4, 7]), build([2, 3, 9, 10]))))        # [1, 2, 3, 4, 7, 9, 10]
```

`O(n + m)` time, `O(1)` extra space (the nodes are relinked). This merge step is the core of **merge sort for linked lists**, which sorts in `O(n log n)` with `O(log n)` stack space and, unlike array sorts, needs no random access:

```python
def sort_list(head):
    if not head or not head.next:
        return head
    slow, fast = head, head.next                # split into two halves
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    second, slow.next = slow.next, None
    return merge_two_sorted(sort_list(head), sort_list(second))

print(to_list(sort_list(build([4, 2, 1, 3, 9, 7]))))        # [1, 2, 3, 4, 7, 9]
```

### Merging k sorted lists with a heap

```python
import heapq

def merge_k_lists(lists):
    heap = [(node.val, i, node) for i, node in enumerate(lists) if node]      # i breaks ties (nodes are not comparable)
    heapq.heapify(heap)
    dummy = tail = ListNode()
    while heap:
        _, i, node = heapq.heappop(heap)
        tail.next = node
        tail = tail.next
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))
    return dummy.next

print(to_list(merge_k_lists([build([1, 4, 5]), build([1, 3, 4]), build([2, 6])])))     # [1, 1, 2, 3, 4, 4, 5, 6]
```

`O(N log k)` for `N` total nodes and `k` lists.

## 7. Technique 6: arithmetic with digit lists

Numbers stored digit by digit (least significant first) can be added with a carry, exactly like on paper.

```python
def add_numbers(a, b):
    dummy = tail = ListNode()
    carry = 0
    while a or b or carry:
        total = carry + (a.val if a else 0) + (b.val if b else 0)
        carry, digit = divmod(total, 10)
        tail.next = ListNode(digit)
        tail = tail.next
        a, b = (a.next if a else None), (b.next if b else None)
    return dummy.next

print(to_list(add_numbers(build([2, 4, 3]), build([5, 6, 4]))))      # [7, 0, 8]   (342 + 465 = 807)
print(to_list(add_numbers(build([9, 9, 9]), build([1]))))            # [0, 0, 0, 1] (999 + 1 = 1000)
```

## 8. Technique 7: intersection and copying with random pointers

```python
def intersection_node(a, b):
    """Two lists may share a tail. Walk both; when one ends, restart it at the other's head: they meet at the junction."""
    p, q = a, b
    while p is not q:
        p = p.next if p else b
        q = q.next if q else a
    return p

common = build([8, 9])
l1, l2 = build([1, 2]), build([5])
l1.next.next = common
l2.next = common
print(intersection_node(l1, l2).val, intersection_node(build([1]), build([2])))        # 8 None
```

Both walkers travel `len(a) + len(b)` steps in total, so they line up at the shared node (or both reach `None`).

## 9. Cheat sheet

| Problem | Technique | Complexity |
|---------|-----------|-----------|
| Delete nodes that may include the head | dummy node | `O(n)`, `O(1)` |
| Reverse a list / a section | three pointers | `O(n)`, `O(1)` |
| Find the middle | fast and slow | `O(n)`, `O(1)` |
| Detect a cycle / find its start | Floyd's two speeds | `O(n)`, `O(1)` |
| n-th from the end | gap of `n` between two pointers | `O(n)`, `O(1)` |
| Merge sorted lists | dummy + relink | `O(n + m)`, `O(1)` |
| Sort a list | split in the middle + merge | `O(n log n)` |
| Palindrome | middle + reverse half + compare | `O(n)`, `O(1)` |
| Add numbers | carry loop | `O(max(n, m))` |
| Merge `k` lists | min-heap | `O(N log k)` |
| Intersection | switch heads when one ends | `O(n + m)`, `O(1)` |

## 10. Two real-world examples

**Example 1: Undo/redo and text editors.** Many editors store text in a **rope** or **gap buffer**, and undo histories in linked structures: inserting or removing in the middle by re-linking nodes avoids copying huge arrays. The same pointer-rewiring skills apply.

**Example 2: Memory allocators and kernels.** Allocators keep **free lists** of blocks as linked lists; coalescing adjacent free blocks is pointer surgery; detecting corruption (an accidental cycle in a free list) uses tortoise-and-hare style checks. The Linux kernel's intrusive linked lists are manipulated with exactly these techniques.

## 11. Common mistakes

- Overwriting `node.next` before saving the rest (the tail is lost).
- Forgetting the head case (use a dummy).
- Off-by-one with the lead pointer gap (`n` versus `n + 1`).
- Not terminating loops: a cycle makes `while node:` infinite.
- Returning the old head after reversing (return `prev`).
- Forgetting to set the new tail's `next = None` when splitting or reversing sections (accidental cycles).
- Using recursion on long lists (stack overflow at roughly 1,000 nodes in Python).

## 12. Practice

1. Reverse a list in groups of `k` nodes (leave a final short group as is).
2. Remove duplicates from a **sorted** list.
3. Rearrange a list so odd-position nodes come first, then even-position nodes (in place).
4. Rotate a list to the right by `k` places.
5. Partition a list so values less than `x` come before the rest, preserving relative order.
6. Detect whether two lists are equal (same values in order).
7. Find the length of a cycle if one exists.

<details>
<summary>Solutions</summary>

**1.**
```python
def reverse_k_group(head, k):
    nodes, probe = [], head
    for _ in range(k):                              # check that k nodes exist
        if not probe: return head
        probe = probe.next
    prev, cur = reverse_k_group(probe, k), head     # the rest, already processed
    for _ in range(k):
        nxt = cur.next
        cur.next = prev
        prev, cur = cur, nxt
    return prev
print(to_list(reverse_k_group(build([1, 2, 3, 4, 5]), 2)), to_list(reverse_k_group(build([1, 2, 3, 4, 5, 6]), 3)))     # [2, 1, 4, 3, 5] [3, 2, 1, 6, 5, 4]
```

**2.**
```python
def dedupe_sorted(head):
    node = head
    while node and node.next:
        if node.val == node.next.val:
            node.next = node.next.next
        else:
            node = node.next
    return head
print(to_list(dedupe_sorted(build([1, 1, 2, 3, 3, 3, 4]))))      # [1, 2, 3, 4]
```

**3.**
```python
def odd_even(head):
    if not head: return head
    odd, even = head, head.next
    even_head = even
    while even and even.next:
        odd.next = even.next; odd = odd.next
        even.next = odd.next; even = even.next
    odd.next = even_head
    return head
print(to_list(odd_even(build([1, 2, 3, 4, 5]))))                  # [1, 3, 5, 2, 4]
```

**4.**
```python
def rotate_right(head, k):
    if not head or not head.next: return head
    length, tail = 1, head
    while tail.next: tail, length = tail.next, length + 1
    k %= length
    if k == 0: return head
    tail.next = head                                # make it circular
    new_tail = head
    for _ in range(length - k - 1): new_tail = new_tail.next
    new_head, new_tail.next = new_tail.next, None   # break the circle at the right place
    return new_head
print(to_list(rotate_right(build([1, 2, 3, 4, 5]), 2)))           # [4, 5, 1, 2, 3]
```

**5.**
```python
def partition(head, x):
    small_head, big_head = ListNode(), ListNode()
    small, big = small_head, big_head
    while head:
        if head.val < x: small.next, small = head, head
        else: big.next, big = head, head
        head = head.next
    big.next = None
    small.next = big_head.next
    return small_head.next
print(to_list(partition(build([1, 4, 3, 2, 5, 2]), 3)))           # [1, 2, 2, 4, 3, 5]
```

**6.**
```python
def lists_equal(a, b):
    while a and b:
        if a.val != b.val: return False
        a, b = a.next, b.next
    return a is None and b is None
print(lists_equal(build([1, 2]), build([1, 2])), lists_equal(build([1, 2]), build([1, 2, 3])))     # True False
```

**7.**
```python
def cycle_length(head):
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow is fast:
            length, node = 1, slow.next
            while node is not slow:
                node, length = node.next, length + 1
            return length
    return 0
print(cycle_length(ring), cycle_length(build([1, 2])))            # 3 0
```

</details>

## 13. Check yourself

1. Why use a dummy node?
2. What are the four steps inside the reversal loop?
3. How do fast and slow pointers find the middle?
4. How do you find the n-th node from the end in one pass?
5. Why does Floyd's algorithm detect cycles?
6. What is the complexity of merging two sorted linked lists?

<details>
<summary>Answers</summary>

1. It removes special cases for changing the head: you always work with `node.next` and return `dummy.next`.
2. Save `next`, point `current.next` to `prev`, advance `prev`, advance `current`.
3. Slow moves one step while fast moves two; when fast reaches the end, slow is at the middle.
4. Advance a lead pointer `n` steps, then move both until lead reaches the end; the follower is at the target (or just before it).
5. Inside a cycle the distance between the two pointers decreases by one each step, so the faster one must eventually meet the slower one.
6. `O(n + m)` time and `O(1)` extra space (nodes are relinked).

</details>

[Back to linked lists](README.md) · Previous: [doubly and circular lists](02-doubly-and-circular.md)
