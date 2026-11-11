# Design Patterns: One-Page Summary

## Questions worth remembering

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

Practice problems with solutions are in the exercises page and in the **Practice** section of each lesson.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Design Patterns](exercises.md) · [Design Patterns](summary.md)
