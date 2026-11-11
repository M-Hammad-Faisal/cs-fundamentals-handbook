# Rapid-Fire Python and CS Questions: One-Page Summary

## Key facts

**Answer shape:** definition (1 sentence) > how/why > example or trade-off. Stop; invite follow-ups. Never bluff.

**Python must-knows:** mutable default args (use `None`); `is` (identity) vs `==` (value); shallow vs deep copy; late-binding closures; LEGB scope, `global`/`nonlocal`; tuples immutable but contents may not be (`t[1] += [x]` mutates then fails); `1 == 1.0 == True` as dict keys; dict order guaranteed; stable sort; `//` floors, `round` ties to even, floats vs `Decimal`; `*args/**kwargs`; generators lazy and single-use; class-level mutable attributes are shared; `__eq__` without `__hash__` = unhashable; `finally` always runs; loop `else` runs without `break`.

**Concepts:** GIL (I/O threads OK, CPU needs processes), threads vs processes vs asyncio, refcount + cycle GC, decorators, MRO/`super()`, `__new__` vs `__init__`, `@staticmethod/@classmethod`, context managers, dataclasses, type hints are not runtime-enforced.

**CS:** process vs thread; deadlock (4 conditions, lock ordering); virtual memory; TCP vs UDP; HTTP codes/idempotency; HTTPS (TLS handshake); **URL-to-page walkthrough** (parse, DNS, TCP, TLS, HTTP, server layers, render); ACID; indexes; joins; normalization; CAP; hash tables; quick vs merge sort; SOLID; common patterns.

**Practice:** explain one concept per day out loud in under 45 seconds, link it to a project you built.

## Pitfalls

- Mutable default arguments; late-binding closures; `is` used for value comparison.
- An assignment anywhere in a function makes that name local, so reading it earlier raises `UnboundLocalError`.
- Changing a list while iterating over it; shallow versus deep copy.
- `x in list` is `O(n)` but `x in set` is `O(1)` on average; `s += part` in a loop is quadratic.
- Floats compared with `==`; `/` versus `//`.

[Lesson](README.md) · [Exercises](exercises.md)
