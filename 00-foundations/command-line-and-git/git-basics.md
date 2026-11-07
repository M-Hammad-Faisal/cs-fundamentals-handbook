# Git Basics: Saving the History of Your Work

**Prerequisites:** [terminal basics](terminal-basics.md). **You will learn:** what version control is and why every developer uses it, Git's mental model (working folder, staging area, repository), the everyday commands (`init`, `add`, `commit`, `status`, `diff`, `log`), `.gitignore`, and how to write good commit messages.

## 1. In plain words

Have you ever saved files as `report_final.docx`, `report_final_v2.docx`, `report_REALLY_final.docx`? **Version control** does this properly. It records the **history of your project** as a series of named **snapshots (commits)** so you can:

- see **what changed, when and why**,
- **go back** to any earlier state,
- work on **experiments** (branches) without breaking the main code,
- **collaborate**: many people change the same project and combine their work.

**Git** is the version-control system used almost everywhere (created by Linus Torvalds in 2005 for Linux). **GitHub**, **GitLab** and **Bitbucket** are websites that host Git repositories so teams can share them. Git is the tool; GitHub is a service built around it.

## 2. The mental model: three areas

```text
 Working directory         Staging area (index)           Repository (history)
 (your files on disk)      (what goes into the next       (all the commits)
                            commit)
        |   git add file   |        git commit -m "..."      |
        |  ──────────────► |  ─────────────────────────────► |
        |                  |                                 |
        |  ◄─────────────────────────── git restore / checkout (get files back)
```

1. You **edit files** in the working directory (normal work).
2. You **`git add`** the changes you want to include: they go to the **staging area** (like putting items in a box).
3. You **`git commit`** to seal the box: a permanent **snapshot** with a message is stored in the repository.

Why a staging area? It lets you choose *which* changes belong together in a commit (a clean history) even if you edited five things at once.

### What a commit is

A **commit** is a snapshot of all tracked files plus metadata: author, date, message and a pointer to its **parent** commit(s). Commits form a chain (really a graph):

```text
   A <── B <── C <── D        each commit points to its parent
                      ▲
                     main     a branch is just a movable label pointing at a commit
                      ▲
                     HEAD     HEAD says "you are here" (usually the current branch)
```

Each commit has a unique **hash** (40 hex characters such as `85fd7d6...`, usually abbreviated to 7) computed from its contents, so history cannot be silently changed. You can see the idea with a few lines of Python: Git names a file's content by hashing `"blob <size>\0" + content`:

```python
import hashlib

def git_blob_hash(data: bytes) -> str:
    header = b"blob %d\x00" % len(data)             # Git hashes a small header plus the content
    return hashlib.sha1(header + data).hexdigest()

print(git_blob_hash(b"hello\n"))                     # ce013625030ba8dba906f756967f9e9ca394464a
# `echo hello | git hash-object --stdin` prints the same value.
print(git_blob_hash(b"hello\n") == git_blob_hash(b"hello\n"), git_blob_hash(b"hello!\n")[:7])    # True (different content, different hash)
```

Same content gives the same hash; any change gives a completely different hash. That is how Git detects changes, avoids storing duplicates and guarantees integrity.

## 3. One-time setup

```text
git config --global user.name  "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
git config --global core.editor "code --wait"       # optional: your preferred editor
git config --list                                    # check
```

The name and email are stamped on every commit you make. (Use the same email as your GitHub account.)

## 4. Your first repository

```text
$ mkdir myproject && cd myproject
$ git init                                  # turn this folder into a Git repository (creates a hidden .git folder)
Initialized empty Git repository in .../myproject/.git/

$ echo "hello" > a.txt
$ git status --short
?? a.txt                                    # ?? = untracked: Git sees the file but is not tracking it yet

$ git add a.txt                             # stage the file
$ git status --short
A  a.txt                                    # A = added (staged)

$ git commit -m "Add a.txt"                 # take the snapshot
[main (root-commit) 77a1985] Add a.txt
 1 file changed, 1 insertion(+)

$ git log --oneline
77a1985 Add a.txt
```

(Hashes in this lesson are examples; yours will differ.)

### The daily loop

```text
# 1. edit some files...
$ git status                  # what changed?
$ git diff                    # show the exact changes not yet staged
$ git add file1 file2         # stage specific files   (git add . stages everything in this folder)
$ git diff --staged           # show what is staged for the next commit
$ git commit -m "Clear message in the imperative mood"
$ git log --oneline           # review history
```

Example of `git diff` output after adding a line to `a.txt`:

```text
$ echo "second line" >> a.txt
$ git diff
diff --git a/a.txt b/a.txt
index ce01362..27019c3 100644
--- a/a.txt
+++ b/a.txt
@@ -1 +1,2 @@
 hello
+second line               <- a line starting with + was added (a minus means removed)
```

### Reading `git status`

| Short code | Meaning |
|------------|---------|
| `??` | untracked (new file Git does not know yet) |
| `A ` | added to the staging area |
| ` M` (space then M) | modified, **not** staged |
| `M ` | modified and staged |
| `MM` | staged, then modified again (the new edit is not staged) |
| `D ` / ` D` | deleted (staged / not staged) |
| `R ` | renamed |
| `UU` / `AA` | merge conflict |

`git status` (without `--short`) explains each state in words and **suggests the next command**. Use it constantly.

## 5. Looking at history

```text
$ git log                         # full history (q to quit)
$ git log --oneline               # one line per commit
$ git log --oneline --graph --all # draw the branch structure
$ git log -p -2                   # the last two commits with their diffs
$ git log --author="ayesha" --since="2 weeks ago"
$ git show <hash>                 # one commit's message and diff
$ git blame file.py               # who last changed each line (and in which commit)
```

```text
$ git log --oneline --graph --all
*   8839ab4 Merge feature
|\
| * 22f7f11 Add b.txt on feature
* | ef10d6a Change a on main
|/
* db30b8b Update a.txt
* 77a1985 Add a.txt
```

## 6. What to commit (and what not to): `.gitignore`

Do **not** commit: virtual environments, compiled files, caches, logs, **secrets** (passwords, API keys, `.env`), large data files, editor settings, OS junk. List patterns in a file named `.gitignore`:

```text
# .gitignore for a Python project
__pycache__/
*.pyc
.venv/
.env
*.log
dist/
build/
.idea/
.vscode/
.DS_Store
node_modules/
```

Patterns: `*.log` (any log file), `build/` (a folder), `!keep.log` (an exception), `/todo.txt` (only in the project root). Files that are **already tracked** are not hidden by adding them to `.gitignore`; remove them from tracking with `git rm --cached file`. **If you accidentally commit a secret, assume it is compromised**: rotate the key immediately; deleting the commit later does not erase it from places that already copied it.

## 7. Writing good commit messages

A commit message is a note to your future self and your teammates.

```text
Add password reset email (subject line: 50 characters or fewer, imperative mood)

Users who forget their password can now request a reset link.
The link expires after 30 minutes. Rate-limited to 3 requests/hour.

(blank line, then a body explaining WHY, wrapped around 72 characters)
Closes #142
```

Guidelines:

- **Imperative subject:** "Add...", "Fix...", "Remove..." (reads as "this commit will add...").
- **One logical change per commit** (small, focused, easy to review and to undo).
- Explain **why**, not just what (the diff shows what).
- Avoid "fix stuff", "wip", "asdf", "final final".
- Many teams use **Conventional Commits**: `feat: add login`, `fix: handle empty cart`, `docs: update README`, `refactor: split parser`, `test: cover edge cases`.

## 8. Useful everyday commands

| Command | Purpose |
|---------|---------|
| `git add -p` | stage changes **piece by piece** (interactive) |
| `git commit -am "msg"` | stage all *modified tracked* files and commit (does not include new files) |
| `git mv old new` / `git rm file` | rename / delete a tracked file |
| `git restore file` | discard unstaged changes in a file (**cannot be undone**) |
| `git restore --staged file` | unstage a file but keep the edits |
| `git diff HEAD~1` | compare the working tree with the previous commit |
| `git status -sb` | short status with the branch |

(More ways to undo things: [undoing mistakes and rewriting history](git-undo-and-history.md).)

## 9. Two real-world examples

**Example 1: Rescuing a project.** A student changes a working program in many places; tomorrow it is broken and they cannot remember what they altered. With Git, `git diff` shows every change line by line and `git restore .` returns to the last good commit. Without version control they would be guessing for hours.

**Example 2: A team finds when a bug started.** A feature stops working. The team uses `git log -p -- path/to/file` and `git blame` to see who changed the suspicious lines and why (the commit message explains the intent), then reverts that single commit. Clear commit history turns a mystery into a five-minute investigation.

## 10. Common mistakes

- Never committing (then losing days of work): commit early and often (small, working steps).
- Committing everything with `git add .` without looking at `git status` or `git diff --staged` (secrets, huge files, debug code get in).
- Vague messages ("update", "changes").
- One giant commit mixing unrelated changes.
- Committing generated files (`__pycache__`, `.venv`, `node_modules`).
- Committing secrets.
- Running `git init` inside a folder that is already inside another repository (nested repos).
- Editing the same file in two places without committing, then being afraid of losing one version.

## 11. Practice

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

## 12. Check yourself

1. What problem does version control solve?
2. What are the three areas in Git's model?
3. What does `git add` do? `git commit`?
4. What is a commit hash, and why does it change when the content changes?
5. What belongs in `.gitignore`?
6. What makes a good commit message?

<details>
<summary>Answers</summary>

1. It records the history of changes so you can inspect, undo, branch and collaborate.
2. The working directory, the staging area (index) and the repository (committed history).
3. `git add` puts changes into the staging area; `git commit` records the staged snapshot permanently with a message.
4. A hash is a unique ID computed from the commit's contents; since it is derived from the content, any change yields a different hash, making history tamper-evident.
5. Generated files, dependencies and environments, caches, logs, editor/OS files and secrets.
6. A short imperative subject, one logical change, and a body that explains why.

</details>

[Back to command line and Git](README.md) · Previous: [terminal basics](terminal-basics.md) · Next: [branches and merging](git-branches-and-merging.md)
