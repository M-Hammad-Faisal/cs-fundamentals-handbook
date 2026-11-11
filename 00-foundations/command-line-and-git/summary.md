# Command Line and Git: One-Page Summary

## Questions worth remembering

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

Practice problems with solutions are in the exercises page and in the **Practice** section of each lesson.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [The Command Line](terminal-basics.md) · [Git Basics](git-basics.md) · [Git Branches, Merging and Resolving Conflicts](git-branches-and-merging.md) · [Undoing Mistakes and Rewriting History in Git](git-undo-and-history.md) · [GitHub and Collaborating with Others](github-collaboration.md)
