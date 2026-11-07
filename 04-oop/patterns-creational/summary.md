# Creational Patterns: One-Page Summary

- **Patterns** = named solutions with intent and trade-offs; GoF families: creational, structural, behavioral. In Python many shrink (modules, functions, decorators, duck typing). Use only when the problem is real.
- **Singleton:** one instance. Pythonic: a **module**; otherwise `__new__` with a lock (guard `__init__`). Cons: global state, hard tests. Prefer **create once and inject**.
- **Factory (simple / Method):** centralize "which class". Registry + `__init_subclass__` makes it open for extension. Examples: `open()`, `logging.getLogger`, `Path.home()`.
- **Abstract Factory:** families of related objects used consistently (themes, vendor SDKs, DB drivers).
- **Builder:** stepwise construction, fluent API, validate in `build()`, immutable result. Often replaced by kwargs/dataclasses unless complex.
- **Prototype:** clone and tweak: `copy.deepcopy`, `dataclasses.replace` (shallow!). Watch shared nested data.
- **Object Pool:** reuse expensive resources; always return them (context manager), bound size, handle exhaustion.
- **Choose:** one instance -> module/DI; pick class -> factory/registry; families -> abstract factory; complex construction -> builder; clone -> prototype; costly resources -> pool.

[Lesson](README.md) · [Exercises](exercises.md)
