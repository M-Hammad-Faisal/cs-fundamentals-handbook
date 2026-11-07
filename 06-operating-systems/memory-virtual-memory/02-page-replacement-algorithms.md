# Page Replacement Algorithms

**Prerequisites:** [paging and address translation](01-paging-and-address-translation.md), [queues](../../02-data-structures/stacks-queues/02-queues-deques-priority-queues.md), [LRU cache](../../02-data-structures/linked-lists/02-doubly-and-circular.md). **You will learn:** what the OS does when RAM is full and a needed page is not in memory, the policies **FIFO, Optimal, LRU, Clock (second chance)** with a runnable simulator, **Belady's anomaly**, and the ideas of **working set** and **thrashing**.

## 1. The problem

RAM has a fixed number of **frames**. A page fault needs a free frame; if none is free, the OS must **evict a victim page** to disk and reuse its frame. Choose badly and you evict something you need a moment later, causing another fault (about a million times slower than a RAM hit). A **page replacement algorithm** decides the victim.

We judge an algorithm by the **number of page faults** on a **reference string** (the sequence of pages a program touches).

## 2. A simulator

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

refs = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]      # the classic textbook string
print(fifo(refs, 3), lru(refs, 3), optimal(refs, 3))       # 15 12 9
```

With 3 frames: **FIFO 15 faults, LRU 12, Optimal 9** (out of 20 references).

## 3. FIFO: evict the oldest

Simple, but "oldest" does not mean "unused": a page loaded long ago may be used constantly (the start of the program). FIFO can evict it and fault immediately.

Trace of the first few references with 3 frames (`F` = fault):

```text
ref:     7   0   1   2   0   3   0   4
frames: [7] [7,0] [7,0,1] [0,1,2] [0,1,2] [1,2,3] [2,3,0] [3,0,4]
fault:   F   F    F       F       .       F       F       F
```

(On reference `2`, page 7, the oldest, is evicted even though it may be needed again.)

### Belady's anomaly: more memory, more faults

Intuition says more frames cannot hurt. For FIFO it can:

```python
belady = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
for frames in range(1, 8):
    print(frames, fifo(belady, frames), lru(belady, frames))
# 1 12 12
# 2 12 12
# 3 9 10
# 4 10 8
# 5 5 5
# 6 5 5
# 7 5 5
```

FIFO goes from **9 faults with 3 frames to 10 with 4 frames**. LRU and Optimal never do this (they are **stack algorithms**: the set of pages held with `n` frames is always a subset of those held with `n + 1`).

## 4. Optimal (Belady's MIN): evict what is needed farthest in the future

It gives the **minimum possible faults** but needs knowledge of the future, so it cannot be implemented in a real OS. Its role is a **yardstick**: a good practical algorithm should come close.

## 5. LRU: evict the least recently used

Past behavior predicts the future (**temporal locality**): a page unused for a long time is unlikely to be needed soon. LRU approximates Optimal looking *backwards* instead of forwards.

Perfect LRU needs updating a recency record on **every memory access**, far too expensive in hardware or software for pages (it is fine for a software cache such as `functools.lru_cache`). Real systems **approximate** it.

## 6. Clock (second chance): cheap LRU approximation

The MMU sets a **reference bit** in a page's entry whenever the page is accessed. Arrange the frames in a circle with a "clock hand":

1. Look at the page under the hand.
2. If its reference bit is **1**, clear it to 0 and advance (a **second chance**).
3. If it is **0**, evict it.

```python
def clock(refs, frames):
    pages = [None] * frames
    ref_bit = [0] * frames
    hand, faults = 0, 0
    for page in refs:
        if page in pages:
            ref_bit[pages.index(page)] = 1                 # hardware sets the bit on access
            continue
        faults += 1
        while ref_bit[hand] == 1:                          # skip (and clear) recently used pages
            ref_bit[hand] = 0
            hand = (hand + 1) % frames
        pages[hand], ref_bit[hand] = page, 1               # replace the victim
        hand = (hand + 1) % frames
    return faults

print(clock(refs, 3), clock(belady, 3), clock(belady, 4))   # 14 9 10
```

On the classic string Clock gets 14 faults: between FIFO (15) and LRU (12). It costs one bit per page and one hand movement per fault, which is why Linux, BSD and others use variants of it (Linux keeps "active" and "inactive" lists with the same idea). Clock can also exhibit Belady-like behavior because it degenerates to FIFO when all bits are set.

**Enhanced clock** also considers the **dirty bit**: prefer evicting clean pages (no write-back needed) over dirty ones.

## 7. Comparing on realistic workloads

Real programs show **locality**: they stay inside a small set of pages for a while. Random references (no locality) make every algorithm look alike. Generate a workload with locality to see the difference:

```python
import random

def locality_trace(n=5000, hot=8, total=200, seed=1):
    random.seed(seed)
    trace, base = [], 0
    for i in range(n):
        if i % 500 == 0:
            base = random.randrange(total - hot)           # the program moves to a new "phase" (a new working set)
        trace.append(base + random.randrange(hot) if random.random() < 0.95 else random.randrange(total))
    return trace

local = locality_trace()
uniform = [random.randrange(200) for _ in range(5000)]
for name, trace in (("locality", local), ("random", uniform)):
    print(f"{name:9}", {algo.__name__: algo(trace, 10) for algo in (fifo, lru, optimal, clock)})
# locality  {'fifo': 703, 'lru': 370, 'optimal': 282, 'clock': 498}
# random    {'fifo': 4790, 'lru': 4792, 'optimal': 3776, 'clock': 4792}
```

On the locality trace the choice matters a lot: FIFO faults 703 times, Clock 498, LRU 370, and Optimal 282. On the random trace FIFO, LRU and Clock are indistinguishable (about 4790 faults of 5000 references): with no locality there is no pattern for a policy to exploit, and only the clairvoyant Optimal does noticeably better.

## 8. Working sets and thrashing

The **working set** of a process is the set of pages it has used in its recent past (say the last `Δ` references). If the process is given **fewer frames than its working set**, it faults constantly.

```python
def working_set_size(trace, window):
    return [len(set(trace[max(0, i - window + 1): i + 1])) for i in range(len(trace))]

sizes = working_set_size(local, 100)
print(max(sizes) <= 100, round(sum(sizes) / len(sizes)))     # True 14   (on average only 14 distinct pages are in use over any 100 references)
```

**Thrashing** happens when the total working sets of all running processes exceed RAM: every process faults, the CPU waits on the disk, utilization collapses, and the OS (seeing low CPU use) may start *more* processes, making it worse. Cures: reduce the number of running processes (swap one out entirely), add RAM, or use a **local replacement policy** with working-set or **page-fault-frequency** control (give more frames to processes that fault too often, take frames from those that fault rarely).

```python
def faults_by_frames(trace, algo=lru):
    return {f: algo(trace, f) for f in (2, 4, 8, 16, 32)}

curve = faults_by_frames(local)
print(curve)                                               # {2: 3932, 4: 2759, 8: 757, 16: 292, 32: 269}
```

This "faults vs frames" curve has a **knee**: going from 8 to 16 frames cuts faults from 757 to 292, but 16 to 32 only from 292 to 269. Below the working-set size faults explode; above it, extra frames barely help.

## 9. Other practical details

- **Global vs local replacement:** pick victims from all pages in the system, or only from the faulting process's own pages.
- **Page buffering and pre-fetching:** keep a few free frames ready; read ahead for sequential access.
- **Swap space:** where evicted dirty (anonymous) pages go; clean file-backed pages are simply dropped and re-read from their file.
- **Huge pages** (2 MB): fewer TLB entries, but coarser eviction.
- **Linux specifics:** `vm.swappiness` tunes how eagerly anonymous pages are swapped versus dropping file cache; the **OOM killer** terminates processes when memory is truly exhausted.

## 10. Two real-world examples

**Example 1: Database buffer pools.** PostgreSQL and MySQL keep their own page cache in RAM and use LRU/Clock variants to decide which table or index pages to evict. A single huge sequential scan can flush out all hot pages ("cache pollution"), so databases use scan-resistant variants (MySQL splits LRU into young/old regions; Postgres uses a small ring buffer for big scans).

**Example 2: Your laptop at 20 tabs.** The browser's idle tabs are swapped or compressed first (cold pages), and the tab you click is paged back in: a noticeable pause is exactly a burst of page faults.

## 11. Common mistakes

- Assuming FIFO is "fair" and therefore good (it ignores usage and can show Belady's anomaly).
- Believing Optimal is a usable algorithm (it needs the future).
- Counting a hit as a fault or forgetting that the first reference to each page is always a fault (a **compulsory miss**).
- Forgetting to update recency on a **hit** in an LRU implementation.
- Measuring replacement policies on random traces without locality.
- Confusing virtual memory size with RAM and ignoring thrashing.

## 12. Practice

1. Simulate FIFO and LRU by hand for the string `1, 2, 3, 1, 4, 2` with 3 frames. Count faults.
2. How many compulsory misses does `[1, 2, 1, 3, 2, 4]` have?
3. Why can Optimal never be worse than LRU?
4. What does the reference bit do in the Clock algorithm?
5. Give a reference string where LRU performs badly (hint: loop over `n + 1` pages with `n` frames).
6. What are the symptoms of thrashing and the cure?
7. Add a `mru` (most recently used) policy to the simulator. On which pattern does it beat LRU?

<details>
<summary>Solutions</summary>

1. FIFO: faults on 1, 2, 3 (3), hit 1, fault 4 (evicts 1; frames 2,3,4), fault 2? No: 2 is still present, hit. Total FIFO = 4. LRU: faults on 1, 2, 3 (3), hit 1, fault 4 (evicts 2, the least recently used; frames 3,1,4), fault 2 (evicts 3): total 5.
   ```python
   s = [1, 2, 3, 1, 4, 2]
   print(fifo(s, 3), lru(s, 3))                          # 4 5
   ```
2. Distinct pages: `{1, 2, 3, 4}`: **4** compulsory misses.
3. Optimal always evicts the page needed farthest in the future, which no algorithm can beat on that string (the proof shows any other choice leads to at least as many later faults).
4. It records that the page was used recently; Clock clears it as the hand passes (second chance) and evicts a page only when its bit is already 0.
5. A loop over one more page than there are frames: LRU evicts exactly the page needed next, every time.
   ```python
   loop = list(range(4)) * 10
   print(lru(loop, 3), optimal(loop, 3))                 # 40 16
   ```
6. Very high fault rate, low CPU utilization, the disk constantly busy. Cure: fewer running processes, more RAM, or working-set/page-fault-frequency control.
7. ```python
   def mru(refs, frames):
       memory, last, faults = [], None, 0
       for page in refs:
           if page in memory:
               last = page; continue
           faults += 1
           if len(memory) == frames:
               memory.remove(last)                       # evict the most recently used
           memory.append(page); last = page
       return faults
   print(mru(loop, 3), lru(loop, 3))                     # 16 40  (MRU wins on cyclic scans bigger than memory)
   ```

</details>

## 13. Check yourself

1. What does a page replacement algorithm decide?
2. What is Belady's anomaly and which algorithms avoid it?
3. Why is Optimal useful if it cannot be implemented?
4. How does Clock approximate LRU?
5. What is a working set?
6. What causes thrashing?

<details>
<summary>Answers</summary>

1. Which resident page to evict when a page fault occurs and no frame is free.
2. More frames producing more faults (seen with FIFO); stack algorithms like LRU and Optimal avoid it.
3. It gives the lower bound on faults, a benchmark for real algorithms.
4. A reference bit per page and a sweeping hand: recently used pages get a second chance, others are evicted.
5. The set of pages a process has used in its recent past.
6. Total working sets exceeding RAM, so processes continually fault each other's pages out.

</details>

[Back to memory management](README.md) · Previous: [paging and address translation](01-paging-and-address-translation.md)
