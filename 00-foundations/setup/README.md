# Setting Up Your Computer for This Handbook

**Prerequisites:** none. **Goal:** in about 30 minutes you will have Python, a code editor, Git, a virtual environment, and a first project that runs tests, so every example in the handbook works on your machine.

## 1. What you need

| Tool | Why | Check it works |
|------|-----|----------------|
| **Python 3.10 or newer** (3.12+ recommended) | runs all the examples | `python3 --version` |
| **A code editor** (VS Code, PyCharm, or similar) | writing and debugging code | open a `.py` file |
| **A terminal** | running commands | see [terminal basics](../command-line-and-git/terminal-basics.md) |
| **Git** | version control | `git --version` |
| **pip / uv** | installing packages | `python3 -m pip --version` |

## 2. Install Python

Check what you already have: open a terminal and run `python3 --version` (on Windows try `py --version`). If it prints `3.10` or higher you can skip installation.

### macOS

```text
brew install python           # with Homebrew (install it from https://brew.sh)   -- or download the installer from python.org
python3 --version
```

### Windows

```text
winget install Python.Python.3.12        # or download the installer from python.org
# IMPORTANT in the installer: tick "Add python.exe to PATH"
py --version
```

For a Linux-like environment on Windows, install **WSL** (Windows Subsystem for Linux) and follow the Linux steps inside it; it matches most tutorials and servers.

### Linux (Debian/Ubuntu)

```text
sudo apt update && sudo apt install python3 python3-venv python3-pip git
python3 --version
```

### Managing several Python versions (optional, later)

`uv python install 3.12` (using the `uv` tool) or `pyenv install 3.12` let you run different versions per project. See [packaging and tooling](../../08-modern-python/packaging-tooling/README.md).

### Verify

```python
import sys, platform
print(sys.version_info >= (3, 10))                 # should print True
print(platform.python_version(), platform.system())
```

You can also type `python3` in the terminal to start the **REPL** (an interactive prompt): try `2 + 3`, then `exit()`.

## 3. Choose an editor

| Editor | Good for | Notes |
|--------|----------|-------|
| **VS Code** (free) | beginners and most developers | install the official *Python* extension; built-in terminal, debugger, Git |
| **PyCharm Community** (free) | Python-focused projects | strong refactoring and debugging out of the box |
| **WebStorm / IntelliJ / others** | if you already use them | add the Python plugin |
| **Jupyter notebooks** | data exploration, learning | run code in cells; `pip install jupyterlab` |

Whichever you pick, learn: running a file, setting a **breakpoint** and stepping through code ([debugging](../python-fundamentals/06-debugging-and-testing.md)), the integrated terminal, search across files, and "go to definition".

Helpful settings: auto-save, a formatter on save (`ruff format`), show whitespace, 4-space indentation, a visible line-length ruler at 88.

## 4. Install Git

```text
git --version                       # already installed? (macOS offers to install developer tools the first time)
# macOS:   brew install git          Windows: winget install Git.Git          Linux: sudo apt install git
git config --global user.name  "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
```

Then follow [Git basics](../command-line-and-git/git-basics.md). Create a free **GitHub** account and add an SSH key ([GitHub and collaboration](../command-line-and-git/github-collaboration.md)).

## 5. Virtual environments and pip

A **virtual environment** is a private copy of Python and its installed packages for one project, so projects never conflict. **Create one for every project.**

```text
mkdir myproject && cd myproject
python3 -m venv .venv                       # create the environment in a folder named .venv
source .venv/bin/activate                   # macOS/Linux       (Windows PowerShell: .venv\Scripts\Activate.ps1)
(.venv) $ python --version                  # the prompt now shows (.venv): you are INSIDE the environment
(.venv) $ pip install pytest                # installs only into this project
(.venv) $ pip list                          # see what is installed
(.venv) $ pip freeze > requirements.txt     # record exact versions so others can recreate it
(.venv) $ deactivate                        # leave the environment
```

Later, someone else (or you on a new machine) runs `python3 -m venv .venv`, activates it, and `pip install -r requirements.txt`.

```python
import sys
print(sys.prefix != sys.base_prefix)      # True when running inside a virtual environment, False for the system Python
```

Rules: **never `sudo pip install`**; put `.venv/` in `.gitignore`; use `python -m pip` so you know which Python runs; if an import fails with `ModuleNotFoundError`, you are probably in the wrong environment or forgot to install the package.

## 6. A first project: hello, test, commit

Build the smallest "professional" project and run it. This is a template you can copy.

```text
myproject/
├── .gitignore
├── README.md
├── requirements.txt
├── greeter.py
└── test_greeter.py
```

```python
# greeter.py
def greet(name: str, excited: bool = False) -> str:
    """Return a greeting for `name`."""
    return f"Hello, {name}{'!' if excited else '.'}"

if __name__ == "__main__":
    print(greet("world", excited=True))
```

```python
# test_greeter.py  (pytest finds files named test_*.py)
from greeter import greet

def test_plain_greeting():
    assert greet("Ana") == "Hello, Ana."

def test_excited_greeting():
    assert greet("Ana", excited=True) == "Hello, Ana!"
```

```text
(.venv) $ python greeter.py                   # prints: Hello, world!
(.venv) $ pytest -q                           # prints: 2 passed in 0.01s
(.venv) $ git init && git add . && git commit -m "Add greeter with tests"
```

You can verify this exact project from Python (it builds it in a temporary folder and runs it):

```python
import subprocess, sys, tempfile, textwrap
from pathlib import Path

project = Path(tempfile.mkdtemp())
(project / "greeter.py").write_text(textwrap.dedent('''
    def greet(name, excited=False):
        return f"Hello, {name}{'!' if excited else '.'}"

    if __name__ == "__main__":
        print(greet("world", excited=True))
'''))
(project / "test_greeter.py").write_text(textwrap.dedent('''
    import unittest
    from greeter import greet

    class TestGreet(unittest.TestCase):
        def test_plain(self):
            self.assertEqual(greet("Ana"), "Hello, Ana.")
        def test_excited(self):
            self.assertEqual(greet("Ana", excited=True), "Hello, Ana!")

    if __name__ == "__main__":
        unittest.main()
'''))
run = subprocess.run([sys.executable, "greeter.py"], cwd=project, capture_output=True, text=True)
print(run.stdout.strip())                                              # Hello, world!
tests = subprocess.run([sys.executable, "-m", "unittest", "-q"], cwd=project, capture_output=True, text=True)
print(tests.returncode, tests.stderr.strip().splitlines()[-1])         # 0 OK
```

## 7. Running the handbook's examples

- Code blocks that start with `import` or define functions can be pasted into a `.py` file or the REPL; **type them rather than paste** so you notice details.
- Blocks marked as text (for example shell commands) are for the terminal, not Python.
- Many examples print results shown in comments (`# 12.57`); if yours differs, compare carefully (floating-point formatting, random numbers and timings can vary slightly).
- Use the **exercises**: try before looking at solutions, then run both and compare.
- Keep a notes file (or Git repo) of what you learn; use the [revision schedule](../../revision/schedule.md).

## 8. Troubleshooting

| Problem | Likely cause and fix |
|---------|----------------------|
| `python: command not found` | try `python3`; on Windows try `py`; check Python is on the PATH (reinstall with "Add to PATH") |
| `ModuleNotFoundError: No module named 'x'` | activate the virtual environment, then `python -m pip install x` |
| `pip` installs to the wrong Python | use `python -m pip ...` (same interpreter) |
| `Permission denied` running a script | `chmod +x script.sh` or run with `python script.py` |
| `SyntaxError` after copying code | smart quotes or hidden characters from a web page; retype it |
| Tab/space `IndentationError` | configure the editor for 4 spaces; convert tabs |
| Different results than the book | check your Python version (`python --version`) |
| Terminal looks frozen | a program is waiting for input or running; press `Ctrl+C` to stop it |
| Anything weird with Git | stop and run `git status`; see [undoing mistakes](../command-line-and-git/git-undo-and-history.md) |

## 9. Check yourself

1. How do you check which Python version is running?
2. Why use a virtual environment for every project?
3. What does `pip freeze > requirements.txt` do?
4. How do you know you are inside a virtual environment?
5. What are the commands to create and activate one?

<details>
<summary>Answers</summary>

1. `python3 --version` (or `python --version`, `py --version` on Windows), or `sys.version_info` inside Python.
2. To keep each project's dependencies isolated so versions never conflict and the project is reproducible.
3. It writes the exact installed package versions to `requirements.txt` so others can reinstall the same set.
4. The prompt shows `(.venv)` and `sys.prefix != sys.base_prefix` is `True`.
5. `python3 -m venv .venv` then `source .venv/bin/activate` (Windows: `.venv\Scripts\activate`).

</details>

[Back to foundations](../README.md)
