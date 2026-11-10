# Part 03: Algorithms

An **algorithm** is a precise recipe for solving a problem. This part teaches the families of algorithms that cover most of what you will meet in interviews and real software, each with step-by-step traces, runnable Python (checked against brute force where possible), practice problems and self-checks.

**Prerequisites:** [Part 01 complexity](../01-complexity/README.md) (Big-O) and [Part 02 data structures](../02-data-structures/README.md). Many algorithms here are built from those structures (heaps for Dijkstra, stacks for DFS, hash maps for counting).

## Reading order

| # | Topic | Detailed lessons | The big idea |
|---|-------|------------------|--------------|
| 1 | [Sorting](sorting/README.md) | [elementary](sorting/01-sorting-basics-and-elementary-sorts.md), [merge and quick](sorting/02-merge-sort-and-quicksort.md), [linear-time and Timsort](sorting/03-linear-time-sorts-and-timsort.md) | put things in order; `n log n` is the comparison limit |
| 2 | [Searching](searching/README.md) | [binary search](searching/01-linear-and-binary-search.md), [on the answer](searching/02-binary-search-on-the-answer.md) | halve the possibilities each step |
| 3 | [Recursion and backtracking](recursion-backtracking/README.md) | [recursion](recursion-backtracking/01-recursion-fundamentals.md), [backtracking](recursion-backtracking/02-backtracking.md) | solve a smaller copy; try, undo, try again |
| 4 | [Greedy](greedy/README.md) | [greedy algorithms](greedy/01-greedy-algorithms.md) | take the best-looking choice and never look back |
| 4b | [Divide and conquer](divide-and-conquer/README.md) | [divide and conquer](divide-and-conquer/01-divide-and-conquer.md) | independent subproblems, the Master theorem |
| 5 | [Dynamic programming](dynamic-programming/README.md) | [1D](dynamic-programming/01-dp-thinking-and-1d-problems.md), [two sequences and grids](dynamic-programming/02-dp-on-two-sequences-and-grids.md), [advanced](dynamic-programming/03-advanced-dp-patterns.md) | remember subproblem answers |
| 6 | [Number theory](number-theory/README.md) | [number theory for programmers](number-theory/01-number-theory-for-programmers.md) | divisibility, remainders, primes |
| 7 | [String algorithms](string-algorithms/README.md) | [matching, palindromes and suffix arrays](string-algorithms/01-string-matching-and-suffix-structures.md) | search and index text in near-linear time |
| 8 | [Graph algorithms](graph-algorithms/README.md) | [all-pairs and A*](graph-algorithms/01-all-pairs-and-heuristic-shortest-paths.md), [connectivity and flow](graph-algorithms/02-connectivity-scc-and-flow.md) (plus the [graph lessons in Part 02](../02-data-structures/graphs/README.md)) | model relationships as vertices and edges |

Each folder also has a quick-reference README, `exercises.md` and a one-page `summary.md`.

## Which technique fits my problem?

| The problem says... | Try |
|---------------------|-----|
| "sort", "order", "k-th", "top k" | sorting, heap, quickselect |
| "sorted array", "minimum x such that...", "maximum min distance" | binary search (on the array or on the answer) |
| "all combinations/permutations/subsets", "place so that no conflict" | backtracking |
| "maximum number of non-overlapping...", "schedule", "cover" and a provable local rule | greedy |
| "number of ways", "minimum cost", "longest", overlapping subproblems | dynamic programming |
| "shortest path", "connected", "dependencies", "network" | graph algorithms |
| a problem splits into independent halves; "recurrence", "Master theorem" | [divide and conquer](divide-and-conquer/README.md) |
| "modulo 10^9+7", gcd, primes, remainders | [number theory](number-theory/README.md) |
| Find a pattern or palindrome in text, index a text | [string algorithms](string-algorithms/README.md) |
| It is a tree or nested structure | recursion |

**When stuck:** (1) write the brute force, (2) find the repeated work or the wasted comparisons, (3) pick the technique that removes them.

## A study routine

1. Read a lesson and **run every example**; predict the output first.
2. Close the page and **re-implement the algorithm from memory**.
3. Do the practice problems; only then open the solutions.
4. Test your implementation against a **brute force** on random small inputs (the lessons show how).
5. Revisit the "Check yourself" questions after a day.

Next: [Part 04: Object-oriented programming](../04-oop/README.md)

Back to the [index](../INDEX.md).
