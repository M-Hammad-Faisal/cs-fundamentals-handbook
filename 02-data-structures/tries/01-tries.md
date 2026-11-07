# Tries (Prefix Trees)

**Prerequisites:** [trees](../trees/01-binary-trees-and-traversals.md), [hash tables](../hash-tables/01-hash-functions-and-collisions.md), [strings](../arrays-strings/03-strings-in-depth.md). **You will learn:** what a trie is and why autocomplete uses it, how to insert/search/delete, prefix search and autocomplete, a memory-saving compressed form, and when a plain `dict` or `set` is better.

## 1. In plain words

Think of a printed dictionary: to find "cart" you do not read every word; you go to the **C** section, then **CA**, then **CAR**. A **trie** (pronounced "try", from re*trie*val) stores words the same way: a tree where **each step down is one character**. Words that share a beginning share a path.

Storing `car`, `cart`, `cat`, `dog`:

```text
root
 ├─ c ─ a ─ r*─ t*      * marks "a word ends here"
 │      └─ t*
 └─ d ─ o ─ g*
```

`car` and `cart` share the path `c-a-r`; `r` is marked as a word end because "car" is a word on its own.

## 2. Implementation

```python
class TrieNode:
    def __init__(self):
        self.children = {}              # character -> TrieNode
        self.is_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()
        self.word_count = 0

    def insert(self, word):
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())       # create the step if it does not exist
        if not node.is_word:
            node.is_word = True
            self.word_count += 1

    def _walk(self, text):
        node = self.root
        for ch in text:
            node = node.children.get(ch)
            if node is None:
                return None
        return node

    def search(self, word):             # is this exact word stored?
        node = self._walk(word)
        return node is not None and node.is_word

    def starts_with(self, prefix):      # does any stored word start with this prefix?
        return self._walk(prefix) is not None

    def words_with_prefix(self, prefix):
        node = self._walk(prefix)
        found = []
        def collect(n, path):
            if n.is_word:
                found.append(path)
            for ch in sorted(n.children):
                collect(n.children[ch], path + ch)
        if node:
            collect(node, prefix)
        return found

trie = Trie()
for w in ["car", "cart", "cat", "dog", "do"]:
    trie.insert(w)
print(trie.search("car"), trie.search("ca"), trie.search("cow"))        # True False False
print(trie.starts_with("ca"), trie.starts_with("cb"))                   # True False
print(trie.words_with_prefix("ca"), trie.words_with_prefix("do"))       # ['car', 'cart', 'cat'] ['do', 'dog']
print(trie.word_count)                                                  # 5
```

Note `search("ca")` is `False` (it is only a prefix) while `starts_with("ca")` is `True`. That distinction is the whole reason for the `is_word` flag.

### Cost

Every operation walks one node per character: **`O(L)`** where `L` is the word length, **independent of how many words are stored**. A hash table is also `O(L)` (hashing reads the whole word), but a trie additionally answers **prefix questions**, which a hash table cannot.

Memory is the price: one node (and a dict) per character; a million words can use hundreds of MB in Python.

## 3. Deleting a word

Unmark the end, then prune any nodes that no longer lead to a word:

```python
def delete(trie, word):
    def helper(node, i):
        if i == len(word):
            if not node.is_word:
                return False                       # word was not stored
            node.is_word = False
            return not node.children               # parent may delete this node if it is now useless
        child = node.children.get(word[i])
        if child is None:
            return False
        should_remove_child = helper(child, i + 1)
        if should_remove_child:
            del node.children[word[i]]
            return not node.is_word and not node.children
        return False
    existed = trie.search(word)
    helper(trie.root, 0)
    if existed:
        trie.word_count -= 1
    return existed

print(delete(trie, "cart"), trie.search("cart"), trie.search("car"))     # True False True
print(delete(trie, "cow"), trie.word_count)                              # False 4
print(trie.words_with_prefix("ca"))                                      # ['car', 'cat']
```

## 4. Autocomplete with ranking

Store a score at each word end and return the best few completions.

```python
import heapq

class AutoComplete:
    def __init__(self):
        self.trie = Trie()
        self.scores = {}

    def add(self, phrase, popularity):
        self.trie.insert(phrase)
        self.scores[phrase] = popularity

    def suggest(self, prefix, k=3):
        candidates = self.trie.words_with_prefix(prefix)
        return heapq.nlargest(k, candidates, key=lambda w: self.scores[w])

ac = AutoComplete()
for phrase, pop in [("python tutorial", 90), ("python list", 70), ("python dict", 85),
                    ("pyramid", 20), ("java tutorial", 60)]:
    ac.add(phrase, pop)
print(ac.suggest("py", 3))               # ['python tutorial', 'python dict', 'python list']
print(ac.suggest("python d"))            # ['python dict']
print(ac.suggest("rust"))                # []
```

Real engines also store the top suggestions *at each node* so a query is just a walk of the prefix, answering in microseconds.

## 5. Word search: pruning with a trie

Find all dictionary words in a letter grid. A trie lets the search **stop early** when no word starts with the path so far.

```python
def find_words(board, words):
    trie = Trie()
    for w in words:
        trie.insert(w)
    rows, cols = len(board), len(board[0])
    found = set()

    def dfs(r, c, node, path):
        ch = board[r][c]
        if ch not in node.children:
            return                                   # no word continues this way: prune
        node = node.children[ch]
        path += ch
        if node.is_word:
            found.add(path)
        board[r][c] = "#"                            # mark visited
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != "#":
                dfs(nr, nc, node, path)
        board[r][c] = ch                             # unmark

    for r in range(rows):
        for c in range(cols):
            dfs(r, c, trie.root, "")
    return sorted(found)

grid = [list("oaan"), list("etae"), list("ihkr"), list("iflv")]
print(find_words(grid, ["oath", "pea", "eat", "rain"]))      # ['eat', 'oath']
```

## 6. A compressed trie (radix tree) and a bit-trie

Long single-child chains waste nodes. A **radix tree / compressed trie** stores whole substrings on edges. It is the idea behind IP routing tables and Git/Redis internals.

A trie over **bits** instead of letters also solves a classic puzzle: the maximum XOR of two numbers in a list.

```python
def max_xor(nums):
    root = {}
    for n in nums:
        node = root
        for bit in range(31, -1, -1):
            node = node.setdefault((n >> bit) & 1, {})
    best = 0
    for n in nums:
        node, value = root, 0
        for bit in range(31, -1, -1):
            wanted = 1 - ((n >> bit) & 1)            # we want the opposite bit to make XOR bits 1
            if wanted in node:
                value |= 1 << bit
                node = node[wanted]
            else:
                node = node[1 - wanted]
        best = max(best, value)
    return best

print(max_xor([3, 10, 5, 25, 2, 8]))                 # 28   (5 XOR 25)
```

## 7. Trie versus dict versus sorted list

| Need | Best choice |
|------|-------------|
| Exact membership only | `set` (simplest, least memory) |
| Prefix search / autocomplete | **trie** (or a sorted list with `bisect` for modest data) |
| Longest matching prefix (routing, tokenizers) | **trie** |
| Memory-tight dictionary of words | compressed trie / DAWG, or a sorted list |

```python
import bisect
words = sorted(["car", "cart", "cat", "dog", "do"])
lo = bisect.bisect_left(words, "ca")
hi = bisect.bisect_left(words, "ca" + "￿")
print(words[lo:hi])                                  # ['car', 'cart', 'cat']   (prefix search with only a sorted list)
```

## 8. Two real-world examples

**Example 1: Search-box autocomplete and phone keyboards.** Each keystroke extends the prefix; the trie walk returns candidate completions without scanning the whole vocabulary.

**Example 2: IP routing.** A router finds the **longest matching prefix** of a destination address among millions of routes using a (bit-level, compressed) trie, in time proportional to the 32 or 128 address bits.

## 9. Common mistakes

- Forgetting the `is_word` flag (then `"ca"` looks like a stored word).
- Not handling the empty string or uppercase/lowercase normalization.
- Using a list of 26 children per node for Unicode text (use a `dict`).
- Deleting a word and leaving orphan nodes (or deleting a prefix shared by other words).
- Using a trie when a `set` is enough.
- Recursion depth on very long words (use iteration).

## 10. Practice

1. Insert `tea`, `ten`, `to`, `inn`. How many nodes (excluding the root) does the trie have?
2. Add `count_prefix(prefix)` returning how many stored words start with the prefix.
3. Write `longest_common_prefix(words)` using only a trie.
4. Implement `replace_words(dictionary_of_roots, sentence)` that swaps each word for its shortest root.
5. Why is trie memory usage often high in Python?
6. What is the time to search a word of length 8 in a trie holding 10 million words?

<details>
<summary>Solutions</summary>

1. The nodes are `t`, `te`, `tea`, `ten`, `to`, `i`, `in`, `inn`: **8** (`tea` and `ten` share `t` and `te`).
2. ```python
   def count_prefix(trie, prefix):
       return len(trie.words_with_prefix(prefix))
   print(count_prefix(trie, "ca"), count_prefix(trie, "do"))      # 2 2
   ```
3. ```python
   def longest_common_prefix(words):
       t = Trie()
       for w in words: t.insert(w)
       node, prefix = t.root, ""
       while len(node.children) == 1 and not node.is_word:
           ch, node = next(iter(node.children.items()))
           prefix += ch
       return prefix
   print(longest_common_prefix(["flower", "flow", "flight"]), longest_common_prefix(["dog", "car"]) == "")      # fl True
   ```
4. ```python
   def replace_words(roots, sentence):
       t = Trie()
       for r in roots: t.insert(r)
       def shortest(word):
           node = t.root
           for i, ch in enumerate(word):
               if ch not in node.children: return word
               node = node.children[ch]
               if node.is_word: return word[:i + 1]
           return word
       return " ".join(shortest(w) for w in sentence.split())
   print(replace_words(["cat", "bat", "rat"], "the cattle was rattled by the battery"))      # the cat was rat by the bat
   ```
5. Every node is a Python object holding a dict, which costs hundreds of bytes even for one child.
6. `O(8)`: it depends on the word length, not on how many words are stored.

</details>

## 11. Check yourself

1. What does each edge of a trie represent?
2. Why is the `is_word` flag needed?
3. What is the cost of insert/search in terms of word length `L`?
4. Which question can a trie answer that a hash set cannot?
5. What is a radix tree?

<details>
<summary>Answers</summary>

1. One character (or one bit for a bit-trie).
2. To tell a stored word apart from a mere prefix of another word.
3. `O(L)`.
4. Prefix queries (autocomplete, longest matching prefix).
5. A compressed trie whose edges hold whole substrings, saving nodes.

</details>

[Back to tries](README.md)
