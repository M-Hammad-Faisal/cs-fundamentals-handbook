# Engineering Workflow

Project layout, quality tools, CI, Docker and publishing a package.

## Detailed lessons

- [Engineering workflow: project layout, quality tools, CI, Docker and publishing](01-ci-docker-pre-commit-and-publishing.md)

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

## Quick reference

| Question | Answer |
|----------|--------|
| Why use the `src/` layout? | So tests import the installed package rather than the working directory, catching packaging mistakes and testing what users receive. |
| What goes in `pyproject.toml`? | Project metadata (name, version, dependencies, entry points, Python requirement), the build backend and the settings for tools such as ruff, mypy and pytest. |
| What do ruff, mypy and pytest each check? | Ruff: style and likely bugs (and formatting); mypy: type consistency; pytest: behaviour. |
| What does pre-commit do, and how is it different from CI? | It runs checks locally at commit time so bad changes never reach the repository; CI runs on a clean server for every push and pull request, so it is the shared, authoritative gate. |
| What is a CI matrix? | A set of values (such as Python versions) for which the same job runs in parallel. |

Back to [modern Python](../README.md).
