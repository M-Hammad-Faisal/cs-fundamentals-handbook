# Rapid-Fire Python and CS Questions

## 1. The concept

Interviewers mix coding rounds with **short conceptual questions**: "What is the GIL?", "Difference between a process and a thread?", "What happens when you type a URL?". Good answers are **short, accurate, with an example**, and show you know the trade-offs. This chapter collects the highest-frequency questions, each with a crisp answer you can say in 30-60 seconds and a link to the handbook lesson that explains it in depth.

**How to answer:** (1) one-sentence definition, (2) how it works or why it matters, (3) a tiny example or trade-off. Stop; let the interviewer ask for more.

## 2. Python language: predict the output

These puzzles come up constantly. Read each, predict, then check the printed result and the explanation.

```python
# 1. Mutable default arguments
def append_to(item, items=[]):
    items.append(item)
    return items

assert append_to(1) == [1]
assert append_to(2) == [1, 2]               # the SAME list is reused: defaults are evaluated once, at definition time

def append_safe(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items

assert append_safe(1) == [1] and append_safe(2) == [2]

# 2. Identity versus equality
a = [1, 2, 3]
b = a
c = [1, 2, 3]
assert a is b and a == c and a is not c    # b is another name for a; c is an equal but separate list

# 3. Small-int caching and interning (implementation details; never rely on `is` for values)
x, y = 256, 256
assert x == y
assert "py" + "thon" == "python"

# 4. Late-binding closures
funcs = [lambda: i for i in range(3)]
assert [f() for f in funcs] == [2, 2, 2]    # every lambda looks up i when called, after the loop ended
fixed = [lambda i=i: i for i in range(3)]
assert [f() for f in fixed] == [0, 1, 2]    # a default argument captures the current value

# 5. Shallow vs deep copy
import copy
original = [[1, 2], [3, 4]]
shallow, deep = copy.copy(original), copy.deepcopy(original)
original[0].append(99)
assert shallow[0] == [1, 2, 99] and deep[0] == [1, 2]

# 6. Tuples are immutable, but their contents may not be
t = ([1, 2], 3)
t[0].append(4)
assert t == ([1, 2, 4], 3)                  # the tuple still points to the same list object

# 7. Augmented assignment on a mutable object mutates in place
l1 = [1, 2]; l2 = l1
l1 += [3]
assert l2 == [1, 2, 3]                      # += on a list extends the same object
t1 = (1, 2); t2 = t1
t1 += (3,)
assert t2 == (1, 2) and t1 == (1, 2, 3)     # tuples are immutable: += builds a new tuple

# 8. Scope: LEGB (Local, Enclosing, Global, Built-in)
counter = 0
def bump():
    global counter
    counter += 1
bump(); bump()
assert counter == 2

def outer():
    n = 0
    def inner():
        nonlocal n
        n += 1
        return n
    return inner
inc = outer()
assert (inc(), inc()) == (1, 2)

# 9. Dictionary and set facts
d = {}
d[1] = "a"; d[1.0] = "b"; d[True] = "c"
assert d == {1: "c"} and len(d) == 1        # 1 == 1.0 == True and they hash equally, so they are the same key
assert list({"b": 1, "a": 2}) == ["b", "a"] # dicts keep insertion order (guaranteed since 3.7)
try:
    {[1, 2]: "x"}
except TypeError:
    pass                                    # lists are unhashable; keys must be hashable (immutable)

# 10. Chained comparison, truthiness, and short-circuit evaluation
assert (1 < 2 < 3) and not (1 < 3 < 2)
assert bool([]) is False and bool([0]) is True and bool("") is False and bool(" ") is True
assert (0 or "default") == "default" and (5 and 7) == 7 and (None or []) == []

# 11. Sorting is stable
people = [("ana", 30), ("bo", 25), ("cy", 30), ("di", 25)]
assert sorted(people, key=lambda p: p[1]) == [("bo", 25), ("di", 25), ("ana", 30), ("cy", 30)]   # ties keep original order

# 12. String facts
s = "hello"
assert s[::-1] == "olleh" and s[1:3] == "el" and s[-1] == "o" and "ell" in s
try:
    s[0] = "H"
except TypeError:
    pass                                    # strings are immutable
assert "".join(["a", "b"]) == "ab" and "a,b".split(",") == ["a", "b"]

# 13. Integer division, rounding and floats
assert 7 // 2 == 3 and -7 // 2 == -4 and 7 % 3 == 1 and -7 % 3 == 2     # floor division rounds toward negative infinity
assert round(2.5) == 2 and round(3.5) == 4                               # banker's rounding: ties go to even
assert 0.1 + 0.2 != 0.3
import math
assert math.isclose(0.1 + 0.2, 0.3)
from decimal import Decimal
assert Decimal("0.1") + Decimal("0.2") == Decimal("0.3")

# 14. *args and **kwargs
def f(a, b=2, *args, c, **kwargs):
    return a, b, args, c, kwargs
assert f(1, 3, 4, 5, c=6, x=7) == (1, 3, (4, 5), 6, {"x": 7})
assert [*range(3), *"ab"] == [0, 1, 2, "a", "b"] and {**{"a": 1}, "b": 2} == {"a": 1, "b": 2}

# 15. Generators are lazy and single-use
gen = (n * n for n in range(3))
assert list(gen) == [0, 1, 4] and list(gen) == []

# 16. `is None` vs `== None`, and the `in` operator costs
assert None is None
assert 3 in {1, 2, 3} and 3 in [1, 2, 3]    # set/dict lookup is O(1); list lookup is O(n)

# 17. Class vs instance attributes
class A:
    items = []                              # shared by ALL instances
    def __init__(self):
        self.mine = []
a1, a2 = A(), A()
a1.items.append(1)
assert a2.items == [1] and a2.mine == []

# 18. __eq__ without __hash__ makes a class unhashable
class P:
    def __init__(self, v): self.v = v
    def __eq__(self, other): return self.v == other.v
try:
    {P(1)}
except TypeError:
    pass

# 19. try / finally and return
def tricky():
    try:
        return "try"
    finally:
        print("cleanup runs even after return")
assert tricky() == "try"

# 20. else on loops
for i in range(3):
    if i == 5:
        break
else:
    found = False                           # the else block runs only if the loop did NOT break
assert found is False
print("all python puzzles ok")
```

## 3. Python conceptual questions (model answers)

**Q: What is the GIL and what does it mean for threads?**
The Global Interpreter Lock lets only one thread execute Python bytecode at a time in CPython. CPU-bound pure-Python code gains nothing from threads (use `multiprocessing`); I/O-bound code still benefits because the GIL is released while waiting; C extensions such as NumPy can release it too. Python 3.13+ has an optional free-threaded build. See [concurrency in Python](../../08-modern-python/async-concurrency/README.md).

**Q: Threads vs processes vs asyncio?**
Threads: shared memory, good for blocking I/O at moderate scale. Processes: separate interpreters, true CPU parallelism, costlier and need IPC. `asyncio`: one thread, cooperative tasks, ideal for very many concurrent I/O operations, but everything must be non-blocking.

**Q: How does Python manage memory?**
Reference counting frees an object immediately when its count reaches zero; a cyclic garbage collector handles reference cycles; small objects use a private allocator (`pymalloc`). Names are references, so assignment never copies. See [classes and objects](../../04-oop/classes-objects/README.md).

**Q: What is the difference between `list` and `tuple`? `list` and `set`? `dict` and `defaultdict`?**
List: mutable ordered sequence. Tuple: immutable, hashable if its items are, used for records and dictionary keys. Set: unordered unique hashable items with O(1) membership. `defaultdict(list)` creates a missing value automatically instead of raising `KeyError`.

**Q: What are decorators and how would you write one?**
A decorator is a callable that takes a function and returns a (usually wrapped) function: `@timed` means `f = timed(f)`. Use `functools.wraps`; add a third layer for arguments. See [Decorator pattern](../../04-oop/design-patterns/structural/decorator.md).

**Q: Generators vs lists? What does `yield` do?**
`yield` pauses a function and preserves its state so values are produced lazily, one at a time, using constant memory; generators are single-use iterators. See [generators](../../08-modern-python/generators-functional/README.md).

**Q: What is the MRO and how does `super()` work?**
The method resolution order is the linearized list of classes searched for an attribute (C3 linearization, `Cls.__mro__`). `super()` delegates to the next class in the MRO, enabling cooperative multiple inheritance. See [inheritance and MRO](../../04-oop/inheritance-mro/README.md).

**Q: `__new__` vs `__init__`? `__str__` vs `__repr__`?**
`__new__` creates the instance (rarely overridden: immutable types, singletons); `__init__` initializes it. `__repr__` is the unambiguous developer view; `__str__` is the friendly user view.

**Q: `@staticmethod` vs `@classmethod` vs instance method?**
Instance methods get `self`; class methods get `cls` (alternative constructors, work with subclasses); static methods get neither (namespacing a plain function).

**Q: What are `*args` and `**kwargs`?**
Collect extra positional arguments into a tuple and keyword arguments into a dict; also used to unpack when calling (`f(*items, **options)`).

**Q: What is a context manager?**
An object with `__enter__`/`__exit__` (or a `@contextmanager` generator) that guarantees setup and cleanup around a `with` block, even on exceptions.

**Q: What are dataclasses and when use them versus a normal class or `NamedTuple`?**
`@dataclass` generates `__init__`, `__repr__`, `__eq__` from annotations; use it for data-holding classes (frozen for value objects). `NamedTuple` for immutable tuple-like records; a normal class when behavior and invariants dominate. See [dataclasses](../../08-modern-python/dataclasses-enums/README.md).

**Q: How do you handle exceptions well?**
Catch specific exceptions, never a bare `except`, preserve causes with `raise ... from e`, clean up with `with`/`finally`, define a base application exception. See [exceptions](../../08-modern-python/exceptions-logging-testing/README.md).

**Q: How do type hints work at runtime?**
They do not: they are metadata for tools (mypy, IDEs) and libraries (pydantic, FastAPI). See [type hints](../../08-modern-python/typing-hints/README.md).

**Q: How would you speed up slow Python code?**
Profile first (`cProfile`); then better algorithm/data structure (set instead of list lookup), avoid repeated work (caching), use built-ins and comprehensions, reduce I/O round trips, use NumPy/vectorization or multiprocessing for CPU work. See [performance](../../08-modern-python/performance-profiling/README.md).

**Q: What is monkey patching and why be careful?**
Changing a class or module at runtime (`module.func = other`); useful in tests (`monkeypatch`), dangerous in production because it hides behavior and breaks assumptions.

**Q: What are metaclasses?**
A metaclass is the class of a class (`type` by default); it customizes class creation. Rarely needed; prefer class decorators or `__init_subclass__`.

## 4. CS fundamentals: model answers

### Operating systems
- **Process vs thread:** a process has its own address space; threads share their process's memory but have their own stack and registers. Processes isolate and are heavier; threads are lighter and need synchronization. See [processes and threads](../../06-operating-systems/processes-threads/README.md).
- **What is a deadlock and how do you prevent it?** Tasks waiting on each other forever. Needs mutual exclusion, hold-and-wait, no preemption and circular wait; break one (lock ordering is the practical fix). See [concurrency](../../06-operating-systems/concurrency-deadlocks/README.md).
- **What is virtual memory?** Each process sees a private address space; the MMU maps pages to physical frames, enabling isolation, overcommit and sharing. See [memory](../../06-operating-systems/memory-virtual-memory/README.md).
- **Context switch?** Saving one task's CPU state and loading another's; pure overhead. **Scheduling algorithms?** FCFS, SJF, Round Robin, priority, MLFQ. See [scheduling](../../06-operating-systems/scheduling/README.md).
- **Race condition vs deadlock vs starvation?** Timing-dependent wrong result; everyone blocked forever; one task never served.

### Networking
- **TCP vs UDP:** TCP is connection-oriented, reliable, ordered, congestion controlled; UDP is connectionless, lightweight, no guarantees (DNS, video, QUIC). See [the network stack](../../07-networking/tcp-ip-osi/README.md).
- **HTTP vs HTTPS, status codes (200, 301, 401, 403, 404, 500, 502, 503), methods (GET, POST, PUT, DELETE), idempotency:** see [DNS and HTTP](../../07-networking/dns-http/README.md).
- **How does HTTPS work?** TLS handshake: key exchange (ECDHE) and certificate verification, then symmetric encryption. See [TLS](../../07-networking/tls-security/README.md).
- **Load balancer, CDN, reverse proxy:** see [load balancing](../../07-networking/load-balancing-cdn/README.md).

### The classic: "What happens when you type `https://example.com` and press Enter?"

1. **Browser parses the URL** (scheme, host, path) and checks caches (HSTS list, browser cache).
2. **DNS resolution:** browser cache, OS cache, then the recursive resolver, which (on a miss) asks root, TLD (`.com`) and authoritative servers; the answer (an IP address) is cached for its TTL.
3. **TCP connection:** three-way handshake (SYN, SYN-ACK, ACK) to port 443 (or QUIC over UDP for HTTP/3).
4. **TLS handshake:** client and server agree on parameters and keys (ECDHE), the server proves identity with its certificate chain (validated against trusted CAs), then both use symmetric encryption (TLS 1.3 takes one round trip).
5. **HTTP request:** `GET / HTTP/1.1` with `Host`, cookies and headers (HTTP/2 multiplexes streams on one connection).
6. **Server side:** the request may hit a CDN edge (cache hit returns immediately), a load balancer (picks an app server), a web server and application code, which may consult a cache and a database, and returns an HTTP response (status, headers, body).
7. **Browser renders:** parses HTML into the DOM, fetches CSS/JS/images (more requests, often reusing the connection), builds the render tree, runs JavaScript, lays out and paints the page.
8. **Connections are reused** (keep-alive) and resources cached according to `Cache-Control`.

Mention latency costs (DNS + TCP + TLS round trips), caching at every layer, and what you would measure.

### Databases
- **ACID?** Atomicity (all or nothing), Consistency (constraints hold), Isolation (concurrent transactions do not interfere), Durability (committed data survives crashes). See [transactions](../../05-databases/transactions-acid/README.md).
- **Index?** A sorted structure (usually a B-tree) that speeds up lookups and range scans at the cost of slower writes and space. See [indexes](../../05-databases/indexes-query-plans/README.md).
- **Inner vs left join? `WHERE` vs `HAVING`?** Inner keeps matches only; left keeps all rows of the left table with NULLs for no match. `WHERE` filters rows before grouping; `HAVING` filters groups after aggregation. See [SQL](../../05-databases/relational-sql/README.md).
- **Normalization?** Storing each fact once (1NF, 2NF, 3NF) to avoid anomalies; denormalize deliberately for read speed. See [schema design](../../05-databases/normalization-schema-design/README.md).
- **SQL vs NoSQL; CAP theorem; sharding vs replication?** See [NoSQL](../../05-databases/nosql/README.md).
- **Isolation levels and anomalies (dirty read, non-repeatable read, phantom, lost update)?** Higher isolation prevents more anomalies at the cost of concurrency.

### Data structures and algorithms
- **Array vs linked list; hash table internals and collisions; BST vs heap; BFS vs DFS; stable sort; Big-O of common operations:** see [data structures](../../02-data-structures/hash-tables/README.md) and [sorting](../../03-algorithms/sorting/README.md).
- **Hash table:** key goes through a hash function to an index; collisions resolved by chaining or open addressing; average O(1), worst O(n); resizes when the load factor grows.
- **Quicksort vs mergesort:** quicksort average O(n log n), in place, worst O(n^2), not stable; mergesort always O(n log n), stable, O(n) extra space; Python uses Timsort (stable, adaptive).

### Object-oriented design
- **Four pillars:** encapsulation, abstraction, inheritance, polymorphism. **SOLID** in one line each. **Composition over inheritance.** **Common patterns** (Singleton, Factory, Observer, Strategy, Decorator, Adapter). See [OOP](../../04-oop/README.md) and [design patterns](../../04-oop/design-patterns/README.md).

## 5. Quick-fire pairs: "difference between X and Y"

| Pair | One-line difference |
|------|---------------------|
| `is` vs `==` | identity (same object) vs equality (same value) |
| list vs tuple | mutable vs immutable (hashable if contents are) |
| `deepcopy` vs `copy` | recursive copy vs copy of the top level only |
| `@staticmethod` vs `@classmethod` | no implicit argument vs receives the class |
| `__str__` vs `__repr__` | for users vs for developers |
| generator vs iterator | a function with `yield` (an easy way to make an iterator) vs any object with `__next__` |
| process vs thread | separate memory vs shared memory |
| concurrency vs parallelism | overlapping progress vs simultaneous execution |
| stack vs heap (memory) | automatic call frames (LIFO) vs dynamic allocation |
| stack vs queue | LIFO vs FIFO |
| array vs linked list | O(1) index, O(n) insert vs O(n) index, O(1) insert at a known node |
| hash map vs BST | O(1) average unordered vs O(log n) ordered |
| BFS vs DFS | queue, shortest path in unweighted graphs vs stack/recursion, exploring deep |
| TCP vs UDP | reliable ordered stream vs fast best-effort datagrams |
| 401 vs 403 | not authenticated vs authenticated but not allowed |
| PUT vs POST vs PATCH | replace (idempotent) vs create/action vs partial update |
| SQL vs NoSQL | relational ACID, ad hoc queries vs flexible schema, horizontal scale, access-pattern design |
| clustered vs non-clustered index | table rows stored in index order vs separate lookup structure |
| authentication vs authorization | who you are vs what you may do |
| symmetric vs asymmetric crypto | one shared key (fast) vs key pair (key exchange, signatures) |
| optimistic vs pessimistic locking | detect conflicts at commit (version check) vs lock first |
| monolith vs microservices | one deployable unit vs many independently deployable services |

## 6. Two real-world examples

### Example 1: Turning a definition into a strong answer
Question: "What is a deadlock?" A weak answer: "When two threads block each other." A strong answer: "A deadlock is when a set of threads each hold a resource and wait for one held by another, so none can proceed. It needs four conditions: mutual exclusion, hold-and-wait, no preemption and circular wait. In practice you break circular wait by always acquiring locks in a fixed global order (for example, always lock the lower account id first in a bank transfer), or use timeouts with try-lock. Databases detect cycles and abort one transaction." It defines, explains, gives a fix and a real example in about 30 seconds.

### Example 2: Using a puzzle to show depth
Asked "what does `append_to(2)` return after `append_to(1)` with a mutable default?", you answer `[1, 2]`, explain that defaults are evaluated once at function definition, show the `None` sentinel fix, and mention the same mechanism behind shared class-level lists and why dataclasses reject a bare `[]` default. One tiny question demonstrates you understand objects, scope timing and API design.

## 7. Tips, tricks and pitfalls

- **Answer the question asked**, briefly, then offer to go deeper.
- Give a **concrete example** with every definition.
- Mention **trade-offs** ("threads are lighter but share state, so you need locks").
- Admit uncertainty honestly and reason from first principles; never bluff.
- Avoid memorized textbook paragraphs; use your own words and your own experience.
- Know the **complexity** of the data structures you use daily (list, dict, set, heap, deque).
- Be ready for follow-ups: "why?", "what could go wrong?", "how would you test/measure that?".
- Link answers to **real projects** you have worked on whenever possible.
- Revise with the handbook's check-yourself questions and summaries (see the [revision schedule](../../revision/schedule.md)).

## 8. Check yourself

1. Why does `def f(x, items=[])` misbehave, and what is the fix?
2. What does the GIL prevent, and what still runs in parallel?
3. Explain `is` vs `==` with an example.
4. What are the four deadlock conditions?
5. Walk through "type a URL and press Enter" in six steps.
6. What does ACID stand for? What is an index trade-off?
7. Why does `sorted` stability matter?
8. Quicksort vs mergesort: when each?
9. Why can't you use a list as a dictionary key?

<details>
<summary>Answers</summary>

1. The default list is created once when the function is defined and shared across calls; use `None` and create the list inside the function.
2. It prevents multiple threads executing Python bytecode simultaneously; I/O waits and C extensions that release the GIL still overlap, and separate processes run in parallel.
3. `a = [1]; b = a; c = [1]`: `a is b` (same object) and `a == c` (equal values) but `a is not c`.
4. Mutual exclusion, hold and wait, no preemption, circular wait.
5. Parse URL and check caches; DNS lookup; TCP (and TLS) handshake; send HTTP request; server processes via CDN/load balancer/app/cache/database and responds; browser parses and renders, fetching more resources.
6. Atomicity, Consistency, Isolation, Durability. An index speeds reads and range scans but slows writes and uses storage.
7. Sorting by one key then another (or by a key with ties) preserves the earlier order of equal items, enabling multi-key sorts and predictable output.
8. Quicksort: in-place average O(n log n) with good constants, but worst case O(n^2) and not stable; mergesort: guaranteed O(n log n), stable, needs extra memory (good for linked lists and external sorting).
9. Lists are mutable and unhashable; dictionary keys must have a stable hash, so use a tuple or frozen type.

</details>

[Exercises](exercises.md) · [Summary](summary.md)

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

Back to the [part overview](../README.md).
