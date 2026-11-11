# Trees: One-Page Summary

## Key facts

- Hierarchical, acyclic. One root, each node one parent. `n` nodes have `n - 1` edges.
- **Depth** = edges from root. **Height** = edges to deepest leaf.
- Binary tree: at most 2 children. **BST**: left < node < right.

### Traversals (all `O(n)`)

| Order | Sequence | Use |
|-------|----------|-----|
| Preorder | root, left, right | Copy, serialize |
| Inorder | left, root, right | Sorted output of a BST |
| Postorder | left, right, root | Delete, sizes, evaluate |
| Level order | BFS with a queue | Shortest depth, per-level work |

### BST costs

| Operation | Balanced | Degenerate |
|-----------|----------|------------|
| Search / insert / delete | `O(log n)` | `O(n)` |

### Balanced trees

- **AVL** (strict), **red-black** (looser, fewer rotations), **B/B+ tree** (wide and shallow for disks and databases).
- Rotations restore balance while keeping BST order.

### Patterns

- Recursion template: base case, recurse children, combine.
- Return extra state (`height`, `is_balanced`) to stay `O(n)`.
- Validate a BST with `(low, high)` bounds.
- Delete with two children: swap in the inorder successor.
- LCA: BST uses ordering; general tree recurses on both sides.

## Pitfalls

- Comparing only parent and child when validating a BST.
- Skewed trees cause deep recursion.
- Confusing "binary tree" with "binary search tree".

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Binary Trees and Traversals](01-binary-trees-and-traversals.md) · [Binary Search Trees](02-binary-search-trees.md) · [Balanced Trees](03-balanced-trees-avl.md) · [Segment Trees and Fenwick Trees](04-segment-and-fenwick-trees.md)
