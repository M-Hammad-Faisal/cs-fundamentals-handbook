# Iterators, Generators and Functional Tools: One-Page Summary

- **Comprehensions:** list `[x for x in xs if c]`, dict `{k: v ...}`, set `{...}`; max two loops or one condition for readability; own scope; walrus `:=` to avoid recomputation.
- **Generators:** `yield` pauses and keeps state; calling returns an iterator; **lazy, constant memory, infinite OK, single use**. Generator expressions `(x for x in xs)`; `sum/any/all` accept them directly.
- **`yield from`** delegates; **`send`** makes coroutines (prime with `next`); `close` triggers `GeneratorExit`; `@contextmanager` builds context managers from generators.
- **Pipelines:** chain generators (read, filter, transform); real files iterate lazily by line.
- **itertools:** `islice`, `chain`, `count`, `cycle`, `accumulate`, `takewhile`, `dropwhile`, `pairwise`, `batched` (3.12), `groupby` (needs sorted input), `product`, `permutations`, `combinations`, `tee`, `zip_longest`.
- **Functions as values:** closures (`nonlocal`), late-binding gotcha (bind with default arg), `lambda` for short callbacks, `sorted/min/max(key=...)`, `functools.partial`, `reduce`, `operator.itemgetter/attrgetter`.
- **Caching:** `@cache`, `@lru_cache(maxsize)`: pure functions, hashable args; beware methods (leaks).
- **Style:** pure functions, avoid mutating arguments, immutability where it helps.
- **Pitfalls:** exhausted generators, side-effect comprehensions, unsorted `groupby`, shared mutable defaults, errors raised lazily at `next()`.

[Lesson](README.md) · [Exercises](exercises.md)
