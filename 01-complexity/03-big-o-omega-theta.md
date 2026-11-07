# Big-O, Omega and Theta: The Language of Growth

**Prerequisites:** [counting steps and growth](02-counting-steps-and-growth.md). **You will learn:** the precise meaning of `O`, `Ω` and `Θ`, the simple rules for simplifying a step count into a Big-O class, the common classes and examples of each, how to check a claim numerically, and the typical misunderstandings.

## 1. In plain words

After counting steps (`T(n) = 3n² + 20n + 7`) we want a **short label** for how the cost grows. **Big-O notation** gives that label: it keeps only the fastest-growing term and drops its constant: `T(n)` is `O(n²)`.

Think of Big-O as a **speed-limit sign** for an algorithm: "this algorithm will **never be slower than** this curve (for large enough inputs, up to a constant factor)". Three related symbols:

| Symbol | Pronounced | Meaning | Think of it as |
|--------|-----------|---------|----------------|
| `O(f(n))` | "big-oh" | grows **no faster than** `f(n)` | an **upper** bound ("at most") |
| `Ω(f(n))` | "big-omega" | grows **at least as fast as** `f(n)` | a **lower** bound ("at least") |
| `Θ(f(n))` | "big-theta" | grows **exactly like** `f(n)` | a **tight** bound (both) |

## 2. The formal definition (do not be scared)

`T(n)` is `O(f(n))` if there are positive constants `c` and `n0` such that

```text
T(n) <= c * f(n)     for every n >= n0
```

In words: "beyond some starting size `n0`, `T(n)` stays below `c` copies of `f(n)`". `c` absorbs constant factors; `n0` ignores tiny inputs.

**Example:** show `3n² + 20n + 7` is `O(n²)`. Pick `c = 4` and see when `3n² + 20n + 7 <= 4n²`, i.e. `20n + 7 <= n²`. That holds for `n >= 21` (since `20·21 + 7 = 427 <= 441`). So `c = 4, n0 = 21` works.

```python
def T(n):                     # the exact step count of some algorithm
    return 3 * n * n + 20 * n + 7

c, n0 = 4, 21
print(all(T(n) <= c * n * n for n in range(n0, 10_000)))       # True   (the definition holds from n0 on)
print([n for n in range(1, 25) if T(n) > c * n * n][-1])       # 20     (the last n where it fails: the inequality fails below n0)

def find_constants(T, f, c_candidates=range(1, 20), search_up_to=100_000):
    """Search for (c, n0) proving T is O(f). Returns the first pair found."""
    for c in c_candidates:
        failing = [n for n in range(1, search_up_to) if T(n) > c * f(n)]
        if not failing or failing[-1] < search_up_to - 1:
            n0 = (failing[-1] + 1) if failing else 1
            return c, n0

print(find_constants(T, lambda n: n * n))                      # (4, 21)
```

Likewise `T(n)` is `Ω(f(n))` if `T(n) >= c * f(n)` for large `n`, and `Θ(f(n))` if it is both `O` and `Ω`. For `3n² + 20n + 7`: it is `O(n²)`, `Ω(n²)`, hence `Θ(n²)`. (It is also `O(n³)` and `O(2ⁿ)`: true but uselessly loose. **Always give the tightest bound you can.**)

## 3. The simplification rules

To get Big-O from a step count:

1. **Drop constant factors**: `5n` becomes `n`; `n/2` becomes `n`; `1,000,000` becomes `1`.
2. **Drop lower-order terms**: `n² + 100n + 5000` becomes `n²`.
3. **Keep the dominant term** (fastest-growing) of a sum: `n + log n + 7` is `O(n)`.
4. **Sequential steps add** (take the largest): do `O(n)` work, then `O(n²)` work: `O(n²)`.
5. **Nested steps multiply**: an `O(n)` loop around an `O(m)` body is `O(n · m)`.
6. **Different inputs, different variables**: looping over list `a` (size `n`) and then list `b` (size `m)` is `O(n + m)`, not `O(n)` or `O(2n)`.
7. **Logarithm bases do not matter**: `log2 n`, `log10 n`, `ln n` differ by a constant: all `O(log n)`.
8. **Ignore constants in exponents' bases?** No! `2ⁿ` and `3ⁿ` are *different* classes (the base is not a constant factor).

Order of growth classes, from slowest to fastest:

```text
O(1) < O(log n) < O(√n) < O(n) < O(n log n) < O(n²) < O(n³) < O(2ⁿ) < O(n!) < O(nⁿ)
constant   log     root   linear  linearithmic quadratic cubic  exponential factorial
```

### Practice simplifying

| Step count | Big-O |
|------------|-------|
| `7` | `O(1)` |
| `3n + 2` | `O(n)` |
| `n²/2 - n/2` | `O(n²)` |
| `4n log n + 10n` | `O(n log n)` |
| `n³ + 500n²` | `O(n³)` |
| `2ⁿ + n¹⁰⁰` | `O(2ⁿ)` |
| `n + m` (two inputs) | `O(n + m)` |
| `log₂ n + log₁₀ n` | `O(log n)` |
| `(n + 1)(n + 2)` | `O(n²)` (expand: `n² + 3n + 2`) |

## 4. The common classes with examples

| Class | Name | Typical code or algorithm |
|-------|------|---------------------------|
| `O(1)` | constant | `items[i]`, `d[key]`, `len(items)`, `x + y`, push/pop on a stack |
| `O(log n)` | logarithmic | binary search, balanced BST lookup, heap push/pop, loops that halve or double |
| `O(n)` | linear | one loop over the input, `sum`, `max`, `x in list`, building a list, BFS/DFS |
| `O(n log n)` | linearithmic | merge sort, heap sort, `sorted()`, many divide-and-conquer algorithms |
| `O(n²)` | quadratic | two nested loops over the input, bubble/insertion/selection sort, comparing all pairs |
| `O(n³)` | cubic | three nested loops, naive matrix multiplication |
| `O(2ⁿ)` | exponential | all subsets, naive recursive Fibonacci, brute-force knapsack |
| `O(n!)` | factorial | all permutations, brute-force travelling salesman |

```python
def constant(items):        return items[0]                                       # O(1)
def logarithmic(n):
    steps = 0
    while n > 1: n //= 2; steps += 1                                              # O(log n)
    return steps
def linear(items):          return sum(items)                                     # O(n)
def linearithmic(items):    return sorted(items)                                  # O(n log n)
def quadratic(items):       return [(a, b) for a in items for b in items]         # O(n^2)
def exponential(items):
    subsets = [[]]
    for x in items:
        subsets += [s + [x] for s in subsets]                                     # doubles each time: O(2^n)
    return subsets

print(constant([5, 6]), logarithmic(1024), linear([1, 2, 3]), linearithmic([3, 1, 2]), len(quadratic(range(10))), len(exponential(range(10))))
# 5 10 6 [1, 2, 3] 100 1024
```

## 5. Best, worst and average belong to *cases*, not to O/Ω/Θ

A common confusion: **`O` is not "worst case"** and **`Ω` is not "best case"**. Big-O/Omega/Theta describe how a *function* grows. You can apply them to *any* of the three cases of an algorithm:

| Algorithm | Best case | Worst case |
|-----------|-----------|------------|
| Linear search | `Θ(1)` (found first) | `Θ(n)` (last or missing) |
| Binary search | `Θ(1)` (middle hit) | `Θ(log n)` |
| Insertion sort | `Θ(n)` (already sorted) | `Θ(n²)` (reversed) |
| Quicksort | `Θ(n log n)` | `Θ(n²)` (bad pivots) |

When people say "linear search is O(n)" they mean "its **worst-case** running time is O(n)", which is also tight (`Θ(n)`). More: [best, average and worst cases](06-cases-and-amortized-analysis.md).

## 6. Verifying a claim numerically

You can sanity-check a Big-O claim by watching the ratio `T(n) / f(n)`: if `T` is `Θ(f)`, the ratio levels off near a constant.

```python
def ratio_table(T, f, sizes):
    return [round(T(n) / f(n), 3) for n in sizes]

import math
sizes = [10, 100, 1_000, 10_000, 100_000]
print(ratio_table(lambda n: 3 * n * n + 20 * n + 7, lambda n: n * n, sizes))
# [5.07, 3.201, 3.02, 3.002, 3.0]        -> settles at 3: Theta(n^2)
print(ratio_table(lambda n: 3 * n * n + 20 * n + 7, lambda n: n, sizes))
# [50.7, 320.07, 3020.007, 30020.001, 300020.0]   -> keeps growing: the function is NOT O(n)
print(ratio_table(lambda n: n * math.log2(n) + 5 * n, lambda n: n * math.log2(n), sizes))
# [2.505, 1.753, 1.502, 1.376, 1.301]    -> slowly approaches 1 (still Theta(n log n))
```

If the ratio **grows without bound**, `f` is too small an upper bound; if it **shrinks toward 0**, `f` is too loose.

## 7. Little-o, little-omega, and why you rarely need them

`o(f)` means "grows **strictly slower** than `f`" (`n` is `o(n²)`); `ω(f)` means "strictly faster". They appear in proofs and textbooks; in practice use `O` and `Θ`.

## 8. Reading Big-O in the wild

- **Documentation:** Python's wiki lists `list.append` as `O(1)` (amortized), `list.insert(0, x)` as `O(n)`, `x in set` as `O(1)` average ([cheat sheet](07-python-operations-cheat-sheet.md)).
- **Interviews:** "What is the time and space complexity?" expects the tightest bound with the worst case (and the average if it differs).
- **Code review:** `O(n²)` over user-controlled input is a performance and security risk (denial of service).
- **Design:** pick data structures by the operations you need most ([data structures](../02-data-structures/arrays-strings/README.md)).

## 9. Two real-world examples

**Example 1: Choosing a data structure for a "seen before?" check.** A deduplication job asks "have I seen this ID?" for 5 million IDs. With a list that is `O(n)` per check: `O(n²)` total (about 10^13 steps, days). With a set it is `O(1)` per check: `O(n)` total (seconds). Big-O made the decision before any code existed.

```python
import time
ids = list(range(30_000))
as_list, as_set = ids, set(ids)
t = time.perf_counter(); sum(1 for i in range(0, 60_000, 2) if i in as_list); list_time = time.perf_counter() - t
t = time.perf_counter(); sum(1 for i in range(0, 60_000, 2) if i in as_set); set_time = time.perf_counter() - t
print(list_time > set_time * 50)         # True: the same question, thousands of times faster with the right structure
```

**Example 2: A security bug that is really a complexity bug.** Some web frameworks once used a hash table whose worst case is `O(n)` per insert. An attacker sent thousands of keys crafted to collide, turning each request into `O(n²)` work and freezing the server (a "hash-collision denial of service"). Python randomizes string hashing (`PYTHONHASHSEED`) precisely to prevent it. Worst-case complexity is a security property.

## 10. Common mistakes

- Saying "O(2n)" or "O(n + 5)": always simplify to `O(n)`.
- Treating `O(n²)` with a tiny constant as automatically worse than `O(n)` with a huge one (true only for large `n`).
- Confusing O with "worst case" (it is a bound on growth; cases are separate).
- Forgetting multiple inputs (`O(n + m)`, `O(n · m)`).
- Calling `log n` "basically constant" while ignoring that it still grows (it is just very slow).
- Counting the cost of a built-in as `O(1)` without checking (`in` on a list, slicing, `str +=`, `list.insert(0, ...)` are `O(n)`).
- Reporting only time: also report space ([space complexity](05-space-complexity.md)).

## 11. Practice

1. Simplify to Big-O: `5n³ + 2n² + 100`, `n + n log n`, `n²/2`, `100`, `log n + 1000`, `2ⁿ + n⁵`.
2. Prove (find `c` and `n0`): `4n + 10` is `O(n)`.
3. Is `n²` also `O(n³)`? Is `n³` `O(n²)`? Explain.
4. Order from slowest to fastest growth: `n²`, `log n`, `2ⁿ`, `n`, `n log n`, `n!`, `1`, `n³`.
5. What is the complexity of: `for i in range(n): for j in range(m): ...` followed by `for k in range(n): ...`?
6. Use the ratio test to check whether `T(n) = 7n log2 n + 3n` is `Θ(n log n)`.

<details>
<summary>Solutions</summary>

**1.** `O(n³)`, `O(n log n)`, `O(n²)`, `O(1)`, `O(1000)` means `O(1)` after the `log n` is considered: `O(log n)` is the dominant term of `log n + 1000`, so `O(log n)`; `O(2ⁿ)`.

**2.** `4n + 10 <= 5n` when `n >= 10`: `c = 5`, `n0 = 10`.
```python
print(all(4 * n + 10 <= 5 * n for n in range(10, 10_000)))       # True
```

**3.** `n²` is `O(n³)` (a valid but loose upper bound: `n² <= n³` for `n >= 1`); `n³` is **not** `O(n²)` (the ratio `n³/n²` grows without bound).

**4.** `1`, `log n`, `n`, `n log n`, `n²`, `n³`, `2ⁿ`, `n!`.

**5.** `O(n · m + n)`, which simplifies to `O(n · m)` if `m >= 1` (the first part dominates).

**6.**
```python
import math
print(ratio_table(lambda n: 7 * n * math.log2(n) + 3 * n, lambda n: n * math.log2(n), [10, 1000, 100_000, 10_000_000]))
# the ratio approaches 7 (a constant): Theta(n log n)
```

</details>

## 12. Check yourself

1. What does `T(n) = O(f(n))` mean formally?
2. State the rules for simplifying a step count.
3. Is `O(2n)` a correct simplification?
4. What is the difference between `O` and `Θ`?
5. Is Big-O the same as worst case?
6. What is the Big-O of two sequential loops, one over `n` items and one over `m` items?

<details>
<summary>Answers</summary>

1. There exist constants `c > 0` and `n0` such that `T(n) <= c · f(n)` for all `n >= n0`.
2. Drop constant factors, drop lower-order terms, keep the dominant term, add for sequential steps, multiply for nested steps, use separate variables for separate inputs.
3. Not as a final answer: it simplifies to `O(n)`.
4. `O` is an upper bound only; `Θ` is a tight bound (both upper and lower).
5. No: Big-O bounds how a function grows; "worst case" is which input you analyze. They are often combined ("worst-case time is O(n)").
6. `O(n + m)`.

</details>

[Back to complexity](README.md) · Previous: [counting steps and growth](02-counting-steps-and-growth.md) · Next: [analyzing loops and recursion](04-analyzing-loops-and-recursion.md)
