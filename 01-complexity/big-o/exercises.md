# Big-O: Exercises

Try each one before opening the solution. Write the answer and the reasoning.

## Part A: Analyze the complexity

**A1.**
```python
def f(n):
    i = 1
    while i < n:
        i *= 2
```

**A2.**
```python
def f(nums):
    for i in range(len(nums)):
        for j in range(len(nums)):
            for k in range(10):
                pass
```

**A3.**
```python
def f(s):
    out = ""
    for ch in s:
        out += ch.upper()
    return out
```

**A4.**
```python
def f(a, b):
    for x in a:
        if x in b:      # b is a list
            print(x)
```

**A5.**
```python
def f(n):
    if n <= 1:
        return 1
    return f(n - 1) + f(n - 1)
```

**A6.**
```python
def f(n):
    for i in range(n):
        j = i
        while j > 0:
            j //= 2
```

## Part B: Improve it

**B1.** Given a list of `n` integers and a target, return `True` if any two numbers sum to the target. Write an `O(n²)` solution, then an `O(n)` solution.

**B2.** Given two lists of `n` and `m` user IDs, return the IDs in both. Make it `O(n + m)`.

**B3.** A function repeatedly calls `my_list.pop(0)` in a loop to process a queue of `n` items. What is its complexity and how do you fix it?

**B4.** Rewrite the naive recursive Fibonacci so it runs in `O(n)` time. Then in `O(1)` extra space.

## Part C: Reason about it

**C1.** An algorithm is `O(n log n)` and another is `O(n²)`. For what sizes of `n` might the `O(n²)` one still win? Why?

**C2.** Why is `"".join(parts)` preferred over `s += part` in a loop?

**C3.** `sorted(data)` is `O(n log n)`. A colleague says "sort first, then scan once" is `O(n)`. What is wrong with that claim?

**C4.** What is the amortized cost of `n` appends to a dynamic array, and why is it not `O(n)` per append?

---

<details>
<summary>Solutions</summary>

**A1.** `O(log n)`. `i` doubles each pass, so the loop runs `log₂ n` times.

**A2.** `O(n²)`. The innermost loop is a constant 10, so the total is `n × n × 10`, which is `O(n²)`.

**A3.** `O(n²)` in the worst case, because strings are immutable and each `+=` can copy the string built so far. Use `"".join(...)` for `O(n)`.

**A4.** `O(n × m)` where `m = len(b)`, because `x in b` on a list scans the list. Convert `b` to a set first: `O(n + m)`.

**A5.** `O(2ⁿ)`. Each call makes two calls of size `n-1`.

**A6.** `O(n log n)`. The outer loop runs `n` times; the inner `while` halves `j`, so it takes at most `log₂ n` steps.

**B1.**
```python
# O(n^2)
def two_sum_slow(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return True
    return False

# O(n) time, O(n) space
def two_sum_fast(nums, target):
    seen = set()
    for x in nums:
        if target - x in seen:
            return True
        seen.add(x)
    return False
```

**B2.** `return set(a) & set(b)`. Building each set is linear; the intersection is linear in the smaller set.

**B3.** Each `pop(0)` shifts the remaining items, so the loop is `O(n²)`. Use `collections.deque` and `popleft()`, which is `O(1)`, giving `O(n)` overall.

**B4.**
```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fib_memo(n):                    # O(n) time, O(n) space
    return n if n < 2 else fib_memo(n - 1) + fib_memo(n - 2)

def fib_iter(n):                    # O(n) time, O(1) space
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
```

**C1.** For small `n`, the `O(n²)` algorithm can win because Big-O hides constants. If it has a tiny constant and the `O(n log n)` one has heavy overhead, the crossover can be in the dozens or hundreds. Timsort exploits this by using insertion sort on small runs.

**C2.** `s += part` can copy the whole string each time (`O(n²)` overall); `join` computes the total size once and builds the result in `O(n)`.

**C3.** Sorting itself costs `O(n log n)`, and that dominates. The total is `O(n log n)`, not `O(n)`. The scan is only the cheap part.

**C4.** Resizes are rare and capacity grows geometrically, so the total copying across `n` appends is proportional to `n`. The cost per append averages out to `O(1)`.

</details>
