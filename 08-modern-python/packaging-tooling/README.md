# Packaging, Environments and Developer Tooling

## 1. The concept

Writing code is half the job. The other half is making it **runnable on someone else's machine, reproducible next year, and safe to change**. That needs:

| Need | Tool |
|------|------|
| Keep project dependencies separate | **virtual environments** (`venv`, `uv`) |
| Declare and install dependencies | **`pip`**, **`uv`**, `pyproject.toml`, lock files |
| Organize code into importable units | **modules and packages**, `src/` layout |
| Share or deploy | **wheels**, PyPI, Docker |
| Offer a command-line program | **entry points**, `argparse`/`typer`/`click` |
| Keep code clean and correct | **ruff** (lint + format), **mypy**, **pytest**, pre-commit, CI |
| Configure without editing code | **environment variables**, config files |

## 2. Modules, packages and imports

A **module** is a `.py` file. A **package** is a directory of modules (with an `__init__.py`). The **import system** finds them by searching `sys.path`.

```python
import importlib, os, sys, tempfile, textwrap

root = tempfile.mkdtemp()
pkg = os.path.join(root, "shapes")
os.makedirs(pkg)
open(os.path.join(pkg, "__init__.py"), "w").write("from .circle import area as circle_area\n")       # the package's public face
open(os.path.join(pkg, "circle.py"), "w").write(textwrap.dedent("""
    import math
    def area(r):
        return math.pi * r * r
"""))

sys.path.insert(0, root)                                   # make the folder importable
shapes = importlib.import_module("shapes")
print(round(shapes.circle_area(1), 2), shapes.__name__)    # 3.14 shapes
print(shapes.circle_area.__module__)                       # shapes.circle
print(shapes.__file__.endswith("__init__.py"))             # True
```

Key facts:

- `import x` runs `x` once and caches it in `sys.modules`; later imports reuse it (this is why a module-level object works as a [singleton](../../04-oop/design-patterns/creational/singleton.md)).
- **Absolute imports** (`from shapes.circle import area`) are clearest; **relative imports** (`from .circle import area`) work inside a package.
- `if __name__ == "__main__":` runs code only when the file is executed, not imported.
- `python -m package` runs `package/__main__.py`; `python -m module` runs a module with the package context correct.
- Avoid circular imports (A imports B imports A): restructure, move shared code to a third module, or import inside the function.
- Control the public API with `__all__` and leading underscores; `import *` is discouraged.

## 3. Virtual environments

A **virtual environment** is an isolated copy of the interpreter plus its own `site-packages`, so project A can use `requests 2.20` while project B uses `2.34`, and nothing touches the system Python.

```text
python -m venv .venv                   # create (once per project)
source .venv/bin/activate              # macOS/Linux   (Windows: .venv\Scripts\activate)
pip install requests                   # installs INTO .venv
which python                           # now points inside .venv
deactivate
```

Rules: **one environment per project**, keep it **out of git** (`.venv/` in `.gitignore`), never `sudo pip install`, and recreate it from declared dependencies rather than copying the folder.

```python
import sys
print(sys.prefix != sys.base_prefix)       # True inside a virtual environment, False when using the system Python
```

## 4. Declaring a project: `pyproject.toml`

`pyproject.toml` is the single standard file for build settings, metadata, dependencies and tool configuration.

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "greeter-demo"
version = "0.1.0"
description = "A tiny demo package"
requires-python = ">=3.10"
dependencies = ["requests>=2.31"]          # runtime dependencies, with compatible ranges

[project.optional-dependencies]
dev = ["pytest", "mypy", "ruff"]           # extras: pip install -e ".[dev]"

[project.scripts]
greet = "greeter.cli:main"                 # creates a `greet` command

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
line-length = 100
```

### The recommended `src/` layout

```text
greeter-demo/
├── pyproject.toml
├── README.md
├── src/
│   └── greeter/
│       ├── __init__.py          # public API, __version__
│       ├── cli.py               # command-line entry point
│       └── __main__.py          # makes `python -m greeter` work
└── tests/
    └── test_greet.py
```

Putting the package under `src/` stops tests from accidentally importing the **uncommitted source folder** instead of the **installed package**, which catches packaging mistakes early.

The files used above (verified):

```python
# src/greeter/__init__.py
def greet(name: str, excited: bool = False) -> str:
    return f"Hello, {name}{'!' if excited else '.'}"
```

```python
# src/greeter/cli.py   (the entry point named in [project.scripts])
import argparse
from greeter import greet

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="greet", description="Say hello")
    parser.add_argument("name")
    parser.add_argument("--excited", action="store_true")
    args = parser.parse_args(argv)
    print(greet(args.name, args.excited))
    return 0
```

Install it for development (**editable**: code changes take effect immediately) and use it:

```text
pip install -e ".[dev]"
greet Ana --excited          ->  Hello, Ana!
python -m greeter Bo         ->  Hello, Bo.
pytest -q                    ->  1 passed
python -m build              ->  dist/greeter_demo-0.1.0-py3-none-any.whl and .tar.gz
```

## 5. Dependencies: ranges, pinning and lock files

| Concept | Meaning |
|---------|---------|
| **Direct dependency** | A package your code imports (declared in `pyproject.toml`) |
| **Transitive dependency** | A dependency of your dependencies |
| **Version specifier** | `requests>=2.31,<3` (compatible range), `==2.34.2` (exact), `~=2.34` (compatible release) |
| **Lock file** | Exact versions of **everything** (`uv.lock`, `requirements.txt` from `pip freeze` / `pip-compile`) for **reproducible installs** |
| **Semantic versioning** | `MAJOR.MINOR.PATCH`: MAJOR = breaking, MINOR = new compatible features, PATCH = bug fixes |

- **Libraries** declare **loose ranges** (so many projects can combine them).
- **Applications** also commit a **lock file** (so every machine and CI run gets identical versions).
- Update deliberately (`uv lock --upgrade`, Dependabot/Renovate PRs) and let tests tell you whether it is safe.
- Audit for known vulnerabilities (`pip-audit`, `uv pip audit`, GitHub security alerts) and prefer few, well-maintained dependencies.

## 6. `uv`: the modern all-in-one tool

`uv` (from Astral) is a very fast replacement for `pip`, `venv`, `pip-tools`, `pipx` and a project manager.

```text
uv init demo-app                 # new project: pyproject.toml, main.py, README.md
uv add requests                  # add a dependency: edits pyproject.toml, updates uv.lock, installs
uv add --dev pytest ruff mypy    # development-only dependencies
uv run main.py                   # run inside the project's managed environment (creates/syncs it first)
uv run pytest                    # run tools without activating anything
uv sync                          # make the environment match the lock file exactly
uv lock --upgrade                # refresh locked versions
uv tree                          # show the dependency tree
uv python install 3.13           # install and manage Python versions
uvx ruff check .                 # run a tool once without installing it into the project (like pipx run)
uv pip install -r requirements.txt   # drop-in pip replacement
```

Verified example flow: `uv init` creates `pyproject.toml`; `uv add requests` writes `dependencies = ["requests>=..."]` and `uv.lock`; `uv run` executes code with those dependencies; `uv lock --check` confirms the lock matches. Alternatives with the same goals: **Poetry**, **PDM**, **Hatch**, **pip-tools**. Pick one per project and document it in the README.

## 7. Command-line programs

```python
import argparse

def build_parser():
    parser = argparse.ArgumentParser(prog="wordcount", description="Count words in text")
    parser.add_argument("text", help="the text to analyse")
    parser.add_argument("-l", "--lower", action="store_true", help="ignore case")
    parser.add_argument("-n", "--top", type=int, default=3, help="how many words to show")
    return parser

def run(argv):
    args = build_parser().parse_args(argv)
    words = args.text.lower().split() if args.lower else args.text.split()
    from collections import Counter
    return Counter(words).most_common(args.top)

print(run(["the cat and The dog and the bird", "--lower", "-n", "2"]))      # [('the', 3), ('and', 2)]
```

Separating **parsing** from **logic** (here `run(argv)`) makes CLIs testable. `argparse` is built in; **Typer** and **Click** build CLIs from type-hinted functions with less code. Return exit codes (`0` success, non-zero failure) and write errors to stderr.

## 8. Configuration and secrets

Follow the twelve-factor idea: **configuration that varies by environment lives in the environment**, not in code.

```python
import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    database_url: str
    debug: bool = False
    workers: int = 4

    @classmethod
    def from_env(cls, env=os.environ):
        return cls(
            database_url=env["DATABASE_URL"],                  # required: fail fast with KeyError if missing
            debug=env.get("DEBUG", "0") in ("1", "true", "True"),
            workers=int(env.get("WORKERS", "4")),
        )

print(Settings.from_env({"DATABASE_URL": "postgres://db/app", "WORKERS": "8"}))
# Settings(database_url='postgres://db/app', debug=False, workers=8)
```

- Pass `env` as a parameter so tests can supply their own dictionary (see [dependency injection](../../04-oop/composition-design/README.md)).
- **Never commit secrets** (API keys, passwords, tokens). Use environment variables, a `.env` file that is git-ignored (loaded by `python-dotenv` or `pydantic-settings`), or a secret manager (Vault, AWS Secrets Manager).
- Commit a `.env.example` listing names without values.

## 9. Code quality tools

| Tool | Job | Typical command |
|------|-----|-----------------|
| **ruff** | Very fast linter + formatter (replaces flake8, isort, black, pyupgrade...) | `ruff check --fix .` and `ruff format .` |
| **mypy / pyright** | Static type checking ([type hints](../typing-hints/README.md)) | `mypy src` |
| **pytest** | Tests ([testing](../exceptions-logging-testing/README.md)) | `pytest -q --cov=greeter` |
| **pre-commit** | Run checks automatically before each commit | `pre-commit install` |
| **tox / nox / uv** | Run tests across Python versions and environments | `nox` |
| **coverage** | Which lines tests executed | `pytest --cov` |
| **pip-audit** | Known vulnerabilities in dependencies | `pip-audit` |

Configure them in `pyproject.toml`. Example `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.0            # pin a real released version
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

### Continuous integration (CI)

CI runs your checks on every push and pull request on a clean machine, so "it works on my machine" stops being an excuse. A minimal GitHub Actions workflow (`.github/workflows/ci.yml`):

```yaml
name: ci
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.12", "3.14"]
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv sync --python ${{ matrix.python-version }}
      - run: uv run ruff check .
      - run: uv run mypy src
      - run: uv run pytest -q
```

Make the checks **required** before merging, keep the pipeline **fast** (under ~10 minutes), and treat a red build as the team's top priority.

## 10. Building, publishing and deploying

| Artifact | What it is | Create with |
|----------|-----------|-------------|
| **sdist** (`.tar.gz`) | Source distribution | `python -m build` |
| **wheel** (`.whl`) | Pre-built install format (fast, no build step for users) | `python -m build` |
| **Docker image** | Your app plus Python plus dependencies | `Dockerfile` |

Publishing a library: build the wheel, test on **TestPyPI**, then upload to **PyPI** with `twine upload` (or trusted publishing from CI, which avoids long-lived tokens). Tag releases in git, follow semantic versioning and keep a changelog.

A typical application Dockerfile:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev        # dependencies first: cached unless the lock file changes
COPY src ./src
CMD ["uv", "run", "python", "-m", "greeter"]
```

Practices: pin the base image tag, install dependencies before copying source (layer caching), run as a non-root user, keep images small (`-slim`), do not bake secrets into images, and expose configuration through environment variables.

## 11. Two real-world examples

### Example 1: Onboarding a new teammate in ten minutes
The repository has `pyproject.toml`, `uv.lock` and a README saying: `uv sync && uv run pytest`. A new engineer clones it, runs two commands and gets the exact versions the team uses, with tests passing. Pre-commit formats and lints on every commit, and CI repeats the checks on three Python versions. Compare with "install these packages, I think Python 3.9, ask Dave about the weird numpy version": that is the cost of skipping packaging discipline.

### Example 2: A shared internal library
Three services share validation and logging code. It becomes a `src/`-layout package with a version, published to the company's private package index by a CI job when a git tag is pushed. Services depend on `company-core>=1.4,<2`; a breaking change bumps the major version, so services upgrade on purpose, with their own tests as the safety net. The same package ships a `company-core-check` command line entry point used in CI.

## 12. Tips, tricks and pitfalls

- One virtual environment per project; never install project dependencies globally.
- Commit `pyproject.toml` and a lock file; do **not** commit `.venv`, `__pycache__`, `.env` or `dist/`.
- Use `python -m pip` / `python -m pytest` so you are sure which interpreter runs.
- Prefer the `src/` layout and editable installs for development.
- Pin applications tightly (lock file), libraries loosely (ranges).
- Do not use `sys.path` hacks or `PYTHONPATH` to "fix" imports: structure the package properly.
- Avoid wildcard imports and circular imports; keep import-time side effects minimal.
- Read dependency licenses and security advisories; remove unused dependencies.
- Declare `requires-python` and test on the oldest and newest versions you support.
- Automate: lint, format, type check, test and audit in pre-commit and CI.
- Document how to set up and run the project in the README (commands that actually work).

## 13. Check yourself

1. Module versus package? How does Python find them?
2. Why use a virtual environment?
3. What goes in `pyproject.toml`?
4. What is the point of the `src/` layout?
5. Difference between `pip install -e .` and `pip install .`?
6. Why have both `pyproject.toml` dependencies and a lock file?
7. What does semantic versioning promise?
8. How do environment variables help configuration, and what must never be committed?
9. What does CI add beyond running tests locally?
10. What does `uv run pytest` do differently from `pytest`?

<details>
<summary>Answers</summary>

1. A module is one `.py` file; a package is a directory of modules with an `__init__.py`. Python searches the directories in `sys.path` (current script directory, installed `site-packages`, and so on) and caches loaded modules in `sys.modules`.
2. Isolation: each project gets its own interpreter and dependency versions, avoiding conflicts and keeping the system Python clean.
3. Build system, project metadata (name, version, `requires-python`), dependencies and optional extras, entry points (scripts), and configuration for tools (pytest, ruff, mypy).
4. It prevents tests from importing the source folder directly instead of the installed package, so packaging errors are found early.
5. `-e` (editable) links the project so code changes apply immediately without reinstalling; a normal install copies the built package into `site-packages`.
6. `pyproject.toml` states what the project needs (ranges); the lock file records the exact resolved versions of all (including transitive) dependencies for reproducible installs.
7. `MAJOR.MINOR.PATCH`: breaking changes bump MAJOR, backward-compatible features bump MINOR, bug fixes bump PATCH (when projects follow it faithfully).
8. They let the same code run in dev, test and production with different settings and keep secrets out of source control; never commit passwords, tokens or API keys.
9. A clean, consistent machine runs lint, types and tests (on several Python versions) for every change and can block merges, so "works on my machine" problems are caught.
10. It first ensures the project's virtual environment exists and matches the lock file, then runs `pytest` inside it, so you do not need to activate anything.

</details>

[Exercises](exercises.md) · [Summary](summary.md)

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

Back to the [part overview](../README.md).
