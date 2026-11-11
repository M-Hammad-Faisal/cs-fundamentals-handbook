# Math for Computer Science: One-Page Summary

## Questions worth remembering

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

Practice problems with solutions are in the exercises page and in the **Practice** section of each lesson.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Exponents, Logarithms and Growth](exponents-and-logarithms.md) · [Logic, Sets and Proofs](logic-sets-proofs.md) · [Counting and Probability](counting-and-probability.md) · [Sequences, Sums and Recurrences](sums-and-recurrences.md)
