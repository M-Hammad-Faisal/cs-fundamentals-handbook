# Design Patterns: A Plain-English Guide

If words like "GoF", "creational" or "Liskov" sound like jargon, start here. This page explains the vocabulary first, then every pattern has **its own detailed file**.

## 1. What is a design pattern?

A **design pattern** is a **named, proven way to solve a problem that keeps showing up** when you design software. It is not a library you install or code you copy. It is an *idea* with a name, like a recipe: "when you need X and you are worried about Y, arrange your classes like this".

Everyday analogy: builders know that a **doorway needs a lintel** above it to carry the wall. Nobody reinvents that; they say "put a lintel" and everybody understands. Patterns give programmers that shared shorthand: "use a **factory** here", "make that an **observer**".

Why learn them:

- **Shared vocabulary.** "Wrap it in a decorator" replaces a ten-minute explanation.
- **Proven trade-offs.** Each pattern lists when it helps and when it hurts.
- **You will meet them anyway.** Django, `logging`, `requests`, React and every large codebase use them.
- **Interviews** ask about them.

What patterns are **not**: rules to apply everywhere. Using a pattern where a plain function would do is over-engineering. In Python many patterns become tiny (a module, a function, a decorator) because the language is flexible. Each file shows both the classic version and the Pythonic shortcut.

## 2. What does "GoF" mean?

**GoF = Gang of Four.** It is the nickname of four authors (Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides) who in **1994** published the book *Design Patterns: Elements of Reusable Object-Oriented Software*. It collected **23 patterns** that experienced developers were already using, gave them names and described them in a fixed format. People say "the GoF patterns" to mean **those 23 classic patterns**. That is all it means. You do not need the book to follow this guide.

The authors sorted the 23 patterns into **three families** by the kind of problem they solve:

| Family | Plain-English question it answers | Patterns |
|--------|-----------------------------------|----------|
| **Creational** | "How do I **create** objects without hard-wiring which class I build?" | [Singleton](creational/singleton.md), [Factory Method](creational/factory-method.md), [Abstract Factory](creational/abstract-factory.md), [Builder](creational/builder.md), [Prototype](creational/prototype.md) (+ [Object Pool](creational/object-pool.md), not in GoF) |
| **Structural** | "How do I **put objects together** into bigger structures, or make mismatched parts fit?" | [Adapter](structural/adapter.md), [Decorator](structural/decorator.md), [Proxy](structural/proxy.md), [Facade](structural/facade.md), [Composite](structural/composite.md), [Bridge](structural/bridge.md), [Flyweight](structural/flyweight.md) |
| **Behavioral** | "How do objects **talk to each other** and share the work?" | [Strategy](behavioral/strategy.md), [Observer](behavioral/observer.md), [Command](behavioral/command.md), [State](behavioral/state.md), [Template Method](behavioral/template-method.md), [Iterator](behavioral/iterator.md), [Chain of Responsibility](behavioral/chain-of-responsibility.md), [Mediator](behavioral/mediator.md), [Memento](behavioral/memento.md), [Visitor](behavioral/visitor.md), [Interpreter](behavioral/interpreter.md) (+ [Null Object](behavioral/null-object.md), not in GoF) |

5 + 7 + 11 = the 23 GoF patterns. Object Pool and Null Object are widely used extras, included here because you will meet them.

## 3. A glossary of the words used in these files

| Term | Meaning in plain English |
|------|--------------------------|
| **Class / object** | A class is a blueprint; an object is one thing built from it. |
| **Interface** | The list of things you can *ask* an object to do (its methods), without caring how. |
| **Abstraction** | Working with the "what" (an interface) and ignoring the "how" (the details). |
| **Abstract class** | A class that cannot be created directly; it exists to define what its children must provide. |
| **Concrete class** | A normal, complete class you can create. |
| **Client** | The code that *uses* the pattern's objects. |
| **Polymorphism** | Different objects respond to the same call in their own way (`shape.area()` works for circles and squares). |
| **Inheritance** | A class reusing and specializing another ("is-a"). |
| **Composition** | An object holding other objects and using them ("has-a"). |
| **Delegation** | Passing a request on to another object to do the work. |
| **Coupling** | How much one piece of code depends on another. Low coupling is good: you can change one without breaking the other. |
| **Cohesion** | How well the parts inside one class belong together. High cohesion is good. |
| **Dependency injection** | Handing an object the things it needs, instead of letting it build them itself. |
| **Encapsulation** | Hiding internal details behind a clean interface. |
| **Instantiate** | Create an object from a class (`Car()` instantiates `Car`). |
| **Refactor** | Reorganize code without changing what it does. |
| **SOLID** | Five design guidelines; see [SOLID](../solid/README.md). Patterns are often *how* you follow them. |

If a term still feels fuzzy, the earlier OOP chapters explain it with code: [classes](../classes-objects/README.md), [inheritance](../inheritance-mro/README.md), [polymorphism](../polymorphism-dunder/README.md), [composition](../composition-design/README.md).

## 4. How every pattern file is organized

Each pattern has one file with the same sections, so you can learn them quickly and revise them later:

1. **In plain words**: what it is, with an everyday analogy.
2. **The problem**: code that hurts without the pattern.
3. **The solution**: the idea, the roles and a diagram.
4. **Step by step**: a complete, runnable implementation.
5. **The Pythonic way**: shortcuts the language gives you.
6. **When to use it (and when not to)**.
7. **Pros and cons**, **related patterns**.
8. **Two real-world examples**.
9. **Practice**: exercises with solutions.
10. **Check yourself**: questions with answers.

## 5. More runnable examples: the companion repository

You also have a separate repository of plain, runnable pattern scripts:

**https://github.com/M-Hammad-Faisal/design-patterns-python**

Every pattern file here ends with a link to the matching script there (`creationalPattern/`, `structuralPattern/`, `behavioralPattern/`). Read the explanation here, run the script there, then change it and break it on purpose: that is how patterns stick. The repository's README lists every pattern with a link back to its detailed lesson.

## 6. Which pattern do I need? (a quick chooser)

| I want to... | Reach for |
|--------------|-----------|
| Make sure there is only one of something | [Singleton](creational/singleton.md) (or a module) |
| Pick which class to create from input or config | [Factory Method](creational/factory-method.md) |
| Create a matching set of objects (all dark-theme widgets) | [Abstract Factory](creational/abstract-factory.md) |
| Build an object with many optional parts, step by step | [Builder](creational/builder.md) |
| Copy an existing object and tweak it | [Prototype](creational/prototype.md) |
| Reuse expensive objects (connections) | [Object Pool](creational/object-pool.md) |
| Make an incompatible class fit my interface | [Adapter](structural/adapter.md) |
| Add features to an object without subclassing | [Decorator](structural/decorator.md) |
| Control access to an object (lazy, cached, protected) | [Proxy](structural/proxy.md) |
| Hide a messy subsystem behind a simple call | [Facade](structural/facade.md) |
| Treat one item and a group of items the same way | [Composite](structural/composite.md) |
| Vary two things independently (shape x renderer) | [Bridge](structural/bridge.md) |
| Share data between thousands of similar objects | [Flyweight](structural/flyweight.md) |
| Swap an algorithm at runtime | [Strategy](behavioral/strategy.md) |
| Notify many listeners when something changes | [Observer](behavioral/observer.md) |
| Turn an action into an object (queue, undo) | [Command](behavioral/command.md) |
| Change behavior as an object moves through states | [State](behavioral/state.md) |
| Fix an algorithm's steps but let parts vary | [Template Method](behavioral/template-method.md) |
| Walk through a collection without exposing it | [Iterator](behavioral/iterator.md) |
| Pass a request along a chain of handlers | [Chain of Responsibility](behavioral/chain-of-responsibility.md) |
| Stop many objects talking to each other directly | [Mediator](behavioral/mediator.md) |
| Save and restore an object's state (undo) | [Memento](behavioral/memento.md) |
| Add new operations to a stable set of classes | [Visitor](behavioral/visitor.md) |
| Evaluate a small custom language or rule syntax | [Interpreter](behavioral/interpreter.md) |
| Stop checking for `None` everywhere | [Null Object](behavioral/null-object.md) |

## 7. Suggested learning order

Start with the ones you will use most, then the rest:

1. **Strategy**, **Factory Method**, **Decorator**, **Observer** (most common).
2. **Adapter**, **Facade**, **Builder**, **Singleton** (and why to be careful with it), **Template Method**.
3. **Command**, **State**, **Composite**, **Proxy**, **Iterator**, **Chain of Responsibility**.
4. **Abstract Factory**, **Bridge**, **Prototype**, **Mediator**, **Memento**, **Flyweight**, **Visitor**, **Interpreter**.

## 8. Five warnings before you start

1. **Do not force patterns.** If a function solves it, use a function.
2. **A pattern is a trade-off.** It adds classes and indirection to buy flexibility. Pay only when you need the flexibility.
3. **Names matter more than code.** Two teams can implement Strategy differently; both are still "Strategy".
4. **Patterns combine.** Real systems mix several (middleware = Chain + Strategy).
5. **Python is not Java.** First-class functions, modules, decorators and duck typing make many patterns shorter. The files show both.

[Creational](creational/README.md) · [Structural](structural/README.md) · [Behavioral](behavioral/README.md) · [Back to OOP](../README.md)
