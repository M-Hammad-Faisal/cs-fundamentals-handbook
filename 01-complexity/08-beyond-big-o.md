# Beyond Big-O: Constants, Caches, Hard Problems and Practical Choices

**Prerequisites:** the previous complexity lessons. **You will learn:** where Big-O stops being enough (constants, small inputs, memory caches, I/O), how to pick between algorithms in practice, what makes some problems **intractable** (P, NP, NP-complete), and what to do when a problem is too hard to solve exactly.

## 1. In plain words

Big-O answers "how does the cost **grow**?" It deliberately ignores **how big the constant is** and **what the hardware does**. That is usually the right thing to ignore, but not always. A professional engineer uses Big-O to rule out hopeless approaches, then **measures** to choose among the survivors. This lesson is the bridge from theory to practice.

## 2. Constants matter when `n` is small (or the gap is small)

```python
import time

def insertion_sort(a):
    a = a[:]
    for i in range(1, len(a)):
        key, j = a[i], i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]; j -= 1
        a[j + 1] = key
    return a

def merge_sort(a):
    if len(a) <= 1: return a
    mid = len(a) // 2
    left, right = merge_sort(a[:mid]), merge_sort(a[mid:])
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]: out.append(left[i]); i += 1
        else: out.append(right[j]); j += 1
    return out + left[i:] + right[j:]

import random
random.seed(1)

def best_time(fn, data, repeat=5):
    best = float("inf")
    for _ in range(repeat):
        t = time.perf_counter(); fn(data); best = min(best, time.perf_counter() - t)
    return best

for n in (8, 64, 512, 2000):
    data = [random.random() for _ in range(n)]
    ins, mer = best_time(insertion_sort, data), best_time(merge_sort, data)
    print(f"n={n:>5}  insertion {ins * 1e6:>10.1f} us   merge {mer * 1e6:>10.1f} us   winner: {'insertion' if ins < mer else 'merge'}")
# For tiny n the "worse" O(n²) insertion sort wins; as n grows the O(n log n) merge sort wins by a widening margin.
```

That is exactly why **Timsort** (Python's `sorted`) and many library sorts switch to **insertion sort for small runs** (about 16-64 items) and use merge-style logic for large ones. Big-O is about **large `n`**; for small `n` constants, caching and simplicity win.

**Practical rule:** do not replace a simple `O(n²)` loop with a complicated `O(n log n)` structure when `n` is at most a few hundred and the code is not a bottleneck.

## 3. The hardware is not the RAM model

The simple "every step costs one unit" model hides the **memory hierarchy** ([how computers work](../00-foundations/computer-basics/how-computers-work.md)): the CPU is far faster than RAM, so data that is **close together** and accessed **in order** is processed much faster (the CPU loads a cache line of 64 bytes at once, and the prefetcher guesses what you will read next).

```python
import array, random, time

n = 2_000_000
values = array.array("q", range(n))                 # a contiguous block of 8-byte integers
order_seq = list(range(n))
order_rand = order_seq[:]
random.shuffle(order_rand)

def walk(order):
    total = 0
    for i in order:
        total += values[i]
    return total

t = time.perf_counter(); a = walk(order_seq); sequential = time.perf_counter() - t
t = time.perf_counter(); b = walk(order_rand); randomized = time.perf_counter() - t
print(a == b, randomized > sequential)             # True True:   the SAME O(n) work, but visiting memory in random order is slower
```

(In Python the interpreter overhead hides much of the effect; in C or NumPy the gap is often 5-20x. The point: two algorithms with the same Big-O can differ greatly because of **memory access patterns**.)

Consequences you will meet:

- **Arrays beat linked lists** in practice for most workloads, even where Big-O says insertion into a linked list is `O(1)`: contiguous memory is cache friendly, pointers are not.
- **Row-major vs column-major** traversal of a 2D array can differ 10x.
- **Struct of arrays vs array of structs**, columnar databases and NumPy exploit sequential access.
- **Batching** (do many small operations in one big call) beats many tiny calls: function-call and system-call overhead are constants.

## 4. The unit of cost is not always a CPU step

| What dominates | Typical cost | What to do |
|----------------|--------------|------------|
| **CPU work** | nanoseconds per step | better algorithm, vectorize, compile |
| **Memory/cache misses** | 100 ns per miss | contiguous data, locality, smaller data |
| **Disk I/O** | 0.1 ms (SSD) to 10 ms (HDD) per access | sequential reads, caching, indexes, batching |
| **Network round trips** | 0.5 ms (same datacenter) to 150 ms (cross-continent) | fewer calls, caching, CDN, async |
| **Lock contention / waiting** | unbounded | less sharing, queues, concurrency design |
| **Garbage collection / allocation** | varies | reuse objects, generators, avoid churn |

An `O(n)` algorithm that makes one **network call per item** (n = 1,000, 50 ms each) takes 50 seconds. An `O(n log n)` algorithm that makes **one batched call** takes milliseconds. Count **round trips and I/O operations**, not just loop iterations ([N+1 queries](../08-modern-python/performance-profiling/README.md)).

```python
import time

def simulated_fetch_one(item):          # pretend each call costs a network round trip
    time.sleep(0.002)
    return item * 2

def simulated_fetch_batch(items):       # one round trip for the whole batch
    time.sleep(0.002)
    return [i * 2 for i in items]

items = list(range(100))
t = time.perf_counter(); [simulated_fetch_one(i) for i in items]; one_by_one = time.perf_counter() - t
t = time.perf_counter(); simulated_fetch_batch(items); batched = time.perf_counter() - t
print(one_by_one > batched * 50)        # True: same "O(n)" loop, 100x fewer round trips
```

## 5. Choosing between algorithms in practice

A decision checklist:

1. **What is the realistic maximum `n`?** (100? 10^5? 10^9?) If small, simplicity wins.
2. **How often will it run?** (once vs millions of times; hot path vs cold path)
3. **What are the constraints?** (memory limit, latency target, worst-case guarantee needed?)
4. **What do the inputs look like?** (nearly sorted? many duplicates? skewed? adversarial?)
5. **Rule out hopeless complexity** (`O(n²)` at 10^6, `O(2ⁿ)` at 50) using the step-count tables.
6. **Prototype the simplest approach and measure** with realistic data; profile before optimizing ([performance](../08-modern-python/performance-profiling/README.md)).
7. **Prefer the standard library** (tuned C code) over hand-written loops.
8. **Keep it readable**; document the complexity assumption (`# O(n log n); n is at most 10^5`).

## 6. Hard problems: P, NP and intractability

Some problems have **no known efficient algorithm**. Complexity theory classifies problems by how hard they are to **solve** and to **check**.

| Class | Meaning | Examples |
|-------|---------|----------|
| **P** | solvable in **polynomial time** (`O(nᵏ)`) | sorting, shortest path, searching, multiplication, linear programming |
| **NP** | a proposed solution can be **checked** in polynomial time (finding it may be hard) | Sudoku (check a filled grid quickly), subset sum, factoring |
| **NP-complete** | the hardest problems in NP: if any one has a fast solution, **all** of NP does | travelling salesman (decision version), boolean satisfiability (SAT), knapsack (decision), graph coloring, Hamiltonian path |
| **NP-hard** | at least as hard as NP-complete (may not even be checkable fast) | the optimization version of travelling salesman |

The famous open question **P vs NP**: is every problem whose solution can be *checked* quickly also *solvable* quickly? Most experts believe **no** (a $1 million Clay Millennium Prize problem).

### Checking is easy, finding is hard: subset sum

```python
from itertools import combinations

def verify_subset_sum(numbers, subset, target):
    """Checking a proposed answer is fast: O(n)."""
    return sum(subset) == target and all(x in numbers for x in subset)

def find_subset_sum(numbers, target):
    """Finding an answer by brute force tries up to 2^n subsets: exponential."""
    for size in range(len(numbers) + 1):
        for subset in combinations(numbers, size):
            if sum(subset) == target:
                return list(subset)
    return None

numbers = [3, 34, 4, 12, 5, 2]
answer = find_subset_sum(numbers, 9)
print(answer, verify_subset_sum(numbers, answer, 9))          # [4, 5] True

import time
for n in (10, 15, 20, 22):
    nums = list(range(1, n + 1))
    t = time.perf_counter(); find_subset_sum(nums, sum(nums) + 1); elapsed = time.perf_counter() - t   # impossible target forces the full search
    print(f"n={n}  subsets checked = {2 ** n:>9,}  time = {elapsed:.3f}s")
# time roughly doubles for each +1 on n (exponential growth)
```

### What to do with NP-hard problems in practice

1. **Check whether `n` is small**: brute force or backtracking with pruning may be enough (`n <= 20-25`).
2. **Exploit structure**: special cases are often easy (shortest path is in P even though longest simple path is NP-hard).
3. **Dynamic programming** gives **pseudo-polynomial** solutions for some (knapsack `O(n · W)`: fast when the capacity `W` is small).
4. **Approximation algorithms** give provably near-optimal answers (a greedy 2-approximation for vertex cover).
5. **Heuristics and metaheuristics**: nearest neighbor, local search, simulated annealing, genetic algorithms: good answers fast, no guarantee.
6. **Solvers**: SAT solvers, integer-programming (OR-Tools, Gurobi), constraint programming handle surprisingly large real instances.
7. **Relax the problem** or accept randomness/approximation.

```python
import random, math

def tour_length(points, order):
    return sum(math.dist(points[order[i]], points[order[(i + 1) % len(order)]]) for i in range(len(order)))

def nearest_neighbor_tour(points):
    """A fast heuristic for the travelling salesman problem: always go to the closest unvisited city. O(n²)."""
    unvisited = set(range(1, len(points)))
    order = [0]
    while unvisited:
        last = points[order[-1]]
        nxt = min(unvisited, key=lambda i: math.dist(last, points[i]))
        order.append(nxt)
        unvisited.remove(nxt)
    return order

random.seed(3)
cities = [(random.random() * 100, random.random() * 100) for _ in range(200)]
heuristic = tour_length(cities, nearest_neighbor_tour(cities))
random_order = tour_length(cities, random.sample(range(200), 200))
print(heuristic < random_order / 5)               # True: instant and far better than random (not optimal, typically 20-25% above optimal)
```

The brute-force optimum for 200 cities would need `199!/2` tours: more than the number of atoms in the universe. The heuristic runs in milliseconds and is good enough for most uses.

### Undecidable problems

Some problems have **no algorithm at all**. The classic: the **halting problem** ("will this program ever stop?") is **undecidable** (Alan Turing, 1936). So tools like perfect bug detectors or "does this code ever loop forever?" cannot exist in general; practical tools use approximations (linters, type checkers, fuzzers) and accept false alarms or misses.

## 7. Practical complexity limits (rules of thumb)

| Technique | Realistic `n` |
|-----------|---------------|
| `O(n!)` brute force | up to about 10 |
| `O(2ⁿ)` brute force / bitmask DP | up to about 20-25 |
| `O(n³)` | up to about 500-1,000 |
| `O(n²)` | up to about 10,000-50,000 (Python), a few hundred thousand (compiled) |
| `O(n log n)` | up to about 10^6-10^7 |
| `O(n)` | up to about 10^7-10^8 (Python 10^7 loop iterations take seconds) |
| `O(log n)` / `O(1)` | effectively unlimited |

(See the [constraint-to-complexity table](../09-interview-playbook/problem-solving-patterns/README.md) for interviews.)

## 8. Two real-world examples

**Example 1: A route planner for delivery drivers.** A logistics company needs good routes for 40 stops per van. Exact optimization (travelling salesman) is NP-hard: `40!` possibilities. They use a **heuristic** (nearest neighbor), improve it with **2-opt local search**, and cap the run at one second. Routes are within a few percent of optimal and recompute instantly when an order changes. A guaranteed-optimal answer was never necessary; a fast, nearly optimal one saves millions in fuel.

**Example 2: "It is O(n log n), so it is fine," but it was not.** A team computed distances between 5,000 products with an `O(n²)` method and replaced it with a clever `O(n log n)` tree structure. On their 5,000 items the tree version was *slower*: constants and cache misses dominated, and it was much harder to maintain. They reverted to a simple NumPy matrix operation (`O(n²)` but vectorized) which ran in 80 ms. Lesson: **measure at your real `n`**.

## 9. Common mistakes

- Choosing a complicated asymptotically faster algorithm for small `n` (or cold code).
- Ignoring I/O and network costs, which dwarf CPU loops.
- Believing Big-O predicts exact speed (it does not; it predicts *growth*).
- Optimizing without measuring (the real bottleneck is elsewhere).
- Trying to solve an NP-hard problem exactly at large `n` instead of approximating.
- Treating "average case O(1)" as a hard guarantee for real-time systems.
- Forgetting that a bad constant factor (Python loop vs C-implemented built-in) is a 10-100x difference.

## 10. Practice

1. For which input sizes does insertion sort beat merge sort in your measurement? Repeat with a nearly sorted list.
2. An `O(n)` algorithm makes one 20 ms API call per item with `n = 500`. A batched version makes 5 calls. Compare total times.
3. Given the subset sum brute force, estimate the time for `n = 30` from the time at `n = 22`.
4. List which of these are known to be in P: sorting; shortest path; subset sum; primality testing; Hamiltonian path.
5. Design a heuristic for the knapsack problem and compare it with the exact DP on random instances.
6. Explain why verifying a Sudoku solution is easy but solving one in general is believed hard.

<details>
<summary>Solutions</summary>

**1.** On many machines insertion sort wins up to roughly `n = 30-100` on random data and for much larger `n` on nearly sorted data (it is `O(n)` there).
```python
nearly = list(range(2000)); nearly[10], nearly[1500] = nearly[1500], nearly[10]
print(best_time(insertion_sort, nearly) < best_time(merge_sort, nearly))      # True: nearly sorted data favors insertion sort
```

**2.** One-per-item: `500 x 20 ms = 10 s`; batched: `5 x 20 ms = 0.1 s` (100x faster); same Big-O in `n` for the local loop, very different I/O count.

**3.** Time roughly doubles per +1: from 22 to 30 is `2^8 = 256` times longer.

**4.** In P: sorting, shortest path (Dijkstra/BFS), primality testing (AKS, in practice Miller-Rabin). Not known to be in P: subset sum (NP-complete, though pseudo-polynomial DP exists), Hamiltonian path (NP-complete).

**5.**
```python
def knapsack_exact(items, capacity):
    best = [0] * (capacity + 1)
    for value, weight in items:
        for w in range(capacity, weight - 1, -1):
            best[w] = max(best[w], best[w - weight] + value)
    return best[capacity]

def knapsack_greedy(items, capacity):
    total_value = total_weight = 0
    for value, weight in sorted(items, key=lambda it: it[0] / it[1], reverse=True):     # best value per weight first
        if total_weight + weight <= capacity:
            total_value += value; total_weight += weight
    return total_value

random.seed(4)
items = [(random.randint(10, 100), random.randint(5, 40)) for _ in range(60)]
exact, greedy = knapsack_exact(items, 300), knapsack_greedy(items, 300)
print(exact, greedy, round(greedy / exact, 3))             # greedy is usually within a few percent of the exact optimum
```

**6.** A filled 9x9 grid can be checked in one pass over rows, columns and boxes (`O(n²)` for an `n x n` board), but finding a valid filling may require exploring exponentially many possibilities (generalized Sudoku is NP-complete). (In practice, puzzle-sized instances are solved quickly with backtracking and constraint propagation.)

</details>

## 11. Check yourself

1. Why can an `O(n²)` algorithm beat an `O(n log n)` one on small inputs?
2. Why do arrays often outperform linked lists despite equal Big-O for scanning?
3. Which cost often dominates real programs more than CPU loops?
4. What do P, NP and NP-complete mean in plain words?
5. What do you do when a problem is NP-hard and `n` is large?
6. Why can no program decide whether any program halts?

<details>
<summary>Answers</summary>

1. Constants and overhead dominate for small `n`; asymptotic advantage only appears beyond the crossover size.
2. Contiguous memory is cache friendly and prefetchable, while linked nodes scatter memory and cause cache misses.
3. I/O: disk and network round trips (and memory access patterns).
4. P: solvable quickly; NP: a proposed answer can be verified quickly; NP-complete: the hardest problems in NP (a fast algorithm for one would give fast algorithms for all).
5. Use approximation algorithms, heuristics, dynamic programming for special cases, solvers, or relax the problem.
6. Turing proved the halting problem undecidable: any such decider could be used to build a program that contradicts itself.

</details>

[Back to complexity](README.md) · Previous: [complexity of Python operations](07-python-operations-cheat-sheet.md)
