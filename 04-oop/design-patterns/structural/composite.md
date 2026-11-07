# Composite Pattern

**Family:** structural · **Also called:** object tree · **How often you will use it:** often (trees everywhere) · **Difficulty:** medium

## 1. In plain words

A **Composite** lets you treat **a single object** and **a group of objects** in exactly the same way. Groups can contain single items *and other groups*, forming a tree.

Analogy: a **folder** in a file system. You can ask a file "what is your size?" and ask a folder "what is your size?"; the folder answers by adding up what is inside it (including sub-folders). The caller does not care which one it is talking to.

## 2. The problem

Code keeps asking "is this a single thing or a group?" and handles each differently:

```python
def total_size(node):
    if isinstance(node, File):
        return node.size
    else:
        return sum(total_size(child) for child in node.children)   # the caller must know the difference
```

Every operation (size, print, search, delete) repeats that type check.

## 3. The solution

```text
          Component (interface: size(), show())
              ▲
      ┌───────┴────────┐
    Leaf             Composite ──contains many──► Component
  (File)             (Folder): operations loop over its children
```

Leaves do the real work; composites delegate to their children. Clients call the same method on either.

## 4. Step by step

```python
from abc import ABC, abstractmethod

class Node(ABC):                                       # the component interface
    def __init__(self, name):
        self.name = name
    @abstractmethod
    def size(self): ...
    @abstractmethod
    def show(self, indent=0): ...

class File(Node):                                      # a leaf
    def __init__(self, name, size):
        super().__init__(name)
        self._size = size
    def size(self):
        return self._size
    def show(self, indent=0):
        return " " * indent + f"{self.name} ({self._size})"

class Folder(Node):                                    # a composite
    def __init__(self, name):
        super().__init__(name)
        self.children = []
    def add(self, node):
        self.children.append(node)
        return self
    def size(self):
        return sum(child.size() for child in self.children)      # recursion over the tree
    def show(self, indent=0):
        lines = [" " * indent + f"{self.name}/ ({self.size()})"]
        lines += [child.show(indent + 2) for child in self.children]
        return "\n".join(lines)

root = (Folder("root")
        .add(File("a.txt", 10))
        .add(Folder("src").add(File("main.py", 40)).add(File("util.py", 25))))
print(root.show())
# root/ (75)
#   a.txt (10)
#   src/ (65)
#     main.py (40)
#     util.py (25)
print(root.size())                                     # 75
```

### Another example: a menu with sub-menus and a total price

```python
class MenuItem:
    def __init__(self, name, price): self.name, self.price = name, price
    def total(self): return self.price
    def find(self, name): return self if self.name == name else None

class Menu:
    def __init__(self, name): self.name, self.children = name, []
    def add(self, node): self.children.append(node); return self
    def total(self): return sum(c.total() for c in self.children)
    def find(self, name):
        if self.name == name:
            return self
        for c in self.children:
            hit = c.find(name)
            if hit:
                return hit
        return None

lunch = Menu("Lunch").add(MenuItem("soup", 4)).add(Menu("Mains").add(MenuItem("pasta", 9)).add(MenuItem("steak", 15)))
print(lunch.total(), lunch.find("pasta").price, lunch.find("sushi"))      # 28 9 None
```

### Design question: where do `add` and `remove` live?

- **Transparency**: put `add`/`remove` on the shared interface (clients treat everything uniformly; leaves must reject them).
- **Safety**: only composites have `add`/`remove` (clients must know what they have). The examples above use the safe style.

## 5. The Pythonic way

- Implement `__iter__` so a tree can be walked with `for` (and `yield from` for recursion).
- Use `__len__`, `__contains__` and `__getitem__` to make composites feel like containers.
- The standard library is full of composites: `ast` nodes, `xml.etree.ElementTree` elements, `pathlib` directories.

```python
class Tree:
    def __init__(self, value, *children):
        self.value, self.children = value, list(children)
    def __iter__(self):                                 # depth-first walk
        yield self.value
        for child in self.children:
            yield from child

t = Tree("a", Tree("b", Tree("d")), Tree("c"))
print(list(t))                                          # ['a', 'b', 'd', 'c']
```

## 6. When to use it (and when not to)

**Use it when** your data forms a **tree** (part-whole hierarchy) and you want the same operations on parts and wholes: file systems, GUI widgets, HTML DOM, organization charts, expression trees, product bundles, menus, document structure.

**Skip it when** the data is flat, or leaves and groups really behave very differently.

## 7. Pros and cons

| Pros | Cons |
|------|------|
| Client code is simple (no type checks) | The shared interface may be too general (leaves get methods that make no sense) |
| New node types need no client changes | Recursion depth and performance on huge trees |
| Naturally recursive operations | Harder to restrict what a group may contain |

## 8. Related patterns

- [Iterator](../behavioral/iterator.md): walking the tree. [Visitor](../behavioral/visitor.md): adding operations to a tree.
- [Decorator](decorator.md): also recursive wrapping, but one child, adds behavior.
- [Builder](../creational/builder.md): often assembles composite trees.
- [Flyweight](flyweight.md): shares leaf nodes to save memory.

## 9. Two real-world examples

**Example 1: The HTML DOM.** An element can contain text or other elements. `element.remove()`, `element.querySelectorAll(...)` and rendering work the same on a `<span>` and a whole `<body>`.

**Example 2: A pricing bundle.** A "Home Office Bundle" contains a desk, a chair and a "Tech Pack" bundle (monitor, keyboard). `bundle.price()` sums the children, whether they are single products or nested bundles.

## 10. Common mistakes

- Cycles in the tree (a folder containing itself) cause infinite recursion.
- Forgetting to keep parent references consistent if you use them.
- Making the interface so general that leaves implement dozens of meaningless methods.
- Recursion limits on very deep trees (use iterative traversal).

## 11. Practice

1. Add `count_files()` and `find(name)` to the `Folder`/`File` classes.
2. Model an organization chart where `Employee` and `Manager` both have `salary_cost()` (a manager includes reports).
3. Write an iterative (non-recursive) traversal using a stack.

<details>
<summary>Solutions</summary>

**1.**
```python
class File2(File):
    def count_files(self): return 1
    def find(self, name): return self if self.name == name else None
class Folder2(Folder):
    def count_files(self): return sum(c.count_files() for c in self.children)
    def find(self, name):
        if self.name == name: return self
        for c in self.children:
            hit = c.find(name)
            if hit: return hit
        return None
r = Folder2("r").add(File2("a", 1)).add(Folder2("d").add(File2("b", 2)))
print(r.count_files(), r.find("b").size())              # 2 2
```

**2.**
```python
class Employee:
    def __init__(self, name, salary): self.name, self.salary = name, salary
    def salary_cost(self): return self.salary
class Manager(Employee):
    def __init__(self, name, salary): super().__init__(name, salary); self.reports = []
    def salary_cost(self): return self.salary + sum(r.salary_cost() for r in self.reports)
boss = Manager("boss", 100); lead = Manager("lead", 80); lead.reports.append(Employee("dev", 60)); boss.reports.append(lead)
print(boss.salary_cost())                               # 240
```

**3.**
```python
def walk(root):
    stack, out = [root], []
    while stack:
        node = stack.pop()
        out.append(node.value)
        stack.extend(reversed(node.children))
    return out
print(walk(Tree("a", Tree("b", Tree("d")), Tree("c"))))  # ['a', 'b', 'd', 'c']
```

</details>

## 12. Check yourself

1. What does Composite let clients ignore?
2. What are the three roles?
3. How is a folder's `size()` computed?
4. Name two real structures that are composites.

<details>
<summary>Answers</summary>

1. Whether they hold a single object or a group.
2. Component (shared interface), Leaf (does the work), Composite (holds children and delegates).
3. The sum of `size()` of each child, recursively; files return their own size.
4. File systems and the HTML DOM (also GUI widget trees, ASTs, org charts).

</details>

## More examples

Runnable script from your companion repository: [`structuralPattern/compositePattern.py`](https://github.com/M-Hammad-Faisal/design-patterns-python/blob/master/structuralPattern/compositePattern.py)

[Family overview](README.md) · [All patterns](../README.md)
