# CS Fundamentals Handbook

A detailed, example-driven revision guide to the computer science fundamentals every software engineer is expected to know: complexity analysis, data structures, algorithms, object-oriented design, databases and SQL, operating systems, networking, and modern Python.

This handbook is written so a **second-year student can learn from it** (and an experienced engineer can revise from it). It has **276 pages, about 57,000 lines and 1,743 Python examples**. The code in the lessons was run, and the output comments were checked against the real output.

## Two levels of every topic

1. **Quick-reference lesson** (`README.md` in each topic folder): the concept, how it works, complexity, two real-world examples, pitfalls, check-yourself questions. Skim it for revision.
2. **Detailed lessons** (numbered files such as `01-...md`): the step-by-step course for learning a topic from zero. Each has **prerequisites and learning objectives**, a **plain-words explanation with an analogy**, **traced examples and diagrams**, **runnable code**, **common mistakes**, **practice problems with collapsible solutions** and **check-yourself questions with answers**. Many are **hands-on labs**: you build a tiny file system, a DNS server, a TLS handshake on localhost, a replicated store, a load balancer.

Code is in Python 3.10+ unless a lesson says otherwise.

## Where to start

| You are... | Start with |
|------------|------------|
| New to programming or CS | [Start here](00-start-here/README.md), then [Foundations](00-foundations/README.md) and [OOP from scratch](04-oop/00-oop-from-scratch.md) |
| A student following a course | work through the parts in order: complexity, data structures, algorithms, OOP, then databases, OS, networking |
| Preparing for interviews | [Problem-solving patterns](09-interview-playbook/problem-solving-patterns/README.md), [ten worked problems](09-interview-playbook/worked-problems/01-ten-worked-interview-problems.md), [system design basics](09-interview-playbook/system-design-basics/README.md), the [12-week plan](09-interview-playbook/behavioral-and-process/README.md), plus the [glossary](GLOSSARY.md) |
| Looking up one idea | the [glossary](GLOSSARY.md) (every term links to the lesson that teaches it) or the [index](INDEX.md) |

## Contents

See [INDEX.md](INDEX.md) for the full map with status, and [the career path](00-career-path/README.md) for how it all fits together.

Each topic is a folder holding `README.md` (quick-reference lesson), numbered detailed lessons, `exercises.md` (practice with solutions) and `summary.md` (one-page recap).

| # | Part | Chapters |
|---|------|----------|
| 00 | [Foundations](00-foundations/) | [Setup](00-foundations/setup/README.md), [computer basics](00-foundations/computer-basics/README.md), [math for CS](00-foundations/math-for-cs/README.md), [Python fundamentals](00-foundations/python-fundamentals/README.md), [command line and Git](00-foundations/command-line-and-git/README.md) |
| 00 | [Career path](00-career-path/) | [Software engineering career path, end to end](00-career-path/README.md) |
| 01 | [Complexity](01-complexity/) | [Overview](01-complexity/README.md): [what is an algorithm](01-complexity/01-what-is-an-algorithm.md), [counting steps](01-complexity/02-counting-steps-and-growth.md), [Big-O](01-complexity/03-big-o-omega-theta.md), [analyzing code](01-complexity/04-analyzing-loops-and-recursion.md), [space](01-complexity/05-space-complexity.md), [cases and amortized](01-complexity/06-cases-and-amortized-analysis.md), [Python operation costs](01-complexity/07-python-operations-cheat-sheet.md), [beyond Big-O](01-complexity/08-beyond-big-o.md) |
| 02 | [Data structures](02-data-structures/README.md) | [Arrays and strings](02-data-structures/arrays-strings/README.md), [linked lists](02-data-structures/linked-lists/README.md), [stacks and queues](02-data-structures/stacks-queues/README.md), [hash tables](02-data-structures/hash-tables/README.md), [trees](02-data-structures/trees/README.md), [heaps](02-data-structures/heaps/README.md), [tries](02-data-structures/tries/README.md), [graphs](02-data-structures/graphs/README.md) |
| 03 | [Algorithms](03-algorithms/README.md) | [Sorting](03-algorithms/sorting/README.md), [searching](03-algorithms/searching/README.md), [recursion and backtracking](03-algorithms/recursion-backtracking/README.md), [dynamic programming](03-algorithms/dynamic-programming/README.md), [greedy](03-algorithms/greedy/README.md), [advanced graph algorithms](03-algorithms/graph-algorithms/README.md) |
| 04 | [Object-oriented design](04-oop/README.md) | [OOP from scratch](04-oop/00-oop-from-scratch.md), [Classes and objects in depth](04-oop/classes-objects/README.md), [encapsulation and abstraction](04-oop/encapsulation-abstraction/README.md), [inheritance, mro and multiple inheritance](04-oop/inheritance-mro/README.md), [polymorphism and the python data model](04-oop/polymorphism-dunder/README.md), [composition, delegation, coupling and object design](04-oop/composition-design/README.md), [solid and other design principles](04-oop/solid/README.md), [design patterns (25 patterns, one file each)](04-oop/design-patterns/README.md) |
| 05 | [Databases](05-databases/README.md) | [Relational model and SQL](05-databases/relational-sql/README.md), [indexes and query plans](05-databases/indexes-query-plans/README.md), [transactions and ACID](05-databases/transactions-acid/README.md), [normalization and schema design](05-databases/normalization-schema-design/README.md), [NoSQL](05-databases/nosql/README.md) |
| 06 | [Operating systems](06-operating-systems/README.md) | [What is an OS?](06-operating-systems/00-what-is-an-operating-system.md), [Processes and threads](06-operating-systems/processes-threads/README.md), [cpu scheduling](06-operating-systems/scheduling/README.md), [memory management and virtual memory](06-operating-systems/memory-virtual-memory/README.md), [concurrency, locks and deadlocks](06-operating-systems/concurrency-deadlocks/README.md), [file systems and i/o](06-operating-systems/file-systems-io/README.md) |
| 07 | [Networking](07-networking/README.md) | [OSI and TCP/IP](07-networking/tcp-ip-osi/README.md), [DNS and HTTP](07-networking/dns-http/README.md), [TLS and security](07-networking/tls-security/README.md), [load balancing and CDNs](07-networking/load-balancing-cdn/README.md) |
| 08 | [Modern Python](08-modern-python/) | [Type hints and static typing](08-modern-python/typing-hints/README.md), [dataclasses, namedtuple and enums](08-modern-python/dataclasses-enums/README.md), [iterators, generators, comprehensions and functional tools](08-modern-python/generators-functional/README.md), [concurrency: threads, processes and asyncio](08-modern-python/async-concurrency/README.md), [modern language features](08-modern-python/modern-syntax/README.md), [performance, profiling and memory](08-modern-python/performance-profiling/README.md), [exceptions, logging and testing](08-modern-python/exceptions-logging-testing/README.md), [packaging, environments and tooling](08-modern-python/packaging-tooling/README.md) |
| 09 | [Interview playbook](09-interview-playbook/) | [Problem-solving patterns](09-interview-playbook/problem-solving-patterns/README.md), [system design basics](09-interview-playbook/system-design-basics/README.md), [rapid-fire python and cs questions](09-interview-playbook/python-and-cs-rapid-fire/README.md), [behavioral interviews, hiring process and 12-week plan](09-interview-playbook/behavioral-and-process/README.md) |
| | [Revision](revision/) | [Spaced schedule](revision/schedule.md) and [progress tracker](revision/PROGRESS.md) |

Every part is written. Each topic folder's README lists its detailed lessons at the top.

## How to study with this

- **First pass:** read the plain-words explanation and the diagrams. Skip the code.
- **Second pass:** type the code out yourself, without copying, then run it and change the inputs.
- **Practice:** do the problems before opening the solutions.
- **Revision:** cover the page and answer the "Check yourself" questions out loud; use the [spaced schedule](revision/schedule.md) and [progress tracker](revision/PROGRESS.md).

## Contributing

Found a mistake or have a better example? Open an issue or a pull request. Corrections are welcome.

## License

MIT. Use it, share it, adapt it.
