# Logic, Sets and Proofs

**Prerequisites:** none. **You will learn:** the boolean logic behind every `if`, truth tables, De Morgan's laws, sets and their operations, and how to prove statements with **induction**. These tools underlie programming, databases (set operations in SQL), algorithms and correctness arguments.

## 1. In plain words

**Logic** is the study of true and false statements and how they combine. Every condition in your code (`if age >= 18 and has_id`) is a logical expression. **Sets** are collections of distinct things, with operations like union and intersection (also how SQL `JOIN`, `UNION` and Python `set` work). **Proof** means showing a claim is true for *all* cases, not just the ones you tested; **induction** is the most common technique in computer science.

## 2. Boolean logic

A **proposition** is a statement that is either **True** or **False**. Three basic operators combine them:

| Operator | Python | Meaning | True when... |
|----------|--------|---------|--------------|
| **AND** | `and` | both | both sides are true |
| **OR** | `or` | at least one | either side (or both) is true |
| **NOT** | `not` | opposite | the operand is false |

### Truth tables

A **truth table** lists every combination of inputs and the output.

| A | B | A and B | A or B | not A | A xor B (exactly one) |
|---|---|---------|--------|-------|-----------------------|
| F | F | F | F | T | F |
| F | T | F | T | T | T |
| T | F | F | T | F | T |
| T | T | T | T | F | F |

```python
from itertools import product

print("A     B     and    or     xor")
for a, b in product([False, True], repeat=2):
    print(f"{a!s:5} {b!s:5} {(a and b)!s:6} {(a or b)!s:6} {(a != b)!s}")
```

Other useful operators: **implication** (`A -> B` is false only when A is true and B is false: "if it rains then I take an umbrella") written in Python as `(not a) or b`, and **equivalence** (`A <-> B`, true when they match: `a == b`).

### Laws you will use constantly

| Law | Statement |
|-----|-----------|
| **De Morgan** | `not (A and B) == (not A) or (not B)`, and `not (A or B) == (not A) and (not B)` |
| Double negation | `not not A == A` |
| Distributive | `A and (B or C) == (A and B) or (A and C)` |
| Identity / domination | `A and True == A`, `A or False == A`, `A and False == False`, `A or True == True` |
| Short circuit | `False and x` never evaluates `x`; `True or x` never evaluates `x` |

```python
from itertools import product

# Verify De Morgan's laws by checking every possible input (a truth-table proof)
for a, b in product([False, True], repeat=2):
    assert (not (a and b)) == ((not a) or (not b))
    assert (not (a or b)) == ((not a) and (not b))
print("De Morgan verified for all 4 cases")

# Simplifying conditions (readability and bug-hunting)
age, has_ticket = 17, True
blocked = not (age >= 18 and has_ticket)             # reads awkwardly
blocked_simple = age < 18 or not has_ticket          # De Morgan applied
print(blocked == blocked_simple)                     # True

# Short-circuit evaluation protects against errors
items = []
print(bool(items) and items[0] == "x")               # False (items[0] never evaluated, so no IndexError)
print(items or ["default"])                          # ['default']  (or returns the first truthy operand)
```

**Truthiness in Python:** `False`, `None`, `0`, `0.0`, `""`, `[]`, `{}`, `()` and `set()` are "falsy"; everything else is truthy. Use explicit comparisons (`if x is None`) when 0 or empty is a valid value.

### Logic in hardware

Computer chips are built from **logic gates** (AND, OR, NOT, XOR). Adding two bits is just two gates: the sum is XOR, the carry is AND. Chaining them builds an adder, and adders build the ALU of the [CPU](../computer-basics/how-computers-work.md).

```python
def half_adder(a, b):
    return a ^ b, a & b              # (sum bit, carry bit)

def full_adder(a, b, carry_in):
    s1, c1 = half_adder(a, b)
    s2, c2 = half_adder(s1, carry_in)
    return s2, c1 | c2

def add_bits(x, y, width=8):
    """Add two numbers using only gate-level logic, one bit at a time."""
    carry, result = 0, 0
    for i in range(width):
        bit, carry = full_adder((x >> i) & 1, (y >> i) & 1, carry)
        result |= bit << i
    return result

print(add_bits(23, 42), add_bits(100, 55))           # 65 155
assert all(add_bits(a, b, 16) == a + b for a in range(0, 300, 7) for b in range(0, 300, 11))
```

## 3. Sets

A **set** is an unordered collection of **distinct** elements. Python's `set` is a hash-based implementation (O(1) membership; see [hash tables](../../02-data-structures/hash-tables/README.md)).

| Math notation | Meaning | Python | Venn picture |
|---------------|---------|--------|--------------|
| `x ∈ A` | x is in A | `x in A` | a dot inside circle A |
| `A ∪ B` | **union**: in A or B or both | `A \| B` | both circles |
| `A ∩ B` | **intersection**: in both | `A & B` | the overlap |
| `A − B` | **difference**: in A but not B | `A - B` | A without the overlap |
| `A △ B` | **symmetric difference**: in exactly one | `A ^ B` | both circles minus the overlap |
| `A ⊆ B` | A is a **subset** of B | `A <= B` | A entirely inside B |
| `|A|` | **cardinality** (size) | `len(A)` | |
| `∅` | empty set | `set()` | |

```python
A = {1, 2, 3, 4}
B = {3, 4, 5, 6}
print(A | B, A & B, A - B, A ^ B)          # {1, 2, 3, 4, 5, 6} {3, 4} {1, 2} {1, 2, 5, 6}
print({3, 4} <= A, A <= B, 3 in A, len(A))          # True False True 4
print(set([1, 1, 2, 2, 3]))                # {1, 2, 3}   (duplicates vanish: deduplicate a list)

# Inclusion-exclusion: |A ∪ B| = |A| + |B| - |A ∩ B|
assert len(A | B) == len(A) + len(B) - len(A & B)

# Power set: all subsets, 2^n of them
from itertools import chain, combinations
def power_set(s):
    s = list(s)
    return list(chain.from_iterable(combinations(s, r) for r in range(len(s) + 1)))
print(len(power_set({1, 2, 3})), power_set({1, 2}))     # 8 [(), (1,), (2,), (1, 2)]
```

Sets in daily programming: **remove duplicates**, **fast membership tests**, **find common/different items** (users in both groups, files only in one folder), and the set operations behind SQL (`INNER JOIN` is like intersection, `UNION`, `EXCEPT`).

```python
group_a = {"ana", "bo", "cy"}
group_b = {"bo", "cy", "di"}
print("in both:", sorted(group_a & group_b))                 # in both: ['bo', 'cy']
print("only in A:", sorted(group_a - group_b))               # only in A: ['ana']
print("everyone:", sorted(group_a | group_b))                # everyone: ['ana', 'bo', 'cy', 'di']
```

### Relations and functions (the vocabulary)

- A **function** maps each input to **exactly one** output (`f(x) = x^2`). Python dictionaries are functions you can store.
- **Injective** (one-to-one): different inputs give different outputs. **Surjective** (onto): every possible output is hit. **Bijective**: both, so it can be reversed (like encoding and decoding).
- A hash function is **not** injective (collisions exist), which is why hash tables handle collisions.

## 4. Quantifiers: "for all" and "there exists"

| Symbol | Meaning | Python |
|--------|---------|--------|
| `∀` (for all) | the claim holds for every element | `all(...)` |
| `∃` (there exists) | at least one element satisfies it | `any(...)` |

```python
nums = [2, 4, 6, 8]
print(all(n % 2 == 0 for n in nums))      # True   ∀ n: n is even
print(any(n > 7 for n in nums))           # True   ∃ n: n > 7
print(all([]), any([]))                   # True False   (vacuous truth: nothing to contradict "for all")
```

**Negating quantifiers** (a favorite exam question): `not (∀x P(x))` is `∃x not P(x)`. To disprove "all numbers are even", find **one counterexample**. A single counterexample disproves a "for all" claim; examples can never prove one.

## 5. Proof techniques

Testing checks some cases; **proof** covers all of them. Four techniques:

1. **Direct proof**: start from assumptions, reason step by step. *Claim: the sum of two even numbers is even.* Let a = 2m, b = 2n; then a + b = 2(m + n), which is even.
2. **Proof by contradiction**: assume the claim is false and derive an impossibility. *Claim: there is no largest integer.* Suppose N is the largest; N + 1 is larger: contradiction.
3. **Counterexample**: disprove a "for all" claim with one failing case. *Claim "n^2 + n + 41 is prime for all n"* fails at n = 40.
4. **Mathematical induction**: prove a claim for all natural numbers (below).

```python
# The counterexample: n^2 + n + 41 looks prime for many n, but not all
def is_prime(n):
    return n > 1 and all(n % d for d in range(2, int(n ** 0.5) + 1))
print(all(is_prime(n * n + n + 41) for n in range(40)))      # True for n = 0..39
print(is_prime(40 * 40 + 40 + 41), 40 * 40 + 40 + 41)        # False 1681   (1681 = 41 * 41)
```

### Mathematical induction

Induction proves a statement `P(n)` for **every** `n = 0, 1, 2, ...` like toppling dominoes:

1. **Base case:** show `P(0)` (or `P(1)`) is true: the first domino falls.
2. **Inductive step:** show that **if** `P(k)` is true **then** `P(k + 1)` is true: each domino knocks over the next.
3. Therefore `P(n)` holds for all `n`.

**Example: the sum 1 + 2 + ... + n equals n(n + 1)/2.**

- Base case: n = 1: left side is 1, right side is 1 x 2 / 2 = 1. ✓
- Inductive step: assume `1 + ... + k = k(k + 1)/2`. Then `1 + ... + k + (k + 1) = k(k + 1)/2 + (k + 1) = (k + 1)(k + 2)/2`, which is the formula for `k + 1`. ✓

```python
# A computer check is NOT a proof, but it builds confidence
assert all(sum(range(1, n + 1)) == n * (n + 1) // 2 for n in range(1, 500))

# Induction is also how we prove that RECURSIVE algorithms work:
def power(x, n):
    """Claim: power(x, n) == x**n for every integer n >= 0."""
    if n == 0:
        return 1                         # base case: x^0 = 1
    return x * power(x, n - 1)           # inductive step: relies on the claim for n - 1
assert all(power(3, n) == 3 ** n for n in range(10))
print("ok")
```

Recursion and induction are twins: the **base case** of the recursion is the base case of the proof, and the **recursive call** relies on the **inductive hypothesis**. When you write a recursive function you are really writing an inductive proof. Loop **invariants** (a fact true before and after each iteration) are the same idea for loops.

## 6. Two real-world examples

**Example 1: Debugging a complicated condition.** A permissions check `if not (is_admin or (is_owner and not is_locked))` is hard to read. Applying De Morgan gives `if not is_admin and (not is_owner or is_locked)`, which says plainly: "deny non-admins who are either not the owner or whose item is locked". Truth-table testing (all `2^3` combinations) proves the rewrite is equivalent before you ship it.

**Example 2: Set operations on real data.** An email service computes who to notify: `subscribers - unsubscribed - bounced` (set difference), who is in both lists `newsletter & beta_testers` (intersection), and total unique audience `a | b | c` (union). In SQL the same logic is `EXCEPT`, `INTERSECT`, `UNION`. Sets make the code short and obviously correct.

## 7. Common mistakes

- Confusing `and`/`or` precedence (`and` binds tighter): use parentheses.
- Writing `if x == 1 or 2:` (always true) instead of `if x == 1 or x == 2:` or `x in (1, 2)`.
- Assuming a few passing tests prove a claim for all inputs.
- Forgetting that sets are unordered (no indexing) and hold only hashable items.
- Skipping the **base case** in induction/recursion.
- Using `is` or `==` on booleans where truthiness would be clearer (or vice versa).

## 8. Practice

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

## 9. Check yourself

1. What does De Morgan's law say?
2. What is the difference between `A | B` and `A & B` for sets?
3. How do you disprove a "for all" statement?
4. What are the two steps of induction?
5. How are recursion and induction related?
6. Why is `all([])` True?

<details>
<summary>Answers</summary>

1. The negation of an AND is the OR of the negations, and the negation of an OR is the AND of the negations.
2. Union keeps elements in either set; intersection keeps only elements in both.
3. With a single counterexample.
4. The base case, and the inductive step (if true for k then true for k + 1).
5. The base case of a recursive function matches the base case of the proof; the recursive call matches the inductive hypothesis.
6. Vacuous truth: with no elements, there is nothing that violates the claim.

</details>

[Back to math](README.md) · Previous: [exponents and logarithms](exponents-and-logarithms.md) · Next: [counting and probability](counting-and-probability.md)
