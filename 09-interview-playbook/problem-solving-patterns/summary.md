# Problem-Solving Patterns: One-Page Summary

**Method (UMPIRE):** Understand (clarify, edge cases) > Match (pattern) > Plan (brute force, then better; state complexity) > Implement (clean, think aloud) > Review (trace examples, edges) > Evaluate (time, space, trade-offs).

**Constraint -> target:** n<=10 O(n!); <=20 O(2^n); <=100 O(n^3); <=1e3 O(n^2); <=1e5 O(n log n); <=1e6 O(n); huge O(log n).

| Signal in the problem | Pattern | Complexity |
|-----------------------|---------|------------|
| Sorted, pair/triple target | Two pointers | O(n) / O(n^2) |
| Contiguous subarray/substring | Sliding window, prefix sums | O(n) |
| Seen before, counting, grouping | Hash map / set | O(n) |
| Cycle, middle of list | Fast and slow pointers | O(n), O(1) space |
| Sorted / monotonic yes-no | Binary search (on the answer) | O(log n) checks |
| Fewest steps, unweighted | BFS | O(V+E) |
| Explore all / components / trees | DFS | O(V+E) |
| Generate all combos | Backtracking (choose, explore, un-choose) | exponential |
| Optimal / count ways, overlap | Dynamic programming | state count x transition |
| Top-k, k-th, merge k, streams | Heap | O(n log k) |
| Next greater, brackets | (Monotonic) stack | O(n) |
| Overlapping ranges | Sort + sweep | O(n log n) |
| Dynamic connectivity | Union-find | ~O(1) amortized |
| Dependencies / order | Topological sort | O(V+E) |
| Local best is global best | Greedy (prove it) | usually O(n log n) |
| Odd one out, subsets, parity | Bit manipulation | O(n) |

**Pitfalls:** off-by-one at boundaries, copy `path[:]` in backtracking, mark BFS visited on enqueue, recursion limits, unproven greedy, hidden O(n) (`in list`, slicing).

[Lesson](README.md) · [Exercises](exercises.md)
