# Big-O and Complexity Analysis

## 1. The concept

**Complexity analysis** answers one question: *how does the cost of an algorithm grow as the input grows?* Cost means either **time** (number of basic operations) or **space** (extra memory).

We do not measure seconds, because seconds depend on the machine, the language, and what else is running. We count how the number of steps scales with the input size `n`.

**Big-O notation** describes an *upper bound* on that growth, ignoring constant factors and lower-order terms.

- `3n + 10` steps is `O(n)`.
- `5n² + 100n + 7` steps is `O(n²)`.
- `1,000,000` steps regardless of input is `O(1)`.

Why drop constants? Because at large `n` the shape of the curve dominates. An `O(n)` algorithm with a big constant still beats an `O(n²)` algorithm once `n` is large enough.

### The three notations

| Notation | Meaning | Think of it as |
|----------|---------|----------------|
| `O(f(n))` | Upper bound: grows **no faster than** `f(n)` | "at most" |
| `Ω(f(n))` | Lower bound: grows **at least as fast as** `f(n)` | "at least" |
| `Θ(f(n))` | Tight bound: both of the above | "exactly this order" |

In everyday engineering and interviews, people say "Big-O" and usually mean the tight worst-case bound (`Θ`). Stay precise when it matters: binary search is `O(log n)` worst case and `O(1)` best case.

## 2. The common growth rates

Ordered from fastest (best) to slowest (worst):

| Class | Name | Example | n = 1,000 | n = 1,000,000 |
|-------|------|---------|-----------|----------------|
| `O(1)` | Constant | Dictionary lookup | 1 | 1 |
| `O(log n)` | Logarithmic | Binary search | ~10 | ~20 |
| `O(n)` | Linear | Scan a list | 1,000 | 1,000,000 |
| `O(n log n)` | Linearithmic | Merge sort | ~10,000 | ~20,000,000 |
| `O(n²)` | Quadratic | Nested loops, bubble sort | 1,000,000 | 10¹² |
| `O(n³)` | Cubic | Naive matrix multiply | 10⁹ | 10¹⁸ |
| `O(2ⁿ)` | Exponential | Naive Fibonacci, subsets | astronomical | impossible |
| `O(n!)` | Factorial | Brute-force travelling salesman | impossible | impossible |

A useful rule of thumb for a one-second budget on a typical machine (about 10⁸ simple operations):

| Input size `n` | Largest class that fits |
|----------------|-------------------------|
| up to 10 | `O(n!)` |
| up to 20 | `O(2ⁿ)` |
| up to 500 | `O(n³)` |
| up to 10,000 | `O(n²)` |
| up to 10⁶ | `O(n log n)` |
| up to 10⁸ | `O(n)` |
| beyond that | `O(log n)` or `O(1)` |

## 3. How to analyze code

### Rule 1: Count loops

```python
def total(nums):
    s = 0                 # O(1)
    for x in nums:        # runs n times
        s += x            # O(1) each
    return s              # total: O(n)
```

### Rule 2: Nested loops multiply

```python
def has_duplicate_slow(nums):
    for i in range(len(nums)):              # n times
        for j in range(i + 1, len(nums)):   # up to n times
            if nums[i] == nums[j]:
                return True
    return False                            # O(n²)
```

The inner loop runs `(n-1) + (n-2) + ... + 1 = n(n-1)/2` times. That is `O(n²)` because we drop the `1/2` and the lower-order `-n/2`.

### Rule 3: Sequential blocks add, then keep the largest

```python
def example(nums):
    for x in nums: ...          # O(n)
    for x in nums:              # O(n²)
        for y in nums: ...
    # O(n) + O(n²) = O(n²)
```

### Rule 4: Halving the problem each step gives `log n`

```python
def binary_search(sorted_nums, target):
    lo, hi = 0, len(sorted_nums) - 1
    while lo <= hi:                       # each pass halves the range
        mid = (lo + hi) // 2
        if sorted_nums[mid] == target:
            return mid
        if sorted_nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1                             # O(log n)
```

`n → n/2 → n/4 → ... → 1` takes `log₂ n` steps.

### Rule 5: Different inputs get different variables

```python
def pairs(a, b):
    for x in a:         # a has n items
        for y in b:     # b has m items
            ...
# O(n * m), not O(n²)
```

Never call two different inputs `n`. This is one of the most common interview mistakes.

### Rule 6: Recursion: write the recurrence

```python
def fib(n):                       # naive Fibonacci
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)
```

`T(n) = T(n-1) + T(n-2) + O(1)`. Each call makes two calls, so the call tree roughly doubles at each level: `O(2ⁿ)`. With memoization each value is computed once, giving `O(n)`.

Common recurrences:

| Recurrence | Result | Example |
|------------|--------|---------|
| `T(n) = T(n/2) + O(1)` | `O(log n)` | Binary search |
| `T(n) = T(n-1) + O(1)` | `O(n)` | Linear recursion |
| `T(n) = 2T(n/2) + O(n)` | `O(n log n)` | Merge sort |
| `T(n) = 2T(n/2) + O(1)` | `O(n)` | Tree traversal |
| `T(n) = 2T(n-1) + O(1)` | `O(2ⁿ)` | Naive subsets |

## 4. Best, average and worst case

The same algorithm can behave differently depending on the input.

| Algorithm | Best | Average | Worst |
|-----------|------|---------|-------|
| Linear search | `O(1)` (first item) | `O(n)` | `O(n)` |
| Quick sort | `O(n log n)` | `O(n log n)` | `O(n²)` (bad pivots) |
| Insertion sort | `O(n)` (already sorted) | `O(n²)` | `O(n²)` |
| Hash table lookup | `O(1)` | `O(1)` | `O(n)` (all keys collide) |

Unless told otherwise, quote the **worst case**, and mention the average when it differs a lot.

## 5. Amortized analysis

Some operations are usually cheap but occasionally expensive. **Amortized cost** spreads the occasional expense over many operations.

The classic case is Python's `list.append`. The list keeps spare capacity. Most appends just write into a free slot (`O(1)`). When the array is full, Python allocates a bigger block (roughly 1.125× growth in CPython) and copies everything (`O(n)`). Because the resizes are rare and the capacity grows geometrically, the *average* cost per append over a long sequence is `O(1)`.

```python
# Appending n items is O(n) total, so O(1) amortized per append
items = []
for i in range(1_000_000):
    items.append(i)
```

Contrast with `list.insert(0, x)`, which shifts every element: `O(n)` every single time.

## 6. Space complexity

Count the *extra* memory your algorithm uses, not counting the input itself.

```python
def reverse_in_place(a):          # O(1) extra space
    i, j = 0, len(a) - 1
    while i < j:
        a[i], a[j] = a[j], a[i]
        i += 1
        j -= 1

def reverse_copy(a):              # O(n) extra space
    return a[::-1]
```

**Recursion uses stack space.** A recursive function that goes `n` levels deep uses `O(n)` stack memory even if it allocates nothing else. Python's default recursion limit is about 1000 frames, so deep recursion raises `RecursionError`.

Time and space often trade off. A hash set makes duplicate detection `O(n)` time but costs `O(n)` space; sorting first costs `O(n log n)` time but can be `O(1)` extra space.

```python
def has_duplicate_fast(nums):        # O(n) time, O(n) space
    seen = set()
    for x in nums:
        if x in seen:
            return True
        seen.add(x)
    return False
```

## 7. Complexity of Python built-ins

Knowing these saves you from accidental quadratic code.

| Operation | `list` | `dict` / `set` | `deque` |
|-----------|--------|----------------|---------|
| Index `a[i]` | `O(1)` | n/a | `O(n)` in the middle |
| Append at end | `O(1)` amortized | n/a | `O(1)` |
| Insert/pop at front | **`O(n)`** | n/a | `O(1)` |
| `x in container` | **`O(n)`** | `O(1)` average | `O(n)` |
| Delete by value | `O(n)` | `O(1)` average | `O(n)` |
| Slice `a[i:j]` | `O(j-i)` (copies) | n/a | n/a |
| `sorted(a)` / `a.sort()` | `O(n log n)` (Timsort) | n/a | n/a |
| `len(a)` | `O(1)` | `O(1)` | `O(1)` |
| `min(a)` / `max(a)` | `O(n)` | `O(n)` | `O(n)` |

Strings are immutable. Building a string with `s += piece` in a loop can be `O(n²)` overall. Use `"".join(parts)` instead, which is `O(n)`.

## 8. Two real-world examples

### Example 1: Autocomplete search box

A site has 5 million product names and wants instant suggestions as the user types.

- **Naive:** scan all names for each keystroke: `O(n)` per keystroke. At 5 million items that is tens of milliseconds to seconds, which is too slow when repeated per key.
- **Better:** keep the names sorted and use binary search to find the first match for the prefix: `O(log n)`, about 23 steps for 5 million items.
- **Best for this case:** a trie (prefix tree) gives `O(k)` where `k` is the prefix length, independent of the catalogue size.

The lesson: the difference between `O(n)` and `O(log n)` is the difference between a feature that works and one that does not.

### Example 2: Finding duplicate customer records

A data pipeline merges 2 million customer rows and must flag duplicate emails.

- **Nested comparison:** compare every pair: `O(n²)`, about 2 × 10¹² comparisons. This would run for days.
- **Hash set:** one pass inserting emails into a set: `O(n)`, finishing in seconds, at the cost of memory proportional to the number of unique emails.
- **Sort then scan:** `O(n log n)` time and little extra memory, which is useful when the data does not fit in RAM.

The lesson: trading memory for speed (or sorting to enable a linear scan) is the most common optimization in real systems.

## 9. Tips, tricks and pitfalls

- **Drop constants and lower-order terms**, but remember constants matter in practice. A `O(n log n)` algorithm with heavy constants can lose to a simple `O(n²)` one for small inputs. This is why Python's Timsort uses insertion sort on tiny runs.
- **Look for hidden loops.** `x in my_list`, `my_list.index(x)`, `list.remove(x)`, `str.count`, slicing, and `sum(...)` are all loops. Calling them inside a loop is a quadratic trap.
- **`while` loops need care.** If the loop variable moves by 1, it is linear. If it doubles or halves, it is logarithmic.
- **Two pointers and sliding windows** often turn `O(n²)` brute force into `O(n)`.
- **Sorting first** is a frequent trick: it costs `O(n log n)` but can make the rest of the algorithm linear.
- **Memoization / caching** turns exponential recursion into polynomial time (`functools.lru_cache`).
- **State your assumptions** in interviews: "assuming hash lookups are `O(1)` average".
- **Space counts too.** Say both: "`O(n)` time, `O(1)` extra space".
- **Big-O is not the whole story.** Cache locality, I/O, network latency and lock contention often dominate in real systems. Profile before optimizing.

## 10. Check yourself

1. What is the time complexity of `for i in range(n): for j in range(i): ...`? Why?
2. Why is `list.append` amortized `O(1)` but `list.insert(0, x)` `O(n)`?
3. What is the complexity of checking `x in some_list` versus `x in some_set`?
4. A function has two sequential loops: one `O(n log n)`, one `O(n)`. What is the total?
5. Write the recurrence for merge sort and state its solution.
6. Why does naive Fibonacci take exponential time, and how do you fix it?
7. What is the space complexity of a recursive function that recurses `n` deep and allocates nothing else?
8. You have 10⁶ items. Is an `O(n²)` solution acceptable? What about `O(n log n)`?

<details>
<summary>Answers</summary>

1. `O(n²)`. The inner loop runs `0 + 1 + ... + (n-1) = n(n-1)/2` times.
2. Append writes into spare capacity and only occasionally resizes (rare, geometric growth). Inserting at index 0 shifts every existing element every time.
3. `O(n)` for a list (linear scan), `O(1)` average for a set (hashing).
4. `O(n log n)`: the larger term dominates.
5. `T(n) = 2T(n/2) + O(n)`, which solves to `O(n log n)`.
6. Each call spawns two more, recomputing the same subproblems. Memoization (or iteration) computes each value once: `O(n)`.
7. `O(n)`, from the call stack.
8. `O(n²)` is about 10¹² operations, far too slow. `O(n log n)` is about 2 × 10⁷, which is fine.

</details>
