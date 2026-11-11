# Part 03: Algorithms

An **algorithm** is a precise recipe for solving a problem. This part teaches the families of algorithms that cover most of what you will meet in interviews and real software, each with step-by-step traces, runnable Python (checked against brute force where possible), practice problems and self-checks.

**Prerequisites:** [Part 01 complexity](../01-complexity/README.md) (Big-O) and [Part 02 data structures](../02-data-structures/README.md). Many algorithms here are built from those structures (heaps for Dijkstra, stacks for DFS, hash maps for counting).

## Topics in this part

Read the topics in this order. Each has an overview, detailed lessons, exercises with solutions and a one-page summary (the full map is in the [index](../INDEX.md)).

<!-- topics:start -->
| Topic | Lessons | Exercises | Summary |
|-------|---------|-----------|---------|
| Sorting | [overview](sorting/README.md)<br>[Sorting Basics and the Elementary Sorts](sorting/01-sorting-basics-and-elementary-sorts.md)<br>[Merge Sort and Quicksort](sorting/02-merge-sort-and-quicksort.md)<br>[Linear-Time Sorts, Timsort and Choosing a Sort](sorting/03-linear-time-sorts-and-timsort.md) | [ex](sorting/exercises.md) | [sum](sorting/summary.md) |
| Searching | [overview](searching/README.md)<br>[Linear Search and Binary Search](searching/01-linear-and-binary-search.md)<br>[Binary Search on the Answer and Other Search Techniques](searching/02-binary-search-on-the-answer.md) | [ex](searching/exercises.md) | [sum](searching/summary.md) |
| Recursion and Backtracking | [overview](recursion-backtracking/README.md)<br>[Recursion Fundamentals](recursion-backtracking/01-recursion-fundamentals.md)<br>[Backtracking](recursion-backtracking/02-backtracking.md) | [ex](recursion-backtracking/exercises.md) | [sum](recursion-backtracking/summary.md) |
| Divide and Conquer | [overview](divide-and-conquer/README.md)<br>[Divide and Conquer](divide-and-conquer/01-divide-and-conquer.md) | [ex](divide-and-conquer/exercises.md) | [sum](divide-and-conquer/summary.md) |
| Dynamic Programming | [overview](dynamic-programming/README.md)<br>[Dynamic Programming](dynamic-programming/01-dp-thinking-and-1d-problems.md)<br>[DP on Two Sequences, Grids and Knapsack](dynamic-programming/02-dp-on-two-sequences-and-grids.md)<br>[Advanced DP Patterns](dynamic-programming/03-advanced-dp-patterns.md) | [ex](dynamic-programming/exercises.md) | [sum](dynamic-programming/summary.md) |
| Greedy Algorithms | [overview](greedy/README.md)<br>[Greedy Algorithms](greedy/01-greedy-algorithms.md) | [ex](greedy/exercises.md) | [sum](greedy/summary.md) |
| Number Theory | [overview](number-theory/README.md)<br>[Number Theory for Programmers](number-theory/01-number-theory-for-programmers.md) | [ex](number-theory/exercises.md) | [sum](number-theory/summary.md) |
| String Algorithms | [overview](string-algorithms/README.md)<br>[String Algorithms](string-algorithms/01-string-matching-and-suffix-structures.md) | [ex](string-algorithms/exercises.md) | [sum](string-algorithms/summary.md) |
| Advanced Graph Algorithms | [overview](graph-algorithms/README.md)<br>[Shortest Paths Beyond Dijkstra](graph-algorithms/01-all-pairs-and-heuristic-shortest-paths.md)<br>[Connectivity, Strongly Connected Components, Bridges and Max Flow](graph-algorithms/02-connectivity-scc-and-flow.md) | [ex](graph-algorithms/exercises.md) | [sum](graph-algorithms/summary.md) |
<!-- topics:end -->

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

Back to the [handbook home](../README.md) · [index](../INDEX.md).
