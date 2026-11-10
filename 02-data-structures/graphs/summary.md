# Graphs: One-Page Summary

## Facts
- Vertices + edges. Directed/undirected, weighted/unweighted, cyclic/acyclic (DAG).
- **Adjacency list** `O(V + E)` (default, sparse); **matrix** `O(V²)` (dense, `O(1)` edge check).

## Traversal
| | BFS | DFS |
|---|-----|-----|
| Structure | Queue | Stack / recursion |
| Finds | Shortest path (unweighted) | Cycles, components, topological order |
| Time / space | `O(V + E)` / `O(V)` | `O(V + E)` / `O(V)` |

## Algorithms
| Problem | Algorithm | Time |
|---------|-----------|------|
| Shortest path, non-negative weights | Dijkstra (heap) | `O((V+E) log V)` |
| Negative weights, cycle detection | Bellman-Ford | `O(V·E)` |
| All pairs | Floyd-Warshall | `O(V³)` |
| Dependency ordering | Topological sort (Kahn/DFS) | `O(V + E)` |
| Connectivity, Kruskal | Union-Find | ~`O(α(n))` per op |
| Minimum spanning tree | Kruskal / Prim | `O(E log E)` |

## Patterns
- Grids are graphs (4 or 8 neighbours).
- Multi-source BFS (rotting oranges).
- Mark visited on enqueue.
- Loop over all vertices for disconnected graphs.
- Directed cycle detection uses three colors; undirected uses the parent check.
- Model state as the vertex when needed.

## Pitfalls
- Dijkstra with negative edges.
- Recursive DFS depth limits.
- Forgetting disconnected components.
- Re-queueing nodes because visited was marked too late.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Graph Basics](01-graph-basics-bfs-dfs.md) · [Graph Algorithms](02-graph-algorithms.md) · [Union-Find](03-union-find.md)
