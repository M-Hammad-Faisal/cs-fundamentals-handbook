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
9. **Wave 8 (done)**: final cross-link, glossary (189 terms), index (detailed lessons listed per part), revision tracker (a row per lesson) and root README pass.

Status of each wave is recorded in the [index](INDEX.md).


## OOP audit (after Wave 4)

- Design patterns (25 files): at the quality bar (prerequisites, runnable code, practice, check yourself).
- Six core topics (classes, encapsulation, inheritance, polymorphism, composition, SOLID): thorough single lessons with separate exercises; added a beginner on-ramp, [OOP from scratch](04-oop/00-oop-from-scratch.md).
- All 50 OOP files pass under Python 3.10+ (two blocks need `match` and `X | None`; the handbook states Python 3.10+ in setup).

## Final status

**What exists now.** 276 pages (about 58,000 lines, 1,743 Python examples). Every part from foundations to the interview playbook is written. Parts 02 to 07 have a quick-reference README per topic **plus numbered detailed lessons** (56 of them, many are hands-on labs), and 04 has a beginner on-ramp.

**How it was verified.**

- Every page was run through a code-block runner on Python 3.15 (and the lessons require Python 3.10+). **263 of 276 pages run cleanly.**
- The remaining 13 pages are not broken; they contain illustrative sketches that assume context: cheat-sheet snippets with placeholder variables (`words`, `nums`, `r.set(...)`), exercise solutions that call helpers defined in the matching lesson (`fifo`, `round_robin`, `qps`, `first_true`), or a script that expects a command-line argument. With the lesson code loaded, those exercise solutions run.
- Output comments in the newer lessons were compared with real output; many were corrected during this pass. Links were checked across the whole repository (0 broken), and a privacy check was run before every push.
- The labs use only the standard library, SQLite and (for the TLS lab) the `openssl` command; no internet access is needed.

## Known gaps (honest list)

These were named in the original audit and are **not** yet written as dedicated lessons:

| Area | Still to write |
|------|----------------|
| 03 Algorithms | stand-alone divide-and-conquer lesson (number theory and string algorithms are now written) |
| 04 OOP | UML and class-diagram guide |
| 05 Databases | a "what is a database" overview with ER modeling, PostgreSQL-specific features (window functions and CTEs now have their own lab) |
| 06 Operating systems | boot and bootloader in more depth, segmentation, a threads-and-GIL lab, containers and namespaces |
| 07 Networking | routing protocols (BGP/OSPF) in depth, WebSockets and REST design lessons, HTTP/2 and HTTP/3 internals, network debugging with `tcpdump`/Wireshark |
| 08 Modern Python | a bridge lesson from Python fundamentals |
| 09 Interview playbook | worked problem walkthroughs by pattern with timed practice |
| All parts | per-topic `exercises.md` and `summary.md` were written before the detailed lessons and could be refreshed to match them |

Contributions and ideas for any of these are welcome.
