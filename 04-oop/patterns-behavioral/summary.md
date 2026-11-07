# Behavioral Patterns: One-Page Summary

| Pattern | Idea | Python flavor |
|---------|------|---------------|
| **Strategy** | Swap algorithms | pass a function; `key=` arguments |
| **Observer** | Notify dependents | callbacks, signals, pub/sub; always unsubscribe |
| **Command** | Request as an object: queue, log, undo | `execute`/`undo`, task queues, `partial` |
| **State** | Behavior follows state | state classes or transition table |
| **Template Method** | Fixed skeleton, variable steps | base class + hooks (`setUp`, class-based views) |
| **Iterator** | Traverse without exposing structure | `__iter__`, generators, `yield from` |
| **Chain of Responsibility** | Pass request along handlers | middleware stacks |
| **Mediator** | Central coordinator for peers | event bus, dialog controller |
| **Memento** | Snapshot and restore | immutable snapshot dataclass |
| **Visitor** | New operations on a stable hierarchy | `singledispatch`, `ast.NodeVisitor` |
| **Null Object** | Do-nothing stand-in for `None` | `NullHandler`, `nullcontext` |

- Strategy vs State: client-chosen algorithm vs self-driven behavior change. Template Method (inheritance) vs Strategy (composition).
- Combine: Command + Memento for undo; Chain + Strategy for middleware; State + Observer for workflow events.
- Risks: observer leaks, mediator god objects, visitor rigidity, over-engineering where a function suffices.

[Lesson](README.md) · [Exercises](exercises.md)
