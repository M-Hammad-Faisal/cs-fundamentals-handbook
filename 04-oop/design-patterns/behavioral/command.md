# Command Pattern

**Family:** behavioral · **Also called:** action, transaction · **How often you will use it:** often (undo, queues, jobs) · **Difficulty:** medium

## 1. In plain words

A **Command** turns a **request into an object**. Because an action is now a thing you can hold, you can **store it, queue it, log it, send it elsewhere, or undo it**.

Analogy: a **restaurant order slip**. The waiter writes your wish on a slip and hands it to the kitchen. The slip can wait in a queue, be logged, or be cancelled. The waiter does not cook; the kitchen does not talk to customers.

## 2. The problem

Calling methods directly means you cannot easily delay, repeat, record or reverse them:

```python
editor.insert("Hello")      # done and gone: no history, no undo, no replay
editor.delete_last(3)
```

## 3. The solution

```text
Invoker ──executes──► Command (execute(), undo())
(History / queue)          ▲
                   ┌───────┴────────┐
             InsertCommand     DeleteCommand ──acts on──► Receiver (TextEditor)
```

Roles: **Command** (an action with `execute`, often `undo`), **Receiver** (does the real work), **Invoker** (runs commands, keeps history), **Client** (builds commands).

## 4. Step by step: a text editor with undo and redo

```python
class TextEditor:                                       # the receiver
    def __init__(self):
        self.text = ""

class InsertCommand:
    def __init__(self, editor, s):
        self.editor, self.s = editor, s
    def execute(self):
        self.editor.text += self.s
    def undo(self):
        self.editor.text = self.editor.text[:-len(self.s)]

class DeleteLastCommand:
    def __init__(self, editor, n):
        self.editor, self.n, self.removed = editor, n, ""
    def execute(self):
        self.removed = self.editor.text[-self.n:]       # remember what we remove, so undo can restore it
        self.editor.text = self.editor.text[:-self.n]
    def undo(self):
        self.editor.text += self.removed

class History:                                          # the invoker
    def __init__(self):
        self._done, self._undone = [], []
    def run(self, command):
        command.execute()
        self._done.append(command)
        self._undone.clear()                            # a new action invalidates the redo stack
    def undo(self):
        if self._done:
            cmd = self._done.pop()
            cmd.undo()
            self._undone.append(cmd)
    def redo(self):
        if self._undone:
            cmd = self._undone.pop()
            cmd.execute()
            self._done.append(cmd)

editor, history = TextEditor(), History()
history.run(InsertCommand(editor, "Hello"))
history.run(InsertCommand(editor, " world"))
history.run(DeleteLastCommand(editor, 3))
print(repr(editor.text))                                # 'Hello wo'
history.undo(); print(repr(editor.text))                # 'Hello world'
history.undo(); print(repr(editor.text))                # 'Hello'
history.redo(); print(repr(editor.text))                # 'Hello world'
```

### A job queue (commands run later)

```python
import queue

jobs = queue.Queue()
jobs.put(InsertCommand(editor, "!"))
jobs.put(InsertCommand(editor, "?"))
while not jobs.empty():
    jobs.get().execute()                                # executed later, perhaps by another worker
print(editor.text)                                      # Hello world!?
```

### A macro (a command made of commands)

```python
class MacroCommand:
    def __init__(self, *commands):
        self.commands = commands
    def execute(self):
        for c in self.commands: c.execute()
    def undo(self):
        for c in reversed(self.commands): c.undo()      # undo in reverse order

ed2 = TextEditor()
macro = MacroCommand(InsertCommand(ed2, "a"), InsertCommand(ed2, "b"), InsertCommand(ed2, "c"))
macro.execute(); print(ed2.text)                        # abc
macro.undo(); print(repr(ed2.text))                     # ''
```

## 5. The Pythonic way

- A command is often just a **callable**: `functools.partial(func, arg)` or a closure, stored in a list.
- Use `functools.partial` for "function + arguments" objects; add an `undo` callable alongside when needed.
- **Task queues** (Celery, RQ, Dramatiq) are distributed Command systems: a task name plus arguments is serialized, sent, and executed later with retries.

```python
from functools import partial

actions = [partial(print, "hello"), partial(print, "a", "b", sep="-")]
for a in actions:
    a()                                                  # hello  /  a-b
```

## 6. When to use it (and when not to)

**Use it when** you need undo/redo, queuing or scheduling work, logging every action (audit, event sourcing), retrying failed operations, macros/batch operations, or decoupling "who asks" from "who performs".

**Skip it when** a direct function call is enough and none of those needs exists.

## 7. Pros and cons

| Pros | Cons |
|------|------|
| Undo/redo, queues and logs become easy | More small classes |
| Decouples the invoker from the receiver | Every command must correctly implement `undo` |
| Compose commands into macros | Storing state for undo can be heavy |
| Open/Closed: add new commands freely | |

## 8. Related patterns

- [Memento](memento.md): stores state snapshots for undo; Command stores the inverse action.
- [Observer](observer.md): notifies many; Command packages one request.
- [Chain of Responsibility](chain-of-responsibility.md): a request may travel along handlers.
- [Strategy](strategy.md): chooses an algorithm; Command represents a request.
- [Composite](../structural/composite.md): macro commands are composites.

## 9. Two real-world examples

**Example 1: Undo in an editor or drawing app.** Each user action (type, delete, move shape) is a command pushed on a stack. Ctrl+Z pops and calls `undo()`.

**Example 2: Celery tasks.** `send_welcome_email.delay(user_id)` serializes "run `send_welcome_email` with `user_id`" into a message. A worker picks it up later, runs it, and retries it if it fails.

## 10. Common mistakes

- Forgetting to capture the information needed for `undo` (such as the removed text).
- Not clearing the redo stack after a new action.
- Commands that depend on shared mutable state that has changed by the time they run.
- Undoing in the wrong order for macros.

## 11. Practice

1. Implement a `Calculator` with `Add` and `Multiply` commands supporting undo/redo.
2. Add a `MacroCommand` that is undone in reverse.
3. Make a command queue that retries failed commands up to 3 times.

<details>
<summary>Solutions</summary>

**1.**
```python
class Calc:
    def __init__(self): self.value = 0
class Add:
    def __init__(self, c, n): self.c, self.n = c, n
    def execute(self): self.c.value += self.n
    def undo(self): self.c.value -= self.n
class Mul:
    def __init__(self, c, n): self.c, self.n, self.prev = c, n, None
    def execute(self): self.prev = self.c.value; self.c.value *= self.n
    def undo(self): self.c.value = self.prev
calc, hist = Calc(), History()
hist.run(Add(calc, 5)); hist.run(Mul(calc, 3)); print(calc.value)          # 15
hist.undo(); print(calc.value); hist.undo(); print(calc.value); hist.redo(); print(calc.value)   # 5 0 5
```

**2.** See `MacroCommand` in the lesson (its `undo` loops `reversed(self.commands)`).

**3.**
```python
def run_with_retries(command, attempts=3):
    for n in range(1, attempts + 1):
        try:
            return command()
        except Exception:
            if n == attempts:
                raise
tries = []
def flaky():
    tries.append(1)
    if len(tries) < 3: raise RuntimeError
    return "ok"
print(run_with_retries(flaky), len(tries))                                  # ok 3
```

</details>

## 12. Check yourself

1. What does it mean to "turn a request into an object"?
2. What two things must a command remember to support undo?
3. Why clear the redo stack on a new action?
4. How do task queues relate to Command?

<details>
<summary>Answers</summary>

1. Represent the action (what to do, and with which arguments) as an object you can store, pass around, queue, log or reverse.
2. What to do (`execute`) and enough state to reverse it (`undo`), such as the removed text or previous value.
3. The redo history no longer applies once the state has diverged.
4. A queued task is a serialized command (name plus arguments) executed later by a worker, often with retries.

</details>

## More examples

Runnable script (added to your companion repository with this lesson): [`behavioralPattern/commandPattern.py`](https://github.com/M-Hammad-Faisal/design-patterns-python/blob/master/behavioralPattern/commandPattern.py)

[Family overview](README.md) · [All patterns](../README.md)
