# Modern Python Language Features: Exercises

These problems go with the [Modern Python Language Features lesson](README.md). Try each one before opening its solution.

## Problems

1. Format a price list so that names are left-aligned in 10 columns and prices right-aligned with 2 decimals and thousands separators, using one f-string per row.
2. Write `connect(host, port=5432, /, *, timeout=5, ssl=True)` and show which calls are valid or invalid.
3. Use `match` to implement `evaluate(expr)` for tuples like `("add", 2, 3)`, `("neg", 5)`, `("mul", ("add", 1, 2), 4)`.
4. Use `match` with a dataclass hierarchy `Click(x, y)`, `Key(char)`, `Scroll(dy)` to produce a description of each event, with a guard for far-right clicks.
5. Rewrite this with the walrus operator and explain the benefit:
   ```python no-run
   # a question snippet (not complete code)
   m = pattern.search(text)
   if m:
       print(m.group(1))
   ```
6. Use `zip(strict=True)` to detect mismatched header/row lengths when building dicts from CSV-like rows.
7. Raise an `ExceptionGroup` from a function validating several fields and handle `ValueError`s and `TypeError`s separately with `except*`.
8. Add a note with `add_note` to an exception and print it when caught.
9. Write `render_sql(template)` for a t-string that returns `(query, params)` replacing each interpolation by `?`. Show it with a hostile value.
10. Using `pathlib` and `tomllib`, write a function that reads `pyproject.toml`-like text from a temp file and returns the `requires-python` value.

<details>
<summary>Solutions</summary>

**1.**
```python
items = [("coffee", 1234.5), ("tea", 99.999), ("cake", 1500000)]
for name, price in items:
    print(f"{name:<10}{price:>14,.2f}")
```

**2.**
```python
def connect(host, port=5432, /, *, timeout=5, ssl=True):
    return host, port, timeout, ssl

print(connect("db"), connect("db", 6000, timeout=1))        # valid
for bad in (lambda: connect("db", port=1), lambda: connect("db", 1, 2)):
    try:
        bad()
    except TypeError as e:
        print("TypeError:", e)
```

**3.**
```python
def evaluate(expr):
    match expr:
        case int() | float():
            return expr
        case ("add", a, b):
            return evaluate(a) + evaluate(b)
        case ("mul", a, b):
            return evaluate(a) * evaluate(b)
        case ("neg", a):
            return -evaluate(a)
        case _:
            raise ValueError(f"bad expression: {expr!r}")

print(evaluate(("mul", ("add", 1, 2), 4)), evaluate(("neg", 5)))     # 12 -5
```

**4.**
```python
from dataclasses import dataclass

@dataclass
class Click: x: int; y: int
@dataclass
class Key: char: str
@dataclass
class Scroll: dy: int

def describe(event):
    match event:
        case Click(x=x, y=y) if x > 1000:
            return f"far-right click at {x},{y}"
        case Click(x, y):
            return f"click at {x},{y}"
        case Key(char="\n"):
            return "enter pressed"
        case Key(c):
            return f"key {c!r}"
        case Scroll(dy) if dy < 0:
            return "scroll up"
        case Scroll():
            return "scroll down"

print([describe(e) for e in (Click(5, 6), Click(1500, 2), Key("a"), Key("\n"), Scroll(-3), Scroll(2))])
```

**5.**
```python
import re
pattern, text = re.compile(r"id=(\d+)"), "user id=42"
if m := pattern.search(text):
    print(m.group(1))                                       # 42
```
The search result is assigned and tested in one step; no extra line and no stale variable.

**6.**
```python
header = ["id", "name", "age"]
rows = [[1, "ana", 30], [2, "bo"]]
for row in rows:
    try:
        print(dict(zip(header, row, strict=True)))
    except ValueError as e:
        print("bad row:", row, "-", e)
```

**7.**
```python
def validate(data):
    errors = []
    if not isinstance(data.get("age"), int):
        errors.append(TypeError("age must be int"))
    if not data.get("name"):
        errors.append(ValueError("name required"))
    if "@" not in data.get("email", ""):
        errors.append(ValueError("invalid email"))
    if errors:
        raise ExceptionGroup("validation failed", errors)

try:
    validate({"age": "x", "email": "nope"})
except* ValueError as g:
    print("value:", [str(e) for e in g.exceptions])
except* TypeError as g:
    print("type:", [str(e) for e in g.exceptions])
```

**8.**
```python
try:
    try:
        int("x")
    except ValueError as e:
        e.add_note("while reading row 7")
        raise
except ValueError as e:
    print(e, e.__notes__)
```

**9.**
```python
from string.templatelib import Template, Interpolation

def render_sql(template: Template):
    query, params = [], []
    for item in template:
        if isinstance(item, Interpolation):
            query.append("?")
            params.append(item.value)
        else:
            query.append(item)
    return "".join(query), params

evil = "x'; DROP TABLE users; --"
print(render_sql(t"SELECT * FROM users WHERE name = {evil} AND age > {18}"))
# ("SELECT * FROM users WHERE name = ? AND age > ?", ["x'; DROP TABLE users; --", 18])
```
The hostile text travels as a parameter, never as SQL.

**10.**
```python
import tempfile, tomllib
from pathlib import Path

def requires_python(path: Path) -> str | None:
    data = tomllib.loads(path.read_text())
    return data.get("project", {}).get("requires-python")

f = Path(tempfile.mkdtemp()) / "pyproject.toml"
f.write_text('[project]\nname = "demo"\nrequires-python = ">=3.10"\n')
print(requires_python(f))                                   # >=3.10
```

</details>

[Lesson](README.md) · [Summary](summary.md)
