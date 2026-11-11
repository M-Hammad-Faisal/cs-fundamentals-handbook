# Build a Tiny Interpreter: Tokens, Parser, Evaluator and Bytecode VM

**Prerequisites:** [recursion](../../03-algorithms/recursion-backtracking/README.md), [stacks and queues](../../02-data-structures/stacks-queues/README.md), [trees](../../02-data-structures/trees/README.md), [dataclasses](../dataclasses-enums/README.md), [the Python data model and internals](01-python-data-model-and-internals.md) (bytecode). **You will learn:** how a programming language implementation works by building one: a **tokenizer** (lexer), a **recursive-descent parser** that builds an **abstract syntax tree**, a **tree-walking interpreter**, and a **compiler to stack bytecode** with a **virtual machine**, the same pipeline CPython uses. You end with a working language that has variables, arithmetic, `if`, `while` and `print`, verified against an independent oracle.

## 1. In plain words

A computer cannot run text like `let x = 2 + 3 * 4;`. Something must turn the characters into meaning and then act on it. Every language implementation does this in stages:

```
source text  ->  tokens  ->  syntax tree (AST)  ->  run it directly (interpreter)
                                                \->  bytecode -> virtual machine (compiler + VM)
```

- **Tokenizing** groups characters into words and symbols: `let`, `x`, `=`, `2`, `+`.
- **Parsing** checks the grammar and builds a **tree** that captures structure and precedence: `2 + 3 * 4` becomes `2 + (3 * 4)`.
- **Interpreting** walks the tree and computes results; **compiling** instead flattens the tree into simple instructions for a fast loop (the VM).

## 2. The language

```
program   := statement*
statement := "let" NAME "=" expr ";"       declare a variable
           | NAME "=" expr ";"             assign
           | "print" expr ";"
           | "if" expr "{" statement* "}" [ "else" "{" statement* "}" ]
           | "while" expr "{" statement* "}"
expr      := sum [ ("<" | ">" | "<=" | ">=" | "==" | "!=") sum ]
sum       := term  { ("+" | "-") term }
term      := unary { ("*" | "/" | "%") unary }
unary     := "-" unary | power
power     := atom [ "**" unary ]
atom      := NUMBER | NAME | "(" expr ")"
```

The grammar's **layering encodes precedence**: `sum` is built from `term`s, so `*` binds tighter than `+`. This is the key idea of a recursive-descent parser: **one function per grammar rule**.

## 3. Step 1: the tokenizer

```python
import re
from dataclasses import dataclass

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

print([(t.kind, t.text) for t in tokenize("let x = 2 + 3 * 4;")])
# [('KEYWORD', 'let'), ('NAME', 'x'), ('OP', '='), ('NUMBER', '2'), ('OP', '+'), ('NUMBER', '3'), ('OP', '*'), ('NUMBER', '4'), ('OP', ';'), ('END', '')]
```

## 4. Step 2: the parser and the AST

Each AST node is a small dataclass. The parser has one method per grammar rule, a **cursor** over the tokens, and helpers to **peek** and **expect**.

```python
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

print(parse("let x = 2 + 3 * 4;")[0])
# Let(name='x', value=BinOp(op='+', left=Num(value=2), right=BinOp(op='*', left=Num(value=3), right=Num(value=4))))
```

The tree shows precedence: the `*` is **deeper** than the `+`, so it is evaluated first. A syntax error gives a clear message:

```python
try:
    parse("let x = 2 + ;")
except SyntaxError as e:
    print("SyntaxError:", e)
# SyntaxError: unexpected ';'
```

## 5. Step 3: a tree-walking interpreter

The simplest way to run an AST: a method that **recursively evaluates each node**.

```python
import operator

BINARY = {"+": operator.add, "-": operator.sub, "*": operator.mul, "/": operator.truediv, "%": operator.mod, "**": operator.pow,
          "<": operator.lt, ">": operator.gt, "<=": operator.le, ">=": operator.ge, "==": operator.eq, "!=": operator.ne}

class Interpreter:
    def __init__(self):
        self.env, self.output = {}, []

    def evaluate(self, node):
        if isinstance(node, Num):
            return node.value
        if isinstance(node, Var):
            if node.name not in self.env:
                raise NameError(f"undefined variable {node.name!r}")
            return self.env[node.name]
        if isinstance(node, Neg):
            return -self.evaluate(node.operand)
        if isinstance(node, BinOp):
            return BINARY[node.op](self.evaluate(node.left), self.evaluate(node.right))
        raise TypeError(f"cannot evaluate {node!r}")

    def run(self, stmts):
        for s in stmts:
            if isinstance(s, (Let, Assign)):
                self.env[s.name] = self.evaluate(s.value)
            elif isinstance(s, Print):
                self.output.append(self.evaluate(s.value))
            elif isinstance(s, If):
                self.run(s.then if self.evaluate(s.cond) else s.otherwise)
            elif isinstance(s, While):
                while self.evaluate(s.cond):
                    self.run(s.body)
        return self.output

factorial = """
let n = 10; let result = 1;
while n > 1 { result = result * n; n = n - 1; }
print result;
"""
print(Interpreter().run(parse(factorial)))
# [3628800]

fib = """
let a = 0; let b = 1; let i = 0;
while i < 10 { print a; let t = a + b; a = b; b = t; i = i + 1; }
"""
print(Interpreter().run(parse(fib)))
# [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

print(Interpreter().run(parse("print 2 + 3 * 4; print (2 + 3) * 4; print 2 ** 3 ** 2; print -2 ** 2; print 7 % 4; print 10 - 3 - 2;")))
# [14, 20, 512, -4, 3, 5]
```

Check the precedence results: `2 ** 3 ** 2 = 2 ** 9 = 512` (power is right-associative), `-2 ** 2 = -(2 ** 2) = -4`, and `10 - 3 - 2 = (10 - 3) - 2 = 5` (left-associative). Our `let` inside a loop assigns an existing name, which is fine for this small language (it has a single flat scope).

## 6. Step 4: compile to bytecode and run on a VM

A tree walker is simple but slow: every node visit costs Python function calls. Real implementations **compile** the tree into a flat list of instructions for a stack machine. Expressions become **postfix** order (operands first, then the operator), loops and branches become **jumps**.

```python
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

print(compile_program("let x = 2 + 3 * 4; print x;"))
# [PUSH 2, PUSH 3, PUSH 4, *, +, STORE x, LOAD x, PRINT]

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

print(VM(compile_program(factorial)).run())
print(VM(compile_program(fib)).run())
# [3628800]
# [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

The listing `PUSH 2, PUSH 3, PUSH 4, *, +, STORE x` is the same shape as what Python's `dis` shows for `x = 2 + 3 * 4` (without the constant folding): a **stack machine** pushes operands and operators pop them. The VM is a simple loop with a **program counter** `pc`; jumps just set `pc`.

## 7. Testing against an independent oracle

How do you know the parser's precedence and the evaluator are right? Generate **random expression trees**, compute each one's expected value **while generating it** (so the oracle does not depend on our parser), print it as source text, and compare all three implementations.

```python
import random

def random_expr(rng, depth=0):
    """Return (source_text, expected_value). Uses only +, -, * on small integers, always parenthesised, so the oracle is trivially correct."""
    if depth > 3 or rng.random() < 0.3:
        n = rng.randint(0, 9)
        return str(n), n
    (ls, lv), (rs, rv) = random_expr(rng, depth + 1), random_expr(rng, depth + 1)
    op = rng.choice("+-*")
    value = {"+": lv + rv, "-": lv - rv, "*": lv * rv}[op]
    return f"({ls} {op} {rs})", value

rng = random.Random(0)
failures = 0
for _ in range(500):
    text, expected = random_expr(rng)
    program = f"print {text};"
    if Interpreter().run(parse(program)) != [expected] or VM(compile_program(program)).run() != [expected]:
        failures += 1
print("random expressions where either implementation disagreed with the oracle:", failures, "of 500")
# random expressions where either implementation disagreed with the oracle: 0 of 500
```

For precedence without parentheses we check specific cases against hand-computed values (already done in section 5) and against Python's own arithmetic rules, which this language copies:

```python
cases = {"1 + 2 * 3 - 4": 3, "2 * 3 % 4": 2, "2 ** 2 ** 3": 256, "-3 + 5": 2, "1 - 2 - 3": -4, "(1 + 2) * (3 + 4)": 21}
print(all(Interpreter().run(parse(f"print {src};")) == [want] for src, want in cases.items()))
# True
```

## 8. How this compares with CPython

| Stage | Our toy | CPython |
|-------|---------|---------|
| Lexing | one regex | a hand-written tokenizer |
| Parsing | recursive descent | a PEG parser producing an AST (the `ast` module shows it) |
| Analysis | none | symbol tables, scopes, constant folding |
| Bytecode | `PUSH`, `LOAD`, `STORE`, jumps | `LOAD_FAST`, `BINARY_OP`, `POP_JUMP_IF_FALSE`... (see `dis`) |
| Execution | a Python loop | a C loop with adaptive specialisation (and an optional JIT) |

```python
import ast
tree = ast.parse("x = 2 + 3 * 4")
print(ast.dump(tree.body[0].value, annotate_fields=False))
# BinOp(Constant(2), Add(), BinOp(Constant(3), Mult(), Constant(4)))
```

Python's own AST has the same shape as ours (`BinOp` with a nested `BinOp` for the multiplication). The ideas scale up: type checkers, linters, formatters, transpilers, SQL engines and template languages all use a tokenizer, a parser and an AST.

## 9. Common mistakes

- Writing the grammar with left recursion (`expr := expr + term`), which makes a recursive-descent parser loop forever; use a loop for repetition instead.
- Getting associativity wrong (`**` is right-associative; `-` and `/` are left-associative).
- Forgetting to check for the end of input, so trailing garbage is silently accepted.
- Evaluating the same sub-tree repeatedly inside loops in a tree walker (compile once instead).
- Error messages without positions; real tools record line and column in each token.
- Treating Python's dynamic-evaluation built-ins as an acceptable shortcut for user-written rules: an interpreter you control is the safe alternative (see [secure Python](../../10-security/threat-modeling/01-threat-modeling-and-secure-python.md)).

## 10. Two real-world examples

**Example 1: A rules engine.** A shop let staff write discount rules like `total > 100 and customer_age >= 18`. Instead of running staff text as Python, the team wrote a small tokenizer, parser and evaluator very similar to this one, supporting only comparisons, `and`/`or` and a whitelist of variables. Rules were validated at save time, evaluated safely and explained back to the user.

**Example 2: Query planning.** A database parses SQL into an AST, rewrites the tree (push filters down, reorder joins) and then compiles it into an execution plan. The same tokenizer, parser, tree transformation pipeline you just built, with an optimiser in the middle.

## 11. Practice

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

## 12. Check yourself

1. What are the four stages from source text to running code in this lesson?
2. What does the layering of grammar rules (`sum` built from `term`) encode?
3. Why is left recursion a problem for recursive descent, and what replaces it?
4. What is the difference between a tree-walking interpreter and a bytecode VM?
5. In postfix order, what is `2 + 3 * 4`?
6. How do `while` loops become jumps?
7. How did we test the parser independently of itself?

<details>
<summary>Answers</summary>

1. Tokenize, parse into an AST, then either interpret the tree directly or compile it to bytecode and run it on a VM.
2. Operator precedence: operators lower in the grammar (`*`) bind tighter than ones above it (`+`).
3. A rule that calls itself first without consuming a token recurses forever; use a loop to repeat `{ op term }` instead.
4. A tree walker recursively evaluates nodes; a VM runs a flat list of simple instructions with a program counter and a stack, which is faster and easier to optimise.
5. `2 3 4 * +`.
6. The condition is tested at the top; a conditional jump leaves the loop when false; at the end of the body an unconditional jump returns to the test.
7. By generating random expression trees whose expected values were computed during generation, so the oracle does not use the parser or evaluator under test.

</details>

[Back to Modern Python](../README.md)
