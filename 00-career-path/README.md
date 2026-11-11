# Software Engineering Career Path: End to End

A practical map from first job to senior and staff level, written for backend-leaning engineers (Python first). Use it to decide what to learn next and to check that your learning matches the level you want.

> Titles and expectations vary by company. Treat the levels as *scope of responsibility*, not as job titles.

## 1. The levels at a glance

| Level | Typical experience | Scope | You are trusted to... |
|-------|--------------------|-------|-----------------------|
| **Junior / Associate** | 0 to 2 years | A task | Finish well-defined tickets with guidance |
| **Software Engineer (mid)** | 2 to 5 years | A feature | Own a feature end to end: design, build, test, ship |
| **Senior Engineer** | 5 to 8 years | A system or service | Design systems, make trade-offs, unblock others, own reliability |
| **Staff Engineer** | 8+ years | A domain or several teams | Set technical direction, solve ambiguous cross-team problems |
| **Principal / Distinguished** | 12+ years | A company or industry | Shape long-term strategy and standards |

Years are a rough guide. What actually moves you up is **scope** and **impact**, not time served.

## 2. What each level really requires

### Junior to mid: become reliable
- Write clean, tested, readable code in one main language (Python).
- Use Git, code review, debugging tools, and a debugger rather than only `print`.
- Understand the basics of your stack: HTTP, databases, the command line.
- Finish tasks without constant help; ask good questions with what you tried.
- **Learn from this handbook:** complexity, core data structures, OOP, SQL basics.

### Mid to senior: become independent and broad
- Design a feature or small service, write a short design doc, and handle trade-offs.
- Go deep on databases (indexes, transactions), concurrency, and API design.
- Own production: monitoring, alerts, incident response, on-call, rollbacks.
- Review others' code well and raise the bar on tests and documentation.
- Estimate honestly and communicate risk early.
- **Learn from this handbook:** algorithms, OS and networking fundamentals, system design basics, concurrency.

### Senior to staff: multiply the team
- Pick the *right problem*, not only solve the assigned one.
- Lead designs that span teams; write proposals and get alignment.
- Mentor, grow other seniors, and shape engineering practices.
- Balance technical debt against delivery with a business reason.
- Make decisions with incomplete information and communicate them clearly.

### Staff and beyond
- Define multi-year technical strategy, influence without authority.
- Be a connector: translate between business goals and architecture.
- Choose the **management path** or stay on the **individual contributor (IC) path**. Both lead to senior leadership.

## 3. The skills stack

Think of your skills in layers. Weak lower layers show up as unstable work higher up.

```
            Leadership & communication
        System design & architecture
     Specialty (backend, data, platform, ML)
   Engineering practice (testing, CI/CD, observability)
 Core CS (DSA, OS, networking, databases, OOP)
Programming language mastery (Python)
```

| Layer | Examples | Where in this repo |
|-------|----------|--------------------|
| Language mastery | Python internals, typing, async | `08-modern-python` |
| Core CS | Big-O, data structures, algorithms, OS, networking, SQL | `01` to `07` |
| Engineering practice | Tests, Git, CI/CD, Docker, logging | `09-interview-playbook` and your job |
| Specialty | Django/FastAPI, scraping, data pipelines | Projects and work |
| System design | Scaling, caching, queues, trade-offs | `09-interview-playbook` |
| Leadership | Design docs, mentoring, estimation | On the job |

## 4. Choosing a track

| Track | What you do | Good fit if you like... |
|-------|-------------|--------------------------|
| **Backend engineer** | APIs, databases, business logic, integrations | Logic, data modelling, reliability |
| **Platform / DevOps / SRE** | Infrastructure, CI/CD, observability, reliability | Systems, automation, operating at scale |
| **Data engineer** | Pipelines, warehouses, streaming | Data flow, performance, correctness |
| **ML / AI engineer** | Model serving, pipelines, evaluation | Math, experimentation, applied research |
| **Full-stack** | Frontend plus backend | Seeing features end to end |
| **Automation / web-data engineer** | Browser automation, extraction, integrations | Messy real-world systems, resilience |

You can move between tracks. The core CS layer is shared, which is why the first parts of this handbook matter for all of them.

## 5. A staged plan

### Stage 1: Solid foundations (months 0 to 3)
- Revise this handbook's complexity, data structures and OOP parts.
- Solve about 40 to 60 problems across arrays, hash maps, linked lists, trees and graphs.
- Refresh SQL: joins, aggregation, subqueries, indexes.
- **Output:** a revision log (see [`revision/`](../revision/)) and 3 clean practice repos.

### Stage 2: Depth and breadth (months 3 to 9)
- Complete algorithms (sorting, searching, recursion, dynamic programming, graphs).
- Study OS (processes, threads, memory) and networking (TCP, HTTP, TLS, DNS).
- Learn concurrency properly: threads, processes, `asyncio`.
- Build one backend project with auth, a database, tests, Docker, and CI.
- **Output:** a deployed project and a written post about what you learned.

### Stage 3: Senior-level habits (months 9 to 24)
- Practice system design weekly: caching, queues, sharding, consistency trade-offs.
- Lead one feature or service from design doc to production.
- Add observability and reliability: metrics, tracing, SLOs, runbooks.
- Mentor others and review code with clear, kind feedback.
- **Output:** a design doc you wrote and a production system you own.

### Stage 4: Specialize or lead (years 2 to 4+)
- Choose a specialty (distributed systems, data, platform, applied AI) or the management path.
- Take ambiguous cross-team problems. Write proposals and get buy-in.
- Build a public track record: talks, posts, open-source contributions.

## 6. Habits that compound

- **Deliberate practice:** a little every day beats a weekend cram. See the [revision schedule](../revision/schedule.md).
- **Teach what you learn.** Writing it down (like this repo) exposes gaps fast.
- **Read other people's code** and good design docs.
- **Measure impact,** not effort: "reduced runtime from 8 hours to 2" beats "worked on tests".
- **Keep a brag document:** a running list of wins, with numbers, for résumés and reviews.
- **Build a network:** colleagues, open-source maintainers, local meetups.
- **Rest.** Sustained learning needs sleep and breaks.

## 7. Interview readiness checklist

- [ ] I can explain Big-O and analyze loops and recursion.
- [ ] I can implement and use arrays, linked lists, stacks, queues, hash maps, trees, heaps, graphs.
- [ ] I can pick the right data structure and justify it.
- [ ] I know the common patterns: two pointers, sliding window, binary search, BFS/DFS, DP.
- [ ] I can explain OOP, SOLID and common design patterns with real examples.
- [ ] I can write and optimize SQL, and explain indexes and transactions.
- [ ] I can explain processes vs threads, deadlocks, and the GIL.
- [ ] I can explain what happens when you type a URL in a browser.
- [ ] I can design a small system (URL shortener, rate limiter, feed) and discuss trade-offs.
- [ ] I have two or three stories with numbers about real impact.

## 8. How to use this handbook with the plan

1. Start at the [index](../INDEX.md) and follow the order of the parts.
2. For every chapter: read, then do the exercises, then read the summary.
3. Log what you finished in [`revision/PROGRESS.md`](../revision/PROGRESS.md).
4. Review on the spaced schedule in [`revision/schedule.md`](../revision/schedule.md).
5. Come back to this page every few months to check your stage and adjust.

## 9. Going deeper on the working habits

The technical levels above also need working habits: reading unfamiliar code, refactoring safely, writing commits, reviews and design docs, estimating, handling incidents. See [Software engineering practice](02-software-engineering-practice.md), which ends with a map of what to learn next.
