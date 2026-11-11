# Arrays and Strings: One-Page Summary

## Key facts

- Arrays are contiguous; index = `base + i * size`, so access is `O(1)`.
- Python `list` is a dynamic array of pointers. Append is amortized `O(1)`; insert/delete at the front is `O(n)`.
- Strings are immutable. Build with `"".join(parts)`, never repeated `+=`.

### Costs

| Operation | Cost |
|-----------|------|
| Index | `O(1)` |
| Append | `O(1)` amortized |
| Insert/delete in middle or front | `O(n)` |
| Search unsorted / sorted | `O(n)` / `O(log n)` |
| Slice | `O(k)` (copy) |

### Techniques

- **Two pointers:** sorted input or converging ends.
- **Sliding window:** contiguous subarray/substring with a running value.
- **Prefix sums:** `O(1)` range sums after `O(n)` build.
- **Hash map/set:** replace an inner search loop.
- **In-place read/write pointers:** filter or dedupe in `O(1)` space.
- **Kadane:** `cur = max(x, cur + x)`.

## Pitfalls

- Off-by-one; slices are half-open.
- `[[0]*m]*n` shares rows.
- Shallow vs deep copy.
- Mutating while iterating.
- Slicing inside recursion copies.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Arrays](01-arrays-and-memory.md) · [Working with Arrays](02-array-techniques.md) · [Strings in Depth](03-strings-in-depth.md)
