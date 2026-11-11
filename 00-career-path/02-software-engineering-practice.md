# Software Engineering Practice: Reading Code, Refactoring, Reviews, Design Docs and Estimates

**Prerequisites:** [the career path](README.md), [Git and GitHub collaboration](../00-foundations/command-line-and-git/github-collaboration.md), [testing in depth](../08-modern-python/testing-in-depth/01-pytest-mocking-and-property-testing.md). **You will learn:** the working habits that separate a programmer who can solve exercises from an engineer teams trust: how to **read and map an unfamiliar codebase**, how to **refactor safely** (with a differential test that proves behaviour did not change), what good **commit messages, pull requests and code reviews** look like, how to write a short **design document**, how to **estimate** honestly with ranges, how to handle **technical debt and incidents**, and a **"what to learn next"** map. The code examples run offline.

## 1. In plain words

In a job, most of your time is not spent writing new programs from nothing. It is spent **understanding existing code, changing it without breaking it, explaining your changes to other people, and agreeing on what to build**. These skills are learnable and they compound: an engineer who is calm in an unfamiliar codebase and clear in writing is worth far more than one who is only fast at typing.

## 2. Reading an unfamiliar codebase

You will join projects with thousands of files and no one who remembers why. A method that works:

1. **Run it first.** Follow the README, get the tests passing, start the app. Understand what it *does* before how.
2. **Find the entry points:** `main`, the CLI commands, the web routes, the scheduled jobs. Everything starts there.
3. **Trace one real request or command end to end,** with a debugger or print statements, writing down the files it touches. One concrete path teaches more than reading everything.
4. **Read the tests:** they are executable documentation of intended behaviour, with examples.
5. **Use search aggressively** (`grep`/`rg`, "find usages" in the editor) and **git history** (`git log -p file`, `git blame`) to learn *why* a line exists.
6. **Draw the map:** modules, data stores, external services. Keep it small and correct.
7. **Ask better questions:** "I traced X to Y and expected Z; what am I missing?" respects people's time.

You can even let a script give you the first overview. This reads a package's source with the `ast` module (the same machinery as the [tiny interpreter](../08-modern-python/internals/02-build-a-tiny-interpreter.md)) and reports its size and what it depends on; point it at any project to get a map in seconds. Here it analyses the standard library's own `json` package:

```python
import ast, json, pathlib
from collections import Counter

def map_package(root: pathlib.Path):
    files, functions, classes, imports = 0, 0, 0, Counter()
    for path in sorted(root.rglob("*.py")):
        tree = ast.parse(path.read_text(), filename=str(path))
        files += 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions += 1
            elif isinstance(node, ast.ClassDef):
                classes += 1
            elif isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                imports[node.module.split(".")[0]] += 1
    return files, functions, classes, imports

root = pathlib.Path(json.__file__).parent
files, functions, classes, imports = map_package(root)
print("files:", files, "| has functions:", functions > 5, "| has classes:", classes >= 2)
print("most imported modules include 're':", "re" in dict(imports.most_common(5)))
# files: 6 | has functions: True | has classes: True
# most imported modules include 're': True
```

(The exact file count changes between Python versions, so the checks that matter are the stable facts.) A map of imports shows which parts depend on which, where the "core" is, and which modules everything else leans on, exactly what you need before changing anything.

## 3. Refactoring safely

**Refactoring** means changing the *structure* of code **without changing its behaviour**, to make it easier to understand and extend. The rules:

1. **Have tests first.** If there are none, write **characterization tests** that record what the code does *now*, even if it looks wrong.
2. **Change in small steps,** running the tests after each one.
3. **Do not mix refactoring with behaviour changes** in the same commit (reviewers cannot tell which is which). If you spot a bug, note it and fix it separately.
4. **Name things;** extract functions with intention-revealing names; replace magic numbers with constants; flatten nesting with early returns.

Here is typical legacy code: deeply nested, magic numbers, easy to misread.

```python
def process_legacy(orders):
    out = []
    for o in orders:
        if o["status"] == "paid":
            t = o["total"]
            if o.get("vip"):
                t = t - t * 0.1
            if t < 100:
                if o.get("country") == "UK":
                    t = t + 5
                else:
                    t = t + 10
            out.append((o["id"], round(t, 2)))
    return out
```

Refactored: each rule is a small named function and the constants have names; the arithmetic is deliberately **kept identical** (changing how money is computed is a separate, behaviour-changing task):

```python
VIP_DISCOUNT = 0.10
FREE_SHIPPING_FROM = 100
SHIPPING_FEES = {"UK": 5}
DEFAULT_SHIPPING_FEE = 10

def after_vip_discount(total, is_vip):
    return total - total * VIP_DISCOUNT if is_vip else total

def with_shipping(total, country):
    if total >= FREE_SHIPPING_FROM:
        return total
    return total + SHIPPING_FEES.get(country, DEFAULT_SHIPPING_FEE)

def process(orders):
    return [
        (o["id"], round(with_shipping(after_vip_discount(o["total"], o.get("vip")), o.get("country")), 2))
        for o in orders
        if o["status"] == "paid"
    ]
```

How do you know you did not change behaviour? Do a **differential test**: run old and new on thousands of random inputs and compare.

```python
import random

def random_order(rng, order_id):
    order = {"id": order_id, "status": rng.choice(["paid", "pending", "refunded"]), "total": round(rng.uniform(0, 250), 2)}
    if rng.random() < 0.5:
        order["vip"] = rng.random() < 0.5
    if rng.random() < 0.7:
        order["country"] = rng.choice(["UK", "US", "PK"])
    return order

rng = random.Random(7)
mismatches = 0
for trial in range(2000):
    orders = [random_order(rng, i) for i in range(rng.randint(0, 6))]
    if process_legacy(orders) != process(orders):
        mismatches += 1
print("random order lists where the refactoring changed the answer:", mismatches, "of 2000")
# random order lists where the refactoring changed the answer: 0 of 2000
```

Now the refactored version can be extended safely: a new shipping country is one dictionary entry instead of another nested branch. (The same technique, comparing a new implementation with the trusted old one on random input, is how large systems are migrated with confidence.) **Strangler pattern** for big rewrites: do not rewrite the whole system; route one feature at a time to the new code and delete the old part when nothing uses it.

## 4. Commit messages, pull requests and code review

**Commit messages** explain *why*, not just what; the diff already shows what. A useful convention:

```text
Add retry with backoff to the payment client

Timeouts from the card provider were failing checkouts on the first
attempt. Retry idempotent calls up to 3 times with exponential backoff
and jitter. Non-idempotent calls are never retried.

Fixes #482
```

A short subject line (about 50 to 72 characters, imperative mood: "Add", "Fix", not "Added"), a blank line, then a body wrapped at ~72 characters. A tiny checker shows the rules concretely:

```python
def check_commit_message(message: str) -> list[str]:
    problems = []
    lines = message.split("\n")
    subject = lines[0]
    if len(subject) > 72:
        problems.append("subject longer than 72 characters")
    if subject.endswith("."):
        problems.append("subject should not end with a period")
    if subject.split(" ")[0].lower().endswith(("ed", "ing")):
        problems.append("use the imperative mood ('Add', not 'Added' or 'Adding')")
    if len(lines) > 1 and lines[1].strip():
        problems.append("leave a blank line after the subject")
    return problems

print(check_commit_message("Add retry with backoff to the payment client\n\nTimeouts were failing checkouts."))
print(check_commit_message("Fixed stuff and also changed the whole login page and a few other things we noticed.\nmore"))
# []
# ['subject longer than 72 characters', 'subject should not end with a period', "use the imperative mood ('Add', not 'Added' or 'Adding')", 'leave a blank line after the subject']
```

Make commits **small and focused** (one logical change), and write messages for the person who will run `git blame` in two years: that person is often you.

**Pull request descriptions** answer: *What changed? Why? How was it tested? What should the reviewer look at? Is anything risky or incomplete?* Keep PRs small (under about 400 changed lines): large ones get shallow reviews. Add screenshots for UI changes and link the ticket.

**Giving a code review:**

- Review the **design first** (does it solve the right problem in the right place?), then correctness, tests, readability, security and performance, and only last style (a formatter and linter should handle style).
- Be **specific and kind:** ask questions ("What happens if `items` is empty?"), explain *why*, suggest alternatives, separate **must fix** from **nit** (a minor preference).
- Review the code, never the person. Praise good things.
- Respond quickly: slow reviews are the biggest hidden cost in teams.

**Receiving a review:** assume good intent; answer every comment (fix, or explain); do not take it personally; if a thread goes long, talk in person or on a call and write down the outcome.

## 5. Writing a short design document

Before building anything large or risky, write 1 to 3 pages and get feedback while changes are still cheap. A good skeleton:

| Section | What goes in it |
|---------|-----------------|
| **Context and problem** | Why are we doing this? Who is affected? Link data or incidents. |
| **Goals and non-goals** | What success looks like; what is deliberately out of scope. |
| **Proposed design** | The approach, with a diagram: components, data flow, APIs, data model. |
| **Alternatives considered** | At least two, and why they lost. (This is where readers learn you thought about it.) |
| **Risks and failure modes** | What can go wrong, how you will notice, how you will roll back. |
| **Rollout and testing plan** | Phases, feature flags, migration steps, how to verify. |
| **Open questions** | What you still need help deciding. |

The aim is **shared understanding and early disagreement**, not a perfect plan. Use the [system design framework](../09-interview-playbook/system-design-basics/README.md) and [reliability checklist](../09-interview-playbook/system-design-basics/03-caching-failure-modes-and-reliability.md) as prompts.

## 6. Estimating honestly

Estimates are predictions under uncertainty, so give **ranges with assumptions**, not a single number. A classic technique is the **three-point (PERT) estimate**: ask for an *optimistic* (O), *most likely* (M) and *pessimistic* (P) time, then compute `mean = (O + 4M + P) / 6` and `standard deviation = (P - O) / 6`. Adding independent tasks adds the means, and the uncertainties combine as the square root of the sum of squared deviations (so a project's relative uncertainty shrinks as it is split into more tasks).

```python
import math

def pert(optimistic, likely, pessimistic):
    return (optimistic + 4 * likely + pessimistic) / 6, (pessimistic - optimistic) / 6

tasks = {"API endpoint": (2, 3, 8), "Database migration": (1, 2, 10), "Frontend form": (2, 4, 9), "Tests and docs": (1, 2, 4)}
means, sds = zip(*(pert(*t) for t in tasks.values()))
total_mean, total_sd = sum(means), math.sqrt(sum(s * s for s in sds))
print(f"expected {total_mean:.1f} days; about 68% chance of finishing within {total_mean - total_sd:.1f} to {total_mean + total_sd:.1f} days;"
      f" quote about {total_mean + 2 * total_sd:.0f} days for roughly 95% confidence")
# expected 13.5 days; about 68% chance of finishing within 11.3 to 15.7 days; quote about 18 days for roughly 95% confidence
```

Habits that make estimates better: **break work into pieces** of a few days; **include testing, review, deployment and surprises** (the unknowns usually dominate); **say what you assumed**; **track actuals** to calibrate yourself; and re-estimate when you learn something. When pressed for a date, offer **options**: "In 2 weeks, I can ship the core without the admin screen; in 3, with it." Be wary of single-number commitments for work you have not yet understood, and surface slippage **early**.

## 7. Technical debt

**Technical debt** is the future cost of shortcuts taken today. Like financial debt, some is a sensible loan (a quick fix to meet a launch that you schedule to repay) and some is reckless (no tests, no names, nobody understands it). It charges **interest**: every feature in that area takes longer and breaks more often.

- **Make it visible:** keep a short, honest list with the *cost of leaving it* ("every release touching billing needs 2 days of manual checks").
- **Pay it down in small steps alongside feature work** ("boy-scout rule": leave the code a little better than you found it), not in one mythical "refactoring quarter".
- **Prioritise by interest:** fix the debt in the code you change often, ignore the ugly module nobody touches.
- **Do not confuse "I did not write it" or "I would have done it differently" with debt.**

## 8. Incidents and blameless postmortems

When production breaks: **stabilise first** (roll back, switch off the feature, shed load), communicate clearly and often (what we know, what we are doing, next update time), and only then investigate the root cause. Afterwards write a **blameless postmortem**: a timeline; what went well; what went wrong; the **contributing factors** (systems and processes, not "Alex pushed the bad commit": an engineer made a reasonable choice that the system allowed to cause harm); and **concrete follow-up actions** with owners and dates (add a test, add an alert, add a guardrail). Teams learn from incidents only if people feel safe describing them honestly. Measure with [SLOs and error budgets](../11-distributed-systems/observability/01-observability-logs-metrics-traces-slos.md).

## 9. What to learn next

The handbook covers the shared foundation. Here are common directions, with where to go in the handbook and what to practise:

| Direction | Handbook starting points | Build something |
|-----------|--------------------------|-----------------|
| **Backend and APIs** | [FastAPI](../08-modern-python/backend-with-fastapi/01-building-a-web-api-with-fastapi.md), [databases](../05-databases/README.md), [PostgreSQL](../05-databases/postgresql/README.md), [security](../10-security/README.md) | A REST service with auth, a database, tests and a Docker image deployed somewhere |
| **Distributed systems and platform** | [distributed systems](../11-distributed-systems/README.md), [containers](../06-operating-systems/containers/01-containers-and-namespaces.md), [observability](../11-distributed-systems/observability/01-observability-logs-metrics-traces-slos.md) | A replicated key-value store; a service with metrics, tracing and an SLO dashboard |
| **Data and machine learning** | [NumPy and pandas](../08-modern-python/data-with-numpy-pandas/01-numpy-and-pandas-essentials.md), [math for CS](../00-foundations/math-for-cs/README.md), [algorithms](../03-algorithms/README.md) | An analysis of a public dataset with reproducible code; later, scikit-learn then PyTorch |
| **Security** | [security](../10-security/README.md), [TLS lab](../07-networking/tls-security/01-cryptography-and-tls-lab.md) | Capture-the-flag practice, a threat model of a project you own |
| **Systems and performance** | [operating systems](../06-operating-systems/README.md), [CPU caches](../00-foundations/computer-basics/cpu-caches-and-memory-hierarchy.md), [internals](../08-modern-python/internals/01-python-data-model-and-internals.md), a language such as Go or Rust | A tiny database or an HTTP server from sockets |
| **Interview preparation** | [interview playbook](../09-interview-playbook/README.md) | Timed practice problems and mock design interviews |

Whatever you choose: **build projects, read other people's code, write about what you learn,** and ship things that real people use. A deployed project with tests, a README and a clear commit history teaches (and shows) more than any certificate.

## 10. Common mistakes

- Starting to change code before understanding it, or before there are tests.
- Refactoring and changing behaviour in the same commit.
- Giant pull requests and one-line commit messages ("fix stuff").
- Reviews that nitpick formatting but never question the design.
- Silent single-number estimates; hiding slippage until the deadline.
- Letting debt accumulate invisibly, or demanding perfection everywhere.
- Treating postmortems as blame sessions, or never following up on the actions.
- Waiting to ask for help until you have been stuck for days.

## 11. Two real-world examples

**Example 1: The 400-line function.** A new engineer inherited a checkout function with 400 lines of nested conditions, no tests and a "do not touch" comment. Instead of rewriting it, they wrote characterization tests from production examples, then extracted one rule at a time into named functions, running a differential test against the old code on a week of replayed orders. After two weeks of small, reviewed commits the function was 60 lines and the next feature took an afternoon.

**Example 2: The two-page doc.** Before building a new notification system, a team lead wrote a two-page design document and shared it for comment. A reviewer pointed out that the chosen queue could not guarantee ordering per user, which the product needed. Changing the design on paper took an hour; the same discovery after the build would have cost weeks.

## 12. Practice

1. Pick any small open-source package you have installed (find its folder with `package.__file__`) and run `map_package` on it. Which modules does it depend on most? Which file would you open first, and why?
2. Add a rule to `process`: customers with `country == "PK"` get free shipping on orders of 50 or more. Do it as a **separate step** after the refactor: what happens to the differential test, and what should you do with it?
3. Rewrite the bad commit message from section 4 into a good one, and check it with `check_commit_message`.
4. Estimate (with three-point ranges) adding a "forgot password" flow to an existing app. Break it into at least five tasks and compute the total.
5. Write a code-review comment for a function that catches `Exception` and returns `None`: be specific, kind and explain why.
6. Draft the "Alternatives considered" section for replacing a cron job with a message queue.

<details>
<summary>Solutions</summary>

1. For example `map_package(pathlib.Path(requests.__file__).parent)` if `requests` is installed. Open the entry points first (the public API in `__init__.py`), then the module that appears most in `imports.most_common()`: that is the core that other parts rely on.
2. The change alters behaviour, so the differential test now **fails by design** for PK orders between 50 and 100. That is correct: first commit the refactor with a passing test; then in a second commit change the rule, **delete or update the old-version comparison** (the legacy function has served its purpose) and add specific tests for the new rule.
3. ```python
   good = "Simplify login page layout\n\nRemove the unused promo banner and extra spacing so the form fits on\nsmall screens without scrolling."
   print(check_commit_message(good))
   # []
   ```
   (Split "and also changed other things" into separate commits.)
4. Example: form and endpoint (1, 2, 4), token generation and storage (1, 2, 5), email sending with a template (1, 3, 8), rate limiting and abuse protection (1, 2, 5), tests (1, 2, 4), security review and fixes (1, 1, 3). Run the numbers with `pert`; note the email integration has the widest range, so de-risk it first with a quick spike.
5. "Catching `Exception` and returning `None` hides every failure: callers cannot tell 'no result' from 'the database is down', and the real error is lost. Could we catch only the specific exception we expect (`KeyError`?) and let the rest propagate, or at least log the exception with `logger.exception(...)`? Happy to pair on it if useful." (Specific, kind, explains why, offers a way forward.)
6. Alternatives: (a) keep cron but add monitoring and retries: cheap, no new infrastructure, but no per-event retry and jobs run only on a schedule; (b) managed queue service (SQS or similar): little to operate, per-message retries and dead-letter queues, but a vendor dependency and cost; (c) self-hosted broker (RabbitMQ or Kafka): most control and throughput, highest operational cost. Include why (b) won for this team.

</details>

## 13. Check yourself

1. List four steps for getting oriented in an unfamiliar codebase.
2. What is refactoring, and why should it not be mixed with behaviour changes?
3. What is a characterization test, and what is a differential test?
4. What should a good commit message explain?
5. What makes a review comment useful?
6. Which sections belong in a design document?
7. Why give estimates as ranges?

<details>
<summary>Answers</summary>

1. Run it and the tests; find the entry points; trace one real request end to end; read tests and git history; map the modules and dependencies.
2. Changing structure without changing behaviour; mixing them makes it impossible to tell which change caused a problem or to review each safely.
3. A characterization test records what existing code does now so you can refactor safely; a differential test runs old and new implementations on many inputs and compares results.
4. Why the change was made (the reason and context), with a short imperative subject line; the diff shows what.
5. It is specific, explains the reason, suggests a path forward, distinguishes must-fix from nitpicks and targets the code, not the person.
6. Context and problem, goals and non-goals, proposed design, alternatives considered, risks and failure modes, rollout and testing plan, open questions.
7. Because uncertainty is real: a range with stated assumptions communicates risk and avoids false precision and surprise slippage.

</details>

[Back to the career path](README.md)
