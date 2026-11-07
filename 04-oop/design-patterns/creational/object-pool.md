# Object Pool Pattern

**Family:** creational (not one of the original GoF 23, but very widely used) · **How often you will use it:** occasionally, usually via a library · **Difficulty:** medium

## 1. In plain words

An **Object Pool** keeps a **fixed set of expensive objects ready to be borrowed and returned**, instead of creating and destroying them each time.

Analogy: a **bike-share station**. Buying a new bike for every trip would be silly; you borrow one, ride, and return it for the next person. If all bikes are out, you wait.

## 2. The problem

Creating some objects is slow or limited: a database connection (network handshake, authentication), a thread, a large buffer. Opening one per request wastes time and may exceed the server's limit:

```python
def handle_request():
    conn = connect_to_database()      # 50 ms and a limited resource, every single request
    ...
    conn.close()
```

## 3. The solution

```text
 borrow  ┌─────────────┐  return
Client ─►│  Pool       │◄─ Client
         │ [c1][c2][c3]│   (fixed size; blocks or fails when empty)
         └─────────────┘
```

Roles: the **pool** (holds idle objects, hands them out, takes them back), the **pooled object**, and the **client** that must always give it back.

## 4. Step by step

```python
import queue
import threading
from contextlib import contextmanager

class Connection:
    created = 0
    def __init__(self):
        Connection.created += 1
        self.id = Connection.created
    def query(self, sql):
        return f"conn{self.id}: {sql}"

class PoolExhausted(Exception):
    pass

class Pool:
    def __init__(self, size):
        self._free = queue.Queue()
        for _ in range(size):
            self._free.put(Connection())

    @contextmanager
    def acquire(self, timeout=1.0):
        try:
            conn = self._free.get(timeout=timeout)       # blocks while the pool is empty
        except queue.Empty:
            raise PoolExhausted("no connection available") from None
        try:
            yield conn
        finally:
            self._free.put(conn)                         # ALWAYS return it, even on error

pool = Pool(2)
used = []
for _ in range(5):
    with pool.acquire() as c:
        used.append(c.id)
print(used, Connection.created)       # [1, 2, 1, 2, 1] 2   (5 uses, only 2 connections ever created)

# Many threads sharing a small pool
results = []
lock = threading.Lock()
def worker(n):
    with pool.acquire(timeout=2) as c:
        with lock:
            results.append(c.query(f"SELECT {n}"))
threads = [threading.Thread(target=worker, args=(i,)) for i in range(6)]
for t in threads: t.start()
for t in threads: t.join()
print(len(results), Connection.created)   # 6 2
```

The context manager (`with pool.acquire()`) makes forgetting to return the object impossible.

### Handling exhaustion

```python
tiny = Pool(1)
with tiny.acquire():
    try:
        with tiny.acquire(timeout=0.1):
            pass
    except PoolExhausted as e:
        print("second borrower:", e)                      # second borrower: no connection available
```

## 5. The Pythonic way

You rarely write a pool yourself:

- `concurrent.futures.ThreadPoolExecutor` (a pool of threads).
- `multiprocessing.Pool` / `ProcessPoolExecutor` (a pool of processes).
- SQLAlchemy's engine pool, `psycopg_pool`, Django's persistent connections.
- `urllib3`/`requests.Session` connection pools (HTTP keep-alive).
- Use `queue.Queue`, `contextlib.contextmanager` and `try/finally` if you must build one.

## 6. When to use it (and when not to)

**Use it when** creation is slow or the resource count is limited (connections, threads, GPU contexts, large buffers).

**Skip it when** objects are cheap (Python object creation is fast), when state leakage between users is hard to prevent, or the resource has its own pooling already.

## 7. Pros and cons

| Pros | Cons |
|------|------|
| Avoids repeated creation cost | Leaked (never returned) objects starve the pool |
| Caps resource use | Objects must be "reset" so one user's state does not leak to the next |
| Smooths load spikes | More complexity: sizing, timeouts, health checks |

## 8. Related patterns

- [Singleton](singleton.md): exactly one instance; the pool is "N instances".
- [Flyweight](../structural/flyweight.md): shares *immutable* data; a pool shares *reusable stateful* objects, one user at a time.
- [Factory Method](factory-method.md): a pool often uses a factory to create its objects.

## 9. Two real-world examples

**Example 1: Database connection pooling.** A web app with 200 concurrent requests uses a pool of 10 database connections. Each request borrows one for its queries and returns it; the database only ever sees 10 connections.

**Example 2: A worker thread pool.** A server hands each incoming job to one of 8 pre-started worker threads instead of spawning a thread per job, avoiding thread-creation cost and capping CPU contention.

## 10. Common mistakes

- Not returning objects when an exception occurs (always use `try/finally` or `with`).
- Returning a broken object (closed connection) to the pool without a health check.
- Sizing the pool too small (waits) or too large (resource exhaustion).
- Sharing a pooled object between threads at the same time.

## 11. Practice

1. Add a `max_uses` limit so each pooled connection is replaced after 3 uses.
2. Add a health check: if `conn.alive` is false when returned, replace it with a new one.
3. Why is a pool of integers a bad idea in Python?

<details>
<summary>Solutions</summary>

**1.**
```python
class ReplacingPool(Pool):
    def __init__(self, size, max_uses=3):
        super().__init__(size)
        self.max_uses, self.uses = max_uses, {}
    @contextmanager
    def acquire(self, timeout=1.0):
        with super().acquire(timeout) as conn:
            yield conn
            self.uses[conn.id] = self.uses.get(conn.id, 0) + 1
rp = ReplacingPool(1)
for _ in range(2):
    with rp.acquire() as c: pass
print(rp.uses)
```
(In production you would close the old connection and put a fresh one back when the count hits `max_uses`.)

**2.**
```python
class HealthyPool(Pool):
    @contextmanager
    def acquire(self, timeout=1.0):
        conn = self._free.get(timeout=timeout)
        try:
            yield conn
        finally:
            self._free.put(conn if getattr(conn, "alive", True) else Connection())
hp = HealthyPool(1)
with hp.acquire() as c:
    c.alive = False
with hp.acquire() as c2:
    print(c2.alive if hasattr(c2, "alive") else "fresh connection")     # fresh connection
```

**3.** Creating a Python `int` is already cheap and ints are immutable, so a pool adds locking overhead and complexity for no gain; pools are for objects that are expensive to create or limited in number.

</details>

## 12. Check yourself

1. What problem does an object pool solve?
2. What must a pool always guarantee about borrowed objects?
3. Why use a context manager for `acquire`?
4. Name two standard pools in Python.

<details>
<summary>Answers</summary>

1. The cost or limit of creating expensive objects repeatedly: it reuses a bounded set.
2. That they are returned (even on errors), that exhaustion is handled (wait with timeout or fail), and that returned objects are clean and healthy.
3. It guarantees the object goes back to the pool via `finally`, so leaks cannot happen from forgotten releases.
4. `ThreadPoolExecutor` and `multiprocessing.Pool` (also connection pools in SQLAlchemy and urllib3).

</details>

## More examples

Runnable script (added to your companion repository with this lesson): [`creationalPattern/objectPoolPattern.py`](https://github.com/M-Hammad-Faisal/design-patterns-python/blob/master/creationalPattern/objectPoolPattern.py)

[Family overview](README.md) · [All patterns](../README.md)
