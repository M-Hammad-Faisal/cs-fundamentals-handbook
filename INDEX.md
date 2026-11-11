# Index

The map of the whole handbook, in reading order. **This page is generated** by `tools/build_index.py` from the files on disk, so it always matches them.

Every topic is one row: its overview and detailed lessons, the exercises (with solutions) and the one-page summary. For definitions of terms see the [glossary](GLOSSARY.md); to track your own progress use the [progress tracker](revision/PROGRESS.md) and the [spaced schedule](revision/schedule.md).

## Start here

How the handbook works and how to study with it. [00-start-here/README.md](00-start-here/README.md)

## Career path

Where the profession is heading, which roles are growing, and the working habits that matter. Overview: [00-career-path/README.md](00-career-path/README.md).

| Topic | Lessons | Exercises | Summary | Status |
|-------|---------|-----------|---------|--------|
| Career Path | [lesson](00-career-path/README.md) | – | – | done |
| Engineering Practice | [lesson](00-career-path/engineering-practice.md) | – | – | done |

## 00 Foundations

Everything the rest assumes: setup, how computers work, math, Python, the command line and Git. Overview: [00-foundations/README.md](00-foundations/README.md).

| Topic | Lessons | Exercises | Summary | Status |
|-------|---------|-----------|---------|--------|
| Setting Up Your Computer for This Handbook | [lesson](00-foundations/setup/README.md) | – | – | done |
| Computer Basics | [overview](00-foundations/computer-basics/README.md)<br>[How a Computer Runs Your Program](00-foundations/computer-basics/how-computers-work.md)<br>[Binary, Hexadecimal and How Data Is Stored](00-foundations/computer-basics/binary-and-data-representation.md)<br>[Variables, Memory, the Stack and the Heap](00-foundations/computer-basics/memory-stack-heap.md)<br>[CPU Caches and the Memory Hierarchy](00-foundations/computer-basics/cpu-caches-and-memory-hierarchy.md) | – | – | done |
| Math for Computer Science | [overview](00-foundations/math-for-cs/README.md)<br>[Exponents, Logarithms and Growth](00-foundations/math-for-cs/exponents-and-logarithms.md)<br>[Logic, Sets and Proofs](00-foundations/math-for-cs/logic-sets-proofs.md)<br>[Counting and Probability](00-foundations/math-for-cs/counting-and-probability.md)<br>[Sequences, Sums and Recurrences](00-foundations/math-for-cs/sums-and-recurrences.md) | – | – | done |
| Python Fundamentals | [overview](00-foundations/python-fundamentals/README.md)<br>[Variables, Types and Operators](00-foundations/python-fundamentals/01-variables-types-operators.md)<br>[Making Decisions and Repeating Things](00-foundations/python-fundamentals/02-control-flow.md)<br>[Functions](00-foundations/python-fundamentals/03-functions.md)<br>[Strings, Lists, Tuples, Dictionaries and Sets](00-foundations/python-fundamentals/04-strings-lists-dicts-sets.md)<br>[Files, Modules and Handling Errors](00-foundations/python-fundamentals/05-files-modules-errors.md)<br>[Debugging and Testing Your Code](00-foundations/python-fundamentals/06-debugging-and-testing.md)<br>[Classes and Objects, a First Look](00-foundations/python-fundamentals/07-classes-first-look.md) | – | – | done |
| Command Line and Git | [overview](00-foundations/command-line-and-git/README.md)<br>[The Command Line](00-foundations/command-line-and-git/terminal-basics.md)<br>[Git Basics](00-foundations/command-line-and-git/git-basics.md)<br>[Git Branches, Merging and Resolving Conflicts](00-foundations/command-line-and-git/git-branches-and-merging.md)<br>[Undoing Mistakes and Rewriting History in Git](00-foundations/command-line-and-git/git-undo-and-history.md)<br>[GitHub and Collaborating with Others](00-foundations/command-line-and-git/github-collaboration.md) | – | – | done |

## 01 Complexity

Measuring how fast and how big. Overview: [01-complexity/README.md](01-complexity/README.md).

| Topic | Lessons | Exercises | Summary | Status |
|-------|---------|-----------|---------|--------|
| What Is an Algorithm? | [lesson](01-complexity/01-what-is-an-algorithm.md) | – | – | done |
| Counting Steps and Understanding Growth | [lesson](01-complexity/02-counting-steps-and-growth.md) | – | – | done |
| Big-O, Omega and Theta | [lesson](01-complexity/03-big-o-omega-theta.md) | – | – | done |
| Analyzing Loops and Recursion Step by Step | [lesson](01-complexity/04-analyzing-loops-and-recursion.md) | – | – | done |
| Space Complexity | [lesson](01-complexity/05-space-complexity.md) | – | – | done |
| Best, Average, Worst Case and Amortized Analysis | [lesson](01-complexity/06-cases-and-amortized-analysis.md) | – | – | done |
| Complexity of Python's Built-in Operations | [lesson](01-complexity/07-python-operations-cheat-sheet.md) | – | – | done |
| Beyond Big-O | [lesson](01-complexity/08-beyond-big-o.md) | – | – | done |
| Big-O and Complexity Analysis | [lesson](01-complexity/big-o/README.md) | [ex](01-complexity/big-o/exercises.md) | [sum](01-complexity/big-o/summary.md) | done |

## 02 Data structures

Storing and organizing data. Overview: [02-data-structures/README.md](02-data-structures/README.md).

| Topic | Lessons | Exercises | Summary | Status |
|-------|---------|-----------|---------|--------|
| Arrays and Strings | [overview](02-data-structures/arrays-strings/README.md)<br>[Arrays](02-data-structures/arrays-strings/01-arrays-and-memory.md)<br>[Working with Arrays](02-data-structures/arrays-strings/02-array-techniques.md)<br>[Strings in Depth](02-data-structures/arrays-strings/03-strings-in-depth.md) | [ex](02-data-structures/arrays-strings/exercises.md) | [sum](02-data-structures/arrays-strings/summary.md) | done |
| Linked Lists | [overview](02-data-structures/linked-lists/README.md)<br>[The Singly Linked List, Built from Scratch](02-data-structures/linked-lists/01-singly-linked-list.md)<br>[Doubly Linked Lists, Circular Lists and the LRU Cache](02-data-structures/linked-lists/02-doubly-and-circular.md)<br>[Linked-List Techniques and Classic Problems](02-data-structures/linked-lists/03-linked-list-techniques.md) | [ex](02-data-structures/linked-lists/exercises.md) | [sum](02-data-structures/linked-lists/summary.md) | done |
| Stacks and Queues | [overview](02-data-structures/stacks-queues/README.md)<br>[Stacks](02-data-structures/stacks-queues/01-stacks.md)<br>[Queues, Deques and Priority Queues](02-data-structures/stacks-queues/02-queues-deques-priority-queues.md)<br>[Stack and Queue Applications](02-data-structures/stacks-queues/03-stack-and-queue-applications.md) | [ex](02-data-structures/stacks-queues/exercises.md) | [sum](02-data-structures/stacks-queues/summary.md) | done |
| Hash Tables | [overview](02-data-structures/hash-tables/README.md)<br>[Hash Functions and Collisions](02-data-structures/hash-tables/01-hash-functions-and-collisions.md)<br>[Implementing Hash Tables](02-data-structures/hash-tables/02-implementing-hash-tables.md)<br>[Dict, Set, Hash-Map Patterns, Bloom Filters and Consistent Hashing](02-data-structures/hash-tables/03-dict-set-internals-and-bloom-filters.md) | [ex](02-data-structures/hash-tables/exercises.md) | [sum](02-data-structures/hash-tables/summary.md) | done |
| Trees | [overview](02-data-structures/trees/README.md)<br>[Binary Trees and Traversals](02-data-structures/trees/01-binary-trees-and-traversals.md)<br>[Binary Search Trees](02-data-structures/trees/02-binary-search-trees.md)<br>[Balanced Trees](02-data-structures/trees/03-balanced-trees-avl.md)<br>[Segment Trees and Fenwick Trees](02-data-structures/trees/04-segment-and-fenwick-trees.md) | [ex](02-data-structures/trees/exercises.md) | [sum](02-data-structures/trees/summary.md) | done |
| Heaps and Priority Queues | [overview](02-data-structures/heaps/README.md)<br>[Binary Heaps and Heapsort](02-data-structures/heaps/01-binary-heaps-and-heapsort.md)<br>[Priority Queue Applications](02-data-structures/heaps/02-priority-queue-applications.md) | [ex](02-data-structures/heaps/exercises.md) | [sum](02-data-structures/heaps/summary.md) | done |
| Tries | [overview](02-data-structures/tries/README.md)<br>[Tries](02-data-structures/tries/01-tries.md) | [ex](02-data-structures/tries/exercises.md) | [sum](02-data-structures/tries/summary.md) | done |
| Graphs | [overview](02-data-structures/graphs/README.md)<br>[Graph Basics](02-data-structures/graphs/01-graph-basics-bfs-dfs.md)<br>[Graph Algorithms](02-data-structures/graphs/02-graph-algorithms.md)<br>[Union-Find](02-data-structures/graphs/03-union-find.md) | [ex](02-data-structures/graphs/exercises.md) | [sum](02-data-structures/graphs/summary.md) | done |

## 03 Algorithms

Solving problems efficiently. Overview: [03-algorithms/README.md](03-algorithms/README.md).

| Topic | Lessons | Exercises | Summary | Status |
|-------|---------|-----------|---------|--------|
| Sorting | [overview](03-algorithms/sorting/README.md)<br>[Sorting Basics and the Elementary Sorts](03-algorithms/sorting/01-sorting-basics-and-elementary-sorts.md)<br>[Merge Sort and Quicksort](03-algorithms/sorting/02-merge-sort-and-quicksort.md)<br>[Linear-Time Sorts, Timsort and Choosing a Sort](03-algorithms/sorting/03-linear-time-sorts-and-timsort.md) | [ex](03-algorithms/sorting/exercises.md) | [sum](03-algorithms/sorting/summary.md) | done |
| Searching | [overview](03-algorithms/searching/README.md)<br>[Linear Search and Binary Search](03-algorithms/searching/01-linear-and-binary-search.md)<br>[Binary Search on the Answer and Other Search Techniques](03-algorithms/searching/02-binary-search-on-the-answer.md) | [ex](03-algorithms/searching/exercises.md) | [sum](03-algorithms/searching/summary.md) | done |
| Recursion and Backtracking | [overview](03-algorithms/recursion-backtracking/README.md)<br>[Recursion Fundamentals](03-algorithms/recursion-backtracking/01-recursion-fundamentals.md)<br>[Backtracking](03-algorithms/recursion-backtracking/02-backtracking.md) | [ex](03-algorithms/recursion-backtracking/exercises.md) | [sum](03-algorithms/recursion-backtracking/summary.md) | done |
| Divide and Conquer | [overview](03-algorithms/divide-and-conquer/README.md)<br>[Divide and Conquer](03-algorithms/divide-and-conquer/01-divide-and-conquer.md) | – | [sum](03-algorithms/divide-and-conquer/summary.md) | done |
| Dynamic Programming | [overview](03-algorithms/dynamic-programming/README.md)<br>[Dynamic Programming](03-algorithms/dynamic-programming/01-dp-thinking-and-1d-problems.md)<br>[DP on Two Sequences, Grids and Knapsack](03-algorithms/dynamic-programming/02-dp-on-two-sequences-and-grids.md)<br>[Advanced DP Patterns](03-algorithms/dynamic-programming/03-advanced-dp-patterns.md) | [ex](03-algorithms/dynamic-programming/exercises.md) | [sum](03-algorithms/dynamic-programming/summary.md) | done |
| Greedy Algorithms | [overview](03-algorithms/greedy/README.md)<br>[Greedy Algorithms](03-algorithms/greedy/01-greedy-algorithms.md) | [ex](03-algorithms/greedy/exercises.md) | [sum](03-algorithms/greedy/summary.md) | done |
| Number Theory | [overview](03-algorithms/number-theory/README.md)<br>[Number Theory for Programmers](03-algorithms/number-theory/01-number-theory-for-programmers.md) | – | [sum](03-algorithms/number-theory/summary.md) | done |
| String Algorithms | [overview](03-algorithms/string-algorithms/README.md)<br>[String Algorithms](03-algorithms/string-algorithms/01-string-matching-and-suffix-structures.md) | – | [sum](03-algorithms/string-algorithms/summary.md) | done |
| Advanced Graph Algorithms | [overview](03-algorithms/graph-algorithms/README.md)<br>[Shortest Paths Beyond Dijkstra](03-algorithms/graph-algorithms/01-all-pairs-and-heuristic-shortest-paths.md)<br>[Connectivity, Strongly Connected Components, Bridges and Max Flow](03-algorithms/graph-algorithms/02-connectivity-scc-and-flow.md) | [ex](03-algorithms/graph-algorithms/exercises.md) | [sum](03-algorithms/graph-algorithms/summary.md) | done |

## 04 Object-oriented design

Structuring larger programs. Overview: [04-oop/README.md](04-oop/README.md).

| Topic | Lessons | Exercises | Summary | Status |
|-------|---------|-----------|---------|--------|
| OOP From Scratch | [lesson](04-oop/00-oop-from-scratch.md) | – | – | done |
| UML and Class Diagrams | [lesson](04-oop/01-uml-and-class-diagrams.md) | – | – | done |
| Classes and Objects in Depth | [lesson](04-oop/classes-objects/README.md) | [ex](04-oop/classes-objects/exercises.md) | [sum](04-oop/classes-objects/summary.md) | done |
| Encapsulation and Abstraction | [lesson](04-oop/encapsulation-abstraction/README.md) | [ex](04-oop/encapsulation-abstraction/exercises.md) | [sum](04-oop/encapsulation-abstraction/summary.md) | done |
| Inheritance, Method Resolution Order and Multiple Inheritance | [lesson](04-oop/inheritance-mro/README.md) | [ex](04-oop/inheritance-mro/exercises.md) | [sum](04-oop/inheritance-mro/summary.md) | done |
| Polymorphism and the Python Data Model | [lesson](04-oop/polymorphism-dunder/README.md) | [ex](04-oop/polymorphism-dunder/exercises.md) | [sum](04-oop/polymorphism-dunder/summary.md) | done |
| Composition, Delegation, Coupling and Object Design | [lesson](04-oop/composition-design/README.md) | [ex](04-oop/composition-design/exercises.md) | [sum](04-oop/composition-design/summary.md) | done |
| SOLID Principles and Other Design Principles | [lesson](04-oop/solid/README.md) | [ex](04-oop/solid/exercises.md) | [sum](04-oop/solid/summary.md) | done |
| Design Patterns | [lesson](04-oop/design-patterns/README.md) | – | – | done |

## 05 Databases

Storing data reliably. Overview: [05-databases/README.md](05-databases/README.md).

| Topic | Lessons | Exercises | Summary | Status |
|-------|---------|-----------|---------|--------|
| What Is a Database | [lesson](05-databases/00-what-is-a-database-and-er-modeling.md) | – | – | done |
| The Relational Model and SQL | [overview](05-databases/relational-sql/README.md)<br>[SQL First Steps](05-databases/relational-sql/01-sql-first-steps.md)<br>[Aggregation and Joins Lab](05-databases/relational-sql/02-aggregation-and-joins-lab.md)<br>[CTEs, Recursive Queries and Window Functions Lab](05-databases/relational-sql/03-ctes-and-window-functions-lab.md) | [ex](05-databases/relational-sql/exercises.md) | [sum](05-databases/relational-sql/summary.md) | done |
| Indexes and Query Plans | [overview](05-databases/indexes-query-plans/README.md)<br>[Indexes Lab](05-databases/indexes-query-plans/01-indexes-lab.md) | [ex](05-databases/indexes-query-plans/exercises.md) | [sum](05-databases/indexes-query-plans/summary.md) | done |
| Transactions, ACID and Isolation | [overview](05-databases/transactions-acid/README.md)<br>[Transactions Lab](05-databases/transactions-acid/01-transactions-lab.md) | [ex](05-databases/transactions-acid/exercises.md) | [sum](05-databases/transactions-acid/summary.md) | done |
| Normalization and Schema Design | [overview](05-databases/normalization-schema-design/README.md)<br>[Normalization Lab](05-databases/normalization-schema-design/01-normalization-lab.md) | [ex](05-databases/normalization-schema-design/exercises.md) | [sum](05-databases/normalization-schema-design/summary.md) | done |
| NoSQL and Choosing a Database | [overview](05-databases/nosql/README.md)<br>[NoSQL Lab](05-databases/nosql/01-nosql-lab.md) | [ex](05-databases/nosql/exercises.md) | [sum](05-databases/nosql/summary.md) | done |
| PostgreSQL | [overview](05-databases/postgresql/README.md)<br>[PostgreSQL-Specific Features](05-databases/postgresql/01-postgresql-specific-features.md) | – | [sum](05-databases/postgresql/summary.md) | done |

## 06 Operating systems

What runs under your code. Overview: [06-operating-systems/README.md](06-operating-systems/README.md).

| Topic | Lessons | Exercises | Summary | Status |
|-------|---------|-----------|---------|--------|
| What Is an Operating System? | [lesson](06-operating-systems/00-what-is-an-operating-system.md) | – | – | done |
| Processes and Threads | [overview](06-operating-systems/processes-threads/README.md)<br>[Processes in Practice](06-operating-systems/processes-threads/01-processes-in-practice.md)<br>[Threads and the GIL Lab](06-operating-systems/processes-threads/02-threads-and-the-gil-lab.md) | [ex](06-operating-systems/processes-threads/exercises.md) | [sum](06-operating-systems/processes-threads/summary.md) | done |
| CPU Scheduling | [overview](06-operating-systems/scheduling/README.md)<br>[CPU Scheduling Algorithms](06-operating-systems/scheduling/01-scheduling-simulator.md) | [ex](06-operating-systems/scheduling/exercises.md) | [sum](06-operating-systems/scheduling/summary.md) | done |
| Memory Management and Virtual Memory | [overview](06-operating-systems/memory-virtual-memory/README.md)<br>[Virtual Memory](06-operating-systems/memory-virtual-memory/01-paging-and-address-translation.md)<br>[Page Replacement Algorithms](06-operating-systems/memory-virtual-memory/02-page-replacement-algorithms.md)<br>[Segmentation](06-operating-systems/memory-virtual-memory/03-segmentation.md) | [ex](06-operating-systems/memory-virtual-memory/exercises.md) | [sum](06-operating-systems/memory-virtual-memory/summary.md) | done |
| Concurrency, Synchronization and Deadlocks | [overview](06-operating-systems/concurrency-deadlocks/README.md)<br>[Race Conditions and Synchronization](06-operating-systems/concurrency-deadlocks/01-race-conditions-and-synchronization.md)<br>[Deadlock](06-operating-systems/concurrency-deadlocks/02-deadlock.md) | [ex](06-operating-systems/concurrency-deadlocks/exercises.md) | [sum](06-operating-systems/concurrency-deadlocks/summary.md) | done |
| File Systems and I/O | [overview](06-operating-systems/file-systems-io/README.md)<br>[File Systems in Depth](06-operating-systems/file-systems-io/01-file-systems-in-depth.md) | [ex](06-operating-systems/file-systems-io/exercises.md) | [sum](06-operating-systems/file-systems-io/summary.md) | done |
| Boot and Startup | [overview](06-operating-systems/boot-and-startup/README.md)<br>[The Boot Process and Bootloaders](06-operating-systems/boot-and-startup/01-boot-process-and-bootloaders.md) | – | [sum](06-operating-systems/boot-and-startup/summary.md) | done |
| Containers | [overview](06-operating-systems/containers/README.md)<br>[Containers, Namespaces and cgroups](06-operating-systems/containers/01-containers-and-namespaces.md) | [ex](06-operating-systems/containers/exercises.md) | [sum](06-operating-systems/containers/summary.md) | done |

## 07 Networking

How computers talk. Overview: [07-networking/README.md](07-networking/README.md).

| Topic | Lessons | Exercises | Summary | Status |
|-------|---------|-----------|---------|--------|
| The Network Stack | [overview](07-networking/tcp-ip-osi/README.md)<br>[Packets, Addressing and Subnets](07-networking/tcp-ip-osi/01-packets-addressing-and-subnets.md)<br>[Sockets Lab](07-networking/tcp-ip-osi/02-sockets-tcp-udp-lab.md) | [ex](07-networking/tcp-ip-osi/exercises.md) | [sum](07-networking/tcp-ip-osi/summary.md) | done |
| Routing | [overview](07-networking/routing/README.md)<br>[Routing Protocols](07-networking/routing/01-routing-protocols.md) | – | [sum](07-networking/routing/summary.md) | done |
| DNS and HTTP | [overview](07-networking/dns-http/README.md)<br>[HTTP from Scratch](07-networking/dns-http/01-http-from-scratch.md)<br>[DNS in Depth](07-networking/dns-http/02-dns-in-depth.md)<br>[HTTP/2 and HTTP/3 Internals](07-networking/dns-http/03-http2-and-http3-internals.md) | [ex](07-networking/dns-http/exercises.md) | [sum](07-networking/dns-http/summary.md) | done |
| TLS and Security Basics | [overview](07-networking/tls-security/README.md)<br>[Cryptography and TLS Lab](07-networking/tls-security/01-cryptography-and-tls-lab.md) | [ex](07-networking/tls-security/exercises.md) | [sum](07-networking/tls-security/summary.md) | done |
| Load Balancing, Proxies, CDNs and Resilience | [overview](07-networking/load-balancing-cdn/README.md)<br>[Load Balancing and Resilience Lab](07-networking/load-balancing-cdn/01-load-balancing-and-resilience-lab.md) | [ex](07-networking/load-balancing-cdn/exercises.md) | [sum](07-networking/load-balancing-cdn/summary.md) | done |
| APIs and Real-Time Communication | [overview](07-networking/apis-realtime/README.md)<br>[REST APIs, Server-Sent Events and WebSockets](07-networking/apis-realtime/01-rest-apis-and-websockets-lab.md) | [ex](07-networking/apis-realtime/exercises.md) | [sum](07-networking/apis-realtime/summary.md) | done |
| Network Debugging | [overview](07-networking/debugging/README.md)<br>[Network Debugging and Packet Capture](07-networking/debugging/01-network-debugging-and-packet-capture.md) | [ex](07-networking/debugging/exercises.md) | [sum](07-networking/debugging/summary.md) | done |

## 08 Modern Python

Professional Python: the language, the tools and the backend stack. Overview: [08-modern-python/README.md](08-modern-python/README.md).

| Topic | Lessons | Exercises | Summary | Status |
|-------|---------|-----------|---------|--------|
| From Python Fundamentals to Modern Python | [lesson](08-modern-python/00-from-fundamentals-to-modern-python.md) | – | – | done |
| Type Hints and Static Typing | [lesson](08-modern-python/typing-hints/README.md) | [ex](08-modern-python/typing-hints/exercises.md) | [sum](08-modern-python/typing-hints/summary.md) | done |
| Dataclasses, NamedTuple and Enums | [lesson](08-modern-python/dataclasses-enums/README.md) | [ex](08-modern-python/dataclasses-enums/exercises.md) | [sum](08-modern-python/dataclasses-enums/summary.md) | done |
| Iterators, Generators, Comprehensions and Functional Tools | [lesson](08-modern-python/generators-functional/README.md) | [ex](08-modern-python/generators-functional/exercises.md) | [sum](08-modern-python/generators-functional/summary.md) | done |
| Concurrency in Python | [lesson](08-modern-python/async-concurrency/README.md) | [ex](08-modern-python/async-concurrency/exercises.md) | [sum](08-modern-python/async-concurrency/summary.md) | done |
| Threads, Processes and Futures | [overview](08-modern-python/concurrency/README.md)<br>[Threads, Processes and Futures in Practice](08-modern-python/concurrency/01-threads-processes-and-futures.md) | – | [sum](08-modern-python/concurrency/summary.md) | done |
| Modern Python Language Features | [lesson](08-modern-python/modern-syntax/README.md) | [ex](08-modern-python/modern-syntax/exercises.md) | [sum](08-modern-python/modern-syntax/summary.md) | done |
| Performance, Profiling and Memory | [lesson](08-modern-python/performance-profiling/README.md) | [ex](08-modern-python/performance-profiling/exercises.md) | [sum](08-modern-python/performance-profiling/summary.md) | done |
| Python Internals | [overview](08-modern-python/internals/README.md)<br>[The Python Data Model and CPython Internals](08-modern-python/internals/01-python-data-model-and-internals.md)<br>[Build a Tiny Interpreter](08-modern-python/internals/02-build-a-tiny-interpreter.md) | – | [sum](08-modern-python/internals/summary.md) | done |
| Exceptions, Logging and Testing | [lesson](08-modern-python/exceptions-logging-testing/README.md) | [ex](08-modern-python/exceptions-logging-testing/exercises.md) | [sum](08-modern-python/exceptions-logging-testing/summary.md) | done |
| Testing in Depth | [overview](08-modern-python/testing-in-depth/README.md)<br>[Testing in Depth](08-modern-python/testing-in-depth/01-pytest-mocking-and-property-testing.md) | – | [sum](08-modern-python/testing-in-depth/summary.md) | done |
| Packaging, Environments and Developer Tooling | [lesson](08-modern-python/packaging-tooling/README.md) | [ex](08-modern-python/packaging-tooling/exercises.md) | [sum](08-modern-python/packaging-tooling/summary.md) | done |
| Engineering Workflow | [overview](08-modern-python/engineering-workflow/README.md)<br>[Engineering Workflow](08-modern-python/engineering-workflow/01-ci-docker-pre-commit-and-publishing.md) | – | [sum](08-modern-python/engineering-workflow/summary.md) | done |
| Standard Library Toolbox | [overview](08-modern-python/stdlib-toolbox/README.md)<br>[The Standard Library Toolbox](08-modern-python/stdlib-toolbox/01-regex-datetime-subprocess-argparse.md) | – | [sum](08-modern-python/stdlib-toolbox/summary.md) | done |
| Backend with FastAPI | [overview](08-modern-python/backend-with-fastapi/README.md)<br>[Building a Web API with FastAPI](08-modern-python/backend-with-fastapi/01-building-a-web-api-with-fastapi.md) | – | [sum](08-modern-python/backend-with-fastapi/summary.md) | done |
| Database Access | [overview](08-modern-python/database-access/README.md)<br>[Database Access from Python](08-modern-python/database-access/01-sqlalchemy-and-database-access.md) | – | [sum](08-modern-python/database-access/summary.md) | done |
| Data with NumPy and pandas | [overview](08-modern-python/data-with-numpy-pandas/README.md)<br>[NumPy and pandas Essentials](08-modern-python/data-with-numpy-pandas/01-numpy-and-pandas-essentials.md) | – | [sum](08-modern-python/data-with-numpy-pandas/summary.md) | done |

## 09 Interview playbook

Turning knowledge into offers. Overview: [09-interview-playbook/README.md](09-interview-playbook/README.md).

| Topic | Lessons | Exercises | Summary | Status |
|-------|---------|-----------|---------|--------|
| Problem-Solving Patterns for Coding Interviews | [lesson](09-interview-playbook/problem-solving-patterns/README.md) | [ex](09-interview-playbook/problem-solving-patterns/exercises.md) | [sum](09-interview-playbook/problem-solving-patterns/summary.md) | done |
| Worked Problems | [overview](09-interview-playbook/worked-problems/README.md)<br>[Ten Worked Interview Problems](09-interview-playbook/worked-problems/01-ten-worked-interview-problems.md)<br>[Worked Problems, Part 2](09-interview-playbook/worked-problems/02-graph-string-dp-and-design-rounds.md) | – | [sum](09-interview-playbook/worked-problems/summary.md) | done |
| System Design Basics | [overview](09-interview-playbook/system-design-basics/README.md)<br>[System Design, Part 2](09-interview-playbook/system-design-basics/02-five-more-designs.md)<br>[System Design, Part 3](09-interview-playbook/system-design-basics/03-caching-failure-modes-and-reliability.md) | [ex](09-interview-playbook/system-design-basics/exercises.md) | [sum](09-interview-playbook/system-design-basics/summary.md) | done |
| Rapid-Fire Python and CS Questions | [lesson](09-interview-playbook/python-and-cs-rapid-fire/README.md) | [ex](09-interview-playbook/python-and-cs-rapid-fire/exercises.md) | [sum](09-interview-playbook/python-and-cs-rapid-fire/summary.md) | done |
| Behavioral Interviews, the Hiring Process and Your Preparation Plan | [lesson](09-interview-playbook/behavioral-and-process/README.md) | [ex](09-interview-playbook/behavioral-and-process/exercises.md) | [sum](09-interview-playbook/behavioral-and-process/summary.md) | done |

## 10 Security

Writing software that holds up against attackers. Overview: [10-security/README.md](10-security/README.md).

| Topic | Lessons | Exercises | Summary | Status |
|-------|---------|-----------|---------|--------|
| Threat Modeling and Secure Python | [overview](10-security/threat-modeling/README.md)<br>[Threat Modeling and Secure Python](10-security/threat-modeling/01-threat-modeling-and-secure-python.md) | – | [sum](10-security/threat-modeling/summary.md) | done |
| Authentication and Authorization | [overview](10-security/authentication/README.md)<br>[Authentication and Authorization](10-security/authentication/01-authn-authz-sessions-jwt.md) | – | [sum](10-security/authentication/summary.md) | done |
| Web Vulnerabilities | [overview](10-security/web-vulnerabilities/README.md)<br>[Common Web Vulnerabilities in Python](10-security/web-vulnerabilities/01-owasp-top-ten-in-python.md) | – | [sum](10-security/web-vulnerabilities/summary.md) | done |
| Secrets and Supply Chain | [overview](10-security/secrets-and-supply-chain/README.md)<br>[Secrets, Dependencies and Hardening](10-security/secrets-and-supply-chain/01-secrets-dependencies-and-hardening.md) | – | [sum](10-security/secrets-and-supply-chain/summary.md) | done |

## 11 Distributed systems

How systems made of many machines stay correct and available. Overview: [11-distributed-systems/README.md](11-distributed-systems/README.md).

| Topic | Lessons | Exercises | Summary | Status |
|-------|---------|-----------|---------|--------|
| Foundations of Distributed Systems | [overview](11-distributed-systems/foundations/README.md)<br>[Failures, Time and Clocks in Distributed Systems](11-distributed-systems/foundations/01-failures-time-and-clocks.md) | – | [sum](11-distributed-systems/foundations/summary.md) | done |
| Replication and Sharding | [overview](11-distributed-systems/replication-sharding/README.md)<br>[Replication, Quorums and Sharding](11-distributed-systems/replication-sharding/01-replication-and-sharding.md) | – | [sum](11-distributed-systems/replication-sharding/summary.md) | done |
| Consensus | [overview](11-distributed-systems/consensus/README.md)<br>[Consensus and Raft](11-distributed-systems/consensus/01-consensus-and-raft.md) | – | [sum](11-distributed-systems/consensus/summary.md) | done |
| Distributed Transactions and Reliability Patterns | [overview](11-distributed-systems/transactions/README.md)<br>[Idempotency, Retries, Circuit Breakers, Sagas and the Outbox](11-distributed-systems/transactions/01-idempotency-retries-and-sagas.md) | – | [sum](11-distributed-systems/transactions/summary.md) | done |
| Messaging and Storage | [overview](11-distributed-systems/messaging-storage/README.md)<br>[Logs, Queues and LSM Trees](11-distributed-systems/messaging-storage/01-logs-queues-and-lsm-trees.md) | – | [sum](11-distributed-systems/messaging-storage/summary.md) | done |
| Observability | [overview](11-distributed-systems/observability/README.md)<br>[Observability](11-distributed-systems/observability/01-observability-logs-metrics-traces-slos.md) | – | [sum](11-distributed-systems/observability/summary.md) | done |

## Revision tools

| Page | Purpose |
|------|---------|
| [Glossary](GLOSSARY.md) | every term in plain words, linked to the lesson that teaches it |
| [Spaced schedule](revision/schedule.md) | when to review what |
| [Progress tracker](revision/PROGRESS.md) | tick off topics and log mistakes |
| [Roadmap](ROADMAP.md) | verification status and what is still missing |

