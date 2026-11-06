# Tries: One-Page Summary

## Facts
- Tree where each edge is a character; paths spell prefixes; shared prefixes share nodes.
- Lookup is `O(L)` (word length), independent of the number of stored words.
- Mark word ends with `is_end`.

## Costs
| Operation | Time |
|-----------|------|
| Insert / search / prefix check | `O(L)` |
| All words with a prefix | `O(L + output)` |
| Space | `O(total characters)` worst case |

## Use a trie when
- You need prefix queries, autocomplete, sorted key iteration, or longest-prefix match.
- Use a plain set if you only need exact membership.

## Variants
Radix/compressed trie · array children (26 slots) · ternary search tree · binary trie (XOR, IP routing).

## Patterns
- Autocomplete: walk to the prefix node, then DFS (or read top-K stored at the node).
- Wildcards: DFS over all children on `.`.
- Max XOR: walk bits preferring the opposite bit.
- Store counts or ranking data at nodes.

## Pitfalls
- Forgetting `is_end`.
- High memory use (dict per node).
- Not normalizing case or Unicode.

[Lesson](README.md) · [Exercises](exercises.md)
