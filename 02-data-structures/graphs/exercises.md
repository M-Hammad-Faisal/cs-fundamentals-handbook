# Graphs: Exercises

## Problems
1. **Number of islands** in a grid of `"1"` (land) and `"0"` (water).
2. Find the **shortest path** (fewest edges) between two vertices.
3. **Clone a graph** (deep copy of an undirected graph).
4. **Course schedule:** given prerequisites, can all courses be finished? Return an order.
5. **Detect a cycle** in an undirected graph.
6. **Word ladder:** shortest transformation length from `begin` to `end`, changing one letter at a time through a word list.
7. **Rotting oranges:** minutes until all oranges rot (multi-source BFS).
8. **Network delay time:** given weighted directed edges, time for a signal from a source to reach all nodes (Dijkstra).
9. **Number of connected components** using Union-Find.
10. **Is the graph bipartite?** (can vertices be 2-colored so no edge joins same colors)
11. **Cheapest flights within K stops** (Bellman-Ford style).

<details>
<summary>Solutions</summary>

```python
import heapq
from collections import defaultdict, deque

# 1
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

# 2
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

# 3
class GNode:
    def __init__(self, val, neighbors=None):
        self.val, self.neighbors = val, neighbors or []

def clone_graph(node):
    if not node:
        return None
    copies = {node: GNode(node.val)}
    q = deque([node])
    while q:
        u = q.popleft()
        for v in u.neighbors:
            if v not in copies:
                copies[v] = GNode(v.val)
                q.append(v)
            copies[u].neighbors.append(copies[v])
    return copies[node]

# 4
def find_order(n, prerequisites):
    graph, indeg = defaultdict(list), [0] * n
    for course, pre in prerequisites:
        graph[pre].append(course)
        indeg[course] += 1
    q = deque(i for i in range(n) if indeg[i] == 0)
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in graph[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return order if len(order) == n else []

# 5
def has_cycle_undirected(n, edges):
    graph = defaultdict(list)
    for u, v in edges:
        graph[u].append(v); graph[v].append(u)
    seen = set()
    def dfs(u, parent):
        seen.add(u)
        for v in graph[u]:
            if v == parent:
                continue
            if v in seen or dfs(v, u):
                return True
        return False
    return any(u not in seen and dfs(u, -1) for u in range(n))

# 6
def ladder_length(begin, end, words):
    words = set(words)
    if end not in words:
        return 0
    q, seen = deque([(begin, 1)]), {begin}
    while q:
        w, d = q.popleft()
        if w == end:
            return d
        for i in range(len(w)):
            for c in "abcdefghijklmnopqrstuvwxyz":
                nw = w[:i] + c + w[i + 1:]
                if nw in words and nw not in seen:
                    seen.add(nw)
                    q.append((nw, d + 1))
    return 0

# 7
def oranges_rotting(grid):
    rows, cols = len(grid), len(grid[0])
    q, fresh = deque(), 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                q.append((r, c, 0))
            elif grid[r][c] == 1:
                fresh += 1
    minutes = 0
    while q:
        r, c, m = q.popleft()
        minutes = max(minutes, m)
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                grid[nr][nc] = 2
                fresh -= 1
                q.append((nr, nc, m + 1))
    return minutes if fresh == 0 else -1

# 8
def network_delay(times, n, k):
    graph = defaultdict(list)
    for u, v, w in times:
        graph[u].append((v, w))
    dist, heap = {}, [(0, k)]
    while heap:
        d, u = heapq.heappop(heap)
        if u in dist:
            continue
        dist[u] = d
        for v, w in graph[u]:
            if v not in dist:
                heapq.heappush(heap, (d + w, v))
    return max(dist.values()) if len(dist) == n else -1

# 9
def count_components(n, edges):
    parent = list(range(n))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    comps = n
    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
            comps -= 1
    return comps

# 10
def is_bipartite(graph):                       # graph: list of neighbor lists
    color = {}
    for start in range(len(graph)):
        if start in color:
            continue
        color[start] = 0
        q = deque([start])
        while q:
            u = q.popleft()
            for v in graph[u]:
                if v not in color:
                    color[v] = 1 - color[u]
                    q.append(v)
                elif color[v] == color[u]:
                    return False
    return True

# 11
def cheapest_flight(n, flights, src, dst, k):
    prices = [float("inf")] * n
    prices[src] = 0
    for _ in range(k + 1):
        nxt = prices[:]
        for u, v, w in flights:
            if prices[u] + w < nxt[v]:
                nxt[v] = prices[u] + w
        prices = nxt
    return -1 if prices[dst] == float("inf") else prices[dst]
```

</details>

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Graph Basics](01-graph-basics-bfs-dfs.md) · [Graph Algorithms](02-graph-algorithms.md) · [Union-Find](03-union-find.md)
