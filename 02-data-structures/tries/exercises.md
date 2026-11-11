# Tries: Exercises

## Problems
1. Implement a `Trie` with `insert`, `search`, and `starts_with`.
2. Add `words_with_prefix(prefix)` returning all words that start with the prefix, sorted.
3. Implement a `WordDictionary` where `search` supports `.` as a single-character wildcard.
4. Return the **longest common prefix** of a list of strings.
5. Implement `delete(word)` that removes a word and prunes unused nodes.
6. Given a list of words and a sentence, **replace each word with its shortest root** from the dictionary.
7. Count how many words in a list **start with a given prefix** in `O(L)` per query (store counts in nodes).
8. Find the **maximum XOR** of any two numbers in a list.

<details>
<summary>Solutions</summary>

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.count = 0                       # words passing through this node

# 1, 2, 7
class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
            node.count += 1
        node.is_end = True

    def _walk(self, s):
        node = self.root
        for ch in s:
            node = node.children.get(ch)
            if node is None:
                return None
        return node

    def search(self, word):
        n = self._walk(word)
        return n is not None and n.is_end

    def starts_with(self, prefix):
        return self._walk(prefix) is not None

    def count_prefix(self, prefix):          # problem 7
        n = self._walk(prefix)
        return n.count if n else 0

    def words_with_prefix(self, prefix):     # problem 2
        node, out = self._walk(prefix), []
        def dfs(n, path):
            if n.is_end:
                out.append(prefix + "".join(path))
            for ch in sorted(n.children):
                path.append(ch)
                dfs(n.children[ch], path)
                path.pop()
        if node:
            dfs(node, [])
        return out

    def delete(self, word):                  # problem 5
        def helper(node, i):
            if i == len(word):
                if not node.is_end:
                    return False
                node.is_end = False
                return not node.children
            ch = word[i]
            child = node.children.get(ch)
            if child is None:
                return False
            if helper(child, i + 1):
                del node.children[ch]
                return not node.children and not node.is_end
            return False
        helper(self.root, 0)

# 3
class WordDictionary:
    def __init__(self):
        self.root = TrieNode()
    def add(self, word):
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.is_end = True
    def search(self, word):
        def dfs(node, i):
            if i == len(word):
                return node.is_end
            ch = word[i]
            if ch == ".":
                return any(dfs(c, i + 1) for c in node.children.values())
            return ch in node.children and dfs(node.children[ch], i + 1)
        return dfs(self.root, 0)

# 4
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

# 6
def replace_words(roots, sentence):
    t = Trie()
    for r in roots:
        t.insert(r)
    def shortest(word):
        node = t.root
        for i, ch in enumerate(word):
            node = node.children.get(ch)
            if node is None:
                return word
            if node.is_end:
                return word[:i + 1]
        return word
    return " ".join(shortest(w) for w in sentence.split())

# 8
def max_xor(nums):
    root = {}
    for n in nums:
        node = root
        for b in range(31, -1, -1):
            bit = (n >> b) & 1
            node = node.setdefault(bit, {})
    best = 0
    for n in nums:
        node, cur = root, 0
        for b in range(31, -1, -1):
            bit = (n >> b) & 1
            want = 1 - bit
            if want in node:
                cur |= 1 << b
                node = node[want]
            else:
                node = node[bit]
        best = max(best, cur)
    return best
```

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Tries](01-tries.md)
