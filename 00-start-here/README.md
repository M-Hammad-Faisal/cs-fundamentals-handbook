# Start Here: How to Use This Handbook

Welcome. This handbook teaches the core of computer science and professional Python programming, from "what is a bit?" to "design a system that serves a million users". It is written so a **second-year student can learn from it on their own**: every idea gets a plain-English explanation, an analogy, a worked example you can run, common mistakes, practice problems with solutions and a self-check quiz.

## 1. What is inside

| Part | Topic | What you get |
|------|-------|--------------|
| [00 Foundations](../00-foundations/README.md) | Setup, computer basics, math, Python fundamentals, command line and Git | The prerequisites, explained from scratch |
| [00 Career path](../00-career-path/README.md) | What the profession looks like | Roles, skills, a plan |
| [01 Complexity](../01-complexity/big-o/README.md) | Measuring how fast and how big | Big-O |
| [02 Data structures](../02-data-structures/arrays-strings/README.md) | Arrays to graphs | Storing and organizing data |
| [03 Algorithms](../03-algorithms/README.md) | Sorting, searching, recursion, DP, greedy, graphs | Solving problems efficiently |
| [04 Object-oriented design](../04-oop/README.md) | Classes, SOLID, 25 design patterns | Structuring larger programs |
| [05 Databases](../05-databases/README.md) | SQL, indexes, transactions, schema design, NoSQL | Storing data reliably |
| [06 Operating systems](../06-operating-systems/README.md) | Processes, scheduling, memory, concurrency, files | What runs under your code |
| [07 Networking](../07-networking/README.md) | TCP/IP, DNS, HTTP, TLS, load balancing | How computers talk |
| [08 Modern Python](../08-modern-python/README.md) | Typing, async, testing, packaging | Professional Python |
| [09 Interview playbook](../09-interview-playbook/README.md) | Patterns, system design, behavioral | Turning knowledge into offers |

Also: the [glossary](../GLOSSARY.md) (every term in plain words), the [index](../INDEX.md) (status of every lesson), the [revision schedule](../revision/schedule.md) and the [progress tracker](../revision/PROGRESS.md).

## 2. How every lesson is built

Each topic file follows the same pattern so you always know where to look:

1. **Prerequisites and what you will learn.**
2. **In plain words**: the idea and an everyday analogy.
3. **How it works**: step-by-step explanation, usually with a small trace or diagram.
4. **Code**: complete examples that run, with checked output in comments.
5. **Complexity, trade-offs, when to use it (and when not to).**
6. **Two real-world examples** (where this appears in actual software).
7. **Common mistakes.**
8. **Practice** with collapsible solutions, then **Check yourself** with collapsible answers.

## 3. How to study (this matters more than what you study)

1. **Type the code.** Do not copy-paste. Change a value, predict the output, run it. Break it on purpose and read the error.
2. **Predict before you run.** Write down what you think will print; mismatches are where learning happens.
3. **Do the practice before the solutions.** Struggle for 10-15 minutes; look at hints only after.
4. **Explain it out loud** (to a friend, a rubber duck or an empty room). If you cannot explain it simply, you do not understand it yet.
5. **Space your revision.** Revisit a topic after 1 day, 3 days, 1 week, 3 weeks ([schedule](../revision/schedule.md)). Short and repeated beats long and once.
6. **Build something.** After each part, make a small project that uses it (a to-do app with a database, a tiny HTTP client, a text-adventure with classes).
7. **Keep an error log.** Write down each mistake and its fix in the [progress tracker](../revision/PROGRESS.md).
8. **Use version control from day one** ([Git lessons](../00-foundations/command-line-and-git/README.md)).
9. **Pace yourself.** Two focused hours daily beat an exhausting weekend. Sleep and breaks are part of learning.

## 4. Check what you already know

Answer these without looking anything up. Where you hesitate, read the linked lesson.

1. What does this print? `x = [1, 2]; y = x; y.append(3); print(x)` ([references](../00-foundations/computer-basics/memory-stack-heap.md))
2. Write a function that returns the largest number in a list without using `max`. ([functions](../00-foundations/python-fundamentals/03-functions.md))
3. What is 45 in binary? ([binary](../00-foundations/computer-basics/binary-and-data-representation.md))
4. What is the difference between `git add` and `git commit`? ([Git](../00-foundations/command-line-and-git/git-basics.md))
5. If a loop halves its input each time, roughly how many steps for one million items? ([logarithms](../00-foundations/math-for-cs/exponents-and-logarithms.md))
6. What is the difference between a list and a dictionary? ([collections](../00-foundations/python-fundamentals/04-strings-lists-dicts-sets.md))
7. What does `try/except` do? ([errors](../00-foundations/python-fundamentals/05-files-modules-errors.md))

<details>
<summary>Answers</summary>

1. `[1, 2, 3]` (both names refer to the same list).
2. `best = nums[0]; for n in nums[1:]: if n > best: best = n; return best`.
3. `101101`.
4. `add` stages changes; `commit` records the staged snapshot in history.
5. About 20 (`log2(1,000,000)`).
6. A list is an ordered sequence accessed by position; a dictionary maps keys to values and is accessed by key.
7. It handles errors without crashing the program: code in `try` runs, and `except` handles a specific failure.

</details>

## 5. Choose your path

### Path A: "I am new to programming" (about 4-5 months at 8 hours/week)

1. [Setup](../00-foundations/setup/README.md) and [Python fundamentals](../00-foundations/python-fundamentals/README.md).
2. [Computer basics](../00-foundations/computer-basics/README.md), [command line and Git](../00-foundations/command-line-and-git/README.md).
3. [Math for CS](../00-foundations/math-for-cs/README.md), then [complexity](../01-complexity/big-o/README.md).
4. [Data structures](../02-data-structures/arrays-strings/README.md) and [algorithms](../03-algorithms/README.md) (the core: spend the longest here).
5. [OOP](../04-oop/README.md), then [databases](../05-databases/README.md).
6. [Operating systems](../06-operating-systems/README.md), [networking](../07-networking/README.md), [modern Python](../08-modern-python/README.md).
7. [Interview playbook](../09-interview-playbook/README.md).

### Path B: "I know Python; I want the CS core" (about 3 months)

[Computer basics](../00-foundations/computer-basics/README.md) and [math for CS](../00-foundations/math-for-cs/README.md) (skim), then parts 01-03 in order, then 05, 06, 07, 04, 08.

### Path C: "Interview in 4-8 weeks"

1. Skim [complexity](../01-complexity/big-o/README.md) and the "Check yourself" sections of [data structures](../02-data-structures/arrays-strings/README.md) and [algorithms](../03-algorithms/README.md).
2. Work through the [problem-solving patterns](../09-interview-playbook/problem-solving-patterns/README.md) with a timer.
3. [System design basics](../09-interview-playbook/system-design-basics/README.md) twice per week.
4. [Rapid-fire questions](../09-interview-playbook/python-and-cs-rapid-fire/README.md) daily; [behavioral](../09-interview-playbook/behavioral-and-process/README.md) stories; mock interviews.
5. Follow the [12-week plan](../09-interview-playbook/behavioral-and-process/README.md) compressed to your timeline.

### Path D: "A course topic is giving me trouble"

Use the [glossary](../GLOSSARY.md) and the [index](../INDEX.md) to jump to the one topic, read its **In plain words** section first, then run the code and do the practice.

## 6. When you get stuck

1. Read the error message from the bottom up ([debugging](../00-foundations/python-fundamentals/06-debugging-and-testing.md)).
2. Shrink the problem to the smallest example that fails.
3. Print or step through (a [debugger](../00-foundations/python-fundamentals/06-debugging-and-testing.md)).
4. Search the exact error text; read the official documentation (docs.python.org).
5. Explain it to someone (or write the question out): you often find the answer while asking.
6. If you still cannot solve it after 30-45 focused minutes, ask for help with a minimal reproducible example: what you expected, what happened, what you tried.

## 7. What "done" looks like

You can **explain each concept in your own words**, **write the code from memory**, **recognize when to use it**, and **say its trade-offs**. When that is true for a topic, tick it in the [progress tracker](../revision/PROGRESS.md).

Start with the [foundations](../00-foundations/README.md), or jump straight to a topic through the [index](../INDEX.md).
