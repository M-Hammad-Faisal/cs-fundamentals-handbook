# Number Theory for Programmers

**Prerequisites:** [exponents and logarithms](../../00-foundations/math-for-cs/exponents-and-logarithms.md), [loops and recursion](../recursion-backtracking/01-recursion-fundamentals.md), [binary search](../searching/01-linear-and-binary-search.md) (helps). **You will learn:** the number-theory toolkit that appears in hashing, cryptography, interviews and competitive programming: **divisibility and GCD** (Euclid's algorithm), **modular arithmetic**, **fast exponentiation**, **modular inverses**, **primes** (sieve of Eratosthenes, primality tests, factorization), **combinatorics modulo a prime**, and **fast Fibonacci**. Every function is checked against a brute-force version.

## 1. In plain words

Number theory studies whole numbers: divisibility, remainders and primes. It matters to programmers because computers work with **integers of fixed size** (so results must be reduced with `%`), because **hash tables, checksums, random generators and encryption** are built on remainders, and because many "count the ways, modulo 1 000 000 007" problems need these tools to avoid astronomically large numbers.

## 2. Divisibility, remainders and `%`

`a % m` is the remainder when `a` is divided by `m`. Key facts:

```python
print(17 % 5, -17 % 5, 17 // 5, -17 // 5)           # 2 3 3 -4    Python's % is never negative for a positive modulus
print(divmod(17, 5), divmod(-17, 5))                 # (3, 2) (-4, 3)
print(12 % 4 == 0, 10 % 4 == 0)                      # True False   "4 divides 12"
```

`a % m` always lands in `0 .. m-1`, and `(a // m) * m + a % m == a`. Remainders let us build **cycles**: a clock face is arithmetic mod 12, weekdays are mod 7.

## 3. GCD: the greatest common divisor

`gcd(a, b)` is the largest number dividing both. **Euclid's algorithm** (about 2300 years old) rests on one fact: `gcd(a, b) = gcd(b, a % b)`, and `gcd(a, 0) = a`.

```text
gcd(48, 18):  48 % 18 = 12  ->  gcd(18, 12)
              18 % 12 = 6   ->  gcd(12, 6)
              12 % 6  = 0   ->  gcd(6, 0) = 6
```

```python
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def lcm(a, b):
    return a // gcd(a, b) * b                        # divide first to keep numbers small

import math, random
random.seed(1)
for _ in range(2000):
    a, b = random.randint(1, 10**6), random.randint(1, 10**6)
    assert gcd(a, b) == math.gcd(a, b) and lcm(a, b) == math.lcm(a, b)
print(gcd(48, 18), lcm(4, 6), gcd(17, 5), gcd(0, 9))                # 6 12 1 9
```

It needs only `O(log min(a, b))` steps (each two steps at least halve the numbers), so even 1000-digit numbers take a few thousand steps. Two numbers with `gcd = 1` are **coprime**. A fraction reduces by dividing by the gcd: `from fractions import Fraction` does exactly that.

### Extended Euclid: Bezout's identity

There always exist integers `x, y` with `a*x + b*y = gcd(a, b)`. The **extended Euclidean algorithm** finds them, and that is the key to modular inverses.

```python
def extended_gcd(a, b):
    if b == 0:
        return a, 1, 0                               # gcd(a, 0) = a = a*1 + 0*0
    g, x, y = extended_gcd(b, a % b)
    return g, y, x - (a // b) * y                    # back-substitute

g, x, y = extended_gcd(240, 46)
print(g, x, y, 240 * x + 46 * y == g)                # 2 -9 47 True
```

## 4. Modular arithmetic

Working "mod m" means we only care about remainders. The rules let you reduce **at every step**, so numbers never grow:

```text
(a + b) mod m = ((a mod m) + (b mod m)) mod m
(a * b) mod m = ((a mod m) * (b mod m)) mod m
(a - b) mod m = ((a mod m) - (b mod m)) mod m          (Python keeps it non-negative)
division is NOT this simple: see modular inverses below
```

```python
M = 1_000_000_007                                    # a famous prime modulus (about 10^9)
a, b = 123_456_789_012, 987_654_321_098
print((a * b) % M == ((a % M) * (b % M)) % M)        # True

def factorial_mod(n, m):
    result = 1
    for k in range(2, n + 1):
        result = result * k % m                      # reduce every step: the intermediate never exceeds m * n
    return result

print(factorial_mod(20, 10**19) == math.factorial(20), factorial_mod(100_000, M))
# True 457992974       (the last number is 100000! mod 1000000007; the true value has 456 574 digits)
```

(`10^9 + 7` is popular because it is prime and its square still fits in a 64-bit integer, which matters in C and Java; Python integers never overflow.)

Real uses: **hash functions** (`h * 31 + c) % table_size`), **clocks and calendars**, **random number generators** (`x_next = (a * x + c) % m`), **checksums** (ISBN, credit-card Luhn), **cryptography**.

## 5. Fast exponentiation (binary exponentiation)

Computing `a^n` with `n - 1` multiplications is hopeless for huge `n`. **Square and halve:** `a^n = (a^(n/2))^2` for even `n`, and `a * a^(n-1)` for odd `n`. That is `O(log n)` multiplications.

```python
def power(a, n):
    result = 1
    while n:
        if n & 1:                                    # this bit of n is 1: multiply the current power in
            result *= a
        a *= a                                       # a, a^2, a^4, a^8, ...
        n >>= 1
    return result

def power_mod(a, n, m):
    result, a = 1, a % m
    while n:
        if n & 1:
            result = result * a % m
        a = a * a % m
        n >>= 1
    return result

print(power(3, 13), 3 ** 13)                         # 1594323 1594323     13 = 0b1101: multiplies by 3^1, 3^4, 3^8
print(power_mod(2, 10**18, M), pow(2, 10**18, M))    # 719476260 719476260   pow(a, n, m) is built into Python and does exactly this
```

Trace for `3^13` (binary `1101`): bits from the right: 1 (multiply by 3), 0 (skip, square to 3^2... ), 1 (multiply by 3^4), 1 (multiply by 3^8): `3 * 81 * 6561 = 1 594 323`. Only 4 squarings instead of 12 multiplications; for `n = 10^18` it is about 60 steps.

The same trick (`O(log n)`) computes **matrix powers**, which gives fast Fibonacci (section 9).

## 6. Modular inverse and division

In ordinary arithmetic you divide by multiplying by `1/b`. Modulo `m`, the **inverse** of `b` is a number `b^-1` with `b * b^-1 = 1 (mod m)`. It exists exactly when `gcd(b, m) = 1`.

- **Via extended Euclid** (works for any `m`): the `x` in `b*x + m*y = 1`.
- **Via Fermat's little theorem** (prime `m`): `b^(m-1) = 1 (mod m)`, so `b^-1 = b^(m-2) mod m`.

```python
def mod_inverse(b, m):
    g, x, _ = extended_gcd(b % m, m)
    if g != 1:
        raise ValueError(f"{b} has no inverse modulo {m}")
    return x % m

print(mod_inverse(3, 11), 3 * mod_inverse(3, 11) % 11)         # 4 1      3 * 4 = 12 = 1 (mod 11)
print(mod_inverse(7, M), pow(7, M - 2, M), pow(7, -1, M))      # 142857144 142857144 142857144   (Python 3.8+ has pow(b, -1, m))
try:
    mod_inverse(6, 9)                                           # gcd(6, 9) = 3: no inverse
except ValueError as e:
    print(e)                                                    # 6 has no inverse modulo 9

# division mod p:  (a / b) mod p = a * inverse(b) mod p
print(10 * pow(4, -1, M) % M)                                   # 500000006    (the value of 10/4 = 5/2 modulo 10^9+7)
print(500000006 * 2 % M)                                        # 5            multiplying back by 2 gives 5, so it behaves like 5/2
```

**RSA** (see the [TLS lab](../../07-networking/tls-security/01-cryptography-and-tls-lab.md)) uses exactly these ingredients: `d = e^-1 mod phi(n)` and fast `power_mod` for encryption.

## 7. Primes

A **prime** has exactly two divisors (1 and itself). Primes are the building blocks: every integer above 1 factors uniquely into primes (the **fundamental theorem of arithmetic**).

### Trial division

A number `n` is composite if it has a divisor up to `sqrt(n)` (if `n = a * b` then one of the two is at most `sqrt(n)`).

```python
def is_prime_trial(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True

print([n for n in range(30) if is_prime_trial(n)])              # [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
print(is_prime_trial(1_000_000_007), is_prime_trial(1_000_000_007 * 3))     # True False
```

Cost `O(sqrt n)`: instant for `10^9`, hopeless for 100-digit numbers.

### The sieve of Eratosthenes: all primes up to N

Cross out multiples: start with 2, remove 4, 6, 8, ...; the next survivor (3) is prime, remove its multiples; and so on. Only primes up to `sqrt(N)` need to be used.

```text
2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 ...
2 3 . 5 . 7 . 9 .  11 .  13 .  15 .       after crossing out multiples of 2
2 3 . 5 . 7 . . .  11 .  13 .  .  .       after crossing out multiples of 3: what remains is prime
```

```python
def sieve(limit):
    is_p = bytearray([1]) * (limit + 1)
    is_p[0:2] = b"\x00\x00"
    for p in range(2, int(limit ** 0.5) + 1):
        if is_p[p]:
            is_p[p * p::p] = bytearray(len(range(p * p, limit + 1, p)))      # cross out multiples starting at p*p
    return [i for i, flag in enumerate(is_p) if flag]

primes = sieve(100)
print(primes)                                                    # [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
print(len(sieve(1_000_000)), len(sieve(10_000_000)))             # 78498 664579
assert sieve(5000) == [n for n in range(5001) if is_prime_trial(n)]
```

Time `O(N log log N)`, nearly linear; 10 million in about a second. The **prime number theorem** says there are about `N / ln N` primes up to `N` (1 in 7 near ten million).

### Primality testing for huge numbers: Miller-Rabin

Trial division cannot test a 300-digit number. **Miller-Rabin** is a fast probabilistic test: it checks a property that every prime satisfies but most composites fail. With the right fixed bases it is **deterministic for all 64-bit integers**.

```python
def is_prime(n):
    if n < 2:
        return False
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for p in small:
        if n % p == 0:
            return n == p
    d, r = n - 1, 0
    while d % 2 == 0:                                           # write n - 1 = d * 2^r with d odd
        d //= 2
        r += 1
    for a in small:                                             # these 12 bases are enough for every n < 3.3 * 10^24
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False                                        # a witness proves n is composite
    return True

assert all(is_prime(n) == is_prime_trial(n) for n in range(20_000))
print(is_prime(2**61 - 1), is_prime(2**61 + 1), is_prime(10**18 + 9))        # True False True   (2^61 - 1 is a Mersenne prime)
print(is_prime(561), is_prime_trial(561))                                     # False False       561 = 3*11*17 fools the simple Fermat test, not Miller-Rabin
```

For cryptographic key generation the same test with random bases is used to find primes hundreds of digits long.

### Prime factorization

```python
def factorize(n):
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        factors[n] = factors.get(n, 0) + 1                      # whatever is left is a prime
    return factors

print(factorize(360), factorize(97), factorize(10**12 - 1))
# {2: 3, 3: 2, 5: 1} {97: 1} {3: 3, 7: 1, 11: 1, 13: 1, 37: 1, 101: 1, 9901: 1}
```

Trial division factors numbers up to about `10^12` quickly. Factoring *large* semiprimes (a product of two big primes) is believed to be hard: that difficulty **is** RSA's security.

Divisor counts and sums follow from the factorization: if `n = p1^a1 * p2^a2 ...` then the number of divisors is `(a1 + 1)(a2 + 1)...`:

```python
def divisor_count(n):
    count = 1
    for exponent in factorize(n).values():
        count *= exponent + 1
    return count

print(divisor_count(360), sum(1 for d in range(1, 361) if 360 % d == 0))                # 24 24
```

For many factorizations, compute a **smallest-prime-factor sieve** once, then factorize each number in `O(log n)`.

## 8. Euler's totient and combinatorics mod p

**Euler's totient** `phi(n)` counts numbers in `1..n` coprime to `n`. For `n = p1^a1 ...`: `phi(n) = n * product(1 - 1/p)`. For a prime `p`, `phi(p) = p - 1`. Euler's theorem: `a^phi(n) = 1 (mod n)` when `gcd(a, n) = 1` (Fermat's is the prime case); RSA's `phi(n) = (p-1)(q-1)`.

```python
def totient(n):
    result = n
    for p in factorize(n):
        result -= result // p
    return result

print(totient(36), sum(1 for k in range(1, 37) if gcd(k, 36) == 1))      # 12 12
print(pow(5, totient(36), 36), pow(5, 12, 36))                           # 1 1    Euler's theorem
```

**Counting "n choose k" modulo a prime** needs division, so use modular inverses of factorials (precompute once, answer each query in `O(1)`):

```python
N = 200_000
fact = [1] * (N + 1)
for i in range(1, N + 1):
    fact[i] = fact[i - 1] * i % M
inv_fact = [1] * (N + 1)
inv_fact[N] = pow(fact[N], M - 2, M)
for i in range(N, 0, -1):
    inv_fact[i - 1] = inv_fact[i] * i % M

def n_choose_k(n, k):
    if k < 0 or k > n:
        return 0
    return fact[n] * inv_fact[k] % M * inv_fact[n - k] % M

print(n_choose_k(10, 3), math.comb(10, 3))                               # 120 120
print(n_choose_k(100_000, 50_000) == math.comb(100_000, 50_000) % M)     # True
```

## 9. Fast Fibonacci by doubling

`F(n)` via the loop takes `n` steps; with the **doubling identities** `F(2k) = F(k) * (2F(k+1) - F(k))` and `F(2k+1) = F(k)^2 + F(k+1)^2` it takes `O(log n)` big-number steps.

```python
def fib_pair(n, m=None):
    """Return (F(n), F(n+1)); optionally modulo m."""
    if n == 0:
        return 0, 1
    a, b = fib_pair(n // 2, m)
    c = a * (2 * b - a)
    d = a * a + b * b
    if m:
        c, d = c % m, d % m
    return (d, c + d) if n % 2 else (c, d)

def fib(n, m=None):
    return fib_pair(n, m)[0]

assert [fib(i) for i in range(30)] == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181, 6765, 10946, 17711, 28657, 46368, 75025, 121393, 196418, 317811, 514229]
print(fib(100), fib(10**18, M))                                          # 354224848179261915075 209783453
```

`fib(10**18) mod p` finishes instantly. (The modular result `209783453` is the well-known value of F(10^18) mod 10^9+7.)

## 10. Chinese remainder theorem (CRT)

If you know a number's remainders modulo several **pairwise coprime** moduli, the number is determined modulo their product: "a number that leaves 2 when divided by 3, 3 when divided by 5 and 2 when divided by 7" is 23 (mod 105).

```python
def crt(remainders, moduli):
    x, m = 0, 1
    for r, mod in zip(remainders, moduli):
        # solve x + m*t = r (mod mod) for t using the modular inverse of m
        t = (r - x) * pow(m, -1, mod) % mod
        x += m * t
        m *= mod
    return x % m, m

print(crt([2, 3, 2], [3, 5, 7]))                                         # (23, 105)
print([23 % 3, 23 % 5, 23 % 7])                                          # [2, 3, 2]
```

Uses: speeding up RSA decryption, splitting big computations across small moduli, calendar problems ("every 4 days and every 7 days").

## 11. Two real-world examples

**Example 1: Hash table sizing and checksums.** A hash function ends with `% size`; choosing a **prime** table size spreads keys with patterns (like multiples of 100) more evenly, because a prime shares no factors with the stride. Credit-card numbers use the **Luhn checksum** (a mod-10 rule) to catch mistyped digits.

**Example 2: RSA key generation and use.** Generate two large primes with Miller-Rabin, multiply to get `n`, compute `phi`, pick `e`, find `d` with the modular inverse (extended Euclid), then encrypt with `power_mod`. Every step is a function in this lesson.

## 12. Common mistakes

- Forgetting to reduce modulo `m` at each step (or only at the end, when the intermediate numbers explode in C/Java; Python is slow rather than wrong).
- Using `a / b` (floating point) for modular division instead of the inverse.
- Trying to invert a number that is not coprime to the modulus.
- Negative remainders in languages where `%` can be negative (Python's is not).
- Checking divisors up to `n` instead of `sqrt(n)`.
- Sieving with a Python list of booleans and multiple `append`s (use a `bytearray` and slice assignment).
- Trusting a simple Fermat test with a few bases (Carmichael numbers like 561 fool it).
- Computing `gcd`/`lcm` for huge numbers by listing divisors.

## 13. Practice

1. Compute `gcd(1071, 462)` by hand with Euclid's steps.
2. Find `x, y` with `35x + 15y = gcd(35, 15)` using `extended_gcd`.
3. What is `7^222 mod 10`? (use `pow`, then explain the pattern of last digits of powers of 7)
4. Find the inverse of 17 modulo 3120. (It is RSA's `d` for `e = 17`, `phi = 3120`.)
5. How many primes are below 1000? Verify with the sieve.
6. Factor 123456 and count its divisors.
7. Write `lcm_of_list(nums)` for a list.
8. How many trailing zeros does `100!` have? (Hint: count factors of 5.)
9. A number leaves remainder 1 mod 4, 2 mod 9 and 3 mod 5. Find the smallest such positive number using `crt`.

<details>
<summary>Solutions</summary>

1. `1071 % 462 = 147`, `462 % 147 = 21`, `147 % 21 = 0`: gcd is **21**.
   ```python
   print(gcd(1071, 462))                                        # 21
   ```
2. ```python
   print(extended_gcd(35, 15))                                  # (5, 1, -2)    35*1 + 15*(-2) = 5
   ```
3. ```python
   print(pow(7, 222, 10), [pow(7, k, 10) for k in range(1, 9)])      # 9 [7, 9, 3, 1, 7, 9, 3, 1]
   ```
   The last digit cycles with period 4 (7, 9, 3, 1); `222 % 4 = 2`, the second element: 9.
4. ```python
   print(mod_inverse(17, 3120))                                 # 2753
   ```
5. ```python
   print(len(sieve(1000)))                                      # 168
   ```
6. ```python
   print(factorize(123456), divisor_count(123456))              # {2: 6, 3: 1, 643: 1} 28
   ```
   (`123456 = 2^6 * 3 * 643`, divisors `(6+1)(1+1)(1+1) = 28`.)
7. ```python
   from functools import reduce
   def lcm_of_list(nums):
       return reduce(lcm, nums, 1)
   print(lcm_of_list([4, 6, 10, 15]))                           # 60
   ```
8. ```python
   n, count, p = 100, 0, 5
   while p <= n:
       count += n // p
       p *= 5
   print(count, len(str(math.factorial(100))) - len(str(math.factorial(100)).rstrip("0")))      # 24 24
   ```
9. ```python
   print(crt([1, 2, 3], [4, 9, 5]))                             # (173, 180)
   ```
   The smallest positive is 173 (check: `173 % 4 = 1`, `173 % 9 = 2`, `173 % 5 = 3`).

</details>

## 14. Check yourself

1. What does Euclid's algorithm compute and why is it fast?
2. When does a modular inverse exist, and how do you compute it?
3. Why is `power_mod` `O(log n)`?
4. How does the sieve of Eratosthenes work and what does it cost?
5. Why can Miller-Rabin handle numbers trial division cannot?
6. Why do we reduce modulo `m` at every step?
7. What difficulty underlies RSA?

<details>
<summary>Answers</summary>

1. The GCD of two numbers via `gcd(a, b) = gcd(b, a mod b)`; the numbers shrink by at least half every two steps, so it takes `O(log)` steps.
2. When `gcd(b, m) = 1`; with extended Euclid (coefficient of `b`), or `b^(m-2)` for prime `m` (Fermat).
3. Each step halves the exponent (square the base, shift the bits of `n`), so about `log2 n` iterations.
4. Cross out multiples of each prime up to `sqrt(N)`; the survivors are primes. `O(N log log N)` time, `O(N)` memory.
5. It tests a property that all primes satisfy and composites almost never do, using modular exponentiation: polynomial in the number of digits, versus `sqrt(n)` for trial division.
6. It keeps numbers small (bounded by `m`) and gives the same final remainder because `+`, `-`, `*` respect congruence.
7. Factoring a product of two large primes is believed to be infeasible, while multiplying them and the modular operations are cheap.

</details>

[Back to algorithms](../README.md)
