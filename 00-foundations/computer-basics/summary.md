# Computer Basics: One-Page Summary

## Key facts

- **The CPU loop:** fetch the next instruction, decode it, execute it, repeat; the program counter says which instruction is next, and loops are compare-and-jump instructions.
- **Memory hierarchy (orders of magnitude):** registers under 1 ns, L1/L2/L3 cache about 1 to 40 ns, RAM about 100 ns, SSD about 100 µs, spinning disk about 10 ms, network round trips milliseconds. Each level is bigger and roughly 10 to 1000 times slower.
- **Locality:** cache lines are 64 bytes, so reading neighbours is cheap (spatial locality) and re-reading recent data is cheap (temporal locality); row-by-row beats column-by-column on large arrays.
- **Binary:** `n` bits hold `2ⁿ` values; a hex digit is 4 bits; signed `n`-bit two's complement covers `-2ⁿ⁻¹` to `2ⁿ⁻¹-1`; Python integers never overflow.
- **Bit tricks:** `x & (x - 1)` clears the lowest set bit, `x & -x` isolates it, `1 << k` builds a mask, `x >> 1` halves (rounding down).
- **Floats:** IEEE-754 doubles keep about 15 to 16 decimal digits and cannot store `0.1` exactly; compare with `math.isclose`, use `Decimal` for money.
- **Text:** a Unicode code point is a number (`ord`, `chr`); UTF-8 stores it in 1 to 4 bytes and is compatible with ASCII; `str` is text, `bytes` is data.
- **Stack and heap:** the call stack holds frames with locals and is freed on return; objects live on the heap while something refers to them. Python names are references, so assignment never copies.
- **Source to running:** Python compiles source to bytecode, and the Python virtual machine executes it.

## Pitfalls

- Comparing floats with `==`, or storing money in floats.
- Assuming one character is one byte: the encoded length depends on the characters and the encoding.
- `b = a` for a list gives two names for one list; copy with `a.copy()` or `a[:]`.
- Unbounded recursion raises `RecursionError` (the default limit is about 1000 frames).
- Mixing up RAM (fast, lost at power-off) with storage (slower, permanent).

## Self-check

- **What are the fetch, decode and execute steps?** Fetch the next instruction from memory, decode what it means, execute it (and store the result).
- **Why does a computer have several memory layers?** Fast memory is small and expensive; large memory is slow and cheap; layers let most accesses hit the fast ones.
- **What is the difference between RAM and an SSD?** RAM is fast and temporary (cleared at power-off); an SSD is slower but permanent.
- **What does the OS do for programs?** It runs programs as processes, shares CPU and memory between them, manages files and devices, and enforces security.
- **What is bytecode and who runs it in Python?** Bytecode is the intermediate instruction set Python compiles your source to; the Python virtual machine executes it.
- **How do loops exist at the machine level?** As compare-and-jump instructions that change the program counter to go back and repeat.
- **How many different values can n bits represent?** 2^n.
- **Why is hex popular with programmers?** One hex digit is exactly 4 bits, so binary data is much shorter and easier to read.
- **How is -1 stored in 8-bit two's complement?** `11111111` (all ones): flip `00000001` to `11111110` and add 1.
- **Why is `0.1 + 0.2 != 0.3`, and how should you compare floats?** The decimal fractions are stored as slightly inexact binary fractions; compare with `math.isclose` (a tolerance) or use `Decimal`.
- **What is the difference between a Unicode code point and a UTF-8 byte?** A code point is a character's number in the Unicode table; UTF-8 is a way to store that number as 1-4 bytes.
- **What does `x & (x - 1)` do?** It clears the lowest set bit (so a result of 0 means x was zero or a power of two).

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [How a Computer Runs Your Program](how-computers-work.md) · [Binary, Hexadecimal and How Data Is Stored](binary-and-data-representation.md) · [Variables, Memory, the Stack and the Heap](memory-stack-heap.md) · [CPU Caches and the Memory Hierarchy](cpu-caches-and-memory-hierarchy.md)
