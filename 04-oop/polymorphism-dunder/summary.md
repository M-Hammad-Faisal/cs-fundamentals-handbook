# Polymorphism and Dunder Methods: One-Page Summary

- **Polymorphism:** one interface, many implementations. Kinds: subtype (overriding, dynamic dispatch), duck typing, ad hoc (operator overloading, `singledispatch`), parametric (generics).
- **Replace `if/elif` on type with overriding**; new subclasses require no client change (Open/Closed).
- **Duck typing + EAFP:** try it, catch the failure; `Protocol` documents/checks the expectation.
- **Data model:** dunders let classes act built in. Groups: representation (`__repr__`, `__str__`, `__format__`), comparison (`__eq__`, `__lt__`, `__hash__`), arithmetic (+ reflected `__r*__`, in-place `__i*__`), conversion (`__bool__`, `__int__`), containers (`__len__`, `__getitem__`, `__contains__`, `__iter__`), `__call__`, context managers (`__enter__`/`__exit__`), attribute hooks, descriptors, async.
- **Operator rules:** return `NotImplemented` for unknown operands; keep immutable types returning new objects; `total_ordering` for comparisons; `__eq__` ⇒ consistent `__hash__`.
- **Free behavior:** subclass `collections.abc.Sequence` / `Mapping` and implement the minimum.
- **Iterables vs iterators:** iterator is single-use; make `__iter__` a generator for reusable iterables.
- **No overloading by signature:** use `singledispatch`, defaults/kwargs, classmethod constructors; `typing.overload` is for type checkers only.
- **Pitfalls:** abusing operators, calling dunders directly, mutable hashables, silent `__getattr__` defaults.

[Lesson](README.md) · [Exercises](exercises.md)
