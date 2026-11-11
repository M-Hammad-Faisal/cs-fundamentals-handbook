# Roadmap

What could come next, and the limits of what has been checked. Readers can ignore this page; it is for contributors. How the pages are generated and checked is described in [`tools/README.md`](tools/README.md).

## Quality bar for every topic

1. **Prerequisites and learning objectives** at the top.
2. **In plain words** with an everyday analogy.
3. **How it works**, traced step by step on a small example.
4. **Code** that runs, with checked output.
5. **Complexity, trade-offs, when to use it and when not to.**
6. **Common mistakes** and **two real-world examples.**
7. **Practice** (with solutions) and **Check yourself** (with answers).
8. One topic per folder with `README.md`, `exercises.md` and `summary.md` in the standard format (CI enforces it).

## Open items

- **Independent review.** Nobody but the author has read the lessons. Ask a student and a working engineer to read three topics each and mark anything wrong or unclear; also re-check the career-path forecasts, which come from secondary sources.
- **Output comments.** CI proves code runs, not that `# output` comments are right. `tools/check_outputs.py` is advisory and compares single-line `print(...)  # value` comments; moving it into CI needs an allow-list for prose and machine-dependent values.
- **One page is skipped by the checker:** `05-databases/transactions-acid/README.md` (both blocks are fragments of the demo script). Everything else runs.
- **Not executed:** the GitHub Actions and PyPI publishing workflows (checked only for valid YAML), the concurrent and `SERIALIZABLE` behaviour of the PostgreSQL lesson, and Wireshark. Timing figures are examples from one laptop.

## Ideas for later

| Area | Ideas |
|------|-------|
| Python | async web frameworks end to end (WebSockets with FastAPI, background workers with queues); Django; typing in depth (protocols, generics, TypedDict); profiling native extensions; Rust or C extensions; free-threaded Python in practice |
| Security | applied cryptography beyond the standard library (`cryptography` package: AEAD, signatures, key exchange); deeper web security (CSP in practice, browser security model); basics of penetration-testing methodology |
| Distributed systems | Paxos and its relatives; CRDTs in depth; distributed transactions across shards (Spanner-style); stream processing; Raft membership changes and snapshots |
| Data and ML | statistics for programmers; a first machine-learning project (scikit-learn); SQL window functions and query optimisation deep dive; data pipelines |
| Systems | compilers beyond the toy (SSA, optimisation passes); writing a small database engine; GPUs and parallel computing |
| Quality | a runnable environment per lesson (dev container); translations |

Contributions and ideas for any of these are welcome.
