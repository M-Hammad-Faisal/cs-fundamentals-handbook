# Modern Python Language Features: One-Page Summary

| Version | Know these |
|---------|-----------|
| 3.8 | walrus `:=`, positional-only `/`, `f"{x=}"` |
| 3.9 | `dict | dict`, `list[int]`, `removeprefix/removesuffix`, `zoneinfo` |
| 3.10 | **`match`/`case`**, `X | Y`, parenthesized `with`, `zip(strict=True)` |
| 3.11 | **`ExceptionGroup`/`except*`**, `add_note`, `tomllib`, `TaskGroup`, `Self`, faster |
| 3.12 | `type` alias, `def f[T]`/`class C[T]`, `@override`, `itertools.batched` |
| 3.13 | experimental free-threaded (no GIL) and JIT builds |
| 3.14 | **t-strings** (`Template`), deferred annotations, `compression.zstd`, `InterpreterPoolExecutor` |

- **f-strings:** `{x:,.2f}`, `{x!r}`, `{x:>8}`, `{x:%Y-%m-%d}`, nested fields; **t-strings** keep text and values separate for safe HTML/SQL.
- **Parameters:** `/` positional-only, `*` keyword-only; star unpacking; `{**a, **b}`; `a | b` for dicts.
- **`match`:** literal, capture (bare name assigns!), wildcard `_`, dotted value, sequence `[a, *rest]`, mapping `{"k": v}`, class `P(x=0)`, `|` or, `as`, guards `if`. First match wins.
- **Exceptions:** groups + `except*` for concurrent errors; notes for context.
- **Stdlib:** `pathlib`, `tomllib`, `zoneinfo`, `secrets`, `functools.cache`, `itertools.batched`.
- **Practice:** target your oldest supported version (`requires-python`), test several, adopt syntax when the minimum allows.

[Lesson](README.md) · [Exercises](exercises.md)
