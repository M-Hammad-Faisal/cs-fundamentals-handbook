# Memento Pattern

**Family:** behavioral · **Also called:** snapshot, checkpoint · **How often you will use it:** occasionally (undo, save games) · **Difficulty:** easy to medium

## 1. In plain words

A **Memento** is a **saved snapshot of an object's state** that lets you **restore it later**, without exposing the object's private internals.

Analogy: a **video-game save point**. You save, try something risky, and if it goes wrong you reload exactly where you were.

## 2. The problem

You want undo or rollback, but copying an object's state from outside would require breaking encapsulation (reading private fields), and the object needs a clean way to restore itself.

## 3. The solution

```text
Originator ──creates──► Memento (opaque, immutable snapshot)
   ▲                            │
   └────── restore(memento) ◄───┘          Caretaker keeps the snapshots (history list)
```

Roles: **Originator** (the object whose state is saved; creates and restores mementos), **Memento** (the snapshot; others cannot change it), **Caretaker** (stores mementos; does not inspect them).

## 4. Step by step

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Snapshot:                                         # the memento: immutable
    text: str
    cursor: int

class Document:                                         # the originator
    def __init__(self):
        self.text, self.cursor = "", 0

    def type(self, s):
        self.text = self.text[:self.cursor] + s + self.text[self.cursor:]
        self.cursor += len(s)

    def save(self):
        return Snapshot(self.text, self.cursor)         # create a snapshot

    def restore(self, snapshot):
        self.text, self.cursor = snapshot.text, snapshot.cursor

doc = Document()
checkpoints = []                                        # the caretaker
doc.type("hello");  checkpoints.append(doc.save())
doc.type(" world"); checkpoints.append(doc.save())
doc.type("!!!")
print(doc.text)                                         # hello world!!!
doc.restore(checkpoints[0])
print(doc.text, doc.cursor)                             # hello 5
```

### An undo stack with a size limit

```python
from collections import deque

class Editor:
    def __init__(self, max_history=3):
        self.doc = Document()
        self.history = deque(maxlen=max_history)        # old snapshots fall off the far end

    def type(self, s):
        self.history.append(self.doc.save())            # snapshot BEFORE changing
        self.doc.type(s)

    def undo(self):
        if self.history:
            self.doc.restore(self.history.pop())

e = Editor()
for word in ("a", "b", "c", "d"):
    e.type(word)
print(e.doc.text)                                       # abcd
e.undo(); e.undo(); e.undo()
print(e.doc.text)                                       # a   (only the last 3 steps could be undone)
e.undo()
print(e.doc.text)                                       # a   (nothing more to undo)
```

## 5. The Pythonic way

- A **frozen dataclass** or a `NamedTuple` is a perfect memento.
- For simple objects, `copy.deepcopy(obj)` or `pickle`-free serialization (JSON of the state) is enough: `state = copy.deepcopy(self.__dict__)`.
- `dataclasses.replace` and immutable data make snapshots trivial (just keep the old object).
- Databases give you mementos as **transactions and savepoints**; version control is a memento history for files.

```python
import copy

class Settings:
    def __init__(self): self.options = {"theme": "light"}
    def snapshot(self): return copy.deepcopy(self.options)
    def restore(self, snap): self.options = snap

s = Settings(); saved = s.snapshot()
s.options["theme"] = "dark"
s.restore(saved)
print(s.options)                                        # {'theme': 'light'}
```

## 6. When to use it (and when not to)

**Use it when** you need undo/redo, checkpoints, rollback after a failed operation, save/load, or "try and revert" (dry runs).

**Skip it when** state is huge and snapshots are expensive (store diffs with [Command](command.md) instead), or when the state includes external resources you cannot restore.

## 7. Pros and cons

| Pros | Cons |
|------|------|
| Restore state without exposing internals | Memory heavy if snapshots are big or frequent |
| Simple undo/rollback | Caretaker must manage history limits |
| Immutable snapshots are safe | Cannot restore external side effects (sent emails, deleted files) |

## 8. Related patterns

- [Command](command.md): undo by storing the inverse operation; Memento undoes by restoring a snapshot (they are often used together).
- [Prototype](../creational/prototype.md): copying objects to create new ones; Memento copies state to restore.
- [Iterator](iterator.md): an iterator may store its position as a memento.

## 9. Two real-world examples

**Example 1: Editors and drawing apps.** Each significant edit saves a snapshot (or a diff) so Ctrl+Z can restore the previous document state.

**Example 2: Database transactions.** `SAVEPOINT before_risky_step;` ... `ROLLBACK TO before_risky_step;` is a memento managed by the database engine.

## 10. Common mistakes

- Making snapshots mutable, so history is silently corrupted.
- Sharing mutable state between the snapshot and the live object (needs deep copy).
- Unbounded history (memory growth).
- Expecting a snapshot to undo side effects outside the object.

## 11. Practice

1. Add `redo()` to the `Editor` (keep a second stack).
2. Implement save points for a game `Player` (`hp`, `inventory` list) and show restoring after dying.
3. Compare snapshot undo with command undo for a 10 MB document.

<details>
<summary>Solutions</summary>

**1.**
```python
class Editor2(Editor):
    def __init__(self, max_history=10):
        super().__init__(max_history)
        self.redo_stack = []
    def type(self, s):
        super().type(s); self.redo_stack.clear()
    def undo(self):
        if self.history:
            self.redo_stack.append(self.doc.save())
            self.doc.restore(self.history.pop())
    def redo(self):
        if self.redo_stack:
            self.history.append(self.doc.save())
            self.doc.restore(self.redo_stack.pop())
e2 = Editor2(); e2.type("a"); e2.type("b"); e2.undo(); print(e2.doc.text); e2.redo(); print(e2.doc.text)   # a ab
```

**2.**
```python
class Player:
    def __init__(self): self.hp, self.inventory = 100, ["sword"]
    def save(self): return copy.deepcopy((self.hp, self.inventory))
    def load(self, s): self.hp, self.inventory = copy.deepcopy(s)
p = Player(); save = p.save()
p.hp = 0; p.inventory.clear()
p.load(save); print(p.hp, p.inventory)                  # 100 ['sword']
```

**3.** A snapshot per edit copies up to 10 MB each time (memory grows quickly); a command stores only "inserted 'x' at 120" and its inverse, a few bytes, but needs a correct `undo` for every action. Hybrid: occasional snapshots plus commands between them.

</details>

## 12. Check yourself

1. What are the three roles?
2. Why should mementos be immutable?
3. Command undo versus Memento undo?
4. What cannot a memento restore?

<details>
<summary>Answers</summary>

1. Originator (creates and restores), Memento (the snapshot), Caretaker (stores them).
2. History must stay accurate; a mutable snapshot could be changed after saving.
3. Command stores the inverse action (small, needs correct `undo`); Memento stores the whole prior state (simple, memory heavy).
4. External side effects such as emails sent, files deleted elsewhere, network calls.

</details>

## More examples

Runnable script (added to your companion repository with this lesson): [`behavioralPattern/mementoPattern.py`](https://github.com/M-Hammad-Faisal/design-patterns-python/blob/master/behavioralPattern/mementoPattern.py)

[Family overview](README.md) · [All patterns](../README.md)
