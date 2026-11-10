# Stacks and Queues: One-Page Summary

## Facts
- **Stack** = LIFO (`push`, `pop`, `peek`). In Python: a `list`.
- **Queue** = FIFO (`enqueue`, `dequeue`). In Python: `collections.deque`.
- **Deque** = both ends `O(1)`. **Priority queue** = best item first (heap).
- All core operations are `O(1)`.

## Patterns
- **Balanced brackets / parsing:** stack.
- **Undo/redo, DFS, call stack:** stack.
- **BFS, job queues, schedulers:** queue.
- **Monotonic stack/deque:** next greater, daily temperatures, window maximum (`O(n)`).
- **Min-stack:** store `(value, running_min)`.
- **Queue from two stacks:** amortized `O(1)`.
- **Ring buffer:** fixed array with modulo wraparound.

## Pitfalls
- `list.pop(0)` is `O(n)`; use `deque`.
- Popping or peeking an empty structure.
- Unbounded queues exhaust memory; bound them.
- Use `queue.Queue` for thread-safe blocking behavior.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Stacks](01-stacks.md) · [Queues, Deques and Priority Queues](02-queues-deques-priority-queues.md) · [Stack and Queue Applications](03-stack-and-queue-applications.md)
