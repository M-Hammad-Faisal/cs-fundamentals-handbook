# Memory Management and Virtual Memory: One-Page Summary

- **Virtual memory** = per-process address space translated by the MMU. Gives isolation, uniform layout, overcommit, sharing.
- **Paging:** address = `page number | offset`; the page table maps page to frame; PTE flags: present, R/W/X, user, dirty, accessed. Multi-level tables keep sparse spaces cheap.
- **TLB** caches translations; flushes on process switch; huge pages reduce misses.
- **Page faults:** minor (map only), major (disk read), invalid (SIGSEGV). Demand paging and copy-on-write rely on them.
- **Replacement:** FIFO (Belady's anomaly), LRU (good, costly), Optimal (benchmark), Clock (practical LRU). Example: 12-reference string, FIFO 9 faults with 3 frames and 10 with 4.
- **Thrashing:** working sets exceed RAM; reduce load or add RAM.
- **Layout:** text, data, heap (up), mmap region, stack (down).
- **Fragmentation:** internal (inside blocks) vs external (between blocks).
- **VIRT vs RSS:** judge memory by RSS; containers die on RSS-based limits.
- `mmap` maps files lazily and shares pages between processes.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Virtual Memory](01-paging-and-address-translation.md) · [Page Replacement Algorithms](02-page-replacement-algorithms.md) · [Segmentation](03-segmentation.md)
