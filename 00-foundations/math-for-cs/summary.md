# Math for Computer Science: One-Page Summary

## Key facts

- **Logarithms:** `log₂ n` is how many times you can halve `n`; `2¹⁰ = 1024 ≈ 10³`, so `log₂ 10⁶ ≈ 20` and `log₂ 10⁹ ≈ 30`. The base does not matter in Big-O (it only changes a constant).
- **Rules:** `aᵐ·aⁿ = aᵐ⁺ⁿ`, `(aᵐ)ⁿ = aᵐⁿ`, `log(xy) = log x + log y`, `log(xᵏ) = k·log x`.
- **Sums to know:** `1 + 2 + … + n = n(n+1)/2` (so `Θ(n²)`), `1 + 2 + 4 + … + 2ᵏ = 2ᵏ⁺¹ - 1` (the last term dominates), `Σ 1/i ≈ ln n` (the harmonic series).
- **Counting:** sum rule adds alternatives, product rule multiplies sequential choices; orderings of `n` items `n!`; ordered picks `n!/(n-k)!`; unordered picks `C(n,k) = n!/(k!(n-k)!)`; subsets of `n` items `2ⁿ`.
- **Probability:** `P(A or B) = P(A) + P(B) - P(A and B)`; independent events multiply; expected value is linear. **Birthday paradox:** a collision becomes likely after about `√N` random draws from `N` values (23 people for 365 days).
- **Logic and proofs:** De Morgan's laws; `p → q` is false only when `p` is true and `q` false; the contrapositive is equivalent; prove with direct argument, contradiction or induction (base case plus step); disprove "for all" with one counterexample.
- **Recurrences:** `T(n-1) + c` is `O(n)`, `T(n/2) + c` is `O(log n)`, `2T(n/2) + n` is `O(n log n)`, `T(n-1) + n` is `O(n²)`, `2T(n-1)` is `O(2ⁿ)`.

## Pitfalls

- Treating `log n` as `n/2`, or forgetting it is the number of halvings.
- Mixing up permutations (order matters) and combinations (it does not).
- Assuming events are independent without a reason.
- "Proving" a for-all claim with examples; off-by-one in the number of terms of a sum.
- Using `/` when you meant integer division `//`.

## Self-check

- **What does `log2(n)` mean in plain words?** How many times you can halve `n` before reaching 1 (or the number of bits needed to count to `n`).
- **Why does the base of the logarithm not matter in Big-O?** Changing the base multiplies the logarithm by a constant, and Big-O ignores constant factors.
- **About how many steps does binary search need for 1,000,000 items?** About 20.
- **What happens to `n^2` if you double `n`? To `2^n` if you add 1 to `n`?** `n^2` becomes 4 times larger; `2^n` becomes twice as large.
- **Which grows faster, `n^100` or `2^n`?** `2^n`: exponential growth eventually beats any polynomial, even if only for very large `n`.
- **What does De Morgan's law say?** The negation of an AND is the OR of the negations, and the negation of an OR is the AND of the negations.
- **What is the difference between `A | B` and `A & B` for sets?** Union keeps elements in either set; intersection keeps only elements in both.
- **How do you disprove a "for all" statement?** With a single counterexample.
- **What are the two steps of induction?** The base case, and the inductive step (if true for k then true for k + 1).
- **How are recursion and induction related?** The base case of a recursive function matches the base case of the proof; the recursive call matches the inductive hypothesis.
- **Why is `all([])` True?** Vacuous truth: with no elements, there is nothing that violates the claim.
- **Sum rule versus product rule?** Sum rule adds the ways for alternative choices; product rule multiplies the ways for sequential independent choices.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Exponents, Logarithms and Growth](exponents-and-logarithms.md) · [Logic, Sets and Proofs](logic-sets-proofs.md) · [Counting and Probability](counting-and-probability.md) · [Sequences, Sums and Recurrences](sums-and-recurrences.md)
