# Engineering Workflow: One-Page Summary

## Key facts

- **Project layout:** a `src/` package folder plus `pyproject.toml` for metadata, dependencies and tool settings; `pip install -e .` installs it in editable mode.
- **Quality tools:** `ruff check` (lint), `ruff format`, `mypy` (types), `pytest` with `--cov` (tests and coverage).
- **pre-commit:** hooks in `.pre-commit-config.yaml` run the checks before every commit (`pre-commit install`).
- **CI:** a GitHub Actions workflow in `.github/workflows/` runs on push and pull request: install, lint, type-check, test, usually across a Python version matrix.
- **Docker:** a slim base image, copy dependency files before source (layer cache), run as a non-root user, add a `.dockerignore`, one process per container.
- **Publishing:** `python -m build` makes a wheel and an sdist; check with `twine check`; prefer trusted publishing; use semantic versioning.
- **Reproducibility:** pin exact versions for applications (a lock file), allow ranges for libraries, keep development dependencies separate.

## Pitfalls

- Committing secrets or an `.env` file; images that run as root and carry build tools.
- Unpinned dependencies and `latest` tags, so a rebuild changes behaviour.
- Tests that pass only on your machine because CI uses a different Python or clean environment.
- Never testing the built package, only the source tree.
- Keeping the version number in several places.

## Self-check

- **Why use the `src/` layout?** So tests import the installed package rather than the working directory, catching packaging mistakes and testing what users receive.
- **What goes in `pyproject.toml`?** Project metadata (name, version, dependencies, entry points, Python requirement), the build backend and the settings for tools such as ruff, mypy and pytest.
- **What do ruff, mypy and pytest each check?** Ruff: style and likely bugs (and formatting); mypy: type consistency; pytest: behaviour.
- **What does pre-commit do, and how is it different from CI?** It runs checks locally at commit time so bad changes never reach the repository; CI runs on a clean server for every push and pull request, so it is the shared, authoritative gate.
- **What is a CI matrix?** A set of values (such as Python versions) for which the same job runs in parallel.
- **Why a multi-stage Dockerfile and a non-root user?** The multi-stage build leaves build tools out of the final image (smaller, fewer vulnerabilities); a non-root user limits what a compromised process can do.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Engineering Workflow](01-ci-docker-pre-commit-and-publishing.md)
