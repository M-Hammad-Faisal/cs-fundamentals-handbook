# Index

The master map of the handbook. Every part is written; each part below also lists its **detailed lessons** (step-by-step, with runnable labs).

Each topic lives in its own folder with a quick-reference README, numbered detailed lessons, and exercises and summary files:

- `README.md`: the full lesson (concept, internals, code, complexity, two real-world examples, tips).
- `exercises.md`: practice problems with collapsible solutions.
- `summary.md`: a one-page recap for quick revision.

## Start here
| Page | Status |
|------|--------|
| [How to use this handbook, study methods and learning paths](00-start-here/README.md) | done |
| [Glossary (203 terms in plain words)](GLOSSARY.md) | done |
| [Coverage audit and roadmap](COVERAGE.md) | done |

## 00 Foundations
One topic per file; each file has a plain-English explanation, runnable code, practice with solutions and a self-check.

| Section | Lessons | Status |
|---------|---------|--------|
| [Setup](00-foundations/setup/README.md) | Python, editor, Git, virtual environments, first tested project | done |
| [Computer basics](00-foundations/computer-basics/README.md) | [How a computer runs programs](00-foundations/computer-basics/how-computers-work.md), [binary and data representation](00-foundations/computer-basics/binary-and-data-representation.md), [memory, stack and heap](00-foundations/computer-basics/memory-stack-heap.md) | done |
| [Math for CS](00-foundations/math-for-cs/README.md) | [Exponents and logarithms](00-foundations/math-for-cs/exponents-and-logarithms.md), [logic, sets and proofs](00-foundations/math-for-cs/logic-sets-proofs.md), [counting and probability](00-foundations/math-for-cs/counting-and-probability.md), [sums and recurrences](00-foundations/math-for-cs/sums-and-recurrences.md) | done |
| [Python fundamentals](00-foundations/python-fundamentals/README.md) | [Variables and types](00-foundations/python-fundamentals/01-variables-types-operators.md), [control flow](00-foundations/python-fundamentals/02-control-flow.md), [functions](00-foundations/python-fundamentals/03-functions.md), [collections](00-foundations/python-fundamentals/04-strings-lists-dicts-sets.md), [files, modules and errors](00-foundations/python-fundamentals/05-files-modules-errors.md), [debugging and testing](00-foundations/python-fundamentals/06-debugging-and-testing.md), [classes: first look](00-foundations/python-fundamentals/07-classes-first-look.md) | done |
| [Command line and Git](00-foundations/command-line-and-git/README.md) | [Terminal](00-foundations/command-line-and-git/terminal-basics.md), [Git basics](00-foundations/command-line-and-git/git-basics.md), [branches and merging](00-foundations/command-line-and-git/git-branches-and-merging.md), [undo and history](00-foundations/command-line-and-git/git-undo-and-history.md), [GitHub collaboration](00-foundations/command-line-and-git/github-collaboration.md) | done |

## 00 Career path
| Page | Status |
|------|--------|
| [Software engineering career path, end to end](00-career-path/README.md) | done |

## 01 Complexity
Overview and learning path: [01-complexity/README.md](01-complexity/README.md). Every lesson has practice with solutions and a self-check.

| Topic | Lesson | Status |
|-------|--------|--------|
| What is an algorithm? | [lesson](01-complexity/01-what-is-an-algorithm.md) | done |
| Counting steps and growth | [lesson](01-complexity/02-counting-steps-and-growth.md) | done |
| Big-O, Omega and Theta | [lesson](01-complexity/03-big-o-omega-theta.md) | done |
| Analyzing loops and recursion | [lesson](01-complexity/04-analyzing-loops-and-recursion.md) | done |
| Space complexity | [lesson](01-complexity/05-space-complexity.md) | done |
| Best, average, worst and amortized analysis | [lesson](01-complexity/06-cases-and-amortized-analysis.md) | done |
| Complexity of Python's built-in operations | [lesson](01-complexity/07-python-operations-cheat-sheet.md) | done |
| Beyond Big-O: constants, caches, P vs NP | [lesson](01-complexity/08-beyond-big-o.md) | done |
| Big-O quick reference (lesson, exercises, summary) | [lesson](01-complexity/big-o/README.md) · [ex](01-complexity/big-o/exercises.md) · [sum](01-complexity/big-o/summary.md) | done |

## 02 Data structures
| Topic | Lesson | Exercises | Summary | Status |
|-------|--------|-----------|---------|--------|
| Arrays and strings | [lesson](02-data-structures/arrays-strings/README.md) | [ex](02-data-structures/arrays-strings/exercises.md) | [sum](02-data-structures/arrays-strings/summary.md) | done |
| Linked lists | [lesson](02-data-structures/linked-lists/README.md) | [ex](02-data-structures/linked-lists/exercises.md) | [sum](02-data-structures/linked-lists/summary.md) | done |
| Stacks and queues | [lesson](02-data-structures/stacks-queues/README.md) | [ex](02-data-structures/stacks-queues/exercises.md) | [sum](02-data-structures/stacks-queues/summary.md) | done |
| Hash tables | [lesson](02-data-structures/hash-tables/README.md) | [ex](02-data-structures/hash-tables/exercises.md) | [sum](02-data-structures/hash-tables/summary.md) | done |
| Trees (binary, BST, balanced) | [lesson](02-data-structures/trees/README.md) | [ex](02-data-structures/trees/exercises.md) | [sum](02-data-structures/trees/summary.md) | done |
| Heaps and priority queues | [lesson](02-data-structures/heaps/README.md) | [ex](02-data-structures/heaps/exercises.md) | [sum](02-data-structures/heaps/summary.md) | done |
| Tries | [lesson](02-data-structures/tries/README.md) | [ex](02-data-structures/tries/exercises.md) | [sum](02-data-structures/tries/summary.md) | done |
| Graphs | [lesson](02-data-structures/graphs/README.md) | [ex](02-data-structures/graphs/exercises.md) | [sum](02-data-structures/graphs/summary.md) | done |

<!-- detailed-lessons:02 -->
**Detailed lessons** (step-by-step, with runnable labs, practice and self-checks):

- **Arrays and Strings:** [Arrays: How Data Sits in Memory](02-data-structures/arrays-strings/01-arrays-and-memory.md), [Working with Arrays: Essential Techniques](02-data-structures/arrays-strings/02-array-techniques.md), [Strings in Depth](02-data-structures/arrays-strings/03-strings-in-depth.md)
- **Graphs:** [Graph Basics: Representations, BFS and DFS](02-data-structures/graphs/01-graph-basics-bfs-dfs.md), [Graph Algorithms: Ordering, Shortest Paths and Spanning Trees](02-data-structures/graphs/02-graph-algorithms.md), [Union-Find (Disjoint Sets) and Kruskal's Algorithm](02-data-structures/graphs/03-union-find.md)
- **Hash Tables:** [Hash Functions and Collisions](02-data-structures/hash-tables/01-hash-functions-and-collisions.md), [Implementing Hash Tables](02-data-structures/hash-tables/02-implementing-hash-tables.md), [Dict, Set, Hash-Map Patterns, Bloom Filters and Consistent Hashing](02-data-structures/hash-tables/03-dict-set-internals-and-bloom-filters.md)
- **Heaps and Priority Queues:** [Binary Heaps and Heapsort](02-data-structures/heaps/01-binary-heaps-and-heapsort.md), [Priority Queue Applications](02-data-structures/heaps/02-priority-queue-applications.md)
- **Linked Lists:** [The Singly Linked List, Built from Scratch](02-data-structures/linked-lists/01-singly-linked-list.md), [Doubly Linked Lists, Circular Lists and the LRU Cache](02-data-structures/linked-lists/02-doubly-and-circular.md), [Linked-List Techniques and Classic Problems](02-data-structures/linked-lists/03-linked-list-techniques.md)
- **Stacks and Queues:** [Stacks: Last In, First Out](02-data-structures/stacks-queues/01-stacks.md), [Queues, Deques and Priority Queues](02-data-structures/stacks-queues/02-queues-deques-priority-queues.md), [Stack and Queue Applications](02-data-structures/stacks-queues/03-stack-and-queue-applications.md)
- **Trees:** [Binary Trees and Traversals](02-data-structures/trees/01-binary-trees-and-traversals.md), [Binary Search Trees](02-data-structures/trees/02-binary-search-trees.md), [Balanced Trees: AVL, Red-Black and B-Trees](02-data-structures/trees/03-balanced-trees-avl.md), [Segment Trees and Fenwick Trees](02-data-structures/trees/04-segment-and-fenwick-trees.md)
- **Tries (Prefix Trees):** [Tries (Prefix Trees)](02-data-structures/tries/01-tries.md)
<!-- detailed-lessons:02 -->

## 03 Algorithms
| Topic | Lesson | Exercises | Summary | Status |
|-------|--------|-----------|---------|--------|
| Sorting (bubble to merge, quick, heap, counting) | [lesson](03-algorithms/sorting/README.md) | [ex](03-algorithms/sorting/exercises.md) | [sum](03-algorithms/sorting/summary.md) | done |
| Searching (linear, binary, search on the answer) | [lesson](03-algorithms/searching/README.md) | [ex](03-algorithms/searching/exercises.md) | [sum](03-algorithms/searching/summary.md) | done |
| Recursion and backtracking | [lesson](03-algorithms/recursion-backtracking/README.md) | [ex](03-algorithms/recursion-backtracking/exercises.md) | [sum](03-algorithms/recursion-backtracking/summary.md) | done |
| Dynamic programming | [lesson](03-algorithms/dynamic-programming/README.md) | [ex](03-algorithms/dynamic-programming/exercises.md) | [sum](03-algorithms/dynamic-programming/summary.md) | done |
| Greedy algorithms | [lesson](03-algorithms/greedy/README.md) | [ex](03-algorithms/greedy/exercises.md) | [sum](03-algorithms/greedy/summary.md) | done |
| Number theory (GCD, modular arithmetic, primes, Miller-Rabin) | [lesson](03-algorithms/number-theory/README.md) | | | done |
| String algorithms (Rabin-Karp, Z-function, Manacher, suffix arrays) | [lesson](03-algorithms/string-algorithms/README.md) | | | done |
| Advanced graph algorithms (Bellman-Ford, MST, A*, SCC) | [lesson](03-algorithms/graph-algorithms/README.md) | [ex](03-algorithms/graph-algorithms/exercises.md) | [sum](03-algorithms/graph-algorithms/summary.md) | done |

<!-- detailed-lessons:03 -->
**Detailed lessons** (step-by-step, with runnable labs, practice and self-checks):

- **Dynamic Programming:** [Dynamic Programming: Thinking and 1D Problems](03-algorithms/dynamic-programming/01-dp-thinking-and-1d-problems.md), [DP on Two Sequences, Grids and Knapsack](03-algorithms/dynamic-programming/02-dp-on-two-sequences-and-grids.md), [Advanced DP Patterns: State Machines, Trees, Bitmasks and Digits](03-algorithms/dynamic-programming/03-advanced-dp-patterns.md)
- **Advanced Graph Algorithms:** [Shortest Paths Beyond Dijkstra: Floyd-Warshall, A*, 0-1 BFS](03-algorithms/graph-algorithms/01-all-pairs-and-heuristic-shortest-paths.md), [Connectivity, Strongly Connected Components, Bridges and Max Flow](03-algorithms/graph-algorithms/02-connectivity-scc-and-flow.md)
- **Greedy Algorithms:** [Greedy Algorithms](03-algorithms/greedy/01-greedy-algorithms.md)
- **Number Theory:** [Number Theory for Programmers](03-algorithms/number-theory/01-number-theory-for-programmers.md)
- **Recursion and Backtracking:** [Recursion Fundamentals](03-algorithms/recursion-backtracking/01-recursion-fundamentals.md), [Backtracking](03-algorithms/recursion-backtracking/02-backtracking.md)
- **Searching:** [Linear Search and Binary Search](03-algorithms/searching/01-linear-and-binary-search.md), [Binary Search on the Answer and Other Search Techniques](03-algorithms/searching/02-binary-search-on-the-answer.md)
- **Sorting:** [Sorting Basics and the Elementary Sorts](03-algorithms/sorting/01-sorting-basics-and-elementary-sorts.md), [Merge Sort and Quicksort](03-algorithms/sorting/02-merge-sort-and-quicksort.md), [Linear-Time Sorts, Timsort and Choosing a Sort](03-algorithms/sorting/03-linear-time-sorts-and-timsort.md)
- **String Algorithms:** [String Algorithms: Matching, Palindromes and Suffix Arrays](03-algorithms/string-algorithms/01-string-matching-and-suffix-structures.md)
<!-- detailed-lessons:03 -->

## 04 Object-oriented design
| Topic | Lesson | Exercises | Summary | Status |
|-------|--------|-----------|---------|--------|
| Classes and objects in depth | [lesson](04-oop/classes-objects/README.md) | [ex](04-oop/classes-objects/exercises.md) | [sum](04-oop/classes-objects/summary.md) | done |
| Encapsulation and abstraction | [lesson](04-oop/encapsulation-abstraction/README.md) | [ex](04-oop/encapsulation-abstraction/exercises.md) | [sum](04-oop/encapsulation-abstraction/summary.md) | done |
| Inheritance, MRO and multiple inheritance | [lesson](04-oop/inheritance-mro/README.md) | [ex](04-oop/inheritance-mro/exercises.md) | [sum](04-oop/inheritance-mro/summary.md) | done |
| Polymorphism and the Python data model (dunder methods) | [lesson](04-oop/polymorphism-dunder/README.md) | [ex](04-oop/polymorphism-dunder/exercises.md) | [sum](04-oop/polymorphism-dunder/summary.md) | done |
| Composition, delegation, coupling and object design | [lesson](04-oop/composition-design/README.md) | [ex](04-oop/composition-design/exercises.md) | [sum](04-oop/composition-design/summary.md) | done |
| SOLID and other design principles | [lesson](04-oop/solid/README.md) | [ex](04-oop/solid/exercises.md) | [sum](04-oop/solid/summary.md) | done |
| Design patterns: plain-English guide (what is GoF?), glossary, chooser | [guide](04-oop/design-patterns/README.md) | in each pattern file | [chooser table](04-oop/design-patterns/README.md) | done |
| Creational patterns (6): Singleton, Factory Method, Abstract Factory, Builder, Prototype, Object Pool | [overview](04-oop/design-patterns/creational/README.md) | one file per pattern, with exercises | [cheat sheet](04-oop/design-patterns/creational/README.md) | done |
| Structural patterns (7): Adapter, Decorator, Proxy, Facade, Composite, Bridge, Flyweight | [overview](04-oop/design-patterns/structural/README.md) | one file per pattern, with exercises | [cheat sheet](04-oop/design-patterns/structural/README.md) | done |
| Behavioral patterns (12): Strategy, Observer, Command, State, Template Method, Iterator, Chain of Responsibility, Mediator, Memento, Visitor, Interpreter, Null Object | [overview](04-oop/design-patterns/behavioral/README.md) | one file per pattern, with exercises | [cheat sheet](04-oop/design-patterns/behavioral/README.md) | done |

<!-- detailed-lessons:04 -->
**Detailed lessons** (step-by-step, with runnable labs, practice and self-checks):

- **Start here:** [OOP From Scratch: Your First Classes](04-oop/00-oop-from-scratch.md)
<!-- detailed-lessons:04 -->

## 05 Databases
Shared dataset for the SQL examples: [sample-data.sql](05-databases/sample-data.sql).

| Topic | Lesson | Exercises | Summary | Status |
|-------|--------|-----------|---------|--------|
| Relational model and SQL (joins, aggregation, window functions, CTEs) | [lesson](05-databases/relational-sql/README.md) | [ex](05-databases/relational-sql/exercises.md) | [sum](05-databases/relational-sql/summary.md) | done |
| Indexes and query plans | [lesson](05-databases/indexes-query-plans/README.md) | [ex](05-databases/indexes-query-plans/exercises.md) | [sum](05-databases/indexes-query-plans/summary.md) | done |
| Transactions, ACID, isolation levels | [lesson](05-databases/transactions-acid/README.md) | [ex](05-databases/transactions-acid/exercises.md) | [sum](05-databases/transactions-acid/summary.md) | done |
| Normalization and schema design | [lesson](05-databases/normalization-schema-design/README.md) | [ex](05-databases/normalization-schema-design/exercises.md) | [sum](05-databases/normalization-schema-design/summary.md) | done |
| NoSQL and choosing a database | [lesson](05-databases/nosql/README.md) | [ex](05-databases/nosql/exercises.md) | [sum](05-databases/nosql/summary.md) | done |

<!-- detailed-lessons:05 -->
**Detailed lessons** (step-by-step, with runnable labs, practice and self-checks):

- **Indexes and Query Plans:** [Indexes Lab: Speed, Query Plans and Trade-offs](05-databases/indexes-query-plans/01-indexes-lab.md)
- **Normalization and Schema Design:** [Normalization Lab: From a Messy Table to a Clean Schema](05-databases/normalization-schema-design/01-normalization-lab.md)
- **NoSQL and Choosing a Database:** [NoSQL Lab: Key-Value, Documents, Search and Replication](05-databases/nosql/01-nosql-lab.md)
- **The Relational Model and SQL:** [SQL First Steps (with Python and SQLite)](05-databases/relational-sql/01-sql-first-steps.md), [Aggregation and Joins Lab](05-databases/relational-sql/02-aggregation-and-joins-lab.md), [CTEs, Recursive Queries and Window Functions Lab](05-databases/relational-sql/03-ctes-and-window-functions-lab.md)
- **Transactions, ACID and Isolation:** [Transactions Lab: ACID, Concurrency and Lost Updates](05-databases/transactions-acid/01-transactions-lab.md)
<!-- detailed-lessons:05 -->

## 06 Operating systems
| Topic | Lesson | Exercises | Summary | Status |
|-------|--------|-----------|---------|--------|
| Processes and threads | [lesson](06-operating-systems/processes-threads/README.md) | [ex](06-operating-systems/processes-threads/exercises.md) | [sum](06-operating-systems/processes-threads/summary.md) | done |
| CPU scheduling | [lesson](06-operating-systems/scheduling/README.md) | [ex](06-operating-systems/scheduling/exercises.md) | [sum](06-operating-systems/scheduling/summary.md) | done |
| Memory management and virtual memory | [lesson](06-operating-systems/memory-virtual-memory/README.md) | [ex](06-operating-systems/memory-virtual-memory/exercises.md) | [sum](06-operating-systems/memory-virtual-memory/summary.md) | done |
| Concurrency, locks and deadlocks | [lesson](06-operating-systems/concurrency-deadlocks/README.md) | [ex](06-operating-systems/concurrency-deadlocks/exercises.md) | [sum](06-operating-systems/concurrency-deadlocks/summary.md) | done |
| File systems and I/O | [lesson](06-operating-systems/file-systems-io/README.md) | [ex](06-operating-systems/file-systems-io/exercises.md) | [sum](06-operating-systems/file-systems-io/summary.md) | done |

<!-- detailed-lessons:06 -->
**Detailed lessons** (step-by-step, with runnable labs, practice and self-checks):

- **Start here:** [What Is an Operating System?](06-operating-systems/00-what-is-an-operating-system.md)
- **Concurrency, Synchronization and Deadlocks:** [Race Conditions and Synchronization](06-operating-systems/concurrency-deadlocks/01-race-conditions-and-synchronization.md), [Deadlock: Detection, Prevention and Avoidance](06-operating-systems/concurrency-deadlocks/02-deadlock.md)
- **File Systems and I/O:** [File Systems in Depth: Inodes, Links, Permissions and Durability](06-operating-systems/file-systems-io/01-file-systems-in-depth.md)
- **Memory Management and Virtual Memory:** [Virtual Memory: Paging and Address Translation](06-operating-systems/memory-virtual-memory/01-paging-and-address-translation.md), [Page Replacement Algorithms](06-operating-systems/memory-virtual-memory/02-page-replacement-algorithms.md)
- **Processes and Threads:** [Processes in Practice: fork, exec, pipes, signals and concurrency models](06-operating-systems/processes-threads/01-processes-in-practice.md)
- **CPU Scheduling:** [CPU Scheduling Algorithms: A Hands-On Simulator](06-operating-systems/scheduling/01-scheduling-simulator.md)
<!-- detailed-lessons:06 -->

## 07 Networking
| Topic | Lesson | Exercises | Summary | Status |
|-------|--------|-----------|---------|--------|
| OSI and TCP/IP models | [lesson](07-networking/tcp-ip-osi/README.md) | [ex](07-networking/tcp-ip-osi/exercises.md) | [sum](07-networking/tcp-ip-osi/summary.md) | done |
| DNS and HTTP | [lesson](07-networking/dns-http/README.md) | [ex](07-networking/dns-http/exercises.md) | [sum](07-networking/dns-http/summary.md) | done |
| TLS and security basics | [lesson](07-networking/tls-security/README.md) | [ex](07-networking/tls-security/exercises.md) | [sum](07-networking/tls-security/summary.md) | done |
| Load balancing, CDNs and resilience | [lesson](07-networking/load-balancing-cdn/README.md) | [ex](07-networking/load-balancing-cdn/exercises.md) | [sum](07-networking/load-balancing-cdn/summary.md) | done |

<!-- detailed-lessons:07 -->
**Detailed lessons** (step-by-step, with runnable labs, practice and self-checks):

- **DNS and HTTP:** [HTTP from Scratch: Requests, Responses, Caching and a Tiny Server](07-networking/dns-http/01-http-from-scratch.md), [DNS in Depth: Wire Format, a Toy Server, Caching and Resolution](07-networking/dns-http/02-dns-in-depth.md)
- **Load Balancing, Proxies, CDNs and Resilience:** [Load Balancing and Resilience Lab](07-networking/load-balancing-cdn/01-load-balancing-and-resilience-lab.md)
- **The Network Stack:** [Packets, Addressing and Subnets (with Runnable Labs)](07-networking/tcp-ip-osi/01-packets-addressing-and-subnets.md), [Sockets Lab: TCP and UDP from Scratch](07-networking/tcp-ip-osi/02-sockets-tcp-udp-lab.md)
- **TLS and Security Basics:** [Cryptography and TLS Lab: Hashes, Keys, Certificates and Web Attacks](07-networking/tls-security/01-cryptography-and-tls-lab.md)
<!-- detailed-lessons:07 -->

## 08 Modern Python
| Topic | Lesson | Exercises | Summary | Status |
|-------|--------|-----------|---------|--------|
| Type hints and static typing | [lesson](08-modern-python/typing-hints/README.md) | [ex](08-modern-python/typing-hints/exercises.md) | [sum](08-modern-python/typing-hints/summary.md) | done |
| Dataclasses, NamedTuple and enums | [lesson](08-modern-python/dataclasses-enums/README.md) | [ex](08-modern-python/dataclasses-enums/exercises.md) | [sum](08-modern-python/dataclasses-enums/summary.md) | done |
| Iterators, generators, comprehensions and functional tools | [lesson](08-modern-python/generators-functional/README.md) | [ex](08-modern-python/generators-functional/exercises.md) | [sum](08-modern-python/generators-functional/summary.md) | done |
| Concurrency: threads, processes and asyncio | [lesson](08-modern-python/async-concurrency/README.md) | [ex](08-modern-python/async-concurrency/exercises.md) | [sum](08-modern-python/async-concurrency/summary.md) | done |
| Modern language features (3.8 to 3.14) | [lesson](08-modern-python/modern-syntax/README.md) | [ex](08-modern-python/modern-syntax/exercises.md) | [sum](08-modern-python/modern-syntax/summary.md) | done |
| Performance, profiling and memory | [lesson](08-modern-python/performance-profiling/README.md) | [ex](08-modern-python/performance-profiling/exercises.md) | [sum](08-modern-python/performance-profiling/summary.md) | done |
| Exceptions, logging and testing | [lesson](08-modern-python/exceptions-logging-testing/README.md) | [ex](08-modern-python/exceptions-logging-testing/exercises.md) | [sum](08-modern-python/exceptions-logging-testing/summary.md) | done |
| Packaging, environments and tooling | [lesson](08-modern-python/packaging-tooling/README.md) | [ex](08-modern-python/packaging-tooling/exercises.md) | [sum](08-modern-python/packaging-tooling/summary.md) | done |

## 09 Interview playbook
| Topic | Lesson | Exercises | Summary | Status |
|-------|--------|-----------|---------|--------|
| Problem-solving patterns (16 patterns with templates) | [lesson](09-interview-playbook/problem-solving-patterns/README.md) | [ex](09-interview-playbook/problem-solving-patterns/exercises.md) | [sum](09-interview-playbook/problem-solving-patterns/summary.md) | done |
| System design basics (framework, estimation, building blocks, worked designs) | [lesson](09-interview-playbook/system-design-basics/README.md) | [ex](09-interview-playbook/system-design-basics/exercises.md) | [sum](09-interview-playbook/system-design-basics/summary.md) | done |
| Rapid-fire Python and CS questions | [lesson](09-interview-playbook/python-and-cs-rapid-fire/README.md) | [ex](09-interview-playbook/python-and-cs-rapid-fire/exercises.md) | [sum](09-interview-playbook/python-and-cs-rapid-fire/summary.md) | done |
| Behavioral interviews, hiring process and 12-week plan | [lesson](09-interview-playbook/behavioral-and-process/README.md) | [ex](09-interview-playbook/behavioral-and-process/exercises.md) | [sum](09-interview-playbook/behavioral-and-process/summary.md) | done |

## Revision tools
| Page | Purpose |
|------|---------|
| [Revision schedule](revision/schedule.md) | Spaced-repetition plan |
| [Progress tracker](revision/PROGRESS.md) | Tick off chapters and log mistakes |
