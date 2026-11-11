# Flyweight Pattern

**Family:** structural · **How often you will use it:** rarely, but important when memory matters · **Difficulty:** medium

## 1. In plain words

A **Flyweight** saves memory by **sharing the data that many objects have in common** instead of storing a copy in every object. Each object keeps only what is unique to it.

Analogy: a **printing press with a case of type**. A book has 500,000 letters on its pages, but there are only 26 letter shapes. You do not make a new metal "e" for every "e"; you reuse the same one many times and only record *where* it goes.

## 2. The problem

You create huge numbers of similar objects and most of their data is identical:

```python no-run
class Tree:
    def __init__(self, x, y, species_name, texture_bytes, color):    # texture is 2 MB
        ...
forest = [Tree(x, y, "oak", big_texture, "green") for x, y in positions]   # 100,000 copies of the texture!
```

## 3. The solution

Split each object's state into two kinds:

- **Intrinsic state**: identical across many objects, immutable, **shared** (species name, texture, color).
- **Extrinsic state**: unique to each use, **stored outside** or passed in (position).

```text
Tree(x, y) ──references──► SpeciesFlyweight("oak", texture)   (one shared object)
Tree(x, y) ──references──► SpeciesFlyweight("oak", texture)   (the same one)
                  ▲
        FlyweightFactory: returns the existing flyweight for a key, creates it only once
```

## 4. Step by step

```python
class Species:                                          # the flyweight: shared, immutable
    __slots__ = ("name", "texture")
    def __init__(self, name, texture):
        self.name, self.texture = name, texture

class SpeciesFactory:                                   # makes sure each species exists once
    _cache = {}
    @classmethod
    def get(cls, name):
        if name not in cls._cache:
            cls._cache[name] = Species(name, texture=f"<2MB texture for {name}>")
        return cls._cache[name]

class Tree:                                             # per-tree (extrinsic) data + a shared reference
    __slots__ = ("x", "y", "species")
    def __init__(self, x, y, species):
        self.x, self.y, self.species = x, y, species

kinds = ("oak", "pine", "fir")
forest = [Tree(i % 500, i // 500, SpeciesFactory.get(kinds[i % 3])) for i in range(60_000)]

print(len(forest), len({id(t.species) for t in forest}), len(SpeciesFactory._cache))
# 60000 3 3     (60,000 trees share just 3 species objects)
print(SpeciesFactory.get("oak") is forest[0].species)   # True
```

### Measuring the saving

```python
import sys

class HeavyTree:                                        # no sharing: every tree has its own species data
    def __init__(self, x, y, name):
        self.x, self.y, self.name, self.texture = x, y, name, "T" * 2000

class LightTree:                                        # shares the species flyweight
    __slots__ = ("x", "y", "species")
    def __init__(self, x, y, species): self.x, self.y, self.species = x, y, species

heavy = [HeavyTree(i, i, "oak") for i in range(1000)]
shared = SpeciesFactory.get("oak")
light = [LightTree(i, i, shared) for i in range(1000)]

heavy_bytes = sum(sys.getsizeof(t) + sys.getsizeof(t.texture) + sys.getsizeof(t.__dict__) for t in heavy)
light_bytes = sum(sys.getsizeof(t) for t in light)
print(light_bytes < heavy_bytes / 5)                    # True
```

## 5. The Pythonic way

Python already uses flyweights:

- **Small integers** (-5..256), `None`, `True`, `False` are single shared objects.
- **Interned strings**: `sys.intern(s)` makes equal strings share one object.
- `functools.lru_cache` on a constructor function returns the *same object* for the same arguments.
- `__slots__` shrinks per-object overhead.
- Tuples of immutable data, `enum` members, and `frozenset`s are natural shared values.

```python
import sys
a = sys.intern("".join(["he", "llo"]))
b = sys.intern("".join(["hel", "lo"]))
print(a is b)                                           # True: one shared string object

from functools import lru_cache

@lru_cache(maxsize=None)
def color(r, g, b):                                     # same arguments, same object
    return (r, g, b)
print(color(1, 2, 3) is color(1, 2, 3))                 # True
```

Libraries like **NumPy** and **pandas** apply the same idea at scale by storing data in compact shared arrays instead of millions of Python objects.

## 6. When to use it (and when not to)

**Use it when** you have a **very large number** of objects, much of whose state is **identical and immutable**, and memory (measured!) is a problem: game worlds, text editors (character styles), map tiles, particle systems.

**Skip it when** you have few objects, the state is mostly unique, or you have not measured a memory problem. The sharing adds complexity.

## 7. Pros and cons

| Pros | Cons |
|------|------|
| Large memory savings | More complex code (factory, split state) |
| Fewer allocations | Shared objects **must be immutable** |
| | Extrinsic state must be supplied or stored somewhere |

## 8. Related patterns

- [Singleton](../creational/singleton.md): one instance of a class; Flyweight: one shared instance per distinct *state*.
- [Factory Method](../creational/factory-method.md): the flyweight factory is a caching factory.
- [Composite](composite.md): leaves of a composite tree are often flyweights.
- [Object Pool](../creational/object-pool.md): shares *mutable* objects one user at a time; Flyweight shares *immutable* ones simultaneously.

## 9. Two real-world examples

**Example 1: A text editor.** A document with 1,000,000 characters does not store a font object per character. Each character holds a reference to a shared `Style(font, size, bold)` flyweight (maybe a dozen distinct ones) plus its own position.

**Example 2: A map renderer.** Millions of tiles reference a handful of shared tile-type objects (grass, water, road) containing image data; each tile stores only its coordinates and a type reference.

## 10. Common mistakes

- Making a flyweight mutable (one user's change affects all).
- Applying it without measuring (a premature optimization).
- Forgetting to include all intrinsic fields in the cache key, so different states share a wrong object.

## 11. Practice

1. Build a `Style` flyweight factory keyed by `(font, size, bold)` and 100,000 characters; show only a few `Style` objects exist.
2. Make a flyweight immutable using a `frozen=True` dataclass and show that mutation fails.
3. Why must flyweights be immutable?

<details>
<summary>Solutions</summary>

**1.**
```python
class Style:
    __slots__ = ("font", "size", "bold")
    def __init__(self, font, size, bold): self.font, self.size, self.bold = font, size, bold
class StyleFactory:
    cache = {}
    @classmethod
    def get(cls, font, size, bold):
        return cls.cache.setdefault((font, size, bold), Style(font, size, bold))
chars = [(c, StyleFactory.get("Arial", 12 if i % 10 else 14, i % 7 == 0)) for i, c in enumerate("x" * 100_000)]
print(len(StyleFactory.cache))                          # 4  (a few distinct styles for 100,000 characters)
```

**2.**
```python
from dataclasses import dataclass
@dataclass(frozen=True)
class FrozenStyle:
    font: str
    size: int
s = FrozenStyle("Arial", 12)
try:
    s.size = 20
except Exception as e:
    print(type(e).__name__)                             # FrozenInstanceError
```

**3.** Many objects reference the same flyweight at once; if one changed it, every other user would see the change. Immutability makes sharing safe.

</details>

## 12. Check yourself

1. What is intrinsic versus extrinsic state?
2. What does the flyweight factory do?
3. Give two flyweights Python already uses.
4. When is Flyweight a premature optimization?

<details>
<summary>Answers</summary>

1. Intrinsic: shared, identical, immutable data kept in the flyweight. Extrinsic: per-object data supplied from outside or stored separately.
2. Returns the existing flyweight for a key and creates it only if missing.
3. Small integers/interned strings/`None`/`True`/`False`; objects from `lru_cache`d constructors.
4. When you have few objects or have not measured a memory problem.

</details>

## More examples

Runnable script (added to your companion repository with this lesson): [`structuralPattern/flyweightPattern.py`](https://github.com/M-Hammad-Faisal/design-patterns-python/blob/master/structuralPattern/flyweightPattern.py)

[Family overview](README.md) · [All patterns](../README.md)
