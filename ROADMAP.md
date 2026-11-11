# Roadmap

Where the handbook stands and what could come next. Readers can ignore this page; it is for contributors and for anyone curious about the project's standards.

## Quality bar for every topic file

1. **Prerequisites and learning objectives** at the top.
2. **In plain words** with an everyday analogy.
3. **How it works**, traced step by step on a small example (diagrams in text).
4. **Code** that runs, with checked output.
5. **Complexity / trade-offs / when to use it and when not to.**
6. **Common mistakes** and **two real-world examples.**
7. **Practice** (with solutions) and **Check yourself** (with answers).
8. **One topic per file**, grouped in folders, with an overview README that gives the learning path.

## Verification status

- Every page was run through a code-block runner on Python 3.15 (and the lessons require Python 3.10+). At the last full check, **263 of 276 pages ran cleanly**; pages added since were each run when written.
- The remaining 13 pages are not broken; they contain illustrative sketches that assume context: cheat-sheet snippets with placeholder variables (`words`, `nums`, `r.set(...)`), exercise solutions that call helpers defined in the matching lesson (`fifo`, `round_robin`, `qps`, `first_true`), or a script that expects a command-line argument. With the lesson code loaded, those exercise solutions run.
- Output comments in the newer lessons were compared with real output, and many were corrected along the way. Links were checked across the whole repository (0 broken), and a privacy check was run before every push.
- The [PostgreSQL features lesson](05-databases/postgresql/01-postgresql-specific-features.md) was first written without a server, then run against PostgreSQL 18.6 in Docker; one bug (`tags || 'vip'`) was fixed. Its `EXPLAIN` plan is illustrative.
- The labs use only the standard library, SQLite and (for the TLS lab) the `openssl` command; no internet access is needed.

## Known gaps (honest list)

Not yet written as dedicated lessons:

| Area | Still to write |
|------|----------------|
| 03 Algorithms | (none: divide and conquer, number theory and string algorithms are written) |
| 05 Databases | none written as dedicated lessons; the PostgreSQL lesson was run on PostgreSQL 18.6 |
| 06 Operating systems | (none: boot, segmentation, containers and the threads-and-GIL lab are written) |
| 07 Networking | none (routing, HTTP/2-3, REST, WebSockets and network debugging are written) |
| 08 Modern Python | none (bridge lesson written) |
| 09 Interview playbook | none (sixteen worked problems written, including graph, string DP and design-pattern rounds) |
| All parts | none (each topic's `exercises.md` and `summary.md` now link to its detailed lessons; their own content predates those lessons and is still valid) |

## Gap audit, November 2026 (Python-focused)

An audit of the whole handbook found these areas thin or missing. Status is updated as each is written.

| # | Area | What to add | Status |
|---|------|-------------|--------|
| 1 | Security | threat modeling and secure Python; authentication, sessions, JWT, OAuth; OWASP-style bugs (SSRF, path traversal, deserialization, access control); secrets, supply chain, hardening | in progress |
| 2 | Distributed systems | failures, clocks; replication and sharding; consensus (Raft); idempotency, retries, sagas; logs, queues, LSM trees; observability | planned |
| 3 | System design depth | five more designs; caching failure modes and reliability | planned |
| 4 | Python depth | data model and internals; threads, processes, futures; testing in depth; web APIs with FastAPI; SQLAlchemy; NumPy and pandas; CI, Docker, publishing; stdlib toolbox | planned |
| 5 | Other CS and engineering | tiny interpreter; CPU caches and memory hierarchy; software engineering practice; what to learn next | planned |
| 6 | Structure | exercises and summaries for apis-realtime, containers, debugging; an automated check that runs every code block | planned |

Contributions and ideas for any of these are welcome.
