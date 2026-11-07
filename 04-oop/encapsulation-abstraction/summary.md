# Encapsulation and Abstraction: One-Page Summary

- **Encapsulation:** bundle data + behavior, control access, protect **invariants**. **Abstraction:** expose *what*, hide *how*.
- **Python access:** `name` public, `_name` internal by convention, `__name` mangled to `_Class__name` (avoids subclass clashes; not security).
- **Properties:** start with plain attributes; add `@property` / `@x.setter` later without breaking callers. Read-only = no setter. `cached_property` = compute once.
- **Protect state:** validate in `__init__` and mutators, return copies/tuples, "tell, don't ask", Law of Demeter.
- **Descriptors** (`__get__`/`__set__`/`__set_name__`) power properties, methods and ORM fields; write one to reuse validation.
- **Abstraction tools:** `ABC` + `@abstractmethod` (enforced at instantiation, shared template methods), `Protocol` (structural typing, no inheritance), plain duck typing.
- **Depend on abstractions** so implementations (memory, SQLite, S3; Stripe, PayPal, fake) swap freely.
- **Leaky abstractions** hide costs or failures; document them and keep abstractions small.
- **Pitfalls:** exposing mutable internals, heavy getters, abstractions without a second implementation, giant base classes.

[Lesson](README.md) · [Exercises](exercises.md)
