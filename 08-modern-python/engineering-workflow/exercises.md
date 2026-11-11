# Engineering Workflow: Exercises

These problems go with the [Engineering Workflow lesson](README.md). Try each one before opening its solution.

## Problems

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

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Engineering Workflow](01-ci-docker-pre-commit-and-publishing.md)
