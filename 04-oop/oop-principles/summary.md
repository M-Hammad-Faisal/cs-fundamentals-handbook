# OOP Principles: One-Page Summary

## Four pillars
| Pillar | One line | Python tool |
|--------|----------|-------------|
| Encapsulation | Hide data, expose a small interface | `_name`, `@property` |
| Abstraction | Show what, hide how | `ABC`, `@abstractmethod`, `Protocol` |
| Inheritance | Reuse through "is-a" | `class Child(Parent)`, `super()` |
| Polymorphism | One interface, many behaviors | Overriding, duck typing, dunder methods |

## Inheritance types
Single · Multilevel · Hierarchical · Multiple · Hybrid (diamond)

- Python resolves multiple inheritance with the **MRO** (C3 linearization). Inspect with `Cls.__mro__`.
- `super()` follows the MRO, not just "the parent".
- **Mixins**: small single-purpose classes added through multiple inheritance.
- **Composition over inheritance** unless the relationship is a true "is-a".

## Method kinds
- Instance method gets `self`. Class method gets `cls` (alternative constructors). Static method gets neither. Property exposes computed values.

## SOLID
- **S**: one reason to change.
- **O**: extend by adding code, not editing it.
- **L**: subclasses must be safely substitutable.
- **I**: small focused interfaces.
- **D**: depend on abstractions; inject dependencies.

## Pitfalls
- Mutable default arguments are shared across calls.
- Forgetting `super().__init__()`.
- Class attributes holding mutable values are shared by all instances.
- `__eq__` without `__hash__` makes objects unhashable.
- Deep hierarchies and over-abstraction.

## Design vocabulary
High **cohesion**, low **coupling**. Patterns: Factory, Singleton, Strategy, Observer, Decorator, Adapter, Builder, Repository.

[Full chapter](README.md) · [Exercises](exercises.md)
