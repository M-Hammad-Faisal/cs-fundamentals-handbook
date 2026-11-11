# Advanced Graph Algorithms: Exercises

These problems go with the [Advanced Graph Algorithms lesson](README.md). Try each one before opening its solution.

## Problems

1. **Bellman-Ford:** shortest distances from a source with possibly negative edges; return `None` for a negative cycle.
2. **Floyd-Warshall:** all-pairs shortest paths.
3. **Network delay / cheapest path:** Dijkstra from a source on a weighted directed graph.
4. **Kruskal:** the total weight of a minimum spanning tree.
5. **Prim:** the same, using a heap.
6. **Minimum cost to connect all points** (Manhattan distance) using an MST.
7. **Strongly connected components** with Kosaraju.
8. **Critical connections** (bridges) in an undirected network.
9. **Path with minimum effort** in a grid (minimize the largest height difference along the path).
10. **A\*** shortest path on a grid with walls.
11. **Detect currency arbitrage** with Bellman-Ford and `-log` weights.

<details>
<summary>Solutions</summary>

```python
import heapq, math
from collections import defaultdict

# 1
def bellman_ford(n, edges, source):
    dist = [float("inf")] * n
    dist[source] = 0
    for _ in range(n - 1):
        changed = False
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w; changed = True
        if not changed:
            break
    for u, v, w in edges:
        if dist[u] + w < dist[v]:
            return None
    return dist

# 2
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
    return d

# 3
def dijkstra(graph, source):                   # graph[u] = [(v, w), ...]
    dist, heap = {}, [(0, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if u in dist:
            continue
        dist[u] = d
        for v, w in graph.get(u, []):
            if v not in dist:
                heapq.heappush(heap, (d + w, v))
    return dist

# 4
def kruskal(n, edges):                         # (w, u, v)
    parent = list(range(n))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    total = 0
    for w, u, v in sorted(edges):
        ru, rv = find(u), find(v)
        if ru != rv:
            parent[ru] = rv; total += w
    return total

# 5
def prim(graph, start):
    seen, heap, total = set(), [(0, start)], 0
    while heap and len(seen) < len(graph):
        w, u = heapq.heappop(heap)
        if u in seen:
            continue
        seen.add(u); total += w
        for v, wv in graph[u]:
            if v not in seen:
                heapq.heappush(heap, (wv, v))
    return total

# 6
def min_cost_connect_points(points):
    n = len(points)
    edges = [(abs(points[i][0] - points[j][0]) + abs(points[i][1] - points[j][1]), i, j)
             for i in range(n) for j in range(i + 1, n)]
    return kruskal(n, edges)

# 7
def kosaraju(n, edges):
    graph, rgraph = defaultdict(list), defaultdict(list)
    for u, v in edges:
        graph[u].append(v); rgraph[v].append(u)
    seen, order = set(), []
    def dfs1(u):
        seen.add(u)
        for v in graph[u]:
            if v not in seen: dfs1(v)
        order.append(u)
    for u in range(n):
        if u not in seen: dfs1(u)
    comps, seen = [], set()
    def dfs2(u, bucket):
        seen.add(u); bucket.append(u)
        for v in rgraph[u]:
            if v not in seen: dfs2(v, bucket)
    for u in reversed(order):
        if u not in seen:
            bucket = []; dfs2(u, bucket); comps.append(bucket)
    return comps

# 8
def critical_connections(n, connections):
    graph = defaultdict(list)
    for a, b in connections:
        graph[a].append(b); graph[b].append(a)
    disc, low, timer, bridges = {}, {}, [0], []
    def dfs(u, parent):
        disc[u] = low[u] = timer[0]; timer[0] += 1
        for v in graph[u]:
            if v == parent:
                continue
            if v not in disc:
                dfs(v, u)
                low[u] = min(low[u], low[v])
                if low[v] > disc[u]:
                    bridges.append([u, v])
            else:
                low[u] = min(low[u], disc[v])
    dfs(0, -1)
    return bridges

# 9
def minimum_effort_path(heights):
    rows, cols = len(heights), len(heights[0])
    best = [[float("inf")] * cols for _ in range(rows)]
    best[0][0] = 0
    heap = [(0, 0, 0)]
    while heap:
        effort, r, c = heapq.heappop(heap)
        if (r, c) == (rows - 1, cols - 1):
            return effort
        if effort > best[r][c]:
            continue
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                ne = max(effort, abs(heights[nr][nc] - heights[r][c]))
                if ne < best[nr][nc]:
                    best[nr][nc] = ne
                    heapq.heappush(heap, (ne, nr, nc))

# 10
def astar(grid, start, goal):
    h = lambda p: abs(p[0] - goal[0]) + abs(p[1] - goal[1])
    heap, best = [(h(start), 0, start)], {start: 0}
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

# 11
def has_arbitrage(currencies, rates):          # rates[i][j] = units of j per 1 of i
    n = len(currencies)
    edges = [(i, j, -math.log(rates[i][j]))
             for i in range(n) for j in range(n) if i != j and rates[i][j] > 0]
    dist = [0.0] * n                            # start everywhere to catch any cycle
    for _ in range(n):
        updated = False
        for u, v, w in edges:
            if dist[u] + w < dist[v] - 1e-12:
                dist[v] = dist[u] + w; updated = True
        if not updated:
            return False
    return True
```

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Shortest Paths Beyond Dijkstra](01-all-pairs-and-heuristic-shortest-paths.md) · [Connectivity, Strongly Connected Components, Bridges and Max Flow](02-connectivity-scc-and-flow.md)
