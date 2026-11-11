# Part 02: Data Structures

A **data structure** is a way of organizing data so the operations you need are fast. Choosing the right one is often the difference between a program that finishes in a blink and one that never finishes. This part teaches every structure from first principles, with runnable Python, step-by-step traces, practice problems and self-checks.

**Prerequisites:** [Part 00 foundations](../00-foundations/README.md) (Python, memory, recursion) and [Part 01 complexity](../01-complexity/README.md) (Big-O). If `O(n)` versus `O(log n)` is new to you, read Part 01 first.

## Topics in this part

Read the topics in this order. Each has an overview, detailed lessons, exercises with solutions and a one-page summary (the full map is in the [index](../INDEX.md)).

<!-- topics:start -->
| Topic | Lessons | Exercises | Summary |
|-------|---------|-----------|---------|
| Arrays and Strings | [overview](arrays-strings/README.md)<br>[Arrays](arrays-strings/01-arrays-and-memory.md)<br>[Working with Arrays](arrays-strings/02-array-techniques.md)<br>[Strings in Depth](arrays-strings/03-strings-in-depth.md) | [ex](arrays-strings/exercises.md) | [sum](arrays-strings/summary.md) |
| Linked Lists | [overview](linked-lists/README.md)<br>[The Singly Linked List, Built from Scratch](linked-lists/01-singly-linked-list.md)<br>[Doubly Linked Lists, Circular Lists and the LRU Cache](linked-lists/02-doubly-and-circular.md)<br>[Linked-List Techniques and Classic Problems](linked-lists/03-linked-list-techniques.md) | [ex](linked-lists/exercises.md) | [sum](linked-lists/summary.md) |
| Stacks and Queues | [overview](stacks-queues/README.md)<br>[Stacks](stacks-queues/01-stacks.md)<br>[Queues, Deques and Priority Queues](stacks-queues/02-queues-deques-priority-queues.md)<br>[Stack and Queue Applications](stacks-queues/03-stack-and-queue-applications.md) | [ex](stacks-queues/exercises.md) | [sum](stacks-queues/summary.md) |
| Hash Tables | [overview](hash-tables/README.md)<br>[Hash Functions and Collisions](hash-tables/01-hash-functions-and-collisions.md)<br>[Implementing Hash Tables](hash-tables/02-implementing-hash-tables.md)<br>[Dict, Set, Hash-Map Patterns, Bloom Filters and Consistent Hashing](hash-tables/03-dict-set-internals-and-bloom-filters.md) | [ex](hash-tables/exercises.md) | [sum](hash-tables/summary.md) |
| Trees | [overview](trees/README.md)<br>[Binary Trees and Traversals](trees/01-binary-trees-and-traversals.md)<br>[Binary Search Trees](trees/02-binary-search-trees.md)<br>[Balanced Trees](trees/03-balanced-trees-avl.md)<br>[Segment Trees and Fenwick Trees](trees/04-segment-and-fenwick-trees.md) | [ex](trees/exercises.md) | [sum](trees/summary.md) |
| Heaps and Priority Queues | [overview](heaps/README.md)<br>[Binary Heaps and Heapsort](heaps/01-binary-heaps-and-heapsort.md)<br>[Priority Queue Applications](heaps/02-priority-queue-applications.md) | [ex](heaps/exercises.md) | [sum](heaps/summary.md) |
| Tries | [overview](tries/README.md)<br>[Tries](tries/01-tries.md) | [ex](tries/exercises.md) | [sum](tries/summary.md) |
| Graphs | [overview](graphs/README.md)<br>[Graph Basics](graphs/01-graph-basics-bfs-dfs.md)<br>[Graph Algorithms](graphs/02-graph-algorithms.md)<br>[Union-Find](graphs/03-union-find.md) | [ex](graphs/exercises.md) | [sum](graphs/summary.md) |
<!-- topics:end -->

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

Back to the [handbook home](../README.md) · [index](../INDEX.md).
