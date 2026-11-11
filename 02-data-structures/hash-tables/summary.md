# Hash Tables: One-Page Summary

## Key facts

- Key → hash → slot. Average `O(1)` insert, lookup, delete; worst `O(n)`.
- Python `dict` (ordered since 3.7) and `set` are hash tables.
- Keys must be **hashable** (immutable). Equal objects must hash equally.
- **Collisions:** chaining or open addressing. **Load factor** triggers resize and rehash.

### Toolkit

`dict.get`, `setdefault`, `defaultdict`, `Counter`, `set` operations (`&`, `|`, `-`).

### Patterns

- **Frequency counting** (`Counter`).
- **Complement lookup** (two sum).
- **Grouping by key** (anagrams).
- **Prefix sum + map** (subarray sum).
- **Set for dedupe / membership / "seen"**.
- **Dict + list** for `O(1)` random access and removal.
- **Consistent hashing** for distributed key placement.

## Pitfalls

- Mutable keys (`list`) are unhashable.
- `d[key]` raises `KeyError`; use `get`.
- Mutating a dict while iterating.
- Floating-point keys.
- `hash()` is not stable across runs and not secure.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Hash Functions and Collisions](01-hash-functions-and-collisions.md) · [Implementing Hash Tables](02-implementing-hash-tables.md) · [Dict, Set, Hash-Map Patterns, Bloom Filters and Consistent Hashing](03-dict-set-internals-and-bloom-filters.md)
