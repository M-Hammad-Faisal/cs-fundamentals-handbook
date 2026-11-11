# Setting Up Your Computer for This Handbook: Exercises

Try each problem before opening its solution. These are the practice problems of this topic's lessons, collected in one place.

## Setting Up Your Computer for This Handbook

Answer each question, then check yourself.

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

[Lesson](README.md) · [Summary](summary.md)
