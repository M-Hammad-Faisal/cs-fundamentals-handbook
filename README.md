# CS Fundamentals Handbook

A detailed, example-driven revision guide to the computer science fundamentals every software engineer is expected to know: complexity analysis, data structures, algorithms, object-oriented design, databases and SQL, operating systems, networking, and modern Python.

Every chapter follows the same shape so you can skim or study deeply:

1. **The concept**: what it is and why it exists, in plain language.
2. **How it works**: internals, pseudocode, and Python code you can run.
3. **Complexity**: time and space, best, average and worst case.
4. **Two real-world examples**: where the idea shows up in production systems.
5. **Tips, tricks and pitfalls**: what interviewers ask and what bites people on the job.
6. **Check yourself**: short questions to test recall.

Code is in Python 3.10+ unless a chapter says otherwise.

## Contents

See [INDEX.md](INDEX.md) for the full map with status, and [the career path](00-career-path/README.md) for how it all fits together.

Each concept is a folder holding `README.md` (lesson), `exercises.md` (practice with solutions) and `summary.md` (one-page recap).

| # | Part | Chapters |
|---|------|----------|
| 00 | [Career path](00-career-path/) | [Software engineering career path, end to end](00-career-path/README.md) |
| 01 | [Complexity](01-complexity/) | [Big-O and complexity analysis](01-complexity/big-o/README.md) |
| 02 | [Data structures](02-data-structures/) | [Arrays and strings](02-data-structures/arrays-strings/README.md), [linked lists](02-data-structures/linked-lists/README.md), [stacks and queues](02-data-structures/stacks-queues/README.md), [hash tables](02-data-structures/hash-tables/README.md), [trees](02-data-structures/trees/README.md), [heaps](02-data-structures/heaps/README.md), [tries](02-data-structures/tries/README.md), [graphs](02-data-structures/graphs/README.md) |
| 03 | [Algorithms](03-algorithms/) | [Sorting](03-algorithms/sorting/README.md), [searching](03-algorithms/searching/README.md), [recursion and backtracking](03-algorithms/recursion-backtracking/README.md), [dynamic programming](03-algorithms/dynamic-programming/README.md), [greedy](03-algorithms/greedy/README.md), [advanced graph algorithms](03-algorithms/graph-algorithms/README.md) |
| 04 | [Object-oriented design](04-oop/) | [Classes and objects in depth](04-oop/classes-objects/README.md), [encapsulation and abstraction](04-oop/encapsulation-abstraction/README.md), [inheritance, mro and multiple inheritance](04-oop/inheritance-mro/README.md), [polymorphism and the python data model](04-oop/polymorphism-dunder/README.md), [composition, delegation, coupling and object design](04-oop/composition-design/README.md), [solid and other design principles](04-oop/solid/README.md), [design patterns i: creational](04-oop/patterns-creational/README.md), [design patterns ii: structural](04-oop/patterns-structural/README.md), [design patterns iii: behavioral](04-oop/patterns-behavioral/README.md) |
| 05 | [Databases](05-databases/) | [Relational model and SQL](05-databases/relational-sql/README.md), [indexes and query plans](05-databases/indexes-query-plans/README.md), [transactions and ACID](05-databases/transactions-acid/README.md), [normalization and schema design](05-databases/normalization-schema-design/README.md), [NoSQL](05-databases/nosql/README.md) |
| 06 | [Operating systems](06-operating-systems/) | [Processes and threads](06-operating-systems/processes-threads/README.md), [cpu scheduling](06-operating-systems/scheduling/README.md), [memory management and virtual memory](06-operating-systems/memory-virtual-memory/README.md), [concurrency, locks and deadlocks](06-operating-systems/concurrency-deadlocks/README.md), [file systems and i/o](06-operating-systems/file-systems-io/README.md) |
| 07 | [Networking](07-networking/) | [OSI and TCP/IP](07-networking/tcp-ip-osi/README.md), [DNS and HTTP](07-networking/dns-http/README.md), [TLS and security](07-networking/tls-security/README.md), [load balancing and CDNs](07-networking/load-balancing-cdn/README.md) |
| 08 | [Modern Python](08-modern-python/) | Typing, dataclasses, async, pattern matching, performance |
| 09 | [Interview playbook](09-interview-playbook/) | Problem-solving patterns and system design basics |
| | [Revision](revision/) | [Spaced schedule](revision/schedule.md) and [progress tracker](revision/PROGRESS.md) |

Chapters marked with a link are written. The rest are being added part by part.

## How to study with this

- **First pass:** read the concept and the two real-world examples. Skip the code.
- **Second pass:** type the code out yourself, without copying, then run it.
- **Revision:** cover the page and answer the "Check yourself" questions out loud.

## Contributing

Found a mistake or have a better example? Open an issue or a pull request. Corrections are welcome.

## License

MIT. Use it, share it, adapt it.
