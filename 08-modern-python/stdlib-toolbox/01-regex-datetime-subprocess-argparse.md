# The Standard Library Toolbox: Regex, Dates and Time Zones, Subprocesses, Command-Line Tools

**Prerequisites:** [strings, lists, dicts and sets](../../00-foundations/python-fundamentals/04-strings-lists-dicts-sets.md), [files, modules and errors](../../00-foundations/python-fundamentals/05-files-modules-errors.md), [exceptions and logging](../exceptions-logging-testing/README.md), [secure Python](../../10-security/threat-modeling/01-threat-modeling-and-secure-python.md). **You will learn:** four standard-library skills that real scripts need constantly: **regular expressions** (`re`) for pulling structure out of text, **dates, times and time zones** (`datetime`, `zoneinfo`) without the classic bugs, running other programs safely with **`subprocess`**, and building **command-line tools** with `argparse`, followed by a map of other useful modules. Everything is standard library, runs offline and was executed with the outputs shown.

## 1. Regular expressions

A **regular expression** (regex) describes a *pattern* of text. Use one when the structure is regular but messy (log lines, ids, simple formats); do not use one for nested formats such as HTML, JSON or code (use a real parser).

### The building blocks

| Pattern | Matches |
|---------|---------|
| `.` | any character except newline |
| `\d` `\w` `\s` | a digit, a word character (letter, digit, underscore), whitespace |
| `[abc]` `[a-z]` `[^0-9]` | one of the listed characters, a range, anything but digits |
| `*` `+` `?` | zero or more, one or more, zero or one of the previous item |
| `{3}` `{2,4}` | exactly 3, between 2 and 4 |
| `^` `$` | start and end of the string (or line with `re.MULTILINE`) |
| `(...)` | a **group**: captures the text; `(?P<name>...)` names it |
| `a|b` | a or b |
| `\b` | a word boundary |

```python
import re

line = '2026-03-14 09:21:07 ERROR payments user=ada amount=49.90 request_id=a1b2c3'

LOG = re.compile(r"""
    (?P<date>\d{4}-\d{2}-\d{2})\s+          # 2026-03-14
    (?P<time>\d{2}:\d{2}:\d{2})\s+          # 09:21:07
    (?P<level>[A-Z]+)\s+                    # ERROR
    (?P<service>\w+)\s+                     # payments
    (?P<rest>.*)                            # everything else
""", re.VERBOSE)                             # VERBOSE: spaces and comments inside the pattern are ignored

m = LOG.fullmatch(line)                      # fullmatch: the WHOLE string must match
print(m.group("level"), m["service"], m.groupdict()["date"])
# ERROR payments 2026-03-14

fields = dict(re.findall(r"(\w+)=(\S+)", m["rest"]))       # findall with two groups returns pairs
print(fields)
# {'user': 'ada', 'amount': '49.90', 'request_id': 'a1b2c3'}
```

**Which function?** `re.match` anchors at the start only; `re.search` finds the first match anywhere; `re.fullmatch` requires the whole string (usually what you want for **validation**); `re.findall` returns all matches (or the groups); `re.finditer` yields match objects with positions; `re.sub` replaces; `re.split` splits. Always **compile** patterns you reuse (`re.compile`) and write them as **raw strings** (`r"\d+"`) so backslashes reach the regex engine.

```python
print(re.sub(r"\d{4}-\d{2}-\d{2}", "<date>", "from 2026-01-02 to 2026-02-03"))
# from <date> to <date>

def mask_email(match):                                       # sub accepts a function: compute the replacement
    user, domain = match["user"], match["domain"]
    return user[0] + "***@" + domain

print(re.sub(r"(?P<user>[\w.]+)@(?P<domain>[\w.]+)", mask_email, "write to ada.lovelace@example.com or bob@test.org"))
# write to a***@example.com or b***@test.org

print(re.split(r"[,;]\s*", "a, b;c,   d"))
# ['a', 'b', 'c', 'd']
```

### Greedy versus lazy, and anchors

Quantifiers are **greedy** by default (take as much as possible); add `?` to make them **lazy**:

```python
html = "<b>bold</b> and <i>italic</i>"
print(re.findall(r"<.+>", html))        # greedy: one giant match from the first < to the last >
# ['<b>bold</b> and <i>italic</i>']
print(re.findall(r"<.+?>", html))       # lazy: the shortest match each time
# ['<b>', '</b>', '<i>', '</i>']
print(re.findall(r"<[^>]+>", html))     # clearer still: "anything but >"
# ['<b>', '</b>', '<i>', '</i>']

print(bool(re.match(r"\d+", "123abc")), bool(re.fullmatch(r"\d+", "123abc")))    # match is a prefix test; fullmatch is a whole-string test
# True False
```

### Regex pitfalls

- **Validation with `search` or `match`** accepts garbage around the pattern; use `fullmatch` or anchors.
- **Backtracking blow-ups:** nested quantifiers like `(a+)+` can take exponential time on crafted input (see [ReDoS](../../10-security/web-vulnerabilities/01-owasp-top-ten-in-python.md)).
- **Over-ambitious patterns:** the "perfect" email regex is thousands of characters; check the format loosely and verify by sending a message.
- **Readability:** use `re.VERBOSE` and named groups; add tests with real examples.

## 2. Dates, times and time zones

Date handling is a classic source of bugs. The rules that prevent most of them:

1. **Store and compute in UTC**; convert to a local zone only for display.
2. Use **timezone-aware** datetimes everywhere (a "naive" datetime has no zone and is ambiguous).
3. Use **IANA zone names** (`"Europe/London"`, `"America/New_York"`) through `zoneinfo`, never fixed offsets for people's local times, because the offset changes with daylight saving time (DST).
4. Measure **durations** with a monotonic clock (`time.monotonic()`), not wall-clock differences.

```python
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

utc_meeting = datetime(2026, 3, 8, 15, 30, tzinfo=timezone.utc)       # an unambiguous instant
print(utc_meeting.isoformat())
# 2026-03-08T15:30:00+00:00

for zone in ("UTC", "America/New_York", "Europe/London", "Asia/Karachi"):
    print(f"{zone:<17}", utc_meeting.astimezone(ZoneInfo(zone)).strftime("%a %Y-%m-%d %H:%M %Z"))
# UTC               Sun 2026-03-08 15:30 UTC
# America/New_York  Sun 2026-03-08 11:30 EDT
# Europe/London     Sun 2026-03-08 15:30 GMT
# Asia/Karachi      Sun 2026-03-08 20:30 PKT
```

New York is on daylight time (EDT, UTC-4) on that date, because clocks in the United States moved forward at 02:00 that very morning, while London is still on GMT. The same instant has different local clock readings, and the zone rules are looked up for you.

### The DST trap: "one day later" is not always 24 hours

```python
ny = ZoneInfo("America/New_York")
before = datetime(2026, 3, 7, 12, 0, tzinfo=ny)                 # noon the day BEFORE the spring-forward change
print((before + timedelta(days=1)).isoformat())                  # wall-clock arithmetic: noon the next day
# 2026-03-08T12:00:00-04:00
elapsed = (before + timedelta(days=1)) - before
print(elapsed)                                                   # same zone object: Python subtracts wall clocks
# 1 day, 0:00:00

real_gap = (before + timedelta(days=1)).astimezone(timezone.utc) - before.astimezone(timezone.utc)
print(real_gap)                                                  # the real elapsed time between the two instants
# 23:00:00
```

Because 2026-03-08 only had 23 hours in New York, "noon tomorrow" is **23 real hours** later. Decide which you mean: *same wall-clock time tomorrow* (calendar arithmetic in the local zone, as the first result) or *24 hours later* (convert to UTC, add, convert back). For anything that must be exact (billing, scheduling across zones) do the arithmetic in UTC.

```python
# parsing and formatting
stamp = datetime.fromisoformat("2026-03-14T09:21:07+00:00")
print(stamp.strftime("%d %b %Y, %H:%M"), "|", stamp.timestamp())
# 14 Mar 2026, 09:21 | 1773480067.0

# differences and ranges
deadline = datetime(2026, 4, 1, tzinfo=timezone.utc)
print((deadline - stamp).days, "days left")
# 17 days left

print(datetime.now(timezone.utc).tzinfo)                         # the reliable way to get "now": always pass a zone
# UTC
```

Naive datetimes cannot be compared with aware ones (`TypeError`), which is a feature: it forces you to decide. For parsing many formats, `datetime.strptime` handles fixed patterns (`"%Y-%m-%d"`); for messy human input, use a library (`dateutil`, `pendulum`) rather than guessing.

## 3. Running other programs with `subprocess`

Scripts often need to call other programs (`git`, `ffmpeg`, a compiler). `subprocess.run` is the tool: it runs a command, waits for it and returns a `CompletedProcess`. The important habits: pass the command as a **list** (no shell, no injection, see [secure Python](../../10-security/threat-modeling/01-threat-modeling-and-secure-python.md)), **capture** output, set a **timeout**, and **check** the exit code.

```python
import subprocess, sys

result = subprocess.run(
    [sys.executable, "-c", "print('hello from a child'); import sys; print('warning', file=sys.stderr)"],
    capture_output=True, text=True, timeout=10,
)
print(result.returncode, repr(result.stdout), repr(result.stderr))
# 0 'hello from a child\n' 'warning\n'

# check=True raises if the exit code is not 0
try:
    subprocess.run([sys.executable, "-c", "import sys; sys.exit(3)"], check=True, capture_output=True)
except subprocess.CalledProcessError as e:
    print("failed with exit code", e.returncode)
# failed with exit code 3

# timeouts stop runaway programs
try:
    subprocess.run([sys.executable, "-c", "import time; time.sleep(30)"], timeout=0.5)
except subprocess.TimeoutExpired:
    print("killed after the timeout")
# killed after the timeout

# feeding input and setting the environment
out = subprocess.run([sys.executable, "-c", "import os, sys; print(os.environ['GREETING'], sys.stdin.read().upper())"],
                     input="data", capture_output=True, text=True, env={"GREETING": "hi"}).stdout
print(out.strip())
# hi DATA
```

**Reading streaming output** while the program runs uses `Popen`:

```python
with subprocess.Popen([sys.executable, "-u", "-c", "for i in range(3): print('line', i)"], stdout=subprocess.PIPE, text=True) as proc:
    for line in proc.stdout:                             # lines arrive as the child produces them
        print("got:", line.strip())
# got: line 0
# got: line 1
# got: line 2
```

Rules: use `sys.executable` to run Python scripts with the **same interpreter**; split a command written as one string with `shlex.split`, never by pasting user input into a string; avoid `shell=True` unless you really need shell features (pipes, globbing) and the input is fully trusted; always handle a **non-zero exit code** and **timeouts**; do not try to read stdout and stderr separately from `Popen` pipes without care (it can deadlock; `run` or `communicate()` handles it).

## 4. Command-line tools with `argparse`

`argparse` turns `sys.argv` into validated, typed options, and generates `--help` for free. Design the parser so it can be **tested without a process**: `parser.parse_args([...])` takes a list.

```python
import argparse

def build_parser():
    parser = argparse.ArgumentParser(prog="todo", description="A tiny to-do manager.")
    parser.add_argument("--db", default="todo.json", help="storage file (default: %(default)s)")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="repeat for more detail (-vv)")
    sub = parser.add_subparsers(dest="command", required=True)          # git-style subcommands

    add = sub.add_parser("add", help="add a task")
    add.add_argument("title")
    add.add_argument("--priority", type=int, choices=range(1, 4), default=2, help="1 (high) to 3 (low)")
    add.add_argument("--tag", action="append", default=[], help="repeatable: --tag a --tag b")

    done = sub.add_parser("done", help="mark a task done")
    done.add_argument("task_id", type=int)

    ls = sub.add_parser("list", help="show tasks")
    group = ls.add_mutually_exclusive_group()
    group.add_argument("--open", action="store_true")
    group.add_argument("--done", dest="only_done", action="store_true")
    return parser

parser = build_parser()
args = parser.parse_args(["-vv", "add", "Write lesson", "--priority", "1", "--tag", "work", "--tag", "py"])
print(args.command, args.title, args.priority, args.tag, args.verbose)
# add Write lesson 1 ['work', 'py'] 2

for bad in (["add"], ["add", "x", "--priority", "9"], ["list", "--open", "--done"], ["done", "abc"]):
    try:
        parser.parse_args(bad)
    except SystemExit as e:                              # argparse prints usage to stderr and exits with code 2
        print("rejected", bad, "-> exit code", e.code)
# rejected ['add'] -> exit code 2
# rejected ['add', 'x', '--priority', '9'] -> exit code 2
# rejected ['list', '--open', '--done'] -> exit code 2
# rejected ['done', 'abc'] -> exit code 2
```

Good CLI manners: **exit code 0 on success and non-zero on failure** (scripts and CI rely on it); **errors to stderr**, results to stdout (so output can be piped); `--help` that says what the tool does; sensible defaults; no secrets as arguments (they show up in process lists; read them from the environment or a file); and a `main(argv=None)` function that returns an exit code, called by `if __name__ == "__main__": raise SystemExit(main())`, as in the [packaging lesson](../engineering-workflow/01-ci-docker-pre-commit-and-publishing.md). For richer tools, **Typer** and **Click** build the parser from function signatures and add colours and prompts.

## 5. A map of other useful standard-library modules

| Need | Module | One-liner |
|------|--------|-----------|
| Paths and files | `pathlib`, `shutil`, `tempfile` | `Path("a") / "b.txt"`, `shutil.copytree`, `tempfile.TemporaryDirectory()` |
| Structured text | `json`, `csv`, `tomllib`, `configparser` | `json.loads`, `csv.DictReader`, `tomllib.load` |
| Counting and grouping | `collections` | `Counter`, `defaultdict`, `deque`, `namedtuple`, `ChainMap` |
| Iteration and functions | `itertools`, `functools` | `chain`, `groupby`, `islice`; `lru_cache`, `partial`, `reduce` |
| Numbers | `decimal`, `fractions`, `statistics`, `math`, `random` | exact money, `statistics.median`, seeded `random.Random` |
| Identity and hashing | `uuid`, `hashlib`, `secrets`, `hmac` | `uuid.uuid4()`, `hashlib.sha256`, `secrets.token_urlsafe` |
| Text | `textwrap`, `string`, `unicodedata`, `difflib` | `textwrap.dedent`, `difflib.unified_diff` |
| Concurrency | `threading`, `concurrent.futures`, `asyncio`, `multiprocessing` | see the [concurrency lesson](../concurrency/01-threads-processes-and-futures.md) |
| Networking | `socket`, `http.server`, `urllib.request`, `ssl` | [sockets lab](../../07-networking/tcp-ip-osi/02-sockets-tcp-udp-lab.md) |
| Data | `sqlite3`, `pickle`, `shelve` | SQLite is a full SQL database in the standard library (never unpickle untrusted data) |
| Testing and debugging | `unittest`, `doctest`, `pdb`, `timeit`, `cProfile`, `logging` | `python -m timeit "..."`, `breakpoint()` |
| Dates and time | `datetime`, `zoneinfo`, `calendar`, `time` | this lesson |

A tiny sample of two of them working together, grouping words by first letter with `collections` and `itertools`:

```python
from collections import Counter, defaultdict
from itertools import groupby

words = "apple avocado banana blueberry cherry apple".split()
by_letter = defaultdict(set)
for w in words:
    by_letter[w[0]].add(w)
print({k: sorted(v) for k, v in sorted(by_letter.items())})
# {'a': ['apple', 'avocado'], 'b': ['banana', 'blueberry'], 'c': ['cherry']}
print(Counter(words).most_common(1))
# [('apple', 2)]
print([(k, len(list(g))) for k, g in groupby(sorted(words), key=lambda w: w[0])])
# [('a', 3), ('b', 2), ('c', 1)]
```

## 6. Common mistakes

- Using `re.match` to validate (it only anchors at the start) instead of `fullmatch`; forgetting raw strings; parsing HTML or JSON with regex.
- Naive datetimes and `datetime.now()` / `utcnow()` without a zone; storing local times; fixed offsets instead of zone names.
- Computing durations from wall-clock time (it can jump); assuming a day has 24 hours.
- `subprocess.run(cmd_string, shell=True)` with input that came from outside.
- Ignoring exit codes and timeouts; capturing huge outputs in memory.
- CLIs that print errors to stdout, always exit 0, or read secrets from arguments.
- Re-implementing what the standard library already does (paths with string concatenation, CSV parsing with `split(",")`).

## 7. Two real-world examples

**Example 1: The log digest.** An on-call engineer wrote a 30-line script with one compiled, named-group regex per log format to turn gigabytes of text logs into a table of errors per service per hour (a `Counter` keyed by `(service, hour)`). It replaced an hour of manual `grep` every morning, and unit tests with sample lines protected it from format changes.

**Example 2: The "off by an hour" meeting.** A scheduling feature stored meeting times as naive local datetimes. During the week clocks changed, some meetings shifted by an hour for attendees in other countries. The fix: store UTC instants plus the organiser's IANA zone name, and convert for display with `zoneinfo`.

## 8. Practice

1. Write a regex that extracts all hashtags (`#word`, letters, digits and underscore) from a tweet, lower-cased and without duplicates (keep first appearance order).
2. Validate a UK-style postcode loosely with `fullmatch` (one or two letters, one or two digits, a space, a digit and two letters). Test it on four valid and four invalid examples.
3. A flight departs `2026-10-24 22:00` in `Asia/Karachi` and lands `2026-10-25 06:30` in `Europe/London` (local times). How long is the flight? (UK clocks go back on 2026-10-25 at 02:00.)
4. Run `git --version` (or `python --version`) with `subprocess.run`, capture the output and handle the case where the program does not exist (`FileNotFoundError`).
5. Add an `export` subcommand to the `todo` parser with a `--format` choice of `json` or `csv`, defaulting to `json`, and test parsing.
6. Explain why `datetime.now()` (naive) is a poor choice for a timestamp stored in a database.

<details>
<summary>Solutions</summary>

1. ```python
   def hashtags(text):
       seen = []
       for tag in re.findall(r"#(\w+)", text):
           tag = tag.lower()
           if tag not in seen:
               seen.append(tag)
       return seen
   print(hashtags("Loving #Python and #python3! #Python #AI_2026"))
   # ['python', 'python3', 'ai_2026']
   ```
2. ```python
   POSTCODE = re.compile(r"[A-Za-z]{1,2}\d{1,2} \d[A-Za-z]{2}")
   good = ["M1 1AE", "SW1 2AA", "EC1 4AB", "B33 8TH"]
   bad = ["", "12345", "M1AE", "SW1 2A"]
   print([bool(POSTCODE.fullmatch(p)) for p in good], [bool(POSTCODE.fullmatch(p)) for p in bad])
   # [True, True, True, True] [False, False, False, False]
   ```
   (Real postcodes have more rules; "loose but safe" is a sensible first filter.)
3. ```python
   depart = datetime(2026, 10, 24, 22, 0, tzinfo=ZoneInfo("Asia/Karachi"))
   arrive = datetime(2026, 10, 25, 6, 30, tzinfo=ZoneInfo("Europe/London"))
   print(arrive.astimezone(timezone.utc) - depart.astimezone(timezone.utc))
   # 13:30:00
   ```
   Convert both to UTC and subtract: Karachi (UTC+5) 22:00 is 17:00 UTC; London at 06:30 on 25 October is already back on GMT (UTC+0), so 06:30 UTC; the flight is 13 hours 30 minutes. (Had you subtracted the naive local clock readings, 22:00 to 06:30, you would get 8.5 hours: wrong.)
4. ```python
   try:
       out = subprocess.run(["git", "--version"], capture_output=True, text=True, check=True, timeout=5)
       print(out.stdout.strip().startswith("git version"))
   except FileNotFoundError:
       print("git is not installed")
   # True
   ```
5. ```python
   parser2 = build_parser()
   sub_actions = [a for a in parser2._actions if isinstance(a, argparse._SubParsersAction)][0]
   export = sub_actions.add_parser("export", help="export tasks")
   export.add_argument("--format", choices=["json", "csv"], default="json")
   print(parser2.parse_args(["export"]).format, parser2.parse_args(["export", "--format", "csv"]).format)
   # json csv
   ```
   (The cleaner way is to add the subparser inside `build_parser`; this shows the idea.)
6. A naive local timestamp does not say which zone it is in, so it cannot be compared across servers or users, and it silently changes meaning when the server's zone or DST rules change. Store aware UTC instants.

</details>

## 9. Check yourself

1. When should you use `fullmatch` instead of `match` or `search`?
2. What do named groups and `re.VERBOSE` buy you?
3. Why store times in UTC and keep an IANA zone name for display?
4. Why is "tomorrow at noon" sometimes not 24 hours away?
5. Why pass a list to `subprocess.run`, and what does `check=True` do?
6. How do you make an `argparse` CLI easy to test?
7. What exit codes should a command-line tool use?

<details>
<summary>Answers</summary>

1. When the entire string must fit the pattern (validation); `match` only anchors at the start and `search` finds a match anywhere.
2. Readable, self-documenting patterns and results accessed by name instead of position.
3. UTC is unambiguous and comparable; the zone name lets you apply the right local rules (including DST) when showing a time to a person.
4. Daylight saving changes make some days 23 or 25 hours long; wall-clock arithmetic and elapsed-time arithmetic differ.
5. A list bypasses the shell so arguments cannot inject commands; `check=True` raises `CalledProcessError` if the exit code is non-zero.
6. Build the parser in a function and call `parse_args([...])` with explicit lists, instead of relying on `sys.argv`.
7. 0 for success, non-zero for failure (argparse uses 2 for usage errors), with errors on stderr.

</details>

[Back to Modern Python](../README.md)
