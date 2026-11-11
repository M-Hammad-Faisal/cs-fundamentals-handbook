# Python Internals: Exercises

Try each problem before opening its solution. These are the practice problems of this topic's lessons, collected in one place.

## The Python Data Model and CPython Internals

1. Write a descriptor `Typed(expected_type)` that raises `TypeError` unless the value has that type, and use it for a `Person` with `name: str` and `age: int`.
2. Show with `sys.getrefcount` how the count changes when you put an object in a list and then remove it.
3. Make two classes that reference each other in a cycle, add `weakref.ref` to break it, and show `gc.collect()` returns 0 for the weak version.
4. Use `__init_subclass__` to enforce that every subclass defines a `run` method.
5. Use `dis.get_instructions` to list the opcode names of `lambda a, b: a + b` and confirm it contains one `BINARY_OP`.
6. Explain why `d.__dict__["computed"] = "x"` did not override the property but did hide the method.

<details>
<summary>Solutions</summary>

1. ```python no-run
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
2. ```python no-run
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
3. ```python no-run
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
4. ```python no-run
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
5. ```python no-run
   import dis
   names = [i.opname for i in dis.get_instructions(lambda a, b: a + b)]
   print(names.count("BINARY_OP"))
   # 1
   ```
   (The loads of `a` and `b` use `LOAD_FAST`-family instructions; recent versions may fuse them into one, so the exact list differs between releases, but there is always exactly one addition.)
6. `property` defines `__set__`, so it is a **data descriptor** and takes priority over the instance `__dict__`. A plain function defines only `__get__` (a **non-data descriptor**), so an entry with the same name in the instance `__dict__` takes priority over it.

</details>

## Build a Tiny Interpreter

1. Add the `and`, `or` and `not` operators (with precedence lower than comparisons, `not` binding tighter than `and`, and `and` tighter than `or`).
2. Add `else if` support by letting `else` be followed by an `if` statement.
3. Make the VM raise a clear `NameError` for an undefined variable and show that division by zero raises `ZeroDivisionError`.
4. Add constant folding to the compiler: if both operands of a `BinOp` are `Num`, emit one `PUSH` of the computed value.
5. Count how many instructions the VM executes for the factorial program, and how many calls `Interpreter.evaluate` makes for the same program.
6. Explain why `10 - 3 - 2` needs the `while` loop in `sum` rather than a recursive call to `sum`.

<details>
<summary>Solutions</summary>

1. ```python no-run
   # grammar: expr := orexpr ; orexpr := andexpr {"or" andexpr}; andexpr := notexpr {"and" notexpr};
   #          notexpr := "not" notexpr | comparison
   # Add "and", "or", "not" to KEYWORDS and the tokenizer; rename the old `expr` method to `comparison`;
   # then write expr/andexpr/notexpr as loops exactly like `sum` and `term`, building BinOp("and", l, r) and a Not node.
   # Because `and` and `or` must short-circuit, handle them in Interpreter.evaluate before evaluating the right operand,
   # and compile them with JUMP_IF_FALSE.
   ```
2. ```python no-run
   # in Parser.statement, inside the `if` branch:
   #     if self.at("else"):
   #         self.advance()
   #         otherwise = [self.statement()] if self.at("if") else self.block()
   ```
3. ```python no-run
   # in VM.run, LOAD branch:
   #     if ins.arg not in self.env: raise NameError(f"undefined variable {ins.arg!r}")
   try:
       VM(compile_program("print 1 / 0;")).run()
   except ZeroDivisionError as e:
       print("ZeroDivisionError:", e)
   # ZeroDivisionError: division by zero
   ```
4. ```python no-run
   # in Compiler.expr, BinOp branch, before emitting:
   #     if isinstance(node.left, Num) and isinstance(node.right, Num):
   #         self.emit("PUSH", BINARY[node.op](node.left.value, node.right.value)); return
   ```
   (Folding nested constants needs the fold applied recursively, bottom-up.)
5. ```python no-run
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
