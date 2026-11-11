# Heaps and Priority Queues: One-Page Summary

## Key facts

- Complete binary tree with the heap property (min-heap: parent <= children).
- Only the root is guaranteed extreme; the rest is partially ordered.
- Stored in an array: `parent = (i-1)//2`, `left = 2i+1`, `right = 2i+2`.

### Costs

| Operation | Cost |
|-----------|------|
| Peek | `O(1)` |
| Push / pop | `O(log n)` |
| Heapify (build) | `O(n)` |
| Search / arbitrary remove | `O(n)` |

### Python

- `heapq` is a **min-heap** on a list: `heappush`, `heappop`, `heapify`, `nlargest`, `nsmallest`, `heappushpop`.
- Max-heap: push negated values.
- Use `(priority, counter, item)` tuples to avoid comparing items.

### Patterns

- **Top K:** keep a min-heap of size K (`O(n log K)`).
- **Merge K sorted:** heap of heads (`O(N log K)`).
- **Running median:** max-heap (lower half) + min-heap (upper half).
- **Heap sort:** `O(n log n)`, in place, not stable.
- **Dijkstra, schedulers, timers:** priority queue.

## Pitfalls

- A heap is not sorted.
- Priority updates need lazy deletion.
- Pushing items one by one when `heapify` would be `O(n)`.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Binary Heaps and Heapsort](01-binary-heaps-and-heapsort.md) · [Priority Queue Applications](02-priority-queue-applications.md)
