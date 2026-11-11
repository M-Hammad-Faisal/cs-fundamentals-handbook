# Exceptions, Logging and Testing: One-Page Summary

## Key facts

### Exceptions

- `try` / `except` (specific!) / `else` (success only) / `finally` (always). Hierarchy: `BaseException` > `Exception` > `ValueError`, `OSError`, ...
- Catch the narrowest type you can handle; never bare `except:`; never `except: pass`; EAFP where checks are racy.
- `raise New(...) from e` keeps the cause; bare `raise` re-raises; define a base exception per app/library and translate low-level errors at layer boundaries.
- Retry only transient, idempotent operations with backoff. `contextlib.suppress`, `@contextmanager` for cleanup.

### Logging

- Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL. Logger hierarchy by name; handlers (where), formatters (how), filters.
- `log = logging.getLogger(__name__)`; libraries never configure handlers (NullHandler); applications configure once (`dictConfig`).
- Lazy `%s` args, identifiers in messages, never log secrets, `log.exception` in `except`, structured JSON for production, no duplicate log-and-raise at every layer.

### Testing

- Pyramid: many unit, some integration, few end-to-end. `unittest` (stdlib) or **pytest** (plain `assert`, fixtures, `parametrize`, `raises`, `tmp_path`, `monkeypatch`, `caplog`).
- Doubles: dummy, stub, **fake**, mock, spy; prefer fakes and outcome assertions.
- Good tests: fast, isolated, deterministic, one idea each, Arrange-Act-Assert, behavior not internals, edge cases.
- TDD: red, green, refactor. Coverage shows what is untested, not what is correct. Add a failing test before fixing a bug. Run in CI.

## Pitfalls

- A bare `except:` or `except Exception: pass` hides real bugs; catch the narrowest exception you can handle.
- Losing the cause: use `raise NewError(...) from err`.
- Logging and re-raising at every layer (duplicate lines); `print` instead of `logging`.
- Logging secrets or personal data; formatting the message eagerly.
- Exceptions used for ordinary control flow; tests that assert nothing.

[Lesson](README.md) · [Exercises](exercises.md)
