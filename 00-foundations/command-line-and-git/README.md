# Command Line and Git

Every developer lives in the terminal and in Git. These five lessons take you from "what is a terminal?" to collaborating on GitHub, with every command explained and the outputs verified on a real repository.

| # | Lesson | You will learn |
|---|--------|----------------|
| 1 | [Terminal basics](terminal-basics.md) | Navigation, files, searching, pipes and redirection, environment variables, permissions, scripts |
| 2 | [Git basics](git-basics.md) | Version control, the three areas, `init/add/commit/status/diff/log`, `.gitignore`, commit messages |
| 3 | [Branches and merging](git-branches-and-merging.md) | What a branch is, merge vs fast-forward, resolving conflicts, rebase, branching strategies |
| 4 | [Undoing mistakes and history](git-undo-and-history.md) | `restore`, `amend`, `revert`, `reset`, `reflog`, `stash`, tags, `bisect` |
| 5 | [GitHub and collaboration](github-collaboration.md) | Remotes, SSH keys, pull requests, code review, forks, issues, CI |

**Study tip:** do the lessons with a terminal open and a scratch folder. Make mistakes there on purpose (create conflicts, reset, recover with reflog) so nothing is scary on a real project.

[Back to foundations](../README.md)

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

## Quick reference

| Question | Answer |
|----------|--------|
| What are the terminal, the shell and a command? | The terminal is the window, the shell is the program that interprets what you type, a command is a program you run by name. |
| What do `pwd`, `ls`, `cd ..` do? | Show the current directory; list files; move up one folder. |
| How does a pipe work? | The output of the left command is fed as input to the right command. |
| What is the `PATH`? | The list of folders the shell searches to find a command by name. |
| What is dangerous about `rm -r`? | It permanently deletes a folder and everything inside it, with no recycle bin. |

Back to the [part overview](../README.md).
