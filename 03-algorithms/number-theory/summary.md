# Number Theory: One-Page Summary

## Quick reference

| Tool | Cost | Python |
|------|------|--------|
| GCD / LCM | `O(log n)` | `math.gcd`, `math.lcm` |
| Modular power | `O(log n)` | `pow(a, n, m)` |
| Modular inverse | `O(log m)` | `pow(b, -1, m)` |
| All primes up to `N` | `O(N log log N)` | sieve with a `bytearray` |
| Is `n` prime? | `O(sqrt n)` trial, `O(k log^2 n)` Miller-Rabin | `is_prime` in the lesson |
| Factorize `n` | `O(sqrt n)` | trial division |
| `nCr mod p` | `O(1)` after `O(N)` setup | factorials and inverse factorials |

Used by: [hash tables](../../02-data-structures/hash-tables/01-hash-functions-and-collisions.md), [RSA and TLS](../../07-networking/tls-security/01-cryptography-and-tls-lab.md), [Rabin-Karp](../string-algorithms/01-string-matching-and-suffix-structures.md).

## Questions worth remembering

- **What does Euclid's algorithm compute and why is it fast?** The GCD of two numbers via `gcd(a, b) = gcd(b, a mod b)`; the numbers shrink by at least half every two steps, so it takes `O(log)` steps.
- **When does a modular inverse exist, and how do you compute it?** When `gcd(b, m) = 1`; with extended Euclid (coefficient of `b`), or `b^(m-2)` for prime `m` (Fermat).
- **Why is `power_mod` `O(log n)`?** Each step halves the exponent (square the base, shift the bits of `n`), so about `log2 n` iterations.
- **How does the sieve of Eratosthenes work and what does it cost?** Cross out multiples of each prime up to `sqrt(N)`; the survivors are primes. `O(N log log N)` time, `O(N)` memory.
- **Why can Miller-Rabin handle numbers trial division cannot?** It tests a property that all primes satisfy and composites almost never do, using modular exponentiation: polynomial in the number of digits, versus `sqrt(n)` for trial division.
- **Why do we reduce modulo `m` at every step?** It keeps numbers small (bounded by `m`) and gives the same final remainder because `+`, `-`, `*` respect congruence.

Practice problems with solutions are in the **Practice** section of each lesson.

[Lesson](README.md) · [Number Theory for Programmers](01-number-theory-for-programmers.md)
