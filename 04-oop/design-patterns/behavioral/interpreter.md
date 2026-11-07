# Interpreter Pattern

**Family:** behavioral · **How often you will use it:** rarely (small languages, rule engines) · **Difficulty:** medium to hard

## 1. In plain words

The **Interpreter** pattern defines a **small language** (a grammar) as classes and **evaluates sentences of that language** by building a tree of objects, where each object knows how to compute its own meaning.

Analogy: **sheet music**. The notation is a tiny language with rules; a musician (the interpreter) reads each symbol and knows how to play it. Or a **calculator** that reads `2 + 3 * 4`.

## 2. The problem

You need to evaluate user-defined expressions or rules ("age > 18 and country == 'PK'", "price * 0.9") that are not known when you write the program, and hard-coding every possible rule is impossible.

## 3. The solution

Represent the grammar with classes: one class per grammar rule. A sentence becomes an **abstract syntax tree (AST)** of these objects; calling `interpret(context)` on the root evaluates the whole thing recursively.

```text
expression:  (age > 18) AND (country == "PK")

          And
         /    \
     Greater   Equals
     /    \    /     \
   Var   Num  Var    Const
  (age)  (18) (country) ("PK")

root.interpret({"age": 21, "country": "PK"})  ->  True
```

## 4. Step by step: a rule engine

```python
class Expression:
    def interpret(self, ctx):
        raise NotImplementedError

class Const(Expression):
    def __init__(self, value): self.value = value
    def interpret(self, ctx): return self.value

class Var(Expression):
    def __init__(self, name): self.name = name
    def interpret(self, ctx): return ctx[self.name]

class Greater(Expression):
    def __init__(self, left, right): self.left, self.right = left, right
    def interpret(self, ctx): return self.left.interpret(ctx) > self.right.interpret(ctx)

class Equals(Expression):
    def __init__(self, left, right): self.left, self.right = left, right
    def interpret(self, ctx): return self.left.interpret(ctx) == self.right.interpret(ctx)

class And(Expression):
    def __init__(self, left, right): self.left, self.right = left, right
    def interpret(self, ctx): return self.left.interpret(ctx) and self.right.interpret(ctx)

class Or(Expression):
    def __init__(self, left, right): self.left, self.right = left, right
    def interpret(self, ctx): return self.left.interpret(ctx) or self.right.interpret(ctx)

rule = And(Greater(Var("age"), Const(18)), Equals(Var("country"), Const("PK")))
print(rule.interpret({"age": 21, "country": "PK"}))     # True
print(rule.interpret({"age": 16, "country": "PK"}))     # False
print(rule.interpret({"age": 30, "country": "US"}))     # False
```

### Adding a parser: from text to the tree

```python
import re

def tokenize(text):
    return re.findall(r"\d+|[A-Za-z_]+|[+\-*/()]", text)

class Parser:
    """Recursive descent for:  expr = term (('+'|'-') term)* ; term = factor (('*'|'/') factor)* ;
       factor = NUMBER | NAME | '(' expr ')'"""
    def __init__(self, text):
        self.tokens, self.pos = tokenize(text), 0
    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None
    def take(self):
        tok = self.tokens[self.pos]; self.pos += 1; return tok
    def expr(self):
        node = self.term()
        while self.peek() in ("+", "-"):
            node = BinOp(self.take(), node, self.term())
        return node
    def term(self):
        node = self.factor()
        while self.peek() in ("*", "/"):
            node = BinOp(self.take(), node, self.factor())
        return node
    def factor(self):
        tok = self.take()
        if tok == "(":
            node = self.expr(); self.take(); return node          # consume ")"
        return Const(int(tok)) if tok.isdigit() else Var(tok)

class BinOp(Expression):
    OPS = {"+": lambda a, b: a + b, "-": lambda a, b: a - b, "*": lambda a, b: a * b, "/": lambda a, b: a / b}
    def __init__(self, op, left, right): self.op, self.left, self.right = op, left, right
    def interpret(self, ctx): return self.OPS[self.op](self.left.interpret(ctx), self.right.interpret(ctx))

tree = Parser("price * (1 - discount) + shipping").expr()
print(tree.interpret({"price": 200, "discount": 0, "shipping": 5}))          # 205
print(Parser("2 + 3 * 4").expr().interpret({}), Parser("(2 + 3) * 4").expr().interpret({}))   # 14 20
```

The parser turns text into the object tree (respecting precedence: `*` binds tighter than `+`); the tree then evaluates itself.

## 5. The Pythonic way

- For tiny rules, a **dictionary of lambdas** or Python's `operator` module may be enough.
- For user-provided formulas, do **not** feed untrusted text to Python's dynamic evaluation functions. Use `ast.literal_eval` for literals only, or a purpose-built parser such as the one above, or a vetted library (`simpleeval`, `lark`, `pyparsing`).
- Use `match` statements to walk small trees; use `lark`/`pyparsing` to generate parsers from a grammar.
- Real interpreters and engines you know: regular expressions, SQL engines, template languages (Jinja), configuration expression languages, Excel formulas.

```python
import ast, operator
OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}

def safe_eval(text, names):
    def walk(node):
        if isinstance(node, ast.Constant): return node.value
        if isinstance(node, ast.Name): return names[node.id]
        if isinstance(node, ast.BinOp): return OPS[type(node.op)](walk(node.left), walk(node.right))
        raise ValueError("unsupported syntax")
    return walk(ast.parse(text, mode="eval").body)

print(safe_eval("price * 2 + 1", {"price": 10}))        # 21
try:
    safe_eval("__import__('os')", {})
except ValueError as e:
    print("blocked:", e)                                # blocked: unsupported syntax
```

## 6. When to use it (and when not to)

**Use it when** you have a simple, well-defined grammar (search filters, business rules, formulas, query mini-languages, configuration conditions) and want users to express logic without redeploying code.

**Skip it when** the language is large or complex (use a parser generator or an embedded language), performance is critical, or fixed options (a dropdown) would do.

## 7. Pros and cons

| Pros | Cons |
|------|------|
| Easy to extend the grammar with new classes | Class count grows with grammar size |
| Grammar is explicit in the code | Slow compared with compiled approaches |
| Reuses tree structure (works with [Visitor](visitor.md)/[Composite](../structural/composite.md)) | Large grammars become unmanageable |
| | Security risks if you evaluate untrusted text carelessly |

## 8. Related patterns

- [Composite](../structural/composite.md): the AST is a composite (terminal vs non-terminal expressions).
- [Visitor](visitor.md): operations over the AST (evaluate, print, optimize).
- [Iterator](iterator.md): walking tokens or nodes. [Flyweight](../structural/flyweight.md): sharing terminal symbols.
- [Strategy](strategy.md): small rules can often be strategies instead.

## 9. Two real-world examples

**Example 1: Rule engines and filters.** An admin configures "order total > 100 AND country in (PK, AE)" for free shipping. The system parses that text into an expression tree and evaluates it for each order, no deployment needed.

**Example 2: Search query languages.** `author:ana AND (python OR django) -tutorial` is parsed into a tree of `And`, `Or`, `Not`, `Field` nodes and translated or evaluated against an index.

## 10. Common mistakes

- Evaluating untrusted input with Python's dynamic evaluation functions.
- Writing a huge interpreter by hand when a parser library would be shorter and safer.
- Mixing parsing and evaluation in one tangled class (separate them).
- Ignoring error messages for malformed input.

## 11. Practice

1. Add `Not` and a `Less` operator to the rule engine.
2. Extend the parser to support unary minus (`-x + 3`).
3. Why is `ast.parse` plus a whitelist safer than dynamic evaluation of user text?

<details>
<summary>Solutions</summary>

**1.**
```python
class Not(Expression):
    def __init__(self, operand): self.operand = operand
    def interpret(self, ctx): return not self.operand.interpret(ctx)
class Less(Expression):
    def __init__(self, left, right): self.left, self.right = left, right
    def interpret(self, ctx): return self.left.interpret(ctx) < self.right.interpret(ctx)
r = And(Less(Var("age"), Const(18)), Not(Equals(Var("country"), Const("US"))))
print(r.interpret({"age": 10, "country": "PK"}), r.interpret({"age": 10, "country": "US"}))   # True False
```

**2.**
```python
class Parser2(Parser):
    def factor(self):
        if self.peek() == "-":
            self.take()
            return BinOp("-", Const(0), self.factor())          # -x is 0 - x
        return super().factor()
print(Parser2("-x + 3").expr().interpret({"x": 5}))             # -2
```

**3.** The whitelist only allows node types you handle (constants, names, arithmetic), so anything else (function calls, imports, attribute access) is rejected; dynamic evaluation would run arbitrary code with your program's privileges.

</details>

## 12. Check yourself

1. What does each class in an Interpreter represent?
2. What are the roles of the parser and the AST?
3. Why is the pattern limited to small languages?
4. How do you stay safe with user-defined formulas?

<details>
<summary>Answers</summary>

1. A rule of the grammar (a terminal such as a constant or variable, or a non-terminal such as And/Add).
2. The parser converts text into an abstract syntax tree of expression objects; the tree evaluates itself recursively.
3. Each grammar rule needs a class and the evaluation is slow, so large or performance-critical languages need parser generators or compilers.
4. Parse into your own AST or a whitelisted `ast` subset, never evaluate raw text dynamically; or use a vetted library.

</details>

## More examples

Runnable script (added to your companion repository with this lesson): [`behavioralPattern/interpreterPattern.py`](https://github.com/M-Hammad-Faisal/design-patterns-python/blob/master/behavioralPattern/interpreterPattern.py)

[Family overview](README.md) · [All patterns](../README.md)
