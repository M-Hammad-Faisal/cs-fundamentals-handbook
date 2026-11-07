# The Command Line (Terminal) Basics

**Prerequisites:** none. **You will learn:** what the terminal is, the commands you use every day (navigate, create, copy, search, view files), pipes and redirection, environment variables, permissions, and how to read help.

## 1. In plain words

The **graphical interface** lets you click icons. The **command line** (also called the terminal, console or shell) lets you control the computer by **typing commands**. It looks old-fashioned but it is faster for many tasks, can be **automated** (scripts), works on **remote servers** (where there is no mouse), and every developer tool (Git, Python, Docker, pip) is used from it.

- The **terminal** is the window.
- The **shell** is the program inside it that reads your commands (bash, zsh, PowerShell).
- A **command** is a program you run by name, usually followed by **options** (flags) and **arguments**: `ls -l Documents` = command `ls`, option `-l`, argument `Documents`.

This lesson uses Unix-style commands (macOS, Linux, WSL on Windows, Git Bash). On Windows PowerShell the same ideas have slightly different names (shown in the table below).

```text
$ ls -l Documents          <- "$" is the prompt (do not type it)
  |  |   |
  |  |   +-- argument: what to act on
  |  +------ option (flag): changes how it works
  +--------- command: the program
```

## 2. Where am I? Navigating the file system

The file system is a **tree of folders (directories)**. The **root** is `/` (on Windows `C:\`). Your **home** folder is `~`.

```text
/
├── home/ (or /Users on macOS)
│   └── ayesha/            <- your home (~)
│       ├── Documents/
│       └── projects/
│           └── handbook/
├── etc/
└── usr/
```

| Command | What it does | Example |
|---------|--------------|---------|
| `pwd` | **p**rint **w**orking **d**irectory (where am I?) | `pwd` -> `/home/ayesha` |
| `ls` | **l**i**s**t files | `ls`, `ls -l` (details), `ls -a` (include hidden), `ls -lh` (readable sizes) |
| `cd folder` | **c**hange **d**irectory | `cd projects`, `cd ..` (up one level), `cd ~` (home), `cd -` (previous folder), `cd /` (root) |
| `mkdir name` | **m**a**k**e **dir**ectory | `mkdir notes`, `mkdir -p a/b/c` (create nested folders) |

**Paths:** an **absolute path** starts at the root (`/home/ayesha/projects`); a **relative path** starts from where you are (`projects/handbook`, `../other`). `.` means "here", `..` means "the parent folder". Tip: press **Tab** to auto-complete names and the **Up arrow** to recall earlier commands.

## 3. Working with files and folders

| Command | What it does | Example |
|---------|--------------|---------|
| `touch file` | create an empty file (or update its timestamp) | `touch notes.txt` |
| `cp src dst` | **c**o**p**y | `cp a.txt b.txt`, `cp -r folder copy` (folders need `-r`) |
| `mv src dst` | **m**o**v**e or rename | `mv a.txt notes/`, `mv old.txt new.txt` |
| `rm file` | **r**e**m**ove (delete). **No recycle bin!** | `rm a.txt`, `rm -r folder` (folders; be careful) |
| `cat file` | print a whole file | `cat notes.txt` |
| `less file` | page through a long file (`q` quits) | `less big.log` |
| `head -n 5 file` / `tail -n 5 file` | first / last lines (`tail -f` follows a growing log) | `tail -n 20 app.log` |
| `wc -l file` | count lines (`-w` words, `-c` bytes) | `wc -l data.csv` |
| `echo text` | print text | `echo hello` |

**Be careful with `rm`:** deleting is permanent, and `rm -r` on the wrong folder can destroy your work. Check with `ls` first and prefer moving things to a trash folder while learning.

You can try these safely in Python without risking your files; this snippet mimics a terminal session inside a throwaway folder:

```python
import os, tempfile, shutil, subprocess, sys
from pathlib import Path

work = Path(tempfile.mkdtemp())
os.chdir(work)                                        # cd into a scratch folder

Path("notes").mkdir()                                  # mkdir notes
Path("notes/todo.txt").write_text("buy milk\nwrite code\n")        # echo ... > notes/todo.txt
shutil.copy("notes/todo.txt", "notes/backup.txt")      # cp notes/todo.txt notes/backup.txt
os.rename("notes/backup.txt", "notes/todo.bak")        # mv notes/backup.txt notes/todo.bak
print(sorted(os.listdir("notes")))                     # ls notes -> ['todo.bak', 'todo.txt']
print(Path("notes/todo.txt").read_text().splitlines()) # cat notes/todo.txt -> ['buy milk', 'write code']
print(len(Path("notes/todo.txt").read_text().splitlines()))        # wc -l -> 2
os.remove("notes/todo.bak")                            # rm notes/todo.bak
os.chdir("/")
shutil.rmtree(work)                                    # rm -r on the scratch folder
```

## 4. Finding and searching

| Command | What it does | Example |
|---------|--------------|---------|
| `grep pattern file` | print lines containing the pattern | `grep ERROR app.log`, `grep -i error app.log` (ignore case), `grep -n ...` (line numbers), `grep -r "TODO" src/` (search a folder), `grep -v ...` (invert) |
| `find path -name pattern` | find files by name | `find . -name "*.py"` |
| `which cmd` | where is a program? | `which python` |
| `history` | your previous commands | `history \| tail` |

## 5. Pipes and redirection: combining small tools

Each command does one small job; **pipes** (`|`) send the output of one command into the next, and **redirection** sends output to a file.

| Symbol | Meaning | Example |
|--------|---------|---------|
| `\|` | pipe: output of left becomes input of right | `cat app.log \| grep ERROR \| wc -l` (count error lines) |
| `>` | write output to a file (**overwrites**) | `ls > files.txt` |
| `>>` | append output to a file | `echo done >> log.txt` |
| `<` | read input from a file | `sort < names.txt` |
| `2>` | redirect error messages | `command 2> errors.txt` |
| `&&` | run the next command only if the first **succeeded** | `mkdir out && cd out` |
| `;` | run commands one after another | `cd a; ls` |

```text
$ cat access.log | grep "404" | cut -d' ' -f1 | sort | uniq -c | sort -rn | head -3
     42 203.0.113.9
     17 198.51.100.4
      5 192.0.2.77
```

(Read it left to right: take the log, keep the 404 lines, take the first column (the IP), sort, count the duplicates, sort by count, show the top three. Five tiny tools, one useful answer.) The same idea in Python:

```python
from collections import Counter

log_lines = ["1.1.1.1 GET /a 404", "2.2.2.2 GET /b 200", "1.1.1.1 GET /c 404", "3.3.3.3 GET /d 404", "1.1.1.1 GET /e 404"]
errors = [line.split()[0] for line in log_lines if line.endswith("404")]      # grep 404 | cut -d' ' -f1
print(Counter(errors).most_common(2))                                          # sort | uniq -c | sort -rn | head -2
# [('1.1.1.1', 3), ('3.3.3.3', 1)]
```

Useful filters: `sort`, `uniq -c`, `cut`, `head`, `tail`, `wc`, `tr`, `sed` (search/replace), `awk` (columns), `xargs` (turn lines into arguments), `tee` (write and pass on).

## 6. Environment variables and the PATH

**Environment variables** are named settings available to every program (`HOME`, `USER`, `PATH`, `LANG`, API keys).

```text
$ echo $HOME                      /home/ayesha
$ export API_URL=https://x.test   set a variable for this shell session and its child programs
$ env | grep API                  list variables matching API
```

`PATH` is a list of folders the shell searches when you type a command name; `which python` shows which one it found. This is why installing a tool but "command not found" often means its folder is not on your `PATH`. Programs read variables for configuration (see [configuration](../../08-modern-python/packaging-tooling/README.md)):

```python
import os
os.environ["DEMO_MODE"] = "on"
print(os.environ.get("DEMO_MODE"), os.environ.get("MISSING", "default"), "PATH" in os.environ)      # on default True
```

## 7. Permissions

On Unix every file has an owner and **read (r), write (w), execute (x)** permissions for the **owner, group and others**. `ls -l` shows them:

```text
-rwxr-xr--  1 ayesha staff  120 Nov 7 10:00 script.sh
 |||||||||
 |||||| +-- others: r--  (4)
 |||+-+---- group:  r-x  (5)
 +-+------- owner:  rwx  (7)
```

| Command | Meaning |
|---------|---------|
| `chmod +x script.sh` | make a script executable |
| `chmod 644 file` | owner read+write, others read (numbers = sum of r=4, w=2, x=1; see [bits](../computer-basics/binary-and-data-representation.md)) |
| `./script.sh` | run a script in the current folder |
| `sudo command` | run as administrator (use sparingly) |

## 8. Getting help

```text
$ ls --help          short usage summary (macOS: man ls)
$ man grep           the manual page (q to quit; / to search)
$ python --version   check a tool's version
$ tldr tar           (optional tool) friendly examples
```

When stuck: read the error message, search the exact text, check the command's `--help`, and look at examples. Nobody memorizes every flag.

## 9. Writing a small shell script

A **script** is a file of commands. It automates repetitive work.

```text
#!/usr/bin/env bash
# backup.sh: copy the notes folder into a dated backup folder
set -e                                   # stop at the first error
today=$(date +%Y-%m-%d)                  # store a command's output in a variable
mkdir -p "backups/$today"
cp -r notes/* "backups/$today/"
echo "Backed up $(ls notes | wc -l) files to backups/$today"
```

Run with `chmod +x backup.sh && ./backup.sh`. For anything more complicated than a few lines, Python scripts are usually clearer (see [Python fundamentals](../python-fundamentals/README.md)).

## 10. Windows quick map

| Task | Bash (macOS/Linux/WSL) | PowerShell |
|------|------------------------|------------|
| list files | `ls` | `ls` or `dir` |
| change folder | `cd` | `cd` |
| current folder | `pwd` | `pwd` |
| copy | `cp` | `cp` |
| delete | `rm` | `rm` |
| show a file | `cat` | `cat` |
| search text | `grep` | `Select-String` |
| environment var | `echo $HOME` | `echo $env:HOME` |

Tip for Windows students: install **WSL** (Windows Subsystem for Linux) or **Git Bash** for a Unix-like terminal; most tutorials assume one.

## 11. Two real-world examples

**Example 1: Investigating a production problem.** A server misbehaves at 3 a.m. You SSH in, run `tail -f app.log` to watch it live, `grep -n "ERROR" app.log | tail` to see the latest failures, `df -h` to check disk space and `ps aux | grep python` to see the process. No graphical tools are available on servers: the terminal is the only interface.

**Example 2: Automating a boring task.** Renaming 300 photos, counting lines of code in a project (`find . -name "*.py" | xargs wc -l`), or running tests before every commit: a one-line command or a ten-line script replaces an hour of clicking, and you can run it again next week.

## 12. Common mistakes

- Running `rm -r` without checking the path (permanent deletion).
- Typing the prompt symbol (`$`) as part of the command.
- Forgetting quotes around names with spaces (`cd "My Documents"`).
- `>` (overwrite) when you meant `>>` (append).
- Running commands in the wrong folder (check with `pwd`).
- Using `sudo` to "fix" permission errors without understanding them.
- Copy-pasting commands from the internet without reading them.

## 13. Practice

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

## 14. Check yourself

1. What are the terminal, the shell and a command?
2. What do `pwd`, `ls`, `cd ..` do?
3. How does a pipe work?
4. What is the `PATH`?
5. What is dangerous about `rm -r`?
6. What does `chmod +x` do?

<details>
<summary>Answers</summary>

1. The terminal is the window, the shell is the program that interprets what you type, a command is a program you run by name.
2. Show the current directory; list files; move up one folder.
3. The output of the left command is fed as input to the right command.
4. The list of folders the shell searches to find a command by name.
5. It permanently deletes a folder and everything inside it, with no recycle bin.
6. It makes a file executable so it can be run as a program.

</details>

[Back to command line and Git](README.md) · Next: [Git basics](git-basics.md)
