# Composition, Delegation, Coupling and Object Design: One-Page Summary

## Key facts

- **Composition** (has-a) over inheritance (is-a): looser coupling, runtime swapping, small focused classes, narrow exposed API, no class explosion (2 + N, not 2 x N).
- **Delegation:** forward calls to a held object; `__getattr__` forwards unknown names but **not dunders** (define those).
- **Relationships:** dependency, association, aggregation (parts independent), composition (parts owned), inheritance.
- **Cohesion high, coupling low.** Coupling ladder: content > common > control > stamp > data > message. Law of Demeter.
- **Dependency injection:** receive collaborators (constructor injection), wire everything in a **composition root**; pass fakes in tests; inject functions like `clock`.
- **Domain vocabulary:** value object (immutable, equality by value, validate once), entity (identity), aggregate root (single entry point protecting invariants).
- **Design steps:** nouns/verbs, CRC responsibilities, relationships, invariants in the owner.
- **Smells:** god class, feature envy, primitive obsession, long parameter list, shotgun surgery, switch on type, refused bequest. Refactor in small tested steps.
- **Testing:** fakes > stubs > mocks; test behavior via the public interface.

## Pitfalls

- Delegating with `__getattr__` and forgetting that special methods are not forwarded.
- Creating collaborators inside a class, which makes it hard to test.
- God classes, and long chains of calls that break the Law of Demeter.
- Over-mocking: testing which calls were made instead of what the behaviour is.
- Replacing inheritance mechanically when the relationship really is is-a.

[Lesson](README.md) · [Exercises](exercises.md)
