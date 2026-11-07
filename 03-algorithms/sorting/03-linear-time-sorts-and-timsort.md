# Linear-Time Sorts, Timsort and Choosing a Sort

**Prerequisites:** [merge sort and quicksort](02-merge-sort-and-quicksort.md). **You will learn:** how **counting sort**, **radix sort** and **bucket sort** beat the `n log n` limit by *not comparing*, what **Timsort** (Python's built-in) does, and a decision guide for choosing a sorting method.

## 1. Breaking the speed limit (with a condition)

The `n log n` lower bound applies to algorithms that only **compare** items. If the keys are **small integers** (or can be turned into them), we can use the value itself as an array index and sort in **`O(n + k)`** time, where `k` is the range of values.

## 2. Counting sort

Count how many times each value appears, then write the values out in order.

```text
data = [4, 2, 2, 8, 3, 3, 1]       range 0..8
counts: index 1:1  2:2  3:2  4:1  8:1
output: 1, 2, 2, 3, 3, 4, 8
```

```python
def counting_sort(a, max_value):
    counts = [0] * (max_value + 1)
    for x in a:
        counts[x] += 1                                    # one pass to count
    result = []
    for value, c in enumerate(counts):
        result.extend([value] * c)                        # one pass over the range to write
    return result

print(counting_sort([4, 2, 2, 8, 3, 3, 1], 8))            # [1, 2, 2, 3, 3, 4, 8]
```

That version loses the identity of items with equal keys. To sort **records** by a small integer key and stay **stable**, use prefix sums to compute each key's final position:

```python
def counting_sort_by_key(items, key, max_key):
    counts = [0] * (max_key + 2)
    for item in items:
        counts[key(item) + 1] += 1
    for i in range(1, len(counts)):
        counts[i] += counts[i - 1]                        # counts[k] = how many items have a smaller key = start index of key k
    output = [None] * len(items)
    for item in items:                                    # left to right keeps equal keys in original order (stable)
        output[counts[key(item)]] = item
        counts[key(item)] += 1
    return output

students = [("Zoya", 3), ("Ali", 1), ("Bilal", 3), ("Dina", 2), ("Eman", 1)]       # (name, grade 0..5)
print(counting_sort_by_key(students, key=lambda s: s[1], max_key=5))
# [('Ali', 1), ('Eman', 1), ('Dina', 2), ('Zoya', 3), ('Bilal', 3)]
```

**Cost:** time `O(n + k)`, space `O(n + k)`. Great when `k` is small (ages 0-120, grades, bytes 0-255); terrible when `k` is huge (sorting 100 numbers up to a billion would allocate a billion slots).

## 3. Radix sort

Sort numbers **digit by digit**, from the least significant digit to the most, using a **stable** sort (counting sort) on each digit. Because each pass is stable, the earlier ordering survives.

```text
[170, 45, 75, 90, 802, 24, 2, 66]
 by ones digit:     [170, 90, 802, 2, 24, 45, 75, 66]
 by tens digit:     [802, 2, 24, 45, 66, 170, 75, 90]
 by hundreds digit: [2, 24, 45, 66, 75, 90, 170, 802]
```

```python
def radix_sort(a):
    if not a:
        return []
    a = list(a)
    place, biggest = 1, max(a)
    passes = 0
    while biggest // place > 0:
        a = counting_sort_by_key(a, key=lambda x: (x // place) % 10, max_key=9)
        place *= 10
        passes += 1
    print("passes:", passes)
    return a

print(radix_sort([170, 45, 75, 90, 802, 24, 2, 66]))      # [2, 24, 45, 66, 75, 90, 170, 802]    (passes: 3)
```

**Cost:** `O(d · (n + b))` for `d` digits in base `b`: effectively linear when numbers have a bounded number of digits. Used for sorting fixed-width keys (IDs, IP addresses, timestamps, fixed-length strings).

## 4. Bucket sort

Spread items into buckets by value range, sort each small bucket, then concatenate. Excellent when data is **uniformly distributed** (for example numbers in `[0, 1)`).

```python
def bucket_sort(a, buckets=10):                           # values assumed in [0, 1)
    bins = [[] for _ in range(buckets)]
    for x in a:
        bins[int(x * buckets)].append(x)                  # the bucket index comes straight from the value
    result = []
    for b in bins:
        result.extend(sorted(b))                          # each bucket is tiny, so any sort is fast
    return result

print(bucket_sort([0.78, 0.17, 0.39, 0.26, 0.72, 0.94, 0.21, 0.12, 0.23, 0.68]))
# [0.12, 0.17, 0.21, 0.23, 0.26, 0.39, 0.68, 0.72, 0.78, 0.94]
```

Average `O(n)` on uniform data; `O(n²)` (or `n log n` with a good inner sort) if everything lands in one bucket.

## 5. A race: linear versus comparison

```python
import random, time

random.seed(8)
data = [random.randrange(100) for _ in range(500_000)]     # small range: ideal for counting sort
t = time.perf_counter(); counting_sort(data, 99); counting_time = time.perf_counter() - t
t = time.perf_counter(); sorted(data); builtin_time = time.perf_counter() - t
print(counting_sort(data, 99) == sorted(data))             # True
print(counting_time < 2 * builtin_time)                    # True   (comparable speed even in pure Python)
```

(The built-in is implemented in C, so a pure-Python counting sort doing similar work at the same order of magnitude shows how strong the linear algorithm is.)

## 6. Timsort: what Python actually uses

Real-world data is rarely random: it often contains **runs** (stretches already ascending or descending). **Timsort** (Tim Peters, 2002, used by Python, Java objects, Android, Swift) exploits this:

1. Scan for natural **runs**; reverse descending runs; extend short runs to a minimum length using **insertion sort** (fast on small chunks).
2. **Merge** adjacent runs with a stack of rules that keep merges balanced, using a technique called **galloping** to skip over long stretches.

Results:

| Input | Timsort time |
|-------|--------------|
| Random | `O(n log n)` |
| Already sorted or reversed | **`O(n)`** |
| Sorted blocks appended together | close to `O(n)` |
| Stability | **stable** |
| Extra space | up to `O(n)` |

```python
import timeit

n = 200_000
random.seed(2)
shuffled = random.sample(range(n), n)
ascending = list(range(n))
two_runs = sorted(random.sample(range(n), n // 2)) + sorted(random.sample(range(n), n // 2))
for label, data in [("random", shuffled), ("sorted", ascending), ("two sorted runs", two_runs)]:
    seconds = timeit.timeit(lambda: sorted(data), number=3) / 3
    print(f"{label:16}{seconds * 1000:7.1f} ms")
# random             26.4 ms   (one run; numbers vary by machine)
# sorted              0.9 ms
# two sorted runs     2.2 ms
```

The sorted input is dramatically faster because Timsort notices a single run and does one pass.

## 7. How to choose a sort

| Situation | Choose |
|-----------|--------|
| Normal Python code | **`sorted()` / `list.sort()`** |
| Need a custom order | `key=` function |
| Tiny array or nearly sorted | insertion sort (or just the built-in) |
| Small integer keys | counting sort |
| Fixed-width keys (IDs, strings of equal length) | radix sort |
| Uniform floats | bucket sort |
| Must be stable and you control the code | merge sort |
| Linked list | merge sort |
| Data larger than memory | external merge sort |
| Only the top k or the median | heap or quickselect, not a full sort |
| Strict memory limit and a guaranteed worst case | heapsort |

## 8. Two real-world examples

**Example 1: Sorting a billion ages.** Ages fall in 0-120, so counting sort does one pass of counting and then writes the output: `O(n)` with 121 counters, far faster than `n log n`.

**Example 2: Sorting IPv4 addresses or phone numbers.** Fixed-width keys are ideal for radix sort: four passes of one byte each sort any number of IPv4 addresses.

## 9. Common mistakes

- Using counting sort when the key range is enormous.
- Forgetting that counting sort on bare values loses the associated records; use the prefix-sum version for records.
- Processing digits from the most significant first in a simple radix sort (use LSD, least significant digit first, with a stable inner sort).
- Hand-writing a sort in production when `sorted` is faster and correct.
- Calling `.sort()` and printing the result (`None`).
- Assuming `sorted` is slow: it is `O(n)` on sorted input.

## 10. Practice

1. Counting-sort `[3, 0, 2, 3, 1]` by hand.
2. Why must radix sort's per-digit sort be stable?
3. Which of these suit counting sort: exam scores 0-100, 64-bit random IDs, letters a-z, floating-point prices?
4. Sort the strings `["dab", "cab", "fad", "bad"]` using radix sort, from the last letter to the first (LSD).
5. Why is Timsort fast on a log file that is "mostly in time order"?
6. Write `sort_by_frequency(s)` that orders characters by how often they appear, most frequent first.

<details>
<summary>Solutions</summary>

1. Counts for 0..3: `[1, 1, 1, 2]`, so the output is `[0, 1, 2, 3, 3]`.
2. Each pass must preserve the order established by the previous (less significant) digits among items with equal current digits; an unstable pass would destroy it.
3. Exam scores (range 101) and letters (26): yes. 64-bit IDs (range `2^64`): no. Floats: not directly (convert to cents first, then maybe).
4. ```python
   words = ["dab", "cab", "fad", "bad"]
   for pos in (2, 1, 0):
       words = sorted(words, key=lambda w: w[pos])        # sorted is stable
   print(words)                                           # ['bad', 'cab', 'dab', 'fad']
   ```
5. Long ascending runs are detected and merged in about one pass; only the few out-of-place items cost extra work.
6. ```python
   from collections import Counter
   def sort_by_frequency(s):
       counts = Counter(s)
       return "".join(sorted(s, key=lambda ch: (-counts[ch], ch)))
   print(sort_by_frequency("tree"))                       # eert
   ```

</details>

## 11. Check yourself

1. How can counting sort beat `n log n`?
2. When is counting sort a bad idea?
3. What is radix sort's strategy?
4. What is a "run" in Timsort and why does it help?
5. What should you use for sorting in everyday Python?

<details>
<summary>Answers</summary>

1. It uses the key as an array index instead of comparing, so the comparison lower bound does not apply.
2. When the range of key values is huge compared with the number of items.
3. Stably sort by each digit from least to most significant.
4. A stretch that is already sorted; Timsort merges runs instead of re-sorting them, so partly ordered data is fast.
5. `sorted()` / `list.sort()` with a `key=` when needed.

</details>

[Back to sorting](README.md) · Previous: [merge sort and quicksort](02-merge-sort-and-quicksort.md)
