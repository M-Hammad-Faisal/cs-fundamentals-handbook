# Structural Patterns: One-Page Summary

| Pattern | Intent | Python / real example |
|---------|--------|-----------------------|
| **Adapter** | Translate an incompatible interface | `io.TextIOWrapper`, vendor wrappers, anti-corruption layer |
| **Decorator** | Add behavior, same interface | `@decorator` syntax, `lru_cache`, `wraps`, stacked notifiers |
| **Proxy** | Control access (lazy, protect, cache, remote) | lazy image, `weakref.proxy`, `__getattr__` forwarding |
| **Facade** | Simple front for a complex subsystem | `requests.get`, `shutil.copytree` |
| **Composite** | Uniform leaves and groups in a tree | file systems, DOM, menus, `size()` recursion |
| **Bridge** | Two independent hierarchies (M + N, not M x N) | shape x renderer, logger x handler |
| **Flyweight** | Share immutable intrinsic state across many objects | interned strings, small ints, `__slots__`, style caches |

- Tell them apart by **intent**, not shape (Decorator and Proxy are structurally the same).
- Use `functools.wraps`; a decorator with arguments is a factory returning a decorator; stacking order matters.
- Prefer **object** adapters; forward dunders explicitly in dynamic proxies; keep facades thin; keep flyweights immutable.

[Lesson](README.md) · [Exercises](exercises.md)
