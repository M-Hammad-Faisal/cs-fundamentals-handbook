# Python Fundamentals: One-Page Summary

## Key facts

- **Types:** `int`, `float`, `str`, `bool`, `None`, `list`, `tuple`, `dict`, `set`. Mutable: `list`, `dict`, `set`. Immutable: numbers, `str`, `tuple`.
- **Falsy values:** `False`, `None`, `0`, `0.0`, `""`, `[]`, `{}`, `()`, `set()`; everything else is truthy.
- **Operators:** `/` true division, `//` floor division, `%` remainder, `**` power; `==` compares values, `is` compares identity; comparisons chain (`0 < x < 10`).
- **Control flow:** indentation defines blocks; `for x in iterable`, `while cond`, `break`, `continue`; `range(start, stop, step)` excludes `stop`; `enumerate` gives index and item, `zip` walks sequences together.
- **Functions:** positional, keyword and default arguments, `*args`, `**kwargs`; a function with no `return` returns `None`; name lookup order is Local, Enclosing, Global, Built-in; functions are values you can pass around.
- **Collections:** list is ordered (append `O(1)`, membership `O(n)`); dict and set give average `O(1)` lookup; tuple is a fixed record; `a[i:j:k]` slices into a new list; `[f(x) for x in xs if cond]` is a comprehension.
- **Files and errors:** `with open(path, encoding="utf-8") as f`; `try / except SomeError / else / finally`; `raise`; read a traceback from the bottom up.
- **Debug and test:** reproduce, isolate, form a hypothesis, fix, add a test; `assert` and pytest functions named `test_*`.
- **Classes:** `__init__` sets up an object, `self` is the instance, `__repr__` is for developers, `__str__` is for users.

## Pitfalls

- Mutable default argument: `def f(x=[])` shares one list across calls; use `None`.
- `input()` always returns a string; convert before doing arithmetic.
- Changing a list while looping over it; off-by-one with `range` and slices.
- `=` (assign) versus `==` (compare); a bare `except:` that hides real bugs.
- Naming a variable `list`, `sum`, `id` or `type` and shadowing the built-in; naming your file `random.py` or `json.py`.

## Self-check

- **What is a variable in Python?** A name that refers to a value (object) in memory.
- **Name five basic types.** `int`, `float`, `str`, `bool`, `NoneType` (plus `list`, `dict`, `tuple`, `set`).
- **Difference between `/`, `//` and `%`?** `/` true division (float), `//` floor division, `%` remainder.
- **What does `input()` return?** A string, always.
- **What is the difference between `=` and `==`?** `=` assigns a value to a name; `==` compares two values for equality.
- **What are the falsy values?** `False`, `None`, `0`, `0.0`, `""`, `[]`, `{}`, `()`, `set()`.
- **How does Python know which lines belong to an `if` block?** By the colon and the indentation (4 spaces) of the following lines.
- **What does `range(2, 10, 3)` produce?** `2, 5, 8`.
- **When use `for` and when `while`?** `for` to iterate over a collection or a known count; `while` to repeat until a condition changes.
- **What do `break` and `continue` do?** `break` exits the loop; `continue` skips to the next iteration.
- **How many times does the body of two nested loops over 10 and 20 items run?** 10 x 20 = 200.
- **What is the accumulator pattern?** Start with an initial value (0, `[]`, ...) and update it in each iteration to build a total, count or collection.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Variables, Types and Operators](01-variables-types-operators.md) · [Making Decisions and Repeating Things](02-control-flow.md) · [Functions](03-functions.md) · [Strings, Lists, Tuples, Dictionaries and Sets](04-strings-lists-dicts-sets.md) · [Files, Modules and Handling Errors](05-files-modules-errors.md) · [Debugging and Testing Your Code](06-debugging-and-testing.md) · [Classes and Objects, a First Look](07-classes-first-look.md)
