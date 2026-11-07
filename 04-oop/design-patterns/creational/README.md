# Creational Patterns

**Question they answer:** *How do I create objects without hard-wiring which class I build, how many exist, or how they are assembled?*

Creating an object with `ClassName(...)` ties your code to that exact class. Creational patterns hide and control **creation**, so the rest of the code asks for what it needs and gets it.

| Pattern | One-line idea | Use it when | Lesson |
|---------|---------------|-------------|--------|
| **Singleton** | Exactly one instance | Truly one shared thing (prefer a module or injection) | [singleton.md](singleton.md) |
| **Factory Method** | A method (or function) decides which class to build | The class depends on input or config | [factory-method.md](factory-method.md) |
| **Abstract Factory** | A factory for a whole matching family | Several objects must be compatible (themes, vendors) | [abstract-factory.md](abstract-factory.md) |
| **Builder** | Assemble a complex object step by step | Many optional parts or validation steps | [builder.md](builder.md) |
| **Prototype** | Clone an existing object | Creation is costly; objects differ slightly | [prototype.md](prototype.md) |
| **Object Pool** (extra) | Reuse a fixed set of expensive objects | Connections, threads, buffers | [object-pool.md](object-pool.md) |

## Comparison

| | Creates | How you choose the class | Typical Python shortcut |
|--|---------|--------------------------|-------------------------|
| Singleton | the *same* object | n/a | module-level instance |
| Factory Method | one product | subclass or key decides | dict of classes, `classmethod` |
| Abstract Factory | a family | the factory object you pass in | a dataclass of classes |
| Builder | one complex product | you, step by step | keyword args / dataclass |
| Prototype | copy of an object | the template you clone | `copy.deepcopy`, `replace` |
| Object Pool | reused objects | the pool hands you any free one | `queue.Queue` + context manager |

## Cheat sheet

- **One instance?** Module, or create at startup and inject. Singleton class only if you must.
- **Which class?** Registry/dictionary factory; use `__init_subclass__` to self-register.
- **Matching family?** Abstract Factory; accept that adding a product type edits every factory.
- **Many options?** Keyword arguments and dataclasses first; Builder for steps, ordering and validation.
- **Copy and tweak?** `copy.deepcopy` / `dataclasses.replace`; remember shallow versus deep.
- **Costly resource?** Pool it, always return it (`with`), size it, give it a timeout.

## Family practice (mixed)

1. Which pattern fits: (a) one logger config shared by all modules, (b) PDF/CSV export chosen by file extension, (c) light/dark widget kits, (d) an HTTP request with optional headers/body/auth, (e) spawning 500 similar monsters, (f) database connections?
2. Why is a global Singleton risky for testing, and what do you do instead?

<details>
<summary>Answers</summary>

1. (a) Singleton (module-level logger); (b) Factory Method / registry; (c) Abstract Factory; (d) Builder; (e) Prototype; (f) Object Pool.
2. It hides a dependency and carries state between tests, and cannot be swapped for a fake; instead create the object once in `main()` and inject it (dependency injection).

</details>

[All patterns](../README.md) · [Structural patterns](../structural/README.md)
