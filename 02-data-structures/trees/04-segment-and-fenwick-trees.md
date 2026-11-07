# Segment Trees and Fenwick Trees

**Prerequisites:** [binary trees](01-binary-trees-and-traversals.md), [prefix sums](../arrays-strings/02-array-techniques.md). **You will learn:** how to answer "sum (or min, max) of a range" **and** update single values, both in `O(log n)`, using a **segment tree** and the lighter **Fenwick tree (binary indexed tree)**.

## 1. In plain words

You have `n` numbers (daily sales). You are asked many times: "what is the total from day `l` to day `r`?" and also told "day `i` was corrected to `x`".

| Approach | Range query | Point update |
|----------|-------------|--------------|
| Plain array, loop | `O(n)` | `O(1)` |
| Prefix sums | `O(1)` | `O(n)` (rebuild) |
| **Segment / Fenwick tree** | **`O(log n)`** | **`O(log n)`** |

With a million values and a million operations, `O(n)` per query is a trillion steps; `O(log n)` is about 20 million.

## 2. Segment tree

Build a tree where **each node stores the answer for a range** and its two children cover the halves.

```text
values: [2, 1, 5, 3]          sum tree
                [11  : 0..3]
               /            \
        [3 : 0..1]        [8 : 2..3]
        /      \          /      \
     [2]       [1]      [5]      [3]
```

A query for the range `1..2` combines just the nodes that fit inside the range (never more than about `2 log n` of them).

```python
class SegmentTree:
    def __init__(self, values, combine=lambda a, b: a + b, identity=0):
        self.n = len(values)
        self.combine, self.identity = combine, identity
        self.tree = [identity] * (2 * self.n)
        self.tree[self.n:] = values                       # leaves live in the second half of the array
        for i in range(self.n - 1, 0, -1):                # build parents from the bottom up
            self.tree[i] = combine(self.tree[2 * i], self.tree[2 * i + 1])

    def update(self, index, value):
        i = index + self.n
        self.tree[i] = value
        while i > 1:                                      # recompute every ancestor
            i //= 2
            self.tree[i] = self.combine(self.tree[2 * i], self.tree[2 * i + 1])

    def query(self, left, right):                         # inclusive range [left, right]
        result_left = result_right = self.identity
        lo, hi = left + self.n, right + self.n + 1
        while lo < hi:
            if lo & 1:
                result_left = self.combine(result_left, self.tree[lo]); lo += 1
            if hi & 1:
                hi -= 1; result_right = self.combine(self.tree[hi], result_right)
            lo //= 2; hi //= 2
        return self.combine(result_left, result_right)

sales = [5, 3, 8, 6, 2, 7, 4, 1]
sums = SegmentTree(sales)
print(sums.query(0, 7), sums.query(2, 5), sums.query(3, 3))       # 36 23 6
sums.update(2, 20)                                                # day 2 corrected from 8 to 20
print(sums.query(0, 7), sums.query(2, 5))                         # 48 35

minimums = SegmentTree(sales, combine=min, identity=float("inf"))
maximums = SegmentTree(sales, combine=max, identity=float("-inf"))
print(minimums.query(0, 3), maximums.query(4, 7))                 # 3 7
```

The same code gives **sum, min, max, gcd, xor...** just by changing `combine` and `identity`. The only requirement is that `combine` is **associative** (`(a+b)+c == a+(b+c)`).

Cost: build `O(n)`, query and update `O(log n)`, memory `2n`.

### Brute-force check

```python
import random
random.seed(5)
data = [random.randint(-50, 50) for _ in range(200)]
tree = SegmentTree(data)
for _ in range(2000):
    if random.random() < 0.3:
        i, v = random.randrange(200), random.randint(-50, 50)
        data[i] = v; tree.update(i, v)
    else:
        l = random.randrange(200); r = random.randrange(l, 200)
        assert tree.query(l, r) == sum(data[l:r + 1])
print("2000 random operations match the brute force")             # 2000 random operations match the brute force
```

Always test a clever structure against the obvious slow solution like this.

## 3. Fenwick tree (binary indexed tree)

A Fenwick tree answers **prefix sums** and handles updates with a tiny array and a bit trick. Each slot `i` stores the sum of a block whose length is the **lowest set bit** of `i`.

```text
index (1-based):   1    2     3    4        5    6     7    8
covers:           [1]  [1-2] [3]  [1-4]    [5]  [5-6] [7]  [1-8]
lowbit(i) = i & -i  gives the block size: lowbit(6) = 2, lowbit(8) = 8
```

- To **query** prefix `i`: add `tree[i]`, then jump to `i - lowbit(i)` (strip the lowest set bit) until 0.
- To **update** index `i`: add to `tree[i]`, then jump to `i + lowbit(i)` until past `n`.

```python
class FenwickTree:
    def __init__(self, size):
        self.n = size
        self.tree = [0] * (size + 1)                   # 1-based indexing

    @classmethod
    def from_list(cls, values):
        ft = cls(len(values))
        for i, v in enumerate(values):
            ft.add(i, v)
        return ft

    def add(self, index, delta):                       # add delta to values[index]
        i = index + 1
        while i <= self.n:
            self.tree[i] += delta
            i += i & -i                                # move to the next block that includes i

    def prefix_sum(self, index):                       # sum of values[0..index]
        i, total = index + 1, 0
        while i > 0:
            total += self.tree[i]
            i -= i & -i                                # drop the lowest set bit
        return total

    def range_sum(self, left, right):
        return self.prefix_sum(right) - (self.prefix_sum(left - 1) if left else 0)

fw = FenwickTree.from_list(sales)
print(fw.prefix_sum(7), fw.range_sum(2, 5))            # 36 23
fw.add(2, 12)                                          # increase value at index 2 by 12 (8 becomes 20)
print(fw.prefix_sum(7), fw.range_sum(2, 5))            # 48 35
```

Fenwick vs segment tree:

| | Fenwick | Segment tree |
|---|---------|--------------|
| Code size | about 10 lines | 30+ lines |
| Memory | `n` | `2n` |
| Operations | prefix sums and invertible operations (sum, xor) | any associative operation (min, max, gcd) |
| Speed | very fast constants | a bit slower |

Use a Fenwick tree for sums/counts, a segment tree when you need min/max or fancier combining.

### Counting inversions with a Fenwick tree

An **inversion** is a pair `i < j` with `a[i] > a[j]`: how out of order a list is. Counting them with two loops is `O(n²)`; a Fenwick tree does it in `O(n log n)`.

```python
def count_inversions(values):
    ranks = {v: r for r, v in enumerate(sorted(set(values)))}     # compress values to 0..m-1
    ft, inversions = FenwickTree(len(ranks)), 0
    for seen_so_far, v in enumerate(values):
        not_greater = ft.prefix_sum(ranks[v])                     # earlier items <= v
        inversions += seen_so_far - not_greater                   # the rest were larger and came earlier
        ft.add(ranks[v], 1)
    return inversions

print(count_inversions([2, 4, 1, 3, 5]), count_inversions([5, 4, 3, 2, 1]), count_inversions([1, 2, 3]))      # 3 10 0
```

## 4. Two real-world examples

**Example 1: Leaderboards and analytics.** "How many players have a score below mine?" is a prefix count: a Fenwick tree over score buckets answers it and handles new scores in `O(log n)`.

**Example 2: Range-aggregation in monitoring.** A time-series database answering "max CPU between 10:00 and 10:15" over millions of samples with live inserts uses segment-tree-like structures (or sparse tables for read-only data).

## 5. Common mistakes

- Off-by-one with inclusive versus exclusive ranges and 0-based versus 1-based indexing (the Fenwick tree is 1-based internally).
- A non-associative `combine` (for example "average of two averages").
- Using the wrong `identity` (`0` for sums, `inf` for min, `-inf` for max).
- Rebuilding the whole structure instead of updating one leaf.
- Reaching for these when prefix sums suffice (no updates) or when `n` is tiny.

## 6. Practice

1. Which structure would you pick for "range minimum with updates"? Why?
2. Build `SegmentTree` for gcd (`math.gcd`, identity `0`) and query `[12, 18, 24, 36]` for the range `0..2`.
3. Use a Fenwick tree to answer "how many of these ages are below 30?" for ages `[25, 31, 28, 40, 22]` (use age buckets 0..99).
4. What is `lowbit(12)`? Which blocks does `prefix_sum` visit for index 11 (1-based 12)?
5. With no updates at all, what is a simpler structure for range sums?

<details>
<summary>Solutions</summary>

1. A segment tree (min is not invertible, so Fenwick alone cannot answer arbitrary ranges).
2. ```python
   import math
   g = SegmentTree([12, 18, 24, 36], combine=math.gcd, identity=0)
   print(g.query(0, 2), g.query(0, 3))             # 6 6
   ```
3. ```python
   ages = FenwickTree(100)
   for a in [25, 31, 28, 40, 22]: ages.add(a, 1)
   print(ages.prefix_sum(29))                      # 3
   ```
4. `12 & -12 = 4`. Visits 12 (covers 9-12), then 8 (covers 1-8), then 0: two blocks.
5. A **prefix-sum array** (`O(1)` per query).

</details>

## 7. Check yourself

1. What does each node of a segment tree store?
2. What is the cost of query and update?
3. What does `i & -i` compute and why is it useful?
4. When must you choose a segment tree over a Fenwick tree?
5. Why test against a brute-force version?

<details>
<summary>Answers</summary>

1. The combined answer (sum, min, ...) for the range of positions below it.
2. `O(log n)` each (build is `O(n)`).
3. The lowest set bit, which is the length of the block that slot `i` covers.
4. When the operation is not invertible, like min, max or gcd.
5. It catches off-by-one and indexing mistakes immediately.

</details>

[Back to trees](README.md) · Previous: [balanced trees](03-balanced-trees-avl.md)
