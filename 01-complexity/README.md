# Complexity Analysis

How do you know whether a program will finish in a second or in a century? This part teaches you to **measure and predict** the cost of algorithms: first by counting steps, then with Big-O notation, then by analyzing real code (loops and recursion), memory use, best/average/worst/amortized cases, the cost of Python's built-ins and the limits of the theory.

## Learning path

| # | Lesson | You will learn |
|---|--------|----------------|
| 1 | [What is an algorithm?](01-what-is-an-algorithm.md) | Algorithms, their properties, tracing, correctness, why efficiency matters |
| 2 | [Counting steps and growth](02-counting-steps-and-growth.md) | The step model, instrumented counters, growth curves, the doubling test |
| 3 | [Big-O, Omega and Theta](03-big-o-omega-theta.md) | Formal definition, simplification rules, common classes, checking claims numerically |
| 4 | [Analyzing loops and recursion](04-analyzing-loops-and-recursion.md) | Twenty worked examples, recurrences, recursion trees, a pattern cheat sheet |
| 5 | [Space complexity](05-space-complexity.md) | Auxiliary space, call-stack cost, in-place algorithms, time-space trade-offs |
| 6 | [Best, average, worst and amortized](06-cases-and-amortized-analysis.md) | Cases, quicksort pivots, dynamic-array amortization, two-stack queue |
| 7 | [Complexity of Python operations](07-python-operations-cheat-sheet.md) | list, dict, set, str, deque, heapq, bisect costs with measured proofs and hidden-cost traps |
| 8 | [Beyond Big-O](08-beyond-big-o.md) | Constants, caches, I/O, choosing algorithms, P vs NP, heuristics |
| ref | [Big-O quick reference (lesson, exercises, summary)](big-o/README.md) | A compact one-file recap with exercises |

**Before you start:** [exponents and logarithms](../00-foundations/math-for-cs/exponents-and-logarithms.md) and [sums and recurrences](../00-foundations/math-for-cs/sums-and-recurrences.md) make this part much easier.

**Where you will use it:** every lesson in [data structures](../02-data-structures/arrays-strings/README.md) and [algorithms](../03-algorithms/README.md) states complexities, and the [interview playbook](../09-interview-playbook/problem-solving-patterns/README.md) asks for them.

[Back to the index](../INDEX.md)
