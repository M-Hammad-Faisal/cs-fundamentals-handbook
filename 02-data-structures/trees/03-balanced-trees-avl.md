# Balanced Trees: AVL, Red-Black and B-Trees

**Prerequisites:** [binary search trees](02-binary-search-trees.md). **You will learn:** why plain BSTs can go wrong, what **balance** means, how **rotations** fix it, a complete **AVL tree** you can run, and how **red-black trees** and **B-trees** (the structure behind databases) take the same idea further.

## 1. The problem

Insert `1, 2, 3, 4, 5` into a plain BST and you get a chain: search costs `O(n)`. A **self-balancing** tree notices when one side gets too tall and **reorganizes locally** after each insert or delete so the height stays `O(log n)`.

## 2. Rotations: the one trick

A **rotation** changes the shape of a small part of the tree while keeping the BST ordering intact (inorder stays the same).

```text
Right rotation at y                 Left rotation at x
      y                x                x                  y
     / \             /   \             / \               /   \
    x   C    --->   A     y    <---   A   y     ...      x     C
   / \                   / \             / \            / \
  A   B                 B   C           B   C          A   B
```

The middle subtree `B` switches parents: it was between `x` and `y` in sorted order and still is.

## 3. AVL trees

An **AVL tree** (Adelson-Velsky and Landis, 1962) stores each node's **height** and enforces:

> For every node, the heights of its left and right subtrees differ by **at most 1**.

The **balance factor** is `height(left) - height(right)`, which must be `-1`, `0` or `+1`. After an insert or delete, walk back up and fix any node whose factor becomes `±2` with rotations. There are four cases:

| Case | Where the heavy side is | Fix |
|------|-------------------------|-----|
| Left-Left | left child's left subtree | one **right** rotation |
| Right-Right | right child's right subtree | one **left** rotation |
| Left-Right | left child's right subtree | rotate the child **left**, then the node **right** |
| Right-Left | right child's left subtree | rotate the child **right**, then the node **left** |

```python
class AVLNode:
    def __init__(self, key):
        self.key = key
        self.left = self.right = None
        self.height = 0                     # a single node has height 0

def height(n):
    return -1 if n is None else n.height

def update(n):
    n.height = 1 + max(height(n.left), height(n.right))

def balance_factor(n):
    return height(n.left) - height(n.right)

def rotate_right(y):
    x = y.left
    y.left, x.right = x.right, y            # x becomes the new root of this subtree
    update(y); update(x)
    return x

def rotate_left(x):
    y = x.right
    x.right, y.left = y.left, x
    update(x); update(y)
    return y

def rebalance(n):
    update(n)
    bf = balance_factor(n)
    if bf > 1:                              # left side too tall
        if balance_factor(n.left) < 0:      # left-right case: first straighten the child
            n.left = rotate_left(n.left)
        return rotate_right(n)
    if bf < -1:                             # right side too tall
        if balance_factor(n.right) > 0:     # right-left case
            n.right = rotate_right(n.right)
        return rotate_left(n)
    return n

def insert(n, key):
    if n is None:
        return AVLNode(key)
    if key < n.key:
        n.left = insert(n.left, key)
    elif key > n.key:
        n.right = insert(n.right, key)
    else:
        return n                            # ignore duplicates
    return rebalance(n)

def delete(n, key):
    if n is None:
        return None
    if key < n.key:
        n.left = delete(n.left, key)
    elif key > n.key:
        n.right = delete(n.right, key)
    else:
        if n.left is None: return n.right
        if n.right is None: return n.left
        successor = n.right
        while successor.left:
            successor = successor.left
        n.key = successor.key
        n.right = delete(n.right, successor.key)
    return rebalance(n)

def inorder(n):
    return [] if n is None else inorder(n.left) + [n.key] + inorder(n.right)

def is_balanced(n):
    return n is None or (abs(balance_factor(n)) <= 1 and is_balanced(n.left) and is_balanced(n.right))
```

### Watching it work

```python
root = None
for k in [1, 2, 3, 4, 5, 6, 7]:         # the sorted input that wrecks a plain BST
    root = insert(root, k)
print(inorder(root), height(root))      # [1, 2, 3, 4, 5, 6, 7] 2
print(root.key, root.left.key, root.right.key)       # 4 2 6   (perfectly balanced)
```

Trace of the first rotations:

```text
insert 1:   1
insert 2:   1            (right-heavy by 1: fine)
             \
              2
insert 3:   1            balance factor of 1 is -2 (right-right case) -> rotate left at 1
             \                     2
              2          ---->    / \
               \                 1   3
                3
insert 4, 5: 5 makes 3 unbalanced -> rotate left at 3 ...
```

```python
import random
big = None
keys = list(range(1, 1001))              # 1000 keys inserted in sorted order
for k in keys:
    big = insert(big, k)
print(height(big), is_balanced(big))     # 9 True    (a plain BST would have height 999)

random.seed(3)
for k in random.sample(keys, 600):       # delete 600 random keys
    big = delete(big, k)
print(len(inorder(big)), height(big), is_balanced(big))      # 400 9 True   (still balanced)
```

An AVL tree with `n` nodes has height at most about `1.44 · log₂ n`, so **search, insert and delete are `O(log n)` guaranteed**, even for sorted input. A rotation is `O(1)` and an insert needs at most one rebalancing (a delete may need up to `O(log n)` rotations).

## 4. Red-black trees (the idea)

A **red-black tree** colors every node red or black and keeps these rules:

1. The root is black.
2. A red node has no red child.
3. Every path from a node to its empty descendants has the **same number of black nodes**.

These rules guarantee that the longest path is at most **twice** the shortest, so height stays `O(log n)`. Compared with AVL:

| | AVL | Red-black |
|---|-----|-----------|
| Balance strictness | tighter (shorter tree: faster **lookups**) | looser |
| Insert/delete | more rotations | fewer rotations (faster **updates**) |
| Used in | databases and read-heavy workloads | Linux scheduler, C++ `std::map`, Java `TreeMap` |

You rarely implement a red-black tree yourself; you should know it exists and why it is the default balanced tree in standard libraries.

## 5. B-trees: trees built for disks

Reading from disk or SSD happens in **pages** (4 KB or more) and is thousands of times slower than memory. A binary tree has to follow about `log₂ n` pointers (one page read each). A **B-tree** puts **many keys in each node** (hundreds), so the tree is very short and each step reads one page.

```text
Order-4 B-tree node holds up to 3 keys and 4 children:

              [ 20 | 50 ]
             /     |      \
   [5 | 10 | 15] [30 | 40] [60 | 70 | 80]
```

- All leaves are at the **same depth**: perfectly balanced by construction.
- A full node **splits** in two and pushes its middle key up (this is how the tree grows *upward*).
- A node with too few keys **borrows from or merges** with a sibling.

```python
import math
for n in (1_000_000, 1_000_000_000):
    print(n, "keys: binary tree depth about", math.ceil(math.log2(n)),
          "| B-tree with 500 keys per node depth about", math.ceil(math.log(n, 500)))
# 1000000 keys: binary tree depth about 20 | B-tree with 500 keys per node depth about 3
# 1000000000 keys: binary tree depth about 30 | B-tree with 500 keys per node depth about 4
```

A billion rows found in 4 page reads: this is why almost every relational database (PostgreSQL, MySQL/InnoDB, SQLite) stores indexes as **B+ trees** (a B-tree variant that keeps all values in linked leaves, making range scans fast). See [databases and indexes](../../05-databases/README.md).

## 6. Other balanced and related structures (names to know)

| Structure | One-line idea |
|-----------|---------------|
| **Splay tree** | moves recently accessed nodes to the root |
| **Treap** | BST by key plus heap by random priority: balanced in expectation |
| **Skip list** | layered linked lists; probabilistically `O(log n)` (used by Redis sorted sets) |
| **Trie** | tree keyed by characters: [see tries](../tries/README.md) |
| **Segment tree / Fenwick tree** | trees for fast range sums: [next lesson](04-segment-and-fenwick-trees.md) |

## 7. Two real-world examples

**Example 1: Ordered database index.** `SELECT ... WHERE price BETWEEN 10 AND 20 ORDER BY price` walks a B+ tree to the first match and then scans the linked leaves: logarithmic start, sequential reads after.

**Example 2: Calendar and booking systems.** An ordered set of reservations (a balanced tree) answers "is 3:00-3:30 free?" by finding the neighboring bookings in `O(log n)`.

## 8. Common mistakes

- Forgetting to update the **height** after rotating (the most common AVL bug).
- Doing a single rotation in the left-right or right-left case.
- Rotating the wrong node or losing a subtree (draw it first).
- Checking balance only at the root instead of every node.
- Implementing balanced trees in production when `sorted list + bisect`, `dict`, or a library already does the job.

## 9. Practice

1. Insert 10, 20, 30 into an AVL tree by hand. Which case occurs and what is the result?
2. Insert 30, 10, 20. Which case occurs?
3. What is the maximum height of an AVL tree with 7 nodes? The minimum?
4. Add a function `avl_search(n, key)` and a `min_key(n)`.
5. Why does a B-tree grow at the root instead of the leaves?
6. Why is a database index a B-tree instead of an AVL tree?

<details>
<summary>Solutions</summary>

1. Right-right case; one left rotation gives root 20 with children 10 and 30.
2. Left-right case: rotate 10 left (20 becomes the left child of 30 with 10 beneath), then rotate 30 right, giving root 20 with children 10 and 30.
3. Minimum height 2 (a perfect tree has 7 nodes). Maximum height 3: the fewest nodes an AVL tree of height `h` can have is `N(h) = N(h-1) + N(h-2) + 1` with `N(0)=1, N(1)=2`, giving `N(2)=4` and `N(3)=7`, so 7 nodes can just reach height 3 but never 4 (which needs 12).
4. ```python
   def avl_search(n, key):
       while n:
           if key == n.key: return True
           n = n.left if key < n.key else n.right
       return False
   def min_key(n):
       while n.left: n = n.left
       return n.key
   print(avl_search(root, 5), avl_search(root, 99), min_key(root))      # True False 1
   ```
5. Splitting a full root creates a new root above it, so every leaf stays at the same depth.
6. A B-tree node holds hundreds of keys, so lookups touch far fewer disk pages than the many nodes a binary tree would visit.

</details>

## 10. Check yourself

1. What does the AVL balance condition say?
2. What does a rotation preserve?
3. Name the four AVL imbalance cases.
4. Why do standard libraries often prefer red-black trees?
5. What is the advantage of B-trees on disk?

<details>
<summary>Answers</summary>

1. Subtree heights of every node differ by at most 1.
2. The inorder (sorted) order, while changing the shape.
3. Left-left, right-right, left-right, right-left.
4. They rotate less often, so inserts and deletes are cheaper, while still `O(log n)`.
5. Very high fan-out means few levels and few page reads.

</details>

[Back to trees](README.md) · Previous: [binary search trees](02-binary-search-trees.md) · Next: [segment and Fenwick trees](04-segment-and-fenwick-trees.md)
