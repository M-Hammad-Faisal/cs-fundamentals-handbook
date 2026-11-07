# Python Basics 4: Strings, Lists, Tuples, Dictionaries and Sets

**Prerequisites:** [functions](03-functions.md). **You will learn:** the built-in collection types, their most useful methods, indexing and slicing, comprehensions, and how to choose the right collection.

## 1. In plain words

Real programs handle **many values at once**: the letters of a word, the items of a cart, a user's profile, the unique visitors of a site. Python's built-in collections cover nearly every need:

| Type | Think of it as | Ordered | Mutable | Duplicates | Example |
|------|----------------|---------|---------|------------|---------|
| `str` | text | yes | no | yes | `"hello"` |
| `list` | a shopping list | yes | **yes** | yes | `[3, 1, 2]` |
| `tuple` | a fixed record | yes | no | yes | `(31.5, 74.3)` |
| `dict` | a phone book (name to number) | yes (insertion order) | **yes** | keys unique | `{"ana": 90}` |
| `set` | a bag of unique items | no | **yes** | no | `{1, 2, 3}` |

**Ordered** means items keep their position and can be reached by index. **Mutable** means you can change the collection after creating it.

## 2. Strings (`str`)

```python
s = "Hello, Python!"
print(len(s), s[0], s[-1], s[7:13], s[:5], s[::2], s[::-1])
# 14 H ! Python Hello Hlo yhn!        (the last: reversed string)
```

**Indexing and slicing** (works the same for lists and tuples): `s[i]` gets one item (counting from 0; negative counts from the end); `s[start:stop:step]` gets a slice (`stop` excluded).

```text
 H  e  l  l  o       s = "Hello"
 0  1  2  3  4       positive index
-5 -4 -3 -2 -1       negative index
s[1:4] = "ell"   s[:2] = "He"   s[3:] = "lo"   s[::-1] = "olleH"
```

Strings are **immutable**: methods return **new** strings.

```python
text = "  The quick brown fox  "
print(text.strip(), "|", text.lower().strip(), "|", text.upper())
print("a,b,c".split(","), " ".join(["x", "y", "z"]), "banana".replace("a", "o"), "banana".count("an"))
print("python".startswith("py"), "python".endswith("on"), "python".find("th"), "python".find("zz"), "abc".isalpha(), "123".isdigit())
print("title case words".title(), "Hello".swapcase(), "hello world".capitalize(), "a-b".partition("-"))
print("5".zfill(3), "ab".center(6, "*"), "tab\tseparated".expandtabs(4))

# f-strings, in-membership and comparisons
name, n = "Ana", 3
print(f"{name} has {n} items", "ell" in "Hello", "apple" < "banana")

# Strings are sequences: you can loop over them
print([ch for ch in "abc"], sorted("banana"), len(set("banana")))      # ['a', 'b', 'c'] ['a', 'a', 'a', 'b', 'n', 'n'] 3
```

Escape sequences: `\n` newline, `\t` tab, `\\` backslash, `\"` quote. Raw strings (`r"C:\new"`) ignore escapes. Multi-line: triple quotes. See [Unicode and encodings](../computer-basics/binary-and-data-representation.md).

## 3. Lists: the workhorse

```python
nums = [5, 2, 9, 1]
nums.append(7)                    # add to the end
nums.insert(0, 100)               # insert at an index (slow for big lists: shifts everything)
nums.extend([3, 3])               # add many
print(nums)                       # [100, 5, 2, 9, 1, 7, 3, 3]

nums.remove(3)                    # remove the FIRST item equal to 3
last = nums.pop()                 # remove and return the last item (pop(0) removes the first)
del nums[0]                       # delete by index
print(nums, last)                 # [5, 2, 9, 1, 7] 3

nums.sort()                       # sort IN PLACE (returns None)
print(nums, sorted(nums, reverse=True), nums[::-1])    # [1, 2, 5, 7, 9] [9, 7, 5, 2, 1] [9, 7, 5, 2, 1]
print(len(nums), min(nums), max(nums), sum(nums), nums.index(5), nums.count(2), 7 in nums)    # 5 1 9 24 2 1 True
```

### Slicing, copying and nesting

```python
a = [1, 2, 3, 4, 5]
print(a[1:3], a[:2], a[-2:], a[::2])          # [2, 3] [1, 2] [4, 5] [1, 3, 5]
a[1:3] = [20, 30, 40]                          # replace a slice (the size may change)
print(a)                                       # [1, 20, 30, 40, 4, 5]

b = a                                          # NOT a copy: another name for the same list
c = a[:]                                       # a shallow copy (also a.copy() or list(a))
b.append("x")
print(a, c)                                    # [1, 20, 30, 40, 4, 5, 'x'] [1, 20, 30, 40, 4, 5]

grid = [[0] * 3 for _ in range(2)]             # a 2 x 3 grid; ALWAYS build rows separately
grid[0][1] = 9
print(grid)                                    # [[0, 9, 0], [0, 0, 0]]
wrong = [[0] * 3] * 2                          # BUG: both rows are the SAME list
wrong[0][1] = 9
print(wrong)                                   # [[0, 9, 0], [0, 9, 0]]
```

### List comprehensions: build a list in one line

```python
squares = [n * n for n in range(1, 6)]                           # [1, 4, 9, 16, 25]
evens = [n for n in range(10) if n % 2 == 0]                     # [0, 2, 4, 6, 8]
pairs = [(x, y) for x in range(3) for y in range(x)]             # [(1, 0), (2, 0), (2, 1)]
words = ["apple", "Bob", "cat"]
print(squares, evens, pairs, [w.upper() for w in words if len(w) > 2])
# [1, 4, 9, 16, 25] [0, 2, 4, 6, 8] [(1, 0), (2, 0), (2, 1)] ['APPLE', 'BOB', 'CAT']
```

Pattern: `[expression for item in iterable if condition]`. More: [generators and comprehensions](../../08-modern-python/generators-functional/README.md).

### Costs (see [Big-O](../../01-complexity/big-o/README.md))

`append` and `pop()` from the end are fast (O(1)); `insert(0, x)`, `pop(0)` and `x in my_list` are O(n). For many front operations use `collections.deque`; for fast membership use a `set`.

## 4. Tuples: fixed records

```python
point = (3, 4)
x, y = point                                  # unpacking
print(point[0], len(point), point + (5,), point * 2)       # 3 2 (3, 4, 5) (3, 4, 3, 4)
single = (7,)                                 # note the comma: (7) is just the number 7
print(type(single), type((7)))                # <class 'tuple'> <class 'int'>

def min_max(items):
    return min(items), max(items)             # functions return tuples to give back several values
low, high = min_max([4, 1, 9])
first, *rest = [1, 2, 3, 4]                   # star unpacking
print(low, high, first, rest)                 # 1 9 1 [2, 3, 4]
```

Use a tuple for data that should not change (coordinates, RGB colors, database rows) and as **dictionary keys** (lists cannot be keys). Tuples are slightly faster and smaller than lists. For named fields use `NamedTuple` or a [dataclass](../../08-modern-python/dataclasses-enums/README.md).

## 5. Dictionaries: key to value

```python
person = {"name": "Ayesha", "age": 21, "city": "Lahore"}
print(person["name"], person.get("email"), person.get("email", "none"))        # Ayesha None none
person["email"] = "a@example.com"             # add or update
person["age"] += 1
del person["city"]
print(person)                                 # {'name': 'Ayesha', 'age': 22, 'email': 'a@example.com'}
print("age" in person, len(person), list(person.keys()), list(person.values()))

for key, value in person.items():             # loop over pairs
    print(f"{key} -> {value}")

try:
    person["phone"]
except KeyError as error:
    print("KeyError:", error)                 # KeyError: 'phone'    (use .get() or `in` to avoid it)
```

Keys must be **hashable** (immutable: strings, numbers, tuples); lookup is **O(1) on average** because dictionaries are [hash tables](../../02-data-structures/hash-tables/README.md). Dictionaries keep **insertion order**.

### Counting and grouping (very common patterns)

```python
from collections import Counter, defaultdict

text = "the cat and the hat and the bat"
counts = {}
for word in text.split():
    counts[word] = counts.get(word, 0) + 1      # count with get()
print(counts)                                   # {'the': 3, 'cat': 1, 'and': 2, 'hat': 1, 'bat': 1}
print(Counter(text.split()).most_common(2))     # [('the', 3), ('and', 2)]

groups = defaultdict(list)                       # a dict that creates missing values automatically
for word in text.split():
    groups[len(word)].append(word)
print(dict(groups))                              # {3: ['the', 'cat', 'and', 'the', 'hat', 'and', 'the', 'bat']}

squares = {n: n * n for n in range(5)}           # dictionary comprehension
inverse = {v: k for k, v in squares.items()}
merged = {**{"a": 1}, **{"b": 2}} | {"c": 3}     # merge dictionaries
print(squares, inverse, merged)
```

Dictionaries nest naturally to model real data (this is JSON):

```python
import json
user = {"id": 1, "name": "Bo", "roles": ["admin", "dev"], "address": {"city": "Karachi", "zip": "75500"}}
print(user["address"]["city"], user["roles"][0])           # Karachi admin
text = json.dumps(user)
print(json.loads(text) == user)                            # True   (convert to/from JSON text)
```

## 6. Sets: unique items and fast membership

```python
a = {1, 2, 3, 3, 2}
print(a, len(a), 2 in a)                       # {1, 2, 3} 3 True    (duplicates removed)
a.add(10); a.discard(1); print(sorted(a))      # [2, 3, 10]

x, y = {1, 2, 3, 4}, {3, 4, 5}
print(x | y, x & y, x - y, x ^ y)              # {1, 2, 3, 4, 5} {3, 4} {1, 2} {1, 2, 5}
print(list(set([3, 1, 3, 2, 1])), len(set("mississippi")))      # [1, 2, 3] 4       (dedupe a list)
empty_set, empty_dict = set(), {}              # careful: {} is an empty DICT, set() is an empty set
```

Sets are unordered (no indexing) and hold hashable items only. Use them to remove duplicates, test membership fast, and compare groups ([set operations](../math-for-cs/logic-sets-proofs.md)).

## 7. Choosing the right collection

| I need... | Use |
|-----------|-----|
| An ordered, changeable sequence | `list` |
| A fixed record / dictionary key / multiple return values | `tuple` |
| Look up by name/ID, count things, group things | `dict` |
| Unique items, fast "is it in there?", set math | `set` |
| A queue with fast pops at both ends | `collections.deque` |
| Sorted order with fast insertion | keep a list sorted with `bisect`, or a heap (`heapq`) |
| Text | `str` |

## 8. Putting it together: word frequency

```python
text = """It was the best of times, it was the worst of times,
it was the age of wisdom, it was the age of foolishness"""

words = [w.strip(",.").lower() for w in text.split()]
frequency = {}
for word in words:
    frequency[word] = frequency.get(word, 0) + 1

top = sorted(frequency.items(), key=lambda pair: (-pair[1], pair[0]))[:3]
print(top)                                       # [('it', 4), ('was', 4), ('of', 4)]
print(len(words), len(set(words)))               # 23 11   (total words and unique words)
```

## 9. Two real-world examples

**Example 1: Shopping cart.** A cart is a list of dictionaries (`[{"sku": "pen", "qty": 2, "price": 150}, ...]`). The total is a comprehension: `sum(i["qty"] * i["price"] for i in cart)`. A `Counter` of SKUs finds best sellers; a `set` of SKUs checks which items are already purchased.

**Example 2: Parsing a log file.** Read each line (a string), `split()` it into fields, store entries in a list of tuples, count errors per hour in a `defaultdict(int)`, collect distinct IP addresses in a `set`. Strings, lists, tuples, dicts and sets all work together in a ten-line script.

## 10. Common mistakes

- Thinking `b = a` copies a list (it does not: use `a.copy()` or `a[:]`).
- `[[0] * 3] * 2` (rows share one list).
- Modifying a list while iterating over it; use a comprehension or iterate over a copy.
- `list.sort()` returns `None` (`nums = nums.sort()` destroys your list); use `sorted(nums)` for a new list.
- `KeyError`: use `.get()` or `in` for missing keys.
- `{}` is an empty dict, not an empty set.
- Using a list or dict as a dictionary key or set member (unhashable).
- Off-by-one slicing: `s[1:3]` has 2 characters (stop is excluded).

## 11. Practice

1. Reverse each word in `"python is fun"` but keep the word order.
2. Find the three most common letters in a sentence (ignore spaces and case).
3. Given two lists, return the items that are in both without duplicates; the items in only one.
4. Group a list of words by their first letter into a dictionary of lists.
5. Remove duplicates from a list while preserving order.
6. Check if two strings are anagrams.
7. Rotate a list left by `k` positions with slicing.
8. Given a list of `(name, score)` tuples, print them sorted by score descending, then name.

<details>
<summary>Solutions</summary>

**1.**
```python
print(" ".join(word[::-1] for word in "python is fun".split()))     # nohtyp si nuf
```

**2.**
```python
from collections import Counter
sentence = "Hello World, hello Python"
letters = [c for c in sentence.lower() if c.isalpha()]
print(Counter(letters).most_common(3))               # [('l', 5), ('o', 4), ('h', 3)]
```

**3.**
```python
a, b = [1, 2, 2, 3, 4], [3, 4, 4, 5]
print(sorted(set(a) & set(b)), sorted(set(a) ^ set(b)))        # [3, 4] [1, 2, 5]
```

**4.**
```python
groups = {}
for word in ["apple", "avocado", "banana", "blueberry", "cherry"]:
    groups.setdefault(word[0], []).append(word)
print(groups)       # {'a': ['apple', 'avocado'], 'b': ['banana', 'blueberry'], 'c': ['cherry']}
```

**5.**
```python
items = [3, 1, 3, 2, 1, 4]
print(list(dict.fromkeys(items)))                    # [3, 1, 2, 4]   (dicts keep insertion order)
```

**6.**
```python
def is_anagram(a, b):
    return sorted(a.replace(" ", "").lower()) == sorted(b.replace(" ", "").lower())
print(is_anagram("Listen", "Silent"), is_anagram("abc", "abd"))     # True False
```

**7.**
```python
def rotate_left(items, k):
    k %= len(items) or 1
    return items[k:] + items[:k]
print(rotate_left([1, 2, 3, 4, 5], 2))               # [3, 4, 5, 1, 2]
```

**8.**
```python
scores = [("ana", 90), ("bo", 85), ("cy", 90)]
for name, score in sorted(scores, key=lambda t: (-t[1], t[0])):
    print(name, score)                               # ana 90 / cy 90 / bo 85
```

</details>

## 12. Check yourself

1. What is the difference between a list and a tuple?
2. What does `s[1:4]` return for `s = "Python"`?
3. How do you safely read a dictionary key that might be missing?
4. How do you remove duplicates from a list?
5. Why is `x in my_set` faster than `x in my_list`?
6. What is wrong with `nums = nums.sort()`?

<details>
<summary>Answers</summary>

1. A list is mutable; a tuple is immutable (and hashable if its contents are).
2. `"yth"` (indices 1, 2, 3).
3. `d.get(key, default)` or test with `key in d`.
4. `list(set(items))` (order not kept) or `list(dict.fromkeys(items))` (order kept).
5. A set uses hashing (O(1) average); a list scans every item (O(n)).
6. `sort()` sorts in place and returns `None`, so `nums` becomes `None`.

</details>

[Back to Python fundamentals](README.md) · Previous: [functions](03-functions.md) · Next: [files, modules and errors](05-files-modules-errors.md)
