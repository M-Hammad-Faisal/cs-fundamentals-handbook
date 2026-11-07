# Visitor Pattern

**Family:** behavioral · **How often you will use it:** rarely (compilers, tree processing) · **Difficulty:** hard (the most confusing GoF pattern)

## 1. In plain words

A **Visitor** lets you **add new operations to a set of classes without modifying those classes**. The operations live in a separate "visitor" object that **visits** each element and does the right thing for its type.

Analogy: a **tax inspector visiting different kinds of businesses** (shop, restaurant, factory). The inspector knows a procedure for each type; the businesses just open their doors ("accept the visit"). A new kind of inspector (fire safety) can visit the same businesses without changing them.

## 2. The problem

You have a stable family of classes (for example nodes of an expression tree) and keep adding operations: evaluate, print, simplify, count depth. Putting each operation inside every class pollutes them:

```python
class Add:
    def evaluate(self): ...
    def to_string(self): ...
    def depth(self): ...        # every new feature edits every node class
```

## 3. The solution

```text
Element.accept(visitor) ──calls──► visitor.visit_<ThisType>(self)     ("double dispatch")

Visitor 1: Evaluator    ─ visit_num, visit_add, visit_mul
Visitor 2: Printer      ─ visit_num, visit_add, visit_mul
```

Each element has a tiny `accept` method; each operation is one visitor class holding a `visit_*` method per element type.

## 4. Step by step

```python
class Num:
    def __init__(self, value): self.value = value
    def accept(self, visitor): return visitor.visit_num(self)

class Add:
    def __init__(self, left, right): self.left, self.right = left, right
    def accept(self, visitor): return visitor.visit_add(self)

class Mul:
    def __init__(self, left, right): self.left, self.right = left, right
    def accept(self, visitor): return visitor.visit_mul(self)

class Evaluator:                                        # operation 1
    def visit_num(self, n): return n.value
    def visit_add(self, n): return n.left.accept(self) + n.right.accept(self)
    def visit_mul(self, n): return n.left.accept(self) * n.right.accept(self)

class Printer:                                          # operation 2
    def visit_num(self, n): return str(n.value)
    def visit_add(self, n): return f"({n.left.accept(self)} + {n.right.accept(self)})"
    def visit_mul(self, n): return f"{n.left.accept(self)} * {n.right.accept(self)}"

expr = Mul(Add(Num(2), Num(3)), Num(4))
print(expr.accept(Printer()), "=", expr.accept(Evaluator()))     # (2 + 3) * 4 = 20

class DepthCounter:                                     # operation 3, added WITHOUT touching Num/Add/Mul
    def visit_num(self, n): return 1
    def visit_add(self, n): return 1 + max(n.left.accept(self), n.right.accept(self))
    def visit_mul(self, n): return 1 + max(n.left.accept(self), n.right.accept(self))

print(expr.accept(DepthCounter()))                      # 3
```

**Double dispatch:** `expr.accept(visitor)` first dispatches on the *element* type, which calls `visitor.visit_mul(...)`, which dispatches on the *visitor* type. The right code runs for the (element, operation) pair.

## 5. The Pythonic way

Python gives you shorter tools:

**`functools.singledispatch`** dispatches on the argument type, with no `accept` methods:

```python
from functools import singledispatch

@singledispatch
def evaluate(node):
    raise TypeError(f"cannot evaluate {type(node).__name__}")

@evaluate.register
def _(node: Num): return node.value
@evaluate.register
def _(node: Add): return evaluate(node.left) + evaluate(node.right)
@evaluate.register
def _(node: Mul): return evaluate(node.left) * evaluate(node.right)

print(evaluate(expr))                                   # 20
```

**`match` statements** (3.10+) with classes:

```python
def show(node):
    match node:
        case Num(value=v):
            return str(v)
        case Add(left=l, right=r):
            return f"({show(l)} + {show(r)})"
        case Mul(left=l, right=r):
            return f"{show(l)} * {show(r)}"

print(show(expr))                                       # (2 + 3) * 4
```

**`ast.NodeVisitor`** in the standard library is a ready-made visitor that dispatches to `visit_ClassName`:

```python
import ast

class NameCollector(ast.NodeVisitor):
    def __init__(self): self.names = []
    def visit_Name(self, node):
        self.names.append(node.id)
        self.generic_visit(node)                        # continue into child nodes

collector = NameCollector()
collector.visit(ast.parse("total = price * qty + tax"))
print(collector.names)                                  # ['total', 'price', 'qty', 'tax']
```

## 6. When to use it (and when not to)

**Use it when** you have a **stable** hierarchy (the classes rarely change) but **many operations** keep being added: compilers and interpreters (abstract syntax trees), document exporters (HTML, PDF, plain text from the same tree), linters, code generators, tax or pricing rules over different item types.

**Skip it when** the class hierarchy changes often (every new element type forces edits to *all* visitors); then use plain polymorphism (methods on the classes), `singledispatch` or `match`.

## 7. Pros and cons

| Pros | Cons |
|------|------|
| Add new operations without touching element classes (Open/Closed) | Adding a new element class means editing every visitor |
| Related logic for one operation sits together | Requires `accept` boilerplate; confusing double dispatch |
| Visitor can accumulate state while traversing | May need access to element internals |

## 8. Related patterns

- [Composite](../structural/composite.md): visitors are the usual way to process composite trees.
- [Iterator](iterator.md): traverses; Visitor performs the operation per element type.
- [Interpreter](interpreter.md): the AST evaluated by the interpreter is often processed with visitors.
- [Strategy](strategy.md): swaps one algorithm; Visitor varies behavior by element *type*.

## 9. Two real-world examples

**Example 1: Compilers and linters.** The Python `ast` module parses code into a tree; linters, formatters and security scanners are `NodeVisitor`s that look for specific node types (calls to `eval`, unused names).

**Example 2: Document export.** A document tree (headings, paragraphs, images, tables) is exported by an `HtmlExporter` visitor, a `MarkdownExporter` visitor and a `WordCounter` visitor. Adding a PDF exporter changes none of the document classes.

## 10. Common mistakes

- Using Visitor when the element types change often.
- Breaking encapsulation: visitors needing private data of elements.
- Forgetting to traverse children (`generic_visit` in `ast.NodeVisitor`).
- Reaching for it when `singledispatch` or `match` is simpler.

## 11. Practice

1. Add a `Neg` node (unary minus) and update `Evaluator`, `Printer`, `DepthCounter`. Note what you had to edit.
2. Write a visitor that collects all `Num` values in an expression.
3. Implement `simplify` with `singledispatch` that turns `x * 1` and `x + 0` into `x`.

<details>
<summary>Solutions</summary>

**1.**
```python
class Neg:
    def __init__(self, operand): self.operand = operand
    def accept(self, visitor): return visitor.visit_neg(self)
Evaluator.visit_neg = lambda self, n: -n.operand.accept(self)
Printer.visit_neg = lambda self, n: f"-{n.operand.accept(self)}"
DepthCounter.visit_neg = lambda self, n: 1 + n.operand.accept(self)
e2 = Add(Num(1), Neg(Num(5)))
print(e2.accept(Printer()), "=", e2.accept(Evaluator()), "depth", e2.accept(DepthCounter()))   # (1 + -5) = -4 depth 3
```
Adding a node type forced edits to **every visitor**: the visitor trade-off.

**2.**
```python
class NumCollector:
    def __init__(self): self.values = []
    def visit_num(self, n): self.values.append(n.value)
    def visit_add(self, n): n.left.accept(self); n.right.accept(self)
    visit_mul = visit_add
nc = NumCollector(); expr.accept(nc); print(nc.values)                # [2, 3, 4]
```

**3.**
```python
@singledispatch
def simplify(node): return node
@simplify.register
def _(node: Add):
    l, r = simplify(node.left), simplify(node.right)
    if isinstance(r, Num) and r.value == 0: return l
    if isinstance(l, Num) and l.value == 0: return r
    return Add(l, r)
@simplify.register
def _(node: Mul):
    l, r = simplify(node.left), simplify(node.right)
    if isinstance(r, Num) and r.value == 1: return l
    if isinstance(l, Num) and l.value == 1: return r
    return Mul(l, r)
print(Printer().visit_num(Num(7)), simplify(Mul(Add(Num(5), Num(0)), Num(1))).accept(Printer()))   # 7 5
```

</details>

## 12. Check yourself

1. What does Visitor let you add without modifying element classes?
2. What is double dispatch?
3. What is hard to add with Visitor?
4. Name two Python alternatives and the standard-library visitor.

<details>
<summary>Answers</summary>

1. New operations over a class hierarchy.
2. The call is resolved on two types: element type (`accept`) and visitor type (`visit_x`).
3. A new element class, since every visitor needs a new `visit_*` method.
4. `functools.singledispatch` and `match` statements; `ast.NodeVisitor`.

</details>

## More examples

Runnable script (added to your companion repository with this lesson): [`behavioralPattern/visitorPattern.py`](https://github.com/M-Hammad-Faisal/design-patterns-python/blob/master/behavioralPattern/visitorPattern.py)

[Family overview](README.md) · [All patterns](../README.md)
