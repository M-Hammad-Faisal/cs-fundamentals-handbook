# Shortest Paths Beyond Dijkstra: Floyd-Warshall, A*, 0-1 BFS

**Prerequisites:** [graph basics](../../02-data-structures/graphs/01-graph-basics-bfs-dfs.md), [Dijkstra and Bellman-Ford](../../02-data-structures/graphs/02-graph-algorithms.md), [dynamic programming thinking](../dynamic-programming/01-dp-thinking-and-1d-problems.md). **You will learn:** how to get **all-pairs** shortest paths with **Floyd-Warshall** (a DP in disguise), how to find one route fast with **A\*** (Dijkstra plus a guess about the remaining distance), the **0-1 BFS** trick for edges that cost 0 or 1, and how to choose among all the shortest-path tools.

## 1. Choosing a shortest-path algorithm

| Situation | Algorithm | Time |
|-----------|-----------|------|
| Unweighted | BFS | `O(V + E)` |
| Weights 0 or 1 | **0-1 BFS** (deque) | `O(V + E)` |
| Non-negative weights, one source | Dijkstra | `O((V + E) log V)` |
| Negative weights, one source | Bellman-Ford | `O(V · E)` |
| **All pairs** (every start and end) | **Floyd-Warshall** | `O(V³)` |
| One source to one target with a good estimate | **A\*** | typically far fewer nodes than Dijkstra |
| DAG | topological order + relax | `O(V + E)` |

## 2. Floyd-Warshall: all pairs in a dozen lines

**Question:** the shortest distance between **every** pair of vertices (a distance table for a whole road network).

**Idea (dynamic programming):** let `dist[i][j]` be the best known distance. Allow the vertices `0, 1, ..., k` one at a time as possible **intermediate stops**. For each new `k`, a path `i -> j` either skips `k` or goes `i -> k -> j`:

```text
dist[i][j] = min( dist[i][j],  dist[i][k] + dist[k][j] )
```

```python
INF = float("inf")

def floyd_warshall(n, edges):
    dist = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    nxt = [[None] * n for _ in range(n)]               # next[i][j] = first step on the best path i -> j
    for u, v, w in edges:
        if w < dist[u][v]:                              # keep the cheapest if there are parallel edges
            dist[u][v] = w
            nxt[u][v] = v
    for k in range(n):                                  # allow k as an intermediate stop
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    nxt[i][j] = nxt[i][k]
    return dist, nxt

def path(nxt, u, v):
    if nxt[u][v] is None:
        return None
    route = [u]
    while u != v:
        u = nxt[u][v]
        route.append(u)
    return route

#  0 -3-> 1 -2-> 2        0 -8-> 2
edges = [(0, 1, 3), (1, 2, 2), (0, 2, 8), (2, 3, 1), (3, 0, 4)]
dist, nxt = floyd_warshall(4, edges)
for row in dist:
    print(row)
# [0, 3, 5, 6]
# [7, 0, 2, 3]
# [5, 8, 0, 1]
# [4, 7, 9, 0]
print(path(nxt, 0, 3), path(nxt, 3, 2))               # [0, 1, 2, 3] [3, 0, 1, 2]
```

**Properties:** three nested loops, so `O(V³)` time and `O(V²)` space; handles **negative edges**; detects a **negative cycle** when some `dist[i][i] < 0`. The loop order (`k` outermost) is essential: that is what makes the DP correct.

```python
dist_neg, _ = floyd_warshall(3, [(0, 1, 1), (1, 2, -3), (2, 0, 1)])         # cycle 0->1->2->0 costs -1
print([dist_neg[i][i] for i in range(3)])             # [-1, -1, -2]    any negative diagonal entry reveals a negative cycle
```

Handy by-products: **transitive closure** (replace `+`/`min` with `and`/`or` to ask "can `i` reach `j`?") and the graph's **diameter**.

```python
def transitive_closure(n, edges):
    reach = [[i == j for j in range(n)] for i in range(n)]
    for u, v in edges:
        reach[u][v] = True
    for k in range(n):
        for i in range(n):
            for j in range(n):
                reach[i][j] = reach[i][j] or (reach[i][k] and reach[k][j])
    return reach

print(transitive_closure(3, [(0, 1), (1, 2)])[0])      # [True, True, True]
```

**When to use it:** small dense graphs (up to a few hundred vertices) where you need many queries. For a large sparse graph, running Dijkstra from each source is faster.

## 3. A* search: Dijkstra with a compass

Dijkstra expands vertices in order of distance from the start, spreading out in all directions like a ripple. If you know **roughly where the goal is**, you can aim: order the search by

```text
f(n) = g(n) + h(n)
g(n) = cost already spent to reach n
h(n) = HEURISTIC: an estimate of the cost still to go from n to the goal
```

If the heuristic is **admissible** (never overestimates the true remaining cost), A* still returns an **optimal** path. If `h` is also **consistent**, no vertex needs to be re-expanded. With `h = 0` A* is exactly Dijkstra.

Grid example with 4-direction moves: the **Manhattan distance** `|dx| + |dy|` never overestimates, so it is admissible.

```python
import heapq

def astar(grid, start, goal):
    rows, cols = len(grid), len(grid[0])
    def h(cell):                                          # Manhattan distance to the goal
        return abs(cell[0] - goal[0]) + abs(cell[1] - goal[1])
    open_heap = [(h(start), 0, start)]                    # (f, g, cell)
    best_g, parent, expanded = {start: 0}, {start: None}, 0
    while open_heap:
        f, g, cell = heapq.heappop(open_heap)
        if g > best_g.get(cell, INF):
            continue                                      # stale entry
        expanded += 1
        if cell == goal:
            route = []
            while cell is not None:
                route.append(cell); cell = parent[cell]
            return route[::-1], expanded
        r, c = cell
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
                ng = g + 1
                if ng < best_g.get((nr, nc), INF):
                    best_g[(nr, nc)] = ng
                    parent[(nr, nc)] = cell
                    heapq.heappush(open_heap, (ng + h((nr, nc)), ng, (nr, nc)))
    return None, expanded

def dijkstra_grid(grid, start, goal):                      # the same search with h = 0, to compare the effort
    rows, cols = len(grid), len(grid[0])
    heap, best, expanded = [(0, start)], {start: 0}, 0
    while heap:
        d, cell = heapq.heappop(heap)
        if d > best.get(cell, INF):
            continue
        expanded += 1
        if cell == goal:
            return d, expanded
        r, c = cell
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0 and d + 1 < best.get((nr, nc), INF):
                best[(nr, nc)] = d + 1
                heapq.heappush(heap, (d + 1, (nr, nc)))
    return None, expanded

size = 40
grid = [[0] * size for _ in range(size)]                  # an open 40 x 40 field with one wall
for r in range(5, 35):
    grid[r][20] = 1
route, a_star_work = astar(grid, (20, 5), (20, 35))
length, dijkstra_work = dijkstra_grid(grid, (20, 5), (20, 35))
print(len(route) - 1, length)                             # 60 60        (same optimal length: the path detours around the wall)
print(a_star_work < dijkstra_work, a_star_work, dijkstra_work)      # True 831 1541
```

Both find a shortest path of the same length (60 steps, going around the wall), but A* expands 831 cells where Dijkstra expands 1541: the heuristic keeps it pointed at the goal.

**A\* is used in** games (NPC pathfinding), robotics, GPS routing (with landmark-based heuristics), and puzzle solvers (the 15-puzzle with a "tiles out of place" heuristic).

**Caveats:** a heuristic that **overestimates** can return a non-optimal path; a poor (but admissible) heuristic degrades towards Dijkstra; A* stores all frontier states, so memory can be the limit (IDA* trades time for memory).

## 4. 0-1 BFS: edges that cost 0 or 1

If every edge weighs 0 or 1, Dijkstra's heap is overkill. Use a **deque**: push a 0-edge neighbor at the **front** (it is as close as the current vertex) and a 1-edge neighbor at the **back**. `O(V + E)`.

```python
from collections import deque

def zero_one_bfs(graph, start):
    dist = {start: 0}
    dq = deque([start])
    while dq:
        u = dq.popleft()
        for v, w in graph[u]:                              # w is 0 or 1
            if dist[u] + w < dist.get(v, INF):
                dist[v] = dist[u] + w
                if w == 0:
                    dq.appendleft(v)
                else:
                    dq.append(v)
    return dist

# Moving along a corridor is free; opening a door costs 1.
g = {"A": [("B", 0), ("C", 1)], "B": [("D", 1)], "C": [("D", 0)], "D": []}
print(zero_one_bfs(g, "A"))                                # {'A': 0, 'B': 0, 'C': 1, 'D': 1}
```

Typical uses: grids where you pay 1 to turn or to break a wall, and "minimum number of flips/changes" problems.

## 5. Verifying the algorithms agree

Two correct algorithms must give identical answers. Cross-check Floyd-Warshall against Dijkstra on random graphs:

```python
import random

def dijkstra_all(n, adj, s):
    dist = [INF] * n
    dist[s] = 0
    heap = [(0, s)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(heap, (d + w, v))
    return dist

random.seed(6)
for _ in range(100):
    n = random.randint(2, 8)
    edges = [(random.randrange(n), random.randrange(n), random.randint(1, 9)) for _ in range(random.randint(0, 20))]
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((v, w))
    fw, _ = floyd_warshall(n, edges)
    for source in range(n):
        assert fw[source] == dijkstra_all(n, adj, source)
print("Floyd-Warshall agrees with Dijkstra on 100 random graphs")       # Floyd-Warshall agrees with Dijkstra on 100 random graphs
```

(Random graphs contain parallel edges and self-loops, which is how this test caught a bug in an earlier draft: always keep the **cheapest** of parallel edges.)

## 6. Two real-world examples

**Example 1: Network routing tables.** Link-state protocols such as OSPF run Dijkstra at every router; small network cores sometimes precompute all-pairs tables like Floyd-Warshall's for instant lookups.

**Example 2: Game and robot navigation.** A* with a good heuristic over a grid or navigation mesh finds routes in milliseconds, which is why almost every game engine ships it.

## 7. Common mistakes

- Floyd-Warshall with the `k` loop **not** outermost (wrong results, not an error).
- Using `INF + INF` carelessly in languages with integer overflow (Python's `float("inf")` is safe).
- A* with a heuristic that overestimates (non-optimal paths) or that is expensive to compute.
- Forgetting stale entries in the A*/Dijkstra heap.
- Using Floyd-Warshall on thousands of vertices (`V³` is billions of steps).
- Treating `dist[i][i] < 0` as an ordinary result instead of a negative-cycle alarm.

## 8. Practice

1. How many operations does Floyd-Warshall do on 100 vertices (about)? On 1000?
2. Run `floyd_warshall` mentally on edges `0->1 (2)`, `1->2 (2)`, `0->2 (5)`. What is `dist[0][2]`?
3. Why is the Manhattan distance admissible for 4-direction grid movement but not for 8-direction (diagonal) movement?
4. Which heuristic is guaranteed admissible for any graph?
5. Use `zero_one_bfs` to find the minimum door-openings from `S` to `T` in: `S -0-> A`, `A -1-> T`, `S -1-> T`.
6. When would you choose Dijkstra-from-each-source over Floyd-Warshall?

<details>
<summary>Solutions</summary>

1. About `100³ = 1 million` and `1000³ = 1 billion` updates.
2. `dist[0][2] = min(5, 2 + 2) = 4`.
   ```python
   print(floyd_warshall(3, [(0, 1, 2), (1, 2, 2), (0, 2, 5)])[0][0][2])      # 4
   ```
3. With diagonals the true cost can be smaller than `|dx| + |dy|` (a diagonal step covers both axes), so Manhattan overestimates; use Chebyshev or octile distance instead.
4. `h = 0` (that is Dijkstra); any lower bound on the remaining cost works.
5. ```python
   print(zero_one_bfs({"S": [("A", 0), ("T", 1)], "A": [("T", 1)], "T": []}, "S")["T"])      # 1
   ```
6. On large sparse graphs: `V` runs of Dijkstra cost `O(V · E log V)`, which beats `V³` when `E` is much smaller than `V²`.

</details>

## 9. Check yourself

1. What does Floyd-Warshall compute and what is its time complexity?
2. What does the `k` loop represent?
3. What is `f(n)` in A*?
4. What does "admissible heuristic" mean?
5. Why does 0-1 BFS use a deque?

<details>
<summary>Answers</summary>

1. The shortest distance between every pair of vertices; `O(V³)`.
2. The set of vertices allowed as intermediate stops so far.
3. `g(n) + h(n)`: cost so far plus the estimated remaining cost.
4. It never overestimates the true remaining cost, which guarantees an optimal path.
5. Zero-cost neighbors go to the front and one-cost neighbors to the back, so vertices come out in nondecreasing distance without a heap.

</details>

[Back to graph algorithms](README.md) · Next: [connectivity, SCC and flow](02-connectivity-scc-and-flow.md)
