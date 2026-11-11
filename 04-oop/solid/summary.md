# SOLID Principles and Other Design Principles: One-Page Summary

## Key facts

| | Principle | Smell | Fix |
|--|-----------|-------|-----|
| **S** | One reason to change per class | "And"/"Manager" classes, tests needing DB + files + clock | Split by axis of change |
| **O** | Extend by adding code, not editing | Growing `if/elif` on type | Polymorphism, registry, strategies |
| **L** | Subtypes substitute for base types (keep preconditions, postconditions, invariants) | Subclass raises `NotImplementedError`, `Square(Rectangle)` | Narrower base, composition, immutable shapes |
| **I** | Small, role-based interfaces | Stub methods in implementations | Split interfaces / `Protocol`s; pass only what's needed |
| **D** | Depend on abstractions; details depend on them | `self.db = MySql()` inside services | Abstraction owned by the high-level code + injection |

- **Fit together:** SRP/ISP shrink units; OCP/DIP extend via abstractions; LSP keeps implementations interchangeable.
- **DIP vs DI vs IoC container:** principle vs technique vs tooling. Architecture result: ports and adapters.
- **Also:** DRY (knowledge, not text), KISS, YAGNI, Law of Demeter, tell-don't-ask, separation of concerns, fail fast, composition over inheritance.
- **Pragmatism:** rule of three; apply where change happens; avoid interface-for-everything and tiny-class sprawl.

## Pitfalls

- Treating SOLID as dogma: an interface for a single implementation, or "one method per class".
- Reading the Single Responsibility Principle as "does one thing" instead of "has one reason to change".
- Substitutability breaks: a subclass that tightens inputs or raises new errors.
- Fat interfaces, and dependency-injection frameworks that hide how the program is wired.
- Open/closed achieved with inheritance ladders when a strategy object would be simpler.

[Lesson](README.md) · [Exercises](exercises.md)
