# Number Theory: Exercises

Try each problem before opening its solution. These are the practice problems of this topic's lessons, collected in one place.

## Number Theory for Programmers

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
   ```python no-run
   print(gcd(1071, 462))                                        # 21
   ```
2. ```python no-run
   print(extended_gcd(35, 15))                                  # (5, 1, -2)    35*1 + 15*(-2) = 5
   ```
3. ```python no-run
   print(pow(7, 222, 10), [pow(7, k, 10) for k in range(1, 9)])      # 9 [7, 9, 3, 1, 7, 9, 3, 1]
   ```
   The last digit cycles with period 4 (7, 9, 3, 1); `222 % 4 = 2`, the second element: 9.
4. ```python no-run
   print(mod_inverse(17, 3120))                                 # 2753
   ```
5. ```python no-run
   print(len(sieve(1000)))                                      # 168
   ```
6. ```python no-run
   print(factorize(123456), divisor_count(123456))              # {2: 6, 3: 1, 643: 1} 28
   ```
   (`123456 = 2^6 * 3 * 643`, divisors `(6+1)(1+1)(1+1) = 28`.)
7. ```python no-run
   from functools import reduce
   def lcm_of_list(nums):
       return reduce(lcm, nums, 1)
   print(lcm_of_list([4, 6, 10, 15]))                           # 60
   ```
8. ```python no-run
   n, count, p = 100, 0, 5
   while p <= n:
       count += n // p
       p *= 5
   print(count, len(str(math.factorial(100))) - len(str(math.factorial(100)).rstrip("0")))      # 24 24
   ```
9. ```python no-run
   print(crt([1, 2, 3], [4, 9, 5]))                             # (173, 180)
   ```
   The smallest positive is 173 (check: `173 % 4 = 1`, `173 % 9 = 2`, `173 % 5 = 3`).

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Number Theory for Programmers](01-number-theory-for-programmers.md)
