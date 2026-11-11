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

- **Automated check** (`tools/check_code_blocks.py`, run in CI by `.github/workflows/check.yml`): it runs every Python code block on every page, in order, one fresh process per page. On the last full run, **263 pages contain code; 243 run cleanly and 20 are skipped on purpose** (listed with reasons in `tools/known-sketches.txt`). The skipped pages are older cheat sheets whose snippets assume names defined elsewhere on the page or in the lesson, pages that show the files of a small separate project, and pages that demonstrate an error on purpose. On those pages the code was run by hand when the lesson was written, but the automated check does not cover them. **Every `exercises.md` page is covered**: where solutions need helpers from the lessons, the page carries a collapsible setup block with that code, and the design-patterns page runs each solution in its own namespace (`<!-- run: isolated -->`).
- The checker verifies that code **runs**. It does **not** compare the `# output` comments with real output. For the lessons added in the 2026 expansion (parts 10 and 11 and the new Python, system design, networking and foundations lessons) every output comment was compared with real output by hand and corrected; for older lessons that was done at the time of writing.
- **Third-party packages:** a few lessons use `pytest`, `hypothesis`, `numpy`, `pandas`, `fastapi`, `sqlalchemy` (see `tools/requirements-check.txt`); everything else uses only the standard library, SQLite and the `openssl` command.
- **Run for real, not just read:** PostgreSQL 18.6 in Docker (the PostgreSQL lesson); `tcpdump` on a generated capture (network debugging); a built wheel installed into a clean virtual environment, `ruff`, `mypy`, `pytest` and a Docker image build and run (engineering workflow); FastAPI through its `TestClient`; random-failure safety tests for the Raft simulator.
- **Not executed:** the GitHub Actions and PyPI publishing workflows (checked only for valid YAML), the concurrent two-worker and `SERIALIZABLE` behaviour of the PostgreSQL lesson, and Wireshark (`tshark` was not available). Timing figures (speed-ups, latency ratios) are examples from one laptop and will differ on yours.
- **Navigation is generated:** `tools/build_index.py` builds the index, progress tracker and README contents from the files on disk (one row per topic, same columns everywhere), and CI fails if they are stale.
- **Uniform topic folders:** every topic folder has `README.md`, `exercises.md` and `summary.md` in the same format (`tools/normalize_topics.py`): exercises are `## Problems` plus collapsible solutions, summaries are `## Key facts`, `## Pitfalls` and an optional `## Self-check`, and CI fails if a page drifts from the format.
- Links are checked across the whole repository (`tools/check_links.py`, 0 broken), and a privacy check was run before every push.

## Known gaps (honest list)

The original gap table is closed (every part has dedicated, run-and-checked lessons). The November 2026 audit added security, distributed systems, system design depth, Python depth and engineering practice; all of that is now written. What remains is the *next* layer of ideas; none of it blocks learning the material above.

| Area | Ideas for later |
|------|-----------------|
| Python | async web frameworks end to end (WebSockets with FastAPI, background workers with queues); Django; typing in depth (protocols, generics, TypedDict); profiling native extensions; Rust or C extensions; free-threaded Python in practice |
| Security | applied cryptography beyond the standard library (`cryptography` package: AEAD, signatures, key exchange); deeper web security (CSP in practice, browser security model); basics of penetration-testing methodology |
| Distributed systems | Paxos and its relatives; CRDTs in depth; distributed transactions across shards (Spanner-style); stream processing; Raft membership changes and snapshots |
| Data and ML | statistics for programmers; a first machine-learning project (scikit-learn); SQL window functions and query optimisation deep dive; data pipelines |
| Systems | compilers beyond the toy (SSA, optimisation passes); writing a small database engine; GPUs and parallel computing |
| Quality | automated comparison of output comments with real output; a runnable test environment per lesson (a dev container); translations |

## Gap audit, November 2026 (Python-focused)

| # | Area | What was added | Status |
|---|------|----------------|--------|
| 1 | Security | [Part 10](10-security/README.md): threat modeling and secure Python; authentication, sessions, JWT, OAuth with PKCE; OWASP-style bugs (SQL injection, XSS, SSRF, path traversal, zip-slip, open redirect, mass assignment, ReDoS); secrets, supply chain, hardening | written |
| 2 | Distributed systems | [Part 11](11-distributed-systems/README.md): failures and clocks; replication, quorums and consistent hashing; a Raft simulator with random-failure tests; idempotency, retries, sagas and the outbox; logs, queues, an LSM tree and Bloom filters; observability and SLOs | written |
| 3 | System design depth | [Five more designs](09-interview-playbook/system-design-basics/02-five-more-designs.md); [caching failure modes and reliability](09-interview-playbook/system-design-basics/03-caching-failure-modes-and-reliability.md) | written |
| 4 | Python depth | internals; a tiny interpreter; threads, processes and futures; testing in depth; FastAPI; SQLAlchemy; NumPy and pandas; CI, Docker and publishing; the standard library toolbox (see [modern Python](08-modern-python/README.md)) | written |
| 5 | Other CS and engineering | [CPU caches](00-foundations/computer-basics/cpu-caches-and-memory-hierarchy.md); [software engineering practice and what to learn next](00-career-path/engineering-practice.md) | written |
| 6 | Structure | exercises and summaries for apis-realtime, containers and debugging; the automated check described above | done |

Contributions and ideas for any of these are welcome.
