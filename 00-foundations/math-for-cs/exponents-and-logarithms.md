# Exponents, Logarithms and Growth

**Prerequisites:** school algebra. **You will learn:** the powers and logarithms that appear in every analysis of algorithms (`n^2`, `2^n`, `log n`), why logarithms mean "how many times can I halve this?", and how fast different functions grow.

## 1. In plain words

- An **exponent** says "multiply this number by itself that many times": `2^5 = 2 x 2 x 2 x 2 x 2 = 32`.
- A **logarithm** is the **opposite question**: "to what power must I raise 2 to get 32?" Answer: 5. So `log2(32) = 5`.

In computing, base 2 is everywhere (bits, halving, doubling), so **log2(n) answers: "how many times can I cut n in half until I reach 1?"** That is why binary search on a million items needs only about 20 steps.

```text
Exponent:  2^5  = 32          (grow: multiply by 2, five times)
Logarithm: log2(32) = 5       (shrink: halve 32 until reaching 1: 32 -> 16 -> 8 -> 4 -> 2 -> 1, five halvings)
```

## 2. Exponent rules (memorize these four)

| Rule | Example |
|------|---------|
| `a^m x a^n = a^(m+n)` | `2^3 x 2^4 = 2^7 = 128` |
| `a^m / a^n = a^(m-n)` | `2^7 / 2^4 = 2^3 = 8` |
| `(a^m)^n = a^(m x n)` | `(2^3)^2 = 2^6 = 64` |
| `a^0 = 1`, `a^(-n) = 1 / a^n` | `2^0 = 1`, `2^-3 = 1/8` |

```python
print(2 ** 5, 2 ** 3 * 2 ** 4 == 2 ** 7, (2 ** 3) ** 2 == 2 ** 6, 2 ** 0, 2 ** -3)    # 32 True True 1 0.125
print(10 ** 6, 10 ** 9, 2 ** 10, 2 ** 20, 2 ** 30)       # 1000000 1000000000 1024 1048576 1073741824
```

Useful anchors: `2^10 = 1,024` (about a thousand), `2^20` is about a million, `2^30` about a billion, `2^32` about 4.3 billion, `2^64` about 1.8 x 10^19.

## 3. Logarithm rules

`log_b(x) = y` means `b^y = x`.

| Rule | Example |
|------|---------|
| `log(a x b) = log a + log b` | `log2(8 x 4) = 3 + 2 = 5` |
| `log(a / b) = log a - log b` | `log2(32 / 4) = 5 - 2 = 3` |
| `log(a^k) = k x log a` | `log2(8^2) = 2 x 3 = 6` |
| change of base: `log_b(x) = log_c(x) / log_c(b)` | `log10(1000) = 3`; `log2(1000) = 3 / log10(2) ≈ 9.97` |

```python
import math

print(math.log2(32), math.log2(1024), math.log10(1000), math.log(math.e))     # 5.0 10.0 3.0 1.0
print(math.log2(8 * 4) == math.log2(8) + math.log2(4))                        # True
print(round(math.log2(1000), 2), round(math.log(1000) / math.log(2), 2))      # 9.97 9.97   (change of base)
print(math.ceil(math.log2(1_000_000)))                                        # 20   (a million items need about 20 halvings)
```

**In Big-O the base of a logarithm does not matter**: `log2(n)`, `log10(n)` and `ln(n)` differ only by a constant factor (change of base), so we just write `O(log n)`.

## 4. Logarithms in algorithms: counting halvings

```python
def halvings(n):
    """How many times can n be halved (integer division) until it reaches 1?"""
    steps = 0
    while n > 1:
        n //= 2
        steps += 1
    return steps

for n in (8, 1_000, 1_000_000, 1_000_000_000):
    print(f"n = {n:>13,}  halvings = {halvings(n):>2}   log2(n) = {math.log2(n):.1f}")
# n =             8  halvings =  3   log2(n) = 3.0
# n =         1,000  halvings =  9   log2(n) = 10.0
# n =     1,000,000  halvings = 19   log2(n) = 19.9
# n = 1,000,000,000  halvings = 29   log2(n) = 29.9
```

A **billion** items can be halved down to one in only **about 30 steps**. That is the superpower of **binary search**, **balanced trees** and **heaps**: they all work by repeatedly halving the problem, which is why they take `O(log n)` time. See [searching](../../03-algorithms/searching/README.md).

The same number also tells you **how many bits** are needed to count to `n`:

```python
for n in (255, 256, 1000, 1_000_000):
    print(n, "needs", n.bit_length(), "bits")        # 255 needs 8 bits, 256 needs 9, 1000 needs 10, 1000000 needs 20
```

## 5. How fast do functions grow?

This table is the heart of algorithm analysis. Compare how many "steps" an algorithm needs for different input sizes `n`:

| Name | Function | n = 10 | n = 100 | n = 1,000 | n = 1,000,000 |
|------|----------|--------|---------|-----------|----------------|
| Constant | 1 | 1 | 1 | 1 | 1 |
| **Logarithmic** | log n | 3 | 7 | 10 | 20 |
| Linear | n | 10 | 100 | 1,000 | 1,000,000 |
| **Linearithmic** | n log n | 33 | 664 | 9,966 | 19,931,569 |
| Quadratic | n^2 | 100 | 10,000 | 1,000,000 | 10^12 |
| Cubic | n^3 | 1,000 | 10^6 | 10^9 | 10^18 |
| **Exponential** | 2^n | 1,024 | 10^30 | 10^301 | impossible |
| Factorial | n! | 3,628,800 | 10^158 | huge | impossible |

```python
import math

def steps(n):
    return {
        "log n": round(math.log2(n)),
        "n": n,
        "n log n": round(n * math.log2(n)),
        "n^2": n ** 2,
        "2^n": 2 ** n if n <= 60 else float("inf"),
    }

for n in (10, 20, 40):
    print(n, steps(n))
# 10 {'log n': 3, 'n': 10, 'n log n': 33, 'n^2': 100, '2^n': 1024}
# 20 {'log n': 4, 'n': 20, 'n log n': 86, 'n^2': 400, '2^n': 1048576}
# 40 {'log n': 5, 'n': 40, 'n log n': 213, 'n^2': 1600, '2^n': 1099511627776}
```

**Reading the table:** if a computer does about 10^8 simple steps per second, then for `n = 1,000,000`: `O(n)` takes 0.01 s, `O(n log n)` about 0.2 s, `O(n^2)` takes **about 3 hours**, and `O(2^n)` would outlive the universe. The shape of the growth decides whether a program is usable. Details in [Big-O](../../01-complexity/big-o/README.md).

### Seeing the growth

```python
import math

print(f"{'n':>7} {'log n':>7} {'n':>9} {'n log n':>12} {'n^2':>16}")
for n in (10, 100, 1_000, 10_000):
    print(f"{n:>7} {math.log2(n):>7.1f} {n:>9} {n * math.log2(n):>12.0f} {n ** 2:>16}")
```

Double the input and see what happens: `n` doubles, `n log n` a little more than doubles, `n^2` becomes **4x**, `2^n` is **squared** (for `n -> n + 1` it merely doubles).

## 6. Other handy math functions

```python
import math

print(math.factorial(5), math.comb(5, 2), math.perm(5, 2))     # 120 10 20
print(math.sqrt(144), math.isqrt(150), math.gcd(84, 36), math.lcm(4, 6))      # 12.0 12 12 12
print(math.floor(3.7), math.ceil(3.2), round(3.5), round(2.5), int(-3.7))     # 3 4 4 2 -3
print(7 // 2, -7 // 2, 7 % 3, -7 % 3, divmod(17, 5))           # 3 -4 1 2 (3, 2)
print(abs(-5), min(3, 1, 2), max([4, 9, 2]), sum(range(1, 101)), pow(2, 10, 1000))   # 5 1 9 5050 24
```

`pow(base, exp, mod)` computes `base^exp mod m` quickly even for huge numbers (used in cryptography). `//` is floor division (rounds toward negative infinity) and `%` the remainder; `divmod` gives both.

## 7. Two real-world examples

**Example 1: Why phone contact search stays instant.** With 1,000,000 sorted contacts, a linear scan needs up to a million comparisons, but binary search needs about 20 (`log2(1,000,000) ≈ 20`). Even at 1 billion contacts it would need about 30. Logarithmic growth is the reason databases (B-tree indexes) can find a row in a table of billions in a few steps.

**Example 2: Why brute-force password cracking gets exponentially harder.** A password of `L` characters from an alphabet of `A` symbols has `A^L` possibilities. For 62 symbols: 6 characters is 5.7 x 10^10 (hours), 8 characters is 2.2 x 10^14 (years at the same rate), 12 characters is 3.2 x 10^21. Each extra character multiplies the work by 62: that is **exponential growth working in your favor**.

```python
for length in (6, 8, 10, 12):
    combos = 62 ** length
    seconds = combos / 10_000_000_000                   # assume 10 billion guesses per second
    print(length, f"{combos:.2e}", f"{seconds / 86400:,.1f} days")
# 6 5.68e+10 0.0 days / 8 2.18e+14 0.3 days / 10 8.39e+17 971.4 days / 12 3.23e+21 3,734,105.0 days
```

## 8. Common mistakes

- Confusing `n^2` (polynomial) with `2^n` (exponential): `n = 50` gives 2,500 versus 10^15.
- Forgetting that in Big-O the log base is irrelevant.
- Thinking `log n` is "almost constant" is *useful* for large n, but it is not exactly constant: for tiny n the constants dominate.
- Mixing `^` (XOR) with `**` (power) in Python.
- Using `math.log` (natural log) when you meant `log2`.

## 9. Practice

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

## 10. Check yourself

1. What does `log2(n)` mean in plain words?
2. Why does the base of the logarithm not matter in Big-O?
3. About how many steps does binary search need for 1,000,000 items?
4. What happens to `n^2` if you double `n`? To `2^n` if you add 1 to `n`?
5. Which grows faster, `n^100` or `2^n`?

<details>
<summary>Answers</summary>

1. How many times you can halve `n` before reaching 1 (or the number of bits needed to count to `n`).
2. Changing the base multiplies the logarithm by a constant, and Big-O ignores constant factors.
3. About 20.
4. `n^2` becomes 4 times larger; `2^n` becomes twice as large.
5. `2^n`: exponential growth eventually beats any polynomial, even if only for very large `n`.

</details>

[Back to math](README.md) · Next: [logic, sets and proofs](logic-sets-proofs.md)
