# Dataclasses, NamedTuple and Enums: One-Page Summary

## Key facts

### Dataclasses

- `@dataclass` generates `__init__`, `__repr__`, `__eq__` from annotated fields.
- **Defaults:** immutables directly; mutables via `field(default_factory=list)` (bare `[]` raises `ValueError`).
- **Options:** `frozen=True` (immutable, hashable), `order=True` (field-order comparisons), `slots=True` (memory), `kw_only=True`, `eq`, `repr`.
- **`field()`:** `init`, `repr`, `compare`, `hash`, `kw_only`, `metadata`. **`__post_init__`** validates and derives fields; **`InitVar`** passes init-only values.
- **Helpers:** `asdict`, `astuple`, `replace` (copy with changes), `fields`, `is_dataclass`. Works with `match`.
- **No runtime type validation**; use `__post_init__` or pydantic for untrusted data.
- **Alternatives:** `NamedTuple` (immutable tuple record), `TypedDict` (typed dict shape, plain dict at runtime), pydantic/attrs (validation).

### Enums

- `Enum` (distinct constants), `IntEnum` (int-compatible), `StrEnum` (string-compatible, 3.11), `Flag`/`IntFlag` (combine with `|`), `auto()`, `@unique`.
- Lookup by value `Status("paid")`, by name `Status["PAID"]`; iterate `list(Status)`; add methods, properties, classmethods; members can carry data via `__init__`.
- Use with `match`; serialize with `.value` (or `StrEnum`).
- Compare with `is`/`==` to members, not raw values (plain `Enum`).

## Pitfalls

Mutable defaults, assuming type enforcement, `order=True` on unrelated fields, unhashable non-frozen dataclasses, `asdict` ignoring custom serialization, `slots` quirks, enum ordering assumptions.

[Lesson](README.md) · [Exercises](exercises.md)
