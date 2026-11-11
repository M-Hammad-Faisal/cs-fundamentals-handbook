# Memory Management and Virtual Memory: Exercises

These problems go with the [Memory Management and Virtual Memory lesson](README.md). Try each one before opening its solution.

<details>
<summary>Setup code the solutions use (copied from the lessons)</summary>

```python
from collections import OrderedDict, deque

def fifo(refs, frames):
    memory, queue, faults = set(), deque(), 0
    for page in refs:
        if page in memory:
            continue
        faults += 1
        if len(memory) == frames:
            memory.remove(queue.popleft())                 # evict the page that has been here longest
        memory.add(page); queue.append(page)
    return faults

def lru(refs, frames):
    memory, faults = OrderedDict(), 0                      # order = recency, least recent first
    for page in refs:
        if page in memory:
            memory.move_to_end(page)                       # refresh: now most recently used
            continue
        faults += 1
        if len(memory) == frames:
            memory.popitem(last=False)                     # evict the least recently used
        memory[page] = True
    return faults

def optimal(refs, frames):
    memory, faults = set(), 0
    for i, page in enumerate(refs):
        if page in memory:
            continue
        faults += 1
        if len(memory) == frames:
            def next_use(p):                               # when is p needed next? never = infinity
                try:
                    return refs.index(p, i + 1)
                except ValueError:
                    return float("inf")
            memory.remove(max(memory, key=next_use))       # evict the page needed farthest in the future
        memory.add(page)
    return faults
```

</details>

## Problems

1. With 4 KiB pages, split virtual address `20000` into page number and offset. If page 4 maps to frame 12, what is the physical address?
2. A system has 32-bit virtual addresses and 4 KiB pages. How many pages are in the address space? How large is a single-level page table with 4-byte entries? Why do multi-level tables help?
3. Run FIFO, LRU and Optimal with 3 frames on `[7,0,1,2,0,3,0,4,2,3,0,3,2]`. Which wins and why?
4. Demonstrate Belady's anomaly by finding the frame counts where FIFO faults increase on `[1,2,3,4,1,2,5,1,2,3,4,5]`.
5. Explain what happens, step by step, when a process touches a page that was swapped out.
6. A process has RSS 200 MB and VIRT 4 GB. Is that a problem? What would you look at?
7. Using `mmap`, write a script that counts occurrences of `b"\n"` in a file without reading it all into a Python bytes object.
8. Why can two processes that load the same shared library use far less physical memory than the sum of their VIRT sizes?

<details>
<summary>Solutions</summary>

**1.** `20000 // 4096 = 4`, offset `20000 - 16384 = 3616`. Physical address `12 * 4096 + 3616 = 52768`.

**2.** `2**32 / 2**12 = 2**20 = 1,048,576` pages. A flat table is `2**20 * 4 B = 4 MiB` per process. Multi-level tables only allocate the sub-tables for regions actually in use, which is tiny for typical sparse address spaces (and essential for 64-bit).

**3.**
```python
refs = [7,0,1,2,0,3,0,4,2,3,0,3,2]
print(fifo(refs, 3), lru(refs, 3), optimal(refs, 3))   # 10 9 7
```
Optimal wins (7) because it knows the future; LRU (9) beats FIFO (10) because recently used pages are likely used again (temporal locality).

**4.**
```python
refs = [1,2,3,4,1,2,5,1,2,3,4,5]
print([(f, fifo(refs, f)) for f in range(1, 7)])
# [(1,12),(2,12),(3,9),(4,10),(5,5),(6,5)]  : 3 -> 4 frames goes from 9 to 10
```

**5.** The access finds the present bit clear, so the CPU traps to the kernel. The kernel verifies the address is valid, finds a free frame (evicting a page if needed, writing it out if dirty), schedules a disk read of the page from swap, blocks the process (others run), then updates the page table and TLB when the I/O completes, and restarts the faulting instruction.

**6.** Usually not: VIRT includes mapped libraries, thread stacks and reserved arenas that are never touched. RSS 200 MB is the real footprint. Check RSS trend over time, `smem`/`pmap` for what dominates, and cgroup memory limits (what the OOM killer uses).

**7.**
```python
import mmap, os, tempfile
path = os.path.join(tempfile.mkdtemp(), "lines.txt")           # a small demo file
with open(path, "wb") as f:
    f.write(b"one\ntwo\nthree\n")
with open(path, "rb") as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as m:
    count, pos = 0, m.find(b"\n")
    while pos != -1:
        count += 1
        pos = m.find(b"\n", pos + 1)
print(count)
# 3
```

**8.** The library's code pages are file-backed and read-only, so the kernel maps the same physical frames into both address spaces. VIRT counts them twice; physical RAM holds them once.

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Virtual Memory](01-paging-and-address-translation.md) · [Page Replacement Algorithms](02-page-replacement-algorithms.md) · [Segmentation](03-segmentation.md)
