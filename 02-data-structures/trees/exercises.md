# Trees: Exercises

Use this node and helper for testing:

```python
class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val, self.left, self.right = val, left, right

def from_list(vals):
    """Build a tree from a level-order list; None means no node."""
    if not vals or vals[0] is None:
        return None
    from collections import deque
    root = TreeNode(vals[0])
    q, i = deque([root]), 1
    while q and i < len(vals):
        node = q.popleft()
        if i < len(vals) and vals[i] is not None:
            node.left = TreeNode(vals[i]); q.append(node.left)
        i += 1
        if i < len(vals) and vals[i] is not None:
            node.right = TreeNode(vals[i]); q.append(node.right)
        i += 1
    return root
```

## Problems
1. Compute the **maximum depth** of a binary tree.
2. **Invert** a binary tree.
3. Check if two trees are **identical**.
4. Check if a tree is **symmetric**.
5. **Level order traversal** returning a list of levels.
6. **Validate** a binary search tree.
7. Find the **lowest common ancestor** of two nodes in a BST.
8. **Diameter** of a binary tree (longest path between any two nodes, in edges).
9. Return the **k-th smallest** value in a BST.
10. Check if a tree is **height-balanced** in `O(n)`.
11. Build a binary tree from **preorder and inorder** traversals.
12. **Serialize and deserialize** a binary tree.

<details>
<summary>Solutions</summary>

```python
from collections import deque

# 1
def max_depth(n):
    return 0 if not n else 1 + max(max_depth(n.left), max_depth(n.right))

# 2
def invert(n):
    if n:
        n.left, n.right = invert(n.right), invert(n.left)
    return n

# 3
def is_same(a, b):
    if not a and not b:
        return True
    if not a or not b or a.val != b.val:
        return False
    return is_same(a.left, b.left) and is_same(a.right, b.right)

# 4
def is_symmetric(root):
    def mirror(a, b):
        if not a and not b:
            return True
        if not a or not b or a.val != b.val:
            return False
        return mirror(a.left, b.right) and mirror(a.right, b.left)
    return mirror(root, root)

# 5
def level_order(root):
    if not root:
        return []
    out, q = [], deque([root])
    while q:
        level = []
        for _ in range(len(q)):
            n = q.popleft()
            level.append(n.val)
            if n.left: q.append(n.left)
            if n.right: q.append(n.right)
        out.append(level)
    return out

# 6
def is_valid_bst(n, lo=float("-inf"), hi=float("inf")):
    if not n:
        return True
    if not lo < n.val < hi:
        return False
    return is_valid_bst(n.left, lo, n.val) and is_valid_bst(n.right, n.val, hi)

# 7
def lca_bst(root, p, q):
    while root:
        if p < root.val and q < root.val:
            root = root.left
        elif p > root.val and q > root.val:
            root = root.right
        else:
            return root

# 8
def diameter(root):
    best = 0
    def depth(n):
        nonlocal best
        if not n:
            return 0
        l, r = depth(n.left), depth(n.right)
        best = max(best, l + r)
        return 1 + max(l, r)
    depth(root)
    return best

# 9
def kth_smallest(root, k):
    stack, cur = [], root
    while cur or stack:
        while cur:
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()
        k -= 1
        if k == 0:
            return cur.val
        cur = cur.right

# 10
def is_balanced(root):
    def check(n):                       # returns height, or -1 if unbalanced
        if not n:
            return 0
        l = check(n.left)
        if l == -1:
            return -1
        r = check(n.right)
        if r == -1 or abs(l - r) > 1:
            return -1
        return 1 + max(l, r)
    return check(root) != -1

# 11
def build_tree(preorder, inorder):
    index = {v: i for i, v in enumerate(inorder)}
    it = iter(preorder)
    def build(lo, hi):
        if lo > hi:
            return None
        val = next(it)
        node = TreeNode(val)
        mid = index[val]
        node.left = build(lo, mid - 1)
        node.right = build(mid + 1, hi)
        return node
    return build(0, len(inorder) - 1)

# 12
def serialize(root):
    out = []
    def go(n):
        if not n:
            out.append("#")
            return
        out.append(str(n.val))
        go(n.left)
        go(n.right)
    go(root)
    return ",".join(out)

def deserialize(data):
    it = iter(data.split(","))
    def go():
        v = next(it)
        if v == "#":
            return None
        node = TreeNode(int(v))
        node.left = go()
        node.right = go()
        return node
    return go()
```

</details>

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Binary Trees and Traversals](01-binary-trees-and-traversals.md) · [Binary Search Trees](02-binary-search-trees.md) · [Balanced Trees](03-balanced-trees-avl.md) · [Segment Trees and Fenwick Trees](04-segment-and-fenwick-trees.md)
