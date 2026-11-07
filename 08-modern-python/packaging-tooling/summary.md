# Packaging and Tooling: One-Page Summary

- **Imports:** module = `.py`; package = directory (+ `__init__.py`); search via `sys.path`, cached in `sys.modules`; `__main__.py` for `python -m pkg`; avoid circular imports and `import *`.
- **Virtual environments:** one per project (`python -m venv .venv` or `uv`); never commit `.venv`; never `sudo pip`.
- **`pyproject.toml`:** build system, metadata, `requires-python`, dependencies, extras (`[project.optional-dependencies]`), scripts (entry points), tool config. **`src/` layout** + `pip install -e .`.
- **Dependencies:** ranges in `pyproject.toml`, exact versions in a **lock file** (apps commit it; libraries use loose ranges). SemVer: MAJOR.MINOR.PATCH. Audit with `pip-audit`.
- **`uv`:** `uv init`, `uv add [--dev]`, `uv run`, `uv sync`, `uv lock --upgrade`, `uv tree`, `uvx tool`, `uv python install`. Alternatives: Poetry, PDM, Hatch.
- **CLIs:** `argparse` (or Typer/Click); parse separately from logic; exit codes.
- **Config:** environment variables (`Settings.from_env`), fail fast on required values, never commit secrets, `.env.example`.
- **Quality:** ruff (lint + format), mypy/pyright, pytest + coverage, pre-commit, tox/nox, **CI** on several Python versions.
- **Ship:** `python -m build` -> wheel + sdist -> TestPyPI -> PyPI (trusted publishing); apps -> Docker (lock file first, slim base, non-root, no secrets in images).

[Lesson](README.md) · [Exercises](exercises.md)
