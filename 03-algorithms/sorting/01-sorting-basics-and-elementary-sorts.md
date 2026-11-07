# Sorting Basics and the Elementary Sorts

**Prerequisites:** [counting steps and growth](../../01-complexity/02-counting-steps-and-growth.md), [arrays](../../02-data-structures/arrays-strings/01-arrays-and-memory.md), [analyzing loops](../../01-complexity/04-analyzing-loops-and-recursion.md). **You will learn:** what sorting is and the vocabulary around it (**stable**, **in-place**, **comparison sort**), and three simple sorts you can write in minutes: **bubble**, **selection** and **insertion** sort, with traces, comparison counts, and when the humble insertion sort is actually the best choice.

## 1. In plain words

Sorting puts items in order: names A to Z, prices low to high, messages newest first. Almost everything else gets easier on sorted data: **binary search** becomes possible, duplicates sit next to each other, and "top 10" is the first 10 items.

Analogy: sorting a hand of playing cards. Most people **pick up one card at a time and slide it into place among the cards already held**. That is **insertion sort**.

## 2. Vocabulary

| Term | Meaning |
|------|---------|
| **Comparison sort** | decides order only by comparing two items (`a < b`) |
| **In-place** | uses `O(1)` extra memory beyond the input |
| **Stable** | items with **equal keys keep their original relative order** |
| **Adaptive** | runs faster when the input is already nearly sorted |
| **Inversion** | a pair out of order (`i < j` but `a[i] > a[j]`); sorting must remove all of them |

**Why stability matters.** Sort people by name, then **stably** by city: within each city the names stay alphabetical. An unstable sort would scramble them.

```python
people = [("Zoya", "Lahore"), ("Ali", "Karachi"), ("Bilal", "Lahore"), ("Dina", "Karachi")]
by_name = sorted(people)                                  # sort by name first
by_city = sorted(by_name, key=lambda p: p[1])             # then by city: Python's sort is stable
print(by_city)
# [('Ali', 'Karachi'), ('Dina', 'Karachi'), ('Bilal', 'Lahore'), ('Zoya', 'Lahore')]
```

**A lower bound.** With `n` items there are `n!` possible orderings, and each comparison halves the possibilities at best, so any comparison sort needs at least `log₂(n!)`, about `n log₂ n`, comparisons. So `O(n log n)` is the best a comparison sort can ever do; [counting and radix sort](03-linear-time-sorts-and-timsort.md) beat it only by not comparing.

## 3. Bubble sort

**Idea:** sweep through the list swapping neighbors that are out of order. After each sweep, the largest remaining item has "bubbled" to the end.

```text
[5, 2, 4, 1]
 pass 1: 5>2 swap [2,5,4,1]  5>4 swap [2,4,5,1]  5>1 swap [2,4,1,5]   5 is in place
 pass 2: 2<4 ok    4>1 swap [2,1,4,5]                                    4 is in place
 pass 3: 2>1 swap [1,2,4,5]                                              sorted
```

```python
def bubble_sort(a):
    a = list(a)                                           # work on a copy
    comparisons = 0
    for end in range(len(a) - 1, 0, -1):
        swapped = False
        for i in range(end):
            comparisons += 1
            if a[i] > a[i + 1]:
                a[i], a[i + 1] = a[i + 1], a[i]
                swapped = True
        if not swapped:                                   # a full pass with no swap: already sorted, stop early
            break
    return a, comparisons

print(bubble_sort([5, 2, 4, 1]))                          # ([1, 2, 4, 5], 6)
print(bubble_sort([1, 2, 3, 4, 5]))                       # ([1, 2, 3, 4, 5], 4)    (already sorted: one pass)
```

Cost: **`O(n²)`** worst and average (about `n²/2` comparisons), **`O(n)`** best case with the early exit. Stable, in place. Bubble sort is mainly a teaching tool.

## 4. Selection sort

**Idea:** repeatedly **select the smallest** remaining item and put it at the front.

```text
[5, 2, 4, 1]
 find min of all (1) swap with index 0:  [1, 2, 4, 5]
 find min of rest (2) already at index 1
 find min of rest (4) already at index 2     sorted
```

```python
def selection_sort(a):
    a = list(a)
    comparisons = swaps = 0
    for i in range(len(a) - 1):
        smallest = i
        for j in range(i + 1, len(a)):
            comparisons += 1
            if a[j] < a[smallest]:
                smallest = j
        if smallest != i:
            a[i], a[smallest] = a[smallest], a[i]
            swaps += 1
    return a, comparisons, swaps

print(selection_sort([5, 2, 4, 1]))                       # ([1, 2, 4, 5], 6, 1)
print(selection_sort([1, 2, 3, 4, 5]))                    # ([1, 2, 3, 4, 5], 10, 0)
```

Cost: **always `n(n-1)/2` comparisons**, even if already sorted (not adaptive), but at most `n - 1` **swaps**. That makes it useful only when writes are very expensive. In place, but **not stable** (the long-distance swap can jump an item over an equal one).

## 5. Insertion sort

**Idea:** keep a sorted prefix; take the next item and **shift larger items right** until it fits.

```text
[5, 2, 4, 1]       sorted prefix | rest
 [5 | 2, 4, 1]     insert 2: shift 5 right          [2, 5 | 4, 1]
 [2, 5 | 4, 1]     insert 4: shift 5 right          [2, 4, 5 | 1]
 [2, 4, 5 | 1]     insert 1: shift 5, 4, 2 right    [1, 2, 4, 5]
```

```python
def insertion_sort(a):
    a = list(a)
    comparisons = 0
    for i in range(1, len(a)):
        item = a[i]
        j = i - 1
        while j >= 0:
            comparisons += 1
            if a[j] > item:
                a[j + 1] = a[j]                           # shift right
                j -= 1
            else:
                break
        a[j + 1] = item                                   # drop the item into the gap
    return a, comparisons

print(insertion_sort([5, 2, 4, 1]))                       # ([1, 2, 4, 5], 6)
print(insertion_sort([1, 2, 3, 4, 5]))                    # ([1, 2, 3, 4, 5], 4)
print(insertion_sort([5, 4, 3, 2, 1]))                    # ([1, 2, 3, 4, 5], 10)
```

Cost: **`O(n²)`** worst case (reverse order), but **`O(n)` on sorted input**, and about `n + (number of inversions)` in general: it is **adaptive**. In place and **stable**.

## 6. Measuring all three

```python
import random

random.seed(4)
for label, data in [("random", random.sample(range(1000), 200)),
                    ("sorted", list(range(200))),
                    ("reversed", list(range(200, 0, -1))),
                    ("nearly sorted", sorted(random.sample(range(1000), 200)))]:
    if label == "nearly sorted":
        data[10], data[11] = data[11], data[10]            # one swap away from sorted
    print(f"{label:14} bubble={bubble_sort(data)[1]:6}  selection={selection_sort(data)[1]:6}  insertion={insertion_sort(data)[1]:6}")
# random         bubble= 19864  selection= 19900  insertion= 10220
# sorted         bubble=   199  selection= 19900  insertion=   199
# reversed       bubble= 19900  selection= 19900  insertion= 19900
# nearly sorted  bubble=   397  selection= 19900  insertion=   200
```

(The random row depends on the seed.) The pattern to remember:

| Algorithm | Best | Average | Worst | Stable | In-place | Swaps/writes |
|-----------|------|---------|-------|--------|----------|--------------|
| Bubble | `O(n)` | `O(n²)` | `O(n²)` | yes | yes | many |
| Selection | `O(n²)` | `O(n²)` | `O(n²)` | no | yes | **at most n - 1** |
| **Insertion** | `O(n)` | `O(n²)` | `O(n²)` | yes | yes | up to `O(n²)` shifts |

## 7. When is insertion sort the right answer?

- **Small arrays** (roughly under 20-60 items): the low overhead beats fancier algorithms. Python's built-in `sorted` and many library quicksorts switch to insertion sort for tiny chunks.
- **Nearly sorted data**: a log file that is almost in time order, or adding one new item to a sorted list.
- **Online sorting**: items arrive one at a time and you keep the list sorted.

```python
import bisect

online = []
for x in [7, 3, 9, 1]:
    bisect.insort(online, x)                              # keeps `online` sorted: binary search + one shift
print(online)                                             # [1, 3, 7, 9]
```

Everywhere else you want an `O(n log n)` algorithm: [merge sort and quicksort](02-merge-sort-and-quicksort.md) next.

## 8. Using Python's sort

You almost never write your own sort in production: `sorted()` and `list.sort()` use **Timsort** (stable, `O(n log n)`, `O(n)` on sorted runs).

```python
words = ["banana", "Apple", "cherry", "apple"]
print(sorted(words))                                      # ['Apple', 'apple', 'banana', 'cherry']   (uppercase sorts before lowercase)
print(sorted(words, key=str.lower))                       # ['Apple', 'apple', 'banana', 'cherry']   (stable: 'Apple' stays before 'apple')
print(sorted(words, key=len, reverse=True))               # ['banana', 'cherry', 'Apple', 'apple']
records = [{"n": "a", "age": 30}, {"n": "b", "age": 25}]
print([r["n"] for r in sorted(records, key=lambda r: r["age"])])      # ['b', 'a']
```

`key=` computes one value per item (cheap and clear); the old `cmp=` style is gone (use `functools.cmp_to_key` if you must).

## 9. Two real-world examples

**Example 1: Spreadsheet column sort.** Sorting by "Region" then "Sales" relies on a **stable** sort: sort by the secondary key first, then the primary, and ties stay in the earlier order.

**Example 2: Maintaining a leaderboard.** A new score arrives: insert it into the already-sorted list (insertion-sort's inner step, `O(n)` shifts or `O(log n)` with a tree) instead of re-sorting everything.

## 10. Common mistakes

- Sorting a list in place when you meant to keep the original (`a.sort()` returns `None`; use `sorted(a)` for a copy).
- Assuming a sort is stable when it is not (selection sort, heapsort, quicksort).
- Off-by-one in the inner loop bounds (`range(len(a) - 1)` versus `range(len(a))`).
- Comparing mixed types (`3 < "a"` raises `TypeError`).
- Using an `O(n²)` sort on large inputs (a million items would take about `10^12` steps).
- Forgetting the early-exit flag in bubble sort.

## 11. Practice

1. Trace insertion sort on `[3, 1, 2]`, writing the list after each insertion.
2. How many comparisons does selection sort use on 100 items?
3. Which of the three is fastest on `[1, 2, 3, 4, 6, 5]`? How many comparisons for insertion sort?
4. Show an input where selection sort is not stable.
5. Sort `["bb", "a", "cc", "d"]` by length, keeping original order among equal lengths (two lines).
6. How many inversions does `[3, 1, 2]` have? What about a reversed list of 10 items?
7. Write `insertion_sort_desc` that sorts descending.

<details>
<summary>Solutions</summary>

1. Start `[3, 1, 2]`. Insert 1: `[1, 3, 2]`. Insert 2: `[1, 2, 3]`.
2. `100 * 99 / 2 = 4950`.
3. Insertion sort: only one inversion, so it needs about `n + 1` comparisons.
   ```python
   print(insertion_sort([1, 2, 3, 4, 6, 5]))             # ([1, 2, 3, 4, 5, 6], 6)
   ```
4. `[2a, 2b, 1]`: selection swaps `2a` with `1`, giving `[1, 2b, 2a]`: the two 2s changed order.
   ```python
   def selection_sort_by(items, key):
       items = list(items)
       for i in range(len(items) - 1):
           smallest = min(range(i, len(items)), key=lambda j: key(items[j]))
           items[i], items[smallest] = items[smallest], items[i]
       return items
   print(selection_sort_by(["2a", "2b", "1c"], key=lambda s: s[0]))      # ['1c', '2b', '2a']   (2a and 2b swapped order)
   ```
5. ```python
   print(sorted(["bb", "a", "cc", "d"], key=len))        # ['a', 'd', 'bb', 'cc']
   ```
6. `[3, 1, 2]` has 2 inversions (3>1, 3>2). A reversed list of 10 has `10 * 9 / 2 = 45`.
7. ```python
   def insertion_sort_desc(a):
       a = list(a)
       for i in range(1, len(a)):
           item, j = a[i], i - 1
           while j >= 0 and a[j] < item:                 # only the comparison flips
               a[j + 1] = a[j]; j -= 1
           a[j + 1] = item
       return a
   print(insertion_sort_desc([3, 1, 4, 2]))              # [4, 3, 2, 1]
   ```

</details>

## 12. Check yourself

1. What does "stable" mean and why does it matter?
2. Which elementary sort does the fewest swaps?
3. Which one is adaptive, and what is its best case?
4. What is the best possible time of any comparison sort?
5. When would you actually use insertion sort?

<details>
<summary>Answers</summary>

1. Equal items keep their original order, which makes multi-key sorting by successive sorts work.
2. Selection sort (at most `n - 1` swaps).
3. Insertion sort (and bubble sort with the early exit); best case `O(n)` on sorted input.
4. `O(n log n)` comparisons.
5. For small or nearly sorted inputs, or for inserting items one at a time into a sorted list.

</details>

[Back to sorting](README.md) · Next: [merge sort and quicksort](02-merge-sort-and-quicksort.md)
