# What Is an Algorithm?

**Prerequisites:** [Python fundamentals](../00-foundations/python-fundamentals/README.md) (functions and loops). **You will learn:** what an algorithm is, the properties every algorithm needs, how to describe one (plain language, pseudocode, flowchart, code), how to trace one by hand, and why *how well* an algorithm is designed matters as much as whether it works.

## 1. In plain words

An **algorithm** is a **precise, step-by-step recipe for solving a problem**. Like a cooking recipe, it takes **ingredients** (the **input**), follows **clear steps**, and produces a **dish** (the **output**). A good recipe works every time, does not say "season to taste" without saying how much (it is **unambiguous**), and finishes (it **terminates**).

You use algorithms constantly without noticing: looking a word up in a dictionary (open near the middle, decide left or right, repeat), sorting playing cards in your hand, finding the shortest route on a map, dividing a bill. Computer science is largely the study of **which algorithms exist for common problems and how good they are**.

```text
          INPUT                 ALGORITHM                 OUTPUT
   a list of numbers  ───►  "find the largest by       ───►  the largest number
   [3, 9, 2, 7]              scanning once"                   9
```

## 2. The five properties of an algorithm

| Property | Meaning | Violation example |
|----------|---------|-------------------|
| **Input** | zero or more well-defined inputs | "sort the stuff" (what stuff?) |
| **Output** | at least one result related to the input | a procedure that computes but returns nothing |
| **Definiteness** | every step is precise and unambiguous | "add a bit of salt", "pick a good number" |
| **Finiteness** | it ends after a finite number of steps | `while True: pass` |
| **Effectiveness** | each step is basic enough to actually do (by a person with pencil and paper, or a computer) | "decide whether the program will ever halt" (impossible in general) |

Also desirable: **correctness** (it always gives the right answer) and **efficiency** (it does so using reasonable time and memory).

## 3. Describing an algorithm

The same algorithm can be written at different levels of detail.

**Problem: find the largest number in a list.**

**Plain language:** "Remember the first number as the biggest so far. Look at each remaining number in turn; if it is bigger than the one you remember, remember it instead. When you reach the end, the number you remember is the answer."

**Pseudocode** (informal, language-neutral, readable by humans):

```text
FUNCTION find_max(list):
    best ← first item of list
    FOR each item in the rest of the list:
        IF item > best THEN
            best ← item
    RETURN best
```

**Flowchart:**

```text
        ┌─────────────┐
        │   start     │
        └──────┬──────┘
        best = list[0]
               │
        ┌──────▼──────┐   no more items
   ┌───►│ next item?  ├───────────────► RETURN best
   │    └──────┬──────┘
   │      yes  │
   │    ┌──────▼──────┐  no
   │    │ item > best?├─────┐
   │    └──────┬──────┘     │
   │      yes  │            │
   │    best = item         │
   └───────────┴────────────┘
```

**Python:**

```python
def find_max(numbers):
    if not numbers:
        raise ValueError("find_max() needs at least one number")      # the problem is undefined for an empty list
    best = numbers[0]
    for item in numbers[1:]:
        if item > best:
            best = item
    return best

print(find_max([3, 9, 2, 7]), find_max([-5, -2, -9]), find_max([4]))       # 9 -2 4
```

## 4. Tracing an algorithm by hand

**Tracing** (a "dry run") means executing the algorithm on a small example, step by step, recording the variables. It is the most important skill for understanding and debugging algorithms.

Trace `find_max([3, 9, 2, 7])`:

| Step | `item` | `item > best`? | `best` after |
|------|--------|----------------|--------------|
| start | | | 3 |
| 1 | 9 | yes | 9 |
| 2 | 2 | no | 9 |
| 3 | 7 | no | 9 |
| end | | | **9** |

You can make the computer print the trace for you:

```python
def find_max_traced(numbers):
    best = numbers[0]
    print(f"start: best = {best}")
    for item in numbers[1:]:
        bigger = item > best
        if bigger:
            best = item
        print(f"item = {item}, bigger? {bigger}, best = {best}")
    return best

find_max_traced([3, 9, 2, 7])
# start: best = 3
# item = 9, bigger? True, best = 9
# item = 2, bigger? False, best = 9
# item = 7, bigger? False, best = 9
```

## 5. One problem, several algorithms

There is rarely only one way to solve a problem. Computer science asks: **which way is better, and why?**

**Problem: compute `1 + 2 + ... + n`.**

```python
def sum_loop(n):
    total = 0
    for i in range(1, n + 1):        # n additions
        total += i
    return total

def sum_formula(n):
    return n * (n + 1) // 2           # Gauss's formula: 3 operations, whatever n is

def sum_recursive(n):
    return 0 if n == 0 else n + sum_recursive(n - 1)       # n calls (and a deep call stack)

for n in (10, 500):
    assert sum_loop(n) == sum_formula(n) == sum_recursive(n)
print(sum_loop(100), sum_formula(100), sum_recursive(100))                  # 5050 5050 5050
```

All three are **correct**, but compare the work:

| Algorithm | Steps for n = 1,000,000 | Memory | Works for n = 10^9? |
|-----------|-------------------------|--------|---------------------|
| Loop | about 1,000,000 additions | constant | slow (seconds) |
| Formula | 3 operations | constant | instantly |
| Recursion | 1,000,000 calls | 1,000,000 stack frames | crashes (`RecursionError`) |

```python
import time
n = 10_000_000
t = time.perf_counter(); sum_loop(n); loop_time = time.perf_counter() - t
t = time.perf_counter(); sum_formula(n); formula_time = time.perf_counter() - t
print(loop_time > formula_time * 1000)             # True: the formula is thousands of times faster
```

The lesson: **a smarter algorithm beats a faster computer.** Buying a machine that is 10 times faster speeds up the loop 10 times; switching to the formula speeds it up a million times.

### Another classic: Euclid's algorithm (about 300 BC)

Greatest common divisor of two numbers. A naive approach tries every candidate; Euclid noticed `gcd(a, b) = gcd(b, a mod b)`:

```python
def gcd_naive(a, b):
    for d in range(min(a, b), 0, -1):                 # try every candidate from the top
        if a % d == 0 and b % d == 0:
            return d

def gcd_euclid(a, b):
    while b:
        a, b = b, a % b                               # replace the pair by (b, remainder)
    return a

print(gcd_naive(1071, 462), gcd_euclid(1071, 462))                      # 21 21
print(gcd_euclid(10 ** 18 + 1, 10 ** 12 + 7))                           # (instant; the naive version would run for hours)

steps = []
a, b = 1071, 462
while b:
    steps.append((a, b)); a, b = b, a % b
print(steps)                                          # [(1071, 462), (462, 147), (147, 21), (21, 0)]
```

Euclid's algorithm finishes in about `log(min(a, b))` steps: another example of **halving** ([logarithms](../00-foundations/math-for-cs/exponents-and-logarithms.md)).

## 6. Correctness: how do you know it works?

1. **Test** with normal, edge and tricky inputs (empty list, one item, duplicates, negatives).
2. **Reason about it** with an **invariant**: a statement that is true before and after every loop iteration. For `find_max`: "after processing the first `k` items, `best` is the largest of those `k` items". It is true at the start (k = 1), each step keeps it true, so at the end `best` is the largest of all items.
3. **Prove** by induction for recursive algorithms ([proofs](../00-foundations/math-for-cs/logic-sets-proofs.md)).

```python
def find_max_checked(numbers):
    best = numbers[0]
    for k, item in enumerate(numbers[1:], start=2):
        best = item if item > best else best
        assert best == max(numbers[:k]), "invariant broken"      # verify the invariant on every step
    return best

assert find_max_checked([3, 9, 2, 7]) == 9
print("invariant held at every step")
```

## 7. Why efficiency matters

An algorithm's cost depends on its **input size** `n`. For small inputs everything is fast; the difference appears as `n` grows:

```python
def count_pairs_quadratic(items):
    """Count equal pairs by comparing every pair: n*(n-1)/2 comparisons."""
    count = 0
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j]:
                count += 1
    return count

def count_pairs_linear(items):
    """Same answer in one pass using a dictionary of counts."""
    seen, count = {}, 0
    for x in items:
        count += seen.get(x, 0)
        seen[x] = seen.get(x, 0) + 1
    return count

import random, time
random.seed(1)
data = [random.randrange(500) for _ in range(3000)]
t = time.perf_counter(); a = count_pairs_quadratic(data); slow = time.perf_counter() - t
t = time.perf_counter(); b = count_pairs_linear(data); fast = time.perf_counter() - t
print(a == b, slow > fast * 20)          # True True
```

With 3,000 items the quadratic version already takes 4.5 million comparisons; with a million items it would take 500 billion (hours), while the linear version needs one million steps. Measuring and reasoning about this growth is exactly what the rest of this part teaches: [counting steps](02-counting-steps-and-growth.md) and [Big-O notation](03-big-o-omega-theta.md).

## 8. Two real-world examples

**Example 1: Maps and navigation.** Finding the fastest route between two cities among millions of roads is solved by **Dijkstra's algorithm** or **A\*** ([graph algorithms](../03-algorithms/graph-algorithms/README.md)). A naive "try every possible route" algorithm would take longer than the age of the universe; a good algorithm answers in milliseconds. The right algorithm is what makes the product possible at all.

**Example 2: Search engines.** Searching billions of web pages for a word in under a second is possible only because pages were pre-processed into an **inverted index** (a hash table from words to page lists) so a query is a few lookups instead of reading every page. The algorithmic idea (precompute so that queries are cheap) is the product.

## 9. Common mistakes

- Starting to code before understanding the problem (always restate it and try small examples by hand first).
- Not handling edge cases (empty input, one item, duplicates, huge values).
- Confusing an algorithm (the idea) with a program (one implementation of it).
- Assuming "it works on my test" means "it is correct".
- Ignoring efficiency until the data grows (what takes 1 ms for 100 items may take a year for a million).
- Using an overly clever algorithm where a simple one is fast enough.

## 10. Practice

1. Write an algorithm (plain language, pseudocode, Python) that counts how many numbers in a list are even. Trace it on `[4, 7, 10, 3]`.
2. Write the three versions of "sum of the first `n` even numbers" (loop, formula, recursion) and verify they agree. What is the formula?
3. Trace Euclid's algorithm for `gcd(48, 18)` by hand.
4. Describe the algorithm you use to look up a word in a paper dictionary. Which later algorithm does it resemble?
5. Which of these is NOT a valid algorithm, and why? (a) "Find the largest prime" (b) "Add the numbers from 1 to n" (c) "Pick a random good number".

<details>
<summary>Solutions</summary>

**1.**
```python
def count_even(numbers):
    count = 0
    for n in numbers:
        if n % 2 == 0:
            count += 1
    return count
print(count_even([4, 7, 10, 3]))            # 2   (trace: 4 even -> 1; 7 odd; 10 even -> 2; 3 odd)
```

**2.**
```python
def even_sum_loop(n): return sum(2 * i for i in range(1, n + 1))
def even_sum_formula(n): return n * (n + 1)                  # 2 * (1 + ... + n) = n(n+1)
def even_sum_rec(n): return 0 if n == 0 else 2 * n + even_sum_rec(n - 1)
assert even_sum_loop(50) == even_sum_formula(50) == even_sum_rec(50)
```

**3.** `gcd(48, 18)`: `(48, 18) -> (18, 12) -> (12, 6) -> (6, 0)`, answer 6.

**4.** Open near the middle; if the target word comes earlier alphabetically go left, otherwise right; repeat on that half. It is **binary search** ([searching](../03-algorithms/searching/README.md)).

**5.** (a) is not valid: there is no largest prime (the problem has no answer). (b) is valid. (c) is not definite: "good" is not precisely defined.

</details>

## 11. Check yourself

1. What are the five properties of an algorithm?
2. What is the difference between an algorithm and a program?
3. What does tracing an algorithm mean?
4. What is a loop invariant?
5. Why might a faster computer not fix a slow algorithm?

<details>
<summary>Answers</summary>

1. Input, output, definiteness, finiteness, effectiveness.
2. An algorithm is the idea (the steps); a program is one implementation of it in a language.
3. Executing it by hand on a small example while recording the variables after each step.
4. A condition that is true before and after every iteration of a loop; it is used to argue correctness.
5. Speeding up the hardware changes the cost by a constant factor, but a better algorithm can change how the cost *grows* with input size, which matters far more at scale.

</details>

[Back to complexity](README.md) · Next: [counting steps and growth](02-counting-steps-and-growth.md)
