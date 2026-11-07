# Counting Steps and Understanding Growth

**Prerequisites:** [what is an algorithm](01-what-is-an-algorithm.md), [exponents and logarithms](../00-foundations/math-for-cs/exponents-and-logarithms.md). **You will learn:** why we count operations instead of seconds, how to count the steps of real code (and let Python count them for you), what "growth" means with a picture, why constants and small terms stop mattering, and how to estimate an algorithm's growth rate **experimentally** with the doubling test.

## 1. In plain words

How fast is a program? "It took 2.3 seconds" is not a useful answer: a faster laptop, a different language, or another program running at the same time changes it. We want a measure that describes the **algorithm itself**. The idea: **count the basic steps** it performs, and see **how that count grows when the input gets bigger**.

Analogy: comparing two ways to find a name in a phone book. Method A: start at page 1 and read every entry. Method B: open the middle, decide left or right, repeat. We do not need a stopwatch to know that for a book with a million names B takes about 20 looks and A up to a million. The *shape of growth* tells the story.

## 2. The simple machine model

To count steps we assume a simple model (the **RAM model**): each of these takes **one step** (one unit of time):

- an arithmetic operation (`+`, `-`, `*`, `//`, `%`),
- a comparison (`<`, `==`),
- an assignment (`x = ...`),
- reading or writing one array/list element by index (`items[i]`),
- a function call/return (overhead only; the work inside is counted separately).

It is a simplification (real operations differ by factors of 2-10), but the *growth* it reveals is the same on every real computer.

### Counting by hand

```python
def sum_list(items):
    total = 0                    # 1 step
    for x in items:              # the loop body runs n times (n = len(items))
        total += x               #   1 step each (an addition and an assignment, call it 1-2)
    return total                 # 1 step
```

Total: `1 + n + 1 = n + 2` steps. We write `T(n) = n + 2`. For `n = 1,000` that is about 1,002 steps; for `n = 1,000,000` about 1,000,002. **The dominant behavior is "about n".**

A nested loop:

```python
def has_duplicate(items):
    for i in range(len(items)):                 # outer: n iterations
        for j in range(i + 1, len(items)):      # inner: n-1, n-2, ..., 1, 0 iterations
            if items[i] == items[j]:            #   1 comparison each
                return True
    return False
```

Worst case (no duplicates): `(n-1) + (n-2) + ... + 1 = n(n-1)/2` comparisons: `T(n) = n²/2 - n/2`. For `n = 1,000` about 500,000; for `n = 1,000,000` about 5 x 10^11. **The dominant behavior is "about n²".**

## 3. Let Python count for you

Instead of counting by hand (and making mistakes), **instrument** the code with a counter. This also verifies your hand analysis.

```python
class Counter:
    """Counts "basic operations" so we can compare algorithms without a stopwatch."""
    def __init__(self):
        self.ops = 0
    def tick(self, n=1):
        self.ops += n

def sum_list_counted(items):
    c = Counter()
    total = 0; c.tick()
    for x in items:
        total += x; c.tick()
    return total, c.ops

def has_duplicate_counted(items):
    c = Counter()
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            c.tick()                                   # one comparison
            if items[i] == items[j]:
                return True, c.ops
    return False, c.ops

for n in (10, 100, 1000):
    data = list(range(n))                              # no duplicates: the worst case
    _, linear_ops = sum_list_counted(data)
    _, quadratic_ops = has_duplicate_counted(data)
    print(f"n={n:>5}  sum: {linear_ops:>5} ops   duplicates: {quadratic_ops:>7} ops   n(n-1)/2 = {n * (n - 1) // 2}")
# n=   10  sum:    11 ops   duplicates:      45 ops   n(n-1)/2 = 45
# n=  100  sum:   101 ops   duplicates:    4950 ops   n(n-1)/2 = 4950
# n= 1000  sum:  1001 ops   duplicates:  499500 ops   n(n-1)/2 = 499500
```

The measured counts match the formulas exactly. Note how a 10x larger input costs **10x** more for the linear algorithm but **about 100x** more for the quadratic one.

## 4. Growth: the shape of the curve

Plot (as a table) the number of steps `T(n)` for several algorithms as `n` doubles:

```python
import math

def growth_table(sizes):
    print(f"{'n':>8} {'log n':>8} {'n':>9} {'n log n':>11} {'n^2':>14} {'2^n':>12}")
    for n in sizes:
        two_n = f"{2 ** n:,}" if n <= 30 else "huge"
        print(f"{n:>8} {math.log2(n):>8.1f} {n:>9,} {n * math.log2(n):>11,.0f} {n * n:>14,} {two_n:>12}")

growth_table([4, 8, 16, 32, 64, 1000])
```

```text
       n    log n         n     n log n            n^2          2^n
       4      2.0         4           8             16           16
       8      3.0         8          24             64          256
      16      4.0        16          64            256       65,536
      32      5.0        32         160          1,024         huge
      64      6.0        64         384          4,096         huge
    1000     10.0     1,000       9,966      1,000,000         huge
```

What each doubling of `n` does:

| Growth | Effect of doubling n | Example |
|--------|----------------------|---------|
| constant | no change | `items[0]` |
| log n | adds one step | binary search |
| n | doubles | scanning a list |
| n log n | slightly more than doubles | good sorting |
| n² | **4 times** | nested loops over the same data |
| n³ | 8 times | three nested loops |
| 2ⁿ | squares the cost (adding **one** to n doubles it) | trying every subset |

A rough ASCII picture (height = steps, width = n):

```text
steps
  │                                       n²   ╱
  │                                          ╱
  │                                       ╱         n log n
  │                                    ╱        ╱‾‾‾
  │                                ╱      ╱‾‾‾          n
  │                           ╱   ╱‾‾ ╱‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
  │                      ╱ ╱‾‾ ╱‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
  │             ╱ ╱‾‾‾‾‾‾ ───────────────────────────────── log n
  │ ───────────────────────────────────────────────────────── constant
  └──────────────────────────────────────────────────────────► n
```

## 5. Why constants and small terms do not matter (for growth)

Suppose algorithm A takes `T_A(n) = 1000 n` steps and algorithm B takes `T_B(n) = n²` steps.

```python
def crossover():
    n = 1
    while n * n <= 1000 * n:         # while B is still cheaper or equal
        n += 1
    return n

print(crossover())                   # 1001
for n in (100, 1000, 10_000, 100_000):
    print(f"n={n:>7,}  A (1000n) = {1000 * n:>14,}   B (n^2) = {n * n:>16,}   B/A = {n * n / (1000 * n):>9,.1f}")
```

For `n` below 1,000 the "slow-growing" algorithm A is actually *worse*; after that it wins by a growing margin (at `n = 100,000`, B is 100 times slower). **Eventually the faster-growing function always loses, whatever the constants.**

Likewise, in `T(n) = n² + 100n + 5000`, the terms `100n` and `5000` become irrelevant:

```python
for n in (10, 100, 1000, 100_000):
    exact = n * n + 100 * n + 5000
    print(f"n={n:>7,}  total={exact:>16,}  n^2 share = {n * n / exact:>6.1%}")
# n=     10  total=           6,100  n^2 share =   1.6%
# n=    100  total=          15,000  n^2 share =  66.7%
# n=  1,000  total=       1,105,000  n^2 share =  90.5%
# n=100,000  total=  10,010,005,000  n^2 share =  99.9%
```

That is why **Big-O keeps only the fastest-growing term and drops its constant** ([Big-O notation](03-big-o-omega-theta.md)).

## 6. Measuring growth experimentally: the doubling test

If you cannot (or do not want to) derive the formula, **run the program for sizes `n`, `2n`, `4n`, ... and watch the ratio of times**:

| Ratio `time(2n) / time(n)` | Growth |
|-----------------------------|--------|
| about 1 | constant |
| about 1 + a little | logarithmic |
| about 2 | linear (n) or n log n |
| about 4 | quadratic |
| about 8 | cubic |
| huge, and growing | exponential |

```python
import time, random

def measure(fn, make_input, sizes):
    """Return the time fn takes for each input size."""
    results = []
    for n in sizes:
        data = make_input(n)
        start = time.perf_counter()
        fn(data)
        results.append(time.perf_counter() - start)
    return results

def estimate_growth(fn, make_input, sizes):
    times = measure(fn, make_input, sizes)
    for n, t, previous in zip(sizes[1:], times[1:], times):
        print(f"n={n:>7,} time={t:>8.4f}s ratio vs half-size = {t / previous:>5.1f}")
    return times

random.seed(1)
make_random = lambda n: [random.random() for _ in range(n)]

print("linear: sum()");        t1 = estimate_growth(sum, make_random, [200_000, 400_000, 800_000, 1_600_000])
print("quadratic: has_duplicate"); t2 = estimate_growth(has_duplicate, make_random, [500, 1000, 2000, 4000])
# linear: ratios near 2.0.  quadratic: ratios near 4.0
assert 1.2 < t1[-1] / t1[-2] < 3.5 and 2.5 < t2[-1] / t2[-2] < 6.0
```

Typical output (your timings will differ, the ratios should not):

```text
linear: sum()
n=400,000 time=  0.0021s ratio vs half-size =   2.0
n=800,000 time=  0.0041s ratio vs half-size =   2.0
n=1,600,000 time= 0.0083s ratio vs half-size =   2.0
quadratic: has_duplicate
n=  1,000 time=  0.0112s ratio vs half-size =   4.0
n=  2,000 time=  0.0450s ratio vs half-size =   4.0
n=  4,000 time=  0.1800s ratio vs half-size =   4.0
```

Doubling the input doubles the linear time but quadruples the quadratic time: exactly as predicted. Cautions: use inputs large enough that the time is not noise (milliseconds or more), repeat measurements and take the minimum, and beware of caches, garbage collection and background load. This test is a sanity check, not a proof.

### From growth to feasibility

If a computer does about `10^8` simple steps per second, here is how long different growth rates take for `n = 1,000,000`:

```python
steps_per_second = 10 ** 8
n = 1_000_000
costs = {"log n": math.log2(n), "n": n, "n log n": n * math.log2(n), "n^2": n ** 2, "n^3": n ** 3}
for name, steps in costs.items():
    seconds = steps / steps_per_second
    if seconds < 1:
        pretty = f"{seconds * 1000:.3f} ms"
    elif seconds < 86400:
        pretty = f"{seconds / 3600:.2f} hours" if seconds > 3600 else f"{seconds:.1f} s"
    else:
        pretty = f"{seconds / 86400 / 365:,.1f} years"
    print(f"{name:>8}: {pretty}")
# log n: 0.000 ms | n: 10.000 ms | n log n: 199.316 ms | n^2: 2.78 hours | n^3: 317,097.9 years
```

This is the most practical use of complexity: **deciding in advance whether an approach can possibly work** for your data size.

## 7. Two real-world examples

**Example 1: Why the "search as you type" box does not freeze.** A catalogue of 2 million products is searched on every keystroke. A linear scan costs about 2 million comparisons (around 20-50 ms in Python, too slow to feel instant when typing fast). Precomputing a sorted index and using binary search takes about 21 comparisons. Counting steps predicted this before anyone wrote the code.

**Example 2: A report that works in testing and dies in production.** A developer tests a report with 500 orders (instant) and ships it. Production has 200,000 orders. The algorithm contained a nested loop (`n²`): 500 orders = 250,000 steps, but 200,000 orders = 40 billion steps (more than an hour). The doubling test or a quick count would have exposed it during development.

## 8. Common mistakes

- Timing only a tiny input (everything is fast for small `n`).
- Believing seconds from one machine describe the algorithm.
- Counting every tiny operation exactly (growth is what matters).
- Forgetting that nested loops with different bounds multiply different variables (`n x m`, not `n²`).
- Treating the doubling ratio as exact (noise, caches and GC bend it).
- Assuming a bigger constant means a worse algorithm for all `n` (it only matters up to the crossover point).

## 9. Practice

1. Count the steps of `for i in range(n): for j in range(n): total += 1` and verify with the `Counter` approach.
2. How many times does the body run? `i = n` then `while i > 0: i //= 2`. Check with `n = 1,000,000`.
3. Two algorithms take `50n` and `n²/10` steps. At what `n` does the first become faster?
4. A program takes 0.8 s for `n = 100,000` and 3.2 s for `n = 200,000`. What is its likely growth? Predict the time for `n = 400,000`.
5. Using the 10^8 steps per second rule, would an `O(n²)` algorithm be feasible for `n = 10,000`? For `n = 1,000,000`?
6. Write an instrumented version of linear search and show its worst-case count is `n`.

<details>
<summary>Solutions</summary>

**1.**
```python
def double_loop(n):
    c = Counter()
    for i in range(n):
        for j in range(n):
            c.tick()
    return c.ops
print(double_loop(30), 30 * 30)           # 900 900
```

**2.**
```python
def halving_steps(n):
    steps = 0
    while n > 0:
        n //= 2
        steps += 1
    return steps
print(halving_steps(1_000_000), math.floor(math.log2(1_000_000)) + 1)       # 20 20
```

**3.** `50n < n²/10` when `n > 500`: for larger `n` the first algorithm is faster.

**4.** Doubling `n` quadrupled the time: quadratic. Prediction for 400,000: about `3.2 x 4 = 12.8 s`.

**5.** `n = 10,000`: `10^8` steps is about 1 second (feasible). `n = 1,000,000`: `10^12` steps is about 10,000 seconds (almost 3 hours: usually not acceptable).

**6.**
```python
def linear_search_counted(items, target):
    comparisons = 0
    for index, value in enumerate(items):
        comparisons += 1
        if value == target:
            return index, comparisons
    return -1, comparisons
print(linear_search_counted(list(range(1000)), -5))        # (-1, 1000): the worst case examines all n items
```

</details>

## 10. Check yourself

1. Why count steps instead of seconds?
2. How many comparisons does a nested loop with a shrinking inner loop make?
3. What does the doubling test show for a quadratic algorithm?
4. Why does a slow-growing algorithm with a big constant eventually win?
5. Why does `n² + 100n + 5000` behave like `n²` for large `n`?

<details>
<summary>Answers</summary>

1. Steps describe the algorithm independent of the machine, language and load; seconds do not.
2. `n(n-1)/2`.
3. Doubling the input multiplies the time by about 4.
4. A function that grows faster always eventually overtakes one that grows slower; the constant only moves the crossover point.
5. As `n` grows, the other terms become a vanishing fraction of the total.

</details>

[Back to complexity](README.md) · Previous: [what is an algorithm](01-what-is-an-algorithm.md) · Next: [Big-O, Omega and Theta](03-big-o-omega-theta.md)
