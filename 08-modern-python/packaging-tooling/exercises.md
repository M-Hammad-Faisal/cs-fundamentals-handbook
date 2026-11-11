# Packaging, Environments and Developer Tooling: Exercises

These problems go with the [Packaging, Environments and Developer Tooling lesson](README.md). Try each one before opening its solution.

## Problems

1. Create a virtual environment, install `requests` in it, and prove (with `sys.prefix` and `pip list`) that the system Python is unaffected.
2. Turn a folder with `utils.py` into an installable package called `textkit` using the `src/` layout and a `pyproject.toml`; install it editable and import it from another directory.
3. Add a console script `textkit-count` that prints the word count of a file given on the command line; test it with `subprocess`.
4. Make a `Settings.from_env` that reads `API_URL` (required), `TIMEOUT` (default 10, int) and `DEBUG` (default false, bool) from a dictionary; write pytest tests for the missing and invalid cases.
5. Explain the difference between `requirements.txt`, `pyproject.toml` dependencies and a lock file. Which would you commit for a web app? For a reusable library?
6. A project uses `requests>=2.0` with no lock file. Last week CI passed; today it fails with an error inside `requests`. What happened and how do you prevent it?
7. Write a `.gitignore` for a Python project and justify each entry.
8. Write the commands (using `uv`) to: start a project, add `httpx`, add `pytest` and `ruff` as dev dependencies, run the tests, and update all dependencies.
9. Write a GitHub Actions job that runs `ruff`, `mypy` and `pytest` on Python 3.11 and 3.13.
10. Fix this circular import and explain two ways to resolve it:
    ```python
    # a.py:  from b import make_b   ;  def make_a(): return "A" + make_b()
    # b.py:  from a import make_a   ;  def make_b(): return "B"
    ```

<details>
<summary>Solutions</summary>

**1.**
```text
python -m venv demo-env && source demo-env/bin/activate
python -c "import sys; print(sys.prefix != sys.base_prefix)"    # True (inside the venv)
pip install requests && pip list                                # requests appears here
deactivate
python -c "import requests"                                     # system Python: ModuleNotFoundError (unless installed globally before)
```

**2.**
```text
textkit/
├── pyproject.toml            # [project] name="textkit", version="0.1.0", requires-python=">=3.10"
└── src/textkit/
    ├── __init__.py
    └── utils.py
pip install -e .
cd /tmp && python -c "import textkit; print(textkit.__file__)"     # imported from the source folder, but available anywhere
```

**3.**
```toml
# pyproject.toml
[project.scripts]
textkit-count = "textkit.cli:main"
```
```python
# src/textkit/cli.py
import argparse, pathlib

def main(argv=None):
    p = argparse.ArgumentParser(prog="textkit-count")
    p.add_argument("path")
    args = p.parse_args(argv)
    print(len(pathlib.Path(args.path).read_text().split()))
    return 0
```
```python
# test (pytest)
import subprocess, sys

def test_cli(tmp_path):
    f = tmp_path / "a.txt"; f.write_text("one two three")
    out = subprocess.run([sys.executable, "-c", "from textkit.cli import main; main()", str(f)],
                         capture_output=True, text=True, check=True)
    assert out.stdout.strip() == "3"
```

**4.**
```python
# pytest
import pytest
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    api_url: str
    timeout: int = 10
    debug: bool = False

    @classmethod
    def from_env(cls, env):
        try:
            url = env["API_URL"]
        except KeyError:
            raise ValueError("API_URL is required") from None
        try:
            timeout = int(env.get("TIMEOUT", "10"))
        except ValueError:
            raise ValueError("TIMEOUT must be an integer") from None
        return cls(url, timeout, env.get("DEBUG", "false").lower() in ("1", "true", "yes"))

def test_defaults():
    s = Settings.from_env({"API_URL": "https://x.test"})
    assert (s.timeout, s.debug) == (10, False)

def test_overrides():
    s = Settings.from_env({"API_URL": "u", "TIMEOUT": "3", "DEBUG": "True"})
    assert (s.timeout, s.debug) == (3, True)

def test_missing_url():
    with pytest.raises(ValueError, match="API_URL"):
        Settings.from_env({})

def test_bad_timeout():
    with pytest.raises(ValueError, match="TIMEOUT"):
        Settings.from_env({"API_URL": "u", "TIMEOUT": "soon"})
```

**5.** `pyproject.toml` declares the project and its **requirements as ranges**; `requirements.txt` is a flat list (hand-written ranges, or a fully pinned `pip freeze`/`pip-compile` output); a **lock file** (`uv.lock`, `poetry.lock`) records the exact resolved versions of all direct and transitive dependencies. Web app: commit `pyproject.toml` **and** the lock file (reproducible deploys). Library: commit `pyproject.toml` with loose ranges (and optionally a lock for development/CI), but do not make users inherit exact pins.

**6.** An unpinned `requests>=2.0` lets CI install a newer release (or a newer transitive dependency) than last week, which broke something. Prevent it with a **lock file** (install exactly the tested versions), upper bounds where a major version is known to break, and scheduled dependency-update PRs that run CI before merging.

**7.**
```text
__pycache__/        # compiled bytecode, regenerated automatically
*.py[cod]
.venv/              # the virtual environment: recreate it, never share it
.env                # secrets and local settings
dist/ build/ *.egg-info/   # build output
.pytest_cache/ .mypy_cache/ .ruff_cache/ .coverage htmlcov/   # tool caches and reports
.idea/ .vscode/ .DS_Store                                      # editor and OS files
```

**8.**
```text
uv init myapp && cd myapp
uv add httpx
uv add --dev pytest ruff
uv run pytest
uv lock --upgrade && uv sync
```

**9.**
```yaml
name: ci
on: [push, pull_request]
jobs:
  checks:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv sync --python ${{ matrix.python-version }}
      - run: uv run ruff check .
      - run: uv run mypy src
      - run: uv run pytest -q
```

**10.** `a` imports `b` at the top while `b` imports `a` at the top, so one of them runs before the other is finished. Fixes: (1) move shared code into a third module that both import (preferred; breaks the cycle in the design), (2) import inside the function that needs it (`def make_b(): from a import make_a ...`) or import the module (`import a`) and use `a.make_a()` lazily. Best: reconsider the dependency direction so only one module depends on the other.

</details>

[Lesson](README.md) · [Summary](summary.md)
