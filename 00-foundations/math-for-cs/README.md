# Math for Computer Science

Four lessons with just the math you need for algorithms, data structures and databases. Everything is explained from scratch and verified with short Python programs.

| # | Lesson | You will learn |
|---|--------|----------------|
| 1 | [Exponents, logarithms and growth](exponents-and-logarithms.md) | Powers, logs (halving), growth-rate table, why `log n` is tiny and `2^n` is hopeless |
| 2 | [Logic, sets and proofs](logic-sets-proofs.md) | Truth tables, De Morgan, gates, set operations, quantifiers, induction |
| 3 | [Counting and probability](counting-and-probability.md) | Permutations, combinations, probability, expected value, birthday paradox |
| 4 | [Sequences, sums and recurrences](sums-and-recurrences.md) | Summations, loop counting, solving recurrences, Master Theorem |

**Study tip:** do the practice questions with pencil and paper first, then check with the Python code.

[Back to foundations](../README.md)

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

## Quick reference

| Question | Answer |
|----------|--------|
| What does `log2(n)` mean in plain words? | How many times you can halve `n` before reaching 1 (or the number of bits needed to count to `n`). |
| Why does the base of the logarithm not matter in Big-O? | Changing the base multiplies the logarithm by a constant, and Big-O ignores constant factors. |
| About how many steps does binary search need for 1,000,000 items? | About 20. |
| What happens to `n^2` if you double `n`? To `2^n` if you add 1 to `n`? | `n^2` becomes 4 times larger; `2^n` becomes twice as large. |
| Which grows faster, `n^100` or `2^n`? | `2^n`: exponential growth eventually beats any polynomial, even if only for very large `n`. |

Back to the [part overview](../README.md).
