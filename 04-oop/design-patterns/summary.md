# Design Patterns: One-Page Summary

## Key facts

- **Three families:** *creational* (how objects are made: singleton, factory method, abstract factory, builder, prototype, object pool); *structural* (how objects are composed: adapter, bridge, composite, decorator, facade, flyweight, proxy); *behavioral* (how objects cooperate: chain of responsibility, command, interpreter, iterator, mediator, memento, null object, observer, state, strategy, template method, visitor).
- **Pick by the problem:** a ladder of `if`s choosing an algorithm is Strategy; behaviour that depends on state is State; notify many listeners is Observer; add behaviour without subclassing is Decorator; an incompatible interface is Adapter; a simple front for a messy subsystem is Facade; undo, queue or log actions is Command; a tree of parts is Composite; step-by-step construction is Builder; control or delay access is Proxy.
- **Look-alikes:** Strategy is chosen by the caller, State changes itself; Decorator adds behaviour while Proxy controls access (same interface); Adapter converts one interface while Facade simplifies many.
- **Python shortcuts:** plain functions often replace Strategy and Command, generators replace Iterator, `@decorators` and wrappers replace Decorator, a module is already a singleton, `dataclass` helps with Builder and Prototype, duck typing replaces interface hierarchies.
- **Guiding rule:** prefer composition over inheritance, and add a pattern only when you can name the pain it removes.

## Pitfalls

- Starting from a pattern instead of from a problem; extra classes with no benefit.
- Singleton as hidden global state that makes tests depend on each other.
- Observers that are never unsubscribed (memory leaks, surprise callbacks).
- Deep inheritance chains where composition would do.
- A "Factory" that only calls a constructor.

## Self-check

- **How does a request move along the chain?** Each handler either handles it or passes it to the next handler.
- **What does it mean to "turn a request into an object"?** Represent the action (what to do, and with which arguments) as an object you can store, pass around, queue, log or reverse.
- **What does each class in an Interpreter represent?** A rule of the grammar (a terminal such as a constant or variable, or a non-terminal such as And/Add).
- **What are the two methods of the iterator protocol?** `__iter__` (returns the iterator) and `__next__` (returns the next value or raises `StopIteration`).
- **What problem does Mediator solve?** A tangle of direct references between many interacting objects; it replaces them with one coordinator.
- **What are the three roles?** Originator (creates and restores), Memento (the snapshot), Caretaker (stores them).
- **What does a null object replace and why?** It replaces `None` with an object that implements the interface neutrally, removing repeated `is not None` checks.
- **Who knows about whom in Observer?** The subject knows only that it has callbacks; observers know the subject (they subscribe). The subject does not know what they do.
- **What does the context delegate to the state object?** Each action (`pay`, `ship`, ...); the state decides the result and the next state.
- **What does Strategy replace?** A conditional ladder choosing between algorithms; the algorithms become interchangeable objects.
- **What does the template method fix and what can subclasses change?** It fixes the order of the algorithm's steps; subclasses override individual steps.
- **What does Visitor let you add without modifying element classes?** New operations over a class hierarchy.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Design Patterns](exercises.md) · [Design Patterns](summary.md)
