# Modern Python

Start with the [bridge from Python fundamentals](00-from-fundamentals-to-modern-python.md), then eight chapters covering the language and tools professional Python developers use every day, followed by the **going deeper** track below (internals, concurrency in practice, testing, web APIs, databases, data, workflow and the standard library). Every code example was run on a current Python (3.15) with pytest, mypy and uv where relevant.

| # | Topic | Lesson |
|---|-------|--------|
| 1 | Type hints and static typing | [lesson](typing-hints/README.md) · [exercises](typing-hints/exercises.md) · [summary](typing-hints/summary.md) |
| 2 | Dataclasses, NamedTuple and enums | [lesson](dataclasses-enums/README.md) · [exercises](dataclasses-enums/exercises.md) · [summary](dataclasses-enums/summary.md) |
| 3 | Iterators, generators, comprehensions and functional tools | [lesson](generators-functional/README.md) · [exercises](generators-functional/exercises.md) · [summary](generators-functional/summary.md) |
| 4 | Concurrency: threads, processes and asyncio | [lesson](async-concurrency/README.md) · [exercises](async-concurrency/exercises.md) · [summary](async-concurrency/summary.md) |
| 5 | Modern language features (3.8 to 3.14) | [lesson](modern-syntax/README.md) · [exercises](modern-syntax/exercises.md) · [summary](modern-syntax/summary.md) |
| 6 | Performance, profiling and memory | [lesson](performance-profiling/README.md) · [exercises](performance-profiling/exercises.md) · [summary](performance-profiling/summary.md) |
| 7 | Exceptions, logging and testing | [lesson](exceptions-logging-testing/README.md) · [exercises](exceptions-logging-testing/exercises.md) · [summary](exceptions-logging-testing/summary.md) |
| 8 | Packaging, environments and tooling | [lesson](packaging-tooling/README.md) · [exercises](packaging-tooling/exercises.md) · [summary](packaging-tooling/summary.md) |

## Learning path

1. **Type hints**: annotate, generics, protocols, narrowing, using mypy.
2. **Dataclasses and enums**: model data with almost no boilerplate.
3. **Generators and functional tools**: laziness, pipelines, itertools, closures, caching.
4. **Concurrency**: choose between threads, processes and asyncio; avoid blocking the loop.
5. **Modern syntax**: f-strings, `match`, exception groups, t-strings, version-by-version tour.
6. **Performance**: measure first; algorithms and data structures before micro-tuning.
7. **Exceptions, logging, testing**: handle failure, observe production, prove it works.
8. **Packaging and tooling**: environments, `pyproject.toml`, `uv`, ruff, CI, shipping.

Related: [OOP and design patterns](../04-oop/README.md), [operating-systems concurrency](../06-operating-systems/concurrency-deadlocks/README.md).


## Going deeper: the professional Python track

These lessons assume the eight chapters above. Some use third-party packages (`pytest`, `hypothesis`, `fastapi`, `sqlalchemy`, `numpy`, `pandas`); each says so at the top, and the outputs shown were produced by running them.

| Topic | Lesson |
|-------|--------|
| Data model, descriptors, memory, bytecode, imports, the GIL | [internals](internals/01-python-data-model-and-internals.md) |
| Build a tokenizer, parser, evaluator and bytecode VM | [tiny interpreter](internals/02-build-a-tiny-interpreter.md) |
| Threads, processes, futures, races and queues, measured | [concurrency in practice](concurrency/01-threads-processes-and-futures.md) |
| pytest, fixtures, mocking, Hypothesis, coverage | [testing in depth](testing-in-depth/01-pytest-mocking-and-property-testing.md) |
| FastAPI, Pydantic, dependencies, auth, idempotent POST | [web APIs with FastAPI](backend-with-fastapi/01-building-a-web-api-with-fastapi.md) |
| sqlite3, SQLAlchemy ORM, sessions, the N+1 problem | [database access](database-access/01-sqlalchemy-and-database-access.md) |
| NumPy arrays and pandas DataFrames | [NumPy and pandas](data-with-numpy-pandas/01-numpy-and-pandas-essentials.md) |
| src layout, ruff, mypy, pre-commit, CI, Docker, publishing | [engineering workflow](engineering-workflow/01-ci-docker-pre-commit-and-publishing.md) |
| Regex, dates and time zones, subprocess, argparse | [standard library toolbox](stdlib-toolbox/01-regex-datetime-subprocess-argparse.md) |

Back to the [index](../INDEX.md).
