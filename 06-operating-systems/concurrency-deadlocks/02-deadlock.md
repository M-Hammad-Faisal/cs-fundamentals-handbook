# Deadlock: Detection, Prevention and Avoidance

**Prerequisites:** [race conditions and synchronization](01-race-conditions-and-synchronization.md), [graph cycles](../../02-data-structures/graphs/01-graph-basics-bfs-dfs.md). **You will learn:** what a **deadlock** is, the **four necessary conditions**, how to reproduce one safely, how to **detect** it (cycle in a wait-for graph), **prevent** it (lock ordering), **avoid** it (**Banker's algorithm**), the **dining philosophers** problem, and related hazards (**livelock, starvation, priority inversion**).

## 1. In plain words

Two cars meet on a one-lane bridge from opposite sides. Neither can move until the other backs up, and neither will. **Deadlock** is the same standoff in software: each of a group of threads holds something and waits for something another thread in the group holds, so **none can ever proceed**.

```text
Thread A: holds lock 1, waits for lock 2
Thread B: holds lock 2, waits for lock 1       <- circular wait: both stuck forever
```

## 2. The four necessary conditions (Coffman conditions)

A deadlock can occur **only if all four hold at once**. Break any one and deadlock is impossible.

| # | Condition | Meaning | How to break it |
|---|-----------|---------|-----------------|
| 1 | **Mutual exclusion** | a resource is held by at most one thread | make resources shareable (read-only data) |
| 2 | **Hold and wait** | a thread holds resources while waiting for more | acquire everything at once, or release before waiting |
| 3 | **No preemption** | resources cannot be forcibly taken away | use timeouts / try-locks and back off |
| 4 | **Circular wait** | a cycle of threads each waiting on the next | impose a global **lock ordering** |

## 3. Reproducing a deadlock safely

We use timeouts so the demo ends instead of hanging forever:

```python
import threading, time

lock_a, lock_b = threading.Lock(), threading.Lock()
outcome = {}

def worker(name, first, second):
    with first:
        time.sleep(0.1)                                   # make sure both threads hold their first lock
        got = second.acquire(timeout=0.5)                 # a real deadlock would wait forever here
        outcome[name] = "got both locks" if got else "DEADLOCK: could not get the second lock"
        if got:
            second.release()

t1 = threading.Thread(target=worker, args=("T1", lock_a, lock_b))
t2 = threading.Thread(target=worker, args=("T2", lock_b, lock_a))        # opposite order: the classic mistake
t1.start(); t2.start(); t1.join(); t2.join()
print(outcome)
# {'T2': 'DEADLOCK: could not get the second lock', 'T1': 'DEADLOCK: could not get the second lock'}   (key order may vary)
```

(Never write production code that waits forever on a second lock after taking a first; the timeout here is for the demonstration.)

## 4. Prevention 1: lock ordering (break circular wait)

Give every lock a fixed rank and **always acquire in increasing order**. A cycle then cannot form, since it would need some thread to go from a higher rank to a lower one.

```python
def worker_ordered(name, x, y):
    first, second = sorted((x, y), key=id)                # one consistent global order (here: by object id)
    with first:
        time.sleep(0.1)
        with second:
            outcome[name] = "got both locks"

outcome = {}
t1 = threading.Thread(target=worker_ordered, args=("T1", lock_a, lock_b))
t2 = threading.Thread(target=worker_ordered, args=("T2", lock_b, lock_a))   # callers pass them in opposite orders
t1.start(); t2.start(); t1.join(); t2.join()
print(outcome)                                            # {'T1': 'got both locks', 'T2': 'got both locks'}
```

The bank-transfer version: lock the two accounts **in account-id order** regardless of the transfer direction:

```python
class Account:
    def __init__(self, ident, balance):
        self.id, self.balance, self.lock = ident, balance, threading.Lock()

def transfer(src, dst, amount):
    first, second = sorted((src, dst), key=lambda a: a.id)
    with first.lock, second.lock:
        if src.balance < amount:
            return False
        src.balance -= amount
        dst.balance += amount
        return True

a, b = Account(1, 1000), Account(2, 1000)
jobs = [threading.Thread(target=transfer, args=(a, b, 1)) for _ in range(500)] + \
       [threading.Thread(target=transfer, args=(b, a, 1)) for _ in range(500)]
for j in jobs: j.start()
for j in jobs: j.join()
print(a.balance + b.balance)                              # 2000   (no deadlock, and no money created or lost)
```

## 5. Prevention 2: try-lock with back-off (break no-preemption / hold-and-wait)

Take the first lock, **try** the second without waiting; if it is busy, release everything and retry after a random pause.

```python
import random

def acquire_both(first, second, attempts=100):
    for _ in range(attempts):
        first.acquire()
        if second.acquire(blocking=False):
            return True                                   # got both
        first.release()                                   # could not get the second: give the first back
        time.sleep(random.uniform(0, 0.001))              # random back-off avoids repeating the same collision
    return False

done = []
def careful(name, x, y):
    if acquire_both(x, y):
        done.append(name)
        y.release(); x.release()

t1 = threading.Thread(target=careful, args=("T1", lock_a, lock_b))
t2 = threading.Thread(target=careful, args=("T2", lock_b, lock_a))
t1.start(); t2.start(); t1.join(); t2.join()
print(sorted(done))                                       # ['T1', 'T2']
```

Danger: if both threads back off in lock-step forever, you have a **livelock** (they keep moving but make no progress). Random delays make that vanishingly unlikely.

## 6. Detection: find the cycle

Build a **wait-for graph**: a vertex per thread, an edge `A -> B` if `A` waits for something `B` holds. **A cycle means deadlock.** (Databases do exactly this and abort one victim transaction.)

```python
def find_deadlock(wait_for):
    """wait_for: {thread: [threads it is waiting on]}. Return one cycle or None."""
    state, stack = {}, []
    def dfs(node):
        state[node] = "visiting"; stack.append(node)
        for nxt in wait_for.get(node, []):
            if state.get(nxt) == "visiting":
                return stack[stack.index(nxt):] + [nxt]           # found a back edge: the cycle
            if nxt not in state:
                cycle = dfs(nxt)
                if cycle:
                    return cycle
        stack.pop(); state[node] = "done"
        return None
    for node in list(wait_for):
        if node not in state:
            cycle = dfs(node)
            if cycle:
                return cycle
    return None

print(find_deadlock({"T1": ["T2"], "T2": ["T3"], "T3": ["T1"], "T4": ["T1"]}))     # ['T1', 'T2', 'T3', 'T1']
print(find_deadlock({"T1": ["T2"], "T2": ["T3"], "T3": []}))                       # None
```

**Recovery** options after detecting a deadlock: kill one participant (the cheapest victim), roll back a transaction, or preempt a resource. Many systems simply **detect and restart**; the Linux kernel's `lockdep` finds *potential* lock-order cycles during development, and Python/Java can dump all thread stacks (`faulthandler.dump_traceback`, `jstack`) so you can see who waits on whom.

```python
import faulthandler, sys
faulthandler.dump_traceback(file=sys.stderr, all_threads=True)    # a snapshot of what every thread is doing (great for hangs)
```

## 7. Avoidance: Banker's algorithm

Instead of preventing a condition, the OS can **refuse to enter an unsafe state**. A state is **safe** if there exists some order in which every process can obtain its remaining maximum need and finish. The OS grants a request only if the resulting state is still safe.

Name comes from banking: a banker never lends so much that it cannot satisfy every customer's maximum credit line in some order.

Data for `n` processes and `m` resource types:

- `available[j]`: free units of resource `j`.
- `max_need[i][j]`: the most process `i` may ever request.
- `allocation[i][j]`: what `i` holds now.
- `need[i][j] = max_need - allocation`.

**Safety check:** repeatedly find a process whose `need <= available`; pretend it runs to completion and returns its allocation; if all can finish, the state is safe.

```python
def is_safe(available, max_need, allocation):
    n, m = len(allocation), len(available)
    need = [[max_need[i][j] - allocation[i][j] for j in range(m)] for i in range(n)]
    work, finished, order = available[:], [False] * n, []
    progress = True
    while progress:
        progress = False
        for i in range(n):
            if not finished[i] and all(need[i][j] <= work[j] for j in range(m)):
                work = [work[j] + allocation[i][j] for j in range(m)]     # i finishes and returns everything
                finished[i] = True
                order.append(i)
                progress = True
    return (True, order) if all(finished) else (False, order)

def request(pid, req, available, max_need, allocation):
    need = [max_need[pid][j] - allocation[pid][j] for j in range(len(req))]
    if any(req[j] > need[j] for j in range(len(req))):
        return "denied: exceeds the process's declared maximum"
    if any(req[j] > available[j] for j in range(len(req))):
        return "wait: not enough resources available right now"
    new_available = [available[j] - req[j] for j in range(len(req))]       # pretend to grant it
    new_alloc = [row[:] for row in allocation]
    new_alloc[pid] = [new_alloc[pid][j] + req[j] for j in range(len(req))]
    safe, order = is_safe(new_available, max_need, new_alloc)
    return f"granted (safe sequence {['P' + str(i) for i in order]})" if safe else "denied: would lead to an unsafe state"

available = [3, 3, 2]                                            # three resource types: A, B, C
max_need = [[7, 5, 3], [3, 2, 2], [9, 0, 2], [2, 2, 2], [4, 3, 3]]
allocation = [[0, 1, 0], [2, 0, 0], [3, 0, 2], [2, 1, 1], [0, 0, 2]]

safe, order = is_safe(available, max_need, allocation)
print(safe, ["P" + str(i) for i in order])                       # True ['P1', 'P3', 'P4', 'P0', 'P2']
print(request(1, [1, 0, 2], available, max_need, allocation))    # granted (safe sequence ['P1', 'P3', 'P4', 'P0', 'P2'])

# After granting P1's request the system state really changes: available becomes [2, 3, 0] and P1 holds [3, 0, 2].
available2 = [2, 3, 0]
allocation2 = [row[:] for row in allocation]
allocation2[1] = [3, 0, 2]
print(request(4, [3, 3, 0], available2, max_need, allocation2))  # wait: not enough resources available right now
print(request(0, [0, 2, 0], available2, max_need, allocation2))  # denied: would lead to an unsafe state
```

Reading the last line: in the updated state process 0 asks for 2 units of B, which are available, but granting them would leave no process able to finish, so the banker says no even though resources exist. (Process 4's request for 3 units of A cannot be met at all right now, so it simply waits.) That is the difference between a **safe** state (a guarantee exists) and merely having free resources.

**Limits:** the algorithm needs every process's maximum need in advance and a fixed process set, and costs `O(m n²)` per request; so general-purpose OSes rarely use it. It is mostly a teaching tool and used in specialized systems. Most real systems rely on **prevention by lock ordering** plus **timeouts and detection**.

## 8. The dining philosophers

Five philosophers sit at a round table with one fork between each pair. To eat, a philosopher needs **both adjacent forks**. If every philosopher picks up their left fork at the same moment, everyone waits for the right fork: deadlock. It is the standard puzzle for these ideas.

```python
import threading, time

def dine(philosophers=5, meals=3, ordered=True):
    forks = [threading.Lock() for _ in range(philosophers)]
    eaten = [0] * philosophers

    def philosopher(i):
        left, right = i, (i + 1) % philosophers
        first, second = (min(left, right), max(left, right)) if ordered else (left, right)    # ordered = break circular wait
        for _ in range(meals):
            with forks[first]:
                time.sleep(0.001)                         # makes the unordered version deadlock almost surely
                if not ordered:
                    if not forks[second].acquire(timeout=0.3):
                        return                            # give up (the demonstration of deadlock)
                    forks[second].release()
                else:
                    with forks[second]:
                        pass
            eaten[i] += 1

    threads = [threading.Thread(target=philosopher, args=(i,)) for i in range(philosophers)]
    for t in threads: t.start()
    for t in threads: t.join()
    return eaten

print(dine(ordered=True))                                  # [3, 3, 3, 3, 3]    everyone finishes all meals
print(sum(dine(ordered=False)) < 15)                       # True               naive left-then-right gets stuck
```

Solutions in the literature: **lock ordering** (as above: the last philosopher picks up the right fork first), **allow at most 4 at the table** (a semaphore of 4), or a **waiter** who grants both forks atomically.

## 9. Related hazards

| Hazard | What happens | Typical fix |
|--------|--------------|-------------|
| **Livelock** | threads keep reacting to each other and make no progress (two people sidestepping in a corridor) | randomized back-off, a tie-breaker |
| **Starvation** | a thread never gets the resource because others always go first | fairness, aging, FIFO lock queues |
| **Priority inversion** | a high-priority task waits for a lock held by a low-priority task that a medium task keeps preempting | **priority inheritance** (the low task temporarily inherits high priority) |

Priority inversion famously hung the **Mars Pathfinder** probe in 1997: a low-priority meteorological task held a shared bus lock, a medium task starved it, and the high-priority bus manager timed out repeatedly and reset the computer. The fix, uploaded from Earth, enabled priority inheritance on that lock.

## 10. Practical rules for avoiding deadlock in your code

1. **Prefer not to hold more than one lock at a time.**
2. When you must, acquire them in a **global fixed order** and document it.
3. Do **not** call unknown code (callbacks, user hooks, I/O) while holding a lock.
4. Use **timeouts** on lock acquisition and treat a timeout as a bug to log, not to ignore.
5. Prefer higher-level tools: queues, thread pools, immutable data, message passing, `asyncio`. Fewer locks, fewer deadlocks.
6. In databases, keep transactions short, touch rows in a consistent order, and retry on deadlock errors (the database aborts one victim for you).

## 11. Two real-world examples

**Example 1: Database deadlocks.** Transaction 1 updates row A then B while transaction 2 updates B then A. PostgreSQL and MySQL detect the cycle within about a second, abort one transaction with a "deadlock detected" error, and your code should simply retry it.

**Example 2: Thread pools waiting on themselves.** A task running in a pool of 4 workers submits a subtask to the same pool and blocks for its result. If all 4 workers do this at once, no worker is free to run the subtasks: a deadlock with no locks involved at all. Fix: do not block a pool thread on work from the same pool; use a separate pool or `async` composition.

## 12. Common mistakes

- Acquiring locks in different orders in different functions.
- Calling a method that takes a lock while already holding another lock (hidden nested locking).
- Ignoring a lock timeout instead of investigating it.
- Using the Banker's algorithm where maximum needs are unknowable.
- Confusing deadlock (nobody progresses, blocked) with livelock (everyone busy, no progress) or starvation (some never progress).
- Swallowing the "deadlock detected" error from a database instead of retrying the transaction.

## 13. Practice

1. List the four Coffman conditions, and say which one lock ordering breaks.
2. Two threads each need locks A and B. Draw the wait-for graph in the deadlock case.
3. Is a state with `available = [0]`, one process holding 1 and needing 1 more (max 2), safe? Use `is_safe`.
4. Does a cycle in a resource graph with **single-instance** resources always mean deadlock? And with multiple instances?
5. Why is the "at most 4 philosophers sit" fix correct?
6. Write a function `acquire_in_order(*locks)` as a context manager that sorts locks by `id` and acquires them.
7. Describe priority inversion and its fix in two sentences.

<details>
<summary>Solutions</summary>

1. Mutual exclusion, hold and wait, no preemption, circular wait. Lock ordering breaks circular wait.
2. `T1 -> T2` (T1 waits for the lock T2 holds) and `T2 -> T1`: a two-node cycle.
   ```python
   print(find_deadlock({"T1": ["T2"], "T2": ["T1"]}))      # ['T1', 'T2', 'T1']
   ```
3. Unsafe: nothing is available, and the only process cannot finish without one more unit.
   ```python
   print(is_safe([0], [[2]], [[1]]))                       # (False, [])
   ```
4. With single-instance resources, yes: a cycle means deadlock. With multiple instances, a cycle is necessary but not sufficient (another process might release a spare instance).
5. With at most 4 seated, at least one philosopher can always obtain two forks (pigeonhole: 4 philosophers, 5 forks), so someone finishes and releases forks.
6. ```python
   from contextlib import contextmanager, ExitStack

   @contextmanager
   def acquire_in_order(*locks):
       with ExitStack() as stack:
           for lock in sorted(locks, key=id):
               stack.enter_context(lock)
           yield

   with acquire_in_order(lock_b, lock_a):
       print("holding both")                               # holding both
   ```
7. A high-priority task waits for a lock held by a low-priority task, which a medium-priority task keeps preempting, so the high-priority task is effectively blocked by a lower one. Priority inheritance lets the lock holder temporarily run at the waiter's priority so it can finish and release the lock.

</details>

## 14. Check yourself

1. What is a deadlock?
2. Which four conditions are necessary?
3. How does lock ordering prevent deadlock?
4. What is a safe state in the Banker's algorithm?
5. What is the difference between deadlock, livelock and starvation?
6. How do databases handle deadlocks?

<details>
<summary>Answers</summary>

1. A set of threads each waiting for a resource held by another in the set, so none can proceed.
2. Mutual exclusion, hold and wait, no preemption, circular wait.
3. It makes a cycle of waits impossible, so circular wait cannot occur.
4. A state from which some ordering lets every process obtain its remaining maximum need and finish.
5. Deadlock: all blocked. Livelock: all active but making no progress. Starvation: some thread never gets served while others progress.
6. They detect cycles in the wait-for graph, abort one transaction as the victim, and the application retries it.

</details>

[Back to concurrency](README.md) · Previous: [race conditions and synchronization](01-race-conditions-and-synchronization.md)
