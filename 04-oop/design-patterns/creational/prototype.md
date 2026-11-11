# Prototype Pattern

**Family:** creational · **How often you will use it:** sometimes · **Difficulty:** easy

## 1. In plain words

A **Prototype** is an existing object you **copy** to make new ones, instead of building each from scratch. You say "make me one like that, but change this".

Analogy: a **document template** or a **cell dividing**. You do not retype the contract; you duplicate the template and edit the name.

## 2. The problem

Creating an object is expensive or fiddly (many fields, a database lookup, a heavy setup), and you need many similar copies:

```python no-run
enemy1 = Enemy("goblin", hp=30, loot=["coin", "dagger"], ai=load_ai("goblin"), sprite=load("goblin.png"))
enemy2 = Enemy("goblin", hp=30, loot=["coin", "dagger"], ai=load_ai("goblin"), sprite=load("goblin.png"))
# repeated setup, repeated cost
```

## 3. The solution

```text
Client --clone()--> [ Prototype object ] --returns--> new independent copy
```

Roles: a **prototype** with a `clone()` method (or Python's `copy` module) and clients that clone it and tweak the copy.

## 4. Step by step

```python
import copy

class Enemy:
    def __init__(self, kind, hp, loot):
        self.kind, self.hp, self.loot = kind, hp, loot

    def clone(self):
        return copy.deepcopy(self)                  # independent copy, including nested data

    def __repr__(self):
        return f"Enemy({self.kind}, hp={self.hp}, loot={self.loot})"

goblin_template = Enemy("goblin", 30, ["coin", "dagger"])
g1 = goblin_template.clone()
g2 = goblin_template.clone()
g2.hp = 45
g2.loot.append("gem")
print(g1)                 # Enemy(goblin, hp=30, loot=['coin', 'dagger'])
print(g2)                 # Enemy(goblin, hp=45, loot=['coin', 'dagger', 'gem'])
print(goblin_template)    # Enemy(goblin, hp=30, loot=['coin', 'dagger'])   (unchanged)
```

### Shallow versus deep copy (the key detail)

```python
original = Enemy("orc", 50, ["axe"])
shallow = copy.copy(original)           # new Enemy, but SAME loot list
deep = copy.deepcopy(original)          # new Enemy AND new loot list
shallow.loot.append("shield")
print(original.loot, deep.loot)         # ['axe', 'shield'] ['axe']   (the shallow copy shares the list)
```

- **Shallow copy** (`copy.copy`): copies the object but shares nested mutable objects.
- **Deep copy** (`copy.deepcopy`): copies everything recursively.
- Customize with `__copy__` and `__deepcopy__` (for example to share a big read-only texture but copy mutable state).

### A prototype registry

```python
class PrototypeRegistry:
    def __init__(self):
        self._items = {}
    def register(self, name, prototype):
        self._items[name] = prototype
    def create(self, name, **overrides):
        obj = self._items[name].clone()
        for k, v in overrides.items():
            setattr(obj, k, v)
        return obj

registry = PrototypeRegistry()
registry.register("goblin", Enemy("goblin", 30, ["coin"]))
registry.register("dragon", Enemy("dragon", 500, ["gold", "gem"]))
boss = registry.create("dragon", hp=900)
print(boss, registry.create("goblin"))
# Enemy(dragon, hp=900, loot=['gold', 'gem']) Enemy(goblin, hp=30, loot=['coin'])
```

## 5. The Pythonic way

- `copy.copy` / `copy.deepcopy` are built in; most classes need no `clone()` method at all.
- For dataclasses, `dataclasses.replace(obj, field=new_value)` gives "a copy with changes":

```python
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class ServerConfig:
    host: str
    port: int
    debug: bool = False

base = ServerConfig("0.0.0.0", 80)
dev = replace(base, port=8080, debug=True)
print(base, dev, sep="\n")
```

`replace` is a **shallow** copy; for mutable fields use `deepcopy` or immutable types (tuples, frozen dataclasses).

## 6. When to use it (and when not to)

**Use it when** creating an object is costly but copying is cheap; objects differ only slightly from a template; you want presets (game units, document templates, configuration profiles); you want to avoid a parallel hierarchy of factories.

**Skip it when** objects are simple, or hold resources that must not be copied (open files, sockets, locks).

## 7. Pros and cons

| Pros | Cons |
|------|------|
| Skips expensive setup | Deep-copying complex graphs (cycles, resources) is tricky and slow |
| Create copies without knowing their concrete class | Shallow-copy sharing bugs |
| Easy presets / variants | Objects with identity (database ids, locks) need care |

## 8. Related patterns

- [Factory Method](factory-method.md) / [Abstract Factory](abstract-factory.md) can be built on prototypes.
- [Memento](../behavioral/memento.md) also copies state, for restoring rather than creating.
- [Composite](../structural/composite.md) and [Decorator](../structural/decorator.md) trees are often cloned.

## 9. Two real-world examples

**Example 1: Game units.** A level spawns 200 goblins from one `goblin_template`: the sprite and AI are loaded once and shared, while hit points and position are per copy.

**Example 2: Report or email templates.** An invoice template with the company header and footer is cloned for each customer, and only the customer name and line items are replaced (`dataclasses.replace` on an immutable template).

## 10. Common mistakes

- Using `copy.copy` and then mutating nested lists/dicts (the original changes too).
- Deep-copying objects that hold sockets, files or locks.
- Forgetting identifiers: a clone of a database record should not keep the same primary key.
- Cloning huge graphs in a hot loop; measure.

## 11. Practice

1. Show the shallow-copy bug with a list-of-lists and fix it.
2. Write `__deepcopy__` for a class that holds a large shared `texture` string (do not copy it) and a mutable `stats` dict (copy it).
3. Use `replace` to create three `ServerConfig` variants from one base.

<details>
<summary>Solutions</summary>

**1.**
```python
grid = [[0, 0], [0, 0]]
bad = copy.copy(grid); bad[0][0] = 9
print(grid)                                         # [[9, 0], [0, 0]]  (shared inner list)
grid = [[0, 0], [0, 0]]
good = copy.deepcopy(grid); good[0][0] = 9
print(grid)                                         # [[0, 0], [0, 0]]
```

**2.**
```python
class Sprite:
    def __init__(self, texture, stats):
        self.texture, self.stats = texture, stats
    def __deepcopy__(self, memo):
        return Sprite(self.texture, copy.deepcopy(self.stats, memo))   # share texture, copy stats
a = Sprite("T" * 1000, {"hp": 1})
b = copy.deepcopy(a); b.stats["hp"] = 5
print(a.stats, b.texture is a.texture)              # {'hp': 1} True
```

**3.**
```python
variants = [replace(base, port=p) for p in (81, 82, 83)]
print([v.port for v in variants])                   # [81, 82, 83]
```

</details>

## 12. Check yourself

1. What does the Prototype pattern create objects from?
2. Shallow versus deep copy, and which bug does the difference cause?
3. What is the Pythonic way to "clone with changes" for a dataclass?
4. What kinds of objects should not be deep-copied?

<details>
<summary>Answers</summary>

1. An existing object that is copied, rather than a class constructor call from scratch.
2. A shallow copy shares nested mutable objects with the original (changes show up in both); a deep copy duplicates everything.
3. `dataclasses.replace(obj, field=value)` (shallow).
4. Objects holding external resources such as open files, sockets, database connections or locks.

</details>

## More examples

Runnable script from your companion repository: [`creationalPattern/prototypePattern.py`](https://github.com/M-Hammad-Faisal/design-patterns-python/blob/master/creationalPattern/prototypePattern.py)

[Family overview](README.md) · [All patterns](../README.md)
