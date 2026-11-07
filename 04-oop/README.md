# Object-oriented design

A seven-part path from the basics of classes to design patterns. Read in order the first time.

| # | Topic | Lesson |
|---|-------|--------|
| 1 | Classes and objects in depth | [lesson](classes-objects/README.md) · [exercises](classes-objects/exercises.md) · [summary](classes-objects/summary.md) |
| 2 | Encapsulation and abstraction | [lesson](encapsulation-abstraction/README.md) · [exercises](encapsulation-abstraction/exercises.md) · [summary](encapsulation-abstraction/summary.md) |
| 3 | Inheritance, MRO and multiple inheritance | [lesson](inheritance-mro/README.md) · [exercises](inheritance-mro/exercises.md) · [summary](inheritance-mro/summary.md) |
| 4 | Polymorphism and the Python data model (dunder methods) | [lesson](polymorphism-dunder/README.md) · [exercises](polymorphism-dunder/exercises.md) · [summary](polymorphism-dunder/summary.md) |
| 5 | Composition, delegation, coupling and object design | [lesson](composition-design/README.md) · [exercises](composition-design/exercises.md) · [summary](composition-design/summary.md) |
| 6 | SOLID and other design principles | [lesson](solid/README.md) · [exercises](solid/exercises.md) · [summary](solid/summary.md) |
| 7 | Design patterns (25 patterns, one detailed file each) | [guide and glossary](design-patterns/README.md) · [creational](design-patterns/creational/README.md) · [structural](design-patterns/structural/README.md) · [behavioral](design-patterns/behavioral/README.md) |

## Learning path

1. **Classes and objects** (identity, attributes, methods, lifecycle, `__slots__`, equality and copying).
2. **Encapsulation and abstraction** (access conventions, properties, descriptors, ABCs, protocols).
3. **Inheritance** (five types, MRO and C3, `super()`, cooperative multiple inheritance, mixins).
4. **Polymorphism and the data model** (dynamic dispatch, duck typing, operator overloading, containers, context managers, iterators).
5. **Composition and design** (delegation, dependency injection, coupling and cohesion, value objects, smells, testing).
6. **SOLID** (violation, symptoms and refactoring for each principle, plus DRY, KISS, YAGNI).
7. **Design patterns**: start with the [plain-English guide](design-patterns/README.md) (what a pattern is, what "GoF" means, a glossary, a "which pattern do I need?" chooser). Then one detailed file per pattern:
   - [Creational](design-patterns/creational/README.md): Singleton, Factory Method, Abstract Factory, Builder, Prototype, Object Pool.
   - [Structural](design-patterns/structural/README.md): Adapter, Decorator, Proxy, Facade, Composite, Bridge, Flyweight.
   - [Behavioral](design-patterns/behavioral/README.md): Strategy, Observer, Command, State, Template Method, Iterator, Chain of Responsibility, Mediator, Memento, Visitor, Interpreter, Null Object.

   Runnable scripts for every pattern live in the companion repository [design-patterns-python](https://github.com/M-Hammad-Faisal/design-patterns-python).

Related: [dataclasses, typing and Protocols](../08-modern-python/README.md) for the modern Python tools that make much of this lighter.

Back to the [index](../INDEX.md).
