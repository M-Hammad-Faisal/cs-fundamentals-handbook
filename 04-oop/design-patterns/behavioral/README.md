# Behavioral Patterns

**Question they answer:** *How do objects communicate, share the work, and change behavior, without being tangled together?*

They replace giant conditionals and tight links between classes with small collaborating objects.

| Pattern | One-line idea | Use it when | Lesson |
|---------|---------------|-------------|--------|
| **Strategy** | Swap an algorithm | Several ways to do one job | [strategy.md](strategy.md) |
| **Observer** | Notify subscribers of changes | One-to-many reactions | [observer.md](observer.md) |
| **Command** | A request as an object | Queue, log, undo | [command.md](command.md) |
| **State** | Behavior follows state | Lifecycles and workflows | [state.md](state.md) |
| **Template Method** | Fixed steps, overridable parts | Shared skeleton, varying details | [template-method.md](template-method.md) |
| **Iterator** | Walk a collection uniformly | Custom structures, lazy streams | [iterator.md](iterator.md) |
| **Chain of Responsibility** | Pass along handlers | Middleware, approvals, validation | [chain-of-responsibility.md](chain-of-responsibility.md) |
| **Mediator** | Central coordinator | Many peers talking to each other | [mediator.md](mediator.md) |
| **Memento** | Snapshot and restore | Undo, checkpoints | [memento.md](memento.md) |
| **Visitor** | New operations on a stable hierarchy | Trees, compilers, exporters | [visitor.md](visitor.md) |
| **Interpreter** | Evaluate a small language | Rules and formulas | [interpreter.md](interpreter.md) |
| **Null Object** (extra) | A do-nothing stand-in for `None` | Optional collaborators | [null-object.md](null-object.md) |

## Easy-to-confuse pairs

| Pair | Difference |
|------|-----------|
| **Strategy vs State** | Strategy: the *client* picks an interchangeable algorithm. State: the *object* changes behavior itself as its state changes. |
| **Strategy vs Template Method** | Composition at runtime vs inheritance at design time. |
| **Observer vs Mediator** | Observer: one-way broadcast. Mediator: central two-way coordination. |
| **Observer vs Chain of Responsibility** | Observer tells *everyone*; a chain gives the request to handlers in order, usually stopping at the first. |
| **Command vs Memento** | Command undoes by running the inverse action; Memento undoes by restoring a saved state. |
| **Visitor vs Strategy** | Visitor varies behavior by the *element's type*; Strategy varies one algorithm by choice. |

## Cheat sheet

- **Strategy:** often just pass a function (`key=`).
- **Observer:** callbacks, `unsubscribe`, watch leaks and exceptions.
- **Command:** `execute()` + `undo()`; keep what undo needs.
- **State:** state classes for real behavior; a transition table for rules only.
- **Template Method:** base class owns the order; hooks are optional.
- **Iterator:** generators and `yield from`; iterators are single-use.
- **Chain:** each handler handles or passes; always have a fallback.
- **Mediator:** thin coordinator, not a god object.
- **Memento:** immutable snapshots with a size limit.
- **Visitor:** only for stable hierarchies; `singledispatch`/`match` are lighter.
- **Interpreter:** small grammars only; never evaluate untrusted text dynamically.
- **Null Object:** neutral behavior; never hide real errors.

## Family practice (mixed)

1. Name the pattern: (a) middleware stack, (b) Ctrl+Z, (c) `sorted(key=...)`, (d) Django `post_save` signals, (e) `unittest.TestCase.setUp/tearDown`, (f) `ast.NodeVisitor`, (g) `logging.NullHandler`.
2. An order must not be shipped before payment. Which pattern, and how would you implement it simply?

<details>
<summary>Answers</summary>

1. (a) Chain of Responsibility, (b) Command (or Memento), (c) Strategy, (d) Observer, (e) Template Method, (f) Visitor, (g) Null Object.
2. State: a transition table `{("pending","pay"): "paid", ("paid","ship"): "shipped"}`; any other event raises an error.

</details>

[Structural patterns](../structural/README.md) · [All patterns](../README.md) · [Back to OOP](../../README.md)
