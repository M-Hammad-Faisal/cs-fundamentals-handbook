# Classes and Objects in Depth: One-Page Summary

## Key facts

- **Everything is an object** with identity (`id`, `is`), type (`type`) and value (`==`). Names are references; assignment never copies.
- **Class parts:** `__init__`, instance attributes (`self.x`), class attributes (shared), **instance / class / static methods** (`self`, `cls`, none). `@classmethod` constructors work with subclasses.
- **Attribute lookup:** instance `__dict__`, then class, then bases. Assigning via an instance shadows, never edits, the class attribute.
- **Lifecycle:** `__new__` creates, `__init__` initializes, refcount + cycle GC frees; use `with`, not `__del__`. `weakref` for non-owning references.
- **`__slots__`** drops the per-instance dict (less memory, no dynamic attributes). `__getattr__` = fallback; `__getattribute__` = every access.
- **Equality:** define `__eq__` (return `NotImplemented` for foreign types) and `__hash__` together; only immutable objects should be hashable.
- **Copies:** shallow shares inner objects; `deepcopy` clones them.
- **`__repr__`** for developers (always define); **`__str__`** for users.

## Pitfalls

- Mutable default arguments and mutable class attributes are shared by every instance.
- Defining `__eq__` without `__hash__`, or hashing objects that change.
- Using `is` for value comparison; relying on `__del__` for cleanup.
- A shallow copy shares inner objects: use `deepcopy` when they must be independent.
- Assigning through an instance when you meant to change the class attribute (it shadows instead).
- Also: mutable default arguments, mutable class attributes, `is` vs `==`, relying on `__del__`.

[Lesson](README.md) · [Exercises](exercises.md)
