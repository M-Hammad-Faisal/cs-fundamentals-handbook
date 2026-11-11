# Worked Problems

Full walkthroughs of classic interview problems, written the way a strong candidate thinks aloud: clarify, example, brute force, bottleneck, pattern, code, complexity, tests.

## Detailed lessons

- [Ten worked interview problems](01-ten-worked-interview-problems.md): Two Sum, longest unique substring, merge intervals, valid parentheses, top K frequent, number of islands, course schedule, coin change, LRU cache, rotated-array search. Every solution is randomly tested against a brute-force or independent implementation.
- [Graphs, string DP and design-pattern rounds](02-graph-string-dp-and-design-rounds.md): word ladder (BFS), network delay (Dijkstra), cycle detection, edit distance, longest common subsequence, longest palindromic substring, and Strategy, Observer and State design rounds. Each is tested against an independent slow solution.

## The loop

`clarify -> example -> brute force -> bottleneck -> pattern -> code -> analyze -> test`

See the [problem-solving patterns](../problem-solving-patterns/README.md) for the full pattern catalogue and [system design basics](../system-design-basics/README.md) for the design-round equivalent.

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

## Quick reference

| Question | Answer |
|----------|--------|
| What are the eight steps of the interview loop? | Clarify, example, brute force, bottleneck, pattern, code, analyze, test. |
| Why state the brute force first? | It is a correct baseline, shows you understand the problem, exposes the bottleneck to attack, and gives you a fallback and a tester. |
| Name the pattern for: (a) pair summing to a target, (b) longest substring with a property, (c) overlapping meetings, (d) ordering with dependencies, (e) fewest coins. | (a) hash map, (b) sliding window, (c) sort then sweep (or heap), (d) topological sort, (e) dynamic programming. |
| Why test against a brute force with random inputs? | It finds edge-case bugs automatically and proves your clever solution matches an obviously correct one. |
| What is the signal that a problem wants binary search even though the data is not sorted? | The data (or the answer space) is monotonic (a yes/no property flips once), such as a rotated sorted array or "smallest capacity that works". |

Back to the [interview playbook](../README.md).
