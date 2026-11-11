# Setting Up Your Computer for This Handbook: One-Page Summary

## Key facts

- **Check the interpreter:** `python3 --version` (Windows: `py --version`); these lessons assume Python 3.12 or newer.
- **Virtual environment:** `python3 -m venv .venv`, then `source .venv/bin/activate` (Windows: `.venv\Scripts\activate`); the prompt shows `(.venv)` and `sys.prefix != sys.base_prefix`.
- **Packages:** `python3 -m pip install name`, `pip freeze > requirements.txt` to record versions, `pip install -r requirements.txt` to rebuild; `deactivate` leaves the environment.
- **Run code:** `python3 script.py`, `python3 -m pytest`; `python3 -m pip` guarantees pip belongs to the same Python.
- **Repository hygiene:** keep `.venv/` in `.gitignore`; commit `requirements.txt`, not the environment.

## Pitfalls

- Installing packages globally instead of in the project's environment.
- A `pip` that belongs to a different Python than `python`: use `python3 -m pip`.
- Forgetting to activate the environment, then wondering why an import fails.
- Committing the `.venv` folder.

## Self-check

- **How do you check which Python version is running?** `python3 --version` (or `python --version`, `py --version` on Windows), or `sys.version_info` inside Python.
- **Why use a virtual environment for every project?** To keep each project's dependencies isolated so versions never conflict and the project is reproducible.
- **What does `pip freeze > requirements.txt` do?** It writes the exact installed package versions to `requirements.txt` so others can reinstall the same set.
- **How do you know you are inside a virtual environment?** The prompt shows `(.venv)` and `sys.prefix != sys.base_prefix` is `True`.
- **What are the commands to create and activate one?** `python3 -m venv .venv` then `source .venv/bin/activate` (Windows: `.venv\Scripts\activate`).

[Lesson](README.md) · [Exercises](exercises.md)
