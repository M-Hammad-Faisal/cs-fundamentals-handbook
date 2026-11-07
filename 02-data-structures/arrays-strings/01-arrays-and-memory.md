# Arrays: How Data Sits in Memory

**Prerequisites:** [binary and memory](../../00-foundations/computer-basics/binary-and-data-representation.md), [stack and heap](../../00-foundations/computer-basics/memory-stack-heap.md), [Big-O](../../01-complexity/03-big-o-omega-theta.md). **You will learn:** what an array is at the memory level, why indexing is instant, the cost of inserting and deleting, how fixed arrays differ from dynamic arrays (Python's `list`), how 2D arrays are laid out, and how to build both kinds yourself.

## 1. In plain words

An **array** is a numbered row of boxes of the same size, stored **side by side in memory**. Because the boxes are neighbors, the computer can jump straight to box number `i` with simple arithmetic instead of searching for it.

Analogy: a **row of lockers** numbered 0, 1, 2, ... Every locker is the same width. To reach locker 57 you walk `57 x width` meters from the start: no need to open lockers 0 to 56 first. That instant jump is called **random access**.

```text
 index:     0     1     2     3     4
          ┌─────┬─────┬─────┬─────┬─────┐
 values:  │  10 │  20 │  30 │  40 │  50 │      all items sit next to each other
          └─────┴─────┴─────┴─────┴─────┘
 address: 1000  1008  1016  1024  1032         (8 bytes per item in this example)
```

## 2. Why indexing is O(1): the address formula

If the array starts at address `base` and each item occupies `size` bytes:

```text
address of item i  =  base  +  i * size
```

One multiplication and one addition, regardless of how big the array is. That is why `a[0]` and `a[1_000_000]` take the same time (`O(1)`).

```python
import array

a = array.array("q", [10, 20, 30, 40, 50])          # "q" = signed 8-byte integers in a compact C-style array
base_address, item_size = a.buffer_info()[0], a.itemsize
print(item_size)                                    # 8 bytes per item
for i in range(len(a)):
    address = base_address + i * item_size          # the formula
    print(f"a[{i}] = {a[i]:>2} lives at base + {i} * {item_size} = +{i * item_size} bytes")
# a[0] = 10 lives at base + 0 * 8 = +0 bytes ... a[4] = 50 lives at base + 4 * 8 = +32 bytes
print(a.buffer_info()[1], len(a) * item_size)       # 5 40   (5 items, 40 bytes in total)
```

Two consequences:

- **Indexing starts at 0** because the first item is at offset 0 (`base + 0 * size`).
- All items must be the **same size** for the formula to work; that is why C arrays hold one type.

## 3. Static (fixed-size) arrays

In languages like C and Java, an array is created with a **fixed length** that cannot change. Let us build one to see the rules:

```python
class StaticArray:
    """A fixed-capacity array with bounds checking, like a C/Java array (but safe)."""
    def __init__(self, capacity):
        self._capacity = capacity
        self._slots = [None] * capacity                 # allocate all slots up front

    def __len__(self):
        return self._capacity

    def __getitem__(self, index):
        self._check(index)
        return self._slots[index]                       # O(1)

    def __setitem__(self, index, value):
        self._check(index)
        self._slots[index] = value                      # O(1)

    def _check(self, index):
        if not 0 <= index < self._capacity:
            raise IndexError(f"index {index} out of range 0..{self._capacity - 1}")

    def __repr__(self):
        return f"StaticArray({self._slots})"

arr = StaticArray(4)
arr[0], arr[1] = "a", "b"
print(arr, arr[1], len(arr))                            # StaticArray(['a', 'b', None, None]) b 4
try:
    arr[4] = "x"                                        # beyond the end
except IndexError as error:
    print("IndexError:", error)                         # IndexError: index 4 out of range 0..3
```

In C the same mistake reads or writes **someone else's memory** (a buffer overflow: one of the most common security bugs in history). Python checks bounds for you.

Limits of fixed arrays: you must guess the size in advance (too small and you run out; too big and you waste memory).

## 4. Dynamic arrays: Python's `list`

A **dynamic array** keeps a fixed block internally but **grows automatically**: when it fills up, it allocates a bigger block (often about double), copies the items over and continues. This is Python's `list`, Java's `ArrayList`, C++'s `vector`.

```python
class DynamicArray:
    """A growable array that doubles its capacity when full. Counts element copies caused by growth."""
    def __init__(self):
        self._capacity = 1
        self._size = 0
        self._slots = [None] * self._capacity
        self.copies = 0

    def __len__(self):
        return self._size

    def __getitem__(self, index):
        if not 0 <= index < self._size:
            raise IndexError("index out of range")
        return self._slots[index]

    def append(self, value):                            # amortized O(1)
        if self._size == self._capacity:
            self._resize(self._capacity * 2)
        self._slots[self._size] = value
        self._size += 1

    def _resize(self, new_capacity):                    # O(n): allocate a bigger block and copy everything
        new_slots = [None] * new_capacity
        for i in range(self._size):
            new_slots[i] = self._slots[i]
            self.copies += 1
        self._slots, self._capacity = new_slots, new_capacity

    def insert(self, index, value):                     # O(n): shifts later items right
        if self._size == self._capacity:
            self._resize(self._capacity * 2)
        for i in range(self._size, index, -1):
            self._slots[i] = self._slots[i - 1]
        self._slots[index] = value
        self._size += 1

    def pop(self, index=None):                          # pop() is O(1); pop(i) is O(n) (shifts left)
        index = self._size - 1 if index is None else index
        value = self._slots[index]
        for i in range(index, self._size - 1):
            self._slots[i] = self._slots[i + 1]
        self._size -= 1
        self._slots[self._size] = None
        return value

    def __repr__(self):
        return f"DynamicArray({self._slots[:self._size]}, capacity={self._capacity})"

d = DynamicArray()
for letter in "abcde":
    d.append(letter)
print(d)                                                # DynamicArray(['a', 'b', 'c', 'd', 'e'], capacity=8)
d.insert(1, "X")                                        # shifts b..e one place right
print(d)                                                # DynamicArray(['a', 'X', 'b', 'c', 'd', 'e'], capacity=8)
print(d.pop(), d.pop(0))                                # e a      (remove the last item, then the first)
print(d)                                                # DynamicArray(['X', 'b', 'c', 'd'], capacity=8)
```

### Visualizing insert and delete (the shifting cost)

```text
Insert "X" at index 1 into [a, b, c, d, e]:

 before:  a  b  c  d  e  _
 shift:      b→ c→ d→ e→        (every item after the index moves right: n - index moves)
 after:   a  X  b  c  d  e

Delete index 1 from [a, X, b, c, d, e]:
 shift:      ←b ←c ←d ←e        (every later item moves left)
 after:   a  b  c  d  e  _
```

| Operation | Cost | Why |
|-----------|------|-----|
| read/write `a[i]` | `O(1)` | address formula |
| append at the end | `O(1)` amortized | spare capacity; occasional resize ([amortized analysis](../../01-complexity/06-cases-and-amortized-analysis.md)) |
| insert/delete at the **front or middle** | `O(n)` | shift the items after it |
| delete the last item | `O(1)` | nothing shifts |
| search an unsorted array | `O(n)` | look at each item |
| search a sorted array | `O(log n)` | binary search |

```python
d2 = DynamicArray()
for i in range(100_000):
    d2.append(i)
print(d2.copies, d2.copies / 100_000)                   # 131071 1.31071   -> about one extra copy per item overall: amortized O(1)
```

### How real Python lists grow

CPython's list over-allocates (about 12.5% extra plus a bit) so appends stay cheap. You can watch the capacity change through memory size:

```python
import sys

numbers, last, changes = [], 0, []
for i in range(60):
    numbers.append(i)
    size = sys.getsizeof(numbers)
    if size != last:
        changes.append((len(numbers), size))
        last = size
print(changes[:6])          # e.g. [(1, 88), (5, 120), (9, 184), (17, 248), (25, 312), (33, 376)]  (exact numbers vary by version)
print(len(changes) < 15)    # True: only a handful of resizes for 60 appends: growth happens rarely
```

## 5. Python lists store references

An important detail: a Python `list` stores **pointers (references) to objects**, not the objects themselves. That is why a list can hold mixed types, and why it uses more memory than a C array of numbers.

```text
 list a = [ ptr0 , ptr1 , ptr2 ]          the contiguous block holds 8-byte pointers
              │      │      │
              ▼      ▼      ▼
             10    "hi"   [1, 2]          the actual objects live elsewhere on the heap
```

```python
import sys, array

mixed = [10, "hi", [1, 2], 3.5, None]
print([type(x).__name__ for x in mixed])                # ['int', 'str', 'list', 'float', 'NoneType']

n = 100_000
as_list = list(range(n))
as_array = array.array("q", range(n))
list_bytes = sys.getsizeof(as_list) + sum(sys.getsizeof(x) for x in as_list)    # pointer block + every int object
array_bytes = sys.getsizeof(as_array)                                            # the packed numbers only
print(array_bytes < list_bytes / 3)                     # True: a packed array uses a fraction of the memory
```

For large numeric data use `array` or **NumPy** arrays (contiguous, typed, fast, vectorized); for general data use `list`.

## 6. Two-dimensional arrays: rows and columns

A 2D array is an array of arrays (Python: a list of lists). In memory the elements are still laid out in a **single line**, in **row-major order** (row 0, then row 1, ...). The address of element `[r][c]` in a grid with `cols` columns is:

```text
index in the flat layout = r * cols + c
```

```python
rows, cols = 3, 4
flat = list(range(rows * cols))                         # [0, 1, 2, ..., 11]: the "memory" of a 3 x 4 grid
grid = [flat[r * cols:(r + 1) * cols] for r in range(rows)]
for row in grid:
    print(row)
# [0, 1, 2, 3]
# [4, 5, 6, 7]
# [8, 9, 10, 11]
r, c = 2, 1
print(grid[r][c], flat[r * cols + c])                   # 9 9     (the same element, two ways to address it)

# Transpose: rows become columns
transposed = [[grid[r][c] for r in range(rows)] for c in range(cols)]
print(transposed)                                       # [[0, 4, 8], [1, 5, 9], [2, 6, 10], [3, 7, 11]]
```

The famous Python trap: building a grid with `[[0] * cols] * rows` makes every row the **same list object**:

```python
wrong = [[0] * 3] * 3
wrong[0][0] = 99
print(wrong)                                            # [[99, 0, 0], [99, 0, 0], [99, 0, 0]]   all rows changed!
right = [[0] * 3 for _ in range(3)]                     # a NEW list for every row
right[0][0] = 99
print(right)                                            # [[99, 0, 0], [0, 0, 0], [0, 0, 0]]
```

Iterating a grid row by row follows the memory layout (cache friendly in compiled languages); going column by column jumps around ([cache effects](../../01-complexity/08-beyond-big-o.md)).

## 7. Arrays in the standard library and beyond

| Tool | What it is | Use for |
|------|------------|---------|
| `list` | dynamic array of references | general-purpose sequences |
| `tuple` | immutable array of references | fixed records, dictionary keys |
| `array.array` | packed typed array | compact numeric data |
| `bytes` / `bytearray` | immutable / mutable array of bytes | binary data, network packets |
| `collections.deque` | double-ended queue (not a plain array) | fast operations at both ends |
| `numpy.ndarray` | N-dimensional typed array | numeric computing, images, machine learning |
| `memoryview` | zero-copy view of a buffer | slicing big data without copying |

## 8. When to use an array (and when not to)

**Good for:** random access by position, iterating in order, appending at the end, storing a known/growing sequence, binary search on sorted data, as the foundation of other structures (heaps, hash tables, stacks).

**Bad for:** frequent insertion or deletion at the front or middle (`O(n)` shifting; consider [linked lists](../linked-lists/README.md) or `deque`), membership tests by value (use a [set](../hash-tables/README.md)), when you need ordered lookups by key (use a dictionary or tree).

## 9. Two real-world examples

**Example 1: Pixels of an image.** A grayscale photo of 1920 x 1080 is a 2D array of 2,073,600 byte values. Filters (blur, brightness) loop over the array in order; reading a pixel by coordinates uses `row * width + column`. Image libraries store the data as one contiguous block precisely so the formula and cache-friendly loops make them fast.

```python
width, height = 5, 3
pixels = bytearray(width * height)                      # a flat, contiguous buffer: 15 bytes
def set_pixel(x, y, value): pixels[y * width + x] = value
def get_pixel(x, y): return pixels[y * width + x]
set_pixel(2, 1, 255)
print(get_pixel(2, 1), list(pixels))                    # 255 [0, 0, 0, 0, 0, 0, 0, 255, 0, 0, 0, 0, 0, 0, 0]
```

**Example 2: A playlist or a list of search results.** The app keeps the songs in a dynamic array: showing "song number 7" is instant, adding to the end is instant, and playing in order is a plain loop. Inserting a song at position 0 of a 100,000-song playlist would shift all the others (`O(n)`), so very large editable playlists use other structures (or batch the moves).

## 10. Common mistakes

- Off-by-one errors: valid indexes are `0` to `len - 1`; `a[len(a)]` raises `IndexError`.
- `[[0] * c] * r` for grids (shared rows).
- Inserting or deleting at the front inside a loop (hidden `O(n²)`).
- Modifying a list while iterating over it.
- Forgetting negative indexes count from the end (`a[-1]` is the last item).
- Using a list when you need fast membership or a fixed-size packed numeric buffer.
- Assuming slicing is free: `a[i:j]` copies `j - i` items.

## 11. Practice

1. Using the address formula, if an array of 4-byte integers starts at address 2000, where is item 25? How many bytes does an array of 1,000 items occupy?
2. Add `remove(value)` (first match) to `DynamicArray` and state its cost.
3. Count how many item moves `insert(0, x)` causes in an array of 10,000 items. What about `insert` at the end?
4. Build a `Matrix` class backed by one flat list with `get(r, c)` and `set(r, c, value)` using the row-major formula.
5. Why does `array.array("q", ...)` use far less memory than a list of the same numbers?
6. Write `shift_left(items, k)` that rotates a list left by `k` in `O(n)` time.

<details>
<summary>Solutions</summary>

**1.** Address = `2000 + 25 * 4 = 2100`; 1,000 items x 4 bytes = 4,000 bytes.

**2.**
```python
def remove(self, value):                                # O(n): search then shift
    for i in range(self._size):
        if self._slots[i] == value:
            self.pop(i)
            return
    raise ValueError(f"{value!r} not in array")
DynamicArray.remove = remove
d = DynamicArray()
for ch in "abcb": d.append(ch)
d.remove("b"); print(d)                                 # DynamicArray(['a', 'c', 'b'], capacity=4)
```

**3.** 10,000 moves at the front; 0 moves at the end (just a write).

**4.**
```python
class Matrix:
    def __init__(self, rows, cols, fill=0):
        self.rows, self.cols = rows, cols
        self._data = [fill] * (rows * cols)
    def get(self, r, c): return self._data[r * self.cols + c]
    def set(self, r, c, value): self._data[r * self.cols + c] = value
m = Matrix(3, 4)
m.set(2, 1, 9)
print(m.get(2, 1), m._data.index(9))                    # 9 9
```

**5.** A list stores 8-byte pointers plus a separate Python `int` object (28+ bytes) for each number; the typed array stores only the raw numbers (8 bytes each).

**6.**
```python
def rotate_left(items, k):
    k %= len(items) or 1
    return items[k:] + items[:k]
print(rotate_left([1, 2, 3, 4, 5], 2))                  # [3, 4, 5, 1, 2]
```

</details>

## 12. Check yourself

1. Why is array indexing `O(1)`?
2. Why is inserting at the front `O(n)`?
3. What is the difference between a static and a dynamic array?
4. What does a Python `list` actually store?
5. How is element `[r][c]` located in a row-major 2D array?
6. Why is `[[0] * 3] * 3` a bug?

<details>
<summary>Answers</summary>

1. Items are contiguous and equally sized, so `address = base + i * size` is one multiplication and addition.
2. Every existing item must shift one position to make room.
3. A static array has a fixed capacity; a dynamic array grows automatically by allocating a larger block and copying (amortized `O(1)` append).
4. A contiguous block of references (pointers) to objects stored elsewhere.
5. At flat index `r * cols + c`.
6. All three rows are the same list object, so changing one changes all.

</details>

[Back to arrays and strings](README.md) · Next: [array techniques](02-array-techniques.md)
