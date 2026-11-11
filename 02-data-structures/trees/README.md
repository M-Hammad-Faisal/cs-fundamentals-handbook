# Trees

## Detailed lessons

1. [Binary trees and traversals](01-binary-trees-and-traversals.md): vocabulary, preorder/inorder/postorder/level-order, classic questions
2. [Binary search trees](02-binary-search-trees.md): search, insert, delete, validation, range queries
3. [Balanced trees](03-balanced-trees-avl.md): rotations, a full AVL tree, red-black trees, B-trees
4. [Segment and Fenwick trees](04-segment-and-fenwick-trees.md): range queries with updates in `O(log n)`

The rest of this page is the quick reference.

## 1. The concept

A **tree** is a hierarchical structure of **nodes** connected by edges, with no cycles. One node is the **root**; every other node has exactly one **parent**. Nodes with no children are **leaves**.

```
        8            root
       / \
      3   10         3 and 10 are siblings; 8 is their parent
     / \    \
    1   6    14      1, 6, 14 are leaves
```

### Vocabulary

| Term | Meaning |
|------|---------|
| **Depth** of a node | Edges from the root to the node |
| **Height** of a node | Edges on the longest path down to a leaf |
| **Height of tree** | Height of the root |
| **Subtree** | A node and all its descendants |
| **Binary tree** | Each node has at most two children (left, right) |
| **Full / complete / perfect** | Full: 0 or 2 children each. Complete: filled level by level, left to right. Perfect: all levels full |
| **Balanced** | Heights of left and right subtrees differ by a small bounded amount |

A tree with `n` nodes has `n - 1` edges. A perfect binary tree of height `h` has `2^(h+1) - 1` nodes, so its height is about `log₂ n`.

## 2. Binary tree node and traversals

```python
class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
```

### Depth-first traversals (recursive)

```python
def preorder(node, out):       # root, left, right
    if node:
        out.append(node.val)
        preorder(node.left, out)
        preorder(node.right, out)

def inorder(node, out):        # left, root, right  (sorted order for a BST)
    if node:
        inorder(node.left, out)
        out.append(node.val)
        inorder(node.right, out)

def postorder(node, out):      # left, right, root  (children before parent)
    if node:
        postorder(node.left, out)
        postorder(node.right, out)
        out.append(node.val)
```

| Order | Typical use |
|-------|-------------|
| Preorder | Copy a tree, serialize, prefix expressions |
| Inorder | Read a BST in sorted order |
| Postorder | Delete a tree, evaluate expression trees, compute sizes/heights |

### Iterative inorder (explicit stack)

```python
def inorder_iter(root):
    out, stack, cur = [], [], root
    while cur or stack:
        while cur:
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()
        out.append(cur.val)
        cur = cur.right
    return out
```

### Breadth-first (level order)

```python
from collections import deque

def level_order(root):
    if not root:
        return []
    out, q = [], deque([root])
    while q:
        level = []
        for _ in range(len(q)):          # one level at a time
            node = q.popleft()
            level.append(node.val)
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        out.append(level)
    return out
```

All traversals visit every node once: `O(n)` time. Recursion uses `O(h)` stack space (`h` = height); BFS uses up to `O(w)` space (`w` = max width).

### Common recursive patterns

```python
def height(node):
    return 0 if not node else 1 + max(height(node.left), height(node.right))

def count_nodes(node):
    return 0 if not node else 1 + count_nodes(node.left) + count_nodes(node.right)

def is_same(a, b):
    if not a and not b:
        return True
    if not a or not b or a.val != b.val:
        return False
    return is_same(a.left, b.left) and is_same(a.right, b.right)

def invert(node):
    if node:
        node.left, node.right = invert(node.right), invert(node.left)
    return node

def lowest_common_ancestor(root, p, q):          # for a general binary tree
    if not root or root is p or root is q:
        return root
    left = lowest_common_ancestor(root.left, p, q)
    right = lowest_common_ancestor(root.right, p, q)
    return root if left and right else left or right
```

Recursion on trees follows a template: handle the empty case, recurse on children, combine the results.

## 3. Binary search trees (BST)

A **BST** keeps this invariant for every node: all values in the **left** subtree are **smaller**, all in the **right** subtree are **larger**. That makes search a binary search down the tree.

```python
class BST:
    def __init__(self):
        self.root = None

    def insert(self, val):
        if not self.root:
            self.root = TreeNode(val)
            return
        cur = self.root
        while True:
            if val < cur.val:
                if cur.left:
                    cur = cur.left
                else:
                    cur.left = TreeNode(val)
                    return
            else:
                if cur.right:
                    cur = cur.right
                else:
                    cur.right = TreeNode(val)
                    return

    def search(self, val):
        cur = self.root
        while cur:
            if val == cur.val:
                return cur
            cur = cur.left if val < cur.val else cur.right
        return None

    def delete(self, val):
        self.root = self._delete(self.root, val)

    def _delete(self, node, val):
        if not node:
            return None
        if val < node.val:
            node.left = self._delete(node.left, val)
        elif val > node.val:
            node.right = self._delete(node.right, val)
        else:
            if not node.left:               # 0 or 1 child
                return node.right
            if not node.right:
                return node.left
            succ = node.right               # 2 children: inorder successor
            while succ.left:
                succ = succ.left
            node.val = succ.val
            node.right = self._delete(node.right, succ.val)
        return node
```

Validate a BST by passing allowed bounds (checking only parent/child pairs is a classic bug):

```python
def is_valid_bst(node, lo=float("-inf"), hi=float("inf")):
    if not node:
        return True
    if not lo < node.val < hi:
        return False
    return (is_valid_bst(node.left, lo, node.val) and
            is_valid_bst(node.right, node.val, hi))
```

### Complexity

| Operation | Balanced BST | Degenerate (sorted insert, a "linked list") |
|-----------|--------------|----------------------------------------------|
| Search | `O(log n)` | `O(n)` |
| Insert | `O(log n)` | `O(n)` |
| Delete | `O(log n)` | `O(n)` |
| Inorder traversal | `O(n)` | `O(n)` |

Everything depends on **height**. Inserting already-sorted data into a plain BST creates a chain of height `n`.

## 4. Balanced trees

Self-balancing trees keep the height `O(log n)` by **rotating** nodes after inserts and deletes.

| Tree | Idea | Where used |
|------|------|------------|
| **AVL** | Strictly keeps subtree height difference at most 1 | Read-heavy in-memory sets/maps |
| **Red-black** | Colors nodes to guarantee height at most 2 log n | C++ `std::map`, Java `TreeMap`, Linux scheduler |
| **B-tree / B+ tree** | Many keys per node, wide and shallow | Database indexes and file systems |

A rotation re-links a few pointers to shift height from one side to the other while preserving the BST ordering:

```
    y                x
   / \              / \
  x   C   <---->   A   y        (right rotation on y / left rotation on x)
 / \                  / \
A   B                B   C
```

Python has no built-in balanced tree. Use `sortedcontainers.SortedList` or `bisect` on a list when you need ordered data.

## 5. Other tree types in brief

- **N-ary tree / file-system tree:** each node has any number of children.
- **Trie:** tree of characters for prefix search ([trie chapter](../tries/README.md)).
- **Heap:** complete tree stored in an array ([heap chapter](../heaps/README.md)).
- **Segment tree / Fenwick tree:** range queries and updates in `O(log n)`.
- **Expression tree:** leaves are operands, internal nodes are operators; postorder evaluates it.
- **Decision tree:** each node is a question; used in machine learning.

## 6. Two real-world examples

### Example 1: Database indexes (B+ trees)

When you run `CREATE INDEX`, PostgreSQL and MySQL build a **B+ tree**. Each node is sized to a disk page and holds hundreds of keys, so the tree is only 3 or 4 levels deep even for hundreds of millions of rows. A lookup reads 3 or 4 pages instead of scanning the table, turning a full scan into a handful of disk reads. Leaf nodes are linked, so range queries (`WHERE date BETWEEN ...`) scan sequentially.

### Example 2: The file system and the DOM

Your folders and files form a tree: a path like `/home/user/docs/cv.pdf` is a walk from the root. A web page's **DOM** is a tree of HTML elements; CSS selectors and JavaScript traversals walk it, and a browser repaints by diffing trees (React's virtual DOM). Directory listing, `find`, and `du` are tree traversals; `du` computes sizes with a postorder walk, because a folder's size depends on its children.

## 7. Tips, tricks and pitfalls

- **Recursion template:** base case (`None`), recurse left and right, combine. Most tree problems fit it.
- **Pick the traversal by the task:** inorder for sorted BST output, level order for shortest depth, postorder when a node needs its children's results first.
- **BST validation needs bounds,** not just a parent/child comparison.
- **Balance matters.** A BST is only fast when its height is `O(log n)`.
- **Deep recursion** on a skewed tree can raise `RecursionError`; convert to iteration with an explicit stack.
- **Track extra state** with return values (`(height, is_balanced)`) to avoid recomputation and keep `O(n)`.
- **Binary tree vs BST:** a binary tree only limits children to two; the ordering rule belongs to a BST.
- **Lowest common ancestor of a BST** can use ordering; for a general tree use the recursive version above.
- **Draw small examples** (3 to 7 nodes) and trace the recursion.

## 8. Check yourself

1. What is the difference between depth and height?
2. Which traversal of a BST yields sorted order, and why?
3. Why can a BST degrade to `O(n)` search, and how do self-balancing trees fix it?
4. How do you validate a BST correctly?
5. Why do databases use B+ trees instead of binary trees?
6. What are the time and space costs of DFS and BFS on a tree?
7. How do you delete a node with two children in a BST?

<details>
<summary>Answers</summary>

1. Depth counts edges from the root down to a node; height counts edges from a node down to its deepest leaf.
2. Inorder (left, node, right), because everything smaller is on the left and everything larger on the right.
3. Inserting sorted data creates a chain of height `n`. AVL and red-black trees rotate nodes to keep the height `O(log n)`.
4. Pass down a valid `(low, high)` range for each node and check `low < val < high`, tightening the range as you go left or right.
5. B+ trees are wide and shallow (hundreds of keys per page), so a lookup touches very few disk pages, and linked leaves make range scans efficient.
6. Both `O(n)` time. DFS uses `O(h)` space (stack), BFS uses `O(w)` (queue width).
7. Replace its value with the inorder successor (smallest value in the right subtree) or predecessor, then delete that successor node from the right subtree.

</details>

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

Back to the [part overview](../README.md).
