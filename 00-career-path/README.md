# Career Path: Software Engineering in the Age of AI

A map for three readers: a **second-year student** choosing what to learn, an **early-career engineer** deciding where to go deep, and an **experienced engineer** who wants a fast, honest revision of what still matters. It says which roles are growing, what AI changes about the work, and which parts of this handbook to use for each goal.

> **Read this page as a forecast, not a promise.** The job market moves faster than a handbook. The role trends below come from public reports (linked, and mostly secondary sources) and from how the work is changing; treat them as direction, check current job postings before big decisions, and revisit this page every six months.

## 1. What is happening to the work (2026)

- **AI coding assistants now write a large share of routine code.** Boilerplate, glue code, tests for obvious cases and first drafts of functions are cheap. What is *not* cheap: deciding what to build, breaking a problem into parts, spotting subtle bugs, securing and operating the result, and being accountable for it.
- **The entry-level market is tougher and the bar is higher.** Reports disagree on how much (figures such as "60% fewer junior postings" circulate, but they are hard to verify and the market looks split rather than uniformly shrinking), yet they agree on the direction: employers want people who can take a small project from idea to deployment, read and review code, and use AI tools *with judgment* ([a Dice summary](https://www.dice.com/career-advice/the-new-junior-developer-harder-to-land-harder-to-replace), [one overview of the 2026 market](https://news.lavx.hu/article/state-of-the-software-engineering-job-market-in-2026)).
- **Demand is concentrated in specific areas.** AI/ML engineering is repeatedly reported as the fastest-growing technical role ([LinkedIn's list, via Dice](https://www.dice.com/career-advice/ai-related-jobs-top-linkedins-fastest-growing-roles-list-for-2026); the World Economic Forum's *Future of Jobs 2025* projects strong growth for AI and big-data specialists to 2030, as summarised [here](https://365datascience.com/career-advice/career-guides/ai-engineer-job-outlook-2025/)). Data engineering, cloud and platform work and security show steady or rising demand in the same reports, though the evidence is thinner.
- **Fundamentals matter more, not less.** If a tool writes the code, your value is in **verifying** it. You cannot review a concurrency fix, a SQL query plan or a threat model you do not understand. Recruiters quoted in these reports rarely hire people with AI skills but weak core skills.

**The durable advice:** be strong on fundamentals (this handbook), be fluent with AI tools, and be able to show real, deployed work.

## 2. Roles that look strong for the next three to five years

"Strong" here means growing demand or a durable need, according to the sources above plus the direction of the work. Every role below is built on the same core (parts 01 to 07).

| Role | What you do | Demand outlook | Use these parts of the handbook | A first project |
|------|-------------|----------------|-------------------------------|-----------------|
| **AI / LLM application engineer** | Build products on top of models: retrieval, tool use, evaluation, cost and latency control, safety | Fastest growing in the reports; also volatile and fashion-driven | [Python](../08-modern-python/README.md), [web APIs](../08-modern-python/backend-with-fastapi/01-building-a-web-api-with-fastapi.md), [databases](../05-databases/README.md), [testing](../08-modern-python/testing-in-depth/01-pytest-mocking-and-property-testing.md), [observability](../11-distributed-systems/observability/01-observability-logs-metrics-traces-slos.md), [security](../10-security/README.md) | A document question-answering service with an evaluation set, tests and cost tracking |
| **ML engineer / data scientist** | Train, evaluate and ship models; build features and pipelines | Strong, but needs math and statistics beyond this handbook | [NumPy and pandas](../08-modern-python/data-with-numpy-pandas/01-numpy-and-pandas-essentials.md), [math for CS](../00-foundations/math-for-cs/README.md), [algorithms](../03-algorithms/README.md) | A reproducible model with a baseline, honest metrics and a served endpoint |
| **Data engineer** | Pipelines, warehouses, streaming, data quality | Steady to strong; reported as a shortage area | [SQL](../05-databases/relational-sql/README.md), [PostgreSQL](../05-databases/postgresql/README.md), [logs and queues](../11-distributed-systems/messaging-storage/01-logs-queues-and-lsm-trees.md), [concurrency](../08-modern-python/concurrency/01-threads-processes-and-futures.md) | An incremental pipeline from a public API into a database with checks and alerts |
| **Platform / cloud / SRE engineer** | Infrastructure, deployment, reliability, cost; internal platforms (including for AI workloads) | Steady to strong | [OS](../06-operating-systems/README.md), [containers](../06-operating-systems/containers/01-containers-and-namespaces.md), [networking](../07-networking/README.md), [distributed systems](../11-distributed-systems/README.md), [CI and Docker](../08-modern-python/engineering-workflow/01-ci-docker-pre-commit-and-publishing.md) | Deploy a small service with CI, metrics, an SLO and a rollback |
| **Security engineer** (application, cloud, AI security) | Threat modeling, secure design, detection, supply-chain and AI-system security | Steady to strong; attackers use AI too | [Security](../10-security/README.md), [TLS](../07-networking/tls-security/README.md), [debugging with packets](../07-networking/debugging/README.md) | Threat-model and harden a project you own; write the findings up |
| **Backend / distributed systems engineer** | APIs, data models, reliability and scale for products | Steady (the broad middle of the market) | [Databases](../05-databases/README.md), [system design](../09-interview-playbook/system-design-basics/README.md), [distributed systems](../11-distributed-systems/README.md) | A multi-service app with idempotent writes, queues and tests |
| **Full-stack / product engineer** | Features end to end, close to users | Steady, but the most exposed to AI automation of routine work; strongest for people with product sense | [Python](../08-modern-python/README.md) plus front-end skills elsewhere | A real product with real users and measured impact |
| **Systems / performance / embedded and edge engineer** | Low-level and performance-critical software, devices, GPUs, runtimes | Niche but durable; hard to automate | [CPU caches](../00-foundations/computer-basics/cpu-caches-and-memory-hierarchy.md), [OS](../06-operating-systems/README.md), [internals](../08-modern-python/internals/01-python-data-model-and-internals.md) plus C, Rust or Go | A small database engine or an HTTP server from sockets |

You can change roles; the shared core is why. **Pick a role by what you enjoy debugging**, not only by headlines.

## 3. Skills that rise in value when AI writes code

| Skill | Why it matters more now | Where to build it |
|-------|-------------------------|-------------------|
| **Reading and reviewing code** | Much of your day becomes checking generated or inherited code | [Engineering practice](engineering-practice.md) |
| **Testing and verification** | Tests are how you *know* generated code is right | [Testing in depth](../08-modern-python/testing-in-depth/01-pytest-mocking-and-property-testing.md) |
| **Systems thinking** (failure, scale, cost) | Models do not carry accountability for the 3 a.m. outage | [Distributed systems](../11-distributed-systems/README.md), [system design](../09-interview-playbook/system-design-basics/README.md) |
| **Security judgment** | Generated code often contains the classic bugs, and AI adds new attack surface | [Security](../10-security/README.md) |
| **Data modelling and SQL** | Almost every product, including every AI product, is a data product | [Databases](../05-databases/README.md) |
| **Specification and communication** | Clear problem statements get better results from tools *and* teammates | [Engineering practice](engineering-practice.md) |
| **Fundamentals (complexity, data structures, OS, networking)** | They let you judge what is plausible, fast and safe | Parts [01](../01-complexity/README.md) to [07](../07-networking/README.md) |

**Use AI tools deliberately while learning:** write the first attempt yourself, then compare; ask the tool to explain, not just to produce; always run and test what it gives you. If you cannot explain a line, you do not own it yet.

## 4. Levels: scope of responsibility, not years

| Level | Scope | You are trusted to... |
|-------|-------|------------------------|
| **Junior** | A task | Finish well-defined work with guidance, and verify it |
| **Mid-level** | A feature | Own it end to end: design, build, test, ship, operate |
| **Senior** | A system or service | Make trade-offs, own reliability, unblock and grow others |
| **Staff and beyond** | A domain or several teams | Pick the right problem, set direction, influence without authority |

Titles and years vary by company and by period; what moves you up is **scope and impact**. Management and the individual-contributor (IC) path both lead to senior leadership.

## 5. Three ways to use this handbook

### A. You are a second-year student (or earlier): a four-semester map

| When | Focus | Handbook | Build |
|------|-------|----------|-------|
| Now | Programming, tools | [Start here](../00-start-here/README.md), [foundations](../00-foundations/README.md), [complexity](../01-complexity/README.md) | Three small command-line projects on GitHub |
| Next semester | Core CS | [Data structures](../02-data-structures/README.md), [algorithms](../03-algorithms/README.md), [OOP](../04-oop/README.md) | Solve about 60 problems; one project using classes and tests |
| Then | Systems | [Databases](../05-databases/README.md), [OS](../06-operating-systems/README.md), [networking](../07-networking/README.md) | A web API with a database, tests and Docker, deployed |
| Before internships | Professional skills | [Modern Python](../08-modern-python/README.md), [security](../10-security/README.md), [engineering practice](engineering-practice.md) | Polish one project: README, CI, tests, a short design doc |
| Final year | Specialise and interview | A role from section 2; [distributed systems](../11-distributed-systems/README.md); the [interview playbook](../09-interview-playbook/README.md) | A portfolio piece in your chosen role |

### B. You are early in your career (0 to 3 years)

- **First 90 days at a job:** read the codebase with the method in [engineering practice](engineering-practice.md), fix small bugs, write tests, learn how deploys and incidents work.
- **Then:** pick a role from section 2 and go deep through the matching parts; own a feature end to end; write one design document; get on call and write a postmortem.
- **Habit:** keep a "wins with numbers" document (for example "cut report time from 8 hours to 20 minutes").

### C. You are an experienced engineer revising

You do not need to read in order. Skim the **summaries** (one page each) first, then open the lesson where you hesitate, then run the exercises.

| Your direction | Skim these first |
|----------------|------------------|
| Preparing for interviews | [Playbook](../09-interview-playbook/README.md): patterns, worked problems, system design parts 1 to 3, behavioral |
| Moving towards AI-backed products | [Python](../08-modern-python/README.md) (typing, async, testing, FastAPI), [databases](../05-databases/README.md), [security](../10-security/README.md), [observability](../11-distributed-systems/observability/01-observability-logs-metrics-traces-slos.md) |
| Moving towards platform or SRE | [OS](../06-operating-systems/README.md), [containers](../06-operating-systems/containers/README.md), [networking](../07-networking/README.md), [distributed systems](../11-distributed-systems/README.md) |
| Moving towards senior or staff | [System design](../09-interview-playbook/system-design-basics/README.md), [distributed systems](../11-distributed-systems/README.md), [engineering practice](engineering-practice.md) |
| Plugging a gap quickly | The [glossary](../GLOSSARY.md), then the [index](../INDEX.md) to find the topic |

A good two-week revision loop: one topic per evening (summary, then exercises without looking at solutions), and the [spaced schedule](../revision/schedule.md) for review.

## 6. Interview readiness checklist

- [ ] I can analyze loops and recursion with Big-O and choose a data structure and justify it.
- [ ] I know the common patterns: two pointers, sliding window, binary search, BFS/DFS, dynamic programming.
- [ ] I can explain OOP, SOLID and common patterns with real examples.
- [ ] I can write and tune SQL and explain indexes, transactions and isolation.
- [ ] I can explain processes versus threads, deadlocks and the GIL, and what happens when you type a URL in a browser.
- [ ] I can design a system (URL shortener, rate limiter, feed, ledger) and discuss failure modes and trade-offs.
- [ ] I can review a piece of code for bugs, tests and security, and explain how I would verify AI-generated code.
- [ ] I can show a deployed project and tell two stories with numbers about real impact.

## 7. Habits that compound

- **Build and ship.** A deployed project with tests, a README and a clear history shows more than any certificate.
- **Teach what you learn** (writing exposes gaps quickly) and **read other people's code and design documents**.
- **Measure impact, not effort.**
- **Practice a little every day** (see the [revision schedule](../revision/schedule.md)); rest is part of learning.
- **Revisit your direction** every six months: the tools and the market will have moved.

## 8. How the rest of this part fits

- [Engineering practice](engineering-practice.md): reading code, refactoring, reviews, design documents, estimating, incidents, and a "what next" table.
- Everything else is in the [index](../INDEX.md), in order, with the [progress tracker](../revision/PROGRESS.md) to log what you finish.

Back to the [handbook home](../README.md).
