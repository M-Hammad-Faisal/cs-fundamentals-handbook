# Command Line and Git: Exercises

These problems go with the [Command Line and Git lesson](README.md). Try each one before opening its solution.

## Problems

### The Command Line

1. Create a folder `practice` with subfolders `a` and `b` using one command; create a file in each.
2. Write the pipeline to count how many `.py` files exist in a project.
3. Show the 5 most recently modified files in a folder.
4. Explain the difference between `>` and `>>` and between `&&` and `;`.
5. Using Python, mimic `grep -c ERROR app.log` (count the matching lines).
6. What does `chmod 755 script.sh` give the owner, group and others?

<details>
<summary>Solutions</summary>

**1.** `mkdir -p practice/a practice/b && touch practice/a/one.txt practice/b/two.txt`

**2.** `find . -name "*.py" | wc -l`

**3.** `ls -t | head -5` (`-t` sorts by modification time, newest first).

**4.** `>` creates or **overwrites** the file; `>>` **appends**. `a && b` runs `b` only if `a` succeeded; `a; b` runs `b` regardless.

**5.**
```python
lines = ["INFO ok", "ERROR disk", "ERROR net", "WARN slow"]
print(sum(1 for line in lines if "ERROR" in line))          # 2
```

**6.** 7 = `rwx` for the owner, 5 = `r-x` for the group, 5 = `r-x` for others.

</details>

### Git Basics

1. Create a repository, add two files, commit them separately with good messages, and view the history.
2. Edit a file, use `git diff`, stage it, use `git diff --staged`, then commit.
3. Create a `.gitignore` that ignores `*.log` and a `secrets.env` file; verify with `git status` that they are ignored.
4. Use `git add -p` to commit only part of your edits to a file.
5. Use `git blame` and `git log -p` on a file with several commits; explain what each line shows.
6. Explain why a commit hash changes if you change one letter in the commit message.

<details>
<summary>Solutions</summary>

**1.**
```text
git init demo && cd demo
echo "# Demo" > README.md && git add README.md && git commit -m "Add README"
echo "print('hi')" > app.py && git add app.py && git commit -m "Add app entry point"
git log --oneline
```

**2.** Edit `app.py`; `git diff` shows the unstaged change; `git add app.py`; `git diff` is now empty but `git diff --staged` shows it; `git commit -m "Print greeting"`.

**3.**
```text
printf '*.log\nsecrets.env\n' > .gitignore
touch app.log secrets.env
git status --short          # only .gitignore appears, the other two are hidden
```

**4.** `git add -p app.py` shows each "hunk" and asks `y` (stage), `n` (skip), `s` (split into smaller hunks), `q` (quit); commit what you staged and leave the rest as unstaged edits.

**5.** `git blame app.py` prints, for each line: the commit hash, author, date and the line itself; `git log -p app.py` shows each commit that touched the file with its diff, newest first.

**6.** A commit hash is computed from the commit's content *including* its message, author, date and parent hash, so any change produces a completely different hash (and, because children store their parent's hash, it would change every later commit too).

</details>

### Git Branches, Merging and Resolving Conflicts

```text
git init -q -b main demo && cd demo
echo "base" > app.txt && git add . && git commit -m "Add app.txt"
git switch -c feature
echo "feature work" >> app.txt && git commit -am "Feature: add line"
git switch main
echo "hotfix" > readme.txt && git add . && git commit -m "Add readme"
git merge feature -m "Merge feature"             # three-way merge (no conflict: different files/lines)
git log --oneline --graph --all
```

To create and resolve a deliberate conflict: on two branches edit the **same line** of the same file differently, commit both, merge, open the file, remove the markers, `git add`, `git commit`.

### Undoing Mistakes and Rewriting History in Git

1. Edit a file, then discard the change. Edit again, stage it, then unstage it.
2. Make a commit with a typo in the message and fix it.
3. Make three commits; `revert` the middle one and read the log.
4. Make a commit, `reset --soft HEAD~1`, and recommit with a better message; then try `--mixed` and `--hard` on throwaway commits and observe the difference.
5. "Lose" a commit with `reset --hard`, then recover it using `reflog`.
6. Stash half-done work, switch branches, come back and pop.
7. Use `git bisect` with a script to find the commit that added a bad word to a file.

<details>
<summary>Solutions</summary>

**1.** `git restore f.txt`; later `git add f.txt` then `git restore --staged f.txt`.

**2.** `git commit --amend -m "Correct message"`.

**3.** `git revert <middle-hash>`; `git log --oneline` shows a new `Revert "..."` commit on top; the middle commit's changes are undone but the history is intact.

**4.** `--soft` leaves the changes staged (just run `git commit` again); `--mixed` leaves them unstaged (`git add` first); `--hard` discards them (they are gone from the working tree).

**5.** `git reset --hard HEAD~1`, then `git reflog` to find the old hash (`HEAD@{1}`), then `git reset --hard HEAD@{1}`.

**6.** `git stash`, `git switch other`, `git switch -`, `git stash pop`.

**7.** `git bisect start HEAD <good-hash>; git bisect run sh -c '! grep -q BADWORD f.txt'; git bisect reset`.

</details>

### GitHub and Collaborating with Others

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

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [The Command Line](terminal-basics.md) · [Git Basics](git-basics.md) · [Git Branches, Merging and Resolving Conflicts](git-branches-and-merging.md) · [Undoing Mistakes and Rewriting History in Git](git-undo-and-history.md) · [GitHub and Collaborating with Others](github-collaboration.md)
