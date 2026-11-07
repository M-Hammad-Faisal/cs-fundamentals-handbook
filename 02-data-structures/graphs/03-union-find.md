# Union-Find (Disjoint Sets) and Kruskal's Algorithm

**Prerequisites:** [graph basics](01-graph-basics-bfs-dfs.md), [graph algorithms](02-graph-algorithms.md) (spanning trees), [amortized analysis](../../01-complexity/06-cases-and-amortized-analysis.md). **You will learn:** the **union-find** structure that answers "are these two things in the same group?" and "merge two groups" in near-constant time, the two optimizations (**path compression** and **union by rank**), and uses: **Kruskal's MST**, **cycle detection** and counting groups.

## 1. In plain words

You are building friend circles. You are told "Ana and Bo are friends", "Bo and Cy are friends", and are asked "Are Ana and Cy in the same circle?" You could rebuild a graph and run BFS for every question (`O(V + E)` each time). **Union-find** keeps the groups up to date as friendships arrive and answers in almost `O(1)`.

Two operations:

- `find(x)`: which group (represented by a **leader**, the root) is `x` in?
- `union(a, b)`: merge the groups of `a` and `b`.

## 2. Idea: each group is a tree of parent pointers

Every element points to a parent; the root points to itself. `find` follows parents up to the root.

```text
start: each element is its own group      union(1, 2)        union(2, 3)
 0   1   2   3   4                        0  1<-2  3  4       0  1<-2  4
                                                                   ^
                                                                   3 (points to 1)
```

## 3. The simple version (and why it is not enough)

```python
class SimpleUnionFind:
    def __init__(self, n):
        self.parent = list(range(n))

    def find(self, x):
        while self.parent[x] != x:
            x = self.parent[x]
        return x

    def union(self, a, b):
        self.parent[self.find(a)] = self.find(b)

chain = SimpleUnionFind(1000)
for i in range(999):
    chain.union(i, i + 1)                    # always attaches the old root under the new element
depth, x = 0, 0
while chain.parent[x] != x:
    x, depth = chain.parent[x], depth + 1
print(depth)                                 # 999   (a long chain: find(0) takes 999 steps)
```

Bad unions produce a chain and `find` degrades to `O(n)`. Two small ideas fix it.

## 4. Two optimizations

1. **Path compression:** during `find`, point every node on the path **directly at the root** so the next `find` is one step.
2. **Union by rank (or size):** always attach the **smaller/shorter** tree under the bigger one so trees stay shallow.

```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n
        self.groups = n

    def find(self, x):
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:               # path compression: re-point everything on the path
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False                            # already in the same group
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra                        # attach the smaller tree under the larger
        self.size[ra] += self.size[rb]
        self.groups -= 1
        return True

    def connected(self, a, b):
        return self.find(a) == self.find(b)

uf = UnionFind(6)
print(uf.union(0, 1), uf.union(1, 2), uf.union(0, 2))       # True True False   (0 and 2 were already connected)
print(uf.connected(0, 2), uf.connected(0, 5), uf.groups)    # True False 4
uf.union(3, 4)
print(uf.groups, uf.size[uf.find(0)])                       # 3 3

big = UnionFind(1000)
for i in range(999):
    big.union(i, i + 1)
steps, x = 0, 999                                           # start from the last element
while big.parent[x] != x:
    x, steps = big.parent[x], steps + 1
print(steps, big.groups)                                    # 1 1   (shallow tree: the last element is one hop from the root)
```

**Cost:** with both optimizations a sequence of `m` operations on `n` items costs `O(m · α(n))`, where `α` is the **inverse Ackermann function**, which is at most 4 for any `n` that fits in the universe. In practice: **constant time**.

## 5. Use 1: counting connected components

```python
def count_components(n, edges):
    uf = UnionFind(n)
    for a, b in edges:
        uf.union(a, b)
    return uf.groups

print(count_components(5, [(0, 1), (1, 2), (3, 4)]), count_components(4, []))      # 2 4
```

Unlike BFS/DFS, union-find handles edges that **arrive one at a time** (a growing network) with no re-search.

## 6. Use 2: detecting a cycle while adding edges

If `union(a, b)` returns `False`, `a` and `b` were already connected, so this edge closes a cycle.

```python
def first_redundant_edge(edges):
    uf = UnionFind(max(max(e) for e in edges) + 1)
    for a, b in edges:
        if not uf.union(a, b):
            return (a, b)
    return None

print(first_redundant_edge([(1, 2), (1, 3), (2, 3)]), first_redundant_edge([(1, 2), (2, 3)]))      # (2, 3) None
```

## 7. Use 3: Kruskal's minimum spanning tree

**Greedy:** sort all edges by weight; take each edge **unless it would form a cycle** (union-find checks that instantly). Stop at `V - 1` edges.

```python
def kruskal(n, edges):
    uf, mst, total = UnionFind(n), [], 0
    for w, a, b in sorted(edges):                     # cheapest first
        if uf.union(a, b):                            # joins two different groups: safe to keep
            mst.append((a, b, w))
            total += w
            if len(mst) == n - 1:
                break
    return total, mst

# vertices 0..4 = A..E (same graph as the Prim example)
edges = [(4, 0, 1), (1, 0, 2), (3, 0, 3), (2, 1, 2), (5, 1, 4), (6, 2, 3), (7, 2, 4)]
print(kruskal(5, edges))                              # (11, [(0, 2, 1), (1, 2, 2), (0, 3, 3), (1, 4, 5)])
```

Same total (11) as Prim's earlier. Time `O(E log E)` for sorting.

| | Prim | Kruskal |
|---|------|---------|
| Grows | one tree | a forest that merges |
| Needs | heap | sorted edges + union-find |
| Better when | dense graphs | sparse graphs, edge lists |

## 8. Use 4: grouping by equivalence

"Accounts with a shared email belong to the same person": union accounts that share an email and count the groups.

```python
from collections import defaultdict

def merge_accounts(accounts):
    uf = UnionFind(len(accounts))
    owner_of_email = {}
    for i, (_, *emails) in enumerate(accounts):
        for e in emails:
            if e in owner_of_email:
                uf.union(i, owner_of_email[e])        # shared email: same person
            else:
                owner_of_email[e] = i
    merged = defaultdict(set)
    for e, i in owner_of_email.items():
        merged[uf.find(i)].add(e)
    return sorted([accounts[i][0]] + sorted(es) for i, es in merged.items())

accounts = [["John", "a@x.com", "b@x.com"], ["John", "b@x.com", "c@x.com"], ["Mary", "m@x.com"]]
print(merge_accounts(accounts))                       # [['John', 'a@x.com', 'b@x.com', 'c@x.com'], ['Mary', 'm@x.com']]
```

## 9. Two real-world examples

**Example 1: Image segmentation and "flood fill" labelling.** Pixels that touch and share a color are unioned; the number of groups is the number of regions. (Video games use it for "which tiles are in the same lake?".)

**Example 2: Network design.** Kruskal's algorithm picks the cheapest set of links connecting all data centers; union-find stops it from adding a redundant link that would form a loop.

## 10. Common mistakes

- Forgetting to call `find` on **both** elements before comparing (comparing `parent[a]` directly is wrong).
- Skipping path compression or union by size (works, but can be very slow).
- Using union-find when you need to **split** groups (it only merges; deletions need other techniques).
- Off-by-one: indexing items `1..n` into a `0..n-1` structure.
- Using it for shortest paths (it only tells you who is connected, not how far).

## 11. Practice

1. After `union(0,1)`, `union(2,3)`, `union(1,3)`, how many groups remain among 5 items, and are 0 and 2 connected?
2. Edges `(0,1), (1,2), (2,0)`: which edge reveals the cycle?
3. Write `largest_group(n, edges)` returning the biggest component size.
4. Use Kruskal on edges `(1, A-B), (4, B-C), (3, A-C), (2, C-D)`. What is the MST weight?
5. Why can `find` use recursion safely only with union by size?
6. Number of provinces: given an `n x n` matrix where `M[i][j] == 1` means cities `i`, `j` are connected, count the provinces.

<details>
<summary>Solutions</summary>

1. 2 groups (`{0,1,2,3}` and `{4}`); yes, connected.
2. `(2, 0)`: by then 0 and 2 are already connected through 1.
3. ```python
   def largest_group(n, edges):
       uf = UnionFind(n)
       for a, b in edges: uf.union(a, b)
       return max(uf.size[uf.find(i)] for i in range(n))
   print(largest_group(6, [(0, 1), (1, 2), (3, 4)]))     # 3
   ```
4. Sorted: `A-B 1`, `C-D 2`, `A-C 3` (joins {A,B} and {C,D}), then `B-C 4` is skipped (cycle). Total `1 + 2 + 3 = 6`.
5. Union by size keeps trees `O(log n)` deep, so recursion depth stays tiny; without it a chain could exceed Python's recursion limit.
6. ```python
   def find_provinces(matrix):
       n = len(matrix)
       uf = UnionFind(n)
       for i in range(n):
           for j in range(i + 1, n):
               if matrix[i][j]: uf.union(i, j)
       return uf.groups
   print(find_provinces([[1, 1, 0], [1, 1, 0], [0, 0, 1]]))      # 2
   ```

</details>

## 12. Check yourself

1. What two operations does union-find support?
2. What do path compression and union by size each do?
3. What does `union` returning `False` tell you?
4. Why is Kruskal's algorithm paired with union-find?
5. Is union-find suitable for removing edges?

<details>
<summary>Answers</summary>

1. `find` (which group) and `union` (merge groups).
2. Compression flattens paths during `find`; union by size attaches small trees under big ones to keep trees shallow.
3. The two items were already connected: the edge would close a cycle.
4. It tests "would this edge form a cycle?" in almost constant time.
5. No: it only merges; splitting needs other structures.

</details>

[Back to graphs](README.md) · Previous: [graph algorithms](02-graph-algorithms.md)
