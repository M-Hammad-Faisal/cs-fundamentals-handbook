# Worked Problems: One-Page Summary

## Questions worth remembering

- **What are the eight steps of the interview loop?** Clarify, example, brute force, bottleneck, pattern, code, analyze, test.
- **Why state the brute force first?** It is a correct baseline, shows you understand the problem, exposes the bottleneck to attack, and gives you a fallback and a tester.
- **Name the pattern for: (a) pair summing to a target, (b) longest substring with a property, (c) overlapping meetings, (d) ordering with dependencies, (e) fewest coins.** (a) hash map, (b) sliding window, (c) sort then sweep (or heap), (d) topological sort, (e) dynamic programming.
- **Why test against a brute force with random inputs?** It finds edge-case bugs automatically and proves your clever solution matches an obviously correct one.
- **What is the signal that a problem wants binary search even though the data is not sorted?** The data (or the answer space) is monotonic (a yes/no property flips once), such as a rotated sorted array or "smallest capacity that works".
- **What do interviewers listen for besides a correct answer?** Clear communication, structured reasoning, handling of edge cases, complexity analysis, testing habits and how you respond to hints.
- **Why is BFS correct for shortest paths in an unweighted graph, and what replaces it for weighted graphs?** BFS visits nodes in increasing number of edges from the start, so the first time it reaches a node is by a shortest path; weighted graphs use Dijkstra (non-negative) or Bellman-Ford (any weights).
- **What is the key invariant of Dijkstra's algorithm, and which input breaks it?** When a node is popped from the heap its distance is final, because all remaining paths are at least as long; negative edges break this.
- **How does DFS detect a cycle in a directed graph?** A cycle exists if the DFS meets a node that is still on the current path (an "in progress" node).
- **State the edit-distance recurrence and its base cases.** Equal last characters: `dp[i-1][j-1]`; otherwise `1 + min(delete, insert, substitute)`; `dp[i][0] = i`, `dp[0][j] = j`.
- **What is the relationship between LCS and edit distance?** With only insertions and deletions the distance is `n + m - 2 * LCS`.
- **Why expanding around centers for palindromes, and what is the complexity?** Every palindrome has a center (2n-1 choices); expanding is `O(n)` per center, `O(n^2)` total, with constant space.

Practice problems with solutions are in the **Practice** section of each lesson.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Ten Worked Interview Problems](01-ten-worked-interview-problems.md) · [Worked Problems, Part 2](02-graph-string-dp-and-design-rounds.md)
