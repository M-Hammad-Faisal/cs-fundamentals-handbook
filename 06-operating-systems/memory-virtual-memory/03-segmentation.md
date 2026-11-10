# Segmentation: Memory in Meaningful Pieces

**Prerequisites:** [paging and address translation](01-paging-and-address-translation.md), [page replacement](02-page-replacement-algorithms.md), [stack and heap](../../00-foundations/computer-basics/memory-stack-heap.md), [binary and hexadecimal](../../00-foundations/computer-basics/binary-and-data-representation.md). **You will learn:** what **segmentation** is (dividing a program's memory by *meaning*: code, data, heap, stack), how a **segment table** translates a **(segment, offset)** address with **base and limit** checks, why it causes **external fragmentation** (and how first-fit, best-fit and compaction behave), how it compares with **paging**, how the two are combined, and how a real **x86 segment descriptor** is laid out (parsed from bytes in Python). Everything runs; no special hardware needed.

## 1. In plain words

Paging cuts memory into **equal-sized, meaningless** blocks. **Segmentation** instead cuts a program into **logical pieces of different sizes** that match how a programmer thinks about it:

- the **code** (instructions, read-only),
- the **global data**,
- the **heap** (grows as you allocate),
- the **stack** (grows with function calls),
- plus maybe shared libraries.

Each piece is a **segment**: a contiguous region with a **base** (where it starts in physical memory), a **limit** (how long it is) and **permissions**. An address is now a pair: **(segment number, offset within the segment)**.

```text
Logical view of one process                 Physical memory
 segment 0 code   [ ........ ]  --->        base 0x3000, limit 0x1000
 segment 1 data   [ ... ]        --->        base 0x9000, limit 0x0400
 segment 2 heap   [ ...... ]     --->        base 0x6000, limit 0x2000
 segment 3 stack  [ ... ]        --->        base 0xF000, limit 0x0800
```

## 2. Address translation with base and limit

The hardware (MMU) keeps a **segment table**. To translate `(s, offset)`:

1. Look up entry `s`: get `base`, `limit` and permissions.
2. If `offset >= limit`: **trap** (a *segmentation fault*: the access is outside the segment).
3. If the access type is not allowed (write to code): trap.
4. Otherwise the physical address is `base + offset`.

```python
from dataclasses import dataclass

@dataclass
class Segment:
    name: str
    base: int
    limit: int
    readable: bool = True
    writable: bool = False
    executable: bool = False

class SegmentationFault(Exception):
    pass

class SegmentedMMU:
    def __init__(self, segments):
        self.table = segments                                  # index in the list = segment number

    def translate(self, segment, offset, access="read"):
        if segment >= len(self.table):
            raise SegmentationFault(f"no segment {segment}")
        seg = self.table[segment]
        if offset < 0 or offset >= seg.limit:
            raise SegmentationFault(f"offset {offset:#x} beyond limit {seg.limit:#x} of segment '{seg.name}'")
        allowed = {"read": seg.readable, "write": seg.writable, "execute": seg.executable}[access]
        if not allowed:
            raise SegmentationFault(f"{access} not permitted on segment '{seg.name}'")
        return seg.base + offset

mmu = SegmentedMMU([
    Segment("code",  base=0x3000, limit=0x1000, executable=True),
    Segment("data",  base=0x9000, limit=0x0400, writable=True),
    Segment("heap",  base=0x6000, limit=0x2000, writable=True),
    Segment("stack", base=0xF000, limit=0x0800, writable=True),
])

print(hex(mmu.translate(0, 0x2A4, "execute")))                  # 0x32a4
print(hex(mmu.translate(3, 0x7FF, "write")))                    # 0xf7ff
for args in ((1, 0x400, "read"), (0, 0x10, "write"), (7, 0, "read")):
    try:
        mmu.translate(*args)
    except SegmentationFault as e:
        print("fault:", e)
# fault: offset 0x400 beyond limit 0x400 of segment 'data'
# fault: write not permitted on segment 'code'
# fault: no segment 7
```

This is where the phrase **"segmentation fault"** comes from. (On modern systems the same error message appears for any invalid memory access, even though the hardware now enforces it with *paging*, see section 7.)

**What segmentation gives you:**

| Benefit | Why |
|---------|-----|
| **Natural protection** | code is read-only and executable; data and stack are writable but not executable (blocks many exploits) |
| **Sharing** | two processes can map the *same* code segment (the same program or library) |
| **Growth** | a heap or stack segment can have its `limit` increased independently |
| **Meaning** | each segment corresponds to something the programmer named |

## 3. The big problem: external fragmentation

Segments have **different sizes**, so as processes start and stop, free memory is chopped into scattered **holes**. Total free space may be plenty, yet **no single hole is big enough** for a new segment. That is **external fragmentation** (paging avoids it because every frame is the same size).

A simulator for a memory with variable-size allocations, using classic placement policies:

```python
class Memory:
    def __init__(self, size):
        self.size = size
        self.blocks = []                                        # allocated blocks as (start, length, name), kept sorted by start

    def holes(self):
        free, cursor = [], 0
        for start, length, _ in self.blocks:
            if start > cursor:
                free.append((cursor, start - cursor))
            cursor = start + length
        if cursor < self.size:
            free.append((cursor, self.size - cursor))
        return free

    def allocate(self, name, length, policy="first"):
        candidates = [(s, l) for s, l in self.holes() if l >= length]
        if not candidates:
            return None
        if policy == "first":
            start = candidates[0][0]                            # the first hole that fits
        elif policy == "best":
            start = min(candidates, key=lambda h: h[1])[0]      # the smallest hole that fits (leaves the smallest leftover)
        else:
            start = max(candidates, key=lambda h: h[1])[0]      # "worst": the biggest hole
        self.blocks.append((start, length, name))
        self.blocks.sort()
        return start

    def free(self, name):
        self.blocks = [b for b in self.blocks if b[2] != name]

    def compact(self):                                          # slide everything down: removes holes, but moves data (expensive)
        cursor, packed = 0, []
        for _, length, name in self.blocks:
            packed.append((cursor, length, name))
            cursor += length
        self.blocks = packed

def scenario(policy):
    m = Memory(1000)
    for name, size in (("A", 200), ("B", 100), ("C", 150), ("D", 250), ("E", 100)):
        m.allocate(name, size, policy)
    for name in ("B", "D"):                                     # B and D finish: two holes appear
        m.free(name)
    placed = {name: m.allocate(name, size, policy) for name, size in (("F", 90), ("G", 220), ("H", 120))}
    return m, placed

for policy in ("first", "best", "worst"):
    m, placed = scenario(policy)
    free_total = sum(l for _, l in m.holes())
    print(f"{policy:5} placed={placed}  free={free_total}  largest hole={max((l for _, l in m.holes()), default=0)}")
# first placed={'F': 200, 'G': 450, 'H': 800}  free=120  largest hole=80
# best  placed={'F': 200, 'G': 450, 'H': 800}  free=120  largest hole=80
# worst placed={'F': 450, 'G': None, 'H': 800}  free=340  largest hole=160
```

Read the results. Blocks B (100 units at 200) and D (250 units at 450) were freed, so there are two holes plus the free tail. **First-fit and best-fit** placed all three new requests (F, G, H), but 120 units remain free in scattered pieces (the largest is only 80). **Worst-fit** put the 90-unit F into the biggest hole, which left no hole big enough for the 220-unit G (`None`), even though 340 units were free. Total free space does not matter; **contiguous** free space does. Typical lessons:

- **First-fit** is fast and usually good enough.
- **Best-fit** minimizes each leftover but tends to create many **tiny, useless slivers**.
- **Worst-fit** leaves large leftovers but fills big holes quickly.
- None of them eliminates the problem: **compaction** (moving segments together and updating base registers) does, at the price of copying memory.

```python
m = Memory(1000)
for name, size in (("A", 300), ("B", 200), ("C", 300)):
    m.allocate(name, size)
m.free("B")                                                     # holes: 200 bytes in the middle, 200 at the end
print(m.holes(), m.allocate("D", 350))                          # [(300, 200), (800, 200)] None    350 free in total, but not contiguous
m.compact()
print(m.holes(), m.allocate("D", 350))                          # [(600, 400)] 600                  after compaction one hole of 400 fits it
```

Total free memory was 400 both times; only compaction made a request of 350 possible. This is exactly why segmentation alone fell out of favor.

## 4. Segmentation versus paging

| | **Segmentation** | **Paging** |
|---|-------------------|------------|
| Unit | variable-size, logical (code, stack, heap) | fixed-size (4 KB), meaningless |
| Address | (segment, offset) | (page number, offset), invisible to the programmer |
| Fragmentation | **external** (holes between segments) | **internal** (unused tail of a page) |
| Protection/sharing | natural (per segment) | per page (permission bits) |
| Table size | tiny (a few segments) | large (multi-level tables) |
| Swapping | whole segments (big, slow) | single pages (fine-grained) |
| Programmer-visible? | yes (in the classic design) | no |

The winner for general-purpose systems was **paging**, because fixed-size frames make allocation trivial and eliminate external fragmentation.

## 5. Segmentation plus paging

The two combine: an address is first split by the **segment** (giving a protected, logical region), then **each segment is paged**. Intel's 32-bit x86 hardware worked this way: segment translation produced a *linear address*, which paging then mapped to physical memory.

```python
PAGE = 4096

class PagedSegment:
    def __init__(self, name, limit, frames, writable=False):
        self.name, self.limit, self.frames, self.writable = name, limit, frames, writable        # frames[i] = frame holding page i of this segment

def translate_segmented_paged(segments, seg, offset, write=False):
    s = segments[seg]
    if offset >= s.limit:
        raise SegmentationFault(f"offset {offset:#x} beyond segment '{s.name}'")
    if write and not s.writable:
        raise SegmentationFault(f"write to read-only segment '{s.name}'")
    page, within = divmod(offset, PAGE)                          # the offset inside the segment is then paged
    return s.frames[page] * PAGE + within

segments = [PagedSegment("code", limit=2 * PAGE, frames=[40, 7]), PagedSegment("heap", limit=3 * PAGE, frames=[12, 90, 33], writable=True)]
print(hex(translate_segmented_paged(segments, 0, PAGE + 0x10)))                 # 0x7010     second page of code lives in frame 7
print(hex(translate_segmented_paged(segments, 1, 2 * PAGE + 5, write=True)))    # 0x21005    third page of the heap lives in frame 33
```

The segment keeps **logical protection and sharing**; paging keeps **allocation simple** (no external fragmentation).

## 6. What happened to segmentation in practice

- **64-bit x86 (x86-64)** largely **disabled segmentation**: the base of the code, data and stack segments is forced to 0 and the limit ignored, the **flat memory model**. Protection is done entirely by **paging** (read, write, execute-disable bits). A "segmentation fault" today is a *page-level* violation reported with the old name.
- Two segment registers remain useful: **`FS` and `GS`** hold a base address, used by operating systems for **thread-local storage** (each thread's `FS` base points at its own data block) and by the kernel for per-CPU data.
- **Memory-safe designs** (WebAssembly's linear memory, hardware capability systems like CHERI) reintroduce bounds checks conceptually similar to base and limit.
- The idea of "separate regions with different permissions" lives on in the process layout and in **`mmap`**, **W^X** (a page is writable or executable, never both) and **ASLR** (randomizing where regions are placed).

You can see a process's regions in Python on Linux through `/proc/self/maps`:

```python
import os

if os.path.exists("/proc/self/maps"):
    regions = [line.split()[1] for line in open("/proc/self/maps")]          # e.g. "r-xp", "rw-p"
    print(sorted({r for r in regions})[:4], "...")                          # permission strings such as ['---p', 'r--p', 'r-xp', 'rw-p']
else:
    print("no /proc on this system (macOS): try `vmmap <pid>` or `pmap` on Linux")      # no /proc on this system (macOS): try `vmmap <pid>` or `pmap` on Linux
```

## 7. A real segment descriptor (x86 GDT entry)

On classic x86, segments are described by **8-byte descriptors** in the **Global Descriptor Table (GDT)**. The layout is scattered across the bytes for historical reasons, which makes it a good bit-manipulation exercise: base is 32 bits, limit 20 bits, plus access and flag bits.

```text
bytes 0-1: limit bits 0-15              byte 5: access byte  (present, privilege level, type, executable, rw ...)
bytes 2-3: base bits 0-15               byte 6: low nibble = limit bits 16-19; high nibble = flags (granularity, 32-bit)
byte 4:    base bits 16-23              byte 7: base bits 24-31
```

```python
import struct

def parse_descriptor(raw: bytes):
    limit_low, base_low, base_mid, access, flags_limit, base_high = struct.unpack("<HHBBBB", raw)
    base = base_low | (base_mid << 16) | (base_high << 24)
    limit = limit_low | ((flags_limit & 0x0F) << 16)
    flags = flags_limit >> 4
    if flags & 0x8:                                              # granularity bit: the limit counts 4 KB pages, not bytes
        limit = (limit << 12) | 0xFFF
    return {
        "base": hex(base),
        "limit": hex(limit),
        "present": bool(access & 0x80),
        "privilege": (access >> 5) & 0b11,                       # ring 0 = kernel ... ring 3 = user
        "code": bool(access & 0x08),                             # executable segment (code) or data
        "writable_or_readable": bool(access & 0x02),
    }

def build_descriptor(base, limit, access, flags):
    return struct.pack("<HHBBBB", limit & 0xFFFF, base & 0xFFFF, (base >> 16) & 0xFF, access,
                       ((flags & 0xF) << 4) | ((limit >> 16) & 0x0F), (base >> 24) & 0xFF)

# The classic flat 32-bit kernel code segment: base 0, limit 4 GiB, ring 0, executable and readable
kernel_code = build_descriptor(base=0, limit=0xFFFFF, access=0x9A, flags=0xC)
user_data = build_descriptor(base=0, limit=0xFFFFF, access=0xF2, flags=0xC)
print(kernel_code.hex())                                         # ffff0000009acf00
print(parse_descriptor(kernel_code))
# {'base': '0x0', 'limit': '0xffffffff', 'present': True, 'privilege': 0, 'code': True, 'writable_or_readable': True}
print(parse_descriptor(user_data)["privilege"], parse_descriptor(user_data)["code"])         # 3 False   ring 3 (user), data segment
assert parse_descriptor(build_descriptor(0x12345678, 0x00ABC, 0x92, 0x4))["base"] == "0x12345678"
```

Note the **flat model** in action: `base 0` and `limit 4 GiB` make a segment that covers the entire address space, so the segment translation does nothing and paging does all the work. Operating systems still need descriptors for the **privilege level**: ring 0 (kernel) versus ring 3 (user), which is what separates your programs from the kernel ([OS overview](../00-what-is-an-operating-system.md)).

## 8. Two real-world examples

**Example 1: Why a null-pointer dereference crashes with "segmentation fault".** The page at address 0 is deliberately left **unmapped**, so any access to it traps. The kernel turns the trap into the `SIGSEGV` signal and ends the process (see [signals](../processes-threads/01-processes-in-practice.md)): the hardware mechanism is paging, the name is a historical leftover from segmentation.

**Example 2: Stack and heap growth.** The process layout (code, data, heap growing up, stack growing down, with a large gap between) is segmentation thinking implemented with paging: regions with their own permissions and growth rules. `ulimit -s` limits the stack segment's size, and exceeding it causes exactly the fault described here (stack overflow).

## 9. Common mistakes

- Confusing segments (variable-size logical pieces) with pages (fixed-size physical units).
- Forgetting the **limit check** (`offset < limit`, not `<=`).
- Believing external fragmentation is cured by total free space: it needs a contiguous hole.
- Assuming modern 64-bit systems still use segment bases and limits for protection (they use paging).
- Treating "segmentation fault" as always meaning a segment violation; it is any invalid memory access.
- Mixing the byte order or bit positions when parsing descriptors (they are little-endian and split).

## 10. Practice

1. With the example `mmu`, translate `(2, 0x1000)` and `(2, 0x2000)` (the heap). What happens for each?
2. Why does best-fit often produce many tiny leftover holes?
3. Memory is 1000 units; holes are of sizes 120, 300 and 180 (non-adjacent). A request of 250 arrives. Which hole does each policy choose?
4. Build a descriptor for a data segment with base `0x00100000`, limit `0x0FFFF` (byte granularity), ring 3, writable, and print the parsed fields.
5. Why do both segmentation and paging exist in the same hardware?
6. What do `FS` and `GS` do on modern x86-64?
7. Explain why internal and external fragmentation are different problems.

<details>
<summary>Solutions</summary>

1. `(2, 0x1000)` is within the heap limit `0x2000`, so it maps to `0x6000 + 0x1000 = 0x7000`; `(2, 0x2000)` equals the limit, so it is out of bounds and faults.
   ```python
   print(hex(mmu.translate(2, 0x1000, "write")))               # 0x7000
   try:
       mmu.translate(2, 0x2000)
   except SegmentationFault as e:
       print(e)                                                # offset 0x2000 beyond limit 0x2000 of segment 'heap'
   ```
2. It always picks the smallest hole that fits, so the leftover after placement is as small as possible: those slivers are too small for almost any later request.
3. First-fit takes the first hole that is big enough: the 300 (the 120 is too small). Best-fit takes the smallest sufficient hole: 300 (the 180 is too small as well). Worst-fit takes the largest: 300. With these sizes all three pick the same hole; try holes of 400 and 300 to see them differ (first-fit 400, best-fit 300, worst-fit 400).
4. ```python
   d = build_descriptor(base=0x00100000, limit=0x0FFFF, access=0xF2, flags=0x4)
   print(d.hex(), parse_descriptor(d))
   # ffff000010f24000 {'base': '0x100000', 'limit': '0xffff', 'present': True, 'privilege': 3, 'code': False, 'writable_or_readable': True}
   ```
5. Segmentation supplies logical, protected regions with per-region permissions and sharing; paging supplies uniform, fragmentation-free allocation. Together (as on 32-bit x86) the OS gets both; 64-bit systems keep only paging plus the flat model.
6. They hold a base address used for **thread-local storage** (per-thread data) and kernel per-CPU data; the other segment bases are forced to zero.
7. Internal fragmentation is wasted space *inside* an allocated unit (the unused end of the last page); external fragmentation is free space scattered *between* allocations, too fragmented to satisfy a large request.

</details>

## 11. Check yourself

1. What is a segment, and what two numbers describe it?
2. How is a `(segment, offset)` address translated, and when does it fault?
3. What is external fragmentation and how can you remove it?
4. How does paging differ from segmentation?
5. Why do modern 64-bit systems rely on paging, and what are `FS`/`GS` still used for?
6. What does a GDT descriptor contain?

<details>
<summary>Answers</summary>

1. A contiguous, variable-size region of a program's logical memory (code, heap, stack...); described by its base and its limit (plus permissions).
2. Look up the segment, check `offset < limit` and the access permission, then physical = `base + offset`; it faults (segmentation fault) on a bad segment number, an offset beyond the limit or a forbidden access.
3. Free memory split into holes between variable-size blocks, none large enough for a big request even though the total is enough; compaction (moving blocks together) removes it, at the cost of copying.
4. Paging uses fixed-size, invisible, uniform pages (internal fragmentation only); segmentation uses variable-size logical pieces visible to the programmer (external fragmentation).
5. Paging gives simple allocation and fine-grained protection with no external fragmentation; `FS`/`GS` carry base addresses for thread-local and per-CPU data.
6. A base address, a limit, and access/flag bits (present, privilege ring, code or data, readable or writable, granularity, 32-bit).

</details>

[Back to memory management](README.md) · Previous: [page replacement algorithms](02-page-replacement-algorithms.md)
