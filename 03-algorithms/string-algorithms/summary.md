# String Algorithms: One-Page Summary

## Quick reference

| Problem | Algorithm | Time |
|---------|-----------|------|
| One pattern in a text | KMP, Z-function, Rabin-Karp | `O(n + m)` |
| Many patterns | Rabin-Karp (equal length), Aho-Corasick | near linear |
| Period / border of a string | prefix function or Z | `O(n)` |
| Longest palindromic substring | Manacher | `O(n)` |
| Many substring queries on one text | suffix array + binary search | `O(m log n)` per query |
| Longest repeated substring, distinct substrings | suffix array + LCP | `O(n log n)` build |

Related: [strings in depth](../../02-data-structures/arrays-strings/03-strings-in-depth.md) (Unicode, KMP), [tries](../../02-data-structures/tries/01-tries.md), [edit distance](../dynamic-programming/02-dp-on-two-sequences-and-grids.md).

## Questions worth remembering

- **How does a rolling hash update in O(1)?** Subtract the leaving character's contribution (`char * base^(m-1)`), multiply by the base, add the entering character, all modulo `M`.
- **Why must Rabin-Karp verify hash matches?** Different strings can have equal hashes (collisions), so a match must be confirmed character by character.
- **What does `z[i]` mean and how is the whole array computed in linear time?** The length of the longest common prefix between the string and the suffix starting at `i`; a window `[l, r)` of the farthest match lets each `z[i]` start from a known value and only extend forward.
- **How does Manacher avoid recomputing palindrome radii?** Inside the current rightmost palindrome, a position's radius is at least the mirror position's radius (capped by the window), so it starts from that value and only extends outward.
- **What is a suffix array and how does it speed up substring queries?** The sorted list of suffix start positions; since every substring is a prefix of a suffix and equal prefixes are adjacent, binary search finds a pattern in `O(m log n)` per query after one preprocessing pass.
- **What does the LCP array tell you?** For adjacent sorted suffixes, how many leading characters they share: the maximum is the longest repeated substring, and `n(n+1)/2 - sum(lcp)` counts distinct substrings.

Practice problems with solutions are in the **Practice** section of each lesson.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [String Algorithms](01-string-matching-and-suffix-structures.md)
