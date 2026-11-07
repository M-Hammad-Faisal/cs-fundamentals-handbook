# String Algorithms

Beyond a simple `in` test: searching in linear time, finding palindromes and indexing a text so that many queries are fast.

## Detailed lesson

- [Matching, palindromes and suffix arrays](01-string-matching-and-suffix-structures.md): Rabin-Karp and rolling hashes, the Z-function, KMP's prefix function, Manacher's algorithm, suffix arrays and the LCP array

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

Back to [algorithms](../README.md).
