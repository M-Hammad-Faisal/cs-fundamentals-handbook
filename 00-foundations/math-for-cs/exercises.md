# Math for Computer Science: Exercises

These problems go with the [Math for Computer Science lesson](README.md). Try each one before opening its solution.

<details>
<summary>Setup code the solutions use (copied from the lessons)</summary>

```python
import math
import random

def collision_probability(n_items, n_slots):
    """Probability that at least two of n_items land in the same slot (all slots equally likely)."""
    p_no_collision = 1.0
    for i in range(n_items):
        p_no_collision *= (n_slots - i) / n_slots
    return 1 - p_no_collision

def halvings(n):
    """How many times can n be halved (integer division) until it reaches 1?"""
    steps = 0
    while n > 1:
        n //= 2
        steps += 1
    return steps
```

</details>

## Problems

### Exponents, Logarithms and Growth

1. Compute by hand: `2^8`, `3^4`, `10^-2`, `log2(64)`, `log10(100000)`.
2. How many halvings does it take to reduce 5,000 to 1? How many bits does 5,000 need?
3. A loop runs `for i in range(n): for j in range(n):`. How many iterations for n = 10, 1,000, 100,000?
4. If an algorithm takes `n^2` steps and 1,000 items take 1 second, how long do 10,000 items take?
5. Rank by growth: `n log n`, `n^3`, `log n`, `2^n`, `n`, `n^2`.

<details>
<summary>Solutions</summary>

**1.** 256, 81, 0.01, 6, 5.
```python
print(2 ** 8, 3 ** 4, 10 ** -2, math.log2(64), math.log10(100000))
```

**2.** `log2(5000) ≈ 12.3`, so 12 halvings; 5000 needs 13 bits.
```python
print(halvings(5000), (5000).bit_length())      # 12 13
```

**3.** `n^2`: 100; 1,000,000; 10,000,000,000 (ten billion: too slow in Python).

**4.** 10x more items means 100x more steps: 100 seconds.

**5.** From slowest growth to fastest: `log n`, `n`, `n log n`, `n^2`, `n^3`, `2^n`.

</details>

### Logic, Sets and Proofs

1. Build the truth table for `(A and not B) or (not A and B)`. What is it equal to?
2. Use De Morgan's law to simplify `not (x > 5 and y < 3)`.
3. Using sets, find the numbers below 50 divisible by 3 **or** 5 but **not** both.
4. Prove by induction that `1 + 3 + 5 + ... + (2n - 1) = n^2`.
5. How many subsets does a set of 10 elements have? How many have exactly 3 elements?
6. Write a loop invariant for a function that finds the maximum of a list.

<details>
<summary>Solutions</summary>

**1.** It is XOR (true when exactly one of A and B is true).
```python
from itertools import product
print(all(((a and not b) or (not a and b)) == (a != b) for a, b in product([0, 1], repeat=2)))     # True
```

**2.** `not (x > 5 and y < 3)` equals `x <= 5 or y >= 3`.

**3.**
```python
three, five = {n for n in range(50) if n % 3 == 0}, {n for n in range(50) if n % 5 == 0}
print(sorted(three ^ five))        # divisible by exactly one of 3 and 5
```

**4.** Base: n = 1: 1 = 1^2. Step: assume the sum of the first k odd numbers is k^2; adding the next odd number (2k + 1) gives k^2 + 2k + 1 = (k + 1)^2. ✓
```python
assert all(sum(2 * i - 1 for i in range(1, n + 1)) == n * n for n in range(1, 300))
```

**5.** 2^10 = 1,024 subsets; `math.comb(10, 3)` = 120 subsets with exactly three elements.

**6.** Invariant: "after processing the first `i` items, `best` is the maximum of those `i` items". True before the loop for the first element, preserved by `best = max(best, item)`, and at the end it covers the whole list.
```python
def maximum(items):
    best = items[0]
    for item in items[1:]:
        best = item if item > best else best      # invariant: best is the max of everything seen so far
    return best
print(maximum([3, 9, 2]))
```

</details>

### Counting and Probability

1. How many 8-character passwords use lowercase letters and digits? How many if no character may repeat?
2. In how many ways can 5 people line up? Choose a president, vice-president and treasurer from 10 people?
3. How many different 5-card hands from 52 cards? What is the probability of a specific hand?
4. A bag has 3 red and 2 blue balls. Draw two without replacement. Probability both are red?
5. Simulate the probability that in 10 coin flips you get at least 7 heads, and compute it exactly.
6. How many people are needed for a 50% collision chance in a hash table with 10,000 slots (approximately)?

<details>
<summary>Solutions</summary>

**1.**
```python
print(36 ** 8, math.perm(36, 8))             # 2821109907456 1220096908800
```

**2.** 5! = 120; P(10, 3) = 720 (`math.perm(10, 3)`).

**3.**
```python
print(math.comb(52, 5), 1 / math.comb(52, 5))        # 2598960 3.8e-07
```

**4.** `3/5 x 2/4 = 3/10`.
```python
from fractions import Fraction
print(Fraction(3, 5) * Fraction(2, 4))               # 3/10
```

**5.**
```python
exact = sum(math.comb(10, k) for k in range(7, 11)) / 2 ** 10
random.seed(0)
sim = sum(sum(random.random() < 0.5 for _ in range(10)) >= 7 for _ in range(50_000)) / 50_000
print(round(exact, 4), abs(sim - exact) < 0.01)      # 0.1719 True
```

**6.** About `1.18 x sqrt(10,000) = 118` items.
```python
print(round(collision_probability(118, 10_000), 2))   # 0.5
```

</details>

### Sequences, Sums and Recurrences

1. Find the exact number of iterations: `for i in range(n): for j in range(i, n):`.
2. Solve by unrolling: `T(n) = T(n-1) + 5`, `T(0) = 1`.
3. What does `T(n) = 2T(n/2) + 1` solve to? (tree traversal)
4. Use the Master Theorem for `T(n) = 4T(n/2) + n`.
5. Count how many times `print` runs: `i = n; while i >= 1: print(i); i //= 3`.
6. Prove by induction that `Fibonacci(n) < 2^n` for `n >= 1`.

<details>
<summary>Solutions</summary>

**1.** `n + (n-1) + ... + 1 = n(n+1)/2`.
```python
def f(n):
    steps = 0
    for i in range(n):
        for j in range(i, n):
            steps += 1
    return steps
print(f(10), 10 * 11 // 2)              # 55 55
```

**2.** `T(n) = T(n-1) + 5 = T(n-2) + 10 = ... = T(0) + 5n = 5n + 1`: `O(n)`.

**3.** a=2, b=2, `n^(log2 2) = n`, f = 1 is smaller: Case 1: `O(n)` (visiting every node once).

**4.** a=4, b=2, `n^2`; f = n grows slower: Case 1: `O(n^2)`.

**5.** The loop runs `floor(log3(n)) + 1` times: `O(log n)`.
```python
def runs(n):
    count, i = 0, n
    while i >= 1:
        count += 1; i //= 3
    return count
print(runs(1), runs(9), runs(10 ** 6), math.floor(math.log(10 ** 6, 3)) + 1)    # 1 3 13 13
```

**6.** Base: F(1) = 1 < 2, F(2) = 1 < 4. Step: assume F(k) < 2^k and F(k-1) < 2^(k-1); then F(k+1) = F(k) + F(k-1) < 2^k + 2^(k-1) < 2^k + 2^k = 2^(k+1). ✓

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Exponents, Logarithms and Growth](exponents-and-logarithms.md) · [Logic, Sets and Proofs](logic-sets-proofs.md) · [Counting and Probability](counting-and-probability.md) · [Sequences, Sums and Recurrences](sums-and-recurrences.md)
