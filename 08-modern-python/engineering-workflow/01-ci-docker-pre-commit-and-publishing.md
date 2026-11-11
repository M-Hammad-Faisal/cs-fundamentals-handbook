# Engineering Workflow: Project Layout, Quality Tools, CI, Docker and Publishing

**Prerequisites:** [packaging, environments and tooling](../packaging-tooling/README.md), [testing in depth](../testing-in-depth/01-pytest-mocking-and-property-testing.md), [Git and GitHub collaboration](../../00-foundations/command-line-and-git/github-collaboration.md), [containers](../../06-operating-systems/containers/01-containers-and-namespaces.md), [secrets and supply chain](../../10-security/secrets-and-supply-chain/01-secrets-dependencies-and-hardening.md). **You will learn:** how a professional Python project is put together and shipped: the **`src/` layout** and `pyproject.toml`, **ruff** (lint and format), **mypy** (types) and **pytest** wired together, **pre-commit** hooks, a **GitHub Actions CI** pipeline, a multi-stage **Dockerfile** with a non-root user, and **building and publishing** a package. Most of it was run for real on a demo project (build, install, lint, type-check, test, Docker build and run); the two things that need GitHub's servers (the CI workflow and the publish workflow) were only checked for valid YAML, and the lesson says so where it matters.

## 1. In plain words

Writing code is half the job. The other half is making sure it **works on every machine, stays correct as it changes, and reaches users reliably**. A good workflow makes the right thing automatic:

```
edit code -> pre-commit hooks (format, lint) -> git push -> CI (lint, types, tests on several Python versions)
          -> merge -> build (wheel / Docker image) -> publish or deploy
```

The principle is **fast feedback**: problems are caught at the earliest, cheapest step (your editor, then your commit, then CI) instead of in production.

## 2. A project that is ready to share: the `src/` layout

```text
greeter-demo/
  pyproject.toml              # metadata, dependencies and tool settings in ONE file
  README.md
  Dockerfile
  .dockerignore
  .pre-commit-config.yaml
  .github/workflows/ci.yml
  src/greeter/                # the importable package lives under src/
    __init__.py
    core.py
    cli.py
  tests/
    test_core.py
```

Why `src/`? With the package under `src/`, tests cannot accidentally import your **working folder** instead of the **installed** package, so you test what users will actually receive. You install the project in **editable mode** (`pip install -e ".[dev]"`) so changes apply immediately.

The whole project is small. First the configuration file:

```toml
# file: pyproject.toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "greeter-demo"
version = "0.1.0"
description = "A tiny package used to demonstrate packaging and CI"
readme = "README.md"
requires-python = ">=3.10"
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=8", "ruff", "mypy"]

[project.scripts]
greeter = "greeter.cli:main"             # creates a `greeter` command that calls greeter.cli.main()

[tool.setuptools.packages.find]
where = ["src"]

[tool.ruff]
line-length = 100
[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP"]      # pycodestyle errors, pyflakes, import sorting, bugbear, pyupgrade

[tool.mypy]
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
```

`pyproject.toml` is the standard (PEP 621) place for project metadata; tools read their settings from `[tool.*]` sections, so one file replaces `setup.py`, `setup.cfg`, `requirements.txt` and `.ruff.toml`. You can read it with the standard library:

```python
import tomllib

config = tomllib.loads('''
[project]
name = "greeter-demo"
version = "0.1.0"
requires-python = ">=3.10"

[project.scripts]
greeter = "greeter.cli:main"
''')
print(config["project"]["name"], config["project"]["scripts"])
# greeter-demo {'greeter': 'greeter.cli:main'}
```

The code and its test:

```python no-run
# file: src/greeter/__init__.py
"""greeter-demo: say hello."""

__version__ = "0.1.0"
```

```python no-run
# file: src/greeter/core.py
def greet(name: str, excited: bool = False) -> str:
    """Return a greeting for `name`."""
    message = f"Hello, {name}"
    return message + "!" if excited else message + "."
```

```python no-run
# file: src/greeter/cli.py
import argparse

from greeter.core import greet


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="greeter", description="Say hello.")
    parser.add_argument("--name", default="world")
    parser.add_argument("--excited", action="store_true")
    args = parser.parse_args(argv)
    print(greet(args.name, args.excited))
    return 0
```

```python no-run
# file: tests/test_core.py
from greeter.cli import main
from greeter.core import greet


def test_greet():
    assert greet("Ada") == "Hello, Ada."
    assert greet("Ada", excited=True) == "Hello, Ada!"


def test_cli(capsys):
    assert main(["--name", "Bo"]) == 0
    assert capsys.readouterr().out == "Hello, Bo.\n"
```

Set up and run everything in a virtual environment:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```

```text
..                                                                       [100%]
2 passed in 0.01s
```

## 3. Quality tools: ruff, mypy, pytest

**ruff** is a very fast linter and formatter (one tool replacing flake8, isort, pyupgrade and black). **mypy** checks type hints ([typing lesson](../typing-hints/README.md)). Together with pytest they catch most mistakes before running anything.

```bash
ruff check .          # lint: unused imports, likely bugs, style, import order
ruff check --fix .    # apply safe automatic fixes
ruff format .         # format code (consistent style, no arguments about it)
mypy src              # type-check
pytest -q             # run the tests
```

On a deliberately sloppy file (`bad.py`):

```python no-run
import os, sys
from greeter.core import greet

def shout(name):
    unused = 1
    return greet(name).upper()

def add(a: int, b: int) -> int:
    return a + b

add("1", 2)
```

the tools report real problems. `ruff check` (abridged) flags `E401` (several imports on one line), `I001` (unsorted imports), the unused imports `F401` and the unused variable `F841`, with a fix for most. `mypy` reports:

```text
src/greeter/bad.py:4: error: Function is missing a type annotation  [no-untyped-def]
src/greeter/bad.py:11: error: Argument 1 to "add" has incompatible type "str"; expected "int"  [arg-type]
Found 2 errors in 1 file (checked 1 source file)
```

`ruff format --diff` shows what it would reformat (here, the missing blank lines between functions). On the clean demo project:

```text
$ ruff check .
All checks passed!
$ mypy src
Success: no issues found in 3 source files
```

Make the tools **strict from the start** on a new project (`strict = true` in mypy); retrofitting types onto a large untyped codebase is painful, so tighten old code gradually.

## 4. pre-commit: catch problems before they are committed

**pre-commit** runs checks automatically on each `git commit` and refuses the commit if a check fails (auto-fixers change the files and you commit again). It stops formatting noise and silly mistakes from ever reaching the repository or CI.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0                     # pin to a current release; `pre-commit autoupdate` bumps it
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-yaml
      - id: check-added-large-files
      - id: detect-private-key      # secrets guard, see the supply-chain lesson
```

Install once per clone with `pip install pre-commit && pre-commit install`; run on everything with `pre-commit run --all-files`. (This file was checked only to be valid YAML here; hook versions move, so pin a current `rev`.)

## 5. Continuous integration with GitHub Actions

**CI** runs your checks on a clean machine for **every push and pull request**, on several Python versions. It answers "does it work anywhere other than my laptop?" and gives reviewers a green or red light. On GitHub, a workflow is a YAML file in `.github/workflows/`:

```yaml
# .github/workflows/ci.yml
name: CI
on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read                    # least privilege for the workflow token

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.10", "3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip
      - name: Install
        run: pip install -e ".[dev]"
      - name: Lint
        run: ruff check . && ruff format --check .
      - name: Type-check
        run: mypy src
      - name: Test
        run: pytest -q

  docker:
    runs-on: ubuntu-latest
    needs: test                     # only build the image if the tests passed
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t greeter-demo .
```

Reading it: **`on`** says when it runs; a **job** is a set of steps on a fresh virtual machine; the **matrix** runs the job once per Python version; **`needs`** orders jobs; each step is either `uses:` (a reusable action) or `run:` (a shell command). Good CI habits: keep it **fast** (cache dependencies, parallelise jobs), make it **identical to what developers run locally** (the same commands), **pin actions** to a version (or a commit hash for security-sensitive repositories), grant the **least permissions**, and treat a red build as the team's top priority. (This workflow was checked only for valid YAML here: it needs GitHub's runners to execute.)

## 6. Docker: a reproducible way to run it anywhere

A **Dockerfile** describes how to build an **image** (a packaged filesystem with your app and its dependencies); a **container** is a running instance ([containers lesson](../../06-operating-systems/containers/01-containers-and-namespaces.md)). A **multi-stage build** compiles in one stage and copies only the result into a small final stage; and a **non-root user** limits damage if the app is compromised.

```dockerfile
# file: Dockerfile
# ---- build stage: has the build tools, is thrown away ----
FROM python:3.13-slim AS build
WORKDIR /src
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir build && python -m build --wheel --outdir /dist

# ---- runtime stage: only what is needed to run ----
FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN useradd --create-home --uid 10001 appuser
COPY --from=build /dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl
USER appuser
ENTRYPOINT ["greeter"]
CMD ["--name", "container"]
```

```text
# file: .dockerignore
.git
.venv
__pycache__
dist
build
*.egg-info
.env
```

The `.dockerignore` keeps junk and **secrets** (`.env`) out of the image's build context. Building and running it for real:

```bash
docker build -t greeter-demo .
docker run --rm greeter-demo                       # uses the default CMD
docker run --rm greeter-demo --name Ada --excited  # arguments replace CMD, ENTRYPOINT stays
docker run --rm --entrypoint id greeter-demo       # check which user the process runs as
```

```text
Hello, container.
Hello, Ada!
uid=10001(appuser) gid=10001(appuser) groups=10001(appuser)
```

The process runs as `appuser` (uid 10001), not root. Other Docker habits: **pin the base image** (`python:3.13-slim`, ideally by digest in production), order the `COPY`/`RUN` lines so rarely changing steps come first (dependency installation is **cached** until `pyproject.toml` changes), never put secrets in `ENV` or `COPY`, one process per container, and keep images small (`slim` bases; `--no-cache-dir`). For development with several services (app plus database), **Docker Compose** describes them together in one file.

## 7. Building and publishing a package

**Build** turns the project into two distributable files: a **wheel** (`.whl`, a ready-to-unpack archive; fast to install) and an **sdist** (`.tar.gz`, the source).

```bash
pip install build twine
python -m build                  # creates dist/greeter_demo-0.1.0-py3-none-any.whl and dist/greeter_demo-0.1.0.tar.gz
twine check dist/*               # validates the metadata and README rendering
```

```text
Checking dist/greeter_demo-0.1.0-py3-none-any.whl: PASSED
Checking dist/greeter_demo-0.1.0.tar.gz: PASSED
```

A wheel is just a zip. Its contents (from `unzip -l`) are the package files plus metadata, including `entry_points.txt` that defines the `greeter` command:

```text
greeter/__init__.py
greeter/cli.py
greeter/core.py
greeter_demo-0.1.0.dist-info/METADATA
greeter_demo-0.1.0.dist-info/WHEEL
greeter_demo-0.1.0.dist-info/entry_points.txt
greeter_demo-0.1.0.dist-info/top_level.txt
greeter_demo-0.1.0.dist-info/RECORD
```

Prove it installs and works in a **clean environment** (the real test of packaging):

```bash
python -m venv /tmp/clean && /tmp/clean/bin/pip install dist/*.whl
/tmp/clean/bin/greeter --name Ada --excited
```

```text
Hello, Ada!
```

**Publishing** to the Python Package Index: practise on **TestPyPI** first (`twine upload --repository testpypi dist/*`). For real releases prefer **trusted publishing**: PyPI trusts your GitHub repository's workflow through short-lived OpenID Connect credentials, so **no long-lived API token** is stored anywhere ([supply-chain lesson](../../10-security/secrets-and-supply-chain/01-secrets-dependencies-and-hardening.md)).

```yaml
# .github/workflows/publish.yml
name: Publish
on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    environment: pypi                   # protected environment: can require manual approval
    permissions:
      id-token: write                   # lets the job request an OIDC token for PyPI
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.13"
      - run: pip install build && python -m build
      - uses: pypa/gh-action-pypi-publish@release/v1
```

(Also only YAML-checked here: it needs a configured PyPI project to run.) **Versioning:** follow **semantic versioning** (`MAJOR.MINOR.PATCH`: breaking change, new feature, bug fix); keep a **changelog**; tag releases in git (`git tag v0.1.0`); never reuse a version number: PyPI will not let you overwrite one.

## 8. Dependencies and reproducibility

- **Libraries** declare **ranges** (`requests>=2.31,<3`) so they combine well with other packages.
- **Applications** pin **exact versions** in a lock file (`uv pip compile`, `pip-compile`, `uv lock`, Poetry's `poetry.lock`) so every deploy installs the same thing; add hashes for tamper protection.
- Update dependencies **regularly and automatically** (Dependabot or Renovate pull requests, the tests tell you whether they are safe), and run `pip-audit` for known vulnerabilities.
- Separate **runtime** from **development** dependencies (`[project.optional-dependencies] dev`).
- **uv** (a very fast installer, resolver and project manager) can replace `pip`, `venv` and `pip-tools` in most workflows; the files above work with it unchanged.

## 9. A checklist for a new project

1. `git init`, `.gitignore` (virtualenvs, `__pycache__`, `.env`), a `README` that says how to install, run and test.
2. `pyproject.toml` with metadata and tool configuration; the `src/` layout.
3. ruff, mypy (strict) and pytest configured; pre-commit installed.
4. A CI workflow running the same commands on pushes and pull requests.
5. Configuration through **environment variables**, never committed secrets.
6. A Dockerfile if it is deployed as a container (non-root, pinned base).
7. A version, changelog and a release process.

## 10. Common mistakes

- Working without a virtual environment and polluting the global Python.
- `requirements.txt` with unpinned versions for an application: builds change under you.
- CI that differs from local commands, so "works on my machine" persists.
- Letting CI stay red ("flaky, ignore it").
- Putting secrets in the repository, an image layer or a build argument.
- Running containers as root; using `latest` tags for base images.
- Skipping `twine check` or never installing the built wheel into a clean environment before publishing.
- Long-lived PyPI tokens stored in CI secrets instead of trusted publishing.
- Version numbers that do not change when behaviour does.
- Huge Docker images and slow, uncached CI.

## 11. Two real-world examples

**Example 1: The Friday deploy.** A team ran tests by hand before each release and occasionally forgot. After adding CI with a Python-version matrix, a bug that only appeared on Python 3.10 (a removed library function) was caught on the pull request instead of by customers, and merging was blocked until the build was green.

**Example 2: The surprise upgrade.** An unpinned dependency released a breaking change on a Tuesday night; the next morning's deploy failed. The team moved to a lock file with hashes and automated dependency-update pull requests, so upgrades became deliberate, tested changes that arrived during working hours.

## 12. Practice

1. Add a `--shout` flag to the CLI that upper-cases the greeting, with a test, and make sure `ruff check`, `mypy src` and `pytest` all pass.
2. Add a CI step that fails the build if test coverage is below 90 percent (`pytest --cov=greeter --cov-fail-under=90`).
3. Write a `.pre-commit-config.yaml` hook list that includes a check for private keys and large files.
4. In the Dockerfile, why are the `COPY pyproject.toml README.md ./` and `COPY src ./src` lines separate from the build command? Reorder them to improve layer caching if you also had a `requirements.lock` file.
5. List three differences between a wheel and an sdist.
6. Why is trusted publishing safer than a PyPI API token in a repository secret?

<details>
<summary>Solutions</summary>

1. ```python
   # in cli.py, after parser.add_argument("--excited", ...):
   #     parser.add_argument("--shout", action="store_true")
   # and replace the print with:
   #     message = greet(args.name, args.excited)
   #     print(message.upper() if args.shout else message)
   # test:
   #     def test_shout(capsys):
   #         assert main(["--name", "Bo", "--shout"]) == 0
   #         assert capsys.readouterr().out == "HELLO, BO.\n"
   ```
2. In the workflow, change the test step to `run: pytest -q --cov=greeter --cov-fail-under=90` and add `pytest-cov` to the `dev` extras.
3. ```yaml
   repos:
     - repo: https://github.com/pre-commit/pre-commit-hooks
       rev: v5.0.0
       hooks:
         - id: detect-private-key
         - id: check-added-large-files
           args: [--maxkb=500]
   ```
4. Docker caches each layer and reuses it until the input of that line changes. Copying the rarely changing files (`pyproject.toml`, a lock file) and installing dependencies **before** copying the frequently changing source means editing code does not re-run the dependency installation. With a lock file: `COPY requirements.lock ./`, `RUN pip install -r requirements.lock`, **then** `COPY src ./src`.
5. A wheel is a pre-built archive that installs by unpacking (no build step, can contain compiled code for one platform); an sdist contains the source and must be built on the user's machine (needs build tools); an sdist is platform-independent and is the fallback when no matching wheel exists.
6. There is no long-lived secret to leak or steal: PyPI issues access only to the specific workflow in the specific repository, for minutes, so a compromised secrets store or a malicious pull request cannot reuse it later.

</details>

## 13. Check yourself

1. Why use the `src/` layout?
2. What goes in `pyproject.toml`?
3. What do ruff, mypy and pytest each check?
4. What does pre-commit do, and how is it different from CI?
5. What is a CI matrix?
6. Why a multi-stage Dockerfile and a non-root user?
7. What is trusted publishing?

<details>
<summary>Answers</summary>

1. So tests import the installed package rather than the working directory, catching packaging mistakes and testing what users receive.
2. Project metadata (name, version, dependencies, entry points, Python requirement), the build backend and the settings for tools such as ruff, mypy and pytest.
3. Ruff: style and likely bugs (and formatting); mypy: type consistency; pytest: behaviour.
4. It runs checks locally at commit time so bad changes never reach the repository; CI runs on a clean server for every push and pull request, so it is the shared, authoritative gate.
5. A set of values (such as Python versions) for which the same job runs in parallel.
6. The multi-stage build leaves build tools out of the final image (smaller, fewer vulnerabilities); a non-root user limits what a compromised process can do.
7. Publishing to PyPI using short-lived OpenID Connect credentials issued to a specific repository workflow, with no stored API token.

</details>

[Back to Modern Python](../README.md)
