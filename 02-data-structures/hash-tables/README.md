# Hash Tables

## Detailed lessons (start here if you are new)

1. [Hash functions and collisions](01-hash-functions-and-collisions.md): hashing, the birthday paradox, load factor
2. [Implementing hash tables](02-implementing-hash-tables.md): chaining, linear probing, tombstones, resizing
3. [Dict, set, patterns, Bloom filters and consistent hashing](03-dict-set-internals-and-bloom-filters.md)

The rest of this page is the quick reference.

## 1. The concept

A **hash table** maps **keys** to **values** with `O(1)` average lookup, insert and delete. Python's `dict` and `set` are hash tables.

The trick: a **hash function** converts any key into an integer, and that integer (reduced modulo the table size) picks a slot in an array. Instead of searching, you compute where the key must be.

```
key "apple" --hash--> 982347 --mod 8--> slot 3
            [0][1][2][ 3: apple->5 ][4][5][6][7]
```

## 2. How it works

### Hash functions

A good hash function is:

- **Deterministic:** the same key always gives the same hash.
- **Uniform:** spreads keys evenly across slots.
- **Fast** to compute.

In Python, `hash(obj)` provides the integer. Keys must be **hashable**: immutable types (`int`, `str`, `tuple` of hashables, `frozenset`) work; `list`, `dict`, `set` do not. If two objects are equal they must have equal hashes.

String hashes are randomized per process (`PYTHONHASHSEED`) to defend against collision attacks, so never persist `hash()` values or rely on them across runs.

### Collisions

Different keys can land in the same slot. Two main strategies:

| Strategy | Idea | Notes |
|----------|------|-------|
| **Separate chaining** | Each slot holds a list (or tree) of entries | Simple; degrades gracefully |
| **Open addressing** | On collision, probe other slots (linear, quadratic, double hashing) | Cache friendly; needs low load factor; CPython's dict uses a form of this |

**Load factor** = entries / slots. As it rises, collisions rise. Tables **resize** (typically double) and **rehash** all keys when the load factor passes a threshold. Resizes are rare, so insert is amortized `O(1)`.

### A minimal chaining implementation

```python
class HashMap:
    def __init__(self, capacity=8):
        self.buckets = [[] for _ in range(capacity)]
        self.size = 0

    def _index(self, key):
        return hash(key) % len(self.buckets)

    def put(self, key, value):
        bucket = self.buckets[self._index(key)]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)      # update
                return
        bucket.append((key, value))
        self.size += 1
        if self.size / len(self.buckets) > 0.75:
            self._resize()

    def get(self, key, default=None):
        for k, v in self.buckets[self._index(key)]:
            if k == key:
                return v
        return default

    def delete(self, key):
        bucket = self.buckets[self._index(key)]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                del bucket[i]
                self.size -= 1
                return True
        return False

    def _resize(self):
        old = self.buckets
        self.buckets = [[] for _ in range(len(old) * 2)]
        self.size = 0
        for bucket in old:
            for k, v in bucket:
                self.put(k, v)
```

### Complexity

| Operation | Average | Worst case |
|-----------|---------|------------|
| Insert | `O(1)` amortized | `O(n)` (all keys collide, or during resize) |
| Lookup | `O(1)` | `O(n)` |
| Delete | `O(1)` | `O(n)` |
| Iterate | `O(n)` | `O(n)` |
| Memory | `O(n)` | `O(n)` |

Python 3.7+ guarantees that `dict` preserves **insertion order**.

## 3. Python toolkit

```python
d = {"a": 1}
d["b"] = 2
d.get("z", 0)                    # safe lookup with default
d.setdefault("k", []).append(1)  # create-if-missing
"a" in d                         # O(1)
for k, v in d.items(): ...

from collections import defaultdict, Counter, OrderedDict

groups = defaultdict(list)
groups["x"].append(1)            # no KeyError

Counter("mississippi")           # {'i': 4, 's': 4, 'p': 2, 'm': 1}
Counter(words).most_common(3)

s = {1, 2, 3}                    # set: hash table of keys only
s & {2, 3, 4}                    # intersection
s | {9}                          # union
s - {1}                          # difference
```

## 4. Patterns

### Frequency counting

```python
def first_unique_char(s):
    counts = Counter(s)
    for i, ch in enumerate(s):
        if counts[ch] == 1:
            return i
    return -1
```

### Complement lookup (two sum)

```python
def two_sum(nums, target):
    seen = {}
    for i, x in enumerate(nums):
        if target - x in seen:
            return seen[target - x], i
        seen[x] = i
```

### Grouping by a key

```python
def group_anagrams(words):
    groups = defaultdict(list)
    for w in words:
        groups["".join(sorted(w))].append(w)
    return list(groups.values())
```

### Prefix sum + hash map (subarrays summing to k)

```python
def subarray_sum(nums, k):
    seen, total, count = {0: 1}, 0, 0
    for x in nums:
        total += x
        count += seen.get(total - k, 0)
        seen[total] = seen.get(total, 0) + 1
    return count
```

### Deduplication and set membership

```python
def has_duplicate(nums):
    return len(nums) != len(set(nums))
```

## 5. Two real-world examples

### Example 1: Caching and memoization

A cache maps a request key (a URL, a function's arguments, a user ID) to a computed result. Lookup is `O(1)`, so a cache hit saves the whole computation. `functools.lru_cache`, Redis, Memcached and CDN edge caches are all hash tables at heart. Without constant-time lookup, caching would not pay off.

### Example 2: Database indexes and deduplication at scale

Hash indexes in databases map a column value to row locations in `O(1)`. In data pipelines, a hash set of seen IDs removes duplicates from billions of events without sorting. Distributed systems use **consistent hashing** to decide which server holds a key, so adding a server moves only a small fraction of keys (used by Cassandra, DynamoDB, and CDNs). Password storage uses **cryptographic hashes** (a different idea: one-way, collision resistant) so a database leak does not expose passwords.

## 6. Tips, tricks and pitfalls

- **Reach for a dict or set whenever you write an inner search loop.** It usually turns `O(n²)` into `O(n)`.
- **Hash keys must be immutable.** Use a `tuple` instead of a `list` as a composite key.
- **Mutating a key's hash-relevant state after insertion breaks lookups.**
- **Order:** `dict` keeps insertion order; `set` does not.
- **Do not modify a dict while iterating it** (`RuntimeError`); iterate over `list(d)`.
- **Missing keys:** `d[key]` raises `KeyError`; `d.get(key)` returns `None`.
- **Worst case exists.** Adversarial inputs can force collisions; Python randomizes string hashes to mitigate this.
- **Floating-point keys are risky** because of precision issues.
- **Memory cost:** hash tables use more memory than arrays because they keep spare slots.
- **Hash is not encryption.** Use `hashlib`/`bcrypt`/`argon2` for security, not `hash()`.

## 7. Check yourself

1. Why is hash table lookup `O(1)` on average but `O(n)` in the worst case?
2. What is a collision, and how do chaining and open addressing handle it?
3. What is the load factor and why do tables resize?
4. Why can a `list` not be a dict key, but a `tuple` can?
5. What must be true about `__eq__` and `__hash__` for custom key objects?
6. How does a hash map solve two-sum in one pass?
7. Why does Python randomize string hashes?

<details>
<summary>Answers</summary>

1. The hash gives the slot directly (`O(1)`). If many keys collide into the same slot, you scan a long chain or probe sequence (`O(n)`).
2. Two keys map to the same slot. Chaining stores multiple entries per slot; open addressing probes for another free slot.
3. Load factor is entries divided by slots. A high load factor means more collisions, so the table grows and rehashes to keep operations fast.
4. Lists are mutable, so their hash could change; tuples of hashables are immutable and hashable.
5. Equal objects must have equal hashes. Define both consistently, and base the hash on immutable fields.
6. For each number, check whether `target - x` was already seen; if not, store `x`. One pass, `O(n)`.
7. To prevent attackers from crafting keys that all collide and degrade the table to `O(n)`.

</details>
