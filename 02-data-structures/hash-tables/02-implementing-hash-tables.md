# Implementing Hash Tables

**Prerequisites:** [hash functions and collisions](01-hash-functions-and-collisions.md), [linked lists](../linked-lists/01-singly-linked-list.md). **You will learn:** the two classic ways to resolve collisions, **separate chaining** and **open addressing** (linear probing), how **resizing** keeps operations `O(1)`, why deletion needs **tombstones**, and how to build a working `dict` yourself.

## 1. In plain words

When two keys want the same slot you have two choices:

- **Chaining:** each slot holds a *small list* of everything that landed there. (A hook that holds several coats.)
- **Open addressing:** each slot holds *one* item; if it is taken, walk to the next free slot. (Finding the next empty hook.)

## 2. Separate chaining

```text
index  bucket
  0    -> ("apple", 1) -> ("fig", 9)
  1
  2    -> ("kiwi", 4)
  3    -> ("date", 7)
```

```python
class ChainedHashMap:
    def __init__(self, capacity=8, max_load=0.75):
        self.buckets = [[] for _ in range(capacity)]
        self.size = 0
        self.max_load = max_load
        self.resizes = 0

    def _bucket(self, key):
        return self.buckets[hash(key) % len(self.buckets)]

    def put(self, key, value):
        bucket = self._bucket(key)
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)                 # update an existing key
                return
        bucket.append((key, value))
        self.size += 1
        if self.size / len(self.buckets) > self.max_load:
            self._resize(len(self.buckets) * 2)

    def get(self, key, default=None):
        for k, v in self._bucket(key):
            if k == key:
                return v
        return default

    def remove(self, key):
        bucket = self._bucket(key)
        for i, (k, _) in enumerate(bucket):
            if k == key:
                del bucket[i]
                self.size -= 1
                return True
        return False

    def _resize(self, new_capacity):
        old = [pair for bucket in self.buckets for pair in bucket]
        self.buckets = [[] for _ in range(new_capacity)]
        self.size = 0
        for k, v in old:                                 # slots depend on capacity, so re-hash everything
            self.put(k, v)
        self.resizes += 1

    def __len__(self):
        return self.size

m = ChainedHashMap()
for i in range(20):
    m.put(f"key{i}", i * i)
m.put("key3", "updated")
print(len(m), len(m.buckets), m.resizes)       # 20 32 2
print(m.get("key3"), m.get("key19"), m.get("nope", "missing"))      # updated 361 missing
print(m.remove("key3"), m.remove("key3"), len(m))                   # True False 19
```

**Cost:** with a good hash and load factor kept below 0.75, buckets are short (about 1 item), so `put`, `get`, `remove` are **`O(1)` average**. Worst case (everything in one bucket) is `O(n)`.

**Why resize by doubling?** A resize costs `O(n)`, but it happens only after `n/2` cheap insertions: **amortized `O(1)`** (the same argument as the [dynamic array](../arrays-strings/01-arrays-and-memory.md)).

## 3. Open addressing with linear probing

All items live inside one array. On collision, try the next slot, then the next (wrapping around).

```text
insert A -> hash says slot 2: [ , ,A, , , ]
insert B -> hash says slot 2: taken, try 3: [ , ,A,B, , ]
insert C -> hash says slot 3: taken, try 4: [ , ,A,B,C, ]
```

**The deletion problem.** If you simply empty B's slot, searching for C (which probed past it) would stop at the hole and wrongly say "not found". The fix is a **tombstone**: a marker meaning "something was here; keep probing".

```python
EMPTY, TOMBSTONE = object(), object()

class ProbingHashMap:
    def __init__(self, capacity=8, max_load=0.5):
        self.slots = [EMPTY] * capacity
        self.used = 0                       # live items + tombstones (both lengthen probes)
        self.size = 0                       # live items only
        self.max_load = max_load
        self.probe_steps = 0

    def _find_slot(self, key):
        """Return (index_of_key_or_None, first_reusable_index)."""
        i = hash(key) % len(self.slots)
        first_free = None
        for _ in range(len(self.slots)):
            slot = self.slots[i]
            if slot is EMPTY:
                return None, first_free if first_free is not None else i
            if slot is TOMBSTONE:
                if first_free is None:
                    first_free = i
            elif slot[0] == key:
                return i, first_free
            self.probe_steps += 1
            i = (i + 1) % len(self.slots)       # linear probing: next slot, wrap around
        return None, first_free

    def put(self, key, value):
        found, free = self._find_slot(key)
        if found is not None:
            self.slots[found] = (key, value)
            return
        if self.slots[free] is EMPTY:
            self.used += 1
        self.slots[free] = (key, value)
        self.size += 1
        if self.used / len(self.slots) > self.max_load:
            self._resize(len(self.slots) * 2)

    def get(self, key, default=None):
        found, _ = self._find_slot(key)
        return default if found is None else self.slots[found][1]

    def remove(self, key):
        found, _ = self._find_slot(key)
        if found is None:
            return False
        self.slots[found] = TOMBSTONE
        self.size -= 1
        return True

    def _resize(self, new_capacity):
        live = [s for s in self.slots if s is not EMPTY and s is not TOMBSTONE]
        self.slots = [EMPTY] * new_capacity
        self.used = self.size = 0
        for k, v in live:                       # tombstones disappear in the rebuild
            self.put(k, v)

    def __len__(self):
        return self.size

p = ProbingHashMap()
for word in ["red", "green", "blue", "cyan", "pink", "gold"]:
    p.put(word, len(word))
print(len(p), len(p.slots))                    # 6 16
print(p.get("blue"), p.remove("blue"), p.get("blue"), p.get("gold"))      # 4 True None 4
```

Trade-offs, side by side:

| | Chaining | Open addressing (linear probing) |
|---|----------|----------------------------------|
| Memory | extra list objects | one compact array |
| Cache behavior | pointer chasing | contiguous: very fast |
| High load factor | degrades gracefully | degrades quickly (needs `α` below about 0.7) |
| Deletion | easy | needs tombstones |
| Clustering | no | **primary clustering** (runs of filled slots grow) |

Cures for clustering: **quadratic probing** (step 1, 4, 9, ...), **double hashing** (second hash sets the step), or the **perturbation** scheme Python uses.

## 4. Watching clustering happen

```python
import random

def average_probes(load, capacity=1000):
    random.seed(1)
    table = ProbingHashMap(capacity=capacity, max_load=2)    # never resize: we want to study load
    for n in range(int(capacity * load)):
        table.put(n * 7919 + random.randrange(10**9), n)
    table.probe_steps = 0
    for n in range(200):
        table.get(random.randrange(10**9))                   # mostly misses: the worst case
    return table.probe_steps / 200

for load in (0.25, 0.5, 0.75, 0.9):
    print(load, round(average_probes(load), 1))
# 0.25 0.3
# 0.5 1.4
# 0.75 5.7
# 0.9 34.6
```

(The number counts the *extra* slots examined before a search ends.)

Searches get dramatically longer as the table fills: from 0.3 extra steps at 25% full to about 35 at 90% full. Theory agrees that cost explodes like `1/(1-α)²` as `α` approaches 1. That is why implementations resize early.

## 5. Using the map as a dictionary and as a set

A **set** is just a map without values. Everything you can do with `dict` keys works with `set`:

```python
class HashSet:
    def __init__(self):
        self._map = ChainedHashMap()
    def add(self, item):
        self._map.put(item, True)
    def __contains__(self, item):
        return self._map.get(item) is True
    def discard(self, item):
        self._map.remove(item)
    def __len__(self):
        return len(self._map)

s = HashSet()
for x in [3, 1, 3, 2, 1]:
    s.add(x)
print(len(s), 2 in s, 9 in s)                  # 3 True False
```

## 6. Two real-world examples

**Example 1: Word frequency.** Counting words in a book is `counts[word] = counts.get(word, 0) + 1`; each of a million words costs about one hash lookup instead of a scan of everything seen so far.

**Example 2: Caches and session stores.** Redis and Memcached are giant hash tables keyed by strings; a web server maps a session cookie to the user's data in `O(1)`.

## 7. Common mistakes

- Forgetting to **re-hash** on resize (copying buckets verbatim breaks lookups).
- Removing from an open-addressing table without a tombstone.
- Counting tombstones as free space in the load factor (they lengthen probes).
- Resizing by adding a constant instead of multiplying (loses amortized `O(1)`).
- Comparing keys with `is` instead of `==`.
- Mutating a key after inserting it.

## 8. Practice

1. Add an `items()` method that yields every `(key, value)` to `ChainedHashMap`.
2. What goes wrong if `_resize` keeps the old bucket count but the load threshold is exceeded?
3. Insert keys that all hash to the same slot into `ProbingHashMap` (use a class whose `__hash__` returns 0). How many probe steps does the 10th lookup need?
4. Explain how two keys with equal `hash()` can still be different keys in the table.
5. Implement `__getitem__`, `__setitem__`, and `__delitem__` so `ChainedHashMap` works with `m["a"] = 1`.

<details>
<summary>Solutions</summary>

**1.**
```python
def items(self):
    for bucket in self.buckets:
        yield from bucket
ChainedHashMap.items = items
m2 = ChainedHashMap(); m2.put("a", 1); m2.put("b", 2)
print(sorted(m2.items()))                      # [('a', 1), ('b', 2)]
```

**2.** Buckets grow longer and longer, lookups drift toward `O(n)`.

**3.**
```python
class Zero:
    def __init__(self, n): self.n = n
    def __hash__(self): return 0
    def __eq__(self, o): return self.n == o.n
z = ProbingHashMap(capacity=64, max_load=1.5)
for n in range(10): z.put(Zero(n), n)
z.probe_steps = 0
z.get(Zero(9))
print(z.probe_steps)                           # 9
```

**4.** Slot placement uses the hash, but the table then compares keys with `==`; different keys can share a hash (a collision) and sit in the same bucket or probe sequence.

**5.**
```python
class DictLikeMap(ChainedHashMap):
    def __getitem__(self, key):
        sentinel = object()
        value = self.get(key, sentinel)
        if value is sentinel:
            raise KeyError(key)
        return value
    def __setitem__(self, key, value):
        self.put(key, value)
    def __delitem__(self, key):
        if not self.remove(key):
            raise KeyError(key)

m3 = DictLikeMap(); m3["a"] = 1
print(m3["a"]); del m3["a"]; print(len(m3))      # 1 then 0
```

</details>

## 9. Check yourself

1. How does chaining handle a collision? How does open addressing?
2. Why is resizing amortized `O(1)`?
3. Why do we need tombstones?
4. What is primary clustering?
5. Why does a table with a higher load factor get slower?

<details>
<summary>Answers</summary>

1. Chaining appends to the slot's list; open addressing probes for the next free slot.
2. Each expensive resize is paid for by the many cheap inserts since the previous one.
3. A plain empty slot would stop a search early and hide items placed past it.
4. Filled slots form long runs, so new keys landing in the run keep extending it.
5. Fewer free slots means longer chains or longer probe sequences.

</details>

[Back to hash tables](README.md) · Previous: [hash functions](01-hash-functions-and-collisions.md) · Next: [dict, set and Bloom filter](03-dict-set-internals-and-bloom-filters.md)
