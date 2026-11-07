# Composition and Object Design: One-Page Summary

- **Composition** (has-a) over inheritance (is-a): looser coupling, runtime swapping, small focused classes, narrow exposed API, no class explosion (2 + N, not 2 x N).
- **Delegation:** forward calls to a held object; `__getattr__` forwards unknown names but **not dunders** (define those).
- **Relationships:** dependency, association, aggregation (parts independent), composition (parts owned), inheritance.
- **Cohesion high, coupling low.** Coupling ladder: content > common > control > stamp > data > message. Law of Demeter.
- **Dependency injection:** receive collaborators (constructor injection), wire everything in a **composition root**; pass fakes in tests; inject functions like `clock`.
- **Domain vocabulary:** value object (immutable, equality by value, validate once), entity (identity), aggregate root (single entry point protecting invariants).
- **Design steps:** nouns/verbs, CRC responsibilities, relationships, invariants in the owner.
- **Smells:** god class, feature envy, primitive obsession, long parameter list, shotgun surgery, switch on type, refused bequest. Refactor in small tested steps.
- **Testing:** fakes > stubs > mocks; test behavior via the public interface.

[Lesson](README.md) · [Exercises](exercises.md)
