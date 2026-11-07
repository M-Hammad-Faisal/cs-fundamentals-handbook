# Race Conditions and Synchronization

**Prerequisites:** [processes and threads](../processes-threads/README.md), [what is an OS](../00-what-is-an-operating-system.md). **You will learn:** why unsynchronized threads corrupt shared data (a **race condition**), what a **critical section** is, how **locks (mutexes)**, **semaphores**, **events** and **condition variables** fix it, the classic **producer-consumer** pattern, and Python specifics (the GIL does not save you).

## 1. In plain words

Two people edit the same bank balance at the same moment: both read 100, one adds 10, the other adds 20, and each writes back its own result. One update is **lost**. The balance should be 130 but is 110 or 120. That is a **race condition**: the result depends on the unlucky timing of operations from several threads.

The root cause: `balance += 10` looks like one step, but is really **three**: **read** the value, **add**, **write** back. Another thread can slip in between.

```text
Thread A: read 100                      add 10 -> 110      write 110
Thread B:          read 100   add 20 -> 120                         write 120   <- A's update vanished
```

## 2. Reproducing a race reliably

Real races are timing dependent, which makes them hard to test. We can force the bad interleaving by yielding between the read and the write:

```python
import threading, time

balance = 100

def add_unsafe(amount):
    global balance
    current = balance                  # read
    time.sleep(0.01)                   # another thread runs here (a stand-in for "bad luck")
    balance = current + amount         # write back a stale result

threads = [threading.Thread(target=add_unsafe, args=(a,)) for a in (10, 20)]
for t in threads: t.start()
for t in threads: t.join()
print(balance)                         # 110 or 120, never the correct 130
```

You can also see lost updates with plain counters when many threads do real work, though the exact numbers differ every run and Python version:

```python
import threading

counter = 0

def bump(times):
    global counter
    for _ in range(times):
        counter += 1                   # read, add, write: NOT atomic

workers = [threading.Thread(target=bump, args=(200_000,)) for _ in range(4)]
for w in workers: w.start()
for w in workers: w.join()
print(counter <= 800_000)              # True   (and often strictly less on a free-threaded build or older Pythons)
```

(Modern CPython sometimes happens to produce the right total because of how its interpreter switches threads, and free-threaded builds make losses far more likely. **Never rely on luck**: the language does not promise `+=` is atomic.)

## 3. Critical sections and mutual exclusion

A **critical section** is code that touches shared data and must not run in two threads at once. **Mutual exclusion** means at most one thread is inside. Requirements for a good solution:

1. **Mutual exclusion**: never two threads inside together.
2. **Progress**: if nobody is inside, a waiting thread can enter (no needless waiting).
3. **Bounded waiting**: no thread waits forever (no starvation).

## 4. Locks (mutexes)

A **lock** has two operations: **acquire** (wait until free, then take it) and **release**. Only the holder may be inside the critical section.

```python
import threading, time

balance = 100
lock = threading.Lock()

def add_safe(amount):
    global balance
    with lock:                         # acquire on entry, release on exit (even if an exception happens)
        current = balance
        time.sleep(0.01)
        balance = current + amount

threads = [threading.Thread(target=add_safe, args=(a,)) for a in (10, 20)]
for t in threads: t.start()
for t in threads: t.join()
print(balance)                         # 130   (always)
```

**Always use `with lock:`** instead of manual `acquire()`/`release()`: if the code between raises an exception, a forgotten `release()` leaves the lock held forever.

Keep critical sections **short** (they serialize your program) and **never call unknown or slow code (I/O, callbacks) while holding a lock**.

A safer design: hide the lock inside the object so callers cannot forget it:

```python
class SafeCounter:
    def __init__(self):
        self._value, self._lock = 0, threading.Lock()
    def increment(self):
        with self._lock:
            self._value += 1
    @property
    def value(self):
        with self._lock:
            return self._value

c = SafeCounter()
workers = [threading.Thread(target=lambda: [c.increment() for _ in range(50_000)]) for _ in range(4)]
for w in workers: w.start()
for w in workers: w.join()
print(c.value)                         # 200000   (exactly)
```

### Reentrant locks

A plain `Lock` deadlocks if the same thread tries to acquire it twice. An **`RLock`** lets the owner re-enter (useful when a locked method calls another locked method):

```python
rlock = threading.RLock()
def outer():
    with rlock:
        inner()
def inner():
    with rlock:                        # same thread: allowed with RLock, would hang with Lock
        return "ok"
print(outer())                         # None   (outer returns nothing, but did not hang)
```

## 5. Semaphores: counting permits

A **semaphore** holds a counter of permits. `acquire` takes one (waiting at zero); `release` gives one back. It limits **how many** threads may use a resource at once, for example 3 database connections.

```python
import threading, time

pool = threading.Semaphore(3)          # at most 3 workers inside at once
inside, peak, guard = 0, 0, threading.Lock()

def worker():
    global inside, peak
    with pool:
        with guard:
            inside += 1
            peak = max(peak, inside)
        time.sleep(0.05)               # pretend to use the database
        with guard:
            inside -= 1

threads = [threading.Thread(target=worker) for _ in range(10)]
for t in threads: t.start()
for t in threads: t.join()
print(peak)                            # 3   (ten workers, never more than three at the same time)
```

A semaphore with value 1 behaves like a lock (a **binary semaphore**), but a lock must be released by its owner while a semaphore can be released by any thread, which makes semaphores good for **signaling**.

## 6. Events and condition variables: waiting for something to happen

**Event:** a flag that threads can wait on until another thread sets it.

```python
ready = threading.Event()
results = []

def waiter():
    ready.wait()                       # sleeps without burning CPU until set()
    results.append("started after the signal")

t = threading.Thread(target=waiter); t.start()
time.sleep(0.05); results.append("setting the event")
ready.set(); t.join()
print(results)                         # ['setting the event', 'started after the signal']
```

**Condition variable:** wait until *a condition about shared state* becomes true, atomically releasing the lock while sleeping. Always re-check the condition in a `while` loop (wake-ups can be spurious).

```python
cond = threading.Condition()
queue = []

def consumer(out):
    with cond:
        while not queue:               # a loop, not an if
            cond.wait()                # releases the lock and sleeps; reacquires it on wake-up
        out.append(queue.pop(0))

def producer(item):
    with cond:
        queue.append(item)
        cond.notify()                  # wake one waiting consumer

got = []
t = threading.Thread(target=consumer, args=(got,)); t.start()
time.sleep(0.05); producer("hello"); t.join()
print(got)                             # ['hello']
```

## 7. The producer-consumer problem (bounded buffer)

Producers create items, consumers use them, sharing a **fixed-size buffer**. Rules: a producer must wait when the buffer is **full**; a consumer must wait when it is **empty**; buffer access must be exclusive.

The classic semaphore solution uses three tools: `empty_slots` (starts at the capacity), `full_slots` (starts at 0) and a mutex for the buffer.

```python
import collections

class BoundedBuffer:
    def __init__(self, capacity):
        self.items = collections.deque()
        self.mutex = threading.Lock()
        self.empty_slots = threading.Semaphore(capacity)    # how many more items fit
        self.full_slots = threading.Semaphore(0)            # how many items are available

    def put(self, item):
        self.empty_slots.acquire()                          # wait for free space
        with self.mutex:
            self.items.append(item)
        self.full_slots.release()                           # announce one more item

    def get(self):
        self.full_slots.acquire()                           # wait for an item
        with self.mutex:
            item = self.items.popleft()
        self.empty_slots.release()                          # announce one more free slot
        return item

buf = BoundedBuffer(capacity=3)
consumed = []

def producer():
    for i in range(10):
        buf.put(i)
    buf.put(None)                                           # sentinel: no more work

def consumer():
    while (item := buf.get()) is not None:
        consumed.append(item * item)

p, c = threading.Thread(target=producer), threading.Thread(target=consumer)
p.start(); c.start(); p.join(); c.join()
print(consumed)                                             # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
```

Python's `queue.Queue` is a ready-made, thread-safe bounded buffer (it does all of the above internally):

```python
import queue

q = queue.Queue(maxsize=3)
done = []
def work():
    while (item := q.get()) is not None:
        done.append(item + 1)
        q.task_done()
    q.task_done()

t = threading.Thread(target=work); t.start()
for i in range(5):
    q.put(i)                           # blocks when 3 items are already waiting
q.put(None); t.join()
print(done)                            # [1, 2, 3, 4, 5]
```

## 8. Readers-writers

Many threads may **read** shared data at once, but a **writer** needs exclusive access. A simple reader-preference lock:

```python
class ReadWriteLock:
    def __init__(self):
        self._readers = 0
        self._readers_lock = threading.Lock()
        self._write_lock = threading.Lock()

    def acquire_read(self):
        with self._readers_lock:
            self._readers += 1
            if self._readers == 1:
                self._write_lock.acquire()          # the first reader blocks writers
    def release_read(self):
        with self._readers_lock:
            self._readers -= 1
            if self._readers == 0:
                self._write_lock.release()          # the last reader lets writers in
    def acquire_write(self):
        self._write_lock.acquire()
    def release_write(self):
        self._write_lock.release()

rw = ReadWriteLock()
rw.acquire_read(); rw.acquire_read()                # two readers at once is fine
print(rw._write_lock.locked())                      # True   (writers are kept out while readers are inside)
rw.release_read(); rw.release_read()
print(rw._write_lock.locked())                      # False
```

(This version can starve writers if readers keep arriving; production implementations add fairness rules.)

## 9. Python specifics: the GIL does not make your code thread-safe

CPython's **global interpreter lock (GIL)** lets one thread execute Python bytecode at a time, which protects the interpreter's internals, **not your logic**. A thread can be switched out between any two bytecode instructions, including between the read and the write of `x += 1`.

```python
import dis
def inc():
    global counter
    counter += 1
dis.dis(inc)       # shows LOAD_GLOBAL, a constant load, BINARY_OP, STORE_GLOBAL (names vary by version): several steps, so a switch can land between them
```

Guidance:

- Protect shared mutable state with locks or hand work through a `queue.Queue`.
- Prefer **sharing nothing**: give each thread its own data, return results through a queue or `Future`.
- CPU-bound work: use processes (`multiprocessing`, `ProcessPoolExecutor`) for real parallelism; I/O-bound: threads or `asyncio`.
- Free-threaded Python builds (no GIL) make unsynchronized code fail more often, so correct locking matters even more.

## 10. Beyond locks: atomics and lock-free ideas

Hardware offers **atomic** instructions such as compare-and-swap (CAS): "set to new only if it still equals old". Lock-free data structures are built on CAS. Python does not expose raw atomics, but the idea shows up as **optimistic concurrency** in databases: read a version number, do the work, and write only if the version is unchanged (retry otherwise).

```python
class VersionedValue:
    def __init__(self, value):
        self.value, self.version, self._lock = value, 0, threading.Lock()

    def compare_and_set(self, expected_version, new_value):
        with self._lock:                            # this tiny lock plays the role of the CPU's atomic instruction
            if self.version != expected_version:
                return False                        # someone else changed it: caller must retry
            self.value, self.version = new_value, self.version + 1
            return True

v = VersionedValue(100)
snapshot_a, snapshot_b = v.version, v.version       # two clients read the same version
print(v.compare_and_set(snapshot_a, 110), v.compare_and_set(snapshot_b, 120))     # True False   (the second must re-read and retry)
```

## 11. Two real-world examples

**Example 1: Ticket booking.** Two users click the last seat simultaneously. Without a lock or an atomic `UPDATE ... WHERE seats > 0`, both succeed and the show is oversold. The fix is either a lock around check-and-update or a single atomic database statement.

**Example 2: Logging and metrics.** Many threads write to one log file or counter. A `queue.Queue` plus one dedicated writer thread (the logging module's `QueueHandler` works this way) avoids interleaved garbage and contention.

## 12. Common mistakes

- Assuming `x += 1`, `list.append` chains, or "check then act" sequences are atomic.
- Forgetting to lock **all** accesses (readers too) to the shared data.
- Holding a lock while doing slow I/O (everything serializes).
- Using `if` instead of `while` around `cond.wait()`.
- Manual `acquire()` without `try/finally` (use `with`).
- Locking at the wrong granularity: one giant lock (no parallelism) or hundreds of tiny ones (bugs and deadlock risk; see [deadlock](02-deadlock.md)).

## 13. Practice

1. Why does `counter += 1` race? List the steps.
2. Fix this bank-transfer bug: two threads call `transfer(a, b, 50)` on the same accounts and the totals drift.
3. A semaphore starts at 2 and five threads call `acquire()`. How many proceed? What happens when one releases?
4. When would you use an `Event` instead of a `Lock`?
5. Why must `cond.wait()` be inside a `while` loop?
6. Rewrite the unsafe counter so each thread counts locally and the totals are added at the end (no lock in the hot loop).
7. Why can the GIL not protect `if balance >= amount: balance -= amount`?

<details>
<summary>Solutions</summary>

1. Read the value, add 1, write the result; another thread can run between those steps, so one update overwrites the other.
2. Make the check-and-update atomic with a lock:
   ```python
   class Account:
       def __init__(self, balance): self.balance, self.lock = balance, threading.Lock()

   def transfer(src, dst, amount):
       with src.lock:
           if src.balance < amount:
               return False
           src.balance -= amount
       with dst.lock:
           dst.balance += amount
       return True

   a, b = Account(100), Account(0)
   ts = [threading.Thread(target=transfer, args=(a, b, 50)) for _ in range(4)]
   for t in ts: t.start()
   for t in ts: t.join()
   print(a.balance, b.balance, a.balance + b.balance)      # 0 100 100   (money is conserved)
   ```
   (Locking two accounts at once needs a consistent order to avoid deadlock; see the next lesson.)
3. Two proceed immediately; the other three block. When one releases, one waiting thread proceeds.
4. To make threads wait for a one-time or repeatable signal ("data loaded", "shutdown requested"), not to protect data.
5. Wake-ups can be spurious, and another thread may consume the item first, so the condition must be re-checked after waking.
6. ```python
   def count_local(times, out, i):
       local = 0
       for _ in range(times):
           local += 1
       out[i] = local
   out = [0] * 4
   ts = [threading.Thread(target=count_local, args=(100_000, out, i)) for i in range(4)]
   for t in ts: t.start()
   for t in ts: t.join()
   print(sum(out))                                         # 400000
   ```
7. The thread can be switched out between the `if` test and the subtraction; another thread may withdraw in between, leaving a negative balance. The check and the update must be one critical section.

</details>

## 14. Check yourself

1. What is a race condition?
2. What are the three requirements of a mutual exclusion solution?
3. How does a semaphore differ from a lock?
4. What problem does the bounded buffer solve and with which tools?
5. Why is `with lock:` preferred over `acquire()`/`release()`?
6. Does the GIL make Python threads safe?

<details>
<summary>Answers</summary>

1. A bug where the outcome depends on the timing of threads accessing shared data.
2. Mutual exclusion, progress, bounded waiting.
3. A semaphore counts permits (limiting concurrency to `n`) and any thread can release it; a lock admits one owner who must release it.
4. Producers and consumers sharing a fixed-size buffer; solved with two counting semaphores (empty and full slots) and a mutex (or `queue.Queue`).
5. It releases automatically even if an exception occurs.
6. No: it protects the interpreter, not your multi-step logic; you still need locks for shared mutable state.

</details>

[Back to concurrency](README.md) · Next: [deadlock](02-deadlock.md)
