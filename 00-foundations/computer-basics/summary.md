# Computer Basics: One-Page Summary

## Questions worth remembering

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

Practice problems with solutions are in the exercises page and in the **Practice** section of each lesson.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [How a Computer Runs Your Program](how-computers-work.md) · [Binary, Hexadecimal and How Data Is Stored](binary-and-data-representation.md) · [Variables, Memory, the Stack and the Heap](memory-stack-heap.md) · [CPU Caches and the Memory Hierarchy](cpu-caches-and-memory-hierarchy.md)
