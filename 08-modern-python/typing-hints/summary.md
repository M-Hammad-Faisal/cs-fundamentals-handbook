# Type Hints: One-Page Summary

- **Hints are not enforced at runtime.** Checkers (mypy, pyright), IDEs and libraries (pydantic, FastAPI, dataclasses) read them. Gradual typing: add them piece by piece.
- **Basics:** `int`, `list[str]`, `dict[str, int]`, `tuple[int, ...]`, `X | None` (not "optional argument"), `Callable[[A], R]`, `Any` (turns checking off), `Literal`, `Final`, `ClassVar`, `NewType`, `TypeAlias`, `Annotated`.
- **Parameters general, returns specific:** `Iterable`/`Sequence`/`Mapping` in, `list`/`dict` out. `list` is invariant (`list[bool]` is not `list[int]`).
- **Generics:** `TypeVar` or 3.12 syntax `def f[T](x: T) -> T`, `class Stack[T]`, bounds `T: Proto`, constraints `(int, float)`, `ParamSpec` for decorators, `Self` for fluent/factory methods.
- **Protocols** = structural typing (no inheritance needed); ABCs when you own the hierarchy.
- **Structures:** `TypedDict` (JSON-like dicts, not enforced at runtime), `NamedTuple`, dataclasses.
- **Narrowing:** `is None`, `isinstance`, `TypeIs`/`TypeGuard`; **exhaustiveness** with `assert_never`; `@overload` for type-dependent returns.
- **Runtime:** `__annotations__`, `typing.get_type_hints`, lazy annotations in 3.14, `annotationlib`.
- **Adopt gradually:** new code first, CI baseline, per-module overrides, `# type: ignore[code]`, stubs, stricter flags later.
- **Pitfalls:** `Any` leaks, treating hints as validation, over-complicated generics, missing `-> None`.

[Lesson](README.md) · [Exercises](exercises.md)
