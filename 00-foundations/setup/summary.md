# Setting Up Your Computer for This Handbook: One-Page Summary

## Questions worth remembering

- **How do you check which Python version is running?** `python3 --version` (or `python --version`, `py --version` on Windows), or `sys.version_info` inside Python.
- **Why use a virtual environment for every project?** To keep each project's dependencies isolated so versions never conflict and the project is reproducible.
- **What does `pip freeze > requirements.txt` do?** It writes the exact installed package versions to `requirements.txt` so others can reinstall the same set.
- **How do you know you are inside a virtual environment?** The prompt shows `(.venv)` and `sys.prefix != sys.base_prefix` is `True`.
- **What are the commands to create and activate one?** `python3 -m venv .venv` then `source .venv/bin/activate` (Windows: `.venv\Scripts\activate`).

Practice problems with solutions are in the exercises page and in the **Practice** section of each lesson.

[Lesson](README.md) · [Exercises](exercises.md)
