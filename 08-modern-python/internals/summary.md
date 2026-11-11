# Python Internals: One-Page Summary

## Questions worth remembering

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

Practice problems with solutions are in the **Practice** section of each lesson.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [The Python Data Model and CPython Internals](01-python-data-model-and-internals.md) · [Build a Tiny Interpreter](02-build-a-tiny-interpreter.md)
