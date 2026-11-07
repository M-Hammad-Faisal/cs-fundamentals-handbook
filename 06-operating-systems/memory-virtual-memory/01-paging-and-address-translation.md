# Virtual Memory: Paging and Address Translation

**Prerequisites:** [what is an OS](../00-what-is-an-operating-system.md), [binary and hexadecimal](../../00-foundations/computer-basics/binary-and-data-representation.md), [stack and heap](../../00-foundations/computer-basics/memory-stack-heap.md). **You will learn:** why every process sees its own private memory, how **virtual addresses** become **physical addresses** through **pages, frames and page tables**, what the **TLB** does, how **multi-level page tables** save space, what a **page fault** is, and how to build a tiny working MMU in Python.

## 1. The problem

Many programs run at once, each believing it owns memory starting at address 0. If they used real addresses directly:

- Program A could overwrite program B (no protection).
- Each program would have to know where free memory happens to be (no portability).
- Memory would fragment into unusable holes; programs bigger than RAM could not run at all.

**Virtual memory** solves all of these with one idea: programs use **virtual addresses**, and hardware (the **MMU**, memory management unit) translates every access into a **physical address**, using tables the OS controls.

## 2. Pages and frames

Cut memory into equal fixed-size chunks (typically **4 KB**):

- Virtual memory is divided into **pages**.
- Physical memory (RAM) is divided into **frames** (same size).
- A **page table** maps each page to a frame.

A virtual address splits into two parts: the **page number** (which page) and the **offset** (where inside the page). The offset passes through unchanged.

```text
virtual address (16 bits, page size 4096 = 2^12):
 | page number (4 bits) | offset (12 bits) |
   0x3                    0x2A8
 page table says page 3 -> frame 7
physical address = frame 7, offset 0x2A8  =  7 * 4096 + 0x2A8 = 0x72A8
```

```python
PAGE_SIZE = 4096
OFFSET_BITS = 12                                      # 2**12 = 4096

def split(virtual_address):
    return virtual_address >> OFFSET_BITS, virtual_address & (PAGE_SIZE - 1)      # (page number, offset)

print(split(0x32A8), split(0x12345))                  # (3, 680) (18, 837)

page_table = {0: 5, 1: 2, 3: 7}                       # page -> frame (pages 2, 4... are not mapped)

def translate(virtual_address):
    page, offset = split(virtual_address)
    if page not in page_table:
        raise MemoryError(f"page fault: page {page} is not in memory (address {hex(virtual_address)})")
    return page_table[page] * PAGE_SIZE + offset

print(hex(translate(0x32A8)))                         # 0x72a8
print(hex(translate(0x0010)), hex(translate(0x1FFF))) # 0x5010 0x2fff
try:
    translate(0x2000)                                 # page 2 is unmapped
except MemoryError as e:
    print(e)                                          # page fault: page 2 is not in memory (address 0x2000)
```

Why this solves the problems:

- **Isolation:** each process has its own page table, so it can only reach frames the OS mapped for it.
- **No contiguity needed:** pages 0, 1, 3 can live in frames 5, 2, 7, scattered anywhere.
- **No external fragmentation:** any free frame will do (only the last page of an allocation wastes some space: **internal fragmentation**).
- **Sharing:** two processes can map the same frame (shared libraries, `fork` copy-on-write).
- **Permissions:** each table entry carries bits: *present*, *read/write*, *user/kernel*, *executable*, *dirty*, *accessed*.

## 3. Page table entries and protection

```python
from dataclasses import dataclass

@dataclass
class PageTableEntry:
    frame: int
    present: bool = True
    writable: bool = True
    user: bool = True
    dirty: bool = False                               # set by hardware on a write
    accessed: bool = False                            # set by hardware on any access (used by replacement)

class MMU:
    def __init__(self):
        self.table = {}
        self.log = []

    def map(self, page, frame, writable=True):
        self.table[page] = PageTableEntry(frame, writable=writable)

    def access(self, virtual_address, write=False):
        page, offset = split(virtual_address)
        entry = self.table.get(page)
        if entry is None or not entry.present:
            self.log.append("PAGE FAULT")
            raise MemoryError("page fault")
        if write and not entry.writable:
            self.log.append("PROTECTION FAULT")
            raise PermissionError("write to a read-only page")
        entry.accessed = True
        entry.dirty = entry.dirty or write
        return entry.frame * PAGE_SIZE + offset

mmu = MMU()
mmu.map(0, 5)                                         # code page: read-only in real systems
mmu.map(1, 9, writable=False)
print(hex(mmu.access(0x0004, write=True)))            # 0x5004
print(hex(mmu.access(0x1008)))                        # 0x9008
for addr, w in ((0x1008, True), (0x7000, False)):
    try:
        mmu.access(addr, write=w)
    except (MemoryError, PermissionError) as e:
        print(type(e).__name__, "-", e)
# PermissionError - write to a read-only page
# MemoryError - page fault
print(mmu.log, mmu.table[0].dirty, mmu.table[1].dirty)        # ['PROTECTION FAULT', 'PAGE FAULT'] True False
```

This is exactly how a `Segmentation fault` happens: the access hits an unmapped page or violates its permissions, the MMU traps to the kernel, and the kernel (unable to fix it) sends the process the `SIGSEGV` signal.

## 4. The problem with big page tables

A 32-bit address space with 4 KB pages has `2^32 / 2^12 = 2^20` = **1 048 576 pages**. At 4 bytes per entry, a **single flat page table is 4 MB per process**, even though a typical process uses a tiny fraction of its address space. For 64-bit addresses a flat table is impossible.

**Solution: multi-level page tables.** Split the page number into several indexes and create inner tables **only where memory is actually used**.

```text
32-bit address:  | 10 bits: outer index | 10 bits: inner index | 12 bits: offset |
outer table (1024 entries) -> points to an inner table (1024 entries) -> gives the frame
```

```python
OUTER_BITS, INNER_BITS = 10, 10

def split2(address):
    offset = address & 0xFFF
    inner = (address >> 12) & 0x3FF
    outer = (address >> 22) & 0x3FF
    return outer, inner, offset

class TwoLevelTable:
    def __init__(self):
        self.outer = {}                               # outer index -> inner dict (created only when needed)
        self.inner_tables = 0

    def map(self, address, frame):
        outer, inner, _ = split2(address)
        if outer not in self.outer:
            self.outer[outer] = {}
            self.inner_tables += 1
        self.outer[outer][inner] = frame

    def translate(self, address):
        outer, inner, offset = split2(address)
        try:
            return self.outer[outer][inner] * PAGE_SIZE + offset
        except KeyError:
            raise MemoryError("page fault")

t = TwoLevelTable()
for addr in range(0x00400000, 0x00400000 + 16 * PAGE_SIZE, PAGE_SIZE):     # a 64 KB code region
    t.map(addr, (addr >> 12) & 0xFF)
for addr in range(0x7FFF0000, 0x7FFF0000 + 4 * PAGE_SIZE, PAGE_SIZE):       # a 16 KB stack region
    t.map(addr, 100 + (addr >> 12) % 16)
print(split2(0x00400123), t.inner_tables)                   # (1, 0, 291) 2
entries_used = 2 * 1024 + 1024                              # two inner tables plus the outer table
print(entries_used * 4, "bytes instead of", (1 << 20) * 4)  # 12288 bytes instead of 4194304
```

A process using two small regions needs just **12 KB** of tables instead of 4 MB. Modern 64-bit CPUs use **4 levels** (x86-64: 9 bits per level), some use 5.

## 5. The TLB: making translation fast

Each memory access would otherwise need extra memory accesses to walk the page table (4 extra reads with 4 levels!). The CPU caches recent translations in a small, very fast cache, the **TLB (translation lookaside buffer)**.

- **TLB hit:** translation takes about 1 cycle.
- **TLB miss:** walk the page table (tens to hundreds of cycles), then cache the result.

Programs have **locality** (they reuse nearby addresses), so hit rates are typically above 99%.

```python
from collections import OrderedDict

class TLB:
    def __init__(self, size=4):
        self.size, self.entries = size, OrderedDict()      # page -> frame; order = recency (LRU)
        self.hits = self.misses = 0

    def lookup(self, page, page_table):
        if page in self.entries:
            self.hits += 1
            self.entries.move_to_end(page)
            return self.entries[page]
        self.misses += 1
        frame = page_table[page]                           # the slow page-table walk
        self.entries[page] = frame
        if len(self.entries) > self.size:
            self.entries.popitem(last=False)               # evict the least recently used translation
        return frame

page_table = {p: p + 100 for p in range(64)}

def run(addresses, tlb_size):
    tlb = TLB(tlb_size)
    for a in addresses:
        tlb.lookup(a >> 12, page_table)
    return tlb.hits, tlb.misses

sequential = [i * 8 for i in range(4000)]                  # walk an array of 8-byte items (very local)
scattered = [(i * 7919 * 4096) % (64 * 4096) for i in range(4000)]      # jump between pages
print(run(sequential, 4), run(scattered, 4))              # (3992, 8) (0, 4000)
```

Walking an array touches the same page 512 times in a row (4096 / 8), so almost every access hits; hopping across 64 pages with a 4-entry TLB almost never hits.

**Effective access time (EAT)** shows why the TLB matters. With memory time `m = 100 ns`, TLB lookup `t = 1 ns`, hit rate `h`:

```python
def effective_access_time(hit_rate, memory_ns=100, tlb_ns=1):
    hit = tlb_ns + memory_ns                               # TLB lookup + the real access
    miss = tlb_ns + memory_ns + memory_ns                  # + one extra memory access for a one-level page table walk
    return hit_rate * hit + (1 - hit_rate) * miss

print([round(effective_access_time(h), 1) for h in (0.0, 0.5, 0.9, 0.99)])      # [201.0, 151.0, 111.0, 102.0]
```

At a 99% hit rate paging costs only about 2% extra. (With a 4-level table the penalty per miss is much bigger, so TLB hit rate matters even more.)

## 6. Page faults and demand paging

Pages need not all be in RAM. A page table entry can say **not present**. When the program touches such a page, the MMU raises a **page fault** and the kernel decides:

1. **Valid but not loaded yet** (first touch of a file-backed or zero page, or swapped out): find a free frame (evicting another page if needed: the page replacement policy), read the data from disk, update the table, **restart the instruction**.
2. **Invalid** (null pointer, address outside any mapping): send `SIGSEGV`, the process dies.
3. **Copy-on-write**: a write to a shared read-only page; copy the frame, then allow the write.

This is **demand paging**: load pages only when touched. It makes `fork` cheap, speeds up program start (only needed code is read), and lets programs use more memory than exists.

A disk read takes about 10 ms (hard disk) or 100 microseconds (SSD) versus 100 ns for RAM: a page fault is **100 000 to 100 000 000 times slower**. Even a tiny fault rate hurts badly:

```python
def eat_with_faults(fault_rate, memory_ns=100, fault_ns=8_000_000):      # 8 ms to service a fault from disk
    return (1 - fault_rate) * memory_ns + fault_rate * fault_ns

for p in (0, 1e-6, 1e-5, 1e-4):
    print(f"fault rate {p:g}: {eat_with_faults(p):.0f} ns per access")
# fault rate 0: 100 ns per access
# fault rate 1e-06: 108 ns per access
# fault rate 1e-05: 180 ns per access
# fault rate 0.0001: 900 ns per access
```

One fault per 10 000 accesses makes memory **9 times slower**. When the system spends most of its time handling faults instead of working (too many processes for the RAM), it is **thrashing**: the cure is fewer processes or more RAM.

## 7. Seeing virtual memory from Python

```python
import mmap, os, resource, sys

# 1. A big allocation is virtual until you touch it: demand paging in action.
before = resource.getrusage(resource.RUSAGE_SELF).ru_minflt          # minor page faults so far
buf = bytearray(50 * 1024 * 1024)                                    # asks for 50 MB of zeroed memory
mid = resource.getrusage(resource.RUSAGE_SELF).ru_minflt
for i in range(0, len(buf), 4096):
    buf[i] = 1                                                       # touch each page once
after = resource.getrusage(resource.RUSAGE_SELF).ru_minflt
print(after > before)                                                # True   (first-touch page faults happened; exact counts vary by OS and allocator)

# 2. Memory-mapped file: the file's pages appear in your address space, loaded on demand.
path = "/tmp/vm_demo.bin"
with open(path, "wb") as f:
    f.write(b"hello virtual memory" + b"\0" * 8192)
with open(path, "r+b") as f, mmap.mmap(f.fileno(), 0) as m:
    print(m[:5], m.size() >= 8192)                                   # b'hello' True
    m[0:5] = b"HELLO"                                                # write through memory; the OS writes pages back
with open(path, "rb") as f:
    print(f.read(5))                                                 # b'HELLO'
os.remove(path)
print(os.sysconf("SC_PAGE_SIZE"))                                    # 4096 (16384 on Apple Silicon Macs)
```

(The last number depends on your CPU: x86 uses 4096, Apple Silicon 16384.)

## 8. Two real-world examples

**Example 1: `fork` is cheap because of copy-on-write.** When Python's `os.fork()` or a web server clones a process, the kernel copies only the page table, marks all pages read-only and shared, and copies a page only when someone writes to it. A 4 GB process forks in milliseconds.

**Example 2: Why "free memory" on Linux looks low.** The kernel uses spare RAM as a **page cache** for files; those frames are reclaimed instantly when programs need them. Judge memory pressure by swapping activity and available memory, not by "free".

## 9. Common mistakes

- Confusing virtual with physical addresses (Python's `id()` is neither a physical address nor stable across runs).
- Forgetting that the offset is copied unchanged and only the page number is translated.
- Assuming a `malloc`/allocation immediately uses RAM (it reserves virtual space; frames are assigned on first touch).
- Treating a high "virtual size" as a leak (resident set size, RSS, is what occupies RAM).
- Ignoring that page faults to disk are millions of times slower than hits.
- Using too small a page size without considering larger page tables, or huge pages without considering internal fragmentation.

## 10. Practice

1. With 4 KB pages, split virtual address `0x5ABC` into page number and offset.
2. If page 5 maps to frame 12, what is the physical address of `0x5ABC`?
3. How many pages does a 48-bit virtual address space have with 4 KB pages?
4. A process uses 1 MB of memory. With 4 KB pages, how many pages? How much internal fragmentation can occur at most?
5. Compute the effective access time with a 95% TLB hit rate, `memory = 80 ns`, `tlb = 2 ns` (single-level table).
6. Why are multi-level page tables smaller than flat ones for sparse address spaces?
7. What happens, step by step, on a write to a read-only page?

<details>
<summary>Solutions</summary>

1. `0x5ABC >> 12 = 5`, offset `0xABC` (2748).
   ```python
   print(split(0x5ABC))                                  # (5, 2748)
   ```
2. `12 * 4096 + 0xABC = 0xCABC`.
   ```python
   page_table = {5: 12}; print(hex(translate(0x5ABC)))   # 0xcabc
   ```
3. `2^48 / 2^12 = 2^36` pages (about 68.7 billion).
4. 1 MB / 4 KB = 256 pages; internal fragmentation is at most one page minus 1 byte (4095 bytes), only in the last page.
5. `0.95 * (2 + 80) + 0.05 * (2 + 80 + 80) = 77.9 + 8.1 = 86.0 ns`.
   ```python
   print(round(effective_access_time(0.95, memory_ns=80, tlb_ns=2), 1))      # 86.0
   ```
6. Inner tables are created only for the regions that are actually used; the unused parts of the address space need no entries.
7. The MMU finds the entry's write-permission bit cleared, raises a protection fault and traps to the kernel. If the page is copy-on-write the kernel copies the frame, remaps it writable and restarts the instruction; otherwise it signals `SIGSEGV`.

</details>

## 11. Check yourself

1. What is the difference between a page and a frame?
2. What are the two parts of a virtual address?
3. What does the TLB cache and why does it matter?
4. What is a page fault, and is it always an error?
5. Why do multi-level page tables exist?
6. What is thrashing?

<details>
<summary>Answers</summary>

1. A page is a fixed-size chunk of virtual memory; a frame is a same-sized chunk of physical memory.
2. The page number (looked up in the page table) and the offset (unchanged).
3. Recent page-to-frame translations; without it each memory access would need extra table lookups in memory.
4. A trap when a needed page is not present or not permitted; not always an error (demand paging and copy-on-write handle valid faults).
5. To avoid storing a huge mostly empty flat table: inner tables exist only for used regions.
6. The system spends most of its time swapping pages in and out instead of running programs because there is too little RAM for the active working sets.

</details>

[Back to memory management](README.md) · Next: page replacement algorithms (coming next)
