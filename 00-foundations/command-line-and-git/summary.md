# Command Line and Git: One-Page Summary

## Key facts

- **Navigate and inspect:** `pwd`, `ls -la`, `cd`, `mkdir -p`, `cp -r`, `mv`, `cat`, `less`, `head`, `tail -f`, `grep -rn "text" .`, `find . -name "*.py"`.
- **Pipes and redirection:** `a | b` feeds a's output to b; `>` overwrites a file, `>>` appends, `2>&1` merges errors into output; exit status `0` means success (`$?`).
- **Environment:** the shell searches `PATH` left to right for commands; `export NAME=value` passes a variable to child programs.
- **Permissions:** `r=4 w=2 x=1` per owner / group / others; `chmod +x script.sh`, `755` for programs, `644` for plain files.
- **Git model:** working directory, `git add` to the staging area, `git commit` to the repository. Check with `git status`, `git diff`, `git diff --staged`, `git log --oneline --graph`.
- **Branches:** a branch is a movable pointer to a commit (`git switch -c name`). **Merge** keeps history as it happened; **rebase** replays your commits on a new base (only for commits you have not shared). Conflicts are marked `<<<<<<<`, `=======`, `>>>>>>>`.
- **Undo ladder:** `restore` (discard edits), `restore --staged` (unstage), `commit --amend` (fix the last unpushed commit), `revert` (safe on shared history), `reset` (move the branch; `--hard` discards work), `reflog` (find "lost" commits), `stash` (park work), `bisect` (find the breaking commit).
- **Collaboration:** `clone`, `fetch` (download only), `pull` (fetch then merge), `push`; the pull-request flow is branch, push, open PR, review, CI passes, merge.

## Pitfalls

- `rm -rf` with a wrong path or an empty variable: there is no recycle bin.
- Committing a secret (`.env`, key): deleting the file later does not remove it from history; **rotate the secret**.
- Rebasing or force-pushing commits other people already have.
- `git add .` without reading `git status`, or one huge commit mixing unrelated changes; vague messages such as "fix".
- Committing in detached `HEAD` state: those commits are easy to lose unless you create a branch.

## Self-check

- **What are the terminal, the shell and a command?** The terminal is the window, the shell is the program that interprets what you type, a command is a program you run by name.
- **What do `pwd`, `ls`, `cd ..` do?** Show the current directory; list files; move up one folder.
- **How does a pipe work?** The output of the left command is fed as input to the right command.
- **What is the `PATH`?** The list of folders the shell searches to find a command by name.
- **What is dangerous about `rm -r`?** It permanently deletes a folder and everything inside it, with no recycle bin.
- **What does `chmod +x` do?** It makes a file executable so it can be run as a program.
- **What problem does version control solve?** It records the history of changes so you can inspect, undo, branch and collaborate.
- **What are the three areas in Git's model?** The working directory, the staging area (index) and the repository (committed history).
- **What does `git add` do? `git commit`?** `git add` puts changes into the staging area; `git commit` records the staged snapshot permanently with a message.
- **What is a commit hash, and why does it change when the content changes?** A hash is a unique ID computed from the commit's contents; since it is derived from the content, any change yields a different hash, making history tamper-evident.
- **What belongs in `.gitignore`?** Generated files, dependencies and environments, caches, logs, editor/OS files and secrets.
- **What makes a good commit message?** A short imperative subject, one logical change, and a body that explains why.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [The Command Line](terminal-basics.md) · [Git Basics](git-basics.md) · [Git Branches, Merging and Resolving Conflicts](git-branches-and-merging.md) · [Undoing Mistakes and Rewriting History in Git](git-undo-and-history.md) · [GitHub and Collaborating with Others](github-collaboration.md)
