# Graph Basics: Representations, BFS and DFS

**Prerequisites:** [trees](../trees/01-binary-trees-and-traversals.md), [stacks and queues](../stacks-queues/03-stack-and-queue-applications.md) (BFS uses a queue, DFS a stack), [hash tables](../hash-tables/01-hash-functions-and-collisions.md). **You will learn:** graph vocabulary, the two standard ways to store a graph, **breadth-first search** and **depth-first search** step by step, and the problems they solve: shortest paths, connected components, grids and cycle detection.

## 1. In plain words

A **graph** is things (**vertices** or **nodes**) connected by links (**edges**). Friends on a social network, cities and roads, web pages and hyperlinks, courses and their prerequisites: all graphs. A tree is just a graph with no cycles and exactly one path between any two nodes.

```text
   A --- B           vertices: A, B, C, D, E      edges: A-B, A-C, B-D, C-D, D-E
   |     |
   C --- D --- E
```

## 2. Vocabulary

| Term | Meaning |
|------|---------|
| **Undirected / directed** | edges go both ways (friendship) / one way (follows, one-way street) |
| **Weighted** | edges have a cost or distance |
| **Neighbors / adjacent** | vertices joined by an edge |
| **Degree** | number of edges at a vertex (in-degree/out-degree if directed) |
| **Path** | sequence of vertices where consecutive ones are connected |
| **Cycle** | a path that returns to its start |
| **Connected** | every vertex can reach every other (undirected) |
| **DAG** | directed acyclic graph: directed, no cycles |
| **Sparse / dense** | few edges (`E` about `V`) / many (`E` about `V²`) |

## 3. Storing a graph

**Adjacency list:** for each vertex, the list of its neighbors. Memory `O(V + E)`. The default choice.

**Adjacency matrix:** a `V x V` table where cell `[i][j]` is 1 (or the weight) if there is an edge. Memory `O(V²)`, but edge checks are `O(1)`.

```python
from collections import defaultdict

edges = [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D"), ("D", "E")]

adjacency_list = defaultdict(list)
for u, v in edges:
    adjacency_list[u].append(v)
    adjacency_list[v].append(u)               # undirected: store both directions
print(dict(adjacency_list))
# {'A': ['B', 'C'], 'B': ['A', 'D'], 'C': ['A', 'D'], 'D': ['B', 'C', 'E'], 'E': ['D']}

names = ["A", "B", "C", "D", "E"]
index = {name: i for i, name in enumerate(names)}
matrix = [[0] * 5 for _ in range(5)]          # build rows separately (not [[0]*5]*5)
for u, v in edges:
    matrix[index[u]][index[v]] = matrix[index[v]][index[u]] = 1
for row in matrix:
    print(row)
# [0, 1, 1, 0, 0]
# [1, 0, 0, 1, 0]
# [1, 0, 0, 1, 0]
# [0, 1, 1, 0, 1]
# [0, 0, 0, 1, 0]
```

| | Adjacency list | Adjacency matrix |
|---|----------------|------------------|
| Memory | `O(V + E)` | `O(V²)` |
| Is there an edge `u-v`? | `O(degree)` (or `O(1)` with sets) | `O(1)` |
| List neighbors of `u` | `O(degree)` | `O(V)` |
| Best for | sparse graphs (most real ones) | dense graphs, small `V` |

A third form, the **edge list** (`[(u, v, weight), ...]`), suits algorithms that sort or scan all edges (Kruskal's MST).

## 4. Breadth-first search (BFS)

**Idea:** explore in **rings**: first the start, then everything 1 edge away, then 2 edges away... A **queue** gives this order. Because it reaches every vertex by the fewest edges, BFS finds the **shortest path in an unweighted graph**.

```text
start at A:       A            queue: [A]
visit A -> add B, C            queue: [B, C]
visit B -> add D               queue: [C, D]
visit C -> D already seen      queue: [D]
visit D -> add E               queue: [E]
visit E                        done   order: A B C D E
```

```python
from collections import deque

graph = dict(adjacency_list)

def bfs(graph, start):
    seen, order, queue = {start}, [], deque([start])
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in seen:                   # mark when ENQUEUED so nothing is queued twice
                seen.add(neighbor)
                queue.append(neighbor)
    return order

print(bfs(graph, "A"))                                 # ['A', 'B', 'C', 'D', 'E']

def shortest_path(graph, start, goal):
    parent, queue = {start: None}, deque([start])
    while queue:
        node = queue.popleft()
        if node == goal:
            path = []
            while node is not None:                    # walk back through the parents
                path.append(node); node = parent[node]
            return path[::-1]
        for neighbor in graph[node]:
            if neighbor not in parent:
                parent[neighbor] = node
                queue.append(neighbor)
    return None

print(shortest_path(graph, "A", "E"))                  # ['A', 'B', 'D', 'E']
print(shortest_path(graph, "A", "Z") if "Z" in graph else "no such vertex")      # no such vertex
```

**Complexity:** each vertex is queued once and each edge examined once (twice if undirected): **`O(V + E)`** time, `O(V)` space.

## 5. Depth-first search (DFS)

**Idea:** go as deep as possible along one path, then **backtrack**. Recursion (the call stack) or an explicit **stack** does this.

```python
def dfs_recursive(graph, node, seen=None):
    seen = seen if seen is not None else set()
    seen.add(node)
    order = [node]
    for neighbor in graph[node]:
        if neighbor not in seen:
            order += dfs_recursive(graph, neighbor, seen)
    return order

def dfs_iterative(graph, start):
    seen, order, stack = set(), [], [start]
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        order.append(node)
        for neighbor in reversed(graph[node]):          # reversed so the first neighbor is explored first
            stack.append(neighbor)
    return order

print(dfs_recursive(graph, "A"))                        # ['A', 'B', 'D', 'C', 'E']
print(dfs_iterative(graph, "A"))                        # ['A', 'B', 'D', 'C', 'E']
```

Also **`O(V + E)`**. The only mechanical difference from BFS is a stack instead of a queue (see the [comparison](../stacks-queues/03-stack-and-queue-applications.md)).

| | BFS | DFS |
|---|-----|-----|
| Data structure | queue | stack / recursion |
| Explores | by distance (rings) | deep first, then back up |
| Shortest path (unweighted) | **yes** | no |
| Memory | up to the widest layer | up to the deepest path |
| Good for | shortest paths, nearest, levels | cycles, components, topological order, backtracking, mazes |

## 6. Connected components

How many separate "islands" does an undirected graph have? Run a search from every unseen vertex.

```python
def connected_components(graph):
    seen, components = set(), []
    for start in graph:
        if start not in seen:
            component = bfs({k: [n for n in v] for k, v in graph.items()}, start)
            seen.update(component)
            components.append(sorted(component))
    return components

two_islands = {"A": ["B"], "B": ["A"], "C": ["D"], "D": ["C"], "E": []}
print(connected_components(two_islands))                # [['A', 'B'], ['C', 'D'], ['E']]
print(len(connected_components(graph)))                 # 1
```

## 7. Grids are graphs

A maze or a map is a graph where each cell connects to its 4 (or 8) neighbors; you never build it explicitly, you just compute neighbors.

```python
def shortest_maze_path(maze, start, goal):
    rows, cols = len(maze), len(maze[0])
    queue, dist = deque([start]), {start: 0}
    while queue:
        r, c = queue.popleft()
        if (r, c) == goal:
            return dist[(r, c)]
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] == "." and (nr, nc) not in dist:
                dist[(nr, nc)] = dist[(r, c)] + 1
                queue.append((nr, nc))
    return -1

maze = ["..#....",
        ".##.##.",
        "....#..",
        ".##...#",
        "...#..."]
print(shortest_maze_path(maze, (0, 0), (4, 6)))         # 10

def count_islands(grid):
    rows, cols, seen, count = len(grid), len(grid[0]), set(), 0
    def sink(r, c):
        stack = [(r, c)]
        while stack:
            x, y = stack.pop()
            if (x, y) in seen or not (0 <= x < rows and 0 <= y < cols) or grid[x][y] != "1":
                continue
            seen.add((x, y))
            stack.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1" and (r, c) not in seen:
                count += 1
                sink(r, c)
    return count

print(count_islands(["11000", "11000", "00100", "00011"]))      # 3
```

## 8. Detecting cycles

**Undirected graph:** a cycle exists if DFS meets an already-seen vertex that is not the vertex it just came from.

**Directed graph:** a cycle exists if DFS reaches a vertex that is **currently on the recursion path** (three colors: unseen, in progress, finished).

```python
def has_cycle_undirected(graph):
    seen = set()
    def dfs(node, parent):
        seen.add(node)
        for nb in graph[node]:
            if nb not in seen:
                if dfs(nb, node): return True
            elif nb != parent:
                return True
        return False
    return any(dfs(v, None) for v in graph if v not in seen)

def has_cycle_directed(graph):
    state = {}                                             # 1 = in progress, 2 = done
    def dfs(node):
        state[node] = 1
        for nb in graph.get(node, []):
            if state.get(nb) == 1: return True             # back to something still on the path
            if nb not in state and dfs(nb): return True
        state[node] = 2
        return False
    return any(dfs(v) for v in graph if v not in state)

print(has_cycle_undirected(graph), has_cycle_undirected({"A": ["B"], "B": ["A", "C"], "C": ["B"]}))      # True False
print(has_cycle_directed({"A": ["B"], "B": ["C"], "C": ["A"]}), has_cycle_directed({"A": ["B", "C"], "B": ["C"], "C": []}))      # True False
```

## 9. Two real-world examples

**Example 1: "People you may know" / degrees of separation.** BFS from you, stopping at depth 2 or 3, lists friends-of-friends and "you are 4 connections away".

**Example 2: Web crawlers.** A crawler is a graph search where pages are vertices and links are edges, with a `seen` set so it does not revisit pages (BFS gives broad coverage, DFS can get lost in endless sites).

## 10. Common mistakes

- Forgetting the `seen` set: BFS/DFS loops forever on a cycle.
- Marking visited when *popping* rather than when *enqueuing* in BFS (nodes get queued many times).
- Recursive DFS on a huge graph: `RecursionError`; use the iterative version.
- Using BFS for **weighted** shortest paths (use Dijkstra, see the [next lesson](02-graph-algorithms.md)).
- Building a matrix with `[[0]*n]*n` (all rows alias one list).
- Forgetting to add both directions for an undirected edge.

## 11. Practice

1. Draw the adjacency list of edges `1-2, 1-3, 2-4, 3-4, 4-5, 6-7`.
2. In that graph, what is the BFS order from 1? How many components?
3. What is the shortest path from 1 to 5?
4. A graph has 1000 vertices and 2000 edges. Which representation? Why?
5. Write `reachable(graph, a, b)`.
6. Write `degrees(graph)` returning a dict of vertex to degree.
7. Write `bipartite(graph)` that tests whether you can 2-color the graph (BFS with colors).

<details>
<summary>Solutions</summary>

1. `1: [2, 3]`, `2: [1, 4]`, `3: [1, 4]`, `4: [2, 3, 5]`, `5: [4]`, `6: [7]`, `7: [6]`.
2. BFS order `1, 2, 3, 4, 5`; two components `{1..5}` and `{6, 7}`.
3. `1-2-4-5` (length 3).
4. An adjacency list: it is sparse (2000 edges versus a possible 1 million), so a matrix would waste memory.
5. ```python
   def reachable(g, a, b):
       return b in bfs(g, a)
   print(reachable(graph, "A", "E"), reachable(two_islands, "A", "D"))      # True False
   ```
6. ```python
   def degrees(g):
       return {v: len(nbs) for v, nbs in g.items()}
   print(degrees(graph))      # {'A': 2, 'B': 2, 'C': 2, 'D': 3, 'E': 1}
   ```
7. ```python
   def bipartite(g):
       color = {}
       for s in g:
           if s in color: continue
           color[s], queue = 0, deque([s])
           while queue:
               u = queue.popleft()
               for v in g[u]:
                   if v not in color:
                       color[v] = 1 - color[u]; queue.append(v)
                   elif color[v] == color[u]:
                       return False
       return True
   print(bipartite({"A": ["B"], "B": ["A", "C"], "C": ["B"]}), bipartite(graph))      # True True
   ```
   (`graph` has even cycle A-B-D-C so it is bipartite.)

</details>

## 12. Check yourself

1. Adjacency list or matrix for a social network, and why?
2. What data structure does BFS use? DFS?
3. Why does BFS find shortest paths in unweighted graphs?
4. What is the time complexity of BFS and DFS?
5. How do you detect a cycle in a directed graph?

<details>
<summary>Answers</summary>

1. Adjacency list: millions of users but each has relatively few friends (sparse).
2. A queue; a stack (or recursion).
3. It visits vertices in order of increasing edge count from the start.
4. `O(V + E)` for both.
5. Run DFS and look for an edge to a vertex that is still on the current recursion path.

</details>

[Back to graphs](README.md) · Next: [graph algorithms](02-graph-algorithms.md)
