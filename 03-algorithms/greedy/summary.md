# Greedy Algorithms: One-Page Summary

## Idea
Take the locally best choice at each step, never reconsider. Fast (often `O(n log n)` from a sort) but correct only when:
1. **Greedy-choice property**: a local best extends to a global best.
2. **Optimal substructure.**

## Proving it
- **Exchange argument**: swap the greedy choice into any optimal solution without loss.
- **Greedy stays ahead**: greedy is never behind at any step.
- Otherwise test against brute force and adversarial cases.

## Greedy vs DP
Greedy commits to one choice. DP tries all choices per state. If you cannot justify the local choice, use DP.

## Classics
| Problem | Greedy rule |
|---------|-------------|
| Activity selection | Earliest **end** time first |
| Jump game | Track the farthest reach |
| Gas station | Reset start when the tank goes negative |
| Fractional knapsack | Highest value/weight ratio |
| Huffman coding | Merge the two least frequent (min-heap) |
| Shortest job first | Sort by duration |
| Dijkstra / Prim / Kruskal | Closest vertex / cheapest valid edge |

## Counterexamples to remember
- General coin change (`{1,3,4}`, amount 6) and 0/1 knapsack need DP.

## Tips
Sort by the right key · define tie-breaks · use a heap for dynamic candidates · verify with a brute force.

[Lesson](README.md) · [Exercises](exercises.md)
