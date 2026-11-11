# CPU Caches and the Memory Hierarchy

**Prerequisites:** [How a computer runs your program](how-computers-work.md), [memory, the stack and the heap](memory-stack-heap.md), [Big-O basics](../../01-complexity/README.md). **You will learn:** why the *same* algorithm can run 5 times slower just by touching memory in a different order, how the **memory hierarchy** (registers, L1/L2/L3 cache, RAM, SSD, network) trades speed for size, what **locality** and **cache lines** are, and how to **measure and simulate** the effect: a working cache simulator that explains why row-by-row traversal beats column-by-column, plus real timings from Python.

## 1. In plain words

A cook can pick up an ingredient from the **counter** instantly, walk to the **fridge** in a few seconds, or drive to the **supermarket** in half an hour. Smart cooks bring what they will need to the counter *before* they need it, and use ingredients that are already nearby. A CPU is the same: it can compute in a fraction of a nanosecond but waiting for data from main memory takes **about a hundred times longer**. Hardware hides the gap with **caches**: small, very fast memories holding recently used data. A program that reuses nearby data runs fast; one that jumps around memory spends most of its time waiting.

## 2. The memory hierarchy

Typical, rounded numbers for a modern laptop or server (they vary by machine, but the **ratios** matter):

| Level | Typical size | Latency | If one nanosecond were one second |
|-------|--------------|---------|-----------------------------------|
| CPU register | a few hundred bytes | under 1 ns | instant |
| L1 cache | 32 to 64 KB per core | ~1 ns | 1 second |
| L2 cache | 256 KB to 2 MB per core | ~4 ns | 4 seconds |
| L3 cache | 8 to 64 MB (shared) | ~15 ns | 15 seconds |
| Main memory (RAM) | 8 to 256 GB | ~100 ns | about 2 minutes |
| SSD | 256 GB to several TB | ~100 microseconds | about 1 day |
| Hard disk | TB | ~10 milliseconds | about 4 months |
| Network, same data centre | | ~0.5 ms | about 6 days |
| Network, across a continent | | ~150 ms | about 5 years |

The pattern: each step down is **bigger, cheaper per byte, and 10 to 1000 times slower**. This is the real reason for [caching in system design](../../09-interview-playbook/system-design-basics/03-caching-failure-modes-and-reliability.md), database [indexes](../../05-databases/indexes-query-plans/README.md) and operating-system [page caches](../../06-operating-systems/memory-virtual-memory/README.md): the same idea at every scale.

## 3. Locality and cache lines

Caches work because programs show **locality**:

- **Temporal locality:** data used recently is likely to be used again soon (a loop counter, a hot variable).
- **Spatial locality:** data near recently used data is likely to be used soon (the next array element).

The cache exploits spatial locality by never fetching a single byte: it moves a whole **cache line** (typically **64 bytes**) at a time. Read element 0 of an array of 8-byte integers, and elements 0 to 7 arrive together; the next seven reads are **free**. The hardware also **prefetches**: it notices sequential access and starts loading the next lines before you ask.

So accessing 8-byte elements one after another costs one slow memory trip per eight accesses, while accessing every 64th byte costs one trip **per access**: eight times the memory traffic for the same number of operations.

## 4. A cache simulator

You can see the effect without special hardware by simulating a cache. This is a **set-associative cache with LRU replacement**: memory is split into 64-byte lines; each line may live in one *set*; each set holds a few lines (the *ways*) and evicts the least recently used one when full. It counts hits and misses.

```python
from collections import OrderedDict

class Cache:
    """A set-associative cache with LRU replacement. Addresses are byte addresses."""
    def __init__(self, size=32 * 1024, line=64, ways=8):
        self.line, self.ways = line, ways
        self.sets = size // (line * ways)
        self.data = [OrderedDict() for _ in range(self.sets)]
        self.hits = self.misses = 0

    def access(self, addr):
        line_no = addr // self.line                      # which 64-byte line holds this byte
        s, tag = line_no % self.sets, line_no // self.sets
        ways = self.data[s]
        if tag in ways:
            ways.move_to_end(tag)                        # hit: now the most recently used
            self.hits += 1
        else:
            self.misses += 1                             # miss: fetch the line from the next level
            ways[tag] = True
            if len(ways) > self.ways:
                ways.popitem(last=False)                 # evict the least recently used line

    @property
    def hit_rate(self):
        return self.hits / (self.hits + self.misses)

# a 32 KB cache reading 8-byte numbers one after another through 1 MB
c = Cache()
for a in range(0, 1 << 20, 8):
    c.access(a)
print(f"sequential reads: hit rate {c.hit_rate:.1%}")
# sequential reads: hit rate 87.5%
```

87.5 percent is exactly `7 / 8`: one miss brings in a line holding eight numbers, the next seven reads hit. Now vary the **stride** (distance between consecutive reads) over the same memory:

```python
for stride in (8, 16, 32, 64, 128):
    c = Cache()
    for a in range(0, 1 << 20, stride):
        c.access(a)
    print(f"stride {stride:>3} bytes: hit rate {c.hit_rate:6.1%}")
# stride   8 bytes: hit rate  87.5%
# stride  16 bytes: hit rate  75.0%
# stride  32 bytes: hit rate  50.0%
# stride  64 bytes: hit rate   0.0%
# stride 128 bytes: hit rate   0.0%
```

Once the stride reaches the line size, **every** access lands on a new line and nothing is ever reused.

### Row-major versus column-major traversal

A 2-D array is stored in memory **row by row** (row-major, as in C, NumPy and flattened Python code): element `[i][j]` is at address `(i * N + j) * 8`. Summing a 256 by 256 array of 8-byte numbers (512 KB, much bigger than the cache) in two orders:

```python
N, ELEM = 256, 8

def address(i, j):
    return (i * N + j) * ELEM

def row_major():                                    # walks along each row: consecutive addresses
    for i in range(N):
        for j in range(N):
            yield address(i, j)

def column_major():                                 # walks down each column: jumps N*8 = 2048 bytes every step
    for j in range(N):
        for i in range(N):
            yield address(i, j)

def tiled(block=8):                                 # visit the matrix in small 8x8 tiles that fit in cache
    for bi in range(0, N, block):
        for bj in range(0, N, block):
            for j in range(bj, bj + block):
                for i in range(bi, bi + block):
                    yield address(i, j)

for name, order in [("row-major", row_major), ("column-major", column_major), ("tiled 8x8 (column order inside)", tiled)]:
    c = Cache()
    for a in order():
        c.access(a)
    print(f"{name:<34} hit rate {c.hit_rate:6.1%}  misses {c.misses}")
# row-major                          hit rate  87.5%  misses 8192
# column-major                       hit rate   0.0%  misses 65536
# tiled 8x8 (column order inside)    hit rate  87.5%  misses 8192
```

Same 65,536 reads, but **eight times as many trips to memory** for column order. The **tiled** version also walks by columns, but only inside an 8 by 8 block whose 8 lines stay in cache while we use all the data in them: it recovers the row-major hit rate. This **blocking** (tiling) trick is how fast matrix multiplication and image-processing libraries get their speed.

### Working set versus cache size

Reuse only helps if the data is still in the cache when you come back:

```python
for kb in (16, 64):
    c = Cache()
    for repetition in range(2):                      # read the same block of memory twice
        for a in range(0, kb * 1024, 8):
            c.access(a)
    print(f"read a {kb} KB block twice: hit rate {c.hit_rate:.1%}")
# read a 16 KB block twice: hit rate 93.8%
# read a 64 KB block twice: hit rate 87.5%
```

A 16 KB block **fits** in the 32 KB cache, so the second pass hits entirely (93.8 percent overall). A 64 KB block does not fit: by the time we return to the start, LRU has evicted it, so the second pass gets nothing extra (87.5 percent, from spatial locality alone). Keeping the **working set** (the data you actively use) smaller than the cache is a powerful optimisation.

## 5. Measuring it on a real machine, from Python

Python's interpreter overhead hides some of the effect, but it is still visible. This reads the **same number of bytes** from a 64 MB buffer in three orders: sequential, with a stride, and randomly. The Python work per read is identical, so any difference comes from memory.

```python
import random, time
from array import array

SIZE, COUNT = 1 << 26, 1_000_000                     # a 64 MB buffer, one million reads
buffer = array("B", bytes(SIZE))
rng = random.Random(1)

orders = {
    "sequential": list(range(COUNT)),
    "stride 4099": [(i * 4099) % SIZE for i in range(COUNT)],
    "random": [rng.randrange(SIZE) for _ in range(COUNT)],
}

def read_all(indices):
    total = 0
    for i in indices:
        total += buffer[i]
    return total

times = {}
for name, indices in orders.items():
    start = time.perf_counter()
    read_all(indices)
    times[name] = time.perf_counter() - start

print("random is slower than sequential:", times["random"] > 1.5 * times["sequential"])
print("stride is slower than sequential:", times["stride 4099"] > 1.2 * times["sequential"])
# random is slower than sequential: True
# stride is slower than sequential: True
for name, seconds in times.items():
    print(f"{name:<12} {seconds / times['sequential']:.1f}x")
# sequential   1.0x
# stride 4099  2.5x          (your numbers will differ, but random is always the slowest)
# random       4.8x
```

On the machine used for this lesson, random access was around **5 times** slower than sequential for identical Python code. With NumPy, where the interpreter overhead disappears, the effect is even sharper: summing the 4096 columns of a 4096 by 4096 array one by one (strided access) took about **14 times longer** than summing the 4096 rows one by one.

## 6. What this means for the code you write

- **Arrays beat linked structures.** A list or array stores neighbours next to each other, so a scan uses whole cache lines. A linked list stores each node wherever the allocator put it, so each `next` pointer is a likely cache miss (**pointer chasing**). This is why `list` and `array` usually beat linked lists in practice even when Big-O says "O(1) insertion" ([linked lists](../../02-data-structures/linked-lists/README.md)).
- **Python lists of objects are cache-unfriendly:** a list holds *pointers* to objects scattered around the heap. NumPy and pandas store raw numbers contiguously, which is a large part of why they are fast ([NumPy lesson](../../08-modern-python/data-with-numpy-pandas/01-numpy-and-pandas-essentials.md)).
- **Struct of arrays versus array of structs:** if a loop only needs one field (the `price`) of a million records, storing each field in its own array reads only useful bytes; an array of whole records drags the unused fields through the cache too. **Columnar** databases and formats (Parquet) use this idea.
- **Loop order matters** for multi-dimensional data: make the innermost loop run along the contiguous dimension (the last index in row-major layouts).
- **Hash tables and trees** scatter data (random access), so large ones are slower than their operation counts suggest; **B-trees** store many keys per node (one node per cache line or disk block) precisely to cut the number of slow memory or disk trips ([indexes](../../05-databases/indexes-query-plans/README.md)).
- **Virtual memory** adds another cache, the **TLB**, for address translation; huge scattered working sets also miss there ([virtual memory](../../06-operating-systems/memory-virtual-memory/README.md)).
- **Multi-core:** each core has its own L1/L2; when two threads write different variables that share one cache line, the line bounces between cores (**false sharing**), slowing both. Padding hot per-thread data apart fixes it. (CPython's GIL hides most of this for pure Python; native code feels it.)
- **Measure before optimising:** locality is one factor among many; use a [profiler](../../08-modern-python/performance-profiling/README.md) to find the real bottleneck first, and prefer better algorithms and data structures over micro-tuning.

## 7. Common mistakes

- Treating all memory accesses as equal cost ("it is O(n) either way").
- Looping over a 2-D structure in the wrong order, or transposing data by striding through it.
- Using a linked structure for sequential workloads where an array would do.
- Optimising memory layout without measuring (the effect is real but only matters on large data in hot loops).
- Benchmarking with tiny inputs that fit entirely in cache, then being surprised at production sizes.
- Forgetting that the first run is slow because the caches (and the disk's page cache) are cold.

## 8. Two real-world examples

**Example 1: The matrix that "should" be fast.** An image-processing script rotated large images by reading pixels column by column. The algorithm was the same as the optimised version, but each read jumped a full image row (several kilobytes), so nearly every read missed the cache. Processing the image in 64 by 64 tiles (reading and writing small blocks that fit in cache) gave a 6 times speed-up without changing the mathematics.

**Example 2: The record scanner.** A service stored one million user records as a list of Python objects with 20 fields and summed one numeric field per request. Moving that column into a NumPy array (contiguous, 8 bytes per value) made the scan read about 8 MB instead of hundreds of megabytes spread across the heap, and turned a 400 ms request into 3 ms.

## 9. Practice

1. Change the cache in the simulator to 64 KB with 4 ways. Re-run the 16 KB and 64 KB double-read experiment. What changes and why?
2. Predict, then measure with the simulator, the hit rate for the column-major traversal if the matrix were only 32 by 32 (8 KB total). Why is it so much better than for 256 by 256?
3. Write a generator for **row-major order but reading two arrays** `A` and `B` alternately (addresses in different regions). Does the hit rate change? What if both regions map to the same cache sets (try offsets that are multiples of the cache size)?
4. A function sums every 16th element of a huge array of 8-byte numbers. What hit rate do you expect with a 64-byte line, and what is the lesson for data layout?
5. Why does a binary search on a huge sorted array suffer more cache misses than a B-tree lookup of the same data?
6. Explain in one paragraph why a Python list of 1 million floats is slower to sum than a NumPy array of 1 million floats, mentioning at least two causes besides the interpreter loop.

<details>
<summary>Solutions</summary>

1. ```python
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
2. ```python
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

## 10. Check yourself

1. Why is main memory about 100 times slower to reach than L1 cache, and how do caches hide that?
2. What is a cache line, and why does reading one element make the next ones cheap?
3. Define temporal and spatial locality with an example each.
4. Why is column-major traversal of a row-major array slow?
5. What is a working set, and why does it matter?
6. Why can a linked list lose to an array even when Big-O favours the list?
7. What is blocking (tiling)?

<details>
<summary>Answers</summary>

1. Main memory is physically farther away and built for capacity rather than speed; caches keep recently and nearby used data in small, fast memory close to the core.
2. The unit of transfer between memory and cache (usually 64 bytes); neighbouring elements arrive in the same line, so later reads hit the cache.
3. Temporal: reusing a variable in a loop; spatial: reading the next array element after the current one.
4. Each step jumps a whole row ahead, so every read lands on a different cache line and the lines are evicted before they are reused.
5. The data a program actively uses over a period; if it fits in cache the program runs fast, if not it keeps missing.
6. List nodes are scattered in memory so each step is likely a cache miss; array elements are contiguous so scanning uses full cache lines and prefetching.
7. Reordering a loop to work on small blocks of data that fit in cache and fully using each block before moving on.

</details>

[Back to computer basics](README.md)
