# Git Branches, Merging and Resolving Conflicts

**Prerequisites:** [Git basics](git-basics.md). **You will learn:** what a branch really is, how to create and switch branches, merge them (fast-forward and three-way), resolve merge conflicts step by step, and when to use rebase.

## 1. In plain words

A **branch** is a separate line of development. You can try a new feature on its own branch, break things freely, and only combine it with the main code (`main`) when it works. Meanwhile other people (or you) can keep working on `main` or other branches. Branches in Git are **cheap and instant**, so use them for everything.

Analogy: a book manuscript. `main` is the published edition; a branch is a photocopy where you rewrite chapter 3. If you like it, you **merge** the changes back; if not, you throw the photocopy away.

## 2. What a branch is

A branch is just a **named pointer to a commit**. When you commit, the current branch's pointer moves forward. `HEAD` points to the branch you are on.

```text
Start:                A ◄── B ◄── C          main (HEAD)

git switch -c feature:   A ◄── B ◄── C       main
                                      ▲
                                    feature (HEAD)       two labels on the same commit

Commit on feature:    A ◄── B ◄── C ◄── D    feature (HEAD)
                                ▲
                              main

Commit on main too:               ┌── D      feature
                      A ◄── B ◄── C
                                  └── E      main (the history has DIVERGED)
```

## 3. Everyday branch commands

```text
$ git branch                       # list branches (* marks the current one)
  feature
* main
$ git switch -c feature/login      # create a new branch AND switch to it   (older: git checkout -b)
$ git switch main                  # switch to an existing branch
$ git branch -d feature/login      # delete a merged branch (-D forces deletion of an unmerged one)
$ git branch -m old-name new-name  # rename
$ git branch -vv                   # show last commits and upstream tracking
```

**Naming:** `feature/login-form`, `fix/cart-crash`, `docs/readme`, `chore/update-deps`: short, lowercase, hyphenated, describes the purpose.

**Before switching**, commit or stash your work (`git stash`, see [undo and history](git-undo-and-history.md)); uncommitted changes can follow you or block the switch.

## 4. Merging

`git merge other-branch` brings the other branch's commits into the **current** branch.

### Fast-forward merge (no divergence)

If `main` has not moved since you branched, Git just slides the `main` pointer forward:

```text
Before:  A ◄── B ◄── C           main
                        ◄── D ◄── E   feature        (main has no new commits)

git switch main && git merge feature      ->    A ◄── B ◄── C ◄── D ◄── E     main = feature (a straight line)
```

### Three-way merge (history diverged)

If both branches have new commits, Git creates a **merge commit** with two parents:

```text
$ git switch main
$ git merge feature -m "Merge feature"
 b.txt | 1 +
 1 file changed, 1 insertion(+)
 create mode 100644 b.txt

$ git log --oneline --graph --all
*   8839ab4 Merge feature            <- the merge commit (two parents)
|\
| * 22f7f11 Add b.txt on feature
* | ef10d6a Change a on main
|/
* db30b8b Update a.txt
```

Use `git merge --no-ff feature` to force a merge commit even when a fast-forward is possible (keeps the branch visible in history), or `--squash` to combine the whole branch into one staged change.

## 5. Merge conflicts

A **conflict** happens when two branches changed **the same lines** (or one deleted what the other edited). Git cannot decide, so it stops and asks you.

```text
$ git merge c1
Auto-merging conflict.txt
CONFLICT (add/add): Merge conflict in conflict.txt
Automatic merge failed; fix conflicts and then commit the result.

$ git status --short
AA conflict.txt                       <- both added: needs your attention

$ cat conflict.txt
<<<<<<< HEAD
from main                             <- your current branch's version (above =======)
=======
from c1                               <- the incoming branch's version (below =======)
>>>>>>> c1
```

### How to resolve a conflict (step by step)

1. **Don't panic.** Nothing is lost; you can abort with `git merge --abort`.
2. Open each conflicted file (`git status` lists them). Find the markers `<<<<<<<`, `=======`, `>>>>>>>`.
3. **Decide the final content**: keep one side, the other, or combine both (often by talking to your teammate!).
4. **Delete the marker lines** and save. The file must look like normal code again.
5. **Run the tests** (a clean merge can still be logically broken).
6. `git add conflict.txt` (marks it resolved), then `git commit` (Git offers a default merge message).

```text
# the file after you decided to keep both lines:
from main
from c1

$ git add conflict.txt
$ git commit -m "Merge c1: keep both lines"
```

Tools: editors like VS Code and PyCharm show "Accept current / incoming / both"; `git mergetool` opens a visual tool. **Reduce conflicts** by pulling often, making small commits, keeping branches short-lived and avoiding mass reformatting.

## 6. Rebase: a straighter history

`git rebase main` (while on your feature branch) **replays your commits on top of the latest `main`**, as if you had started from there. The result is a **linear history** without merge commits.

```text
Before:                D ◄── E        feature
                     /
        A ◄── B ◄── C ◄── F           main

git switch feature && git rebase main

After:   A ◄── B ◄── C ◄── F ◄── D' ◄── E'     (D' and E' are NEW commits with the same changes)
```

| | Merge | Rebase |
|--|-------|--------|
| History | preserves exactly what happened (a graph) | rewrites into a straight line |
| Safety | non-destructive | **rewrites commits** (new hashes) |
| Use when | combining shared branches | tidying **your own local** branch before sharing |

**Golden rule: never rebase commits that other people already have** (that you pushed to a shared branch). Rewritten history forces everyone else to fix their copies.

Interactive rebase (`git rebase -i HEAD~4`) lets you **squash** small commits into one, reorder, reword or drop commits to clean up before a pull request.

## 7. Branching strategies teams use

| Strategy | How it works | Good for |
|----------|--------------|----------|
| **GitHub Flow** | `main` is always deployable; every change is a short-lived branch merged through a pull request | most teams, continuous delivery |
| **Trunk-based development** | tiny changes merged to `main` many times a day, feature flags hide unfinished work | high-performing teams with strong CI |
| **Git Flow** | long-lived `develop`, `release/*`, `hotfix/*` branches | scheduled releases, older practice |

Whichever you use: keep `main` healthy, branch from it, merge back through review, delete merged branches.

## 8. Practice scenario you can run

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

## 9. Two real-world examples

**Example 1: Feature branches in a team.** Ayesha creates `feature/search-bar`, commits for two days, and opens a pull request. Bilal works on `fix/login-bug` in parallel. `main` stays stable: both changes are reviewed, tested by CI, and merged independently. If Ayesha's feature is cancelled, deleting the branch costs nothing.

**Example 2: A conflict in a shared file.** Two people edit `settings.py`: one adds `TIMEOUT = 10`, the other `TIMEOUT = 30` on the same line. The second to merge gets a conflict. They talk, agree on 30, edit the file, remove the markers, run the tests and commit the resolution. The lesson is communication: conflicts are social as much as technical.

## 10. Common mistakes

- Committing directly to `main` (use branches).
- Long-lived branches that drift far from `main` (huge painful conflicts).
- Resolving conflicts by blindly accepting "theirs" or "mine" without understanding.
- Leaving conflict markers in the file (`<<<<<<<` in committed code).
- Rebasing shared history.
- Forgetting which branch you are on (check `git status` / `git branch`).
- Merging without running tests afterwards.

## 11. Practice

1. Create a branch, make two commits on it, merge it into `main` (observe a fast-forward). Repeat with a commit on `main` first (observe a merge commit).
2. Create a conflict in one file between two branches and resolve it by combining both versions.
3. Abort a merge halfway with `git merge --abort`.
4. Rebase a feature branch onto an updated `main` and compare the log with a merge.
5. Use `git rebase -i` to squash three small commits into one.
6. Explain the difference between `git merge` and `git rebase` and when to avoid rebase.

<details>
<summary>Solutions</summary>

**1.** On `feature` commit twice; `git switch main && git merge feature` prints `Fast-forward`. For a merge commit, add a commit to `main` before merging: Git then reports `Merge made by the 'ort' strategy` and creates a merge commit.

**2.** `git switch -c a`, edit line 1 of `f.txt` to "A", commit; `git switch main`, `git switch -c b`, edit the same line to "B", commit; `git merge a` conflicts; open `f.txt`, keep "A and B", delete markers, `git add f.txt`, `git commit`.

**3.** After `git merge x` reports a conflict, run `git merge --abort`: the repository returns to its state before the merge.

**4.** `git switch feature && git rebase main` yields a straight line with new commit hashes; `git log --oneline --graph` shows no merge commit, whereas merging would add one.

**5.** `git rebase -i HEAD~3`, change `pick` to `squash` (or `s`) on the 2nd and 3rd lines, save, edit the combined message.

**6.** Merge combines branches by adding a merge commit and preserves history; rebase rewrites your commits onto a new base for a linear history. Avoid rebasing commits that have already been pushed and shared, because it rewrites history others depend on.

</details>

## 12. Check yourself

1. What is a branch in Git?
2. When can Git do a fast-forward merge?
3. What do the markers `<<<<<<<`, `=======`, `>>>>>>>` mean?
4. What are the steps to resolve a conflict?
5. What is the golden rule of rebase?
6. Why should branches be short-lived?

<details>
<summary>Answers</summary>

1. A movable pointer to a commit; committing advances the current branch.
2. When the target branch has no new commits since the other branch diverged, so its pointer can simply move forward.
3. The start of your version, the divider, and the end of the incoming version of the conflicting lines.
4. Open the files, decide the final content, remove the markers, run tests, `git add` the files, then `git commit`.
5. Never rebase commits that others already have.
6. The longer a branch lives, the more it diverges from `main`, making conflicts larger and merging riskier.

</details>

[Back to command line and Git](README.md) · Previous: [Git basics](git-basics.md) · Next: [undoing mistakes and history](git-undo-and-history.md)
