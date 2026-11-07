# Number Theory

The arithmetic of whole numbers: divisibility, remainders and primes. It underlies hashing, cryptography, random number generators and a large family of interview and contest problems.

## Detailed lesson

- [Number theory for programmers](01-number-theory-for-programmers.md): GCD and extended Euclid, modular arithmetic, fast exponentiation, modular inverses, sieve of Eratosthenes, Miller-Rabin, factorization, Euler's totient, `nCr` mod a prime, fast Fibonacci, the Chinese remainder theorem

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

Back to [algorithms](../README.md).
