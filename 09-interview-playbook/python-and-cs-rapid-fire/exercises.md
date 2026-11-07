# Rapid-Fire Questions: Exercises

## A. Predict the output (then run it)

1.
```python
# skip
def f(n, acc=[]):
    acc.append(n)
    return len(acc)
print(f(1), f(2), f(3))
```
2.
```python
# skip
a = [1, 2, 3]
b = a[:]
b.append(4)
c = a
c.append(5)
print(a, b, c)
```
3.
```python
# skip
x = 10
def g():
    print(x)
    x = 20
g()
```
4.
```python
# skip
print([i * j for i in range(3) for j in range(i)])
```
5.
```python
# skip
d = {"a": 1}
for k in d:
    d[k + "x"] = 0
```
6.
```python
# skip
print(sorted(["b", "a", "C", "B"]), sorted(["b", "a", "C", "B"], key=str.lower))
```
7.
```python
# skip
class A:
    def hello(self): return "A"
class B(A):
    def hello(self): return "B" + super().hello()
class C(A):
    def hello(self): return "C" + super().hello()
class D(B, C):
    pass
print(D().hello())
```
8.
```python
# skip
print(any([]), all([]), sum([]), max([], default="none"))
```
9.
```python
# skip
t = (1, [2, 3])
t[1] += [4]
```
10.
```python
# skip
import copy
a = {"k": [1]}
b = dict(a)
c = copy.deepcopy(a)
a["k"].append(2)
print(b, c)
```

## B. Answer out loud in under 45 seconds (compare with the model answers)

11. What is the difference between a process and a thread? When would you pick each in Python?
12. Explain how a hash map works and what happens on a collision.
13. What is the difference between an inner join and a left join? Give a query.
14. What is idempotency and why does it matter for HTTP and payments?
15. Explain the CAP theorem with one example of a CP and one of an AP choice.
16. What is a race condition? Show a fix.
17. What is Big-O of: dict lookup, list append, list insert at index 0, sorting, binary search, `x in list`, `x in set`?
18. Describe three ways to make a slow API endpoint faster.

<details>
<summary>Solutions</summary>

**1.** Prints `1 2 3`: the same default list persists across calls.
```python
def f(n, acc=[]):
    acc.append(n)
    return len(acc)
assert (f(1), f(2), f(3)) == (1, 2, 3)
```

**2.** `[1, 2, 3, 5] [1, 2, 3, 4] [1, 2, 3, 5]`: `b` is a copy; `c` is another name for `a`.
```python
a = [1, 2, 3]; b = a[:]; b.append(4); c = a; c.append(5)
assert (a, b, c) == ([1, 2, 3, 5], [1, 2, 3, 4], [1, 2, 3, 5])
```

**3.** `UnboundLocalError`: assigning to `x` anywhere in `g` makes it local for the whole function, so `print(x)` runs before the local exists.
```python
x = 10
def g():
    print(x)
    x = 20
try:
    g()
except UnboundLocalError:
    pass
```

**4.** `[0, 0, 2]`: the loops produce pairs `(i, j)` with `j < i`: `(1,0) -> 0`, `(2,0) -> 0`, `(2,1) -> 2`, so `[0, 0, 2]`.
```python
assert [i * j for i in range(3) for j in range(i)] == [0, 0, 2]
```

**5.** `RuntimeError: dictionary changed size during iteration`: never add or remove keys while iterating a dict (iterate over `list(d)`).
```python
d = {"a": 1}
try:
    for k in d:
        d[k + "x"] = 0
except RuntimeError:
    pass
```

**6.** `['B', 'C', 'a', 'b'] ['a', 'b', 'B', 'C']`: uppercase sorts before lowercase in Unicode order; `key=str.lower` is case-insensitive, and the sort is stable (`'b'` stays before `'B'`).
```python
assert sorted(["b", "a", "C", "B"]) == ["B", "C", "a", "b"]
assert sorted(["b", "a", "C", "B"], key=str.lower) == ["a", "b", "B", "C"]
```

**7.** `BCA`: the MRO is `D, B, C, A, object`, so `B.hello` calls `super()` which is `C`, which calls `A`.
```python
class A:
    def hello(self): return "A"
class B(A):
    def hello(self): return "B" + super().hello()
class C(A):
    def hello(self): return "C" + super().hello()
class D(B, C): pass
assert D().hello() == "BCA"
```

**8.** `False True 0 none`: `any` of nothing is False, `all` of nothing is True (vacuous truth), `sum([])` is 0, and `max` with `default`.
```python
assert (any([]), all([]), sum([]), max([], default="none")) == (False, True, 0, "none")
```

**9.** `TypeError` **and** the list is mutated: `t[1] += [4]` first extends the list in place, then tries to assign the result back into the immutable tuple, which fails.
```python
t = (1, [2, 3])
try:
    t[1] += [4]
except TypeError:
    pass
assert t == (1, [2, 3, 4])
```

**10.** `{'k': [1, 2]} {'k': [1]}`: `dict(a)` is a shallow copy (shares the list); `deepcopy` duplicates it.
```python
import copy
a = {"k": [1]}; b = dict(a); c = copy.deepcopy(a); a["k"].append(2)
assert b == {"k": [1, 2]} and c == {"k": [1]}
```

**11.** A process has its own address space and resources (isolation, true parallelism, heavier, IPC needed); threads share a process's memory (lighter, fast communication, need locks, one crash can take down the process). In Python, use **threads** (or asyncio) for I/O-bound work and **processes** for CPU-bound work because of the GIL.

**12.** A hash function maps the key to a bucket index; lookups jump straight to the bucket (average O(1)). Different keys can map to the same bucket (collision): chaining stores a small list per bucket; open addressing probes for the next free slot. When the load factor gets high the table is resized and rehashed. Worst case is O(n) if everything collides.

**13.** An inner join returns only rows with a match in both tables; a left join returns every row from the left table and fills the right side with NULLs where there is no match.
```sql
SELECT c.name, o.total FROM customers c LEFT JOIN orders o ON o.customer_id = c.id;   -- includes customers with no orders
```

**14.** An operation is idempotent if repeating it has the same effect as doing it once (`PUT`, `DELETE`, `GET`). Networks fail and clients retry, so non-idempotent operations such as charging a card need an **idempotency key** so a retried request is applied once.

**15.** CAP: during a network partition a system must choose consistency (refuse some requests to avoid stale/conflicting data) or availability (keep answering, possibly with stale data). A bank transfer service chooses CP (refuse rather than risk a wrong balance); a shopping cart or social feed can choose AP (merge and reconcile later).

**16.** A race condition is a bug where the result depends on the timing of concurrent operations (two threads read, increment and write a counter and lose an update). Fix with a lock around the critical section, atomic operations, a queue, or by not sharing mutable state.

**17.** dict lookup O(1) average; list append O(1) amortized; list insert at 0 O(n); sorting O(n log n); binary search O(log n); `x in list` O(n); `x in set` O(1) average.

**18.** Cache responses/queries (Redis, HTTP caching); fix the database access (indexes, avoid N+1 queries, pagination, select only needed columns); do heavy work asynchronously (queue) and return quickly; reduce payload size (compression, fields); use a CDN; profile first to find the real bottleneck.

</details>

[Lesson](README.md) · [Summary](summary.md)
