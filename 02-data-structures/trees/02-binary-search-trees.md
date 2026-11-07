# Binary Search Trees

**Prerequisites:** [binary trees and traversals](01-binary-trees-and-traversals.md), [binary search](../arrays-strings/02-array-techniques.md). **You will learn:** the BST rule, search/insert/delete step by step (including the tricky two-children case), why order of insertion matters, how to validate a BST, and the useful extras: floor/ceiling, k-th smallest, range queries.

## 1. In plain words

A **binary search tree (BST)** is a binary tree with one extra rule that makes searching fast, like the "higher or lower?" guessing game:

> For every node, **everything in its left subtree is smaller**, and **everything in its right subtree is larger**.

```text
            8
          /   \
         3     10
        / \      \
       1   6      14
          / \    /
         4   7  13
```

To find 6: start at 8 (6 < 8, go left), 3 (6 > 3, go right), 6: found in 3 steps instead of scanning 9 values. Each step throws away a whole subtree: about half the data when the tree is balanced.

## 2. Search, insert, find min/max

```python
class Node:
    def __init__(self, key):
        self.key = key
        self.left = self.right = None

class BST:
    def __init__(self):
        self.root = None
        self.size = 0

    def search(self, key):
        node = self.root
        while node:
            if key == node.key:
                return True
            node = node.left if key < node.key else node.right
        return False

    def insert(self, key):
        if self.root is None:
            self.root, self.size = Node(key), 1
            return
        node = self.root
        while True:
            if key == node.key:
                return                                  # ignore duplicates
            side = "left" if key < node.key else "right"
            child = getattr(node, side)
            if child is None:
                setattr(node, side, Node(key))
                self.size += 1
                return
            node = child

    def minimum(self, node=None):
        node = node or self.root
        while node.left:
            node = node.left
        return node.key

    def maximum(self, node=None):
        node = node or self.root
        while node.right:
            node = node.right
        return node.key

    def inorder(self):
        out, stack, node = [], [], self.root
        while stack or node:
            while node:
                stack.append(node); node = node.left
            node = stack.pop(); out.append(node.key); node = node.right
        return out

    def height(self):
        def h(n): return -1 if n is None else 1 + max(h(n.left), h(n.right))
        return h(self.root)

tree = BST()
for k in [8, 3, 10, 1, 6, 14, 4, 7, 13]:
    tree.insert(k)
print(tree.inorder())                       # [1, 3, 4, 6, 7, 8, 10, 13, 14]   (always sorted!)
print(tree.search(6), tree.search(5))       # True False
print(tree.minimum(), tree.maximum())       # 1 14
print(tree.size, tree.height())             # 9 3
```

Inorder traversal of a BST is **sorted**: that is the BST rule seen from outside.

## 3. Deleting a node (three cases)

Deleting is where students struggle, so take it slowly.

1. **Leaf (no children):** remove it.
2. **One child:** replace the node by its child.
3. **Two children:** you cannot just remove it. Find its **inorder successor** (the smallest key in its right subtree, which is the next bigger value), copy that key into the node, then delete the successor from the right subtree (the successor has at most one child, so this is case 1 or 2).

```text
Delete 3 (two children: 1 and 6):
        8                         8
      /   \                     /   \
     3     10        ->        4     10        successor of 3 is 4 (leftmost of right subtree)
    / \      \                / \      \
   1   6      14             1   6      14
      / \    /                    \    /
     4   7  13                     7  13
```

```python
def delete(node, key):
    """Return the root of the subtree after deleting key."""
    if node is None:
        return None
    if key < node.key:
        node.left = delete(node.left, key)
    elif key > node.key:
        node.right = delete(node.right, key)
    else:
        if node.left is None:                   # cases 1 and 2: no left child (also covers leaf)
            return node.right
        if node.right is None:                  # case 2: no right child
            return node.left
        successor = node.right                  # case 3: two children
        while successor.left:
            successor = successor.left
        node.key = successor.key                # copy the successor's key up
        node.right = delete(node.right, successor.key)    # remove the successor from the right subtree
    return node

def remove(tree, key):
    if tree.search(key):
        tree.root = delete(tree.root, key)
        tree.size -= 1
        return True
    return False

print(remove(tree, 3), tree.inorder())      # True [1, 4, 6, 7, 8, 10, 13, 14]
print(remove(tree, 14), tree.inorder())     # True [1, 4, 6, 7, 8, 10, 13]
print(remove(tree, 99), tree.size)          # False 7
```

## 4. Complexity, and the problem of shape

Every operation follows one root-to-leaf path, so cost is **`O(h)`**, where `h` is the height.

- **Balanced** (random-ish insertions): `h ≈ log₂ n` so operations are **`O(log n)`**: a million items need about 20 steps.
- **Degenerate** (sorted insertions): the tree becomes a **linked list**, `h = n`, so operations are **`O(n)`**.

```python
import random

def build(keys):
    t = BST()
    for k in keys:
        t.insert(k)
    return t

n = 500
print(build(range(n)).height())                 # 499  (inserting in sorted order: a chain!)
random.seed(7)
shuffled = random.sample(range(n), n)
print(build(shuffled).height())                 # 16  (random order: far from 499; a perfect tree would be about log2(500) = 9)
```

Because the shape depends on insertion order, production code uses **self-balancing trees** ([AVL and red-black trees](03-balanced-trees-avl.md)) that guarantee `O(log n)`.

## 5. Validating a BST

A common mistake is checking only parent versus child. A node deep in the left subtree must be smaller than **every ancestor** it was placed left of. Pass down the allowed range:

```python
def is_valid_bst(node, low=float("-inf"), high=float("inf")):
    if node is None:
        return True
    if not (low < node.key < high):
        return False
    return is_valid_bst(node.left, low, node.key) and is_valid_bst(node.right, node.key, high)

print(is_valid_bst(tree.root))                  # True

bad = Node(5); bad.left = Node(3); bad.left.right = Node(6)      # 6 is right of 3, but left of 5 so it must be < 5
print(is_valid_bst(bad))                        # False
```

(A check of only `left < node < right` locally would wrongly accept `bad`.)

## 6. Useful extras

```python
def floor(node, key):          # largest key <= given key
    best = None
    while node:
        if node.key == key: return key
        if node.key < key:
            best, node = node.key, node.right
        else:
            node = node.left
    return best

def ceiling(node, key):        # smallest key >= given key
    best = None
    while node:
        if node.key == key: return key
        if node.key > key:
            best, node = node.key, node.left
        else:
            node = node.right
    return best

def kth_smallest(root, k):     # inorder traversal visits keys in order: stop at the k-th
    stack, node = [], root
    while stack or node:
        while node:
            stack.append(node); node = node.left
        node = stack.pop()
        k -= 1
        if k == 0:
            return node.key
        node = node.right

def range_query(node, low, high):    # all keys in [low, high], skipping subtrees that cannot match
    if node is None: return []
    out = []
    if low < node.key:  out += range_query(node.left, low, high)
    if low <= node.key <= high: out.append(node.key)
    if node.key < high: out += range_query(node.right, low, high)
    return out

keys_tree = build([8, 3, 10, 1, 6, 14, 4, 7, 13])
print(floor(keys_tree.root, 5), ceiling(keys_tree.root, 5))      # 4 6
print(kth_smallest(keys_tree.root, 3))                           # 4
print(range_query(keys_tree.root, 5, 10))                        # [6, 7, 8, 10]

def sorted_array_to_bst(values):     # picks the middle as root, giving a balanced tree
    if not values: return None
    mid = len(values) // 2
    node = Node(values[mid])
    node.left, node.right = sorted_array_to_bst(values[:mid]), sorted_array_to_bst(values[mid + 1:])
    return node

def tree_height(n): return -1 if n is None else 1 + max(tree_height(n.left), tree_height(n.right))
print(tree_height(sorted_array_to_bst(list(range(500)))))        # 8  (perfectly balanced: about log2(500))
```

## 7. Python has no built-in BST: what to use

| Need | Use |
|------|-----|
| Fast lookup only | `dict` / `set` |
| Sorted iteration, order queries, floor/ceiling | keep a sorted `list` with `bisect` (fine for read-heavy data), or `sortedcontainers.SortedList` (third-party) |
| Smallest/largest repeatedly | `heapq` ([heaps](../heaps/README.md)) |

```python
import bisect
data = [1, 4, 6, 7, 8, 10]
bisect.insort(data, 5)
print(data, bisect.bisect_left(data, 7))        # [1, 4, 5, 6, 7, 8, 10] 4
```

## 8. Two real-world examples

**Example 1: Database indexes.** An index lets the database find rows by a column without scanning the table. Most use a **B-tree**, a wide cousin of the BST that keeps nodes full of keys to minimize disk reads: `O(log n)` search and sorted range scans (`WHERE age BETWEEN 20 AND 30`).

**Example 2: Ordered maps in standard libraries.** `std::map` (C++) and `TreeMap` (Java) are red-black trees: they keep keys sorted so you can ask for "the next booking after 3pm" in `O(log n)`, something a hash table cannot do.

## 9. Common mistakes

- Validating a BST by comparing only parent and child.
- Forgetting the two-children deletion case.
- Assuming a BST is always balanced.
- Inserting sorted data into a plain BST.
- Duplicates: decide a policy (ignore, count, or always go right) and be consistent.
- Mutating a key after insertion (breaks the ordering).

## 10. Practice

1. Insert 5, 2, 8, 1, 9, 3 and draw the tree. What is its inorder? Height?
2. Delete 2 from that tree, then 5. Draw each result.
3. Write `lowest_common_ancestor_bst(root, a, b)` using the BST rule (no full search).
4. Write `count_in_range(root, low, high)`.
5. Insert 1, 2, 3, 4, 5 in order. What shape results and what does `search(5)` cost?
6. Convert the sorted list `[1, 2, 3, 4, 5, 6, 7]` to a balanced BST. What is its height?

<details>
<summary>Solutions</summary>

1. Tree: root 5; left 2 (children 1 and 3); right 8 (right child 9). Inorder `[1, 2, 3, 5, 8, 9]`, height 2.
2. Delete 2 (two children): successor is 3, so 3 replaces 2 and its old spot disappears (left 3 with child 1). Delete 5 (two children): successor is 8, so 8 becomes root with right child 9.
3. ```python
   def lca_bst(node, a, b):
       while node:
           if a < node.key and b < node.key: node = node.left
           elif a > node.key and b > node.key: node = node.right
           else: return node.key           # the paths split here (or hit a or b)
   print(lca_bst(keys_tree.root, 4, 7), lca_bst(keys_tree.root, 1, 4), lca_bst(keys_tree.root, 7, 14))      # 6 3 8
   ```
4. ```python
   def count_in_range(n, low, high):
       if n is None: return 0
       if n.key < low: return count_in_range(n.right, low, high)
       if n.key > high: return count_in_range(n.left, low, high)
       return 1 + count_in_range(n.left, low, high) + count_in_range(n.right, low, high)
   print(count_in_range(keys_tree.root, 5, 10))      # 4
   ```
5. A chain leaning right (a linked list); `search(5)` takes 5 steps: `O(n)`.
6. ```python
   print(tree_height(sorted_array_to_bst([1, 2, 3, 4, 5, 6, 7])))      # 2
   ```

</details>

## 11. Check yourself

1. What is the BST property?
2. What is the cost of search, and when is it bad?
3. How do you delete a node with two children?
4. What does an inorder traversal of a BST produce?
5. Why can a hash table not answer "the smallest key greater than 50"?
6. How do you validate a BST correctly?

<details>
<summary>Answers</summary>

1. Left subtree keys are smaller and right subtree keys larger, for every node.
2. `O(h)`: `O(log n)` balanced, `O(n)` when the tree degenerates into a chain.
3. Replace its key with the inorder successor's (smallest in the right subtree), then delete that successor.
4. The keys in sorted order.
5. A hash table scatters keys, so it has no notion of order or neighbors.
6. Pass down a `(low, high)` range that every node must stay inside (or check that inorder is strictly increasing).

</details>

[Back to trees](README.md) · Previous: [binary trees and traversals](01-binary-trees-and-traversals.md) · Next: [balanced trees: AVL](03-balanced-trees-avl.md)
