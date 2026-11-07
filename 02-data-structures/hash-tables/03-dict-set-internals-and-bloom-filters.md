# Dict, Set, Hash-Map Patterns, Bloom Filters and Consistent Hashing

**Prerequisites:** [implementing hash tables](02-implementing-hash-tables.md). **You will learn:** how Python's `dict` and `set` really behave (ordering, memory, speed), the everyday **hash-map patterns** (counting, grouping, two-sum, caching), the **Bloom filter** (membership with tiny memory), and **consistent hashing** (how big systems spread keys).

## 1. Python's dict in practice

Facts worth knowing:

- Lookup, insert and delete are **`O(1)` average**.
- Since Python 3.7 a `dict` **remembers insertion order**. (A `set` does not.)
- Keys must be hashable; values can be anything.
- The table is **open addressing** with a compact entries array, which is why dicts are fast and memory-friendly.

```python
import sys, time

d = {}
d["b"] = 2; d["a"] = 1; d["c"] = 3
print(list(d))                          # ['b', 'a', 'c']   (insertion order)
del d["a"]; d["a"] = 9
print(list(d))                          # ['b', 'c', 'a']   (re-inserted keys go to the end)

big = list(range(1_000_000))
as_set = set(big)
t = time.perf_counter(); 999_999 in big; list_time = time.perf_counter() - t
t = time.perf_counter(); 999_999 in as_set; set_time = time.perf_counter() - t
print(list_time > 100 * set_time)       # True   (a scan of a million items versus one hash lookup)

print(sys.getsizeof([]), sys.getsizeof({}), sys.getsizeof(set()))       # 56 64 216 on one build (empty containers; exact bytes vary by Python version)
```

### Useful dict tools

```python
from collections import defaultdict, Counter

inventory = {"apples": 3, "pears": 0}
print(inventory.get("kiwis", 0))                         # 0     (no KeyError)
inventory.setdefault("plums", 5)
print(inventory)                                         # {'apples': 3, 'pears': 0, 'plums': 5}
merged = {"a": 1} | {"b": 2, "a": 10}                    # Python 3.9+: right side wins
print(merged)                                            # {'a': 10, 'b': 2}

groups = defaultdict(list)
for word in ["tea", "eat", "ate", "tan", "nat", "bat"]:
    groups["".join(sorted(word))].append(word)
print(list(groups.values()))                             # [['tea', 'eat', 'ate'], ['tan', 'nat'], ['bat']]

print(Counter("mississippi").most_common(2))             # [('i', 4), ('s', 4)]
```

## 2. The hash-map patterns that solve most interview problems

**Pattern 1: counting.**

```python
def first_unique_char(s):
    counts = Counter(s)
    for i, ch in enumerate(s):
        if counts[ch] == 1:
            return i
    return -1
print(first_unique_char("leetcode"), first_unique_char("aabb"))          # 0 -1
```

**Pattern 2: "have I seen this?" (two-sum).** Brute force checks every pair: `O(n²)`. With a map of *value → index*, each number looks up the one it needs:

```python
def two_sum(nums, target):
    seen = {}                                   # value -> index
    for i, x in enumerate(nums):
        if target - x in seen:
            return seen[target - x], i
        seen[x] = i
    return None
print(two_sum([2, 7, 11, 15], 9), two_sum([3, 2, 4], 6), two_sum([1, 2], 10))      # (0, 1) (1, 2) None
```

**Pattern 3: grouping by a canonical key** (the anagram groups above): choose a key that is equal for things you want grouped.

**Pattern 4: prefix-sum + map** (subarrays with a given sum in `O(n)`):

```python
def count_subarrays_with_sum(nums, k):
    seen = defaultdict(int, {0: 1})             # prefix sum -> how many times seen
    total = count = 0
    for x in nums:
        total += x
        count += seen[total - k]                # a previous prefix that leaves exactly k
        seen[total] += 1
    return count
print(count_subarrays_with_sum([1, 1, 1], 2), count_subarrays_with_sum([3, 4, 7, 2, -3, 1, 4, 2], 7))      # 2 4
```

**Pattern 5: memoization (caching results).**

```python
from functools import lru_cache

calls = 0
@lru_cache(maxsize=None)
def fib(n):
    global calls
    calls += 1
    return n if n < 2 else fib(n - 1) + fib(n - 2)
print(fib(80), calls)                           # 23416728348467685 81
```

Without the cache `fib(80)` would take billions of years; the dictionary inside `lru_cache` makes it 81 calls.

**Pattern 6: longest consecutive sequence (a set makes it `O(n)`).**

```python
def longest_consecutive(nums):
    members, best = set(nums), 0
    for x in members:
        if x - 1 not in members:                # only start counting at the beginning of a run
            length = 1
            while x + length in members:
                length += 1
            best = max(best, length)
    return best
print(longest_consecutive([100, 4, 200, 1, 3, 2]))       # 4
```

## 3. Set operations

```python
a, b = {1, 2, 3, 4}, {3, 4, 5}
print(a | b, a & b, a - b, a ^ b)               # {1, 2, 3, 4, 5} {3, 4} {1, 2} {1, 2, 5}
print({3, 4} <= a, a.isdisjoint({9}))           # True True
```

Union, intersection, difference and symmetric difference run in about `O(len)` of the smaller operand (for intersection), so "common friends of two users" is cheap.

## 4. Bloom filter: remember "maybe" with almost no memory

**Problem:** a browser wants to warn about dangerous URLs from a list of 10 million without storing all of them. A **Bloom filter** is a bit array plus several hash functions:

- `add(x)`: set `k` bits (positions given by `k` hashes of `x`).
- `might_contain(x)`: if **any** of the `k` bits is 0 the item is **definitely not** present; if all are 1 it is **probably** present.

So: **no false negatives, a small chance of false positives**, and you cannot delete or list items.

```python
import hashlib, math

class BloomFilter:
    def __init__(self, expected_items, false_positive_rate=0.01):
        self.m = math.ceil(-expected_items * math.log(false_positive_rate) / (math.log(2) ** 2))   # bits
        self.k = max(1, round(self.m / expected_items * math.log(2)))                              # hash functions
        self.bits = bytearray(self.m // 8 + 1)

    def _positions(self, item):
        digest = hashlib.sha256(str(item).encode()).digest()
        h1 = int.from_bytes(digest[:8], "big")
        h2 = int.from_bytes(digest[8:16], "big") | 1
        return [(h1 + i * h2) % self.m for i in range(self.k)]          # k hashes from two (double hashing)

    def add(self, item):
        for pos in self._positions(item):
            self.bits[pos // 8] |= 1 << (pos % 8)

    def might_contain(self, item):
        return all(self.bits[pos // 8] & (1 << (pos % 8)) for pos in self._positions(item))

bad_urls = BloomFilter(expected_items=10_000, false_positive_rate=0.01)
for i in range(10_000):
    bad_urls.add(f"http://evil{i}.example")

print(bad_urls.m // 8, "bytes,", bad_urls.k, "hashes")      # 11981 bytes, 7 hashes
print(all(bad_urls.might_contain(f"http://evil{i}.example") for i in range(10_000)))      # True (never a false negative)
false_positives = sum(bad_urls.might_contain(f"http://good{i}.example") for i in range(10_000))
print(false_positives / 10_000)                 # about 0.01 (the rate we asked for; one run gave 0.0109)
```

Memory: about **1.2 KB per 1000 items at 1% error** (roughly 9.6 bits per item) versus storing every URL string.

Use it as a **cheap first check**: "definitely not present" is trusted instantly; "maybe present" triggers the expensive exact lookup (disk, network, database).

## 5. Consistent hashing: spreading keys across servers

`server = hash(key) % N` breaks when `N` changes: almost every key moves. **Consistent hashing** places servers and keys on a circle (a sorted list of hash positions); a key belongs to the **next server clockwise**. Adding or removing a server only moves the keys next to it.

```python
import bisect

class HashRing:
    def __init__(self, servers, replicas=100):
        self.replicas = replicas
        self.ring = []                              # sorted list of (position, server)
        for s in servers:
            self.add(s)

    @staticmethod
    def _hash(text):
        return int(hashlib.md5(text.encode()).hexdigest(), 16)

    def add(self, server):
        for i in range(self.replicas):              # virtual nodes smooth out the distribution
            bisect.insort(self.ring, (self._hash(f"{server}#{i}"), server))

    def lookup(self, key):
        i = bisect.bisect(self.ring, (self._hash(key), ""))
        return self.ring[i % len(self.ring)][1]

keys = [f"user{i}" for i in range(10_000)]
ring = HashRing(["A", "B", "C"])
before = {k: ring.lookup(k) for k in keys}
ring.add("D")
after = {k: ring.lookup(k) for k in keys}
moved = sum(before[k] != after[k] for k in keys)
print(round(moved / len(keys), 2))                  # about 0.25 (only keys that now belong to D)

modulo_before = {k: ["A", "B", "C"][HashRing._hash(k) % 3] for k in keys}
modulo_after = {k: ["A", "B", "C", "D"][HashRing._hash(k) % 4] for k in keys}
print(round(sum(modulo_before[k] != modulo_after[k] for k in keys) / len(keys), 2))      # about 0.75 with plain modulo
```

DynamoDB, Cassandra, memcached clients and CDNs use this idea.

## 6. Two real-world examples

**Example 1: Chrome's Safe Browsing and database engines** (Cassandra, HBase, Postgres extensions) put a Bloom filter in front of expensive lookups, skipping the disk for keys that are definitely absent.

**Example 2: Cache clusters.** When a memcached node dies, consistent hashing remaps only that node's keys instead of cold-starting every cache.

## 7. Common mistakes

- Using a list where a set/dict would turn an `O(n²)` loop into `O(n)`.
- Mutating a dict while iterating over it (`RuntimeError`); iterate over `list(d)` instead.
- Relying on set ordering.
- Using a Bloom filter when you need exact answers or deletions (use a counting filter or a real set).
- Forgetting that `defaultdict` creates keys on read (`if k in d` does not).
- Using `hash(key) % N` for sharding in a system that grows.

## 8. Practice

1. Find the first repeated element in a list in `O(n)`.
2. Check whether two strings are anagrams with a `Counter`.
3. Group a list of words by their length.
4. Write `is_subset(a, b)` without using `<=`.
5. Given a list of intervals sorted by start, which structure helps detect duplicates fast? (answer in one line)
6. Why can a Bloom filter never have a false negative?
7. A Bloom filter has 10 bits and 2 hash functions and holds 3 items. What happens as items increase?

<details>
<summary>Solutions</summary>

**1.**
```python
def first_repeat(items):
    seen = set()
    for x in items:
        if x in seen:
            return x
        seen.add(x)
print(first_repeat([3, 1, 4, 1, 5, 9, 2, 6, 5]))       # 1
```

**2.**
```python
print(Counter("listen") == Counter("silent"), Counter("abc") == Counter("abd"))      # True False
```

**3.**
```python
by_len = defaultdict(list)
for w in ["a", "to", "be", "and", "or"]:
    by_len[len(w)].append(w)
print(dict(by_len))                                     # {1: ['a'], 2: ['to', 'be', 'or'], 3: ['and']}
```

**4.**
```python
def is_subset(a, b):
    sb = set(b)
    return all(x in sb for x in a)
print(is_subset([1, 2], [3, 2, 1]), is_subset([1, 9], [3, 2, 1]))      # True False
```

**5.** A set of `(start, end)` tuples (hashing makes duplicate detection `O(1)` per interval).

**6.** Adding an item sets its bits to 1 and bits are never cleared, so a present item always finds all of its bits set.

**7.** The array fills with 1s, so almost every query finds all its bits set: the false-positive rate climbs towards 100%. Size the filter for the number of items you expect.

</details>

## 9. Check yourself

1. What order does a `dict` iterate in?
2. Why does `two_sum` with a dict beat brute force?
3. What does a Bloom filter answer, and with what guarantees?
4. What problem does consistent hashing solve?
5. Name three problems that a counting `dict` solves.

<details>
<summary>Answers</summary>

1. Insertion order (guaranteed since Python 3.7).
2. One `O(1)` lookup per element replaces scanning the rest of the list: `O(n)` rather than `O(n²)`.
3. "Definitely not present" or "probably present"; no false negatives, tunable false positives, no deletion.
4. Changing the number of servers moves only a small share of the keys instead of nearly all.
5. Word frequency, first unique character, anagram checks (also majority element, mode, histogram).

</details>

[Back to hash tables](README.md) · Previous: [implementing hash tables](02-implementing-hash-tables.md)
