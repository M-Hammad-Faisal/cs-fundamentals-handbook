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
| 04 | [Object-oriented design](04-oop/) | [OOP principles, inheritance types and SOLID](04-oop/oop-principles/README.md) |
| 05 | [Databases](05-databases/) | Relational model, SQL, indexes, transactions, normalization, NoSQL |
| 06 | [Operating systems](06-operating-systems/) | Processes, threads, scheduling, memory, concurrency, file systems |
| 07 | [Networking](07-networking/) | OSI and TCP/IP, DNS, HTTP, TLS, load balancing |
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
