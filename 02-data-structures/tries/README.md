# Tries (Prefix Trees)

## Detailed lesson (start here if you are new)

- [Tries in depth](01-tries.md): insert/search/delete, autocomplete, word search, radix and bit tries

The rest of this page is the quick reference.

## 1. The concept

A **trie** (pronounced "try") is a tree where each edge represents a **character** and each path from the root spells a **prefix**. Words that share a prefix share the same path, so common beginnings are stored only once.

```
Words: car, card, care, cat, dog

root
 ├─ c ─ a ─ r* ─┬─ d*      (* marks the end of a word)
 │              └─ e*
 │         └ t*
 └─ d ─ o ─ g*
```

The key idea: **lookup time depends on the length of the word, not on how many words are stored.**

## 2. How it works

```python
class TrieNode:
    def __init__(self):
        self.children = {}        # char -> TrieNode
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):                       # O(L)
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.is_end = True

    def search(self, word):                       # O(L)
        node = self._walk(word)
        return node is not None and node.is_end

    def starts_with(self, prefix):                # O(L)
        return self._walk(prefix) is not None

    def _walk(self, s):
        node = self.root
        for ch in s:
            node = node.children.get(ch)
            if node is None:
                return None
        return node

    def words_with_prefix(self, prefix):          # autocomplete
        node = self._walk(prefix)
        out = []
        def dfs(n, path):
            if n.is_end:
                out.append(prefix + "".join(path))
            for ch, child in sorted(n.children.items()):
                path.append(ch)
                dfs(child, path)
                path.pop()
        if node:
            dfs(node, [])
        return out
```

### Complexity

Let `L` be the length of the word or prefix, and `N` the total number of characters stored.

| Operation | Time | Notes |
|-----------|------|-------|
| Insert | `O(L)` | |
| Search exact word | `O(L)` | |
| Prefix check | `O(L)` | Hash set cannot do this fast |
| Collect all words with a prefix | `O(L + output size)` | |
| Space | `O(N)` worst case | Shared prefixes reduce it |

### Trie vs hash set

| Need | Hash set | Trie |
|------|----------|------|
| Exact membership | `O(L)` to hash, `O(1)` average | `O(L)` |
| "Does any word start with `pre`?" | `O(n)` scan | `O(L)` |
| Sorted iteration | Not available | Natural (walk children in order) |
| Memory | Lower | Higher (a node per character) |

Choose a trie when **prefix operations** matter.

### Variants

- **Compressed trie / radix tree:** merges chains of single-child nodes into one edge labelled with a string. Saves memory (used in routing tables and Redis internals).
- **Array children:** for lowercase letters only, use `children = [None] * 26` for speed.
- **Ternary search tree:** compact alternative storing three pointers per node.
- **Binary trie:** keys are bit strings (used in IP routing and XOR problems).

## 3. Classic patterns

### Word search with wildcards

```python
class WordDictionary:
    def __init__(self):
        self.root = TrieNode()

    def add(self, word):
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.is_end = True

    def search(self, word):                       # '.' matches any one letter
        def dfs(node, i):
            if i == len(word):
                return node.is_end
            ch = word[i]
            if ch == ".":
                return any(dfs(c, i + 1) for c in node.children.values())
            return ch in node.children and dfs(node.children[ch], i + 1)
        return dfs(self.root, 0)
```

### Longest common prefix

```python
def longest_common_prefix(words):
    if not words:
        return ""
    prefix = words[0]
    for w in words[1:]:
        while not w.startswith(prefix):
            prefix = prefix[:-1]
        if not prefix:
            return ""
    return prefix
```

### Maximum XOR of two numbers (binary trie)

Insert each number's bits (most significant first). For each number, walk the trie choosing the opposite bit whenever possible to maximize the XOR. `O(n * bits)`.

## 4. Two real-world examples

### Example 1: Autocomplete and spell-check

When you type "pyth" in a search box, the system walks to the node for `pyth` and collects the most popular completions below it. The time depends on the prefix length (4), not on whether the dictionary has ten thousand or ten million entries. Search engines, IDE code completion, phone keyboards, and command-line tab completion work this way (often with popularity counts stored at each node, or a heap of the top suggestions per node).

### Example 2: IP routing tables

A router must find the **longest prefix match** for a destination IP among thousands of routes (`10.0.0.0/8`, `10.1.0.0/16`, ...). A binary trie (or radix tree) keyed by the address bits walks as deep as it can and remembers the last matching route. The lookup takes at most 32 steps (IPv4) regardless of table size. URL routers in web frameworks use a similar radix-tree idea to match request paths quickly.

## 5. Tips, tricks and pitfalls

- **Mark word ends explicitly** (`is_end`). Without it you cannot distinguish "car" (a word) from "car" (just a prefix of "card").
- **Memory is the main cost.** A dict per node is heavy in Python; use arrays of 26, compressed tries, or a library for huge dictionaries.
- **Store extra data at nodes** (counts, top suggestions, document IDs) to support ranking.
- **Deletion:** unmark `is_end`, then prune childless nodes on the way back up (optional).
- **Recursion depth** equals word length; fine for words but be careful with very long keys.
- **Case and Unicode:** normalize input (lowercase, NFC) before inserting.
- **Prefer a plain set** if you never need prefix queries.

## 6. Check yourself

1. Why does trie lookup time not depend on the number of stored words?
2. What is the purpose of the `is_end` flag?
3. When would you pick a trie over a hash set?
4. How does a radix tree reduce memory?
5. How can a trie support autocomplete with ranking?
6. How does a binary trie help find the maximum XOR pair?

<details>
<summary>Answers</summary>

1. You follow one edge per character, so the work is the length of the word, regardless of how many other words exist.
2. It marks that a complete word ends at that node, separating real words from mere prefixes.
3. When you need prefix queries, autocomplete, or sorted iteration over keys.
4. It merges chains of single-child nodes into one edge labelled with a string, reducing the node count.
5. Store a popularity count or top-K list at each node and collect or return the best completions below the prefix node.
6. Bits are stored from most significant to least; for each number, walk the trie preferring the opposite bit at each level, which maximizes the XOR greedily.

</details>
