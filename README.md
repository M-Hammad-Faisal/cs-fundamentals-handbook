# CS Fundamentals Handbook

A detailed, example-driven guide to the computer science and engineering fundamentals every software engineer needs: complexity, data structures, algorithms, object-oriented design, databases, operating systems, networking, professional Python, security and distributed systems.

It serves three readers at once:

- **A second-year student** learning from zero: every idea has a plain-English explanation, a worked example you can run, practice with solutions and a self-check.
- **An early-career engineer** going deep in a chosen direction, with a [career path](00-career-path/README.md) that reflects where the field is heading (including how AI changes the work).
- **An experienced engineer revising**: every topic has a one-page summary and runnable exercises, so you can skim, test yourself and fill gaps fast.

<!-- stats:start -->
**379 pages, about 76,000 lines, 2,245 Python code blocks and 331 glossary terms.**
<!-- stats:end -->
The code in the lessons was run and the output comments were checked; `tools/check_code_blocks.py` re-runs the code in CI (see [ROADMAP.md](ROADMAP.md) for exactly what is and is not verified).

## Where to start

| You are... | Start with |
|------------|------------|
| New to programming or CS | [Start here](00-start-here/README.md), then [Foundations](00-foundations/README.md) |
| A student following a course | The parts in order: [complexity](01-complexity/README.md), [data structures](02-data-structures/README.md), [algorithms](03-algorithms/README.md), [OOP](04-oop/README.md), then [databases](05-databases/README.md), [OS](06-operating-systems/README.md), [networking](07-networking/README.md) |
| Choosing a career direction | The [career path](00-career-path/README.md): roles that look strong, what AI changes, and a learning map for each stage |
| An engineer revising | The one-page `summary.md` in each topic folder (find them in the [index](INDEX.md)), then the exercises |
| Preparing for interviews | The [interview playbook](09-interview-playbook/README.md), the [glossary](GLOSSARY.md) and the 12-week plan inside the playbook |
| Looking up one idea | The [glossary](GLOSSARY.md) (every term links to the lesson that teaches it) or the [index](INDEX.md) |

## How a topic is organised

Each topic is a folder holding a `README.md` (the quick-reference lesson), optional numbered detailed lessons (the step-by-step course, often a hands-on lab), `exercises.md` (practice with solutions) and `summary.md` (a one-page recap). Every lesson follows the same shape: prerequisites and objectives, plain words with an analogy, traced examples, runnable code with checked output, trade-offs, common mistakes, two real-world examples, practice and check-yourself questions. Code is Python 3.10+ unless a lesson says otherwise.

## Contents

The [index](INDEX.md) is the full map: every topic, every lesson, with its exercises and summary. In brief:

<!-- contents:start -->
| Part | Topics |
|------|--------|
| [Career path](00-career-path/README.md) | [Career Path](00-career-path/README.md), [Engineering Practice](00-career-path/engineering-practice.md) |
| [00 Foundations](00-foundations/README.md) | [Setting Up Your Computer for This Handbook](00-foundations/setup/README.md), [Computer Basics](00-foundations/computer-basics/README.md), [Math for Computer Science](00-foundations/math-for-cs/README.md), [Python Fundamentals](00-foundations/python-fundamentals/README.md), [Command Line and Git](00-foundations/command-line-and-git/README.md) |
| [01 Complexity](01-complexity/README.md) | [What Is an Algorithm?](01-complexity/01-what-is-an-algorithm.md), [Counting Steps and Understanding Growth](01-complexity/02-counting-steps-and-growth.md), [Big-O, Omega and Theta](01-complexity/03-big-o-omega-theta.md), [Analyzing Loops and Recursion Step by Step](01-complexity/04-analyzing-loops-and-recursion.md), [Space Complexity](01-complexity/05-space-complexity.md), [Best, Average, Worst Case and Amortized Analysis](01-complexity/06-cases-and-amortized-analysis.md), [Complexity of Python's Built-in Operations](01-complexity/07-python-operations-cheat-sheet.md), [Beyond Big-O](01-complexity/08-beyond-big-o.md), [Big-O and Complexity Analysis](01-complexity/big-o/README.md) |
| [02 Data structures](02-data-structures/README.md) | [Arrays and Strings](02-data-structures/arrays-strings/README.md), [Linked Lists](02-data-structures/linked-lists/README.md), [Stacks and Queues](02-data-structures/stacks-queues/README.md), [Hash Tables](02-data-structures/hash-tables/README.md), [Trees](02-data-structures/trees/README.md), [Heaps and Priority Queues](02-data-structures/heaps/README.md), [Tries](02-data-structures/tries/README.md), [Graphs](02-data-structures/graphs/README.md) |
| [03 Algorithms](03-algorithms/README.md) | [Sorting](03-algorithms/sorting/README.md), [Searching](03-algorithms/searching/README.md), [Recursion and Backtracking](03-algorithms/recursion-backtracking/README.md), [Divide and Conquer](03-algorithms/divide-and-conquer/README.md), [Dynamic Programming](03-algorithms/dynamic-programming/README.md), [Greedy Algorithms](03-algorithms/greedy/README.md), [Number Theory](03-algorithms/number-theory/README.md), [String Algorithms](03-algorithms/string-algorithms/README.md), [Advanced Graph Algorithms](03-algorithms/graph-algorithms/README.md) |
| [04 Object-oriented design](04-oop/README.md) | [OOP From Scratch](04-oop/00-oop-from-scratch.md), [UML and Class Diagrams](04-oop/01-uml-and-class-diagrams.md), [Classes and Objects in Depth](04-oop/classes-objects/README.md), [Encapsulation and Abstraction](04-oop/encapsulation-abstraction/README.md), [Inheritance, Method Resolution Order and Multiple Inheritance](04-oop/inheritance-mro/README.md), [Polymorphism and the Python Data Model](04-oop/polymorphism-dunder/README.md), [Composition, Delegation, Coupling and Object Design](04-oop/composition-design/README.md), [SOLID Principles and Other Design Principles](04-oop/solid/README.md), [Design Patterns](04-oop/design-patterns/README.md) |
| [05 Databases](05-databases/README.md) | [What Is a Database](05-databases/00-what-is-a-database-and-er-modeling.md), [The Relational Model and SQL](05-databases/relational-sql/README.md), [Indexes and Query Plans](05-databases/indexes-query-plans/README.md), [Transactions, ACID and Isolation](05-databases/transactions-acid/README.md), [Normalization and Schema Design](05-databases/normalization-schema-design/README.md), [NoSQL and Choosing a Database](05-databases/nosql/README.md), [PostgreSQL](05-databases/postgresql/README.md) |
| [06 Operating systems](06-operating-systems/README.md) | [What Is an Operating System?](06-operating-systems/00-what-is-an-operating-system.md), [Processes and Threads](06-operating-systems/processes-threads/README.md), [CPU Scheduling](06-operating-systems/scheduling/README.md), [Memory Management and Virtual Memory](06-operating-systems/memory-virtual-memory/README.md), [Concurrency, Synchronization and Deadlocks](06-operating-systems/concurrency-deadlocks/README.md), [File Systems and I/O](06-operating-systems/file-systems-io/README.md), [Boot and Startup](06-operating-systems/boot-and-startup/README.md), [Containers](06-operating-systems/containers/README.md) |
| [07 Networking](07-networking/README.md) | [The Network Stack](07-networking/tcp-ip-osi/README.md), [Routing](07-networking/routing/README.md), [DNS and HTTP](07-networking/dns-http/README.md), [TLS and Security Basics](07-networking/tls-security/README.md), [Load Balancing, Proxies, CDNs and Resilience](07-networking/load-balancing-cdn/README.md), [APIs and Real-Time Communication](07-networking/apis-realtime/README.md), [Network Debugging](07-networking/debugging/README.md) |
| [08 Modern Python](08-modern-python/README.md) | [From Python Fundamentals to Modern Python](08-modern-python/00-from-fundamentals-to-modern-python.md), [Type Hints and Static Typing](08-modern-python/typing-hints/README.md), [Dataclasses, NamedTuple and Enums](08-modern-python/dataclasses-enums/README.md), [Iterators, Generators, Comprehensions and Functional Tools](08-modern-python/generators-functional/README.md), [Concurrency in Python](08-modern-python/async-concurrency/README.md), [Threads, Processes and Futures](08-modern-python/concurrency/README.md), [Modern Python Language Features](08-modern-python/modern-syntax/README.md), [Performance, Profiling and Memory](08-modern-python/performance-profiling/README.md), [Python Internals](08-modern-python/internals/README.md), [Exceptions, Logging and Testing](08-modern-python/exceptions-logging-testing/README.md), [Testing in Depth](08-modern-python/testing-in-depth/README.md), [Packaging, Environments and Developer Tooling](08-modern-python/packaging-tooling/README.md), [Engineering Workflow](08-modern-python/engineering-workflow/README.md), [Standard Library Toolbox](08-modern-python/stdlib-toolbox/README.md), [Backend with FastAPI](08-modern-python/backend-with-fastapi/README.md), [Database Access](08-modern-python/database-access/README.md), [Data with NumPy and pandas](08-modern-python/data-with-numpy-pandas/README.md) |
| [09 Interview playbook](09-interview-playbook/README.md) | [Problem-Solving Patterns for Coding Interviews](09-interview-playbook/problem-solving-patterns/README.md), [Worked Problems](09-interview-playbook/worked-problems/README.md), [System Design Basics](09-interview-playbook/system-design-basics/README.md), [Rapid-Fire Python and CS Questions](09-interview-playbook/python-and-cs-rapid-fire/README.md), [Behavioral Interviews, the Hiring Process and Your Preparation Plan](09-interview-playbook/behavioral-and-process/README.md) |
| [10 Security](10-security/README.md) | [Threat Modeling and Secure Python](10-security/threat-modeling/README.md), [Authentication and Authorization](10-security/authentication/README.md), [Web Vulnerabilities](10-security/web-vulnerabilities/README.md), [Secrets and Supply Chain](10-security/secrets-and-supply-chain/README.md) |
| [11 Distributed systems](11-distributed-systems/README.md) | [Foundations of Distributed Systems](11-distributed-systems/foundations/README.md), [Replication and Sharding](11-distributed-systems/replication-sharding/README.md), [Consensus](11-distributed-systems/consensus/README.md), [Distributed Transactions and Reliability Patterns](11-distributed-systems/transactions/README.md), [Messaging and Storage](11-distributed-systems/messaging-storage/README.md), [Observability](11-distributed-systems/observability/README.md) |
<!-- contents:end -->

Also: the [glossary](GLOSSARY.md), the [revision schedule](revision/schedule.md), the [progress tracker](revision/PROGRESS.md) and the [roadmap](ROADMAP.md).

## How to study with this

- **First pass:** read the plain-words explanation and the diagrams. Skip the code.
- **Second pass:** type the code out yourself, without copying, then run it and change the inputs.
- **Practice:** do the problems before opening the solutions.
- **Revision:** cover the page and answer the "Check yourself" questions out loud; use the [spaced schedule](revision/schedule.md) and [progress tracker](revision/PROGRESS.md).

## Contributing

Found a mistake or have a better example? Open an issue or a pull request. Run `python tools/build_index.py` after adding or renaming a page so the index, tracker and contents stay in sync, and `python tools/check_code_blocks.py` and `python tools/check_links.py` before submitting (see [tools/README.md](tools/README.md)).

## License

MIT. Use it, share it, adapt it.
