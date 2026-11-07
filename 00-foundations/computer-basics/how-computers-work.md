# How a Computer Runs Your Program

**Prerequisites:** none. **You will learn:** the main parts of a computer, how the CPU runs instructions, why memory comes in layers, what an operating system does, and how a Python program actually executes.

## 1. In plain words

A computer is a machine that **follows instructions very fast**. It has a few simple parts that cooperate:

| Part | Job | Everyday analogy |
|------|-----|------------------|
| **CPU** (processor) | Runs instructions: arithmetic, comparisons, jumps | The **cook** following a recipe |
| **RAM** (memory) | Fast, temporary storage for the programs and data in use right now | The **kitchen counter**: small, fast, cleared when you leave |
| **Storage** (SSD/HDD) | Slow, permanent storage for files and programs | The **pantry/fridge**: large, slower to reach, keeps things |
| **Input/Output devices** | Keyboard, screen, network card, disk | Waiters and delivery drivers bringing things in and out |
| **Operating system** | Manages all of the above and shares them between programs | The **restaurant manager** |

Programs and data live in storage. To run, they are **loaded into RAM**. The CPU then **fetches instructions from RAM, one after another**, and does what they say.

## 2. The CPU: fetch, decode, execute

The CPU repeats one cycle billions of times per second:

```text
 1. FETCH    get the next instruction from memory (the address is in the "program counter")
 2. DECODE   work out what it means ("add these two numbers")
 3. EXECUTE  do it (using the ALU, the arithmetic/logic unit, and registers)
 4. STORE    write the result to a register or memory, then move to the next instruction
```

- **Registers** are tiny, extremely fast storage cells inside the CPU (a handful of numbers).
- The **clock speed** (for example 3 GHz = 3 billion cycles per second) sets the rhythm.
- A modern CPU has **several cores** (several cooks working at once) and many tricks (caches, pipelines, prediction) to stay busy.

### A toy CPU you can run

This tiny "computer" has three registers, a list of instructions, and the same fetch-decode-execute loop. It makes the idea concrete.

```python
def run(program, trace=False):
    """A toy CPU. Each instruction is a tuple such as ("LOAD", "A", 5)."""
    registers = {"A": 0, "B": 0, "C": 0}
    pc = 0                                       # program counter: index of the next instruction
    while pc < len(program):
        op, *args = program[pc]                  # FETCH the instruction and DECODE it into parts
        if trace:
            print(f"pc={pc} {program[pc]} registers={registers}")
        if op == "LOAD":                         # EXECUTE: put a constant into a register
            registers[args[0]] = args[1]
        elif op == "ADD":                        # ADD dest src: dest = dest + src
            registers[args[0]] += registers[args[1]]
        elif op == "SUB":
            registers[args[0]] -= registers[args[1]]
        elif op == "MUL":
            registers[args[0]] *= registers[args[1]]
        elif op == "JNZ":                        # jump if the register is not zero (how loops work)
            if registers[args[0]] != 0:
                pc = args[1]
                continue
        elif op == "HALT":
            break
        pc += 1                                  # move on to the next instruction
    return registers

# 2 + 3
print(run([("LOAD", "A", 2), ("LOAD", "B", 3), ("ADD", "A", "B"), ("HALT",)]))     # {'A': 5, 'B': 3, 'C': 0}

# A loop: total = 3 + 2 + 1, counting a register down from 3 to 0
loop = [
    ("LOAD", "A", 0),      # 0: total = 0
    ("LOAD", "B", 3),      # 1: counter = 3
    ("LOAD", "C", 1),      # 2: the constant 1
    ("ADD", "A", "B"),     # 3: total += counter        <- the loop body starts here
    ("SUB", "B", "C"),     # 4: counter -= 1
    ("JNZ", "B", 3),       # 5: if counter != 0, jump back to instruction 3
    ("HALT",),             # 6: stop
]
print(run(loop))           # {'A': 6, 'B': 0, 'C': 1}
```

This is exactly what `for`/`while` loops become at the lowest level: **compare and jump**. Real CPUs have a few hundred instruction types, but nothing more mysterious than this.

## 3. Memory comes in layers

Fast memory is expensive and small; large memory is cheap and slow. Computers combine several layers so that **most accesses hit the fast ones**.

| Layer | Typical size | Typical access time | Analogy |
|-------|--------------|---------------------|---------|
| Registers | a few dozen numbers | under 1 ns | Items in your hand |
| CPU cache (L1/L2/L3) | KBs to tens of MB | 1-10 ns | Your desk |
| RAM | 8-64 GB | ~100 ns | The shelf in the room |
| SSD | 256 GB - 4 TB | ~100 microseconds | The warehouse across town |
| HDD / network storage | TBs | milliseconds | A warehouse in another country |

Each step down is roughly **10-1000 times slower**. This is why:

- **Caching** is everywhere (CPU caches, browser caches, Redis).
- Code that reads data **in order** (sequential) is faster than code that jumps around: the CPU loads a whole "cache line" at a time.
- Databases and programs try hard to avoid going to disk or across a network.

```python
import time

n = 3_000_000
data = list(range(n))

start = time.perf_counter()
total = 0
for i in range(n):                       # sequential access: cache friendly
    total += data[i]
sequential = time.perf_counter() - start
print(total == n * (n - 1) // 2, sequential > 0)       # True True
```

## 4. What the operating system does

The **operating system (OS)**: Windows, macOS, Linux, Android, iOS: is the **first program that runs** and the one that manages everything else:

- **Runs programs** as *processes* and shares the CPU between them (scheduling).
- **Manages memory**, giving each program its own private space (virtual memory).
- **Manages files and storage** (file systems).
- **Talks to hardware** through drivers (disk, network, keyboard, screen).
- **Provides security**: users, permissions, isolation between programs.
- Offers programs a **system-call interface** (for example "open this file", "send these bytes").

Details: [processes and threads](../../06-operating-systems/processes-threads/README.md), [scheduling](../../06-operating-systems/scheduling/README.md), [memory](../../06-operating-systems/memory-virtual-memory/README.md), [file systems](../../06-operating-systems/file-systems-io/README.md).

## 5. From source code to running program

Computers only understand **machine code** (binary instructions for that CPU). Humans write **source code**. Something must translate:

| Approach | How | Examples |
|----------|-----|----------|
| **Compiled** | A compiler translates the whole program to machine code ahead of time; you run the result | C, C++, Rust, Go |
| **Interpreted** | An interpreter reads and executes the program step by step | Python (mostly), JavaScript, Ruby |
| **Hybrid (bytecode + VM)** | Source is compiled to an intermediate **bytecode**, which a virtual machine runs (often with a JIT compiler) | Java, C#, Python, JavaScript engines |

Python compiles your source to **bytecode** (instructions for the Python virtual machine) and runs it. You can look at it:

```python
import dis

def add(a, b):
    return a + b

dis.dis(add)
# (output varies by version, roughly:)
#   LOAD_FAST a
#   LOAD_FAST b
#   BINARY_OP +
#   RETURN_VALUE
instructions = [i.opname for i in dis.get_instructions(add)]
print("BINARY_OP" in instructions or "BINARY_ADD" in instructions)      # True
```

Python's bytecode instructions look just like our toy CPU's: load some values, add them, return. **The Python virtual machine is a program (written in C) that fetches and executes these instructions in a loop**, which is why Python is slower than compiled languages: every Python instruction costs many machine instructions.

## 6. Putting it together: what happens when you run `python hello.py`

1. You type the command; the **shell** asks the **OS** to start the `python` program.
2. The OS finds `python` on **storage**, loads it into **RAM**, and creates a **process** for it.
3. The **CPU** starts running the interpreter's machine code (fetch, decode, execute).
4. The interpreter **reads** `hello.py` (a file-system call), **compiles** it to bytecode, and **runs** the bytecode.
5. `print("hello")` asks the OS (a **system call**) to write bytes to the terminal; the OS talks to the display.
6. The program ends; the OS **frees its memory** and removes the process.

## 7. Two real-world examples

**Example 1: Why does opening a big file make an app feel slow?** Reading from SSD is about 1,000 times slower than RAM, and from a network drive even slower. The app waits, so good programs load data in the background, show a progress bar, and keep recently used data in memory (a cache).

**Example 2: Why does a program crash with "out of memory"?** RAM is finite. If a program keeps asking for memory (for instance building a list of a billion items), the OS eventually refuses, or starts using disk as extra memory (swapping), which is so much slower that everything freezes. Streaming the data in small pieces instead avoids it.

## 8. Common mistakes and misconceptions

- "More GHz always means faster": cores, caches and memory speed matter just as much.
- "RAM and storage are the same thing": RAM is temporary working space; storage is permanent.
- "The compiler/interpreter makes my code fast": algorithm choice usually matters far more.
- Treating the computer as magic: every program is just a very long list of simple instructions.

## 9. Practice

1. Extend the toy CPU with a `MUL` instruction and compute `4 * 5` by repeated addition using the loop pattern.
2. Using the memory-layer table, estimate how many times slower reading from SSD is than RAM.
3. Use `dis.dis` on a function with an `if` and a `for` loop; find the jump instructions.
4. Explain, in your own words, what the program counter is.

<details>
<summary>Solutions</summary>

**1.** Multiply `4 * 5` by repeated addition: keep the total in `A`, add a register holding 4 five times.
```python
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
```python
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

## 10. Check yourself

1. What are the fetch, decode and execute steps?
2. Why does a computer have several memory layers?
3. What is the difference between RAM and an SSD?
4. What does the OS do for programs?
5. What is bytecode and who runs it in Python?
6. How do loops exist at the machine level?

<details>
<summary>Answers</summary>

1. Fetch the next instruction from memory, decode what it means, execute it (and store the result).
2. Fast memory is small and expensive; large memory is slow and cheap; layers let most accesses hit the fast ones.
3. RAM is fast and temporary (cleared at power-off); an SSD is slower but permanent.
4. It runs programs as processes, shares CPU and memory between them, manages files and devices, and enforces security.
5. Bytecode is the intermediate instruction set Python compiles your source to; the Python virtual machine executes it.
6. As compare-and-jump instructions that change the program counter to go back and repeat.

</details>

[Back to foundations](../README.md) · Next: [binary and data representation](binary-and-data-representation.md)
