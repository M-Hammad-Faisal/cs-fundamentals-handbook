# Engineering Workflow: One-Page Summary

## Questions worth remembering

- **Why use the `src/` layout?** So tests import the installed package rather than the working directory, catching packaging mistakes and testing what users receive.
- **What goes in `pyproject.toml`?** Project metadata (name, version, dependencies, entry points, Python requirement), the build backend and the settings for tools such as ruff, mypy and pytest.
- **What do ruff, mypy and pytest each check?** Ruff: style and likely bugs (and formatting); mypy: type consistency; pytest: behaviour.
- **What does pre-commit do, and how is it different from CI?** It runs checks locally at commit time so bad changes never reach the repository; CI runs on a clean server for every push and pull request, so it is the shared, authoritative gate.
- **What is a CI matrix?** A set of values (such as Python versions) for which the same job runs in parallel.
- **Why a multi-stage Dockerfile and a non-root user?** The multi-stage build leaves build tools out of the final image (smaller, fewer vulnerabilities); a non-root user limits what a compromised process can do.

Practice problems with solutions are in the **Practice** section of each lesson.

[Lesson](README.md) · [Engineering Workflow](01-ci-docker-pre-commit-and-publishing.md)
