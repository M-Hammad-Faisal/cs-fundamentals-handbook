# Undoing Mistakes and Rewriting History in Git

**Prerequisites:** [Git basics](git-basics.md), [branches and merging](git-branches-and-merging.md). **You will learn:** how to undo almost anything: discard edits, unstage, fix the last commit, revert a bad commit safely, reset history, rescue "lost" commits with `reflog`, park work with `stash`, mark releases with tags, and find the commit that introduced a bug with `bisect`.

## 1. In plain words

Git's superpower is that **committed work is very hard to lose**. Mistakes are normal; this lesson is your "undo" menu. The key question is always: **where is the change right now?** (working directory, staging area, a local commit, or a commit you have already pushed?) The answer picks the safe tool.

| Where is the mistake? | Safe tool |
|-----------------------|-----------|
| Edited a file, not staged | `git restore file` |
| Staged by mistake | `git restore --staged file` |
| Last commit message/content wrong, **not pushed** | `git commit --amend` |
| A bad commit **already shared** | `git revert <hash>` (adds an opposite commit) |
| Local commits you want to discard, **not pushed** | `git reset` |
| "I lost a commit!" | `git reflog` then `git reset` / `git switch -c` |
| Unfinished work, need to switch tasks | `git stash` |
| Find which commit broke something | `git bisect` |

Examples below use a tiny repository with three commits (`Add line 1`, `Add line 2`, `Add line 3`). Hashes are examples.

## 2. Discard working-directory changes: `git restore`

```text
$ echo "oops" >> f.txt
$ git status --short
 M f.txt                       <- modified, not staged
$ git restore f.txt            <- throw the edit away (CANNOT be undone: it was never committed)
$ cat f.txt
line 1
line 2
line 3
```

`git restore .` discards every unstaged change. Use it only when you are sure.

## 3. Unstage: `git restore --staged`

```text
$ echo "x" > n.txt
$ git add n.txt
$ git restore --staged n.txt   <- remove from the staging area, keep the file and its content
$ git status --short
?? n.txt
```

## 4. Fix the last commit: `git commit --amend`

```text
$ git commit -m "Add f with typo mesage"
$ git commit --amend -m "Add f with fixed message"        # rewrite the message
$ git log --oneline
85fd7d6 Add f with fixed message                          <- NEW hash: amend creates a replacement commit

$ echo b >> f.txt
$ git add f.txt
$ git commit --amend --no-edit                            # add the forgotten change to the previous commit
```

**Only amend commits you have not pushed**, because it replaces the commit (new hash).

## 5. Undo a shared commit safely: `git revert`

`revert` creates a **new commit that applies the opposite changes**. History is preserved: the right tool for anything already pushed.

```text
$ git log --oneline
cf6a45e Add line 3
ea6855e Add line 2
9dec7f4 Add line 1

$ git revert --no-edit cf6a45e
$ git log --oneline
7a7743f Revert "Add line 3"                              <- a new commit undoing the effect
cf6a45e Add line 3
ea6855e Add line 2
9dec7f4 Add line 1
```

## 6. Move or discard commits: `git reset`

`reset` **moves the current branch pointer** to another commit. It has three modes depending on what happens to your files:

| Command | Branch pointer | Staging area | Working files |
|---------|----------------|--------------|---------------|
| `git reset --soft HEAD~1` | moves back one commit | **kept** (changes stay staged) | kept |
| `git reset --mixed HEAD~1` (default) | moves back | cleared | **kept** (changes stay as edits) |
| `git reset --hard HEAD~1` | moves back | cleared | **discarded** (dangerous) |

```text
$ git reset --hard HEAD~1       # delete the last commit and its changes
$ git log --oneline
2bc3b51 Typo mesage
cf6a45e Add line 3
```

Use `--soft` to "uncommit and recommit differently", `--mixed` to unstage everything, `--hard` only when you truly want to throw changes away. **Do not reset commits you already pushed** (use `revert`), unless you coordinate and force-push deliberately.

## 7. Time machine: `git reflog`

Git records every move of `HEAD` in the **reflog** (kept for weeks). Even after a hard reset your "lost" commits are usually recoverable.

```text
$ git reflog
2bc3b51 HEAD@{0}: reset: moving to HEAD~1
7a7743f HEAD@{1}: revert: Revert "Add line 3"
2bc3b51 HEAD@{2}: commit: Typo mesage
cf6a45e HEAD@{3}: commit: Add line 3
ea6855e HEAD@{4}: commit: Add line 2

$ git reset --hard 7a7743f      # jump back to the state before the mistake
# or keep it safe on a new branch:
$ git switch -c rescue 7a7743f
```

If something vanished, run `git reflog` **before** doing anything else.

## 8. Park unfinished work: `git stash`

You are halfway through a change and must switch branches (an urgent bug). Do not commit half-finished work; **stash** it.

```text
$ echo "wip" >> f.txt
$ git stash                     # save the uncommitted changes and clean the working tree
$ git status --short            # (empty)
$ git switch hotfix             # ...fix the urgent thing, come back...
$ git switch main
$ git stash pop                 # bring the changes back (and remove the stash entry)
$ tail -1 f.txt
wip
```

Other commands: `git stash list`, `git stash push -m "describe it"`, `git stash apply` (keep the entry), `git stash drop`, `git stash -u` (include untracked files).

## 9. Tags: name important commits

A **tag** is a permanent name for a commit: usually a release (`v1.0.0`).

```text
$ git tag -a v1.0 -m "First release"        # annotated tag (recommended: has author, date, message)
$ git tag                                    # list
v1.0
$ git show v1.0
$ git push origin v1.0                       # tags are not pushed automatically
```

Use **semantic versioning** (`MAJOR.MINOR.PATCH`): breaking changes bump MAJOR, compatible features bump MINOR, fixes bump PATCH.

## 10. Find the commit that broke it: `git bisect`

If something worked last month and is broken now, with 200 commits in between, Git can **binary-search** the history ([binary search](../../03-algorithms/searching/README.md): about 8 steps for 200 commits).

```text
$ git bisect start HEAD <known-good-commit>      # HEAD is bad, the other is good
Bisecting: 3 revisions left to test after this (roughly 2 steps)
[01eadbb...] good3
$ git bisect run sh -c '! grep -q BAD f.txt'     # let a script decide: exit 0 = good, non-zero = bad
45a61f4... is the first bad commit
    introduce bug
$ git bisect reset                               # go back to where you started
```

Without a script you test manually and type `git bisect good` or `git bisect bad` at each step.

## 11. Other useful commands

| Command | Use |
|---------|-----|
| `git checkout <hash>` / `git switch --detach <hash>` | look at an old commit (detached HEAD: do not commit here; `git switch main` to return) |
| `git cherry-pick <hash>` | copy one commit onto the current branch |
| `git restore --source=<hash> file` | bring a file back from an old commit |
| `git clean -n` / `git clean -fd` | preview / delete untracked files |
| `git diff A B` | compare any two commits |
| `git shortlog -sn` | contributors ranked by commits |
| `git commit --fixup <hash>` + `git rebase -i --autosquash` | tidy history before a pull request |

## 12. The safety rules

1. **Commit often**: committed work can be recovered, uncommitted work cannot.
2. **Before a risky operation**, create a backup branch: `git branch backup-before-reset`.
3. **Shared history is read-only:** use `revert`, not `reset`/`amend`/`rebase`, for anything pushed.
4. **`git status` and `git log --oneline --graph --all`** before and after each operation.
5. **Force-push only with `--force-with-lease`**, only on your own branches, and tell your team if it is shared.
6. **When confused, stop.** Run `git status`, `git reflog`, ask for help; do not try random commands.

## 13. Two real-world examples

**Example 1: "I committed a password."** A student commits `config.py` containing an API key and pushes it. They must (1) **rotate the key immediately** (the secret is now public), (2) remove it from the file and use environment variables, (3) optionally rewrite history with tools like `git filter-repo` (coordinating with collaborators). The lesson: `revert` alone does not erase history, so treat any leaked secret as compromised.

**Example 2: "I ran reset --hard and lost two hours of commits."** `git reflog` shows `HEAD@{1}: commit: Add checkout page` just before the reset; `git reset --hard HEAD@{1}` restores everything. Reflog is why experienced Git users are rarely afraid of breaking things.

## 14. Common mistakes

- Using `git reset --hard` or `git restore .` without checking `git status` first.
- Amending or resetting commits that others already pulled.
- Panicking and re-cloning the repository instead of using `reflog`.
- Forgetting that `git stash` does not stash untracked files by default (`-u`).
- Rebasing/force-pushing a shared branch.
- Leaving a repository in a detached HEAD state and committing there (create a branch: `git switch -c name`).
- Thinking `git revert` deletes history (it adds a new commit).

## 15. Practice

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

## 16. Check yourself

1. How do you discard unstaged edits? Unstage a file?
2. When use `revert` and when `reset`?
3. What does `git reset --hard` do to your working files?
4. How can you recover a commit after a hard reset?
5. What is `git stash` for?
6. How does `git bisect` find a bad commit quickly?

<details>
<summary>Answers</summary>

1. `git restore file`; `git restore --staged file`.
2. `revert` for commits already shared (it adds an opposite commit); `reset` for local, unpushed commits.
3. It discards uncommitted changes, resetting files to the target commit.
4. Find the old hash in `git reflog` and `git reset --hard` (or `git switch -c`) to it.
5. To temporarily save uncommitted changes so you can switch tasks and restore them later.
6. It performs a binary search over the commits between a good and a bad one, testing the middle each time.

</details>

[Back to command line and Git](README.md) · Previous: [branches and merging](git-branches-and-merging.md) · Next: [GitHub and collaboration](github-collaboration.md)
