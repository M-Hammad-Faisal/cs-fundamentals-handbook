# Hash Functions and Collisions

**Prerequisites:** [arrays and memory](../arrays-strings/01-arrays-and-memory.md) (indexing is `O(1)`), [exponents and logarithms](../../00-foundations/math-for-cs/exponents-and-logarithms.md). **You will learn:** what a hash function is, what makes one good, why **collisions** are unavoidable, the **birthday paradox**, and the **load factor**.

## 1. In plain words

An array finds item number 7 instantly because the address is `start + 7 * size`. But what if you want to find the item named `"alice"`? A **hash table** turns the *key* into an array index with a **hash function**, so lookup by name is as fast as lookup by number.

Analogy: a coat check. You hand over your coat and get ticket **#42**; the coat hangs on hook 42. To retrieve it you do not search every hook; you go straight to 42. A hash function is the machine that invents the ticket number from the coat (the key).

## 2. What a hash function must do

1. **Deterministic:** the same key always gives the same number (within one run).
2. **Fast:** much cheaper than searching.
3. **Uniform:** keys spread evenly across the slots, so no slot gets crowded.
4. Equal keys must have equal hashes (`a == b` implies `hash(a) == hash(b)`).

The index is `hash(key) % table_size`.

```python
def bad_hash(key):                 # sum of character codes
    return sum(ord(c) for c in key)

def better_hash(key):              # polynomial rolling hash (like Java's String.hashCode)
    h = 0
    for c in key:
        h = (h * 31 + ord(c)) % (2**32)
    return h

for word in ["stop", "pots", "tops", "spot"]:                  # anagrams of each other
    print(word, bad_hash(word), better_hash(word))
# stop 454 3540994
# pots 454 3446974
# tops 454 3566014
# spot 454 3537154
```

`bad_hash` gives **the same number for every anagram** (addition ignores order), so all four words pile into one slot. `better_hash` multiplies by 31 at every step, so *position matters* and the anagrams get different values. Always make order and every part of the key influence the result.

## 3. Collisions are unavoidable

If you have more possible keys than slots, two keys must share a slot (the **pigeonhole principle**). That is a **collision**.

```python
SIZE = 10
keys = ["apple", "banana", "cherry", "date", "elder", "fig", "grape"]
slots = {}
for k in keys:
    slots.setdefault(better_hash(k) % SIZE, []).append(k)
print(sorted(slots.items()))
# [(0, ['apple', 'fig']), (3, ['cherry']), (4, ['date', 'elder']), (7, ['grape']), (9, ['banana'])]
```

Even 7 keys in 10 slots often collide. How often? The **birthday paradox**: in a room of just **23 people** there is a 50% chance two share a birthday (365 slots!). Collisions arrive far sooner than intuition says.

```python
import math

def collision_probability(n_keys, n_slots):
    no_collision = 1.0
    for i in range(n_keys):
        no_collision *= (n_slots - i) / n_slots
    return 1 - no_collision

print(round(collision_probability(23, 365), 3))       # 0.507
print(round(collision_probability(10, 100), 3))       # 0.372
print(round(collision_probability(100, 1_000_000), 3))  # 0.005
```

So **a hash table must have a plan for collisions**: [chaining or open addressing](02-implementing-hash-tables.md).

## 4. Load factor

**Load factor** `α = n / m`, where `n` is the number of stored items and `m` the number of slots.

- Low `α` (0.1): fast but wastes memory.
- High `α` (0.95): crowded, slow.
- Typical thresholds: Python `dict` resizes at about 2/3 full; Java `HashMap` at 0.75.

Expected cost of a lookup with a good hash and chaining is about `1 + α`, so keeping `α` bounded by **resizing** (doubling and re-inserting) gives **`O(1)` average**.

## 5. Hashing in Python

`hash(x)` exists for **immutable** objects; the built-in `dict` and `set` use it.

```python
print(hash(42), hash(3.0) == hash(3), hash((1, 2)) == hash((1, 2)))   # 42 True True

try:
    hash([1, 2])
except TypeError as e:
    print(e)                                                          # unhashable type: 'list'
```

Why are lists unhashable? If the contents change after insertion, the hash changes and the table could never find the item again. **Keys must be immutable** (or at least never change in a way that alters equality).

String hashes are **randomized per process** (`PYTHONHASHSEED`) to prevent attackers crafting colliding keys (a hash-flooding denial of service), so never rely on the number across runs, and never store `hash()` results in files.

Custom classes: define `__eq__` and `__hash__` together.

```python
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def __eq__(self, other):
        return isinstance(other, Point) and (self.x, self.y) == (other.x, other.y)
    def __hash__(self):
        return hash((self.x, self.y))          # hash the same fields used in __eq__

visited = {Point(1, 2), Point(1, 2), Point(3, 4)}
print(len(visited))                            # 2
```

## 6. Cryptographic versus table hashes

| | Table hash (`hash()`, FNV, MurmurHash) | Cryptographic (SHA-256) |
|---|---|---|
| Goal | spread keys fast | impossible to reverse or forge |
| Speed | very fast | slower |
| Use | dictionaries, sets | checksums, signatures, passwords (with salt and slow hashes such as bcrypt/argon2) |

```python
import hashlib
print(hashlib.sha256(b"hello").hexdigest()[:16])    # 2cf24dba5fb0a30e
```

Never use a plain fast hash for passwords.

## 7. Two real-world examples

**Example 1: Deduplication.** To find duplicate files, hash each file's content (SHA-256) and put the hash into a dictionary; equal hashes (almost surely) mean equal files. Backup tools and Git (which names objects by their hash) work this way.

**Example 2: Sharding.** A distributed cache picks the server for a key by `hash(key) % number_of_servers`. Adding a server remaps nearly every key, which is why large systems use **consistent hashing**.

## 8. Common mistakes

- Using a mutable object (list, dict) as a key.
- Defining `__eq__` without `__hash__` (Python then makes the class unhashable).
- A hash that ignores order or part of the key (the anagram bug).
- Saving `hash()` of strings between runs.
- Using `% size` with a poor hash and a power-of-two table (low bits may be all alike); good hashes mix all bits.
- Treating a hash as encryption.

## 9. Practice

1. Why can a hash table promise `O(1)` only on average?
2. Compute the load factor for 600 items in 1000 slots.
3. Write a hash for a 2D grid coordinate `(row, col)` that never collides for a 100x100 grid.
4. How many people make a 50% birthday collision when there are 1000 slots? (use the function)
5. Explain why `hash(3) == hash(3.0)` must be true.

<details>
<summary>Solutions</summary>

1. A bad input set can send many keys to one slot (all collide), making operations `O(n)`.
2. `600 / 1000 = 0.6`.
3. `row * 100 + col` (a unique number for each of the 10 000 cells).
4. ```python
   n = 1
   while collision_probability(n, 1000) < 0.5: n += 1
   print(n)    # 38
   ```
5. `3 == 3.0` is `True`, and equal keys must hash equally, otherwise `d[3]` and `d[3.0]` would live in different slots.

</details>

## 10. Check yourself

1. What does a hash function do?
2. What is a collision and why is it unavoidable?
3. What is the load factor?
4. Why must dictionary keys be immutable?
5. Why are Python string hashes randomized?

<details>
<summary>Answers</summary>

1. Turns a key into an integer, then `% size` gives a slot.
2. Two keys landing in the same slot; there are more possible keys than slots.
3. Items divided by slots.
4. A change would change the hash and the item would be lost.
5. To stop attackers from crafting colliding keys that slow a server to a crawl.

</details>

[Back to hash tables](README.md) · Next: [implementing hash tables](02-implementing-hash-tables.md)
