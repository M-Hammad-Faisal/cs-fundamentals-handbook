# Advanced Graph Algorithms: One-Page Summary

## Shortest path chooser
| Situation | Algorithm | Time |
|-----------|-----------|------|
| Unweighted | BFS | `O(V + E)` |
| Non-negative weights | Dijkstra (heap) | `O((V+E) log V)` |
| Negative weights | Bellman-Ford | `O(V·E)` |
| DAG | Topological order + relax | `O(V + E)` |
| All pairs | Floyd-Warshall (`k` outermost) | `O(V³)` |
| Heuristic available | A\* (admissible `h`) | usually far fewer nodes |
| Weights 0/1 | 0-1 BFS (deque) | `O(V + E)` |

## Spanning trees
- **MST** = `V - 1` edges, minimum total weight.
- **Kruskal**: sort edges + Union-Find (`O(E log E)`). **Prim**: heap from a start vertex (`O((V+E) log V)`).

## Connectivity
- **Components**: DFS/BFS or Union-Find.
- **SCC** (directed): Kosaraju (finish order, reverse graph) or Tarjan, `O(V + E)`.
- **Bridges / articulation points**: Tarjan with discovery/low times; show single points of failure.

## Other
- Negative cycle = arbitrage (use `-log(rate)` weights).
- Euler path: all degrees even except ≤ 2. Hamiltonian path: NP-hard.
- Max flow = min cut (Edmonds-Karp, BFS augmenting paths).

## Pitfalls
- Dijkstra with negative edges.
- Non-admissible heuristics in A\*.
- Skipping stale heap entries.
- Recursion limits in big DFS-based algorithms.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Shortest Paths Beyond Dijkstra](01-all-pairs-and-heuristic-shortest-paths.md) · [Connectivity, Strongly Connected Components, Bridges and Max Flow](02-connectivity-scc-and-flow.md)
