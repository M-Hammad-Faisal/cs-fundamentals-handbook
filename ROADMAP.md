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
- The labs use only the standard library, SQLite and (for the TLS lab) the `openssl` command; no internet access is needed.

## Known gaps (honest list)

Not yet written as dedicated lessons:

| Area | Still to write |
|------|----------------|
| 03 Algorithms | (none: divide and conquer, number theory and string algorithms are written) |
| 05 Databases | PostgreSQL-specific features (the "what is a database" and ER-modeling overview, and the window-functions lab, are written) |
| 06 Operating systems | (none: boot, segmentation, containers and the threads-and-GIL lab are written) |
| 07 Networking | network debugging with `tcpdump`/Wireshark (routing, HTTP/2-3, REST and WebSockets are written) |
| 08 Modern Python | a bridge lesson from Python fundamentals |
| 09 Interview playbook | more worked walkthroughs (ten are written; add graph, DP-on-strings and design-pattern rounds) |
| All parts | per-topic `exercises.md` and `summary.md` were written before the detailed lessons and could be refreshed to match them |

Contributions and ideas for any of these are welcome.
