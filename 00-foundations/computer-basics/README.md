# Computer Basics

Four short lessons that explain what is happening *underneath* your code. Everything later in the handbook (operating systems, memory, performance, even Python behavior) builds on these ideas.

| # | Lesson | You will learn |
|---|--------|----------------|
| 1 | [How a computer runs your program](how-computers-work.md) | CPU, RAM, storage, the fetch-decode-execute cycle (with a toy CPU you run), memory layers, the OS, bytecode |
| 2 | [Binary, hex and data representation](binary-and-data-representation.md) | Bits and bytes, number bases, two's complement, floating point (and why `0.1 + 0.2` is odd), Unicode and UTF-8, bitwise operators |
| 3 | [Memory, the stack and the heap](memory-stack-heap.md) | Variables as references, mutable vs immutable, the call stack, recursion limits, garbage collection, scope |
| 4 | [CPU caches and the memory hierarchy](cpu-caches-and-memory-hierarchy.md) | Latency numbers, locality, cache lines, a cache simulator you run, row-major versus column-major, why arrays beat linked lists, real timings in Python |

[Back to foundations](../README.md)

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

## Quick reference

| Question | Answer |
|----------|--------|
| What are the fetch, decode and execute steps? | Fetch the next instruction from memory, decode what it means, execute it (and store the result). |
| Why does a computer have several memory layers? | Fast memory is small and expensive; large memory is slow and cheap; layers let most accesses hit the fast ones. |
| What is the difference between RAM and an SSD? | RAM is fast and temporary (cleared at power-off); an SSD is slower but permanent. |
| What does the OS do for programs? | It runs programs as processes, shares CPU and memory between them, manages files and devices, and enforces security. |
| What is bytecode and who runs it in Python? | Bytecode is the intermediate instruction set Python compiles your source to; the Python virtual machine executes it. |

Back to the [part overview](../README.md).
