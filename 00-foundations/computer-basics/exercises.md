# Computer Basics: Exercises

Try each problem before opening its solution. These are the practice problems of this topic's lessons, collected in one place.

## How a Computer Runs Your Program

1. Extend the toy CPU with a `MUL` instruction and compute `4 * 5` by repeated addition using the loop pattern.
2. Using the memory-layer table, estimate how many times slower reading from SSD is than RAM.
3. Use `dis.dis` on a function with an `if` and a `for` loop; find the jump instructions.
4. Explain, in your own words, what the program counter is.

<details>
<summary>Solutions</summary>

**1.** Multiply `4 * 5` by repeated addition: keep the total in `A`, add a register holding 4 five times.
```python no-run
# registers: A = total, B = counter (5), C = the constant 1, X = the amount to add (4)
repeated_addition = [
    ("LOAD", "A", 0),      # total = 0
    ("LOAD", "B", 5),      # counter = 5
    ("LOAD", "C", 1),      # constant 1
    ("LOAD", "X", 4),      # the amount to add (register X is created on the first LOAD)
    ("ADD", "A", "X"),     # 4: total += 4
    ("SUB", "B", "C"),     # 5: counter -= 1
    ("JNZ", "B", 4),       # 6: repeat while counter != 0
    ("HALT",),
]
print(run(repeated_addition)["A"])                     # 20
print(run([("LOAD", "A", 4), ("LOAD", "B", 5), ("MUL", "A", "B"), ("HALT",)])["A"])    # 20 using the new MUL instruction
```
(`MUL` is already in the toy CPU above; the loop shows how multiplication can be built from addition when a CPU lacks it.)

**2.** About 100 microseconds / 100 ns = 1,000 times slower.

**3.**
```python no-run
import dis
def f(items):
    total = 0
    for x in items:
        if x > 0:
            total += x
    return total
ops = [i.opname for i in dis.get_instructions(f)]
print([o for o in ops if "JUMP" in o or "FOR_ITER" in o or "POP_JUMP" in o][:5])
```

**4.** The program counter is a register holding the address (index) of the next instruction to fetch. After each instruction it normally advances by one; jump instructions overwrite it, which is how loops and `if` statements change the flow.

</details>

## Binary, Hexadecimal and How Data Is Stored

1. Convert 200 to binary and hex by hand, then check with Python.
2. Write `count_ones(n)` (number of 1 bits) without `bin`.
3. What is `0b1010 ^ 0b0110`? What is `5 << 3`?
4. Represent -20 in 8-bit two's complement.
5. Why does `"naïve".encode("utf-8")` have 6 bytes? How many characters?
6. Write a function that returns the permission string (like `rw-`) for a 3-bit number.
7. Compute exactly 0.1 + 0.2 with `Decimal` and with integer cents.

<details>
<summary>Solutions</summary>

**1.** 200 = 128 + 64 + 8 = `11001000` = `0xC8`.
```python no-run
print(f"{200:b}", f"{200:X}", bin(200), hex(200))        # 11001000 C8 0b11001000 0xc8
```

**2.**
```python no-run
def count_ones(n):
    count = 0
    while n:
        count += n & 1                 # look at the last bit
        n >>= 1                        # drop it
    return count
print(count_ones(0b101101), count_ones(255), count_ones(0))     # 4 8 0
```

**3.** `1010 ^ 0110 = 1100` = 12; `5 << 3 = 5 * 8 = 40`.
```python no-run
print(0b1010 ^ 0b0110, 5 << 3)                  # 12 40
```

**4.** 20 = `00010100`; flip = `11101011`; add 1 = `11101100`.
```python no-run
print(to_twos_complement(-20))                  # 11101100
```

**5.** `ï` takes 2 bytes in UTF-8 and the other 4 letters take 1 byte each: 5 characters, 6 bytes.
```python no-run
print(len("naïve"), len("naïve".encode("utf-8")))           # 5 6
```

**6.**
```python no-run
def perm_string(bits):
    return ("r" if bits & 4 else "-") + ("w" if bits & 2 else "-") + ("x" if bits & 1 else "-")
print(perm_string(7), perm_string(5), perm_string(4), perm_string(0))     # rwx r-x r-- ---
```

**7.**
```python no-run
from decimal import Decimal
print(Decimal("0.1") + Decimal("0.2"))           # 0.3
print((10 + 20) / 100)                           # 0.3  (10 and 20 are cents: store money as integers)
```

</details>

## Variables, Memory, the Stack and the Heap

1. Predict and then run: `a = [1, 2]; b = a; b += [3]; c = a + [4]; print(a, b, c)`.
2. Write a function that reverses a list **in place** and another that returns a **new** reversed list. Show the difference with `is`.
3. Write a recursive `factorial(n)`, then an iterative one; find the largest `n` the recursive version handles before `RecursionError`.
4. Draw the call stack for `a()` calling `b()` calling `c()` when `c` raises an error.
5. Show that two equal strings or tuples are not necessarily the same object (`is`), and explain when to use `is`.

<details>
<summary>Solutions</summary>

**1.**
```python no-run
a = [1, 2]; b = a; b += [3]; c = a + [4]
print(a, b, c)               # [1, 2, 3] [1, 2, 3] [1, 2, 3, 4]   (+= mutates in place; + builds a new list)
```

**2.**
```python no-run
def reverse_in_place(items):
    items.reverse()
    return items

def reversed_copy(items):
    return items[::-1]

nums = [1, 2, 3]
print(reverse_in_place(nums) is nums, reversed_copy(nums) is nums)       # True False
```

**3.**
```python no-run
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
```python no-run
s1 = "".join(["py", "thon"]); s2 = "python"
print(s1 == s2, s1 is s2)                       # True False   (equal values, different objects)
x = None
print(x is None)                                # True   (use `is` for None, True, False and identity checks)
```

</details>

## CPU Caches and the Memory Hierarchy

1. Change the cache in the simulator to 64 KB with 4 ways. Re-run the 16 KB and 64 KB double-read experiment. What changes and why?
2. Predict, then measure with the simulator, the hit rate for the column-major traversal if the matrix were only 32 by 32 (8 KB total). Why is it so much better than for 256 by 256?
3. Write a generator for **row-major order but reading two arrays** `A` and `B` alternately (addresses in different regions). Does the hit rate change? What if both regions map to the same cache sets (try offsets that are multiples of the cache size)?
4. A function sums every 16th element of a huge array of 8-byte numbers. What hit rate do you expect with a 64-byte line, and what is the lesson for data layout?
5. Why does a binary search on a huge sorted array suffer more cache misses than a B-tree lookup of the same data?
6. Explain in one paragraph why a Python list of 1 million floats is slower to sum than a NumPy array of 1 million floats, mentioning at least two causes besides the interpreter loop.

<details>
<summary>Solutions</summary>

1. ```python no-run
   for kb in (16, 64):
       c = Cache(size=64 * 1024, ways=4)
       for repetition in range(2):
           for a in range(0, kb * 1024, 8):
               c.access(a)
       print(f"{kb} KB block twice: {c.hit_rate:.1%}")
   # 16 KB block twice: 93.8%
   # 64 KB block twice: 93.8%
   ```
   With a 64 KB cache both blocks now fit, so the second pass hits entirely for both (the cache size, not the algorithm, decided the result).
2. ```python no-run
   def column_major_small(n):
       for j in range(n):
           for i in range(n):
               yield (i * n + j) * 8
   c = Cache()
   for a in column_major_small(32):
       c.access(a)
   print(f"{c.hit_rate:.1%}")
   # 87.5%
   ```
   The whole 32 by 32 matrix (8 KB, 128 lines) fits in the 32 KB cache, so after the first column pulls each row's line in, the following columns hit: the working set is smaller than the cache.
3. Alternating two sequential streams still gives 87.5 percent, as long as the two regions map to different sets or there are enough ways. If both regions have the same set mapping and you read many arrays at once, they can evict each other (**conflict misses**); associativity (more ways per set) reduces this. Try offsets that are multiples of `size // ways` to see the hit rate drop when more arrays than ways collide.
4. Every 16th 8-byte number is 128 bytes apart, so every access hits a new line: hit rate 0 percent, and 7/8 of every fetched line is wasted. The lesson: if you only need one field, store it **contiguously** (column layout), so each cache line holds eight useful values.
5. Binary search makes about `log2(n)` probes at widely scattered addresses, and each of the early probes lands on a different cache line and page. A B-tree packs many keys per node (one line or one disk block), so each step examines many keys at the cost of one memory access, and it has far fewer levels.
6. A Python list holds 1 million **pointers** to separate float objects scattered across the heap (24 or more bytes each, plus the 8-byte pointer), so summing it chases pointers (poor spatial locality), touches a lot more memory and increments reference counts; a NumPy array stores 1 million raw 8-byte doubles back to back, so the scan reads 8 MB sequentially (prefetcher-friendly) in compiled code, possibly with SIMD instructions.

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [How a Computer Runs Your Program](how-computers-work.md) · [Binary, Hexadecimal and How Data Is Stored](binary-and-data-representation.md) · [Variables, Memory, the Stack and the Heap](memory-stack-heap.md) · [CPU Caches and the Memory Hierarchy](cpu-caches-and-memory-hierarchy.md)
