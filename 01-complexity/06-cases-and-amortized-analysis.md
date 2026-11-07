# Best, Average, Worst Case and Amortized Analysis

**Prerequisites:** [Big-O, Omega and Theta](03-big-o-omega-theta.md), [analyzing loops and recursion](04-analyzing-loops-and-recursion.md). **You will learn:** why one algorithm can have several running times, how to find the best, average and worst case, why the **worst case** is usually the one we report, what **amortized analysis** means (and why `list.append` is "O(1)" even though some appends are expensive), and when randomized algorithms give guarantees.

## 1. In plain words

Some algorithms take different amounts of time on different inputs **of the same size**. Looking for your keys: if they are in the first pocket you check, great; if they are in the last place you look, or lost, you check everything. Same method, very different effort.

| Case | Question | Typical use |
|------|----------|-------------|
| **Best case** | What is the cheapest input of size `n`? | rarely useful alone (can be misleading) |
| **Worst case** | What is the most expensive input of size `n`? | **the safe default**: a guarantee |
| **Average case** | What is the expected cost over typical (random) inputs? | realistic performance; needs a probability model |
| **Amortized** | What is the **average cost per operation** over a long sequence, even if one operation is occasionally expensive? | data structures (dynamic arrays, hash tables) |

## 2. Linear search: all three cases

```python
def linear_search(items, target):
    comparisons = 0
    for index, value in enumerate(items):
        comparisons += 1
        if value == target:
            return index, comparisons
    return -1, comparisons

data = list(range(1000))
print(linear_search(data, 0))          # (0, 1)       best case: found immediately            -> 1 comparison: Θ(1)
print(linear_search(data, 999))        # (999, 1000)  worst case: found at the end            -> n comparisons: Θ(n)
print(linear_search(data, -1))         # (-1, 1000)   worst case: not present                 -> n comparisons

# Average case, if the target is equally likely to be at any position: (1 + 2 + ... + n) / n = (n + 1) / 2
total = sum(linear_search(data, t)[1] for t in data)
print(total / len(data), (len(data) + 1) / 2)       # 500.5 500.5   -> about n/2: still Θ(n)
```

Best case `Θ(1)`, worst case `Θ(n)`, average case `Θ(n)` (the `1/2` is a constant). Note that **average does not mean better in Big-O terms here**.

## 3. When the cases really differ: insertion sort and quicksort

**Insertion sort** (take each item and slide it left into place):

```python
def insertion_sort(items):
    items = items[:]
    shifts = 0
    for i in range(1, len(items)):
        key, j = items[i], i - 1
        while j >= 0 and items[j] > key:
            items[j + 1] = items[j]                 # shift larger items right
            j -= 1
            shifts += 1
        items[j + 1] = key
    return items, shifts

n = 1000
already_sorted = list(range(n))
reversed_input = list(range(n, 0, -1))
import random
random.seed(5)
shuffled = random.sample(range(n), n)
print(insertion_sort(already_sorted)[1])            # 0        best case: Θ(n) (just n comparisons, no shifts)
print(insertion_sort(reversed_input)[1])            # 499500   worst case: n(n-1)/2 -> Θ(n²)
print(insertion_sort(shuffled)[1])                  # 253350: average ≈ n²/4 -> Θ(n²)
```

The best case is linear (already sorted data) which is why insertion sort is a great choice for **nearly sorted** data (and why Python's Timsort uses it for small runs).

**Quicksort** picks a pivot, partitions into smaller and larger, and recurses:

```python
def quicksort_comparisons(items, pivot_rule):
    comparisons = 0
    def sort(lst):
        nonlocal comparisons
        if len(lst) <= 1:
            return lst
        pivot = pivot_rule(lst)
        smaller, equal, larger = [], [], []
        for x in lst:
            comparisons += 1
            (smaller if x < pivot else equal if x == pivot else larger).append(x)
        return sort(smaller) + equal + sort(larger)
    sort(items)
    return comparisons

first_item = lambda lst: lst[0]                              # a naive pivot choice
middle_item = lambda lst: lst[len(lst) // 2]
random_item = lambda lst: random.choice(lst)

n = 900
random.seed(2)
shuffled = random.sample(range(n), n)
print(quicksort_comparisons(shuffled, first_item))           # 12517: about n log2 n on random data: Θ(n log n)
print(quicksort_comparisons(list(range(n)), first_item))     # 405449: about n²/2 = WORST case on already-sorted data with a first-item pivot: Θ(n²)
print(quicksort_comparisons(list(range(n)), middle_item))    # 7598: a better pivot rule avoids that worst case
print(quicksort_comparisons(list(range(n)), random_item))    # 10141: a RANDOM pivot makes the worst case extremely unlikely on any input
```

Quicksort is `Θ(n log n)` on average but `Θ(n²)` in the worst case; **randomizing the pivot** makes the expected time `O(n log n)` for *every* input (the "worst case" becomes astronomically unlikely).

## 4. Why we usually report the worst case

1. It is a **guarantee**: "this will never take longer than...". Systems with deadlines (a web request, a game frame, a medical device) must hold under the worst input.
2. The **average** needs assumptions about input distribution ("random data") that real inputs may violate (sorted data, repeated keys, attacker-chosen inputs).
3. The **worst case is often the average case** (linear search, many algorithms).
4. Adversaries exploit worst cases (algorithmic-complexity attacks: crafted inputs that make a hash table or regex take quadratic or exponential time).

Report all three when they differ ("quicksort: `O(n log n)` average, `O(n²)` worst; with random pivots the worst case is negligible").

## 5. Amortized analysis

### The puzzle

`list.append(x)` is documented as `O(1)`. But a Python list is a **dynamic array**: when it is full, it must allocate a bigger block and **copy every item** (`O(n)`). How can `append` be `O(1)`?

Because the expensive copy happens **rarely**, and its cost is **spread over many cheap appends**. The **amortized cost** is the total cost of a sequence of `m` operations divided by `m`.

### Doubling strategy, simulated

```python
class DynamicArray:
    """A simplified dynamic array that doubles its capacity when full, counting every element copy."""
    def __init__(self):
        self.capacity, self.size = 1, 0
        self.data = [None] * self.capacity
        self.copies = 0                                   # element copies caused by resizing

    def append(self, value):
        if self.size == self.capacity:                    # full: allocate double and copy everything over
            self.capacity *= 2
            new_data = [None] * self.capacity
            for i in range(self.size):
                new_data[i] = self.data[i]
                self.copies += 1
            self.data = new_data
        self.data[self.size] = value
        self.size += 1

for n in (10, 100, 1_000, 100_000):
    arr = DynamicArray()
    for i in range(n):
        arr.append(i)
    total_work = n + arr.copies                            # n writes plus the copies
    print(f"n={n:>7,}  copies={arr.copies:>7,}  total work={total_work:>8,}  work per append = {total_work / n:.2f}")
# n=     10  copies=     15  total work=      25  work per append = 2.50
# n=    100  copies=    127  total work=     227  work per append = 2.27
# n=  1,000  copies=  1,023  total work=   2,023  work per append = 2.02
# n=100,000  copies=131,071  total work= 231,071  work per append = 2.31
```

**The average work per append stays below about 3 no matter how big `n` is**: that constant is the **amortized `O(1)`** cost. The copies add up to `1 + 2 + 4 + 8 + ... + n < 2n` (a geometric series: [sums](../00-foundations/math-for-cs/sums-and-recurrences.md)).

```text
append #:  1  2  3  4  5  6  7  8  9 ... 16 17
cost:      1  2  3  1  5  1  1  1  9 ... 1  17     <- expensive appends at powers of two
                                      average of any prefix stays about 2-3
```

### Why doubling (and not "add 10 slots") matters

```python
class GrowByConstant(DynamicArray):
    """Grows by a fixed number of slots instead of doubling: the copies add up to quadratic work."""
    def append(self, value):
        if self.size == self.capacity:
            self.capacity += 10                           # fixed increment
            new_data = [None] * self.capacity
            for i in range(self.size):
                new_data[i] = self.data[i]; self.copies += 1
            self.data = new_data
        self.data[self.size] = value; self.size += 1

for cls in (DynamicArray, GrowByConstant):
    arr = cls()
    for i in range(20_000):
        arr.append(i)
    print(cls.__name__, arr.copies)
# DynamicArray 32767            -> O(n) total copies: amortized O(1) per append
# GrowByConstant 19992000       -> about n²/20 copies: O(n) per append: quadratic overall
```

Growing by a **constant factor** (2x, or CPython's roughly 1.125x plus overallocation) gives amortized `O(1)`; growing by a constant **amount** gives `O(n)` per append. Real implementations use factors like 1.5x-2x.

### Three ways to argue amortized cost

1. **Aggregate method:** total cost of `m` operations divided by `m` (as above): copies sum to less than `2n`, so the average is less than 3.
2. **Accounting (banker's) method:** charge each append a fixed "price" (say 3 coins); cheap appends spend 1 coin and **save** 2 for the future; an expensive resize is paid for by the savings stored on the items being copied.
3. **Potential method:** define a "potential energy" function of the data structure state whose increase pays for later expensive operations (used in advanced proofs).

### Other amortized examples

| Structure / operation | Worst case of one operation | Amortized |
|-----------------------|-----------------------------|-----------|
| Dynamic array append | `O(n)` (resize) | `O(1)` |
| Hash table insert (with resizing) | `O(n)` (rehash everything) | `O(1)` average |
| Stack/queue with a "two stacks" queue | `O(n)` for one dequeue (reverse the stack) | `O(1)` |
| Splay trees, union-find with path compression | one operation can be slow | `O(log n)` or near `O(1)` amortized |
| `str` building with `+=` | `O(n)` per concatenation in general | (use `"".join`: `O(n)` total) |

A queue built from two stacks:

```python
class QueueFromTwoStacks:
    def __init__(self):
        self.inbox, self.outbox, self.moves = [], [], 0
    def enqueue(self, x):
        self.inbox.append(x)                                # O(1)
    def dequeue(self):
        if not self.outbox:                                 # only when empty: reverse the inbox into the outbox
            while self.inbox:
                self.outbox.append(self.inbox.pop())
                self.moves += 1
        return self.outbox.pop()

q = QueueFromTwoStacks()
for i in range(1000):
    q.enqueue(i)
out = [q.dequeue() for _ in range(1000)]
print(out[:3], q.moves)             # [0, 1, 2] 1000    -> one dequeue cost 1000 moves, but each item moved only ONCE: amortized O(1)
```

### Amortized is not average-case

- **Average case** averages over **random inputs** (probability).
- **Amortized** averages over a **sequence of operations** on the *same* structure, with **no probability**: it is a worst-case guarantee for the whole sequence.

## 6. Measuring `append` in real Python

```python
import time

def time_appends(n):
    items = []
    start = time.perf_counter()
    for i in range(n):
        items.append(i)
    return time.perf_counter() - start

small, big = time_appends(200_000), time_appends(2_000_000)
print(round(big / small, 1))                                # 10.1 (10x the appends take about 10x the time): linear total => O(1) amortized each
```

## 7. Two real-world examples

**Example 1: Why a web server's hash tables are fast on average but rarely stall.** A hash table doubles its bucket array when it gets too full and rehashes every key (`O(n)` for that one insert). Because doubling is rare, inserts are amortized `O(1)`. For latency-sensitive systems (real-time games, trading) that occasional stall matters, so they pre-size the table, use incremental rehashing (Redis spreads a resize over many operations), or choose structures with predictable worst cases. The distinction between amortized and worst-case per operation drives real engineering choices.

**Example 2: Choosing quicksort variants and the introsort trick.** C++'s `std::sort` and many libraries use **introsort**: quicksort that switches to heap sort if recursion gets too deep, guaranteeing `O(n log n)` worst case while keeping quicksort's fast average. Knowing the cases explains why a "fast on average" algorithm is wrapped in a safety net.

## 8. Common mistakes

- Reporting the best case as if it were typical ("insertion sort is `O(n)`").
- Confusing average case (probability over inputs) with amortized (guarantee over a sequence).
- Assuming "average case" is always better than worst case in Big-O (linear search average is still `Θ(n)`).
- Forgetting that amortized `O(1)` still allows an occasional `O(n)` operation (a problem for hard real-time systems).
- Ignoring adversarial inputs when relying on average-case behavior of hashing or pivot selection.
- Growing a buffer by a fixed amount instead of a factor.

## 9. Practice

1. Give best, worst and average case comparisons for linear search on 1,000 items (target equally likely at any position).
2. Which input makes insertion sort fastest? Slowest? How many comparisons for each with `n = 8`?
3. Why does a random pivot protect quicksort from sorted input?
4. Simulate a dynamic array that grows by factor 1.5 and compute copies per append for `n = 100,000`.
5. Explain amortized `O(1)` using the "two stacks queue".
6. A function builds a string with `s += piece` for 100,000 pieces. What is the complexity and what is the fix?

<details>
<summary>Solutions</summary>

**1.** Best 1, worst 1,000, average 500.5 (computed above).

**2.** Fastest: already sorted (`n - 1 = 7` comparisons, 0 shifts); slowest: reversed (`n(n-1)/2 = 28` shifts).
```python
print(insertion_sort(list(range(8)))[1], insertion_sort(list(range(8, 0, -1)))[1])      # 0 28
```

**3.** The pivot is a random element, so for any input (sorted or adversarial) the chance of consistently terrible pivots is vanishingly small; the expected time is `O(n log n)` on all inputs.

**4.**
```python
class GrowBy15(DynamicArray):
    def append(self, value):
        if self.size == self.capacity:
            self.capacity = max(self.capacity + 1, int(self.capacity * 1.5))
            new_data = [None] * self.capacity
            for i in range(self.size):
                new_data[i] = self.data[i]; self.copies += 1
            self.data = new_data
        self.data[self.size] = value; self.size += 1
arr = GrowBy15()
for i in range(100_000):
    arr.append(i)
print(round(arr.copies / 100_000, 2))          # 2.77: still a constant, amortized O(1)
```

**5.** Each element is moved from the inbox to the outbox at most once in its life; `n` enqueues and `n` dequeues cost at most `3n` stack operations in total, so each operation costs `O(1)` amortized even though one dequeue may move `n` items.

**6.** Repeated concatenation can copy the growing string each time: up to `O(n²)` in the worst case (CPython sometimes optimizes it, but do not rely on it). Fix: collect pieces in a list and `"".join(pieces)` (`O(n)`).

</details>

## 10. Check yourself

1. What are the best, worst and average cases of linear search?
2. Why is the worst case the default?
3. What is amortized analysis, and why is `list.append` amortized `O(1)`?
4. How does amortized analysis differ from average-case analysis?
5. What happens to dynamic array append cost if the array grows by a fixed amount instead of doubling?
6. Why do implementations randomize quicksort pivots?

<details>
<summary>Answers</summary>

1. Best: 1 comparison (first item); worst: `n` (last or missing); average about `n/2`.
2. It is a guarantee that holds for any input, and average-case needs assumptions that may not hold.
3. Amortized cost is the total cost of a sequence of operations divided by the number of operations; appends are cheap except the occasional resize, whose cost is spread over many cheap appends, leaving a constant average.
4. Average-case averages over random inputs (a probabilistic statement); amortized averages over a sequence of operations on one structure with no probability, and is a worst-case guarantee for the whole sequence.
5. Total copies become quadratic, so each append costs `O(n)` on average.
6. So that no particular input (such as sorted data) reliably triggers the `O(n²)` worst case.

</details>

[Back to complexity](README.md) · Previous: [space complexity](05-space-complexity.md) · Next: [complexity of Python operations](07-python-operations-cheat-sheet.md)
