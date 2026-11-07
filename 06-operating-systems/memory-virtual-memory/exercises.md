# Memory Management and Virtual Memory: Exercises

Use the functions from the lesson.

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
import mmap, sys
with open(sys.argv[1], "rb") as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as m:
    count, pos = 0, m.find(b"\n")
    while pos != -1:
        count += 1
        pos = m.find(b"\n", pos + 1)
print(count)
```

**8.** The library's code pages are file-backed and read-only, so the kernel maps the same physical frames into both address spaces. VIRT counts them twice; physical RAM holds them once.

</details>

[Lesson](README.md) · [Summary](summary.md)
