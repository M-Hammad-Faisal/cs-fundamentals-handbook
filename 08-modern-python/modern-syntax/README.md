# Modern Python Language Features (3.8 to 3.14)

## 1. The concept

Python changes every year. Code written "the modern way" is shorter, safer and easier to read: structural pattern matching instead of `if/elif` chains, f-strings instead of `%` formatting, `pathlib` instead of string paths, exception groups, better generics. This chapter is a tour of the features you should know and **when each arrived**, so you can read new code and know what your Python version supports.

| Version | Highlights |
|---------|-----------|
| **3.8** | walrus `:=`, positional-only parameters `/`, f-string `=` |
| **3.9** | `dict | dict`, `list[int]` built-in generics, `str.removeprefix/removesuffix`, `zoneinfo` |
| **3.10** | **`match`/`case`**, `X | Y` unions, parenthesized context managers, `zip(strict=True)`, better error messages |
| **3.11** | **exception groups and `except*`**, `tomllib`, `asyncio.TaskGroup`, `Self`, 10-60% faster |
| **3.12** | `type` statement, **generic syntax** `def f[T]`, `@override`, f-string nesting, `itertools.batched` |
| **3.13** | free-threaded (no GIL) and JIT **experimental builds**, better REPL |
| **3.14** | **t-strings** (template strings), deferred annotation evaluation, `compression.zstd`, `InterpreterPoolExecutor` |

(Check your own version with `python --version`; use `sys.version_info >= (3, 12)` in code.)

## 2. Strings: f-strings and formatting

```python
name, price, qty = "Ana", 1234.5, 3
print(f"{name} bought {qty} items")                         # Ana bought 3 items
print(f"total: {price * qty:,.2f}")                          # total: 3,703.50   (thousands separator, 2 decimals)
print(f"{name!r} {name:>8}| {name:<8}| {name:^8}|")          # 'Ana'      Ana| Ana     |   Ana   |
print(f"{255:#x} {255:08b} {0.256:.1%}")                     # 0xff 11111111 25.6%
x = 42
print(f"{x=} {x*2=}")                                        # x=42 x*2=84      (debugging: name and value, 3.8+)

import datetime
d = datetime.date(2026, 11, 7)
print(f"{d:%d %b %Y}")                                       # 07 Nov 2026      (format spec is passed to __format__)

width = 10
print(f"[{'hi':>{width}}]")                                  # [        hi]   (nested format field)
```

Older styles still exist (`"%s" % x`, `"{}".format(x)`), but **f-strings** are the default: faster and more readable. Use `str.format` or `string.Template` when the template is stored separately from the values.

Useful string methods: `str.removeprefix`, `removesuffix` (3.9), `str.join`, `split`/`rsplit`/`partition`, `casefold` (for case-insensitive comparison), `str.isdigit()` vs `isnumeric()`.

```python
print("test_data.csv".removesuffix(".csv"), "a,b,,c".split(","), "k=v=w".partition("="))
# test_data ['a', 'b', '', 'c'] ('k', '=', 'v=w')
```

### Template strings (t-strings, 3.14)

A **t-string** looks like an f-string but does **not** produce a string immediately; it produces a `Template` object holding the text parts and the interpolated values **separately**, so a function can process them **safely** (escape HTML, parameterize SQL, quote shell arguments) before combining.

```python
from string.templatelib import Template, Interpolation
import html

def render_html(template: Template) -> str:
    parts = []
    for item in template:
        if isinstance(item, Interpolation):
            parts.append(html.escape(str(item.value)))        # escape ONLY the dynamic parts
        else:
            parts.append(item)                                # the literal text is trusted
    return "".join(parts)

user_input = "<script>alert(1)</script>"
safe = render_html(t"<p>Hello {user_input}!</p>")
print(safe)                          # <p>Hello &lt;script&gt;alert(1)&lt;/script&gt;!</p>
```

This is the safe alternative to building HTML/SQL with f-strings, which would let user input inject code.

## 3. Functions: parameters, unpacking and the walrus

```python
def describe(a, b, /, c, *, d):               # a, b: positional-only | c: either | d: keyword-only
    return (a, b, c, d)

print(describe(1, 2, 3, d=4), describe(1, 2, c=3, d=4))      # (1, 2, 3, 4) (1, 2, 3, 4)
try:
    describe(a=1, b=2, c=3, d=4)                              # a and b cannot be passed by name
except TypeError:
    print("positional-only parameters")
```

Positional-only (`/`) lets you rename parameters later without breaking callers; keyword-only (`*`) forces readable calls for flags (`connect(host, *, timeout=5)`).

```python
first, *middle, last = [1, 2, 3, 4, 5]                        # star unpacking
print(first, middle, last)                                    # 1 [2, 3, 4] 5
head, *_ = "hello"
merged = {**{"a": 1, "b": 2}, **{"b": 3}}                    # dict unpacking: later keys win
print(merged, {"a": 1} | {"b": 2}, [*range(3), *"ab"])       # {'a': 1, 'b': 3} {'a': 1, 'b': 2} [0, 1, 2, 'a', 'b']

def total(*numbers, **options):                               # collect extra arguments
    return sum(numbers), options
print(total(1, 2, 3, round=True))                             # (6, {'round': True})

import re
if (m := re.search(r"(\d+)-(\d+)", "range 10-20")) is not None:   # walrus: assign inside an expression
    print(int(m.group(2)) - int(m.group(1)))                  # 10
```

`zip(strict=True)` (3.10) turns silent truncation bugs into errors:

```python
print(list(zip([1, 2], "ab", strict=True)))                   # [(1, 'a'), (2, 'b')]
try:
    list(zip([1, 2], "a", strict=True))
except ValueError as e:
    print(e)                                                  # zip() argument 2 is shorter than argument 1
```

## 4. Structural pattern matching (`match`/`case`, 3.10)

`match` compares a value against **patterns** and can **destructure** it. It is not just a `switch`: it matches on shape, type and content.

```python
def handle(command):
    match command:
        case "quit" | "exit":                                  # OR pattern with literals
            return "bye"
        case ["go", direction]:                                # sequence pattern: exactly two items
            return f"going {direction}"
        case ["pick", *items] if items:                        # star pattern + guard
            return f"picked {', '.join(items)}"
        case {"action": "move", "x": x, "y": y}:               # mapping pattern (extra keys allowed)
            return f"move to {x},{y}"
        case _:                                                # wildcard: the default
            return "unknown command"

print(handle("exit"), handle(["go", "north"]), handle(["pick", "key", "map"]))
print(handle({"action": "move", "x": 1, "y": 2, "speed": 5}), handle(42))
# bye going north picked key, map
# move to 1,2 unknown command
```

### Class patterns, `as` captures and guards

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

@dataclass
class Circle:
    center: Point
    r: float

def where(shape):
    match shape:
        case Point(x=0, y=0):
            return "origin"
        case Point(x, 0) | Point(0, x):                         # either axis, binds x
            return f"on an axis at {x}"
        case Point(x, y) if x == y:
            return "on the diagonal"
        case Circle(center=Point(x=cx, y=cy), r=r) if r > 10:
            return f"big circle at {cx},{cy}"
        case Circle() as c:
            return f"circle {c}"
        case (int() | float()) as number:                       # type pattern
            return f"number {number}"
        case _:
            return "something else"

print(where(Point(0, 0)), "|", where(Point(5, 0)), "|", where(Point(2, 2)))
print(where(Circle(Point(1, 1), 20)), "|", where(Circle(Point(0, 1), 2)), "|", where(3.5))
```

Pattern kinds at a glance: **literal** (`"quit"`, `404`, `None`), **capture** (`x`), **wildcard** (`_`), **value** (`Color.RED`, dotted names), **sequence** (`[a, b, *rest]`), **mapping** (`{"k": v}`), **class** (`Point(x=0)`), **or** (`A | B`), **as** (`pattern as name`), plus **guards** (`if condition`).

Gotchas: a bare name in a pattern is a **capture** (it assigns!), not a comparison with a variable: use dotted names (`Color.RED`) or guards to compare. `match` falls through nothing: the first matching case wins.

```python
from enum import Enum
class Color(Enum):
    RED = 1
    GREEN = 2

def paint(color):
    match color:
        case Color.RED:                  # dotted name = compare to the value
            return "stop"
        case Color.GREEN:
            return "go"

print(paint(Color.RED), paint(Color.GREEN))                    # stop go
```

## 5. Exceptions: groups, notes and `except*` (3.11)

An **`ExceptionGroup`** bundles several unrelated exceptions (for example from concurrent tasks); `except*` handles the parts by type.

```python
def run_all():
    raise ExceptionGroup("batch failed", [ValueError("bad id"), TypeError("bad type"), ValueError("bad email")])

try:
    run_all()
except* ValueError as group:
    print("value errors:", [str(e) for e in group.exceptions])    # value errors: ['bad id', 'bad email']
except* TypeError as group:
    print("type errors:", [str(e) for e in group.exceptions])     # type errors: ['bad type']
```

Add context to an exception with **notes** instead of wrapping it:

```python
try:
    try:
        int("abc")
    except ValueError as e:
        e.add_note("while parsing the 'age' column, row 42")
        raise
except ValueError as e:
    print(e.__notes__)                                             # ["while parsing the 'age' column, row 42"]
```

(Exception design and logging are covered in [exceptions, logging and testing](../exceptions-logging-testing/README.md).)

## 6. Types and classes: modern syntax

```python
from typing import override

type Pair[T] = tuple[T, T]                                         # the `type` statement (3.12): a lazily evaluated alias
print(Pair.__value__)                                              # tuple[T, T]

class Animal:
    def speak(self) -> str:
        return "..."

class Dog(Animal):
    @override                                                      # the checker verifies this really overrides something
    def speak(self) -> str:
        return "woof"

print(Dog().speak())                                               # woof
```

Also: PEP 604 unions (`int | None`), built-in generics (`list[int]`), `def f[T](x: T) -> T` and `class Box[T]:` ([type hints](../typing-hints/README.md)), `dataclasses` with `slots=True` and `kw_only=True` ([dataclasses](../dataclasses-enums/README.md)), and in 3.14 **deferred evaluation of annotations** (forward references work without quotes; use `annotationlib.get_annotations`).

## 7. Standard-library upgrades worth knowing

```python
from pathlib import Path
import tomllib, json, tempfile

root = Path(tempfile.mkdtemp())
config_file = root / "app.toml"                                    # "/" joins paths
config_file.write_text('name = "demo"\nworkers = 4\n[db]\nurl = "sqlite://"\n')
config = tomllib.loads(config_file.read_text())                    # read TOML (3.11+), standard library
print(config["workers"], config["db"]["url"], config_file.suffix, config_file.stem)    # 4 sqlite:// .toml app

(root / "out").mkdir(exist_ok=True)
(root / "out" / "a.json").write_text(json.dumps({"ok": True}))
print([p.name for p in root.rglob("*.json")])                      # ['a.json']

from itertools import batched                                      # 3.12
print(list(batched("abcdefg", 3)))                                 # [('a', 'b', 'c'), ('d', 'e', 'f'), ('g',)]

from functools import cache, cached_property
from collections import Counter, defaultdict, deque, ChainMap
from zoneinfo import ZoneInfo                                      # time zones without third-party packages
import datetime
print(datetime.datetime(2026, 1, 1, 12, tzinfo=ZoneInfo("Asia/Karachi")).utcoffset())    # 5:00:00
```

- **`pathlib`** replaces most `os.path` string juggling.
- **`tomllib`** reads TOML (the format of `pyproject.toml`).
- **`zoneinfo`** is the standard time-zone database interface.
- **`secrets`** for tokens (not `random`), **`statistics`**, **`graphlib.TopologicalSorter`**, **`contextlib.suppress`**, **`argparse`**, **`logging`**, **`sqlite3`**, **`concurrent.futures`**, **`asyncio`**, **`dataclasses`** are all batteries included.
- **3.14:** `compression.zstd` (Zstandard compression in the standard library), `concurrent.futures.InterpreterPoolExecutor`, improved `asyncio` introspection.

## 8. Performance and runtime changes (3.11 to 3.14)

- **3.11** made CPython roughly 10-60% faster (adaptive specializing interpreter, cheaper frames).
- **3.13** introduced **experimental builds**: a **free-threaded** build without the GIL (`python3.13t`) and an experimental **JIT**.
- **3.14** made free-threaded support officially supported (but optional), added **multiple interpreters in the standard library** (`concurrent.interpreters`, `InterpreterPoolExecutor`) and deferred annotations.
- Check at runtime: `sys._is_gil_enabled()`; do not assume it is `False`.

```python
import sys
print(sys.version_info >= (3, 12), "GIL enabled:", sys._is_gil_enabled())
```

Practical advice: target the **oldest supported version** your users have, declare it in `pyproject.toml` (`requires-python = ">=3.10"`), test on several versions, and adopt new syntax once your minimum version supports it.

## 9. Two real-world examples

### Example 1: A command parser with `match`
A chat-bot or CLI receives text commands (`"move north"`, `"take lamp"`, `"quit"`) and JSON events from a server. A `match` statement with sequence and mapping patterns replaces 40 lines of `if/elif` with `.startswith`, `.split` and key checks, and the guards and class patterns document each case. Adding a command is one new `case`.

### Example 2: Safe templating with t-strings
A web app builds HTML snippets and SQL queries. With f-strings, a username like `<script>` or `'; DROP TABLE` can slip into the output. With t-strings a small `render_html` or `to_sql(template)` function receives the literal text and each value separately: it HTML-escapes values or turns them into query parameters. The call site stays as readable as an f-string, but the dangerous mistake becomes impossible by construction.

## 10. Tips, tricks and pitfalls

- Use f-strings for most formatting; never build SQL, HTML or shell commands with f-strings from user input.
- In `match`, a bare name **captures**; compare to constants via dotted names (`Color.RED`) or guards.
- `case _:` is the default; without it, an unmatched value silently falls out of the `match`.
- Use `zip(strict=True)` when lengths must match.
- The walrus operator is for avoiding repetition in conditions and comprehensions; do not hide important assignments in it.
- Positional-only `/` and keyword-only `*` are API-design tools: use them to keep your public functions stable and readable.
- `except*` is for exception groups (concurrency); ordinary `except` is still right for single exceptions.
- Do not use new syntax in libraries whose users run older Python: check `requires-python`.
- Prefer `pathlib.Path` to string concatenation for paths; prefer `secrets` over `random` for security.
- Read release notes (`What's New in Python 3.x`) once a year; the language moves fast.

## 11. Check yourself

1. What does `f"{x=}"` print and why is it useful?
2. What do `/` and `*` in a function signature mean?
3. Show a `match` that destructures a dict, a list and a dataclass.
4. Why does `case RED:` (bare name) not compare to a constant?
5. What is an `ExceptionGroup` and when do you use `except*`?
6. How is a t-string different from an f-string, and what is it for?
7. Which module reads TOML? Which handles time zones?
8. What is `sys.version_info >= (3, 12)` used for?

<details>
<summary>Answers</summary>

1. `x=42`: the expression text and its value, handy for quick debugging (3.8+).
2. Parameters before `/` are positional-only; parameters after `*` are keyword-only.
3. `case {"type": "circle", "r": r}:`, `case [first, *rest]:`, `case Point(x=0, y=y):` (patterns bind variables for the parts).
4. A bare name in a pattern is a capture pattern that always matches and assigns; use dotted names (`Color.RED`) or a guard to compare.
5. An `ExceptionGroup` bundles several exceptions (for example from concurrent tasks); `except*` handles members by type, possibly several handlers for one group.
6. A t-string produces a `Template` object keeping literal text and interpolated values separate, so a function can escape or parameterize values safely; an f-string immediately merges everything into one string.
7. `tomllib` (3.11+); `zoneinfo`.
8. Feature-gating code or tooling on the running Python version.

</details>

[Exercises](exercises.md) · [Summary](summary.md)
