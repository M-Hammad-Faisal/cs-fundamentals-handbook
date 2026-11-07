# Space Complexity: How Much Memory Does an Algorithm Use?

**Prerequisites:** [analyzing loops and recursion](04-analyzing-loops-and-recursion.md), [memory, stack and heap](../00-foundations/computer-basics/memory-stack-heap.md). **You will learn:** what space complexity measures, the difference between input space and auxiliary space, how recursion consumes the call stack, in-place algorithms, the time-space trade-off (caches, hash sets, precomputation), and how to measure memory in Python.

## 1. In plain words

Time is not the only resource. Every algorithm also needs **memory (space)**: variables, copies of data, tables, the call stack. **Space complexity** describes how the memory an algorithm needs grows with the input size `n`, using the same Big-O notation.

Analogy: solving a jigsaw puzzle. The puzzle pieces are the **input** (you cannot avoid them). Some strategies need a huge extra table to lay out sorted groups of pieces (**extra space**); others work directly on the pieces in place with just a few notes (**constant extra space**).

## 2. Two ways to count space

| Term | Meaning | Example |
|------|---------|---------|
| **Total space** | everything: the input **plus** extra memory | a list of `n` numbers plus a copy: `2n` |
| **Auxiliary space** | only the **extra** memory the algorithm allocates beyond the input | the copy: `n` |

When people ask for "the space complexity" of an algorithm they usually mean the **auxiliary space** (and mention if they include input).

| Auxiliary space | Meaning | Typical example |
|-----------------|---------|-----------------|
| `O(1)` | constant: a few variables | finding the max, swapping two items, two pointers |
| `O(log n)` | grows slowly | recursive binary search (call stack), quicksort stack (average) |
| `O(n)` | proportional to input | making a copy, building a set, merge sort's buffer, BFS queue |
| `O(n²)` | grows with the square | a full `n x n` table (some DP, adjacency matrix) |

## 3. Examples: counting auxiliary space

```python
def max_of(items):                           # O(1) extra space: only `best` and a loop variable
    best = items[0]
    for x in items:
        if x > best:
            best = x
    return best

def reversed_copy(items):                    # O(n) extra space: a whole new list
    return items[::-1]

def reverse_in_place(items):                 # O(1) extra space: swaps inside the same list
    lo, hi = 0, len(items) - 1
    while lo < hi:
        items[lo], items[hi] = items[hi], items[lo]
        lo, hi = lo + 1, hi - 1
    return items

def pairs(items):                            # O(n²) extra space: n*n tuples stored
    return [(a, b) for a in items for b in items]

nums = list(range(1000))
print(max_of(nums), len(reversed_copy(nums)), reverse_in_place(nums[:5]), len(pairs(range(30))))
# 999 1000 [4, 3, 2, 1, 0] 900
```

Both reversal functions take `O(n)` **time**, but one needs `O(n)` extra memory and the other `O(1)`: space complexity captures that difference.

### Measuring memory in Python

```python
import sys, tracemalloc

def peak_memory(fn, *args):
    tracemalloc.start()
    result = fn(*args)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak

n = 200_000
data = list(range(n))
print(peak_memory(max_of, data) < 2_000)                       # True   (O(1): a tiny constant amount, independent of n)
print(peak_memory(reversed_copy, data) > 1_000_000)            # True   (O(n): about 8 bytes per element for the new list)
print(peak_memory(reverse_in_place, data) < 2_000)             # True   (O(1))
```

(`sys.getsizeof` measures one object shallowly; `tracemalloc` measures allocations during a run: see [performance and profiling](../08-modern-python/performance-profiling/README.md).)

## 4. The call stack counts: recursion uses space

Every active recursive call holds a **stack frame** ([call stack](../00-foundations/computer-basics/memory-stack-heap.md)). So a recursion of depth `d` uses `O(d)` space *even if it allocates nothing else*.

```python
def sum_to_recursive(n):                     # depth n: O(n) stack space
    return 0 if n == 0 else n + sum_to_recursive(n - 1)

def sum_to_loop(n):                          # O(1) space
    total = 0
    for i in range(1, n + 1):
        total += i
    return total

print(sum_to_recursive(500), sum_to_loop(500))                  # 125250 125250
try:
    sum_to_recursive(50_000)                                    # O(n) frames: exceeds Python's recursion limit
except RecursionError:
    print("recursion depth is a space cost too:", sum_to_loop(50_000))       # 1250025000
```

Depth versus space:

| Algorithm | Recursion depth | Stack space |
|-----------|-----------------|-------------|
| Linear recursion (`f(n-1)`) | `n` | `O(n)` |
| Binary search (recursive) | `log n` | `O(log n)` |
| Merge sort | `log n` (plus `O(n)` buffer) | `O(n)` overall |
| Quicksort (average, good pivots) | `log n` | `O(log n)` |
| Quicksort worst case | `n` | `O(n)` |
| Tree DFS | tree height `h` (`log n` balanced, `n` degenerate) | `O(h)` |
| Naive Fibonacci | `n` (the two calls do not both go deep at once) | `O(n)` stack, though time is exponential |

**Tail recursion** can use `O(1)` stack in languages that optimize it, but **Python does not**, so convert deep recursion to loops or use an explicit stack.

## 5. In-place algorithms

An algorithm is **in place** if it uses `O(1)` auxiliary space (it modifies the input directly rather than building new structures).

```python
def remove_evens_new_list(nums):             # O(n) extra space
    return [x for x in nums if x % 2]

def remove_evens_in_place(nums):             # O(1) extra space: write pointer + read pointer
    write = 0
    for read in range(len(nums)):
        if nums[read] % 2:
            nums[write] = nums[read]
            write += 1
    del nums[write:]
    return nums

a = [1, 2, 3, 4, 5, 6, 7]
print(remove_evens_new_list(a), remove_evens_in_place(a[:]))    # [1, 3, 5, 7] [1, 3, 5, 7]
```

Examples of in-place sorts: insertion, selection, bubble, heap sort, (in-place) quicksort. Merge sort needs `O(n)` extra for merging. In-place algorithms **mutate their input**, which may surprise callers; document it ([mutation and references](../00-foundations/computer-basics/memory-stack-heap.md)).

## 6. The time-space trade-off

Memory can often be **traded for speed** (and vice versa). Recognize the trade and choose deliberately.

| Spend memory to save time | Spend time to save memory |
|---------------------------|---------------------------|
| Cache/memoize results | Recompute instead of storing |
| Store a hash set to test membership in `O(1)` | Scan the data each time (`O(n)`) |
| Precompute a lookup table or prefix sums | Compute on demand |
| Build an index | Full scan |
| Keep decompressed data in memory | Compress and decompress on use |

```python
import time

# Trade 1: a set uses O(n) memory to answer "is x present?" in O(1) instead of O(n)
haystack = list(range(50_000))
needles = list(range(0, 100_000, 7))
t = time.perf_counter(); hits_list = sum(n in haystack for n in needles); slow = time.perf_counter() - t
lookup = set(haystack)                                         # extra O(n) space
t = time.perf_counter(); hits_set = sum(n in lookup for n in needles); fast = time.perf_counter() - t
print(hits_list == hits_set, slow > fast * 100)                # True True

# Trade 2: memoization turns exponential time into linear time at the cost of O(n) space
from functools import lru_cache

def fib_slow(n): return n if n < 2 else fib_slow(n - 1) + fib_slow(n - 2)

@lru_cache(maxsize=None)
def fib_fast(n): return n if n < 2 else fib_fast(n - 1) + fib_fast(n - 2)

t = time.perf_counter(); fib_slow(27); slow = time.perf_counter() - t
t = time.perf_counter(); fib_fast(27); fast = time.perf_counter() - t
print(slow > fast * 1000)                                      # True: O(2^n) time versus O(n) time with O(n) cache

# Trade 3: the opposite: O(1)-space two-pointer solution versus O(n)-space hash set (find a pair summing to target in SORTED data)
def pair_sum_sorted(nums, target):                             # O(n) time, O(1) space (needs sorted input)
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        s = nums[lo] + nums[hi]
        if s == target: return True
        lo, hi = (lo + 1, hi) if s < target else (lo, hi - 1)
    return False

def pair_sum_hash(nums, target):                               # O(n) time, O(n) space (any order)
    seen = set()
    for x in nums:
        if target - x in seen: return True
        seen.add(x)
    return False

nums = list(range(0, 2000, 3))
print(pair_sum_sorted(nums, 1500), pair_sum_hash(nums, 1500), pair_sum_sorted(nums, 7), pair_sum_hash(nums, 7))     # True True False False
```

### Space-saving techniques

- **Generators and streaming:** process one item at a time instead of building a list of everything (`O(1)` instead of `O(n)`).
- **Rolling variables/arrays:** if a DP needs only the previous row, keep two rows instead of the whole table (`O(n²)` becomes `O(n)`).
- **Compact types:** `array`/NumPy instead of lists of Python ints; bit sets; `__slots__`.
- **Sharing:** interning, flyweights ([Flyweight pattern](../04-oop/design-patterns/structural/flyweight.md)).
- **Approximate structures:** Bloom filters and HyperLogLog trade exactness for tiny memory.

```python
# Streaming versus building a list: same answer, different space
def sum_squares_list(n):   return sum([i * i for i in range(n)])      # O(n) space: the list
def sum_squares_stream(n): return sum(i * i for i in range(n))        # O(1) space: a generator

n = 300_000
print(sum_squares_list(n) == sum_squares_stream(n))                    # True
print(peak_memory(sum_squares_stream, n) < peak_memory(sum_squares_list, n) / 100)     # True

# DP with rolling rows: the number of paths in a grid with O(cols) space instead of O(rows * cols)
def grid_paths(rows, cols):
    row = [1] * cols
    for _ in range(rows - 1):
        for j in range(1, cols):
            row[j] += row[j - 1]
    return row[-1]
print(grid_paths(3, 7), grid_paths(18, 18))                            # 28 2333606220
```

## 7. Typical space costs of familiar algorithms and structures

| Item | Auxiliary space |
|------|-----------------|
| Linear/binary search (iterative) | `O(1)` |
| Bubble, selection, insertion, heap sort | `O(1)` |
| Merge sort | `O(n)` |
| Quicksort | `O(log n)` average (stack) |
| Counting sort | `O(n + k)` |
| BFS | `O(n)` queue (can be the widest level) |
| DFS | `O(h)` stack/recursion (`h` = depth) |
| Hash set/dict of `n` items | `O(n)` |
| Memoized recursion | `O(n)` table + stack |
| DP table `n x m` | `O(n · m)` (often reducible to one row) |
| Adjacency matrix | `O(V²)`; adjacency list `O(V + E)` |

## 8. Two real-world examples

**Example 1: Processing a 20 GB log file.** Reading it into a list (`lines = f.readlines()`) needs about 20 GB of RAM: `O(n)` space, and the process dies. Iterating (`for line in f:`) keeps `O(1)` memory per line, so the same machine handles the file with a few megabytes. Space complexity decides what is possible at all.

**Example 2: Mobile apps and memory budgets.** A photo-filter app needs the output image (`n` pixels). A naive implementation copies the image at every filter stage (`O(k · n)` for `k` stages: on a 12-megapixel photo with 10 filters that is over 500 MB), while an in-place or streaming pipeline processes tiles using `O(1)` extra memory per stage. Operating systems kill apps that exceed their budget.

## 9. Common mistakes

- Reporting only time and forgetting memory.
- Forgetting that recursion depth is stack space (and that Python limits it).
- Counting the input as extra space (or ignoring that you made a copy with `list(x)` or slicing).
- Hidden copies: `x[:]`, `sorted(x)`, `list(x)`, string slicing/concatenation, `+` on lists, passing around slices.
- Using a list where a generator would do.
- Trading `O(n)` memory for a small speed-up when memory is the scarce resource (or the reverse).
- Assuming Python's memory use equals the data size (each `int` object costs 28+ bytes; lists store pointers).

## 10. Practice

1. State the auxiliary space of: summing a list, building a squares list, `sorted(items)`, in-place `items.sort()`, recursive factorial, iterative factorial, BFS on a graph.
2. Rewrite `is_palindrome` to use `O(1)` extra space instead of reversing a copy.
3. Compute the number of lattice paths with two-row (or one-row) space; compare with the full table.
4. Show with `tracemalloc` that a generator pipeline over a million items uses far less memory than the equivalent list pipeline.
5. A recursive depth-first traversal of a degenerate tree (a chain of 100,000 nodes) crashes. Why, and how do you fix it?
6. Explain the trade-off in "store every Fibonacci number" versus "keep the last two".

<details>
<summary>Solutions</summary>

**1.** `O(1)`, `O(n)`, `O(n)` (a new list), `O(1)` (Timsort uses up to `O(n)` temporary space but in-place conceptually; say "`O(n)` worst case"), `O(n)` (stack), `O(1)`, `O(n)` (queue; bounded by the widest level).

**2.**
```python
def is_palindrome_o1(s):
    lo, hi = 0, len(s) - 1
    while lo < hi:
        while lo < hi and not s[lo].isalnum(): lo += 1
        while lo < hi and not s[hi].isalnum(): hi -= 1
        if s[lo].lower() != s[hi].lower(): return False
        lo, hi = lo + 1, hi - 1
    return True
print(is_palindrome_o1("A man, a plan, a canal: Panama"), is_palindrome_o1("hello"))       # True False
```

**3.** See `grid_paths` above (one row of `cols` numbers): `O(cols)` space versus `O(rows · cols)` for a full table.

**4.**
```python
def pipeline_list(n):
    squares = [i * i for i in range(n)]
    evens = [x for x in squares if x % 2 == 0]
    return sum(evens)
def pipeline_gen(n):
    return sum(x for x in (i * i for i in range(n)) if x % 2 == 0)
n = 400_000
print(pipeline_list(n) == pipeline_gen(n), peak_memory(pipeline_gen, n) < peak_memory(pipeline_list, n) / 100)    # True True
```

**5.** The recursion depth equals the tree height (100,000) which exceeds the call-stack limit; use an explicit stack (iteration): `stack = [root]; while stack: node = stack.pop(); ...`.

**6.** Storing all numbers takes `O(n)` memory (useful if you need them again); keeping only the last two takes `O(1)` memory and is enough for computing the next value: choose by what you need later.

</details>

## 11. Check yourself

1. What is auxiliary space?
2. Why does recursion count toward space?
3. What does "in place" mean?
4. Name two time-space trade-offs.
5. How can a generator reduce space complexity?

<details>
<summary>Answers</summary>

1. The extra memory an algorithm allocates beyond the input.
2. Each active call occupies a stack frame, so depth `d` costs `O(d)` space.
3. It uses `O(1)` extra memory, modifying the input directly.
4. Memoization/caching (more memory, less time); hash sets and indexes (memory for fast lookup); precomputed tables; or the reverse: recomputing to save memory.
5. It produces items lazily one at a time instead of storing all of them in memory.

</details>

[Back to complexity](README.md) · Previous: [analyzing loops and recursion](04-analyzing-loops-and-recursion.md) · Next: [best, average, worst and amortized](06-cases-and-amortized-analysis.md)
