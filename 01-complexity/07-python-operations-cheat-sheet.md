# Complexity of Python's Built-in Operations

**Prerequisites:** [Big-O, Omega and Theta](03-big-o-omega-theta.md). **You will learn:** the time complexity of every common operation on `list`, `tuple`, `dict`, `set`, `str`, `deque`, `heapq` and `bisect`, **why** each costs what it does, the hidden-cost traps that turn loops quadratic, and how to **prove** a cost by measuring it.

## 1. In plain words

You rarely implement lists and dictionaries yourself; you *use* them. To predict a program's speed you need to know what each built-in operation costs. Python's containers are implemented in C with specific designs (a list is a **dynamic array**, a dict and a set are **hash tables**, a string is an **immutable array of characters**, a deque is a **doubly linked list of blocks**). Knowing the design tells you the cost.

Notation: `n` = size of the container, `k` = size of the other argument or slice. "Avg" = average case (hash tables are `O(n)` in the worst case when many keys collide, which is rare).

## 2. `list` (a dynamic array)

```text
 index:   0    1    2    3    4    (contiguous memory of pointers; spare capacity at the end)
        [ a ][ b ][ c ][ d ][ e ] [   ][   ]
```

| Operation | Cost | Why |
|-----------|------|-----|
| `a[i]`, `a[i] = x` | `O(1)` | direct address calculation |
| `len(a)` | `O(1)` | the size is stored |
| `a.append(x)` | `O(1)` amortized | spare capacity at the end; occasional resize ([amortized](06-cases-and-amortized-analysis.md)) |
| `a.pop()` (last) | `O(1)` | nothing shifts |
| `a.pop(0)` / `a.pop(i)` | `O(n)` | every later item shifts left |
| `a.insert(0, x)` / `a.insert(i, x)` | `O(n)` | every later item shifts right |
| `x in a`, `a.index(x)`, `a.count(x)`, `a.remove(x)` | `O(n)` | scans the list (compares one by one) |
| `a[i:j]` (slice) | `O(j - i)` | copies those items |
| `a + b`, `a * k` | `O(n + m)`, `O(n·k)` | builds a new list |
| `a.extend(b)` | `O(m)` | appends each item of `b` |
| `a.sort()`, `sorted(a)` | `O(n log n)` (best `O(n)` if nearly sorted) | Timsort |
| `min(a)`, `max(a)`, `sum(a)` | `O(n)` | one pass |
| `a.reverse()` | `O(n)` | |
| `a == b` | `O(min(n, m))` | compares until a difference |
| `list(iterable)` | `O(n)` | |
| `a.copy()`, `a[:]` | `O(n)` | |
| `del a[i]` | `O(n)` | shifts |
| `for x in a` | `O(n)` | |

### Proof by measurement

```python
import time
from timeit import timeit

# 1. Indexing is O(1): the time does not depend on the list size
small, big = list(range(1_000)), list(range(1_000_000))
t_small = timeit("a[500]", globals={"a": small}, number=200_000)
t_big = timeit("a[500]", globals={"a": big}, number=200_000)
print(t_big < t_small * 3)                                  # True  (about equal)

# 2. `in` on a list is O(n): 1000x more items, about 1000x slower
t_small = timeit("-1 in a", globals={"a": small}, number=2_000)
t_big = timeit("-1 in a", globals={"a": big}, number=2_000)
print(t_big > t_small * 100)                                # True

# 3. insert(0, x) is O(n); append is O(1)
def build_with_insert(n):
    a = []
    for i in range(n): a.insert(0, i)
def build_with_append(n):
    a = []
    for i in range(n): a.append(i)
slow, fast = timeit(lambda: build_with_insert(30_000), number=1), timeit(lambda: build_with_append(30_000), number=1)
print(slow > fast * 10)                                     # True: n inserts at the front is O(n²) in total
```

## 3. `tuple`

Immutable array: `t[i]` `O(1)`, `x in t` `O(n)`, `t + u` `O(n + m)` (new tuple), `len(t)` `O(1)`, hashing a tuple `O(n)` (uses all elements). Slightly faster and smaller than a list; use it for fixed records and dictionary keys.

## 4. `dict` and `set` (hash tables)

```text
 key ──hash()──► number ──mod table size──► slot ──► (compare keys on collisions)
```

| Operation | Average | Worst | Notes |
|-----------|---------|-------|-------|
| `d[key]`, `d.get(key)`, `key in d` | `O(1)` | `O(n)` | worst case needs many colliding hashes |
| `d[key] = value` | `O(1)` amortized | `O(n)` | occasional resize and rehash |
| `del d[key]`, `d.pop(key)` | `O(1)` | `O(n)` | |
| `len(d)` | `O(1)` | | |
| `for k in d`, `d.items()` | `O(n)` | | insertion order is preserved |
| `d.copy()`, `dict(d)` | `O(n)` | | |
| `d1 \| d2`, `d.update(d2)` | `O(m)` / `O(n + m)` | | |
| `s.add(x)`, `x in s`, `s.remove(x)` | `O(1)` | `O(n)` | sets are dicts without values |
| `s1 \| s2` (union) | `O(n + m)` | | |
| `s1 & s2` (intersection) | `O(min(n, m))` | `O(n · m)` | iterates the smaller set |
| `s1 - s2` (difference) | `O(n)` | | |
| `s1 <= s2` (subset) | `O(n)` | | |

Requirements: keys/elements must be **hashable** (immutable: numbers, strings, tuples of hashables); `__eq__` and `__hash__` must agree ([equality and hashing](../04-oop/classes-objects/README.md)). More: [hash tables](../02-data-structures/hash-tables/README.md).

```python
import random
from timeit import timeit

haystack_list = list(range(50_000))
haystack_set = set(haystack_list)
needles = [random.randrange(100_000) for _ in range(300)]
t_list = timeit("[n in h for n in needles]", globals={"h": haystack_list, "needles": needles}, number=5)
t_set = timeit("[n in h for n in needles]", globals={"h": haystack_set, "needles": needles}, number=5)
print(t_list > t_set * 100)                                 # True: a set answers "is it there?" in O(1), a list in O(n)

# Sets deduplicate and speed up membership: the classic fix for a quadratic loop
def intersection_slow(a, b): return [x for x in a if x in b]               # O(n * m) with a list b
def intersection_fast(a, b):
    b = set(b)
    return [x for x in a if x in b]                                        # O(n + m)
a, b = list(range(0, 20_000, 2)), list(range(0, 20_000, 3))
assert intersection_slow(a, b) == intersection_fast(a, b)
print(timeit(lambda: intersection_slow(a, b), number=1) > timeit(lambda: intersection_fast(a, b), number=1) * 20)    # True
```

## 5. `str` (immutable)

| Operation | Cost | Notes |
|-----------|------|-------|
| `s[i]`, `len(s)` | `O(1)` | |
| `s[i:j]` | `O(j - i)` | copies characters |
| `s + t` | `O(len(s) + len(t))` | **always builds a new string** |
| `s += t` in a loop | up to `O(n²)` total | CPython sometimes optimizes in place, never rely on it |
| `"".join(parts)` | `O(total length)` | the correct way to build a string from many pieces |
| `t in s` (substring search) | `O(n · m)` worst, typically about `O(n)` | |
| `s.find`, `s.count`, `s.replace`, `s.split`, `s.strip`, `s.lower` | `O(n)` | one pass |
| `s == t` | `O(min(n, m))` | |
| `s * k` | `O(n · k)` | |
| `sorted(s)` | `O(n log n)` | returns a list of characters |

```python
from timeit import timeit

def concat_loop(n):
    s = ""
    for i in range(n):
        s = s + "x"                     # builds a new string each time (use s += "x" is the same trap)
    return s

def join_once(n):
    return "".join("x" for _ in range(n))

print(len(concat_loop(1000)) == len(join_once(1000)) == 1000)
slow = timeit(lambda: concat_loop(100_000), number=1)
fast = timeit(lambda: join_once(100_000), number=1)
print(slow >= fast)                                        # True in general: the gap widens with n (CPython may hide it for small cases)

# Hidden quadratic: repeated slicing to consume a string
def count_chars_slicing(s):
    total = 0
    while s:
        total += 1
        s = s[1:]                       # each slice copies the rest of the string: O(n) per step -> O(n²)
    return total

def count_chars_index(s):
    total = 0
    for i in range(len(s)):             # O(n) overall
        total += 1
    return total
```

## 6. `collections.deque` (double-ended queue)

| Operation | Cost |
|-----------|------|
| `append`, `appendleft`, `pop`, `popleft` | `O(1)` |
| `d[i]` (index) | `O(n)` in the middle, `O(1)` near the ends |
| `x in d`, `d.remove(x)` | `O(n)` |
| `d.rotate(k)` | `O(k)` |

Use a `deque` whenever you remove from the **front** (queues, BFS, sliding windows) instead of `list.pop(0)`.

```python
from collections import deque
from timeit import timeit

list_queue = timeit("while q: q.pop(0)", setup="q = list(range(40_000))", number=1)
deque_queue = timeit("while q: q.popleft()", setup="from collections import deque; q = deque(range(40_000))", number=1)
print(list_queue > deque_queue * 5)                        # True: O(n²) versus O(n) in total
```

## 7. `heapq` (binary min-heap on a list) and `bisect`

| Operation | Cost |
|-----------|------|
| `heapq.heappush(h, x)`, `heapq.heappop(h)` | `O(log n)` |
| `h[0]` (peek the minimum) | `O(1)` |
| `heapq.heapify(list)` | `O(n)` |
| `heapq.nlargest(k, a)`, `nsmallest` | `O(n log k)` |
| `bisect.bisect_left(a, x)` (on a **sorted** list) | `O(log n)` |
| `bisect.insort(a, x)` | `O(n)` (search `O(log n)`, but the insertion shifts) |

See [heaps](../02-data-structures/heaps/README.md) and [binary search](../03-algorithms/searching/README.md).

```python
import heapq, bisect, random

data = random.sample(range(1_000_000), 100_000)
top5 = heapq.nlargest(5, data)                                  # O(n log 5): cheaper than sorting everything
assert top5 == sorted(data, reverse=True)[:5]

sorted_data = sorted(data)
i = bisect.bisect_left(sorted_data, 123_456)                     # O(log n): about 17 comparisons for 100,000 items
print(0 <= i <= len(sorted_data))
```

## 8. Other useful costs

| Operation | Cost |
|-----------|------|
| `sorted(iterable)`, `list.sort()` | `O(n log n)`; adaptive: `O(n)` on already-sorted data |
| `sum`, `min`, `max`, `any`, `all` | `O(n)` (`any`/`all` can stop early) |
| `enumerate`, `zip`, `map`, `filter`, `reversed` (as iterators) | `O(1)` to create, `O(n)` to consume, `O(1)` extra space |
| `list(zip(...))`, `list(map(...))` | `O(n)` time and space |
| `functools.lru_cache` hit | `O(1)` |
| `collections.Counter(items)` | `O(n)` |
| `collections.Counter.most_common(k)` | `O(n log k)` |
| `itertools.combinations(n, k)` | produces `C(n, k)` items |
| `itertools.permutations(n)` | produces `n!` items |
| `random.sample(population, k)` | `O(k)` (or `O(n)`) |
| `copy.deepcopy(x)` | `O(size of the object graph)` |
| file read of `b` bytes | `O(b)` (but dominated by I/O latency) |
| `open()` iteration by lines | `O(1)` memory per line |
| `import module` (first time) | depends on the module; cached afterwards (`O(1)`) |

## 9. The hidden-cost traps (quadratic code that looks linear)

| Looks like one loop | Hidden `O(n)` | Fix |
|---------------------|---------------|-----|
| `for x in a: if x in other_list:` | `in` on a list | `other = set(other_list)` |
| `for ...: result = result + [x]` | list concatenation copies | `result.append(x)` |
| `for ...: s += piece` | string concatenation | collect and `"".join` |
| `while q: item = q.pop(0)` | shifts the list | `collections.deque` |
| `for i in range(len(a)): a.insert(0, ...)` | shifts the list | build with append, then reverse |
| `for ...: sorted(items)` inside a loop | re-sorting each time | sort once, or use `heapq`/`bisect.insort` |
| `for ...: items.remove(x)` | search plus shift | filter into a new list or use a set |
| `while s: s = s[1:]` | slice copies | use an index |
| `len(set(items))` inside a loop | rebuilding the set | maintain the set incrementally |
| `list(d.keys())[0]` repeatedly | builds a list each time | `next(iter(d))` |

```python
# Count how many times the "inner" operation really happens by instrumenting `in`
class CountingList(list):
    scans = 0
    def __contains__(self, item):
        CountingList.scans += 1
        return super().__contains__(item)

seen = CountingList()
for x in range(1000):
    if x not in seen:                    # looks like O(1), actually scans the list: O(n) per check
        seen.append(x)
print(CountingList.scans)                # 1000 scans, each over a growing list: ~n²/2 = 500,000 element comparisons in total
```

## 10. Two real-world examples

**Example 1: A CSV import that took 4 hours.** A script loaded 200,000 rows, and for each row checked `if row["email"] not in emails_seen` where `emails_seen` was a **list**. Each check scanned up to 200,000 items: `O(n²)` = 20 billion comparisons. Changing `[]` to `set()` (two characters) made it run in 2 seconds. The function was correct; only the data structure choice was wrong, and the cheat sheet would have flagged it on code review.

**Example 2: Building a long log message.** A function built a 5 MB report with `report += line` in a loop over 100,000 lines. On some Python builds that is quadratic (each `+=` copies the whole string), and memory churn made the service spike. Switching to `lines.append(line)` and `"\n".join(lines)` made it linear and use a fraction of the memory.

## 11. Common mistakes

- Using a list for membership tests on large data (`in` is `O(n)`).
- Using `list.pop(0)` / `insert(0, ...)` as a queue.
- Assuming `s += t` is cheap everywhere.
- Treating `sorted()` inside a loop as free.
- Forgetting that dict/set `O(1)` is *average*; adversarial keys can degrade it (Python randomizes string hashes to prevent attacks).
- Memorizing complexities without knowing *why*: derive them from the data structure (contiguous array, hash table, immutable string).
- Optimizing the wrong operation: measure first ([performance and profiling](../08-modern-python/performance-profiling/README.md)).

## 12. Practice

1. Classify each as `O(1)`, `O(log n)`, `O(n)`, `O(n log n)`: `d["k"]`, `a.append(x)`, `a.pop(0)`, `x in s`, `sorted(a)`, `bisect_left(a, x)`, `a[2:50]`, `sum(a)`, `heappop(h)`.
2. Rewrite this to be linear and explain the saving: `dups = [x for x in a if a.count(x) > 1]`.
3. Choose the best structure: (a) a queue of tasks, (b) membership tests among 10 million IDs, (c) always get the smallest item, (d) keep items sorted with frequent lookups by value, (e) count word frequencies.
4. Measure the cost of `x in list` for sizes 1,000, 10,000 and 100,000 and show it grows linearly.
5. A function removes every even number from a list with `for x in a: if x % 2 == 0: a.remove(x)`. What are two problems? Give a linear version.
6. Explain why `d1 | d2` on dictionaries is `O(n + m)` while `d[key] = v` is `O(1)`.

<details>
<summary>Solutions</summary>

**1.** `O(1)`, `O(1)` amortized, `O(n)`, `O(1)` (set) , `O(n log n)`, `O(log n)`, `O(48)` = `O(k)` slice size, `O(n)`, `O(log n)`.

**2.** `a.count(x)` is `O(n)` inside an `O(n)` loop: `O(n²)`. Linear:
```python
from collections import Counter
a = [1, 2, 2, 3, 3, 3, 4]
counts = Counter(a)
print([x for x in a if counts[x] > 1])         # [2, 2, 3, 3, 3]   O(n)
```

**3.** (a) `collections.deque`; (b) `set` (or a Bloom filter if memory is the problem); (c) `heapq` (min-heap); (d) a sorted list with `bisect` (reads) or a balanced tree structure (e.g. `sortedcontainers`); (e) `collections.Counter`.

**4.**
```python
from timeit import timeit
times = [timeit("-1 in a", globals={"a": list(range(n))}, number=300) for n in (1_000, 10_000, 100_000)]
print([round(times[i + 1] / times[i], 1) for i in range(2)])      # about [10, 10]: 10x the size, 10x the time
```

**5.** Problems: modifying a list while iterating skips elements, and each `remove` is `O(n)` (total `O(n²)`). Linear: `a = [x for x in a if x % 2]` or the in-place two-pointer approach.

**6.** `d[key] = v` hashes one key and stores one item. `d1 | d2` creates a new dict, copying all `n` items of `d1` and inserting all `m` items of `d2`.

</details>

## 13. Check yourself

1. Why is `list.insert(0, x)` `O(n)` but `append` `O(1)`?
2. Why is `x in set` fast but `x in list` slow?
3. Why is `"".join(parts)` better than `+=` in a loop?
4. Which structure replaces `list.pop(0)` for queues?
5. What is the cost of `heapq.heappop`?
6. What does "average `O(1)`" mean for dictionaries?

<details>
<summary>Answers</summary>

1. A list is a contiguous array; inserting at the front shifts all items, appending at the end only fills spare capacity.
2. A set hashes the item to find its slot directly; a list compares with each element in turn.
3. `join` computes the total length and copies each piece once (`O(n)`); repeated `+=` can copy the growing string every time.
4. `collections.deque` (`popleft` is `O(1)`).
5. `O(log n)`.
6. With a good hash function the typical lookup is constant time; in the worst case (many collisions) it degrades to `O(n)`.

</details>

[Back to complexity](README.md) · Previous: [best, average, worst and amortized](06-cases-and-amortized-analysis.md) · Next: [beyond Big-O](08-beyond-big-o.md)
