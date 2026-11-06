# Graphs

## 1. The concept

A **graph** is a set of **vertices** (nodes) connected by **edges**. It models anything made of things and relationships: cities and roads, people and friendships, web pages and links, tasks and dependencies.

Trees are a special case: connected graphs with no cycles.

### Vocabulary

| Term | Meaning |
|------|---------|
| **Directed** | Edges have a direction (`A -> B`); Twitter follows |
| **Undirected** | Edges go both ways; Facebook friendships |
| **Weighted** | Edges carry a cost (distance, time, price) |
| **Path** | A sequence of vertices connected by edges |
| **Cycle** | A path that starts and ends at the same vertex |
| **Connected** | Every vertex reachable from every other (undirected) |
| **DAG** | Directed acyclic graph; models dependencies |
| **Degree** | Number of edges at a vertex (in-degree/out-degree if directed) |
| **Sparse / dense** | Few edges (`E ≈ V`) vs many (`E ≈ V²`) |

## 2. Representations

### Adjacency list (the default)

Each vertex stores a list of neighbours. Space `O(V + E)`.

```python
from collections import defaultdict

graph = defaultdict(list)
def add_edge(u, v, directed=False):
    graph[u].append(v)
    if not directed:
        graph[v].append(u)

add_edge("A", "B"); add_edge("A", "C"); add_edge("B", "D")
# {'A': ['B', 'C'], 'B': ['A', 'D'], 'C': ['A'], 'D': ['B']}
```

Weighted: store `(neighbor, weight)` pairs.

### Adjacency matrix

A `V x V` table where `matrix[u][v]` marks (or weights) an edge. Space `O(V²)`.

| | A | B | C |
|---|---|---|---|
| A | 0 | 1 | 1 |
| B | 1 | 0 | 0 |
| C | 1 | 0 | 0 |

### Edge list

A flat list of `(u, v, w)` tuples. Handy for algorithms that sort edges (Kruskal).

### Which to choose

| Operation | Adjacency list | Adjacency matrix |
|-----------|----------------|------------------|
| Space | `O(V + E)` | `O(V²)` |
| Is there an edge `u-v`? | `O(degree)` | `O(1)` |
| List neighbours of `u` | `O(degree)` | `O(V)` |
| Best for | Sparse graphs (most real graphs) | Dense graphs, quick edge checks |

## 3. Traversal

### Breadth-first search (BFS)

Explores level by level using a **queue**. In an unweighted graph it finds the **shortest path** (fewest edges).

```python
from collections import deque

def bfs(graph, start):
    seen, order = {start}, []
    q = deque([start])
    while q:
        u = q.popleft()
        order.append(u)
        for v in graph[u]:
            if v not in seen:
                seen.add(v)          # mark when enqueued, not when dequeued
                q.append(v)
    return order

def shortest_path(graph, start, goal):
    prev, q = {start: None}, deque([start])
    while q:
        u = q.popleft()
        if u == goal:
            path = []
            while u is not None:
                path.append(u)
                u = prev[u]
            return path[::-1]
        for v in graph[u]:
            if v not in prev:
                prev[v] = u
                q.append(v)
    return None
```

### Depth-first search (DFS)

Goes as deep as possible, then backtracks. Uses recursion or a **stack**.

```python
def dfs(graph, start):
    seen, order = set(), []
    def visit(u):
        seen.add(u)
        order.append(u)
        for v in graph[u]:
            if v not in seen:
                visit(v)
    visit(start)
    return order

def dfs_iter(graph, start):
    seen, order, stack = set(), [], [start]
    while stack:
        u = stack.pop()
        if u in seen:
            continue
        seen.add(u)
        order.append(u)
        stack.extend(v for v in graph[u] if v not in seen)
    return order
```

Both run in `O(V + E)` time and `O(V)` space.

| Use BFS for | Use DFS for |
|-------------|-------------|
| Shortest path (unweighted) | Cycle detection, topological sort |
| Level-order, nearest neighbour | Connected components, backtracking |
| Spreading processes (infection, rumor) | Exploring all paths, maze solving |

### Grid problems are graph problems

```python
def num_islands(grid):
    rows, cols, count = len(grid), len(grid[0]), 0
    def sink(r, c):
        if 0 <= r < rows and 0 <= c < cols and grid[r][c] == "1":
            grid[r][c] = "0"
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                sink(r + dr, c + dc)
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1":
                count += 1
                sink(r, c)
    return count
```

## 4. Key algorithms

### Cycle detection

- **Undirected:** during DFS, a visited neighbour that is not the parent means a cycle.
- **Directed:** track three states (unvisited, in current path, done). Reaching an "in current path" node means a cycle.

```python
def has_cycle_directed(graph):
    WHITE, GRAY, BLACK = 0, 1, 2
    color = defaultdict(int)
    def visit(u):
        color[u] = GRAY
        for v in graph[u]:
            if color[v] == GRAY or (color[v] == WHITE and visit(v)):
                return True
        color[u] = BLACK
        return False
    return any(color[u] == WHITE and visit(u) for u in list(graph))
```

### Topological sort (DAGs)

Orders vertices so every edge `u -> v` has `u` before `v`. Used for build systems and course prerequisites. **Kahn's algorithm** repeatedly removes vertices with in-degree 0:

```python
def topo_sort(num_nodes, edges):
    graph, indeg = defaultdict(list), [0] * num_nodes
    for u, v in edges:
        graph[u].append(v)
        indeg[v] += 1
    q = deque(i for i in range(num_nodes) if indeg[i] == 0)
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in graph[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return order if len(order) == num_nodes else []   # empty means a cycle
```

### Dijkstra: shortest paths with non-negative weights

Always expand the closest unvisited vertex, using a min-heap. `O((V + E) log V)`.

```python
import heapq

def dijkstra(graph, source):                 # graph[u] = [(v, weight), ...]
    dist = {source: 0}
    heap = [(0, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist.get(u, float("inf")):
            continue                          # stale entry
        for v, w in graph[u]:
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                heapq.heappush(heap, (nd, v))
    return dist
```

It fails with **negative edges**; use **Bellman-Ford** (`O(V * E)`, detects negative cycles) there.

### Union-Find (Disjoint Set Union)

Tracks connected components with near-constant-time `find` and `union`. Used for connectivity queries and Kruskal's algorithm.

```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]   # path compression
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True
```

### Minimum spanning tree

A subset of edges connecting all vertices with the smallest total weight. **Kruskal:** sort edges, add each one that does not form a cycle (check with Union-Find). **Prim:** grow the tree from one vertex using a min-heap.

### Complexity summary

| Algorithm | Time | Notes |
|-----------|------|-------|
| BFS / DFS | `O(V + E)` | |
| Topological sort | `O(V + E)` | DAGs only |
| Dijkstra (heap) | `O((V + E) log V)` | Non-negative weights |
| Bellman-Ford | `O(V * E)` | Handles negative weights |
| Floyd-Warshall | `O(V³)` | All pairs |
| Kruskal | `O(E log E)` | With Union-Find |
| Union-Find ops | ~`O(α(n))` | Nearly constant |

## 5. Two real-world examples

### Example 1: Maps and navigation

Road networks are weighted directed graphs: intersections are vertices, road segments are edges weighted by travel time (updated with live traffic). Google Maps and similar apps run variants of **Dijkstra and A\*** to find the fastest route among millions of vertices, using heuristics and precomputed shortcuts to answer in milliseconds. Ride-sharing matches drivers to riders with the same machinery.

### Example 2: Social networks and dependency management

Friend suggestions ("people you may know") come from BFS to depth 2 over the social graph: friends of friends who are not yet friends. Package managers (pip, npm), build tools (Make, Bazel) and CI pipelines model dependencies as a **DAG** and use **topological sort** to decide the install or build order, and **cycle detection** to report circular dependencies. Search engines rank pages with PageRank over the web's link graph.

## 6. Tips, tricks and pitfalls

- **Mark visited when you enqueue** (BFS), or the same node can be queued many times.
- **Handle disconnected graphs:** loop over all vertices and start a traversal from each unvisited one.
- **Directed vs undirected cycle detection differ.** The parent check works only for undirected graphs.
- **Dijkstra requires non-negative weights.** With negatives, use Bellman-Ford.
- **Recursion depth:** DFS on a large graph can overflow the stack; use an explicit stack.
- **Pick the representation by density.** Use adjacency lists unless the graph is dense.
- **Many problems hide a graph:** word ladders, grid mazes, state machines, currency exchange, course schedules.
- **Model the state** carefully: sometimes a vertex is `(position, keys_held)`, not just a position.
- **Use `dict`/`set` for sparse or non-integer vertex IDs.**

## 7. Check yourself

1. When would you pick an adjacency matrix over an adjacency list?
2. Why does BFS find shortest paths in unweighted graphs but DFS does not?
3. What is the complexity of BFS and DFS?
4. How do you detect a cycle in a directed graph?
5. What does a topological sort give you, and when is it impossible?
6. Why does Dijkstra fail with negative edges?
7. What does Union-Find do, and what do path compression and union by rank achieve?
8. How would you model "word ladder" as a graph?

<details>
<summary>Answers</summary>

1. For dense graphs, or when you need `O(1)` "is there an edge?" checks.
2. BFS visits vertices in order of increasing distance (by edge count), so the first time it reaches a vertex is via a shortest path. DFS may reach it through a long path first.
3. `O(V + E)` time and `O(V)` space.
4. Run DFS tracking three states (unvisited, in progress, done); reaching an in-progress vertex means a cycle. Or run Kahn's algorithm and see whether all vertices were ordered.
5. A linear order where every edge goes from earlier to later. It is impossible if the graph has a cycle.
6. Dijkstra assumes that once a vertex is settled its distance is final; a negative edge could later make a settled vertex's distance smaller.
7. It maintains disjoint sets with `find` and `union`. Compression flattens trees on `find`, rank keeps trees shallow on `union`; together operations are almost constant time.
8. Words are vertices; connect two words that differ by one letter; BFS from the start word finds the shortest transformation sequence.

</details>
