# Python Internals

How Python really works: the data model, descriptors, memory management, bytecode, imports and a tiny interpreter you build yourself.

## Detailed lessons

- [The Python data model and CPython internals](01-python-data-model-and-internals.md)
- [Build a tiny interpreter](02-build-a-tiny-interpreter.md)

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

## Quick reference

| Question | Answer |
|----------|--------|
| What does it mean that variables are names bound to objects? | Assignment attaches a label to an object without copying; several names can refer to the same object, so mutation through one is visible through the others. |
| When does CPython free an object, and what does the cycle collector add? | Immediately when its reference count reaches zero; the cycle collector finds groups of objects that only reference each other and frees them. |
| State the attribute lookup order and say where data descriptors fit. | Class data descriptor, then instance `__dict__`, then class non-data descriptor or plain class attribute, then `__getattr__`. |
| How do bound methods work? | A function in a class is a non-data descriptor; its `__get__` returns a method object that stores the instance and passes it as the first argument. |
| When would you use `__init_subclass__` versus a metaclass? | `__init_subclass__` for hooks that run when subclasses are created (registries, validation); a metaclass only when you must change how the class object itself is constructed or behaves. |

Back to [modern Python](../README.md).
