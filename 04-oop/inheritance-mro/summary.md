# Inheritance and MRO: One-Page Summary

- **Inheritance** = is-a: reuse + specialization. Subclass can **extend**, **override**, or **override and call `super()`**. Two purposes: subtyping (strong) and code reuse (often better as composition).
- **Five types:** single, multilevel (chain), hierarchical (one parent many children), multiple (many parents), hybrid (e.g. diamond).
- **MRO:** `Cls.__mro__`; C3 linearization keeps children before parents, preserves base order, lists each class once. Impossible orders raise `TypeError`.
- **`super()`** = next class in the MRO (not "the parent"); enables **cooperative multiple inheritance**: every method calls `super()`, forward `**kwargs`, end the chain in a base class.
- **Mixins:** small single-capability classes; place before the main base; no instantiation on their own.
- **Patterns in inheritance:** template method (fixed algorithm, overridable steps), `__init_subclass__` registries, exception hierarchies.
- **Built-ins:** subclass `UserDict`/`UserList`/`collections.abc`, not `dict`/`list`, to change behavior.
- **Problems:** fragile base class, deep trees, Liskov violations (Square/Rectangle), inheriting only for reuse (`Stack(list)`).
- **Rule:** favor composition; inherit for true is-a with a stable base and polymorphism.

[Lesson](README.md) · [Exercises](exercises.md)
