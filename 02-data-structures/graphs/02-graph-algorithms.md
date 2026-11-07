# Graph Algorithms: Ordering, Shortest Paths and Spanning Trees

**Prerequisites:** [graph basics, BFS and DFS](01-graph-basics-bfs-dfs.md), [heaps](../heaps/02-priority-queue-applications.md). **You will learn:** **topological sort** (ordering tasks with dependencies), **Dijkstra** and **Bellman-Ford** (shortest paths in weighted graphs), and **minimum spanning trees** with Prim's algorithm. Kruskal's algorithm is in the [union-find lesson](03-union-find.md).

## 1. Topological sort: ordering with dependencies

A **topological order** lists the vertices of a directed acyclic graph (DAG) so every edge `u -> v` has `u` before `v`. Think: *you must put on socks before shoes*; *course A is a prerequisite of course B*. If the graph has a **cycle**, no valid order exists.

### Kahn's algorithm (BFS style)

Repeatedly take a vertex with **no unmet prerequisites** (in-degree 0), output it, and remove its edges.

```python
from collections import deque, defaultdict

def topological_sort(graph):
    indegree = {v: 0 for v in graph}
    for u in graph:
        for v in graph[u]:
            indegree[v] = indegree.get(v, 0) + 1
    queue = deque(v for v, d in indegree.items() if d == 0)
    order = []
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in graph.get(u, []):
            indegree[v] -= 1
            if indegree[v] == 0:                      # all prerequisites of v are done
                queue.append(v)
    if len(order) != len(indegree):
        raise ValueError("cycle detected: no valid order")
    return order

courses = {
    "intro": ["data structures", "discrete math"],
    "data structures": ["algorithms"],
    "discrete math": ["algorithms"],
    "algorithms": ["databases"],
    "databases": [],
}
print(topological_sort(courses))
# ['intro', 'data structures', 'discrete math', 'algorithms', 'databases']

try:
    topological_sort({"a": ["b"], "b": ["c"], "c": ["a"]})
except ValueError as e:
    print(e)                                           # cycle detected: no valid order
```

Time `O(V + E)`. The cycle check comes free: if some vertices never reach in-degree 0, they sit on a cycle.

### The DFS way

Run DFS and add each vertex to a list **after** visiting all its descendants (postorder); the reverse of that list is a topological order.

```python
def topological_sort_dfs(graph):
    seen, post = set(), []
    def dfs(u):
        seen.add(u)
        for v in graph.get(u, []):
            if v not in seen:
                dfs(v)
        post.append(u)                                  # finished: everything after u is already listed
    for u in graph:
        if u not in seen:
            dfs(u)
    return post[::-1]

print(topological_sort_dfs(courses))
# ['intro', 'discrete math', 'data structures', 'algorithms', 'databases']
```

Both answers are valid: a graph usually has several correct topological orders.

**Where it is used:** build systems (`make`, Bazel, npm installing dependencies in the right order), spreadsheet recalculation, course scheduling, Airflow task pipelines.

## 2. Weighted shortest paths

BFS counts edges. When edges have different costs (distance, time, price) we need other tools.

| Algorithm | Handles | Time |
|-----------|---------|------|
| BFS | unweighted | `O(V + E)` |
| **Dijkstra** | non-negative weights | `O((V + E) log V)` with a heap |
| **Bellman-Ford** | negative weights too; detects negative cycles | `O(V · E)` |
| DAG relaxation | any weights on a DAG | `O(V + E)` |
| Floyd-Warshall | all pairs | `O(V³)` |

### Dijkstra (with the path)

The heap-based version was introduced in [priority queue applications](../heaps/02-priority-queue-applications.md); here it also reconstructs the route.

```python
import heapq

def dijkstra(graph, start):
    dist, parent = {start: 0}, {start: None}
    heap = [(0, start)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue                                    # stale heap entry
        for v, w in graph[u]:
            if d + w < dist.get(v, float("inf")):
                dist[v], parent[v] = d + w, u
                heapq.heappush(heap, (d + w, v))
    return dist, parent

def path_to(parent, target):
    path = []
    while target is not None:
        path.append(target); target = parent[target]
    return path[::-1]

roads = {
    "Lahore":     [("Islamabad", 380), ("Multan", 340), ("Faisalabad", 130)],
    "Faisalabad": [("Islamabad", 340), ("Multan", 240)],
    "Multan":     [("Karachi", 880)],
    "Islamabad":  [("Peshawar", 180)],
    "Karachi":    [],
    "Peshawar":   [],
}
dist, parent = dijkstra(roads, "Lahore")
print(dist["Peshawar"], path_to(parent, "Peshawar"))    # 560 ['Lahore', 'Islamabad', 'Peshawar']
print(dist["Karachi"], path_to(parent, "Karachi"))      # 1220 ['Lahore', 'Multan', 'Karachi']
```

**Why it works (greedy):** when the closest unsettled vertex `u` is popped, any other route to it would have to pass through some unsettled vertex that is at least as far away, plus a non-negative edge, so it cannot be shorter. A **negative edge** breaks this argument.

### Bellman-Ford

Relax **every edge** `V - 1` times: after round `k`, all shortest paths using at most `k` edges are correct. If a further round still improves something, a **negative cycle** exists (a loop that gets cheaper each lap, so "shortest" has no answer).

```python
def bellman_ford(vertices, edges, start):
    dist = {v: float("inf") for v in vertices}
    dist[start] = 0
    for _ in range(len(vertices) - 1):
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    for u, v, w in edges:
        if dist[u] + w < dist[v]:
            raise ValueError("negative cycle reachable from the start")
    return dist

money = [("A", "B", 4), ("A", "C", 5), ("B", "C", -3), ("C", "D", 2)]      # B->C has negative weight: a refund
print(bellman_ford("ABCD", money, "A"))                  # {'A': 0, 'B': 4, 'C': 1, 'D': 3}

try:
    bellman_ford("ABC", [("A", "B", 1), ("B", "C", -2), ("C", "B", 1)], "A")
except ValueError as e:
    print(e)                                             # negative cycle reachable from the start
```

Real uses: currency-arbitrage detection (a negative cycle in log-rates) and distance-vector routing protocols such as RIP.

### Shortest paths on a DAG (cheap and exact)

Process vertices in topological order and relax their outgoing edges once: `O(V + E)`, works with negative weights, and the same trick finds the **longest path** (critical path in project planning) by negating weights.

```python
def dag_shortest(graph, start):
    dist = {v: float("inf") for v in graph}
    dist[start] = 0
    order = topological_sort_dfs({u: [v for v, _ in edges] for u, edges in graph.items()})      # ignore weights for ordering
    for u in order:
        if dist[u] < float("inf"):
            for v, w in graph[u]:
                dist[v] = min(dist[v], dist[u] + w)
    return dist

tasks = {"A": [("B", 3), ("C", 2)], "B": [("D", 4)], "C": [("D", 1)], "D": []}
print(dag_shortest(tasks, "A"))                          # {'A': 0, 'B': 3, 'C': 2, 'D': 3}
```

## 3. Minimum spanning tree (MST)

Given a weighted, connected, undirected graph, a **spanning tree** connects all vertices using `V - 1` edges with no cycle. The **minimum spanning tree** has the smallest total weight. Classic use: laying cable or pipes to connect all sites as cheaply as possible.

### Prim's algorithm

Grow one tree from a start vertex; always add the **cheapest edge leaving the tree** (a heap finds it).

```python
def prim(graph, start):
    in_tree, edges, total = {start}, [], 0
    heap = [(w, start, v) for v, w in graph[start]]
    heapq.heapify(heap)
    while heap and len(in_tree) < len(graph):
        w, u, v = heapq.heappop(heap)
        if v in in_tree:
            continue                                      # this edge would form a cycle
        in_tree.add(v)
        edges.append((u, v, w))
        total += w
        for nxt, nw in graph[v]:
            if nxt not in in_tree:
                heapq.heappush(heap, (nw, v, nxt))
    return total, edges

offices = {
    "A": [("B", 4), ("C", 1), ("D", 3)],
    "B": [("A", 4), ("C", 2), ("E", 5)],
    "C": [("A", 1), ("B", 2), ("D", 6), ("E", 7)],
    "D": [("A", 3), ("C", 6)],
    "E": [("B", 5), ("C", 7)],
}
print(prim(offices, "A"))                                # (11, [('A', 'C', 1), ('C', 'B', 2), ('A', 'D', 3), ('B', 'E', 5)])
```

Time `O(E log V)`. The **cut property** justifies the greed: for any split of the vertices into two groups, the cheapest edge crossing the split belongs to some MST.

## 4. Choosing the right tool

| Question | Use |
|----------|-----|
| Fewest hops | BFS |
| Cheapest route, non-negative costs | Dijkstra (A* if you have a good heuristic) |
| Costs may be negative / find arbitrage | Bellman-Ford |
| Tasks with prerequisites | topological sort |
| Cheapest way to connect everything | Prim or Kruskal |
| Are two things connected (with edges arriving over time)? | [union-find](03-union-find.md) |

## 5. Two real-world examples

**Example 1: Package managers.** `pip`, `npm` and `apt` build a dependency graph and use a topological order to install libraries before the things that need them (and report a cycle as an error).

**Example 2: Maps.** Navigation apps run Dijkstra-like searches (with heuristics such as A*, and precomputed shortcuts) on road graphs with travel times as weights.

## 6. Common mistakes

- Running Dijkstra with negative edge weights.
- Forgetting to skip stale heap entries in Dijkstra.
- Using topological sort on a graph with a cycle without checking.
- Using BFS on a weighted graph and trusting hop counts as costs.
- Treating "shortest path" in Bellman-Ford as defined when a negative cycle is reachable.
- Prim's algorithm on a disconnected graph (you only get one component's tree).

## 7. Practice

1. Give a topological order for `shirt -> tie -> jacket`, `trousers -> shoes -> jacket`, `trousers -> belt -> jacket`.
2. How many topological orders does a graph with no edges and 3 vertices have?
3. Run Dijkstra by hand from `S` in `S->A 1`, `S->B 4`, `A->B 2`, `B->T 1`, `A->T 6`.
4. With `S->A 1`, `S->B 2`, `B->A -5`, what does textbook Dijkstra (which never revisits a settled vertex) report for A, and what is the true cost?
5. Find the MST total for edges `A-B 1`, `B-C 2`, `A-C 3`.
6. Write `has_valid_schedule(prerequisites)` that returns whether courses can all be finished.

<details>
<summary>Solutions</summary>

1. One valid order: `shirt, tie, trousers, shoes, belt, jacket`.
2. 6 (`3! = 6` orderings, since nothing constrains them).
3. Distances: `A=1`, `B=3` (via A), `T=4` (via B). Path `S-A-B-T`.
4. Dijkstra settles A first at cost 1 (it is the closest) and treats that as final. The true cheapest route is `S->B->A = 2 - 5 = -3`. Our lazy-heap code would happen to re-relax A here, but with negative edges that behavior can blow up to exponential time and is not guaranteed correct in general: use Bellman-Ford.
5. Edges `A-B` (1) and `B-C` (2): total **3**.
6. ```python
   def has_valid_schedule(prereqs):
       graph = defaultdict(list)
       nodes = set()
       for course, before in prereqs:
           graph[before].append(course); nodes |= {course, before}
       try:
           topological_sort({n: graph[n] for n in nodes}); return True
       except ValueError:
           return False
   print(has_valid_schedule([(1, 0), (2, 1)]), has_valid_schedule([(1, 0), (0, 1)]))      # True False
   ```

</details>

## 8. Check yourself

1. What does a topological order require of the graph?
2. How does Kahn's algorithm detect a cycle?
3. When must you use Bellman-Ford instead of Dijkstra?
4. What is a minimum spanning tree?
5. What is the complexity of Dijkstra with a binary heap?

<details>
<summary>Answers</summary>

1. It must be a directed acyclic graph.
2. Vertices on a cycle never reach in-degree 0, so fewer vertices are output than exist.
3. When some edge weights are negative.
4. A set of `V - 1` edges connecting every vertex with minimum total weight and no cycle.
5. `O((V + E) log V)`.

</details>

[Back to graphs](README.md) · Previous: [graph basics](01-graph-basics-bfs-dfs.md) · Next: [union-find](03-union-find.md)
