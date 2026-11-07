# Connectivity, Strongly Connected Components, Bridges and Max Flow

**Prerequisites:** [graph basics, BFS and DFS](../../02-data-structures/graphs/01-graph-basics-bfs-dfs.md), [union-find](../../02-data-structures/graphs/03-union-find.md), [recursion](../recursion-backtracking/01-recursion-fundamentals.md). **You will learn:** how to analyze the **structure** of a graph: **strongly connected components** (Kosaraju), **bridges and articulation points** (the single points of failure, via Tarjan's low-link idea), **Euler paths**, and **maximum flow** (Edmonds-Karp) with **bipartite matching** as its best-known application.

## 1. Connectivity in two flavors

- **Undirected graph:** *connected components* are the islands (BFS/DFS or union-find, see earlier lessons).
- **Directed graph:** "can reach" is not symmetric. A **strongly connected component (SCC)** is a maximal set of vertices where **every vertex can reach every other**. Collapsing each SCC into one node always yields a **DAG** (the *condensation graph*).

```text
 A -> B -> C -> D -> E <-> F
 ^         |
 +---------+            SCCs: {A, B, C} (a loop), {D}, {E, F}
                        edges between different SCCs only ever go one way
```

## 2. Strongly connected components: Kosaraju's algorithm

1. DFS the graph and record vertices in order of **finishing time**.
2. **Reverse all edges.**
3. Process vertices in **decreasing finish time**, running a DFS on the *reversed* graph from each unvisited vertex; every DFS tree is one SCC.

Why it works: the vertex that finishes last sits in a "source" SCC of the condensation DAG; in the reversed graph you cannot escape that SCC into another, so a DFS from it collects exactly its component.

```python
from collections import defaultdict

def kosaraju_scc(graph):
    order, seen = [], set()
    def dfs1(u):
        seen.add(u)
        for v in graph.get(u, []):
            if v not in seen:
                dfs1(v)
        order.append(u)                                    # finish time order
    for u in list(graph):
        if u not in seen:
            dfs1(u)

    reverse = defaultdict(list)
    for u in graph:
        for v in graph[u]:
            reverse[v].append(u)

    components, seen = [], set()
    def dfs2(u, component):
        seen.add(u)
        component.append(u)
        for v in reverse[u]:
            if v not in seen:
                dfs2(v, component)
    for u in reversed(order):                              # decreasing finish time
        if u not in seen:
            component = []
            dfs2(u, component)
            components.append(sorted(component))
    return components

g = {"A": ["B"], "B": ["C"], "C": ["A", "D"], "D": ["E"], "E": ["F"], "F": ["E"]}
print(kosaraju_scc(g))                                     # [['A', 'B', 'C'], ['D'], ['E', 'F']]
print(kosaraju_scc({"x": ["y"], "y": [], "z": []}))        # [['z'], ['x'], ['y']]   (a DAG: every vertex is alone)
```

Time `O(V + E)`. **Tarjan's algorithm** finds SCCs in a single DFS with low-link values (below); Kosaraju is simpler to remember.

**Uses:** finding mutually dependent modules (circular imports form an SCC of size > 1), "who can reach whom" in social/follow graphs, deadlock analysis, 2-SAT solving, and condensing a graph before a DAG algorithm such as topological sort.

```python
def has_circular_dependency(deps):                         # any SCC with more than one node, or a self-loop
    for comp in kosaraju_scc(deps):
        if len(comp) > 1 or comp[0] in deps.get(comp[0], []):
            return comp
    return None

print(has_circular_dependency({"app": ["db", "utils"], "db": ["utils"], "utils": ["app"]}))      # ['app', 'db', 'utils']
print(has_circular_dependency({"app": ["db"], "db": []}))                                         # None
```

## 3. Bridges and articulation points (single points of failure)

In an undirected connected graph:

- A **bridge** is an edge whose removal disconnects the graph.
- An **articulation point (cut vertex)** is a vertex whose removal disconnects it.

Network engineers care deeply: a bridge is a cable whose failure splits the network.

**Brute force:** remove each edge and test connectivity: `O(E · (V + E))`. **Tarjan's trick** does it in one DFS (`O(V + E)`):

- `disc[u]` = the time the DFS first visited `u`.
- `low[u]` = the earliest discovery time reachable from `u`'s DFS subtree using at most **one back edge**.
- A tree edge `u -> v` is a **bridge** if `low[v] > disc[u]`: nothing in `v`'s subtree can reach back to `u` or above, so cutting the edge isolates that subtree.

```python
def find_bridges(n, edges):
    adj = [[] for _ in range(n)]
    for idx, (u, v) in enumerate(edges):
        adj[u].append((v, idx))
        adj[v].append((u, idx))
    disc, low, bridges, timer = [-1] * n, [0] * n, [], [0]
    def dfs(u, parent_edge):
        disc[u] = low[u] = timer[0]; timer[0] += 1
        for v, idx in adj[u]:
            if idx == parent_edge:
                continue                                   # do not walk back along the edge we came by
            if disc[v] == -1:
                dfs(v, idx)
                low[u] = min(low[u], low[v])
                if low[v] > disc[u]:
                    bridges.append(edges[idx])             # no way back up: this edge is a bridge
            else:
                low[u] = min(low[u], disc[v])              # back edge: we can climb to an earlier vertex
    for s in range(n):
        if disc[s] == -1:
            dfs(s, -1)
    return sorted(tuple(sorted(e)) for e in bridges)

def find_articulation_points(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v); adj[v].append(u)
    disc, low, cut, timer = [-1] * n, [0] * n, set(), [0]
    def dfs(u, parent):
        disc[u] = low[u] = timer[0]; timer[0] += 1
        children = 0
        for v in adj[u]:
            if v == parent:
                continue
            if disc[v] == -1:
                children += 1
                dfs(v, u)
                low[u] = min(low[u], low[v])
                if parent != -1 and low[v] >= disc[u]:
                    cut.add(u)                             # v's subtree cannot bypass u
            else:
                low[u] = min(low[u], disc[v])
        if parent == -1 and children > 1:
            cut.add(u)                                     # a root is a cut vertex only if it has 2+ DFS children
    for s in range(n):
        if disc[s] == -1:
            dfs(s, -1)
    return sorted(cut)

#   0 --- 1 --- 3 --- 4        triangle 0-1-2 (no bridges inside it);
#    \   /                      1-3 and 3-4 are bridges
#      2
edges = [(0, 1), (1, 2), (2, 0), (1, 3), (3, 4)]
print(find_bridges(5, edges))                              # [(1, 3), (3, 4)]
print(find_articulation_points(5, edges))                  # [1, 3]
```

Verify the fast version against brute force on random graphs:

```python
import random

def components_count(n, edges):
    parent = list(range(n))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for u, v in edges:
        parent[find(u)] = find(v)
    return len({find(x) for x in range(n)})

def bridges_bruteforce(n, edges):
    base = components_count(n, edges)
    return sorted(tuple(sorted(e)) for i, e in enumerate(edges)
                  if components_count(n, edges[:i] + edges[i + 1:]) > base)

random.seed(12)
for _ in range(200):
    n = random.randint(2, 8)
    pool = [(a, b) for a in range(n) for b in range(a + 1, n)]
    chosen = random.sample(pool, random.randint(0, len(pool)))
    assert find_bridges(n, chosen) == bridges_bruteforce(n, chosen)
print("Tarjan bridges matched brute force on 200 random graphs")      # Tarjan bridges matched brute force on 200 random graphs
```

## 4. Euler paths: visit every *edge* once

An **Euler path** uses every edge exactly once; an **Euler circuit** also returns to the start (the "draw it without lifting the pen" puzzle; the original problem was Euler's Seven Bridges of Konigsberg, 1736).

**Rule (undirected, connected edges):** a circuit exists iff **every vertex has even degree**; a path exists iff **exactly 0 or 2** vertices have odd degree (the path must start and end at the odd ones).

```python
def euler_type(n, edges):
    degree = [0] * n
    for u, v in edges:
        degree[u] += 1; degree[v] += 1
    odd = sum(d % 2 for d in degree)
    return "circuit" if odd == 0 else "path" if odd == 2 else "none"

print(euler_type(3, [(0, 1), (1, 2), (2, 0)]))             # circuit    (a triangle)
print(euler_type(4, [(0, 1), (1, 2), (2, 3)]))             # path       (a line: ends have degree 1)
print(euler_type(4, [(0, 1), (0, 2), (0, 3)]))             # none       (a star: four odd degrees)
```

The connectedness of the edges must also be checked. **Hierholzer's algorithm** constructs the actual circuit in `O(E)`:

```python
def eulerian_circuit(edges, start):
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v); adj[v].append(u)
    stack, circuit = [start], []
    while stack:
        u = stack[-1]
        if adj[u]:
            v = adj[u].pop()
            adj[v].remove(u)                               # use the edge in both directions
            stack.append(v)
        else:
            circuit.append(stack.pop())                    # dead end: this vertex closes the loop
    return circuit[::-1]

print(eulerian_circuit([(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 2)], 0))      # [0, 2, 4, 3, 2, 1, 0]   (one valid circuit: it uses all 6 edges and returns to 0)
```

(A **Hamiltonian** path, visiting every *vertex* once, looks similar but is NP-complete: no known fast algorithm; the neighbor problem of the travelling salesman.)

## 5. Maximum flow

**Problem:** each edge is a pipe with a **capacity**. What is the largest amount that can be pushed from a source `s` to a sink `t`? (Water through pipes, packets through links, cars through roads.)

**Ford-Fulkerson idea:** repeatedly find an **augmenting path** (a path from `s` to `t` with spare capacity), push the bottleneck amount along it, and update **residual capacities**: forward edges lose capacity, and **reverse edges gain it** (which lets later paths "undo" earlier choices). Stop when no augmenting path exists. **Edmonds-Karp** uses BFS to find the shortest augmenting path each time, giving `O(V · E²)`.

```python
from collections import deque

def max_flow(capacity, source, sink):
    """capacity: dict of dicts, capacity[u][v] = capacity of the edge u -> v."""
    residual = defaultdict(lambda: defaultdict(int))
    for u in capacity:
        for v, c in capacity[u].items():
            residual[u][v] += c                            # forward capacity (reverse starts at 0)
    flow = 0
    while True:
        parent = {source: None}
        queue = deque([source])
        while queue and sink not in parent:                # BFS for an augmenting path
            u = queue.popleft()
            for v, c in residual[u].items():
                if c > 0 and v not in parent:
                    parent[v] = u
                    queue.append(v)
        if sink not in parent:
            return flow                                    # no augmenting path left: the flow is maximum
        bottleneck, v = float("inf"), sink
        while parent[v] is not None:                       # smallest spare capacity along the path
            bottleneck = min(bottleneck, residual[parent[v]][v]); v = parent[v]
        v = sink
        while parent[v] is not None:
            residual[parent[v]][v] -= bottleneck           # use up forward capacity
            residual[v][parent[v]] += bottleneck           # create reverse capacity
            v = parent[v]
        flow += bottleneck

network = {
    "s": {"a": 10, "b": 10},
    "a": {"b": 2, "c": 4, "d": 8},
    "b": {"d": 9},
    "c": {"t": 10},
    "d": {"c": 6, "t": 10},
    "t": {},
}
print(max_flow(network, "s", "t"))                         # 19
```

**Max-flow min-cut theorem:** the maximum flow equals the capacity of the cheapest **cut** (a set of edges whose removal separates `s` from `t`). The same computation therefore also tells you the **bottleneck** of a network.

### Application: bipartite matching

Assign people to jobs where each person can do certain jobs; maximize the number of people employed. Build a flow network: `source -> each person` (capacity 1), `person -> job` (capacity 1, if able), `job -> sink` (capacity 1). The max flow is the maximum matching.

```python
def max_matching(can_do):
    network = defaultdict(dict)
    for person, jobs in can_do.items():
        network["source"][("P", person)] = 1
        for job in jobs:
            network[("P", person)][("J", job)] = 1
            network[("J", job)]["sink"] = 1
    return max_flow(network, "source", "sink")

print(max_matching({"Ana": ["web", "db"], "Bo": ["web"], "Cy": ["db", "ops"], "Di": ["ops"]}))      # 3   (four people but only three jobs exist)
print(max_matching({"Ana": ["web"], "Bo": ["web"], "Cy": ["web"]}))                                  # 1
```

Other uses: project selection, image segmentation (graph cuts), airline crew and baseball elimination problems.

## 6. Which tool for which question?

| Question | Tool |
|----------|------|
| Are these two nodes connected? Count the islands | union-find or BFS/DFS |
| Which directed nodes are mutually reachable? Circular dependencies? | SCC (Kosaraju/Tarjan) |
| Which links/servers are single points of failure? | bridges and articulation points |
| Can I traverse every road exactly once? | Euler path/circuit (degree parity) |
| Largest throughput; minimum cut; best assignment | max flow / bipartite matching |
| Shortest routes | BFS/Dijkstra/A*/Floyd-Warshall |
| Cheapest way to connect everything | MST (Prim/Kruskal) |

## 7. Two real-world examples

**Example 1: Network resilience audits.** Operators run bridge/articulation analysis on their topology to find links whose failure would partition the network, then add redundancy there.

**Example 2: Ride and task assignment.** Matching drivers to riders, students to schools or interns to projects is bipartite matching (with weights, the more general assignment problem), solved by flow-based algorithms.

## 8. Common mistakes

- Running undirected-graph connectivity code on a directed graph (and vice versa).
- Tarjan's bridge check: forgetting to skip the **parent edge** (and using the parent vertex instead of the parent edge id breaks multigraphs).
- Treating a DFS root as an articulation point without checking it has 2 or more DFS children.
- Max flow: forgetting reverse edges (the algorithm then gets stuck below the optimum).
- Recursion depth on large graphs (use iterative DFS or raise limits carefully).
- Confusing Euler (edges) with Hamiltonian (vertices) problems.

## 9. Practice

1. List the SCCs of `1->2, 2->3, 3->1, 3->4, 4->5, 5->4`.
2. Why must the condensation graph of SCCs be acyclic?
3. Find the bridges in a path of 4 vertices `0-1-2-3`. In a cycle of 4?
4. Does the 5-vertex "house" graph (a square with a triangle roof) have an Euler path?
5. Compute the max flow for `s->a 3, s->b 2, a->t 2, b->t 3, a->b 1`.
6. A bipartite graph has 3 people and 3 jobs where everyone can do only job X. What is the maximum matching?

<details>
<summary>Solutions</summary>

1. `{1, 2, 3}` and `{4, 5}`.
   ```python
   print(kosaraju_scc({1: [2], 2: [3], 3: [1, 4], 4: [5], 5: [4]}))      # [[1, 2, 3], [4, 5]]
   ```
2. If two SCCs could reach each other, every vertex of both could reach every vertex of the other, so they would be one SCC.
3. A path: all 3 edges are bridges; a cycle: none.
   ```python
   print(find_bridges(4, [(0, 1), (1, 2), (2, 3)]), find_bridges(4, [(0, 1), (1, 2), (2, 3), (3, 0)]))      # [(0, 1), (1, 2), (2, 3)] []
   ```
4. Edges: `0-1, 1-2, 2-3, 3-0` (the square) plus `0-4, 1-4` (the roof). Degrees: vertices 0 and 1 have 3, vertices 2, 3 and 4 have 2. Exactly two odd vertices, so **yes**, an Euler path exists (it must start at 0 and end at 1, or the reverse).
   ```python
   house = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 4), (1, 4)]
   print(euler_type(5, house))                                          # path
   ```
5. ```python
   print(max_flow({"s": {"a": 3, "b": 2}, "a": {"t": 2, "b": 1}, "b": {"t": 3}, "t": {}}, "s", "t"))      # 5
   ```
6. Only one job exists for them, so at most **1** person can be matched.
   ```python
   print(max_matching({"p1": ["X"], "p2": ["X"], "p3": ["X"]}))        # 1
   ```

</details>

## 10. Check yourself

1. What is an SCC and how many DFS passes does Kosaraju's algorithm need?
2. What does `low[v] > disc[u]` mean for a tree edge `u -> v`?
3. What is the parity rule for an Euler circuit?
4. Why do residual graphs have reverse edges?
5. What does the max-flow min-cut theorem say?

<details>
<summary>Answers</summary>

1. A maximal set of mutually reachable vertices; two DFS passes (one on the graph, one on the reversed graph).
2. Nothing in `v`'s subtree can reach back to `u` or above, so the edge is a bridge.
3. Every vertex has an even degree (and the edges are connected).
4. They let later augmenting paths cancel flow that earlier paths sent, which is needed to reach the true maximum.
5. The maximum flow from `s` to `t` equals the smallest total capacity of any cut separating them.

</details>

[Back to graph algorithms](README.md) · Previous: [all-pairs and heuristic shortest paths](01-all-pairs-and-heuristic-shortest-paths.md)
