# Concurrency, Synchronization and Deadlocks: One-Page Summary

- **Concurrency** = overlapping tasks; **parallelism** = simultaneous execution. Shared mutable state is the hazard.
- **Race condition:** outcome depends on timing (`+=` is read, add, write). Fix with a **critical section** (lock) or by not sharing.
- **Tools:** Lock, RLock, Semaphore (N permits), Condition (wait for a predicate, always in a loop), Event, Barrier, **Queue** (best default), read-write lock.
- **Producer/consumer:** bounded queue gives back-pressure; sentinels stop workers.
- **Deadlock** needs all four: mutual exclusion, hold and wait, no preemption, circular wait. Prevent by **global lock ordering**, try-lock with timeouts, or acquiring everything at once.
- **Livelock** = active but no progress; **starvation** = never served; **priority inversion** = fix with inheritance.
- **Models:** threads+locks, message passing, event loop (`asyncio`), processes, actors.
- **Pitfalls:** lock held across I/O, check-then-act, forgetting `with`, shared state across `await`, daemon threads.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Race Conditions and Synchronization](01-race-conditions-and-synchronization.md) · [Deadlock](02-deadlock.md)
