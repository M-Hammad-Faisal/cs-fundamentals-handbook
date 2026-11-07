# GitHub and Collaborating with Others

**Prerequisites:** [Git basics](git-basics.md), [branches and merging](git-branches-and-merging.md). **You will learn:** remotes (`clone`, `push`, `pull`, `fetch`), SSH keys, the pull-request workflow, forking and contributing to open source, code review etiquette, issues, README/license basics, and how CI protects `main`.

## 1. In plain words

Git works entirely on your own computer. To **share and collaborate** you put a copy of the repository on a server: a **remote**. **GitHub** (also GitLab, Bitbucket) hosts remotes and adds collaboration features: **pull requests** (propose changes and get them reviewed), **issues** (track bugs and tasks), **Actions/CI** (run tests automatically), and a public **portfolio** of your work.

```text
 Your computer                              GitHub (remote "origin")                 Teammate's computer
 ┌─────────────┐   git push ────────────►  ┌────────────────────┐ ◄──── git push    ┌─────────────┐
 │ local repo  │                           │  shared repository │                   │ local repo  │
 └─────────────┘   git pull/fetch ◄──────  └────────────────────┘  ──── git pull ─► └─────────────┘
```

## 2. Remotes: push, pull, fetch, clone

```text
$ git clone https://github.com/user/project.git     # copy a remote repository (all history) to your computer
$ cd project
$ git remote -v                                      # list remotes ("origin" is the default name for where you cloned from)
origin  https://github.com/user/project.git (fetch)
origin  https://github.com/user/project.git (push)

# Connect an existing local repo to a new empty GitHub repo:
$ git remote add origin git@github.com:you/myproject.git
$ git push -u origin main                            # -u remembers: "main tracks origin/main"

$ git push                                           # upload your new commits
$ git fetch                                          # download others' commits WITHOUT changing your files (safe)
$ git pull                                           # fetch + merge into your current branch  (git pull --rebase for a straight history)
$ git status                                         # "Your branch is behind 'origin/main' by 2 commits"
```

| Command | Meaning |
|---------|---------|
| `git fetch` | update your knowledge of the remote (`origin/main`) but do not touch your branch |
| `git pull` | `fetch` then merge (or rebase) into the current branch |
| `git push` | send your local commits to the remote branch |
| `git push -u origin feature` | publish a new branch and set it to track the remote one |
| `git branch -r` | list remote branches |
| `git push origin --delete feature` | delete a remote branch |

**If `git push` is rejected** ("non-fast-forward"), someone pushed first: run `git pull` (resolve any conflicts), then push again. Never "force push" to fix it on a shared branch.

## 3. Authentication: SSH keys (and tokens)

GitHub needs to know who you are. Two common ways:

- **HTTPS + personal access token** (instead of your password).
- **SSH keys** (recommended): a key pair; the **private** key stays on your computer, the **public** key goes to GitHub.

```text
$ ssh-keygen -t ed25519 -C "you@example.com"        # create the key pair (press Enter to accept defaults)
$ cat ~/.ssh/id_ed25519.pub                          # copy THIS public key into GitHub: Settings > SSH and GPG keys
$ ssh -T git@github.com                              # test: "Hi username! You've successfully authenticated..."
```

**Never share or commit the private key** (no `.pub` extension) or any token. Use a different key per machine, protect it with a passphrase.

## 4. The pull-request (PR) workflow

This is how almost every team works day to day (GitHub Flow):

```text
 1. Update main:           git switch main && git pull
 2. Create a branch:       git switch -c feature/search-bar
 3. Work + commit:         (small commits with clear messages)
 4. Push the branch:       git push -u origin feature/search-bar
 5. Open a Pull Request:   on GitHub (base: main, compare: your branch); describe what and why
 6. CI runs automatically: tests, linters, type checks
 7. Code review:           teammates comment, you push fixes (new commits update the PR)
 8. Approve + merge:       "Squash and merge" / "Rebase and merge" / "Create a merge commit"
 9. Clean up:              delete the branch; git switch main && git pull
```

### Writing a good pull request

```text
Title:   Add search bar to the product list

What:    Adds a search input that filters products by name (case-insensitive).
Why:     Users could not find products in long lists (issue #231).
How:     Debounced input in ProductList; new `filter_products()` helper with tests.
Testing: Added 6 unit tests; manually checked empty, no-match and special-character searches.
Screenshots: (before / after)
Notes:   Does not change sorting. Follow-up: highlight matches (#240).
```

Guidelines: **small PRs** (under ~400 lines) get reviewed faster and better; one purpose per PR; explain *why*; link the issue (`Closes #231`); include tests; self-review your diff before asking others; keep CI green.

### Merge options on GitHub

| Option | Result | Use when |
|--------|--------|----------|
| **Merge commit** | keeps all branch commits plus a merge commit | you want full history |
| **Squash and merge** | all branch commits become **one** commit on `main` | typical default: clean history, messy WIP commits hidden |
| **Rebase and merge** | commits replayed on `main` without a merge commit | linear history, tidy commits |

## 5. Code review: giving and receiving

**As an author:** keep the PR small, explain context, respond to every comment ("Done", or explain why not), do not take feedback personally (it is about the code), say thanks.

**As a reviewer:** be kind and specific; ask questions ("what happens if the list is empty?") rather than commanding; separate **blocking issues** (bugs, security) from **nits** (style: prefix with "nit:"); praise good solutions; check correctness, tests, readability, naming, error handling, performance and security; approve when it is good enough, not perfect.

Review checklist: Does it do what the description says? Are edge cases handled? Are there tests? Is it readable? Any secrets or debug code? Does it change behavior silently? Is documentation updated?

## 6. Forks and contributing to open source

You cannot push to someone else's repository, so you **fork** it (your own copy on GitHub), then propose changes with a PR.

```text
 1. Fork the repo on GitHub (button)             -> github.com/you/project  (your copy)
 2. git clone git@github.com:you/project.git
 3. git remote add upstream https://github.com/original/project.git     # the original repo
 4. git switch -c fix/typo-in-readme
 5. (edit) git commit -am "Fix typo in README"
 6. git push -u origin fix/typo-in-readme
 7. Open a Pull Request: you/project:fix/typo-in-readme  ->  original/project:main
 8. Keep in sync later:  git fetch upstream && git switch main && git merge upstream/main
```

How to start contributing: look for issues labelled **good first issue** or **help wanted**; read `CONTRIBUTING.md` and the code of conduct; start with docs or tests; ask before large changes; be patient with maintainers. A few merged PRs in well-known projects are excellent résumé items ([interview playbook](../../09-interview-playbook/behavioral-and-process/README.md)).

## 7. Issues, projects and labels

An **issue** is a tracked task, bug report or feature request. A good bug report has: **title** (specific), **steps to reproduce**, **expected vs actual behavior**, environment (OS, version), logs or screenshots. Link PRs to issues with `Closes #12` so merging closes them automatically. Labels (`bug`, `enhancement`, `documentation`), milestones and project boards organize the work.

## 8. A good repository: README, license, structure

Every public repository should have:

- **README.md**: what it is, why it exists, a screenshot or demo, how to install and run, how to test, how to contribute, license.
- **LICENSE**: without one, nobody may legally reuse your code (MIT = permissive; Apache-2.0 = permissive with patent grant; GPL = copyleft).
- **.gitignore**, **requirements/pyproject**, **tests/**, **CONTRIBUTING.md** (optional), **CHANGELOG.md** (optional).
- **Protected `main`**: require PRs, reviews and passing checks before merging (Settings > Branches).

```text
my-project/
├── README.md
├── LICENSE
├── .gitignore
├── pyproject.toml
├── src/my_project/...
├── tests/...
└── .github/workflows/ci.yml        <- GitHub Actions
```

## 9. Continuous integration with GitHub Actions

A workflow file in `.github/workflows/` runs on every push and PR: tests, linting, type checking. PRs show a green check or red X, and branch protection can **block merging until it is green**.

```yaml
# .github/workflows/ci.yml
name: ci
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt pytest
      - run: pytest -q
```

More in [packaging and tooling](../../08-modern-python/packaging-tooling/README.md).

## 10. Working agreements that make teams fast

- **Pull before you start; push often** (at least daily) so work is backed up and visible.
- **Branch per task**, merge through PRs, delete merged branches.
- **Keep `main` always working** (green CI).
- **Small, frequent merges** beat big-bang merges.
- **Communicate**: comment on issues, ask before big refactors, tell people when you change shared files.
- Agree on conventions (commit style, branch names, formatting via a tool like `ruff format` so formatting never causes review noise).
- **Never commit secrets**; use environment variables and a secrets manager.

## 11. Two real-world examples

**Example 1: A student project team of four.** They use GitHub Flow: protected `main`, one branch per task, PRs with at least one review, CI running pytest and ruff. Merge conflicts are rare because branches are small. When the deadline hits, `main` is always demonstrable, and the commit history (commits, PRs, issues) shows each person's contribution: great evidence for a portfolio or a group-project grade.

**Example 2: First open-source contribution.** A student notices a broken link in a library's documentation. They fork, fix the link, and open a PR titled "Fix broken link in installation docs", referencing the issue. A maintainer approves and merges within a day. Total effort: 15 minutes; result: a visible contribution and understanding of the real workflow.

## 12. Common mistakes

- Working directly on `main` and pushing half-done work.
- Giant PRs (reviewers skim; bugs slip through).
- `git push --force` on shared branches (destroys teammates' work).
- Committing secrets, large binaries or `node_modules`/`.venv`.
- Ignoring failing CI or review comments.
- Not pulling before pushing (rejected pushes, avoidable conflicts).
- No README: nobody can run your project.
- Forgetting to delete the key from GitHub if a laptop is lost; losing track of which email is on commits.

## 13. Practice

1. Create a GitHub repository, clone it, add a README and push.
2. Make a feature branch, push it, open a pull request to `main` on your own repo, and merge it using "Squash and merge".
3. Fork a small public repository (for example a practice repo), fix a typo and open a PR (to your own fork's `main` if you do not want to disturb the original).
4. With a friend, both edit the same line, push, and resolve the resulting conflict.
5. Write a `.github/workflows/ci.yml` that runs `python -m unittest` on every PR.
6. Write a good bug report for a hypothetical crash (title, steps, expected, actual, environment).
7. Review a classmate's PR with three constructive comments and one compliment.

<details>
<summary>Solutions</summary>

**1.** On GitHub create an empty repo; `git clone git@github.com:you/name.git && cd name && echo "# name" > README.md && git add . && git commit -m "Add README" && git push`.

**2.** `git switch -c feature/x`, commit, `git push -u origin feature/x`, then on GitHub "Compare & pull request", merge with "Squash and merge", delete the branch, `git switch main && git pull`.

**3.** Fork (button), clone your fork, branch, fix, push, open a PR; keep `upstream` configured and sync with `git fetch upstream`.

**4.** Person A pushes first; person B's `git push` is rejected; B runs `git pull` (conflict), edits the file to keep the agreed text, removes markers, `git add`, `git commit`, `git push`.

**5.**
```yaml
name: ci
on: [pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: python -m unittest -v
```

**6.**
```text
Title: App crashes with ZeroDivisionError when the cart is empty
Steps: 1) Open the app 2) Click Checkout with no items
Expected: message "Your cart is empty"
Actual: crash, traceback ends in calculate_average() division by zero
Environment: Python 3.12, macOS 14, app v1.4.2
Logs/screenshot: (attached)
```

**7.** Example comments: "Question: what happens if `items` is empty? (blocking)"; "nit: rename `x` to `item_count`"; "Suggestion: this loop could be a comprehension"; "Nice use of a helper function; much easier to test."

</details>

## 14. Check yourself

1. What is a remote? What is `origin`?
2. Difference between `git fetch` and `git pull`?
3. What are the steps of the pull-request workflow?
4. Why are small PRs better?
5. What is a fork and when do you use one?
6. What does CI do for a pull request?
7. What should never be committed or shared?

<details>
<summary>Answers</summary>

1. A remote is a copy of the repository on a server; `origin` is the default name of the one you cloned from.
2. `fetch` downloads new commits without changing your files; `pull` fetches and then merges (or rebases) them into your current branch.
3. Update `main`, create a branch, commit, push, open a PR, let CI run, review and fix, merge, clean up.
4. They are easier and faster to review, contain fewer hidden bugs and cause fewer conflicts.
5. A personal copy of someone else's repository on GitHub; you use it to propose changes (via a PR) to projects you cannot push to.
6. It automatically runs tests, linters and other checks and reports pass/fail before merging.
7. Secrets (passwords, tokens, private keys, `.env`), large generated files and personal data.

</details>

[Back to command line and Git](README.md) · Previous: [undoing mistakes and history](git-undo-and-history.md)
