# Binary Trees and Traversals

**Prerequisites:** [linked lists](../linked-lists/01-singly-linked-list.md), [recursion](../../00-foundations/python-fundamentals/README.md), [stacks and queues](../stacks-queues/01-stacks.md). **You will learn:** tree vocabulary, how to build a binary tree, the four traversals (preorder, inorder, postorder, level-order) both recursively and iteratively, and the classic tree questions (height, size, symmetry, paths, lowest common ancestor).

## 1. In plain words

A list is a chain. A **tree** is a chain that *branches*: a family tree, a folder structure, an HTML page, a company org chart. Every tree has one **root** at the top; each item (**node**) can have **children** below it.

```text
          8            <- root (depth 0)
        /   \
       3     10        <- internal nodes
      / \      \
     1   6      14     <- 1 and 6 are children of 3; 14 is a child of 10
        / \    /
       4   7  13       <- leaves (no children)
```

## 2. Vocabulary

| Term | Meaning |
|------|---------|
| **Root** | the top node (no parent) |
| **Parent / child / sibling** | direct relations |
| **Leaf** | a node with no children |
| **Edge** | link between parent and child |
| **Depth** of a node | edges from the root down to it |
| **Height** of a tree | edges on the longest root-to-leaf path |
| **Subtree** | a node plus everything below it |
| **Binary tree** | each node has at most **two** children, called *left* and *right* |
| **Full / perfect / complete** | full: 0 or 2 children each; perfect: all levels completely filled; complete: all levels filled except possibly the last, filled left to right |

A tree with `n` nodes always has **`n - 1` edges**. A perfect tree of height `h` has `2^(h+1) - 1` nodes, so height is about **`log₂ n`** when balanced and up to **`n - 1`** when it degenerates into a chain.

## 3. Building a binary tree

```python
class TreeNode:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

#        1
#       / \
#      2   3
#     / \   \
#    4   5   6
root = TreeNode(1,
        TreeNode(2, TreeNode(4), TreeNode(5)),
        TreeNode(3, None, TreeNode(6)))

def height(node):                       # edges on the longest path; an empty tree has height -1
    if node is None:
        return -1
    return 1 + max(height(node.left), height(node.right))

def count_nodes(node):
    return 0 if node is None else 1 + count_nodes(node.left) + count_nodes(node.right)

print(height(root), count_nodes(root))  # 2 6
```

**The tree mindset:** almost every tree function has the same shape: *handle the empty case, solve the left subtree, solve the right subtree, combine.* Trust the recursion.

## 4. The four traversals

Visiting every node exactly once can be done in different orders. The first three are **depth-first** (go deep before wide); the last is **breadth-first**.

| Name | Order | Typical use |
|------|-------|-------------|
| **Preorder** | node, left, right | copy a tree, serialize it, prefix expressions |
| **Inorder** | left, node, right | read a BST in **sorted order** |
| **Postorder** | left, right, node | delete a tree, compute sizes/heights, postfix expressions |
| **Level-order** | level by level | shortest path, printing by depth |

```python
def preorder(n):  return [] if n is None else [n.value] + preorder(n.left) + preorder(n.right)
def inorder(n):   return [] if n is None else inorder(n.left) + [n.value] + inorder(n.right)
def postorder(n): return [] if n is None else postorder(n.left) + postorder(n.right) + [n.value]

print(preorder(root))       # [1, 2, 4, 5, 3, 6]
print(inorder(root))        # [4, 2, 5, 1, 3, 6]
print(postorder(root))      # [4, 5, 2, 6, 3, 1]
```

Trace of inorder on the small tree `2` with children `4`, `5`: go left (`4`, no children, emit 4), emit 2, go right (emit 5): `[4, 2, 5]`.

A memory trick: the word says *when the node is visited relative to its children*: **pre**order = node **before**, **in**order = node **in between**, **post**order = node **after**.

### Level-order (breadth-first)

```python
from collections import deque

def level_order(n):
    result, queue = [], deque([n] if n else [])
    while queue:
        level = []
        for _ in range(len(queue)):               # process exactly one level
            node = queue.popleft()
            level.append(node.value)
            for child in (node.left, node.right):
                if child:
                    queue.append(child)
        result.append(level)
    return result

print(level_order(root))    # [[1], [2, 3], [4, 5, 6]]
```

### Iterative versions (no recursion)

Recursion uses the call stack; we can use our own stack. This matters for very deep (degenerate) trees where recursion would hit Python's limit.

```python
def inorder_iterative(root):
    result, stack, node = [], [], root
    while stack or node:
        while node:                       # go as far left as possible
            stack.append(node)
            node = node.left
        node = stack.pop()
        result.append(node.value)         # visit
        node = node.right                 # then handle the right subtree
    return result

def preorder_iterative(root):
    result, stack = [], [root] if root else []
    while stack:
        node = stack.pop()
        result.append(node.value)
        if node.right: stack.append(node.right)     # push right first so left is processed first
        if node.left:  stack.append(node.left)
    return result

print(inorder_iterative(root), preorder_iterative(root))
# [4, 2, 5, 1, 3, 6] [1, 2, 4, 5, 3, 6]
```

All traversals visit each node once: **`O(n)` time**. Space is **`O(h)`** (the stack or call depth), `O(log n)` balanced, `O(n)` for a chain; level-order uses `O(w)` where `w` is the widest level.

## 5. Classic tree questions

```python
def is_symmetric(root):
    def mirror(a, b):
        if a is None and b is None: return True
        if a is None or b is None or a.value != b.value: return False
        return mirror(a.left, b.right) and mirror(a.right, b.left)
    return root is None or mirror(root.left, root.right)

def max_path_sum(root):                # best sum on any downward path from the root to a leaf
    if root is None: return 0
    return root.value + max(max_path_sum(root.left), max_path_sum(root.right))

def all_root_to_leaf_paths(node, prefix=()):
    if node is None: return []
    prefix = prefix + (node.value,)
    if not node.left and not node.right:
        return [prefix]
    return all_root_to_leaf_paths(node.left, prefix) + all_root_to_leaf_paths(node.right, prefix)

def lowest_common_ancestor(node, a, b):
    if node is None or node.value in (a, b):
        return node
    left = lowest_common_ancestor(node.left, a, b)
    right = lowest_common_ancestor(node.right, a, b)
    return node if left and right else left or right      # both sides found something: this is the split point

def diameter(root):                    # longest path (in edges) between any two nodes
    best = 0
    def depth(n):
        nonlocal best
        if n is None: return 0
        l, r = depth(n.left), depth(n.right)
        best = max(best, l + r)
        return 1 + max(l, r)
    depth(root)
    return best

print(is_symmetric(root))                               # False
print(max_path_sum(root))                               # 10
print(all_root_to_leaf_paths(root))                     # [(1, 2, 4), (1, 2, 5), (1, 3, 6)]
print(lowest_common_ancestor(root, 4, 5).value)         # 2
print(lowest_common_ancestor(root, 4, 6).value)         # 1
print(diameter(root))                                   # 4
```

### Building a tree from two traversals

An inorder list **plus** a preorder list identify a unique tree (when values are distinct): the first preorder item is the root; it splits the inorder list into left and right parts.

```python
def build_tree(preorder_list, inorder_list):
    if not preorder_list:
        return None
    root_value = preorder_list[0]
    split = inorder_list.index(root_value)
    left = build_tree(preorder_list[1:1 + split], inorder_list[:split])
    right = build_tree(preorder_list[1 + split:], inorder_list[split + 1:])
    return TreeNode(root_value, left, right)

rebuilt = build_tree([1, 2, 4, 5, 3, 6], [4, 2, 5, 1, 3, 6])
print(level_order(rebuilt))         # [[1], [2, 3], [4, 5, 6]]
```

## 6. Representing a tree in an array

A **complete** binary tree fits in a list with no pointers: for index `i`, the left child is `2i + 1`, the right child `2i + 2`, the parent `(i - 1) // 2`. This is how [heaps](../heaps/README.md) are stored.

```python
tree_array = [1, 2, 3, 4, 5, None, 6]
i = 1
print(tree_array[2 * i + 1], tree_array[2 * i + 2], tree_array[(i - 1) // 2])      # 4 5 1
```

## 7. Beyond binary: general trees

A node with any number of children keeps a **list of children**; the same traversals apply.

```python
class Folder:
    def __init__(self, name, children=()):
        self.name, self.children = name, list(children)

disk = Folder("root", [Folder("docs", [Folder("cv.pdf")]), Folder("src", [Folder("app.py"), Folder("utils.py")])])

def show(node, indent=0):
    print("  " * indent + node.name)
    for child in node.children:
        show(child, indent + 1)
show(disk)
# root
#   docs
#     cv.pdf
#   src
#     app.py
#     utils.py
```

## 8. Two real-world examples

**Example 1: The HTML DOM.** A browser parses a page into a tree of elements. Finding an element (`querySelector`) is a depth-first search, and CSS inheritance flows from parent to child.

**Example 2: File systems and `du`.** The total size of a folder is a **postorder** computation: you only know a folder's size after summing its children's.

## 9. Common mistakes

- Forgetting the base case `if node is None`.
- Confusing **depth** (from the top) with **height** (from the bottom), and counting nodes versus edges (decide, and be consistent).
- Using inorder on a general binary tree and expecting sorted output (that only holds for a **binary search tree**).
- Recursing on a very deep tree and hitting `RecursionError`; use the iterative versions.
- Modifying a tree while traversing it without care.

## 10. Practice

1. List preorder, inorder, postorder for a tree with root 7, left child 3, right child 9.
2. How many nodes does a perfect binary tree of height 4 have?
3. Write `count_leaves(node)`.
4. Write `mirror(node)` that swaps left and right children everywhere.
5. Write `is_same_tree(a, b)`.
6. Write `right_side_view(root)` returning the last node of each level.
7. What is the height of a tree with one node? An empty tree?

<details>
<summary>Solutions</summary>

1. Preorder `7 3 9`, inorder `3 7 9`, postorder `3 9 7`.
2. `2^(4+1) - 1 = 31`.
3. ```python
   def count_leaves(n):
       if n is None: return 0
       if not n.left and not n.right: return 1
       return count_leaves(n.left) + count_leaves(n.right)
   print(count_leaves(root))                      # 3
   ```
4. ```python
   def mirror(n):
       if n:
           n.left, n.right = mirror(n.right), mirror(n.left)
       return n
   print(level_order(mirror(build_tree([1, 2, 4, 5, 3, 6], [4, 2, 5, 1, 3, 6]))))      # [[1], [3, 2], [6, 5, 4]]
   ```
5. ```python
   def is_same_tree(a, b):
       if a is None or b is None: return a is b
       return a.value == b.value and is_same_tree(a.left, b.left) and is_same_tree(a.right, b.right)
   print(is_same_tree(root, root), is_same_tree(root, root.left))      # True False
   ```
6. ```python
   def right_side_view(root):
       return [level[-1] for level in level_order(root)]
   print(right_side_view(root))                   # [1, 3, 6]
   ```
7. One node: height 0 (edges). Empty tree: -1 (or 0 if you count nodes; be consistent).

</details>

## 11. Check yourself

1. Which traversal gives a BST in sorted order?
2. What is the time and space of a traversal?
3. What data structure does level-order use? Iterative DFS?
4. How are the children of index `i` found in an array tree?
5. Why can one traversal alone not rebuild a tree, but two can?

<details>
<summary>Answers</summary>

1. Inorder.
2. `O(n)` time; space `O(h)` for DFS (stack/call depth), `O(width)` for BFS.
3. A queue; a stack.
4. `2i + 1` and `2i + 2`.
5. Different shapes can share one traversal order; preorder gives the root and inorder tells you which nodes are on each side.

</details>

[Back to trees](README.md) · Next: [binary search trees](02-binary-search-trees.md)
