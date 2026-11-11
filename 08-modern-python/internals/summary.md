# Python Internals: One-Page Summary

## Key facts

- **Objects and names:** every value is an object with identity (`id`, `is`), type and value; a name is a label bound to an object, and assignment never copies.
- **Memory:** reference counting frees an object the moment its count reaches zero; a cycle collector (`gc`) handles reference cycles; `weakref` refers without owning.
- **Attribute lookup:** data descriptor on the type, then the instance `__dict__`, then non-data descriptors and class attributes, then `__getattr__`; functions are descriptors, which is how bound methods work, and `property` is a descriptor too.
- **Classes are objects:** `type` builds them; `__init_subclass__` hooks subclass creation; `__slots__` removes the per-instance dict to save memory.
- **Bytecode:** source is compiled to stack-machine bytecode (`dis.dis(f)` shows it) and run by the interpreter loop.
- **Imports:** a module runs once and is cached in `sys.modules`; `sys.path` decides where to look; circular imports see half-built modules.
- **The GIL:** one thread runs bytecode at a time in the standard build and is released during blocking I/O; free-threaded builds are available in newer versions.
- **Interpreter pipeline:** tokenizer, parser, AST, then either a tree walker or compiled bytecode on a VM.

## Pitfalls

- Relying on `id`, small-integer caching or exact reference counts: they are implementation details.
- Using `is` to compare values instead of identity.
- Counting on `__del__` to run at a precise moment.
- Mutable class attributes shared by all instances.
- Reaching for a metaclass when `__init_subclass__` or a decorator would do.

## Self-check

- **What does it mean that variables are names bound to objects?** Assignment attaches a label to an object without copying; several names can refer to the same object, so mutation through one is visible through the others.
- **When does CPython free an object, and what does the cycle collector add?** Immediately when its reference count reaches zero; the cycle collector finds groups of objects that only reference each other and frees them.
- **State the attribute lookup order and say where data descriptors fit.** Class data descriptor, then instance `__dict__`, then class non-data descriptor or plain class attribute, then `__getattr__`.
- **How do bound methods work?** A function in a class is a non-data descriptor; its `__get__` returns a method object that stores the instance and passes it as the first argument.
- **When would you use `__init_subclass__` versus a metaclass?** `__init_subclass__` for hooks that run when subclasses are created (registries, validation); a metaclass only when you must change how the class object itself is constructed or behaves.
- **What do `__slots__` give you and cost you?** They give smaller instances and no accidental attributes; they cost dynamic attributes and make multiple inheritance harder.
- **What are the four stages from source text to running code in this lesson?** Tokenize, parse into an AST, then either interpret the tree directly or compile it to bytecode and run it on a VM.
- **What does the layering of grammar rules (`sum` built from `term`) encode?** Operator precedence: operators lower in the grammar (`*`) bind tighter than ones above it (`+`).
- **Why is left recursion a problem for recursive descent, and what replaces it?** A rule that calls itself first without consuming a token recurses forever; use a loop to repeat `{ op term }` instead.
- **What is the difference between a tree-walking interpreter and a bytecode VM?** A tree walker recursively evaluates nodes; a VM runs a flat list of simple instructions with a program counter and a stack, which is faster and easier to optimise.
- **In postfix order, what is `2 + 3 * 4`?** `2 3 4 * +`.
- **How do `while` loops become jumps?** The condition is tested at the top; a conditional jump leaves the loop when false; at the end of the body an unconditional jump returns to the test.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [The Python Data Model and CPython Internals](01-python-data-model-and-internals.md) · [Build a Tiny Interpreter](02-build-a-tiny-interpreter.md)
