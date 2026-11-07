# Part 02: Data Structures

A **data structure** is a way of organizing data so the operations you need are fast. Choosing the right one is often the difference between a program that finishes in a blink and one that never finishes. This part teaches every structure from first principles, with runnable Python, step-by-step traces, practice problems and self-checks.

**Prerequisites:** [Part 00 foundations](../00-foundations/README.md) (Python, memory, recursion) and [Part 01 complexity](../01-complexity/README.md) (Big-O). If `O(n)` versus `O(log n)` is new to you, read Part 01 first.

## Reading order

| # | Structure | Lessons | Core idea |
|---|-----------|---------|-----------|
| 1 | [Arrays and strings](arrays-strings/README.md) | [arrays and memory](arrays-strings/01-arrays-and-memory.md), [techniques](arrays-strings/02-array-techniques.md), [strings](arrays-strings/03-strings-in-depth.md) | contiguous memory, instant indexing |
| 2 | [Linked lists](linked-lists/README.md) | [singly](linked-lists/01-singly-linked-list.md), [doubly and circular](linked-lists/02-doubly-and-circular.md), [techniques](linked-lists/03-linked-list-techniques.md) | nodes joined by pointers, cheap inserts |
| 3 | [Stacks and queues](stacks-queues/README.md) | [stacks](stacks-queues/01-stacks.md), [queues](stacks-queues/02-queues-deques-priority-queues.md), [applications](stacks-queues/03-stack-and-queue-applications.md) | last-in-first-out and first-in-first-out |
| 4 | [Hash tables](hash-tables/README.md) | [hashing](hash-tables/01-hash-functions-and-collisions.md), [implementing](hash-tables/02-implementing-hash-tables.md), [dict/set and Bloom filters](hash-tables/03-dict-set-internals-and-bloom-filters.md) | key to slot in `O(1)` |
| 5 | [Trees](trees/README.md) | [traversals](trees/01-binary-trees-and-traversals.md), [BST](trees/02-binary-search-trees.md), [balanced](trees/03-balanced-trees-avl.md), [segment/Fenwick](trees/04-segment-and-fenwick-trees.md) | hierarchy, halving the search |
| 6 | [Heaps](heaps/README.md) | [binary heaps](heaps/01-binary-heaps-and-heapsort.md), [applications](heaps/02-priority-queue-applications.md) | always know the minimum |
| 7 | [Tries](tries/README.md) | [tries](tries/01-tries.md) | one character per step: prefix search |
| 8 | [Graphs](graphs/README.md) | [BFS/DFS](graphs/01-graph-basics-bfs-dfs.md), [algorithms](graphs/02-graph-algorithms.md), [union-find](graphs/03-union-find.md) | things and their connections |

Each folder also has a quick-reference README, an `exercises.md` and a one-page `summary.md`.

## Which structure should I use?

| I need to... | Reach for |
|--------------|-----------|
| Access item number `i` | list (array) |
| Look up by a key, count things, remove duplicates | `dict` / `set` |
| Process in arrival order | `collections.deque` (queue) |
| Undo, match brackets, backtrack | list as a stack |
| Always get the smallest/largest next | `heapq` (heap) |
| Keep items sorted with fast search and insert | balanced tree, or sorted list + `bisect` |
| Prefix search, autocomplete | trie |
| Model connections, find routes, order tasks | graph (adjacency list) |
| Range sums with updates | Fenwick or segment tree |
| "Are these two connected?" while links arrive | union-find |
| Cheap "definitely not present" check | Bloom filter |

## Cost cheat sheet (average case)

| Structure | Access by index | Search | Insert | Delete | Notes |
|-----------|-----------------|--------|--------|--------|-------|
| Array / list | `O(1)` | `O(n)` | `O(n)` (end: `O(1)` amortized) | `O(n)` | |
| Linked list | `O(n)` | `O(n)` | `O(1)` at a known node | `O(1)` at a known node | |
| Stack / queue (deque) | - | `O(n)` | `O(1)` | `O(1)` at the ends | |
| Hash table | - | `O(1)` | `O(1)` | `O(1)` | worst case `O(n)` |
| Balanced BST | - | `O(log n)` | `O(log n)` | `O(log n)` | sorted order |
| Heap | - | `O(n)` | `O(log n)` | `O(log n)` (min) | min in `O(1)` |
| Trie | - | `O(L)` | `O(L)` | `O(L)` | `L` = key length |
| Graph (adjacency list) | - | `O(V + E)` traversal | `O(1)` add edge | `O(degree)` | |

## How to study this part

1. Read a lesson, then **type and run every example**; change the input and predict the output first.
2. Do the **Practice** problems before opening the collapsible solutions.
3. Answer **Check yourself** from memory; revisit anything you missed tomorrow.
4. After each structure, solve three or four problems on a site like LeetCode or NeetCode to make the patterns stick.

Next: [Part 03: Algorithms](../03-algorithms/README.md)
