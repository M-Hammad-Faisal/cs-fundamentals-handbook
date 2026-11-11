# Python Internals: Exercises

These problems go with the [Python Internals lesson](README.md). Try each one before opening its solution.

<details>
<summary>Setup code the solutions use (copied from the lessons)</summary>

```python
import re
from dataclasses import dataclass
import operator

@dataclass
class Token:
    kind: str       # NUMBER, NAME, KEYWORD, OP or END
    text: str

KEYWORDS = {"let", "print", "if", "else", "while"}
TOKEN_RE = re.compile(r"\s*(?:(?P<NUMBER>\d+(?:\.\d+)?)|(?P<NAME>[A-Za-z_]\w*)|(?P<OP>\*\*|<=|>=|==|!=|[-+*/%<>=(){};]))")

def tokenize(source: str) -> list[Token]:
    tokens, pos = [], 0
    while pos < len(source):
        if source[pos:].strip() == "":
            break
        m = TOKEN_RE.match(source, pos)
        if not m:
            raise SyntaxError(f"unexpected character {source[pos:].lstrip()[0]!r}")
        kind, text = m.lastgroup, m.group(m.lastgroup)
        if kind == "NAME" and text in KEYWORDS:
            kind = "KEYWORD"
        tokens.append(Token(kind, text))
        pos = m.end()
    tokens.append(Token("END", ""))
    return tokens

@dataclass
class Num:    value: float

@dataclass
class Var:    name: str

@dataclass
class BinOp:  op: str; left: object; right: object

@dataclass
class Neg:    operand: object

@dataclass
class Let:    name: str; value: object

@dataclass
class Assign: name: str; value: object

@dataclass
class Print:  value: object

@dataclass
class If:     cond: object; then: list; otherwise: list

@dataclass
class While:  cond: object; body: list

class Parser:
    def __init__(self, tokens):
        self.tokens, self.i = tokens, 0

    def peek(self):
        return self.tokens[self.i]
    def advance(self):
        tok = self.tokens[self.i]
        self.i += 1
        return tok
    def at(self, text):
        return self.peek().text == text and self.peek().kind in ("OP", "KEYWORD")
    def expect(self, text):
        if not self.at(text):
            raise SyntaxError(f"expected {text!r} but found {self.peek().text!r}")
        return self.advance()

    def program(self):
        stmts = []
        while self.peek().kind != "END":
            stmts.append(self.statement())
        return stmts

    def block(self):
        self.expect("{")
        stmts = []
        while not self.at("}"):
            stmts.append(self.statement())
        self.expect("}")
        return stmts

    def statement(self):
        if self.at("let"):
            self.advance(); name = self.advance().text; self.expect("=")
            value = self.expr(); self.expect(";")
            return Let(name, value)
        if self.at("print"):
            self.advance(); value = self.expr(); self.expect(";")
            return Print(value)
        if self.at("if"):
            self.advance(); cond = self.expr(); then = self.block(); otherwise = []
            if self.at("else"):
                self.advance(); otherwise = self.block()
            return If(cond, then, otherwise)
        if self.at("while"):
            self.advance(); cond = self.expr()
            return While(cond, self.block())
        if self.peek().kind == "NAME":
            name = self.advance().text; self.expect("=")
            value = self.expr(); self.expect(";")
            return Assign(name, value)
        raise SyntaxError(f"unexpected {self.peek().text!r}")

    def expr(self):                                       # comparison
        left = self.sum()
        for op in ("<=", ">=", "==", "!=", "<", ">"):
            if self.at(op):
                self.advance()
                return BinOp(op, left, self.sum())
        return left

    def sum(self):
        node = self.term()
        while self.at("+") or self.at("-"):
            op = self.advance().text
            node = BinOp(op, node, self.term())           # left-associative: (a - b) - c
        return node

    def term(self):
        node = self.unary()
        while self.at("*") or self.at("/") or self.at("%"):
            op = self.advance().text
            node = BinOp(op, node, self.unary())
        return node

    def unary(self):
        if self.at("-"):
            self.advance()
            return Neg(self.unary())
        return self.power()

    def power(self):
        base = self.atom()
        if self.at("**"):
            self.advance()
            return BinOp("**", base, self.unary())        # right-associative: 2 ** 3 ** 2 = 2 ** 9
        return base

    def atom(self):
        tok = self.advance()
        if tok.kind == "NUMBER":
            return Num(float(tok.text) if "." in tok.text else int(tok.text))
        if tok.kind == "NAME":
            return Var(tok.text)
        if tok.text == "(":
            node = self.expr()
            self.expect(")")
            return node
        raise SyntaxError(f"unexpected {tok.text!r}")

def parse(source):
    return Parser(tokenize(source)).program()

BINARY = {"+": operator.add, "-": operator.sub, "*": operator.mul, "/": operator.truediv, "%": operator.mod, "**": operator.pow,
          "<": operator.lt, ">": operator.gt, "<=": operator.le, ">=": operator.ge, "==": operator.eq, "!=": operator.ne}

factorial = """
let n = 10; let result = 1;
while n > 1 { result = result * n; n = n - 1; }
print result;
"""

@dataclass
class Instr:
    op: str
    arg: object = None
    def __repr__(self):
        return f"{self.op} {self.arg}" if self.arg is not None else self.op

class Compiler:
    def __init__(self):
        self.code = []
    def emit(self, op, arg=None):
        self.code.append(Instr(op, arg))
        return len(self.code) - 1                         # index of the instruction just emitted

    def expr(self, node):
        if isinstance(node, Num):
            self.emit("PUSH", node.value)
        elif isinstance(node, Var):
            self.emit("LOAD", node.name)
        elif isinstance(node, Neg):
            self.expr(node.operand); self.emit("NEG")
        elif isinstance(node, BinOp):
            self.expr(node.left); self.expr(node.right)   # postfix: both operands, then the operator
            self.emit(node.op)

    def stmts(self, stmts):
        for s in stmts:
            if isinstance(s, (Let, Assign)):
                self.expr(s.value); self.emit("STORE", s.name)
            elif isinstance(s, Print):
                self.expr(s.value); self.emit("PRINT")
            elif isinstance(s, If):
                self.expr(s.cond)
                jump_false = self.emit("JUMP_IF_FALSE", None)       # target patched below
                self.stmts(s.then)
                jump_end = self.emit("JUMP", None)
                self.code[jump_false].arg = len(self.code)           # false branch starts here
                self.stmts(s.otherwise)
                self.code[jump_end].arg = len(self.code)
            elif isinstance(s, While):
                start = len(self.code)
                self.expr(s.cond)
                jump_false = self.emit("JUMP_IF_FALSE", None)
                self.stmts(s.body)
                self.emit("JUMP", start)                              # back to re-test the condition
                self.code[jump_false].arg = len(self.code)

def compile_program(source):
    c = Compiler()
    c.stmts(parse(source))
    return c.code

class VM:
    def __init__(self, code):
        self.code, self.stack, self.env, self.output = code, [], {}, []

    def run(self):
        pc = 0
        while pc < len(self.code):
            ins = self.code[pc]
            pc += 1
            op = ins.op
            if op == "PUSH":
                self.stack.append(ins.arg)
            elif op == "LOAD":
                self.stack.append(self.env[ins.arg])
            elif op == "STORE":
                self.env[ins.arg] = self.stack.pop()
            elif op == "NEG":
                self.stack.append(-self.stack.pop())
            elif op == "PRINT":
                self.output.append(self.stack.pop())
            elif op == "JUMP":
                pc = ins.arg
            elif op == "JUMP_IF_FALSE":
                if not self.stack.pop():
                    pc = ins.arg
            else:                                              # binary operator
                right, left = self.stack.pop(), self.stack.pop()
                self.stack.append(BINARY[op](left, right))
        return self.output
```

</details>

## Problems

### The Python Data Model and CPython Internals

1. Write a descriptor `Typed(expected_type)` that raises `TypeError` unless the value has that type, and use it for a `Person` with `name: str` and `age: int`.
2. Show with `sys.getrefcount` how the count changes when you put an object in a list and then remove it.
3. Make two classes that reference each other in a cycle, add `weakref.ref` to break it, and show `gc.collect()` returns 0 for the weak version.
4. Use `__init_subclass__` to enforce that every subclass defines a `run` method.
5. Use `dis.get_instructions` to list the opcode names of `lambda a, b: a + b` and confirm it contains one `BINARY_OP`.
6. Explain why `d.__dict__["computed"] = "x"` did not override the property but did hide the method.

<details>
<summary>Solutions</summary>

1. ```python
   class Typed:
       def __init__(self, expected_type):
           self.expected_type = expected_type
       def __set_name__(self, owner, name):
           self.private = "_" + name
       def __get__(self, obj, objtype=None):
           return self if obj is None else getattr(obj, self.private)
       def __set__(self, obj, value):
           if not isinstance(value, self.expected_type):
               raise TypeError(f"expected {self.expected_type.__name__}, got {type(value).__name__}")
           setattr(obj, self.private, value)
   class Person:
       name = Typed(str)
       age = Typed(int)
       def __init__(self, name, age):
           self.name, self.age = name, age
   print(Person("Ada", 36).age)
   try:
       Person("Ada", "36")
   except TypeError as e:
       print(e)
   # 36
   # expected int, got str
   ```
2. ```python
   import sys
   obj = object()
   before = sys.getrefcount(obj)
   holder = [obj]
   during = sys.getrefcount(obj)
   holder.clear()
   after = sys.getrefcount(obj)
   print(during - before, after - before)
   # 1 0
   ```
3. ```python
   import gc, weakref
   class Parent:
       pass
   class Child:
       pass
   p, c = Parent(), Child()
   p.child = c
   c.parent = weakref.ref(p)                     # weak back-reference: no cycle of strong references
   del p, c
   print(gc.collect())
   # 0
   ```
4. ```python
   class Task:
       def __init_subclass__(cls, **kw):
           super().__init_subclass__(**kw)
           if "run" not in cls.__dict__:
               raise TypeError(f"{cls.__name__} must define run()")
   class Good(Task):
       def run(self): pass
   try:
       class Bad(Task):
           pass
   except TypeError as e:
       print(e)
   # Bad must define run()
   ```
5. ```python
   import dis
   names = [i.opname for i in dis.get_instructions(lambda a, b: a + b)]
   print(names.count("BINARY_OP"))
   # 1
   ```
   (The loads of `a` and `b` use `LOAD_FAST`-family instructions; recent versions may fuse them into one, so the exact list differs between releases, but there is always exactly one addition.)
6. `property` defines `__set__`, so it is a **data descriptor** and takes priority over the instance `__dict__`. A plain function defines only `__get__` (a **non-data descriptor**), so an entry with the same name in the instance `__dict__` takes priority over it.

</details>

### Build a Tiny Interpreter

1. Add the `and`, `or` and `not` operators (with precedence lower than comparisons, `not` binding tighter than `and`, and `and` tighter than `or`).
2. Add `else if` support by letting `else` be followed by an `if` statement.
3. Make the VM raise a clear `NameError` for an undefined variable and show that division by zero raises `ZeroDivisionError`.
4. Add constant folding to the compiler: if both operands of a `BinOp` are `Num`, emit one `PUSH` of the computed value.
5. Count how many instructions the VM executes for the factorial program, and how many calls `Interpreter.evaluate` makes for the same program.
6. Explain why `10 - 3 - 2` needs the `while` loop in `sum` rather than a recursive call to `sum`.

<details>
<summary>Solutions</summary>

1. ```python
   # grammar: expr := orexpr ; orexpr := andexpr {"or" andexpr}; andexpr := notexpr {"and" notexpr};
   #          notexpr := "not" notexpr | comparison
   # Add "and", "or", "not" to KEYWORDS and the tokenizer; rename the old `expr` method to `comparison`;
   # then write expr/andexpr/notexpr as loops exactly like `sum` and `term`, building BinOp("and", l, r) and a Not node.
   # Because `and` and `or` must short-circuit, handle them in Interpreter.evaluate before evaluating the right operand,
   # and compile them with JUMP_IF_FALSE.
   ```
2. ```python
   # in Parser.statement, inside the `if` branch:
   #     if self.at("else"):
   #         self.advance()
   #         otherwise = [self.statement()] if self.at("if") else self.block()
   ```
3. ```python
   # in VM.run, LOAD branch:
   #     if ins.arg not in self.env: raise NameError(f"undefined variable {ins.arg!r}")
   try:
       VM(compile_program("print 1 / 0;")).run()
   except ZeroDivisionError as e:
       print("ZeroDivisionError:", e)
   # ZeroDivisionError: division by zero
   ```
4. ```python
   # in Compiler.expr, BinOp branch, before emitting:
   #     if isinstance(node.left, Num) and isinstance(node.right, Num):
   #         self.emit("PUSH", BINARY[node.op](node.left.value, node.right.value)); return
   ```
   (Folding nested constants needs the fold applied recursively, bottom-up.)
5. ```python
   class CountingVM(VM):
       def run(self):
           self.steps = 0
           pc = 0
           while pc < len(self.code):
               self.steps += 1
               ins = self.code[pc]; pc += 1
               if ins.op == "PUSH": self.stack.append(ins.arg)
               elif ins.op == "LOAD": self.stack.append(self.env[ins.arg])
               elif ins.op == "STORE": self.env[ins.arg] = self.stack.pop()
               elif ins.op == "NEG": self.stack.append(-self.stack.pop())
               elif ins.op == "PRINT": self.output.append(self.stack.pop())
               elif ins.op == "JUMP": pc = ins.arg
               elif ins.op == "JUMP_IF_FALSE":
                   if not self.stack.pop(): pc = ins.arg
               else:
                   right, left = self.stack.pop(), self.stack.pop()
                   self.stack.append(BINARY[ins.op](left, right))
           return self.output
   vm = CountingVM(compile_program(factorial))
   vm.run()
   print(vm.steps)
   # 127
   ```
   Do the same for the tree walker by wrapping `evaluate` with a counter: it makes a Python-level call per node, which is why compiled forms are faster.
6. A recursive call would build `10 - (3 - 2)`, which is right-associative and gives 9. The loop builds `(10 - 3) - 2` by repeatedly making the node-so-far the **left** child, which gives 5.

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [The Python Data Model and CPython Internals](01-python-data-model-and-internals.md) · [Build a Tiny Interpreter](02-build-a-tiny-interpreter.md)
