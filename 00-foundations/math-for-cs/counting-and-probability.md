# Counting and Probability

**Prerequisites:** [exponents and logarithms](exponents-and-logarithms.md). **You will learn:** how to count possibilities (permutations, combinations), why some problems explode (`n!`, `2^n`), the basics of probability, expected value, and how hashing, randomness and testing use them.

## 1. In plain words

**Counting** (combinatorics) answers "how many ways?": how many passwords, how many orderings of a list, how many subsets. It tells you **how big a search space is**: whether brute force is possible or hopeless. **Probability** answers "how likely?": how often a hash collision happens, how a random algorithm behaves on average, how reliable a system is.

## 2. The basic counting rules

| Rule | Idea | Example |
|------|------|---------|
| **Sum rule** | If tasks are *alternatives*, add the ways | 3 pizzas **or** 4 pastas: 3 + 4 = 7 choices |
| **Product rule** | If choices are *in sequence* and independent, multiply | 3 shirts **and** 4 pants: 3 x 4 = 12 outfits |

```python
shirts, pants, shoes = 3, 4, 2
print(shirts * pants * shoes)                       # 24 outfits (multiply independent choices)

# Passwords: 4 digits, each 0-9, repetition allowed
print(10 ** 4)                                      # 10000

# Binary strings of length n: 2 choices per position
print(2 ** 10, 2 ** 20)                             # 1024 1048576   (why n bits give 2^n values)
```

## 3. Permutations: order matters

A **permutation** is an **ordering**.

- Ways to arrange all `n` distinct items: **n!** (n factorial) = n x (n-1) x ... x 1.
- Ways to pick and order `k` of `n` items: **P(n, k) = n! / (n-k)!** = n x (n-1) x ... x (n-k+1).

```text
Arrange the letters A, B, C:  ABC ACB BAC BCA CAB CBA   -> 3! = 6
Pick and order 2 of 3:        AB AC BA BC CA CB          -> P(3,2) = 3 x 2 = 6
```

```python
import math
from itertools import permutations

print(math.factorial(5), math.perm(5, 2))                    # 120 20
print(list(permutations("ABC")))                             # [('A','B','C'), ('A','C','B'), ... six orderings]
print(len(list(permutations(range(7)))))                     # 5040 = 7!

# Factorial growth is explosive
for n in (5, 10, 15, 20):
    print(n, math.factorial(n))
# 5 120 / 10 3628800 / 15 1307674368000 / 20 2432902008176640000
```

This is why **brute-forcing every ordering** (the travelling salesman problem, trying every schedule) stops working around n = 10-12: `12! = 479,001,600` and `20!` is 2.4 x 10^18.

## 4. Combinations: order does not matter

A **combination** is a **selection** (a subset); order is ignored. Number of ways to choose `k` of `n`:

**C(n, k) = n! / (k! x (n-k)!)** read "n choose k".

```text
Choose 2 of {A, B, C}:  {A,B} {A,C} {B,C}  -> C(3,2) = 3
(AB and BA are the same selection, so we divide the permutations by k! to remove the duplicates.)
```

```python
import math
from itertools import combinations

print(math.comb(5, 2), math.comb(52, 5))                     # 10 2598960   (poker hands)
print(list(combinations("ABCD", 2)))                         # [('A','B'), ('A','C'), ('A','D'), ('B','C'), ('B','D'), ('C','D')]
print(math.comb(10, 3) == math.comb(10, 7))                  # True   (choosing 3 to take = choosing 7 to leave)

# The number of all subsets of an n-element set is 2^n = sum of C(n, k) for k = 0..n
n = 6
assert sum(math.comb(n, k) for k in range(n + 1)) == 2 ** n
```

**Pascal's triangle** builds `C(n, k)`: each number is the sum of the two above it. It appears in dynamic programming ([DP](../../03-algorithms/dynamic-programming/README.md)):

```python
def pascal(rows):
    triangle = [[1]]
    for _ in range(rows - 1):
        prev = triangle[-1]
        triangle.append([1] + [prev[i] + prev[i + 1] for i in range(len(prev) - 1)] + [1])
    return triangle

for row in pascal(5):
    print(row)
# [1] / [1, 1] / [1, 2, 1] / [1, 3, 3, 1] / [1, 4, 6, 4, 1]
assert pascal(10)[9] == [math.comb(9, k) for k in range(10)]
```

### Which formula? A quick guide

| Does order matter? | Repetition allowed? | Count | Example |
|--------------------|---------------------|-------|---------|
| Yes | Yes | `n^k` | 4-digit PIN: 10^4 |
| Yes | No | `P(n, k)` | 1st, 2nd, 3rd prize among 10 runners: 10 x 9 x 8 |
| No | No | `C(n, k)` | Choosing 3 committee members from 10 |
| No | Yes | `C(n + k - 1, k)` | Picking 3 scoops from 5 flavors, repeats allowed |

## 5. Probability basics

**Probability** is a number from 0 (impossible) to 1 (certain): `P(event) = favorable outcomes / total equally likely outcomes`.

| Concept | Meaning | Example |
|---------|---------|---------|
| **Sample space** | All possible outcomes | Rolling a die: {1,...,6} |
| **Event** | A set of outcomes | "even number": {2, 4, 6} |
| `P(A)` | favorable / total | P(even) = 3/6 = 0.5 |
| **Complement** | `P(not A) = 1 - P(A)` | P(not even) = 0.5 |
| **Independent events** | `P(A and B) = P(A) x P(B)` | Two coin flips both heads: 0.5 x 0.5 = 0.25 |
| **Mutually exclusive** | `P(A or B) = P(A) + P(B)` | P(1 or 2) = 1/6 + 1/6 |
| General OR | `P(A or B) = P(A) + P(B) - P(A and B)` | |
| **Conditional** | `P(A given B) = P(A and B) / P(B)` | |

```python
from fractions import Fraction
from itertools import product

die = range(1, 7)
p_even = Fraction(sum(1 for r in die if r % 2 == 0), 6)
print(p_even, 1 - p_even)                                    # 1/2 1/2

# Two dice: probability the sum is 7 (count outcomes exhaustively)
outcomes = list(product(die, repeat=2))
p_seven = Fraction(sum(1 for a, b in outcomes if a + b == 7), len(outcomes))
print(p_seven, float(p_seven))                               # 1/6 0.16666666666666666

# Independent events multiply: three heads in a row
print(Fraction(1, 2) ** 3)                                   # 1/8

# At least one 6 in four rolls = 1 - P(no six at all)
print(round(1 - (5 / 6) ** 4, 4))                            # 0.5177
```

### Simulation (Monte Carlo) to check your reasoning

```python
import random

random.seed(42)
trials = 100_000
hits = sum(1 for _ in range(trials) if sum(random.randint(1, 6) for _ in range(2)) == 7)
print(abs(hits / trials - 1 / 6) < 0.01)                     # True   (the simulation agrees with 1/6)
```

### Expected value: the long-run average

**E[X] = sum of (value x probability)**. A fair die: `(1+2+3+4+5+6)/6 = 3.5`. Expected value is how we reason about **average cost** of randomized algorithms (quicksort with a random pivot: expected `O(n log n)`) and bets.

```python
values = range(1, 7)
print(sum(v * Fraction(1, 6) for v in values))               # 7/2

# A game: pay 3, win 10 on a six, otherwise nothing. Expected profit per play?
print(Fraction(1, 6) * 10 - 3)                               # -4/3  (lose 1.33 on average: a bad bet)
```

## 6. The birthday paradox: why hash collisions come sooner than you think

In a room of just **23 people**, the chance that two share a birthday is over **50%**. The surprise comes from counting **pairs** (253 pairs among 23 people), not people.

```python
def collision_probability(n_items, n_slots):
    """Probability that at least two of n_items land in the same slot (all slots equally likely)."""
    p_no_collision = 1.0
    for i in range(n_items):
        p_no_collision *= (n_slots - i) / n_slots
    return 1 - p_no_collision

print(round(collision_probability(23, 365), 3))              # 0.507
print(round(collision_probability(50, 365), 3))              # 0.97
# Hash tables: with a million slots, 1,200 random keys already have a ~50% chance of a collision
print(round(collision_probability(1200, 1_000_000), 2))      # 0.51
```

This is why **hash tables must handle collisions** ([hash tables](../../02-data-structures/hash-tables/README.md)) and why short random IDs need to be long enough (UUIDs, [system design](../../09-interview-playbook/system-design-basics/README.md)).

## 7. Randomness in Python

```python
import random

random.seed(7)                                               # fixing the seed makes "random" results repeatable (for tests)
print(random.randint(1, 6), random.random() < 1, random.choice(["a", "b", "c"]))
items = [1, 2, 3, 4, 5]
random.shuffle(items)                                        # in-place random permutation
print(sorted(items), random.sample(range(100), 3).__len__())     # [1, 2, 3, 4, 5] 3
```

`random` is **pseudo-random** (fine for games and simulations, predictable if you know the seed). For passwords and tokens use `secrets` (cryptographically secure): `secrets.token_hex(16)`.

## 8. Two real-world examples

**Example 1: How strong is a password?** A password drawn from 94 printable characters with length 10 has `94^10 ≈ 5.4 x 10^19` possibilities. Adding one character multiplies the count by 94. A random 4-word passphrase from a 7,776-word list has `7776^4 ≈ 3.7 x 10^15`: easier to remember, still enormous. Counting rules tell you exactly how much security each design choice buys.

**Example 2: A/B test sanity check.** With 1,000 visitors per variant and a true conversion rate of 10%, you expect 100 conversions, but random variation alone gives a spread of roughly plus or minus 20. Two identical pages routinely differ by 10-20%. Probability tells you how to separate real improvement from luck (statistical significance), which is why engineers should not declare a winner after 50 visitors.

```python
import random
random.seed(1)
def conversions(visitors=1000, rate=0.10):
    return sum(random.random() < rate for _ in range(visitors))
a, b = conversions(), conversions()
print(a, b, abs(a - b))          # two IDENTICAL variants still differ: random noise
```

## 9. Common mistakes

- Using permutations when order does not matter (or combinations when it does).
- Forgetting that factorial and exponential counts explode: always estimate before brute-forcing.
- The **gambler's fallacy**: after five heads, tails is not "due"; independent events have no memory.
- Treating `P(A or B)` as `P(A) + P(B)` when events overlap.
- Using `random` for security tokens.
- Testing a probabilistic function once and concluding it works.

## 10. Practice

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

## 11. Check yourself

1. Sum rule versus product rule?
2. When do you use permutations and when combinations?
3. How many subsets does an n-element set have?
4. What is the probability of getting two heads in a row with a fair coin?
5. What does expected value mean?
6. Why does the birthday paradox matter for hashing?

<details>
<summary>Answers</summary>

1. Sum rule adds the ways for alternative choices; product rule multiplies the ways for sequential independent choices.
2. Permutations when order matters (rankings, arrangements); combinations when only the selection matters (committees, subsets).
3. 2^n.
4. 1/2 x 1/2 = 1/4.
5. The long-run average outcome: the sum of each value times its probability.
6. Collisions occur after about the square root of the table size insertions, so collision handling is essential.

</details>

[Back to math](README.md) · Previous: [logic, sets and proofs](logic-sets-proofs.md) · Next: [sequences, sums and recurrences](sums-and-recurrences.md)
