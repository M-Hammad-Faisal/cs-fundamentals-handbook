# Iterator Pattern

**Family:** behavioral · **How often you will use it:** constantly (it is built into Python) · **Difficulty:** easy once you know `yield`

## 1. In plain words

An **Iterator** lets you **walk through the items of a collection one at a time** without knowing (or caring) how the collection stores them: list, tree, database cursor, file, network stream.

Analogy: a **TV remote's "next channel" button**. You do not need to know how channels are stored; you just press next until you are back where you started.

## 2. The problem

Each collection is traversed differently, and callers would need to know the internals:

```python no-run
for i in range(len(items)): ...      # works for lists, not for trees, files, or infinite streams
node = tree.root                     # for a tree you must know left/right pointers and write a recursive walk
```

## 3. The solution

```text
Collection ──creates──► Iterator (next item, or "done")
Client: for item in collection:   ← same loop for every kind of collection
```

In Python the protocol has two methods: `__iter__()` returns an **iterator**; `__next__()` returns the next value or raises `StopIteration`.

## 4. Step by step

### A class-based iterator (the explicit protocol)

```python
class Countdown:
    def __init__(self, start):
        self.start = start

    def __iter__(self):                                 # called by for / list() / sum() ...
        return CountdownIterator(self.start)

class CountdownIterator:
    def __init__(self, n):
        self.n = n
    def __iter__(self):
        return self
    def __next__(self):
        if self.n <= 0:
            raise StopIteration                         # signals "no more items"
        self.n -= 1
        return self.n + 1

c = Countdown(3)
print(list(c), list(c))                                 # [3, 2, 1] [3, 2, 1]   (fresh iterator each time: reusable)
```

### The easy way: a generator

```python
class Countdown2:
    def __init__(self, start): self.start = start
    def __iter__(self):
        n = self.start
        while n > 0:
            yield n                                     # yield makes this function an iterator factory
            n -= 1

print(list(Countdown2(4)), sum(Countdown2(4)))          # [4, 3, 2, 1] 10
```

### Walking a tree without exposing its structure

```python
class Tree:
    def __init__(self, value, left=None, right=None):
        self.value, self.left, self.right = value, left, right

    def __iter__(self):                                 # in-order traversal
        if self.left:
            yield from self.left
        yield self.value
        if self.right:
            yield from self.right

    def level_order(self):                              # a second way to traverse the same tree
        queue = [self]
        while queue:
            node = queue.pop(0)
            yield node.value
            queue.extend(n for n in (node.left, node.right) if n)

t = Tree(4, Tree(2, Tree(1), Tree(3)), Tree(6, Tree(5), Tree(7)))
print(list(t), sum(t), max(t))                          # [1, 2, 3, 4, 5, 6, 7] 28 7
print(list(t.level_order()))                            # [4, 2, 6, 1, 3, 5, 7]
```

### Lazy and infinite sequences

```python
from itertools import islice

def fibonacci():
    a, b = 0, 1
    while True:                                         # infinite, but only computed on demand
        yield a
        a, b = b, a + b

print(list(islice(fibonacci(), 10)))                    # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

def batched(iterable, n):
    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) == n:
            yield batch
            batch = []
    if batch:
        yield batch

print(list(batched(range(7), 3)))                       # [[0, 1, 2], [3, 4, 5], [6]]
```

### Iterable versus iterator (a classic gotcha)

```python
nums = [1, 2, 3]
it = iter(nums)                                         # an iterator over the list
print(list(it), list(it))                               # [1, 2, 3] []   (an iterator is single use)
print(list(nums), list(nums))                           # [1, 2, 3] [1, 2, 3]   (the list is reusable)
```

An **iterable** can produce iterators (has `__iter__`); an **iterator** produces values (has `__next__`) and is used up after one pass.

## 5. The Pythonic way

This pattern is **built into the language**: `for`, comprehensions, `list()`, `sum()`, `zip()`, unpacking, `in`, file objects (iterate lines), `dict.items()`, database cursors, `os.scandir`. Use **generators** (`yield`, `yield from`), **generator expressions** `(x*x for x in data)`, and the **`itertools`** module (`islice`, `chain`, `groupby`, `tee`, `cycle`, `product`) instead of writing iterator classes.

```python
from itertools import chain, islice
print(list(chain([1, 2], (3, 4), range(5, 7))))         # [1, 2, 3, 4, 5, 6]
squares = (n * n for n in range(10**9))                 # no memory used yet
print(list(islice(squares, 5)))                         # [0, 1, 4, 9, 16]
```

## 6. When to use it (and when not to)

**Use it when** you want a uniform way to traverse a custom data structure, process data lazily (large files, streams, infinite sequences), offer several traversals of one structure, or pipeline transformations.

**Skip it when** a plain list is fine and small.

## 7. Pros and cons

| Pros | Cons |
|------|------|
| Uniform `for` loop for any collection | Single-use iterators surprise beginners |
| Lazy: constant memory, can be infinite | No random access or length unless you add it |
| Several independent traversals at once | Modifying a collection while iterating causes bugs |

## 8. Related patterns

- [Composite](../structural/composite.md): iterators walk composite trees.
- [Visitor](visitor.md): performs operations on each node while traversing.
- [Memento](memento.md): iterators can store their position.

## 9. Two real-world examples

**Example 1: Reading a huge log file.** `for line in open("big.log")` yields one line at a time, so a 20 GB file needs almost no memory. The file object hides buffering, newlines and disk access.

**Example 2: Paginated API.** A generator `def all_users(): page = 1; while True: data = fetch(page); if not data: return; yield from data; page += 1` makes a paginated API look like one long list.

## 10. Common mistakes

- Reusing an exhausted iterator and getting nothing.
- Mutating a list while looping over it.
- Returning `self` from `__iter__` on a collection that should be reusable.
- Forgetting that generators are lazy: errors appear when consumed, not when created.

## 11. Practice

1. Write a generator `chunks(path, size)` that yields file contents in blocks.
2. Create an iterable `Range2(start, stop, step)` that supports multiple loops.
3. Show why `list(zip(a, a))` on a one-shot iterator behaves unexpectedly.

<details>
<summary>Solutions</summary>

**1.**
```python
import tempfile, os
def chunks(path, size):
    with open(path, "rb") as f:
        while block := f.read(size):
            yield block
p = os.path.join(tempfile.mkdtemp(), "f.bin"); open(p, "wb").write(b"abcdefghij")
print(list(chunks(p, 4)))                               # [b'abcd', b'efgh', b'ij']
```

**2.**
```python
class Range2:
    def __init__(self, start, stop, step=1): self.start, self.stop, self.step = start, stop, step
    def __iter__(self):
        n = self.start
        while n < self.stop:
            yield n
            n += self.step
r = Range2(0, 10, 3)
print(list(r), list(r))                                 # [0, 3, 6, 9] [0, 3, 6, 9]
```

**3.**
```python
it = iter([1, 2, 3, 4])
print(list(zip(it, it)))                                # [(1, 2), (3, 4)]  (both arguments advance the SAME iterator)
```

</details>

## 12. Check yourself

1. What are the two methods of the iterator protocol?
2. Iterable versus iterator?
3. Why use generators?
4. What happens when you loop over an iterator twice?

<details>
<summary>Answers</summary>

1. `__iter__` (returns the iterator) and `__next__` (returns the next value or raises `StopIteration`).
2. An iterable can produce iterators and is reusable; an iterator yields values once and is exhausted.
3. They create iterators with no boilerplate, are lazy, use constant memory and can be infinite.
4. The second loop gets nothing, because the iterator is already exhausted.

</details>

## More examples

Runnable script (added to your companion repository with this lesson): [`behavioralPattern/iteratorPattern.py`](https://github.com/M-Hammad-Faisal/design-patterns-python/blob/master/behavioralPattern/iteratorPattern.py)

[Family overview](README.md) · [All patterns](../README.md)
