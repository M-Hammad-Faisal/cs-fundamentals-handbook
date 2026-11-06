# Hash Tables: Exercises

## Problems
1. Return `True` if a list contains any duplicate.
2. Find the first non-repeating character in a string.
3. Two sum, returning indices, in one pass.
4. Group words that are anagrams of each other.
5. Count subarrays whose sum equals `k`.
6. Find the **longest consecutive sequence** in an unsorted list in `O(n)`.
7. Check whether two strings are **isomorphic** (consistent one-to-one character mapping).
8. Return the `k` most frequent elements.
9. Implement your own hash map with chaining (put, get, delete, resize).
10. Design a data structure with `insert`, `remove` and `get_random` all in `O(1)`.

<details>
<summary>Solutions</summary>

```python
import random
from collections import Counter, defaultdict

# 1
def has_duplicate(nums):
    return len(nums) != len(set(nums))

# 2
def first_unique(s):
    c = Counter(s)
    for i, ch in enumerate(s):
        if c[ch] == 1:
            return i
    return -1

# 3
def two_sum(nums, target):
    seen = {}
    for i, x in enumerate(nums):
        if target - x in seen:
            return seen[target - x], i
        seen[x] = i

# 4
def group_anagrams(words):
    g = defaultdict(list)
    for w in words:
        g["".join(sorted(w))].append(w)
    return list(g.values())

# 5
def subarray_sum(nums, k):
    seen, total, count = {0: 1}, 0, 0
    for x in nums:
        total += x
        count += seen.get(total - k, 0)
        seen[total] = seen.get(total, 0) + 1
    return count

# 6  (only start counting from the beginning of a run)
def longest_consecutive(nums):
    s, best = set(nums), 0
    for x in s:
        if x - 1 not in s:
            y = x
            while y + 1 in s:
                y += 1
            best = max(best, y - x + 1)
    return best

# 7
def is_isomorphic(a, b):
    if len(a) != len(b):
        return False
    ab, ba = {}, {}
    for x, y in zip(a, b):
        if ab.setdefault(x, y) != y or ba.setdefault(y, x) != x:
            return False
    return True

# 8  (O(n log k) with a heap; this is O(n log n) and simple)
def top_k_frequent(nums, k):
    return [x for x, _ in Counter(nums).most_common(k)]

# 9
class HashMap:
    def __init__(self, capacity=8):
        self.buckets = [[] for _ in range(capacity)]
        self.size = 0
    def _bucket(self, key):
        return self.buckets[hash(key) % len(self.buckets)]
    def put(self, key, value):
        b = self._bucket(key)
        for i, (k, _) in enumerate(b):
            if k == key:
                b[i] = (key, value)
                return
        b.append((key, value))
        self.size += 1
        if self.size / len(self.buckets) > 0.75:
            self._resize()
    def get(self, key, default=None):
        for k, v in self._bucket(key):
            if k == key:
                return v
        return default
    def delete(self, key):
        b = self._bucket(key)
        for i, (k, _) in enumerate(b):
            if k == key:
                del b[i]
                self.size -= 1
                return True
        return False
    def _resize(self):
        old = self.buckets
        self.buckets = [[] for _ in range(len(old) * 2)]
        self.size = 0
        for b in old:
            for k, v in b:
                self.put(k, v)

# 10  (list for random access + dict value->index; swap with last on delete)
class RandomizedSet:
    def __init__(self):
        self.items, self.pos = [], {}
    def insert(self, v):
        if v in self.pos:
            return False
        self.pos[v] = len(self.items)
        self.items.append(v)
        return True
    def remove(self, v):
        if v not in self.pos:
            return False
        i, last = self.pos[v], self.items[-1]
        self.items[i], self.pos[last] = last, i
        self.items.pop()
        del self.pos[v]
        return True
    def get_random(self):
        return random.choice(self.items)
```

</details>
