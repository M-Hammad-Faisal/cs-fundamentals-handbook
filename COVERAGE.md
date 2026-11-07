# Coverage Audit and Roadmap

This page records an honest audit of the handbook: what is deep, what is thin, what is missing, and the plan to close the gaps. The target reader is a **second-year computer science student** who may be meeting a topic for the first time, so every topic should explain *what it is*, *why it exists*, *how it works step by step*, show *runnable code*, list *common mistakes*, and end with *practice and self-check questions*.

## Quality bar for every topic file

1. **Prerequisites and learning objectives** at the top.
2. **In plain words** with an everyday analogy.
3. **How it works**, traced step by step on a small example (diagrams in text).
4. **Code** that runs, with checked output.
5. **Complexity / trade-offs / when to use it and when not to.**
6. **Common mistakes** and **two real-world examples.**
7. **Practice** (with solutions) and **Check yourself** (with answers).
8. **One topic per file**, grouped in folders, with an overview README that gives the learning path.

## Audit results (before this pass)

| Part | Depth before | Main gaps |
|------|--------------|-----------|
| 00 Career path | Good overview | Needs a "start here" guide, learning paths and a glossary |
| (missing) Foundations | None | Binary/data representation, how a computer runs a program, math for CS, Python fundamentals, command line and Git, environment setup |
| 01 Complexity | 1 file (273 lines) | Needs separate files: what an algorithm is, Big-O in depth, space complexity, amortized analysis, recurrences, analyzing real code |
| 02 Data structures | 8 files, each bundling many topics (150-315 lines) | Split into one file per structure/variant (e.g. singly/doubly/circular lists, BST/AVL/B-tree, graph representations and traversals), add union-find, segment tree, Fenwick tree, Bloom filter, LRU, deque and more |
| 03 Algorithms | 6 files bundling many algorithms | One file per algorithm family member (each sort, each search, classic DP problems, each graph algorithm), plus divide and conquer, string algorithms, number theory |
| 04 OOP | Strong (9 chapters, 25 pattern files) | Add UML and class diagrams, and an OOP-from-scratch primer for beginners |
| 05 Databases | 5 files (200-400 lines), SQL lesson has no runnable blocks | Add "what is a database", ER modeling, and per-topic SQL files (select/filter, joins, aggregation, subqueries, window functions, DDL/constraints), index internals (B-tree), transaction isolation experiments |
| 06 Operating systems | 5 files, 140-226 lines, 2-5 code blocks each | Per-topic deep dives: boot and kernel, system calls, process lifecycle, IPC, scheduling algorithms one by one, paging and segmentation, page replacement, synchronization primitives, deadlock handling, file system structures, I/O models |
| 07 Networking | 4 files, 160-200 lines | Per-layer files, IP addressing and subnetting, routing, TCP in depth, UDP, sockets programming, DNS, HTTP evolution, REST, WebSockets, TLS/PKI, common attacks, network tools |
| 08 Modern Python | 8 chapters, 340-550 lines | Good; add a bridge from Python fundamentals |
| 09 Interview playbook | Good | Link to new foundations; add worked problem walkthroughs by pattern |

## Plan (waves)

1. **Wave 0 (this page)**: audit and quality bar.
2. **Wave 1 (done)**: `00-start-here` and `00-foundations` (computer basics, math, Python fundamentals, command line and Git, setup, glossary).
3. **Wave 2 (done)**: `01-complexity` expanded into eight beginner-friendly lessons.
4. **Wave 3 (done)**: split and deepen `02-data-structures` (one file per structure and variant).
5. **Wave 4 (done)**: split and deepen `03-algorithms` (one file per algorithm).
6. **Wave 5 (done)**: deepen `06-operating-systems`.
7. **Wave 6 (done)**: deepen `07-networking`.
8. **Wave 7 (done)**: deepen `05-databases`.
9. **Wave 8**: final cross-link, glossary, index and revision-tracker pass.

Status of each wave is recorded in the [index](INDEX.md).


## OOP audit (after Wave 4)

- Design patterns (25 files): at the quality bar (prerequisites, runnable code, practice, check yourself).
- Six core topics (classes, encapsulation, inheritance, polymorphism, composition, SOLID): thorough single lessons with separate exercises; added a beginner on-ramp, [OOP from scratch](04-oop/00-oop-from-scratch.md).
- All 50 OOP files pass under Python 3.10+ (two blocks need `match` and `X | None`; the handbook states Python 3.10+ in setup).
