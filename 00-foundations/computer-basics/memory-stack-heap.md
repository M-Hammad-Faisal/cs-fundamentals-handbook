# Variables, Memory, the Stack and the Heap

**Prerequisites:** [how computers work](how-computers-work.md). **You will learn:** what a variable really is, how Python stores objects, what the **call stack** and **heap** are, why recursion can crash with "maximum recursion depth", and how memory is freed.

## 1. In plain words

When your program runs it needs places to keep values. The computer's memory is like a **very long row of numbered mailboxes**; each mailbox has an **address** and holds one byte. Programs ask the operating system for blocks of these mailboxes.

Two regions matter to every programmer:

| Region | What lives there | How it behaves | Analogy |
|--------|------------------|----------------|---------|
| **The stack** (call stack) | Information about **function calls in progress**: parameters, local variables, where to return to | Automatic, very fast, strictly last-in first-out; small (limited size) | A **stack of plates**: you add to the top, take from the top |
| **The heap** | Objects that need to **live longer** or have a size not known in advance (lists, strings, dictionaries, your own objects) | Allocated on request, freed when no longer used; larger, slightly slower | A big **warehouse** where items are stored and found by a ticket (a reference) |

In Python, **all objects live on the heap**; the stack holds **references** (tickets) to them and the bookkeeping for each running function.

## 2. Variables are names, not boxes

In many languages a variable is a box that holds a value. In Python a variable is a **name that points to an object**. Assigning never copies the object.

```text
a = [1, 2, 3]        a ──────►  [1, 2, 3]          (one list object on the heap)
b = a                b ──────┘                      (b is a second name for the SAME list)
b.append(4)          a and b both see [1, 2, 3, 4]
```

```python
a = [1, 2, 3]
b = a                              # b points to the same object; nothing is copied
b.append(4)
print(a, b, a is b)                # [1, 2, 3, 4] [1, 2, 3, 4] True
print(id(a) == id(b))              # True   (id() is the object's identity: roughly its memory address)

c = a.copy()                       # a NEW list with the same contents
c.append(5)
print(a, c, a is c)                # [1, 2, 3, 4] [1, 2, 3, 4, 5] False

x = 10
y = x
y += 1                             # integers are immutable: this makes y point to a NEW object (11)
print(x, y)                        # 10 11
```

### Mutable versus immutable objects

| Immutable (cannot be changed after creation) | Mutable (can be changed in place) |
|----------------------------------------------|-----------------------------------|
| `int`, `float`, `bool`, `str`, `tuple`, `frozenset`, `bytes`, `None` | `list`, `dict`, `set`, `bytearray`, most user-defined objects |

Why it matters: with mutable objects, **two names can change the same thing** (surprising bugs); with immutable objects, "changing" creates a new object.

```python
def add_item(items):
    items.append("new")            # mutates the caller's list!

my_list = ["a"]
add_item(my_list)
print(my_list)                     # ['a', 'new']

def add_one(n):
    n += 1                         # rebinds the local name n; the caller's int is untouched
    return n

value = 5
add_one(value)
print(value)                       # 5

# Python passes "object references": the function receives a reference to the same object.
# Mutating it affects the caller; rebinding the parameter name does not.
```

## 3. The call stack

Every time you **call a function**, Python pushes a **stack frame** holding that call's parameters, local variables and the place to return to. When the function returns, the frame is popped.

```python
def c():
    return "done"

def b():
    return c()

def a():
    return b()

print(a())                         # done
```

```text
Call stack while c() is running (top of stack at the top):

   | c()  |   <- currently running
   | b()  |
   | a()  |
   | main |
   +------+

When c returns, its frame is removed; then b's, then a's.
```

Python can show you the stack: a **traceback** is the list of frames at the moment an error occurred.

```python
import traceback

def divide(a, b):
    return a / b

def calculate():
    return divide(1, 0)

try:
    calculate()
except ZeroDivisionError:
    text = traceback.format_exc()
    print(text.count("File"), "frames in the traceback")          # 3 frames in the traceback
    print(text.strip().splitlines()[-1])                          # ZeroDivisionError: division by zero
```

Read tracebacks **from the bottom up**: the last line is the error; the lines above show how the program got there.

### Recursion and stack overflow

**Recursion** is a function calling itself. Each call adds a frame, and the stack has limited size, so recursion that never stops (or goes too deep) crashes.

```python
import sys

def countdown(n):
    if n == 0:                     # base case: the recursion MUST have a way to stop
        return "liftoff"
    return countdown(n - 1)        # each call adds a stack frame

print(countdown(100))              # liftoff
print(sys.getrecursionlimit())     # 1000   (Python's safety limit on stack depth; the exact number can vary)

def forever(n):
    return forever(n + 1)          # no base case

try:
    forever(0)
except RecursionError as error:
    print("RecursionError:", str(error)[:40])                     # RecursionError: maximum recursion depth exceeded
```

In C or Java the same bug produces a **stack overflow** crash. Fixes: add the base case, convert the recursion to a loop, or increase the limit carefully (`sys.setrecursionlimit`). See [recursion](../../03-algorithms/recursion-backtracking/README.md).

## 4. The heap and object lifetime

Objects are created on the heap when you write literals or call constructors, and they live **as long as something refers to them**.

```python
import sys

data = [1, 2, 3]                   # one reference: the name `data`
print(sys.getrefcount(data) - 1)   # 1     (getrefcount adds one temporary reference itself)
alias = data
print(sys.getrefcount(data) - 1)   # 2
del alias                          # remove one name
print(sys.getrefcount(data) - 1)   # 1
data = None                        # now nothing refers to the list: Python frees it immediately
```

### Garbage collection

Python uses **reference counting**: every object counts how many references point to it and is freed the instant the count reaches zero. This misses **cycles** (A refers to B and B refers to A, so neither count reaches zero), so Python also runs a **cyclic garbage collector** periodically.

```python
import gc, weakref

class Node:
    pass

a, b = Node(), Node()
a.other, b.other = b, a            # a reference cycle
probe = weakref.ref(a)             # a "weak" reference does not keep the object alive
del a, b
print(probe() is not None)         # True   (the cycle keeps both alive)
gc.collect()                       # the cycle collector finds them
print(probe() is None)             # True   (now they are freed)
```

Languages differ: **C/C++** make you free memory manually (leaks and crashes if you get it wrong); **Java, Go, Python, JavaScript** use garbage collection; **Rust** uses ownership rules checked at compile time.

## 5. How big are things?

```python
import sys

print(sys.getsizeof(0), sys.getsizeof(2 ** 100))             # 28 40       (ints grow with their value)
print(sys.getsizeof(""), sys.getsizeof("hello"))             # 41 46       (overhead plus one byte per ASCII char; numbers vary by version)
print(sys.getsizeof([]), sys.getsizeof([1, 2, 3]))           # 56 88       (a list stores pointers to its items)
print(sys.getsizeof({}), sys.getsizeof({"a": 1}))            # 64 184      (sizes vary a little by Python version)

big = [0] * 1_000_000              # a million references: about 8 MB for the list itself
print(sys.getsizeof(big) > 7_000_000)                        # True
```

Python objects carry **overhead** (type pointer, reference count). A Python `int` takes 28 bytes where C needs 4; that is the price of flexibility, and why NumPy stores numbers in compact arrays for heavy math.

## 6. Local, global and nonlocal variables (scope)

Where a name is **visible** is its **scope**. Python looks names up in this order, **LEGB**: **L**ocal (inside the current function), **E**nclosing (outer functions), **G**lobal (module level), **B**uilt-in (`len`, `print`).

```python
x = "global"

def outer():
    x = "enclosing"
    def inner():
        x = "local"
        return x
    return inner(), x

print(outer(), x)                  # ('local', 'enclosing') global

counter = 0

def increment():
    global counter                 # say you mean the module-level variable, not a new local one
    counter += 1

increment(); increment()
print(counter)                     # 2

def make_counter():
    count = 0
    def step():
        nonlocal count             # rebind the enclosing function's variable
        count += 1
        return count
    return step

step = make_counter()
print(step(), step())              # 1 2
```

Use **local** variables and **parameters** by default; global variables make programs hard to test and reason about.

## 7. Two real-world examples

**Example 1: A shared-list bug in a web app.** A developer writes `def add_tag(tag, tags=[])` so that each new post starts with an empty list. All posts share one list (the default argument is created once on the heap and reused), so tags from one post leak into others. Understanding that names are references to heap objects explains and fixes it (`tags=None`, create the list inside the function).

**Example 2: "RecursionError" processing a deeply nested JSON or a long linked list.** A recursive function that walks a 50,000-element structure exceeds the stack depth. The fix is to walk it with an explicit stack (a list) on the heap, which can grow far larger than the call stack. Many production tools (parsers, file-tree walkers) are written iteratively for exactly this reason.

## 8. Common mistakes

- Thinking `b = a` copies a list (it creates a second name).
- Using a mutable default argument (`def f(x=[])`).
- Recursion without a base case, or too deep for the stack.
- Using `is` to compare values (use `==`; `is` is for identity checks like `x is None`).
- Overusing globals.
- Forgetting that a shallow copy shares inner objects (use `copy.deepcopy` when needed).

## 9. Practice

1. Predict and then run: `a = [1, 2]; b = a; b += [3]; c = a + [4]; print(a, b, c)`.
2. Write a function that reverses a list **in place** and another that returns a **new** reversed list. Show the difference with `is`.
3. Write a recursive `factorial(n)`, then an iterative one; find the largest `n` the recursive version handles before `RecursionError`.
4. Draw the call stack for `a()` calling `b()` calling `c()` when `c` raises an error.
5. Show that two equal strings or tuples are not necessarily the same object (`is`), and explain when to use `is`.

<details>
<summary>Solutions</summary>

**1.**
```python
a = [1, 2]; b = a; b += [3]; c = a + [4]
print(a, b, c)               # [1, 2, 3] [1, 2, 3] [1, 2, 3, 4]   (+= mutates in place; + builds a new list)
```

**2.**
```python
def reverse_in_place(items):
    items.reverse()
    return items

def reversed_copy(items):
    return items[::-1]

nums = [1, 2, 3]
print(reverse_in_place(nums) is nums, reversed_copy(nums) is nums)       # True False
```

**3.**
```python
def factorial_rec(n):
    return 1 if n <= 1 else n * factorial_rec(n - 1)

def factorial_iter(n):
    result = 1
    for k in range(2, n + 1):
        result *= k
    return result

assert factorial_rec(10) == factorial_iter(10) == 3628800
try:
    factorial_rec(5000)
except RecursionError:
    print("recursion too deep; the iterative version still works:", len(str(factorial_iter(1000))), "digits in 1000!")
```

**4.** At the moment of the error: `main` at the bottom, then `a`, `b`, `c` on top; the traceback prints them from `main` down to `c`, and the exception travels back down the stack until a `try/except` catches it.

**5.**
```python
s1 = "".join(["py", "thon"]); s2 = "python"
print(s1 == s2, s1 is s2)                       # True False   (equal values, different objects)
x = None
print(x is None)                                # True   (use `is` for None, True, False and identity checks)
```

</details>

## 10. Check yourself

1. What is the difference between the stack and the heap?
2. What does `b = a` do when `a` is a list?
3. Which of these are mutable: `tuple`, `list`, `str`, `dict`?
4. What is a stack frame and when is it created?
5. Why does infinite recursion end in an error?
6. How does Python free unused memory?
7. What does LEGB stand for?

<details>
<summary>Answers</summary>

1. The stack holds function-call frames (parameters, locals, return addresses) automatically and in LIFO order; the heap holds objects that live as long as they are referenced and are allocated on request.
2. It makes `b` another name for the same list object; no copy is made.
3. `list` and `dict` are mutable; `tuple` and `str` are immutable.
4. A stack frame holds the data for one function call; it is pushed when the function is called and popped when it returns.
5. Each call adds a frame; the stack has finite size, so Python raises `RecursionError` (other languages crash with a stack overflow).
6. By reference counting (free when the count hits zero) plus a cyclic garbage collector for reference cycles.
7. Local, Enclosing, Global, Built-in: the order Python searches for a name.

</details>

[Back to foundations](../README.md) · Previous: [binary and data representation](binary-and-data-representation.md)
