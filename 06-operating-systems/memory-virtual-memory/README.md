# Memory Management and Virtual Memory

## Detailed lessons

- [Paging and address translation](01-paging-and-address-translation.md): pages, frames, page tables, TLB, page faults, with a runnable MMU
- [Page replacement algorithms](02-page-replacement-algorithms.md): FIFO, LRU, Optimal, Clock, Belady's anomaly, working sets, thrashing
- [Segmentation](03-segmentation.md): base and limit, external fragmentation, segmentation plus paging, x86 descriptors

The rest of this page is the quick reference.

## 1. The concept

Every process believes it owns a large, private, contiguous block of memory. That illusion is **virtual memory**. The OS and the CPU's **MMU** (memory management unit) translate each **virtual address** into a **physical address** in RAM, on every access.

Why it exists:
- **Isolation:** one process cannot touch another's memory.
- **Simplicity:** programs use the same address layout regardless of what else runs.
- **Overcommit:** a process can use more memory than is physically free; unused pages live on disk.
- **Sharing:** the same physical page (a shared library, a forked parent's data) can appear in many address spaces.

## 2. How it works

### Paging

Memory is divided into fixed-size **pages** (commonly 4 KiB) in virtual space and **frames** of the same size in RAM. A **page table** maps page number to frame number. A virtual address splits into `page number | offset`; the offset is unchanged.

```text
virtual address 4100 with 4096-byte pages:
  page = 4100 // 4096 = 1,  offset = 4100 % 4096 = 4
  page table says page 1 -> frame 9
  physical address = 9 * 4096 + 4 = 36868
```

Page-table entries also hold flags: **present**, **read/write/execute**, **user/kernel**, **dirty** (modified), **accessed** (recently used).

A 64-bit machine uses **multi-level page tables** (4 or 5 levels on x86-64), so only the parts of the address space that are in use need table memory.

### The TLB

Walking tables on every access would be slow, so the CPU caches recent translations in the **TLB** (translation lookaside buffer). A TLB hit costs about a cycle; a miss costs a table walk. Context switches between processes flush or tag the TLB, which is part of why they are expensive. **Huge pages** (2 MiB) reduce TLB misses for big heaps (databases).

### Page faults and demand paging

If the present bit is clear, the CPU raises a **page fault** and the OS handles it:

1. **Minor fault:** page is in memory but not mapped (first touch of fresh memory, shared page): just fix the mapping.
2. **Major fault:** page must be read from disk (swap or a file-backed page): millisecond-scale delay.
3. **Invalid access:** the address is not valid: the process gets `SIGSEGV` (segmentation fault).

Pages are loaded **on demand**; `fork` uses **copy-on-write**; memory-mapped files load lazily.

### Page replacement

When RAM is full the OS evicts a page. Policies, measured by **page faults** on a reference string:

```python
from collections import OrderedDict, deque

def fifo(refs, frames):
    mem, q, faults = set(), deque(), 0
    for p in refs:
        if p not in mem:
            faults += 1
            if len(mem) == frames:
                mem.remove(q.popleft())
            mem.add(p); q.append(p)
    return faults

def lru(refs, frames):
    mem, faults = OrderedDict(), 0
    for p in refs:
        if p in mem:
            mem.move_to_end(p)
        else:
            faults += 1
            if len(mem) == frames:
                mem.popitem(last=False)
            mem[p] = True
    return faults

def optimal(refs, frames):
    mem, faults = [], 0
    for i, p in enumerate(refs):
        if p in mem:
            continue
        faults += 1
        if len(mem) == frames:
            future = refs[i + 1:]
            victim = max(mem, key=lambda x: future.index(x) if x in future else float("inf"))
            mem.remove(victim)
        mem.append(p)
    return faults

def translate(vaddr, page_table, page_size=4096):
    page, offset = divmod(vaddr, page_size)
    if page not in page_table:
        raise LookupError(f"page fault on page {page}")
    return page_table[page] * page_size + offset
```

On the classic reference string `1 2 3 4 1 2 5 1 2 3 4 5`:

| Frames | FIFO | LRU | Optimal |
|--------|------|-----|---------|
| 3 | 9 | 10 | 7 |
| 4 | **10** | 8 | 6 |

Notice FIFO gets *worse* with more frames: **Belady's anomaly** (it does not happen for LRU or Optimal, which are stack algorithms). **Optimal** (evict the page used furthest in the future) is unrealizable but a benchmark. Real systems approximate LRU with the **clock** algorithm using the accessed bit.

### Thrashing

If the combined **working sets** of running processes exceed RAM, the system spends its time swapping pages and little useful work gets done. Fixes: add RAM, run fewer processes, reduce memory use.

### Process memory layout

```text
high addresses   stack   (grows down: locals, return addresses)
                 ...
                 mmap region (shared libs, mapped files)
                 ...
                 heap    (grows up: malloc / Python objects)
                 data    (globals)
low addresses    text    (code, read-only)
```

### Allocation and fragmentation

- **Internal fragmentation:** wasted space inside an allocated block (a 4 KiB page holding 100 bytes).
- **External fragmentation:** free space is split into pieces too small to use. Paging removes it for physical memory.
- Allocators (`malloc`, jemalloc, Python's `pymalloc` arenas) keep size-class free lists to stay fast.

### Memory-mapped files in Python

```python
import mmap, os, tempfile

path = os.path.join(tempfile.mkdtemp(), "data.bin")
with open(path, "wb") as f:
    f.write(b"hello virtual memory")

with open(path, "r+b") as f, mmap.mmap(f.fileno(), 0) as m:
    print(m[:5])              # b'hello' : read through memory, no read() call
    m[0:5] = b"HELLO"         # write through memory; the OS flushes it to the file
    m.flush()

print(open(path, "rb").read())   # b'HELLO virtual memory'
```

The kernel pages file contents in lazily and shares them between processes that map the same file.

## 3. Two real-world examples

### Example 1: Why a forked Redis snapshot does not double memory
Redis saves a snapshot by calling `fork`. Parent and child share all pages copy-on-write; the child writes the dataset to disk while the parent keeps serving writes, and only pages that change get copied. Memory use grows with the *write rate during the snapshot*, not with dataset size. That is why heavy writes during a snapshot can spike memory and trigger the OOM killer if there is no headroom.

### Example 2: A Python process "using" more memory than it needs
`top` shows a large **virtual size (VIRT)** because of mapped libraries and reserved regions, but only **resident (RES/RSS)** counts pages actually in RAM. A server whose RSS keeps growing is leaking or fragmenting; use `tracemalloc` or a profiler to find where. Containers are killed by the cgroup OOM killer based on RSS (plus page cache accounting), not VIRT.

## 4. Tips, tricks and pitfalls

- Think in **RSS** (real use) not VIRT; know the difference.
- Memory leaks in managed languages are usually **references kept alive** (caches, globals, listeners).
- Swapping on a latency-sensitive service is usually worse than a crash-and-restart; many deployments disable swap.
- Sequential access is cache- and prefetch-friendly; random access across a huge heap causes TLB and cache misses.
- Use `mmap` for large read-mostly files; use generators and streaming instead of loading everything.
- A segmentation fault means an invalid memory reference (null pointer, use after free, stack overflow); in pure Python you see it only through C extensions or ctypes misuse.

## 5. Check yourself

1. What does the MMU do and why have virtual memory?
2. Translate address 9000 with 4 KiB pages if page 2 maps to frame 7.
3. What is a TLB and why does it matter?
4. Differences between minor and major page faults?
5. What is Belady's anomaly?
6. What is thrashing and how do you stop it?
7. Why is copy-on-write useful for `fork`?
8. VIRT versus RSS?

<details>
<summary>Answers</summary>

1. It translates virtual to physical addresses on each access. Virtual memory gives isolation, a simple uniform layout, overcommit with disk backing, and sharing.
2. `9000 // 4096 = 2`, offset `9000 - 8192 = 808`. Frame 7 gives `7 * 4096 + 808 = 29480`.
3. A cache of recent page translations; without it every memory access would need several extra page-table reads.
4. Minor: no disk I/O, just map a page already in memory or allocate a zero page. Major: read the page from disk, which is thousands of times slower.
5. With FIFO replacement, adding more frames can increase the number of faults (the reference string above: 9 faults with 3 frames, 10 with 4).
6. The system spends most time paging because working sets exceed RAM. Reduce concurrency, shrink memory use, or add RAM.
7. The child shares the parent's pages until one writes, so `fork` is fast and memory-cheap.
8. VIRT is the total address space reserved or mapped; RSS is the part actually resident in RAM.

</details>

[Exercises](exercises.md) · [Summary](summary.md)

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

Back to the [part overview](../README.md).
