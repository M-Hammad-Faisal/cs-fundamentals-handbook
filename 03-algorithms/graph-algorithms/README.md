# Advanced Graph Algorithms

## Detailed lessons (start here if you are new)

Start with the [graphs lessons in Part 02](../../02-data-structures/graphs/README.md) (BFS/DFS, Dijkstra, topological sort, MST, union-find), then:

1. [All-pairs and heuristic shortest paths](01-all-pairs-and-heuristic-shortest-paths.md): Floyd-Warshall, A*, 0-1 BFS
2. [Connectivity, SCC and flow](02-connectivity-scc-and-flow.md): Kosaraju, bridges, Euler paths, max flow, matching

The rest of this page is the quick reference.

This chapter builds on [graphs](../../02-data-structures/graphs/README.md), which covers representations, BFS, DFS, cycle detection, topological sort, basic Dijkstra and Union-Find. Here we add the algorithms you meet next: shortest paths with negative weights, all-pairs paths, minimum spanning trees, A\*, connectivity analysis, and a few classic problems.

## 1. Choosing a shortest-path algorithm

| Situation | Algorithm | Time |
|-----------|-----------|------|
| Unweighted | BFS | `O(V + E)` |
| Non-negative weights | Dijkstra (heap) | `O((V + E) log V)` |
| Negative weights, no negative cycles | Bellman-Ford | `O(V · E)` |
| DAG | Topological order + relax | `O(V + E)` |
| All pairs, small `V` | Floyd-Warshall | `O(V³)` |
| Single target with a good heuristic | A\* | Often far less than Dijkstra |
| Weights only 0 or 1 | 0-1 BFS (deque) | `O(V + E)` |

## 2. Bellman-Ford

Relax every edge `V - 1` times. A path has at most `V - 1` edges, so after that all shortest paths are final. A further improvement on pass `V` reveals a **negative cycle**.

```python
def bellman_ford(n, edges, source):               # edges: (u, v, w)
    dist = [float("inf")] * n
    dist[source] = 0
    for _ in range(n - 1):
        changed = False
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                changed = True
        if not changed:
            break
    for u, v, w in edges:                         # negative cycle check
        if dist[u] + w < dist[v]:
            return None
    return dist
```

## 3. Floyd-Warshall (all pairs)

Try every vertex `k` as an intermediate stop.

```python
def floyd_warshall(n, edges):
    INF = float("inf")
    d = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    for u, v, w in edges:
        d[u][v] = min(d[u][v], w)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if d[i][k] + d[k][j] < d[i][j]:
                    d[i][j] = d[i][k] + d[k][j]
    return d                                      # O(V^3)
```

## 4. A\* search

Dijkstra expands in order of distance from the start. **A\*** orders by `g + h`, where `g` is the cost so far and `h` is a **heuristic** estimate of the remaining cost. If `h` never overestimates (it is *admissible*), A\* is optimal and typically explores far fewer nodes.

```python
import heapq

def astar(grid, start, goal):                     # 0 = free, 1 = wall
    def h(p):                                     # Manhattan distance heuristic
        return abs(p[0] - goal[0]) + abs(p[1] - goal[1])

    heap = [(h(start), 0, start)]
    best = {start: 0}
    while heap:
        _, g, cur = heapq.heappop(heap)
        if cur == goal:
            return g
        if g > best[cur]:
            continue
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = cur[0] + dr, cur[1] + dc
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] == 0:
                ng = g + 1
                if ng < best.get((nr, nc), float("inf")):
                    best[(nr, nc)] = ng
                    heapq.heappush(heap, (ng + h((nr, nc)), ng, (nr, nc)))
    return -1
```

Game pathfinding, robotics and map routing use A\*.

## 5. Minimum spanning tree (MST)

A **spanning tree** connects all vertices with `V - 1` edges and no cycles. The **minimum** one has the smallest total weight.

### Kruskal (sort edges, use Union-Find)

```python
def kruskal(n, edges):                            # edges: (w, u, v)
    parent = list(range(n))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    total, used = 0, []
    for w, u, v in sorted(edges):
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv
            total += w
            used.append((u, v, w))
    return total, used                            # O(E log E)
```

### Prim (grow from a vertex with a heap)

```python
import heapq

def prim(graph, start):                           # graph[u] = [(v, w), ...]
    seen, heap, total = set(), [(0, start)], 0
    while heap and len(seen) < len(graph):
        w, u = heapq.heappop(heap)
        if u in seen:
            continue
        seen.add(u)
        total += w
        for v, wv in graph[u]:
            if v not in seen:
                heapq.heappush(heap, (wv, v))
    return total                                  # O((V + E) log V)
```

Kruskal suits sparse graphs and edge lists; Prim suits dense graphs.

## 6. Connectivity analysis

### Connected components (undirected)

Run DFS/BFS from each unvisited vertex, or use Union-Find. Count how many times you start a new search.

### Strongly connected components (SCC) in a directed graph

A **strongly connected component** is a maximal set where every vertex reaches every other. **Kosaraju's algorithm:**

1. DFS the graph, recording vertices by finish time.
2. Reverse all edges.
3. DFS the reversed graph in decreasing finish time; each tree is one SCC.

```python
from collections import defaultdict

def kosaraju(n, edges):
    graph, rgraph = defaultdict(list), defaultdict(list)
    for u, v in edges:
        graph[u].append(v)
        rgraph[v].append(u)

    seen, order = set(), []
    def dfs1(u):
        seen.add(u)
        for v in graph[u]:
            if v not in seen:
                dfs1(v)
        order.append(u)
    for u in range(n):
        if u not in seen:
            dfs1(u)

    comp, seen = [], set()
    def dfs2(u, bucket):
        seen.add(u)
        bucket.append(u)
        for v in rgraph[u]:
            if v not in seen:
                dfs2(v, bucket)
    for u in reversed(order):
        if u not in seen:
            bucket = []
            dfs2(u, bucket)
            comp.append(bucket)
    return comp                                   # O(V + E)
```

### Bridges and articulation points

A **bridge** is an edge whose removal disconnects the graph; an **articulation point** is a vertex with that property. They reveal single points of failure. Tarjan's algorithm finds them in `O(V + E)` using DFS discovery times and "lowest reachable" values.

## 7. More patterns

### 0-1 BFS

When edge weights are only 0 or 1, use a deque: push 0-weight neighbours to the **front** and 1-weight to the **back**. `O(V + E)`, simpler than Dijkstra.

### Bipartite check

Two-color the graph with BFS/DFS; a conflict means it is not bipartite (it contains an odd cycle).

### Euler paths and Hamiltonian paths

- **Euler path** (visits every *edge* once): exists when all vertices have even degree except at most two. Solvable in `O(E)` (Hierholzer).
- **Hamiltonian path** (visits every *vertex* once) is NP-hard.

### Maximum flow (overview)

Given capacities on edges, find the most flow from source to sink. **Ford-Fulkerson / Edmonds-Karp** repeatedly find augmenting paths with BFS. By the **max-flow min-cut theorem**, max flow equals the capacity of the smallest cut. Used for network capacity, bipartite matching, and image segmentation.

## 8. Two real-world examples

### Example 1: Currency arbitrage and network routing

Model currencies as vertices and exchange rates as edge weights `-log(rate)`. A **negative cycle** (found with Bellman-Ford) means you can convert around a loop and end up with more money than you started with: arbitrage. Distance-vector routing protocols such as RIP are distributed Bellman-Ford. Link-state protocols like OSPF run Dijkstra on each router.

### Example 2: Infrastructure design and failure analysis

Laying cable, fibre or pipes to connect every site at minimal cost is an **MST** problem (Kruskal/Prim). **Bridges and articulation points** identify single points of failure in a network, so engineers know which link or server must be made redundant. **SCC** analysis finds clusters of mutually dependent services or mutually linking web pages (used in compilers, package dependency analysis, and the first stages of PageRank-style processing). **Max flow** schedules bandwidth and matches workers to jobs.

## 9. Tips, tricks and pitfalls

- **Pick the algorithm from the constraints:** weights (negative? uniform?), one source or all pairs, graph density, and size of `V`.
- **Dijkstra breaks on negative edges;** Bellman-Ford does not (but is slower).
- **Floyd-Warshall's loop order is `k, i, j`;** `k` must be the outermost loop.
- **A\* needs an admissible heuristic** (never overestimates), or the result may be suboptimal.
- **Stale heap entries:** skip popped entries whose distance is worse than the best known.
- **Disconnected graphs:** an MST becomes a minimum spanning *forest*; handle by looping over components.
- **Recursion depth** in SCC/bridge DFS can exceed Python's limit on big graphs; use iterative versions.
- **Model the problem as a graph first** (states as vertices, moves as edges); many puzzles reduce to BFS or shortest paths.

## 10. Check yourself

1. Why does Bellman-Ford run `V - 1` rounds, and how does it detect a negative cycle?
2. When would you choose Floyd-Warshall over running Dijkstra from every vertex?
3. What makes a heuristic admissible, and why does A\* need that?
4. How do Kruskal's and Prim's algorithms differ?
5. What is a strongly connected component?
6. What is a bridge, and why do engineers care?
7. When can 0-1 BFS replace Dijkstra?

<details>
<summary>Answers</summary>

1. A shortest path has at most `V - 1` edges, so `V - 1` rounds of relaxing all edges finalize distances. If an edge can still be relaxed afterwards, a negative cycle exists.
2. When the graph is small or dense and you need all-pairs distances (or have negative edges without negative cycles): it is simple, `O(V³)`.
3. It never overestimates the true remaining cost. A\* then never discards the optimal path, so the first time it reaches the goal the path is optimal.
4. Kruskal sorts all edges and adds the cheapest that does not form a cycle (Union-Find). Prim grows one tree outward, always adding the cheapest edge leaving it (heap).
5. A maximal set of vertices in a directed graph where each vertex can reach every other.
6. A bridge is an edge whose removal disconnects the graph. It marks a single point of failure that should be made redundant.
7. When every edge weight is 0 or 1: put 0-weight neighbours at the deque front and 1-weight at the back.

</details>
