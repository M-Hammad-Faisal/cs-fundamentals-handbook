# Linked Lists: One-Page Summary

## Facts
- Nodes hold a value and pointer(s). Types: singly, doubly, circular.
- No random access: reaching index `i` is `O(n)`.
- Insert/delete at a known position is `O(1)` (doubly linked, given the node).
- Poor cache locality; arrays often win in practice.

## Costs
| Operation | Singly | Doubly |
|-----------|--------|--------|
| Head insert/delete | `O(1)` | `O(1)` |
| Tail insert | `O(n)` (`O(1)` with tail ptr) | `O(1)` |
| Delete known node | `O(n)` | `O(1)` |
| Search / index | `O(n)` | `O(n)` |

## Patterns
- **Dummy head** removes head edge cases.
- **Reverse:** save `next`, flip pointer, advance.
- **Slow/fast pointers:** middle, cycle detection, cycle start, k-th from end.
- **Merge sorted lists:** dummy plus tail pointer.
- **LRU cache:** hash map + doubly linked list.

## Pitfalls
- Overwriting `next` before saving it.
- Dereferencing `None`.
- Forgetting to update `head`/`tail`.
- Unintended cycles cause infinite loops.

[Lesson](README.md) · [Exercises](exercises.md)
