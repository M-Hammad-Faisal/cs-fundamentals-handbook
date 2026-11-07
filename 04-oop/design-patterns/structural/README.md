# Structural Patterns

**Question they answer:** *How do I put objects together into bigger structures, or make mismatched parts fit, while keeping everything flexible?*

Most of these patterns are different ways of **putting one object in front of another** (wrapping). The trick to telling them apart is the **intent**, not the shape.

| Pattern | One-line idea | Use it when | Lesson |
|---------|---------------|-------------|--------|
| **Adapter** | Translate one interface into another | A library or legacy class does not match what you expect | [adapter.md](adapter.md) |
| **Decorator** | Add behavior, same interface | Stackable features (logging, caching, retry) | [decorator.md](decorator.md) |
| **Proxy** | Stand-in that controls access | Lazy loading, caching, permissions, remote calls | [proxy.md](proxy.md) |
| **Facade** | One simple front for a complex subsystem | Hide many steps behind one call | [facade.md](facade.md) |
| **Composite** | Treat one item and a group the same | Trees: files, menus, DOM | [composite.md](composite.md) |
| **Bridge** | Separate abstraction from implementation | Two independent dimensions of variation | [bridge.md](bridge.md) |
| **Flyweight** | Share common immutable data | Huge numbers of similar objects | [flyweight.md](flyweight.md) |

## How to tell the look-alikes apart

| | Wraps | Interface | Intent |
|--|-------|-----------|--------|
| **Adapter** | one object | **changes** it | make incompatible things fit |
| **Decorator** | one object | **same** | add features |
| **Proxy** | one object | **same** | control access |
| **Facade** | many objects | **new, simpler** | simplify |
| **Bridge** | holds an implementation | two hierarchies | vary independently |
| **Composite** | many children, same type | **same** for leaf and group | uniform trees |

## Cheat sheet

- **Mismatch?** Adapter (prefer composition over inheriting from the adaptee).
- **Extra behavior?** Decorator (`functools.wraps`, mind the stacking order).
- **Lazy/guarded/cached/remote?** Proxy.
- **Too many steps to call?** Facade (keep it thin; do not hide the subsystem completely).
- **Tree?** Composite (`__iter__` + recursion).
- **M x N classes?** Bridge (M + N).
- **Millions of copies?** Flyweight (shared data must be immutable; measure first).

## Family practice (mixed)

1. Name the pattern: (a) `functools.lru_cache`, (b) `io.TextIOWrapper`, (c) `shutil.copytree`, (d) a lazy-loaded image placeholder, (e) a folder containing files and folders, (f) interned strings.
2. How do Decorator and Proxy differ if they look identical in code?

<details>
<summary>Answers</summary>

1. (a) Decorator, (b) Adapter, (c) Facade, (d) Proxy (virtual), (e) Composite, (f) Flyweight.
2. A decorator adds features the caller chooses to stack; a proxy controls access to the object (lazy, protected, cached, remote) and often manages its lifecycle.

</details>

[Creational patterns](../creational/README.md) · [All patterns](../README.md) · [Behavioral patterns](../behavioral/README.md)
