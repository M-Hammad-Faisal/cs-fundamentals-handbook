# Python Basics 5: Files, Modules and Handling Errors

**Prerequisites:** [collections](04-strings-lists-dicts-sets.md). **You will learn:** how to read and write files (text, CSV, JSON), organize code into modules, use the standard library, and handle errors with `try/except`.

## 1. In plain words

Real programs need to **keep data** (files), **split code into pieces** (modules) and **survive things going wrong** (exceptions). Files are how data outlives your program; modules keep large programs organized; exceptions let you handle failures instead of crashing.

## 2. Files

```python
import os, tempfile

folder = tempfile.mkdtemp()                       # a throwaway folder so these examples can run anywhere
path = os.path.join(folder, "notes.txt")

with open(path, "w", encoding="utf-8") as f:      # "w" = write (creates or overwrites)
    f.write("first line\n")
    f.write("second line\n")
    f.writelines(["third line\n", "fourth line\n"])

with open(path, encoding="utf-8") as f:           # "r" = read (the default)
    whole = f.read()
print(repr(whole[:22]))                           # 'first line\nsecond line\n'

with open(path, encoding="utf-8") as f:
    for line_number, line in enumerate(f, start=1):      # iterate: reads one line at a time (big-file friendly)
        print(line_number, line.rstrip("\n"))

with open(path, "a", encoding="utf-8") as f:      # "a" = append to the end
    f.write("fifth line\n")

with open(path, encoding="utf-8") as f:
    lines = f.read().splitlines()
print(len(lines), lines[-1])                      # 5 fifth line
```

| Mode | Meaning |
|------|---------|
| `"r"` | read text (default); error if the file is missing |
| `"w"` | write text; **erases** existing content |
| `"a"` | append to the end |
| `"x"` | create; error if it already exists |
| `"b"` suffix (`"rb"`, `"wb"`) | binary (images, PDFs) |

**Always use `with open(...)`**: it closes the file automatically even when an error happens. **Always give `encoding="utf-8"`** for text ([encodings](../computer-basics/binary-and-data-representation.md)).

### Paths: use `pathlib`

```python
from pathlib import Path

root = Path(folder)
p = root / "data" / "report.txt"                  # / joins path parts on any operating system
p.parent.mkdir(parents=True, exist_ok=True)       # create the folder (and parents) if missing
p.write_text("hello\n", encoding="utf-8")
print(p.name, p.stem, p.suffix, p.exists(), p.read_text(encoding="utf-8").strip())    # report.txt report .txt True hello
print(sorted(x.name for x in root.rglob("*.txt")))                  # ['notes.txt', 'report.txt']
print(p.stat().st_size, p.is_file(), p.parent.is_dir())             # 6 True True
```

### CSV and JSON (the two formats you will use constantly)

```python
import csv, json

csv_path = root / "students.csv"
rows = [{"name": "Ana", "score": 91}, {"name": "Bo", "score": 78}]
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "score"])
    writer.writeheader()
    writer.writerows(rows)

with open(csv_path, newline="", encoding="utf-8") as f:
    students = list(csv.DictReader(f))            # every value is a STRING
print(students)                                   # [{'name': 'Ana', 'score': '91'}, {'name': 'Bo', 'score': '78'}]
print(sum(int(s["score"]) for s in students) / len(students))       # 84.5

json_path = root / "config.json"
config = {"debug": True, "ports": [80, 443], "name": "demo"}
json_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
loaded = json.loads(json_path.read_text(encoding="utf-8"))
print(loaded == config, loaded["ports"])          # True [80, 443]
```

## 3. Modules and packages

A **module** is simply a `.py` file whose names you can reuse with `import`. A **package** is a folder of modules. The **standard library** ships with hundreds of modules ("batteries included").

```python
import math                                  # use as math.sqrt(...)
from math import sqrt, pi                    # import specific names
import random as rnd                         # rename with `as`

print(math.sqrt(16), sqrt(25), round(pi, 3), rnd.Random(1).randint(1, 6) in range(1, 7))     # 4.0 5.0 3.142 True

from collections import Counter, defaultdict, deque
from datetime import date, datetime, timedelta
print(date(2026, 11, 7).strftime("%A %d %B %Y"), date(2026, 11, 7) + timedelta(days=30))     # Saturday 07 November 2026 2026-12-07
print(Counter("hello").most_common(1), (datetime(2026, 1, 1, 10, 30) - datetime(2026, 1, 1, 8, 0)).seconds // 60)   # [('l', 2)] 150
```

Handy standard modules: `math`, `random`, `statistics`, `datetime`, `collections`, `itertools`, `functools`, `re` (regular expressions), `json`, `csv`, `os`, `pathlib`, `sys`, `argparse`, `logging`, `sqlite3`, `unittest`, `urllib`/`http`, `subprocess`, `threading`, `asyncio`.

### Writing your own module

```python
import sys, importlib, tempfile, textwrap

mod_dir = tempfile.mkdtemp()
Path(mod_dir, "geometry.py").write_text(textwrap.dedent('''
    """Small geometry helpers."""
    import math

    def circle_area(radius):
        return math.pi * radius ** 2

    def rectangle_area(width, height):
        return width * height

    if __name__ == "__main__":          # runs only when executed directly, NOT when imported
        print("running as a script")
'''), encoding="utf-8")

sys.path.insert(0, mod_dir)               # make the folder importable (normally your project folder already is)
geometry = importlib.import_module("geometry")
print(round(geometry.circle_area(2), 2), geometry.rectangle_area(3, 4))      # 12.57 12
```

`if __name__ == "__main__":` is the standard way to make a file usable both as a program and as an importable module. More on packages, `pip` and virtual environments: [packaging and tooling](../../08-modern-python/packaging-tooling/README.md).

### Third-party packages

Install with `pip` into a [virtual environment](../setup/README.md): `pip install requests`, then `import requests`. Popular ones: `requests` (HTTP), `numpy`/`pandas` (data), `flask`/`django`/`fastapi` (web), `pytest` (testing).

## 4. Errors and exceptions

When something goes wrong Python raises an **exception**. If nothing handles it, the program stops and prints a **traceback**.

```python
# Common exceptions and what causes them (each lambda runs one failing operation)
failures = {
    'int("abc")': lambda: int("abc"),
    "1 / 0": lambda: 1 / 0,
    "[1, 2][5]": lambda: [1, 2][5],
    '{"a": 1}["b"]': lambda: {"a": 1}["b"],
    "undefined_name": lambda: undefined_name,
    '"a" + 1': lambda: "a" + 1,
    'open("/no/such/file")': lambda: open("/no/such/file"),
}
for label, action in failures.items():
    try:
        action()
    except Exception as error:
        print(f"{label:24} -> {type(error).__name__}: {str(error)[:40]}")
# int("abc")               -> ValueError: invalid literal for int() with base 10: 'abc'
# 1 / 0                    -> ZeroDivisionError: division by zero
# [1, 2][5]                -> IndexError: list index out of range
# {"a": 1}["b"]            -> KeyError: 'b'
# undefined_name           -> NameError: name 'undefined_name' is not defined
# "a" + 1                  -> TypeError: can only concatenate str (not "int") to str
# open("/no/such/file")    -> FileNotFoundError: [Errno 2] No such file or directory: '/no/such/file'
```

### `try`, `except`, `else`, `finally`

```python
def read_number(text):
    try:
        value = int(text)                    # code that might fail
    except ValueError:                       # handle ONE specific kind of error
        print(f"{text!r} is not a number")
        return None
    else:                                    # runs only if no error happened
        return value
    finally:                                 # ALWAYS runs: cleanup (closing files, releasing locks)
        print("done checking", repr(text))

print(read_number("42"))                     # done checking '42'   then   42
print(read_number("abc"))                    # 'abc' is not a number / done checking 'abc' / None

def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return float("inf")
    except TypeError as error:               # several except clauses for different errors
        raise ValueError("both arguments must be numbers") from error     # raise a clearer error

print(safe_divide(10, 2), safe_divide(1, 0))          # 5.0 inf
```

### Raising your own errors

```python
def set_age(age):
    if not isinstance(age, int):
        raise TypeError("age must be an integer")
    if age < 0:
        raise ValueError("age cannot be negative")
    return age

for value in (20, -5, "x"):
    try:
        print(set_age(value))
    except (TypeError, ValueError) as error:         # catch several types at once
        print(f"invalid: {error}")
# 20 / invalid: age cannot be negative / invalid: age must be an integer
```

### Rules of good error handling

1. **Catch specific exceptions** (`except ValueError:`), not everything (`except:`) and never silence errors with `pass`.
2. **Handle errors where you can do something useful**; otherwise let them propagate.
3. **Use `with`/`finally`** to clean up resources.
4. **Raise clear errors** with helpful messages (`raise ValueError(f"bad port: {port}")`).
5. **Do not use exceptions for normal flow** when a simple check is clearer.

Deep dive: [exceptions, logging and testing](../../08-modern-python/exceptions-logging-testing/README.md).

## 5. Putting it together: a small data-processing script

```python
from collections import defaultdict

log_path = root / "app.log"
log_path.write_text("""2026-01-01 INFO started
2026-01-01 ERROR disk full
2026-01-02 WARNING slow response
2026-01-02 ERROR timeout
malformed
2026-01-03 ERROR disk full
""", encoding="utf-8")

def summarize(path):
    counts = defaultdict(int)
    problems = []
    with open(path, encoding="utf-8") as f:
        for number, line in enumerate(f, start=1):
            parts = line.split(maxsplit=2)
            if len(parts) < 3:
                problems.append(number)                 # skip malformed lines, but remember them
                continue
            date, level, message = parts
            counts[level] += 1
    return dict(counts), problems

counts, problems = summarize(log_path)
print(counts, "bad lines:", problems)                  # {'INFO': 1, 'ERROR': 3, 'WARNING': 1} bad lines: [5]

try:
    summarize(root / "missing.log")
except FileNotFoundError:
    print("log file not found: check the path")
```

## 6. Two real-world examples

**Example 1: A nightly report.** A script reads a CSV of orders (`csv.DictReader`), groups totals by day with a `defaultdict`, and writes the summary to JSON and a text file. If a row is malformed it logs the line number and continues (try/except per row) instead of crashing the whole job.

**Example 2: A config loader.** An application loads `config.json` at startup. If the file is missing it falls back to defaults; if it contains invalid JSON it raises a clear `ConfigError("config.json line 4: ...")`. Users see a helpful message instead of a stack trace.

## 7. Common mistakes

- Forgetting to close files (use `with`).
- Opening with `"w"` and accidentally erasing data.
- Forgetting `encoding="utf-8"` (garbled text on some systems).
- Reading a giant file with `.read()` (memory); iterate line by line.
- Treating CSV values as numbers (they are strings until you convert them).
- A bare `except:` that hides bugs (it even catches `KeyboardInterrupt`).
- Naming your own file like a standard module (`random.py`, `json.py`) so imports break.
- Hard-coding paths like `C:\Users\me\data.txt`; use `pathlib` and relative paths.

## 8. Practice

1. Write a function that counts the lines, words and characters of a text file.
2. Read a CSV of products and print the total value (`price x qty`).
3. Save a dictionary to JSON and load it back, comparing equality.
4. Write `safe_int(text, default=0)` returning a default when conversion fails.
5. Write a function that reads a file and returns `None` (with a message) if it does not exist.
6. Create a small module `mathutils.py` with `mean` and `median`, and import it.
7. Explain what `finally` guarantees with an example involving a file or lock.

<details>
<summary>Solutions</summary>

**1.**
```python
def file_stats(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    return len(text.splitlines()), len(text.split()), len(text)
print(file_stats(path))                               # (5, 10, 57)
```

**2.**
```python
products = root / "products.csv"
products.write_text("name,price,qty\npen,50,10\nbook,300,2\n", encoding="utf-8")
with open(products, newline="", encoding="utf-8") as f:
    total = sum(float(r["price"]) * int(r["qty"]) for r in csv.DictReader(f))
print(total)                                          # 1100.0
```

**3.**
```python
data = {"a": [1, 2], "b": {"c": True}}
(root / "x.json").write_text(json.dumps(data), encoding="utf-8")
print(json.loads((root / "x.json").read_text(encoding="utf-8")) == data)      # True
```

**4.**
```python
def safe_int(text, default=0):
    try:
        return int(text)
    except (ValueError, TypeError):
        return default
print(safe_int("12"), safe_int("x"), safe_int(None, -1))        # 12 0 -1
```

**5.**
```python
def read_or_none(file_path):
    try:
        with open(file_path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"{file_path} does not exist")
        return None
print(read_or_none(root / "nope.txt"))
```

**6.**
```python
Path(mod_dir, "mathutils.py").write_text('''
def mean(xs): return sum(xs) / len(xs)
def median(xs):
    s = sorted(xs); mid = len(s) // 2
    return s[mid] if len(s) % 2 else (s[mid - 1] + s[mid]) / 2
''', encoding="utf-8")
mathutils = importlib.import_module("mathutils")
print(mathutils.mean([1, 2, 3, 4]), mathutils.median([1, 2, 3, 4]))      # 2.5 2.5
```

**7.** `finally` runs whether the `try` block succeeds, raises or returns, so cleanup is guaranteed:
```python
log = []
def work():
    try:
        log.append("acquire lock")
        raise RuntimeError("boom")
    finally:
        log.append("release lock")        # runs even though an error was raised
try:
    work()
except RuntimeError:
    pass
print(log)                                # ['acquire lock', 'release lock']
```

</details>

## 9. Check yourself

1. Why use `with open(...)`?
2. What do the file modes `"r"`, `"w"` and `"a"` do?
3. What is a module, and what does `if __name__ == "__main__":` do?
4. What happens if you do not handle an exception?
5. Why is `except:` (bare) discouraged?
6. When does the `else` block of a `try` run? The `finally` block?

<details>
<summary>Answers</summary>

1. It closes the file automatically, even if an error occurs.
2. Read, write (erasing existing content), append to the end.
3. A module is a `.py` file you can import; the guard runs the code only when the file is executed directly, not when imported.
4. The program stops and prints a traceback.
5. It hides unexpected errors and catches things like `KeyboardInterrupt`; catch specific exceptions instead.
6. `else` runs only if the `try` block raised nothing; `finally` always runs.

</details>

[Back to Python fundamentals](README.md) · Previous: [strings, lists, dicts and sets](04-strings-lists-dicts-sets.md) · Next: [debugging and testing](06-debugging-and-testing.md)
