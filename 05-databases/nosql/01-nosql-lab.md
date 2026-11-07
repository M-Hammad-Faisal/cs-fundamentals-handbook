# NoSQL Lab: Key-Value, Documents, Search and Replication

**Prerequisites:** [normalization lab](../normalization-schema-design/01-normalization-lab.md), [hash tables](../../02-data-structures/hash-tables/01-hash-functions-and-collisions.md), [transactions lab](../transactions-acid/01-transactions-lab.md). **You will learn (by building small versions):** why "NoSQL" databases exist and what they trade away; how a **key-value store** with **TTL and eviction** works (the heart of Redis and caches); how to model **documents** (embed or reference) and query JSON; how a **search engine's inverted index** finds text in milliseconds; and how **replication and quorums** (`R + W > N`) decide whether you can read stale data, which is the **CAP/eventual consistency** trade-off in action. Everything runs with the standard library and SQLite.

## 1. In plain words

Relational databases are superb general tools, but they assume one machine (or a primary with replicas), a fixed schema and joins. **NoSQL** ("not only SQL") databases are a family of designs that give up some of that to gain something else:

| Family | Data model | Optimized for | Examples |
|--------|-----------|---------------|----------|
| **Key-value** | `key -> opaque value` | ultra-fast lookups, caching, sessions | Redis, Memcached, DynamoDB |
| **Document** | `key -> JSON document` | flexible, nested records, schema evolution | MongoDB, Couchbase, Firestore |
| **Wide-column** | rows with many sparse columns, partitioned | massive write throughput, time series | Cassandra, HBase, Bigtable |
| **Graph** | nodes and edges | relationship-heavy queries (friends of friends) | Neo4j |
| **Search** | inverted index over text | full-text search, analytics | Elasticsearch, OpenSearch |

The recurring trade: **flexibility and horizontal scale** versus **joins, strong constraints and cross-record transactions**. There is no universally better choice, only a better fit for your access patterns.

## 2. A key-value store with TTL and LRU eviction

A key-value store is a [hash table](../../02-data-structures/hash-tables/02-implementing-hash-tables.md) served over a network, plus **expiry** (so cached data does not live forever) and **eviction** (so memory stays bounded). Here is the core of Redis-like behavior:

```python
from collections import OrderedDict

class KeyValueStore:
    def __init__(self, max_items=3, clock=None):
        self.max_items = max_items
        self.clock = clock or (lambda: 0.0)
        self.data = OrderedDict()                     # key -> (value, expires_at or None); order = recency
        self.stats = {"hits": 0, "misses": 0, "evictions": 0, "expired": 0}

    def set(self, key, value, ttl=None):
        expires = self.clock() + ttl if ttl is not None else None
        self.data[key] = (value, expires)
        self.data.move_to_end(key)
        while len(self.data) > self.max_items:        # over capacity: evict the least recently used
            self.data.popitem(last=False)
            self.stats["evictions"] += 1

    def get(self, key):
        item = self.data.get(key)
        if item is None:
            self.stats["misses"] += 1
            return None
        value, expires = item
        if expires is not None and expires <= self.clock():
            del self.data[key]                        # lazy expiry: delete when noticed
            self.stats["expired"] += 1
            self.stats["misses"] += 1
            return None
        self.data.move_to_end(key)                    # mark as recently used
        self.stats["hits"] += 1
        return value

    def incr(self, key, amount=1):                    # atomic counters: a classic Redis use
        current = self.get(key) or 0
        self.set(key, current + amount)
        return current + amount

now = {"t": 100.0}
store = KeyValueStore(max_items=3, clock=lambda: now["t"])
store.set("session:42", {"user": "ana"}, ttl=30)
store.set("page:/home", "<html>home</html>")
store.set("page:/about", "<html>about</html>")
print(store.get("session:42"))                        # {'user': 'ana'}
store.set("page:/contact", "<html>contact</html>")    # a fourth item: the least recently used one is evicted
print(list(store.data))                               # ['page:/about', 'session:42', 'page:/contact']   (page:/home was the least recently used; reading the session moved it to the end)
now["t"] += 31                                        # 31 seconds later the session has expired
print(store.get("session:42"), store.stats)           # None {'hits': 1, 'misses': 1, 'evictions': 1, 'expired': 1}
print([store.incr("visits") for _ in range(3)])       # [1, 2, 3]
```

Typical uses: **caching** database results, **sessions**, **rate-limit counters** (see the [resilience lab](../../07-networking/load-balancing-cdn/01-load-balancing-and-resilience-lab.md)), **leaderboards** (Redis sorted sets), **queues**, **distributed locks**. The access pattern is always "get by exact key": no queries, no joins, which is exactly why it is fast and easy to spread over many machines (**sharding** by key hash; see consistent hashing in the [hash tables lesson](../../02-data-structures/hash-tables/03-dict-set-internals-and-bloom-filters.md)).

**Cache patterns:** *cache-aside* (app checks the cache, on a miss loads from the database and stores it), *write-through* (write both together), *write-behind* (write to cache, flush later: fast but risks loss). **Cache invalidation** (knowing when cached data is stale) is famously one of the hard problems: prefer short TTLs and delete-on-write.

```python
database = {"user:1": {"name": "Ana", "plan": "free"}}
db_reads = {"n": 0}

def load_user(user_id, cache):
    cached = cache.get(f"user:{user_id}")
    if cached is not None:
        return cached                                 # cache hit: no database work
    db_reads["n"] += 1
    value = database[f"user:{user_id}"]               # the slow, authoritative read
    cache.set(f"user:{user_id}", value, ttl=60)
    return value

cache = KeyValueStore(max_items=100, clock=lambda: now["t"])
for _ in range(1000):
    load_user(1, cache)
print(db_reads["n"], cache.stats["hits"])             # 1 999    (1000 requests, only one touched the database)
```

## 3. Documents: JSON records with nested data

A **document database** stores self-contained JSON documents, so one read returns an entire aggregate (a blog post with its comments) without joins, and different documents can have different fields (no `ALTER TABLE` migrations for new optional fields).

```python
import sqlite3, json

db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE posts (id INTEGER PRIMARY KEY, doc TEXT NOT NULL CHECK (json_valid(doc)))")   # SQLite stores JSON as text and offers JSON functions

posts = [
    {"title": "Hello NoSQL", "author": {"name": "Ana", "country": "PK"}, "tags": ["databases", "intro"],
     "comments": [{"by": "Bilal", "text": "Nice!"}, {"by": "Chen", "text": "Thanks"}]},
    {"title": "Indexes explained", "author": {"name": "Bilal", "country": "PK"}, "tags": ["databases", "performance"],
     "comments": []},
    {"title": "Cooking pasta", "author": {"name": "Chen", "country": "UK"}, "tags": ["food"],
     "comments": [{"by": "Ana", "text": "Yum"}], "calories": 600},               # an extra field only this document has
]
db.executemany("INSERT INTO posts (doc) VALUES (?)", [(json.dumps(p),) for p in posts])

print(db.execute("SELECT json_extract(doc, '$.title') FROM posts WHERE json_extract(doc, '$.author.country') = 'PK'").fetchall())
# [('Hello NoSQL',), ('Indexes explained',)]
print(db.execute("SELECT json_extract(doc, '$.title'), json_array_length(doc, '$.comments') FROM posts ORDER BY id").fetchall())
# [('Hello NoSQL', 2), ('Indexes explained', 0), ('Cooking pasta', 1)]
print(db.execute("""SELECT DISTINCT json_extract(doc, '$.title') FROM posts, json_each(posts.doc, '$.tags')
                    WHERE json_each.value = 'databases' ORDER BY 1""").fetchall())
# [('Hello NoSQL',), ('Indexes explained',)]      query inside arrays
print(db.execute("SELECT json_extract(doc, '$.calories') FROM posts ORDER BY id").fetchall())
# [(None,), (None,), (600,)]                       missing fields are simply NULL: schema-flexible
```

(In MongoDB the same ideas look like `db.posts.find({"author.country": "PK"})`, with indexes on fields inside documents:)

```python
db.execute("CREATE INDEX idx_author_country ON posts (json_extract(doc, '$.author.country'))")
plan = db.execute("EXPLAIN QUERY PLAN SELECT id FROM posts WHERE json_extract(doc, '$.author.country') = 'PK'").fetchall()
print(plan[0][3])                                    # SEARCH posts USING COVERING INDEX idx_author_country (<expr>=?)
```

### Embed or reference? The central modeling decision

| | **Embed** (nest inside the document) | **Reference** (store an id, look it up) |
|---|--------------------------------------|----------------------------------------|
| Example | comments inside the post | `author_id` pointing to a users collection |
| Reads | one fetch gets everything | needs extra lookups (or a join-like step in the application) |
| Updates | atomic for the whole document | spread across documents (no multi-document transaction in many systems) |
| Duplication | data copied into many documents | each fact stored once |
| Good when | data is read **together**, belongs to one parent, and stays **bounded** (a post's first comments) | data is **shared**, changes often, or can grow **unbounded** (all of an author's posts) |

```python
# Embedding a bounded list: adding a comment is one atomic document update
db.execute("""UPDATE posts SET doc = json_insert(doc, '$.comments[#]', json('{"by": "Dina", "text": "Great read"}'))
              WHERE json_extract(doc, '$.title') = 'Indexes explained'""")
print(db.execute("SELECT json_array_length(doc, '$.comments') FROM posts WHERE id = 2").fetchone())          # (1,)
```

**The denormalization warning from the [normalization lab](../normalization-schema-design/01-normalization-lab.md) applies:** if you embed an author's name in every post and the author renames themselves, you must update every post. Embed what is **read together and changes rarely**; reference what is shared or volatile. Design the documents **around your queries** (the opposite of relational design, which models the data first and queries later).

## 4. A mini search engine: the inverted index

SQL `LIKE '%word%'` scans every row. A **search engine** builds an **inverted index**: for every word, the list of documents containing it (like the index at the back of a book). Lookups become dictionary lookups plus list intersections. This is what Lucene (inside Elasticsearch, OpenSearch, Solr) does.

```python
import re
from collections import defaultdict
import math

documents = {
    1: "Python is great for data analysis and web development",
    2: "Databases store data; indexes make databases fast",
    3: "A web server answers HTTP requests quickly",
    4: "Data pipelines move data between databases and warehouses",
}

def tokenize(text):
    return re.findall(r"[a-z0-9]+", text.lower())                   # lowercase, split into words

index = defaultdict(set)                                            # word -> set of document ids (the inverted index)
for doc_id, text in documents.items():
    for word in tokenize(text):
        index[word].add(doc_id)

print(sorted(index["data"]), sorted(index["databases"]), sorted(index["web"]))
# [1, 2, 4] [2, 4] [1, 3]

def search_all(query):                                              # documents containing ALL the words (AND)
    sets = [index.get(word, set()) for word in tokenize(query)]
    return sorted(set.intersection(*sets)) if sets else []

print(search_all("data databases"))                                 # [2, 4]
print(search_all("web data"))                                       # [1]
print(search_all("kubernetes"))                                     # []
```

**Ranking** orders the matches by relevance. **TF-IDF** scores a word higher if it is frequent *in this document* (term frequency) and rare *across all documents* (inverse document frequency):

```python
term_counts = {doc_id: defaultdict(int) for doc_id in documents}
for doc_id, text in documents.items():
    for word in tokenize(text):
        term_counts[doc_id][word] += 1

def tfidf_search(query, top=3):
    n_docs = len(documents)
    scores = defaultdict(float)
    for word in tokenize(query):
        if word not in index:
            continue
        idf = math.log(1 + n_docs / len(index[word]))               # rare words weigh more
        for doc_id in index[word]:
            tf = term_counts[doc_id][word] / sum(term_counts[doc_id].values())
            scores[doc_id] += tf * idf
    return sorted(((round(score, 3), doc_id) for doc_id, score in scores.items()), reverse=True)[:top]

print(tfidf_search("databases data"))
# [(0.435, 2), (0.349, 4), (0.094, 1)]     doc 2 mentions "databases" twice in a short text: it ranks first
print(documents[2])
```

Real engines add **stemming** ("indexes" matches "index"), **stop-word** handling, phrase and fuzzy queries, **BM25** scoring (a better TF-IDF), and shard the index across machines. Elasticsearch is usually a **secondary** store fed from the primary database, since it is optimized for search, not for being your system of record.

SQLite ships a real inverted index too (FTS5), if available in your build:

```python
try:
    fts = sqlite3.connect(":memory:")
    fts.execute("CREATE VIRTUAL TABLE docs USING fts5(body)")
    fts.executemany("INSERT INTO docs VALUES (?)", [(t,) for t in documents.values()])
    print(fts.execute("SELECT rowid FROM docs WHERE docs MATCH 'data AND databases' ORDER BY rowid").fetchall())      # [(2,), (4,)]
except sqlite3.OperationalError:
    print("this SQLite build has no FTS5")
```

## 5. Replication, quorums and the CAP trade-off

To survive machine failures and serve more readers, data is **replicated**: `N` copies on different nodes. Now a question appears that single-node databases never face: **if I write to some copies and read from others, will I see my write?**

Dynamo-style stores (Cassandra, DynamoDB, Riak) answer with a **quorum**: write to `W` replicas, read from `R` replicas, out of `N`. If **`R + W > N`**, every read set overlaps every write set in at least one replica, so a read always touches a replica holding the latest value. If `R + W <= N`, a read can miss it and return **stale** data.

Let us verify by brute force: try *every possible* choice of which replicas the write and the read hit.

```python
from itertools import combinations

def stale_read_possible(n, w, r):
    replicas = range(n)
    for write_set in combinations(replicas, w):
        for read_set in combinations(replicas, r):
            if not set(write_set) & set(read_set):             # the read set shares no replica with the write set
                return True                                    # so the reader sees only old data
    return False

print("N=3")
for w, r in ((1, 1), (1, 2), (2, 1), (2, 2), (3, 1), (1, 3)):
    print(f"  W={w} R={r}  R+W={r + w}  stale read possible: {stale_read_possible(3, w, r)}")
#   W=1 R=1  R+W=2  stale read possible: True
#   W=1 R=2  R+W=3  stale read possible: True
#   W=2 R=1  R+W=3  stale read possible: True
#   W=2 R=2  R+W=4  stale read possible: False
#   W=3 R=1  R+W=4  stale read possible: False
#   W=1 R=3  R+W=4  stale read possible: False
```

Look at `W=1, R=2`: `R + W = 3`, which is **not** greater than `N = 3`, so a stale read is still possible (the two replicas you read may be exactly the two the write missed). The rule is strictly `R + W > N`, and the exhaustive check confirms it for every combination.

A running simulation with versions shows what a client sees:

```python
class Replica:
    def __init__(self):
        self.value, self.version = None, 0

class Cluster:
    def __init__(self, n=3):
        self.replicas = [Replica() for _ in range(n)]
        self.version = 0

    def write(self, value, targets):                         # the write reaches only `targets` right now
        self.version += 1
        for i in targets:
            self.replicas[i].value, self.replicas[i].version = value, self.version

    def read(self, targets):                                 # return the freshest value among those read (last-write-wins by version)
        best = max((self.replicas[i] for i in targets), key=lambda r: r.version)
        return best.value

c = Cluster(3)
c.write("v1", targets=[0, 1, 2])                             # initially all replicas agree
c.write("v2", targets=[0])                                   # W=1: the other replicas have not received v2 yet (network delay)
print(c.read([1]))                                           # v1   R=1 reads a stale replica
print(c.read([1, 2]))                                        # v1   R=2 can still miss it (R+W = 3 is not > 3)
print(c.read([0, 1]))                                        # v2   a read that happens to include replica 0 sees it

c2 = Cluster(3)
c2.write("v1", targets=[0, 1, 2])
c2.write("v2", targets=[0, 1])                               # W=2
print(all(c2.read(list(rs)) == "v2" for rs in combinations(range(3), 2)))        # True   R=2, W=2: every read set overlaps the write set
```

Background mechanisms heal the stragglers: **read repair** (a read that notices old replicas updates them), **hinted handoff**, **anti-entropy** with Merkle trees. Concurrent writes to different replicas create **conflicts**, resolved by **last-write-wins** (simple, can lose updates) or **vector clocks/CRDTs** (keep both versions, merge them).

### CAP in one picture

The **CAP theorem**: when the network **partitions** (some nodes cannot talk to others), a distributed store must choose between

- **Consistency (C):** refuse requests it cannot answer correctly (unavailable during the partition), or
- **Availability (A):** keep answering from whatever data a node has (possibly stale).

You cannot have both during a partition. (Partitions are a fact of life, so the real choice is C or A **when they happen**; with a healthy network you can have both.)

| Style | During a partition | Examples |
|-------|--------------------|----------|
| **CP** (consistency over availability) | some requests fail or wait | HBase, etcd/ZooKeeper, MongoDB (default settings), Spanner-like systems |
| **AP** (availability over consistency) | always answer, maybe stale; reconcile later (**eventual consistency**) | Cassandra, DynamoDB (eventual reads), Riak, DNS |

**Eventual consistency** means: if no new writes arrive, all replicas will eventually hold the same value. DNS ([DNS lab](../../07-networking/dns-http/02-dns-in-depth.md)) is the world's biggest eventually consistent system: a changed record spreads as caches expire. The **PACELC** refinement adds that even *without* partitions you trade **latency vs consistency** (waiting for more replicas is slower).

Many systems let you **choose per operation**: DynamoDB's "strongly consistent read" flag, Cassandra's `QUORUM` versus `ONE`.

## 6. Choosing a database

Start from your **access patterns and consistency needs**, not from fashion:

| Need | Reasonable choice |
|------|-------------------|
| Transactions across several records, ad-hoc queries, reporting, constraints | **relational** (PostgreSQL, MySQL): the default |
| Fast lookups by key, caching, sessions, counters, leaderboards | **key-value** (Redis, DynamoDB) |
| Nested, flexible records read as a unit; fast iteration on schema | **document** (MongoDB, Firestore), or PostgreSQL `jsonb` |
| Huge write volume, time series, spread across data centers | **wide-column** (Cassandra, ScyllaDB), or a time-series DB (TimescaleDB, InfluxDB) |
| Full-text search, log analytics, faceted filtering | **search engine** (Elasticsearch/OpenSearch), fed from your primary store |
| Deep relationship queries (recommendations, fraud rings) | **graph** (Neo4j) |
| Large-scale analytics over history | **data warehouse** (BigQuery, Snowflake, ClickHouse) |

**Polyglot persistence** (several databases, each for what it does best) is normal in large systems: PostgreSQL as the **system of record**, Redis as a cache, Elasticsearch for search, a warehouse for analytics, kept in sync by events. The cost is operational complexity: do not add a database until a measured need justifies it. Modern PostgreSQL (with `jsonb`, full-text search, extensions, and partitioning) covers a surprising share of cases alone.

```python
# A decision helper encoding the table above (a thinking aid, not a rule engine)
def suggest(needs):
    rules = [
        ("multi-record transactions", "relational (PostgreSQL)"),
        ("ad-hoc queries", "relational (PostgreSQL)"),
        ("cache or sessions", "key-value (Redis)"),
        ("flexible nested documents", "document (MongoDB) or PostgreSQL jsonb"),
        ("massive writes", "wide-column (Cassandra) or time-series"),
        ("full-text search", "search engine (Elasticsearch)"),
        ("relationship traversal", "graph (Neo4j)"),
    ]
    return sorted({answer for need, answer in rules if need in needs}) or ["start with PostgreSQL"]

print(suggest({"multi-record transactions", "full-text search"}))
# ['relational (PostgreSQL)', 'search engine (Elasticsearch)']       (primary store plus a search index)
print(suggest(set()))                                                # ['start with PostgreSQL']
```

## 7. Two real-world examples

**Example 1: A shopping site.** PostgreSQL stores orders and payments (transactions, constraints); Redis holds sessions and carts and counts rate limits; Elasticsearch powers product search; a warehouse feeds sales dashboards. A change event after each order commit updates the search index and the warehouse asynchronously, so those copies are **eventually consistent** while the order data is strongly consistent.

**Example 2: A global "likes" or telemetry service.** Writes arrive at enormous rates from many regions. A wide-column or Dynamo-style store accepts them with `W=1` for low latency (AP), counts are allowed to be slightly stale for a moment, and a stream job aggregates exact totals later. For a **bank balance** the same team would insist on a CP, transactional store.

## 8. Common mistakes

- Choosing NoSQL "to scale" before measuring; a single PostgreSQL handles millions of rows and thousands of requests per second.
- Modeling documents like relational tables (everything referenced, joined in application code) or embedding unbounded lists (a document that grows forever).
- Treating a cache as the source of truth (it can be evicted or expire at any moment).
- Assuming eventual consistency means "usually fine" without designing for stale reads and conflicting writes.
- No expiry or eviction policy on a cache (memory fills up).
- Ignoring that many NoSQL stores lack multi-document transactions and ad-hoc joins.
- Using Elasticsearch as the primary database.
- Forgetting access patterns: NoSQL schemas are designed around the queries you will run.

## 9. Practice

1. In the `KeyValueStore`, what happens to `page:/about` if you `get` it right before inserting a new key into a full store?
2. Why can a document database store posts with different fields without a migration?
3. When would you embed comments in a post and when reference them?
4. With `N=5`, which pairs `(W, R)` guarantee reading the latest write?
5. What does "eventually consistent" promise?
6. Build the inverted index for `["a b", "b c"]` by hand and answer the query `b`.
7. Name a system for each of CP and AP behavior and the cost of each choice.

<details>
<summary>Solutions</summary>

1. Getting it marks it most recently used, so it is *not* the eviction victim; the least recently used key goes instead.
2. A document is self-describing JSON; there is no fixed column list, so a new optional field simply appears in the documents that have it (missing fields read as null).
3. Embed a bounded number of comments displayed with the post and not queried independently (one read, atomic update); reference them if comments are numerous, unbounded, edited or queried on their own (for example a moderation queue).
4. Any pair with `W + R > 5` (for example `W=3, R=3`; `W=5, R=1`; `W=1, R=5`; `W=4, R=2`; `W=2, R=4`).
   ```python
   print([(w, r) for w in range(1, 6) for r in range(1, 6) if not stale_read_possible(5, w, r)][:6])
   # [(1, 5), (2, 4), (2, 5), (3, 3), (3, 4), (3, 5)]
   ```
5. If writes stop, all replicas converge to the same value after some time; until then reads may be stale.
6. `a -> {1}`, `b -> {1, 2}`, `c -> {2}`; the query `b` returns documents 1 and 2.
7. CP: etcd or ZooKeeper, which stop accepting writes without a majority (cost: unavailability during partitions). AP: Cassandra or DynamoDB with eventual reads, which always answer (cost: possibly stale reads and conflicts to reconcile).

</details>

## 10. Check yourself

1. What does a key-value store give up and gain compared with SQL?
2. What is the inverted index and why is it fast?
3. What is the embed-versus-reference decision based on?
4. State the quorum rule and what happens if it is violated.
5. What does the CAP theorem say?
6. Why do large systems use several databases?

<details>
<summary>Answers</summary>

1. It gives up queries, joins and multi-record constraints; it gains very fast key lookups, simplicity and easy horizontal partitioning.
2. A map from each word to the documents containing it; a query becomes a few dictionary lookups and set intersections instead of scanning all documents.
3. Whether the data is read together, bounded in size, owned by one parent and rarely changed (embed), or shared, volatile or unbounded (reference).
4. `R + W > N` guarantees the read set overlaps the latest write; otherwise a read can hit only stale replicas.
5. During a network partition a distributed store must choose between consistency (refuse some requests) and availability (answer possibly stale data).
6. Different workloads (transactions, caching, search, analytics) are served best by different engines; the costs are synchronization and operational complexity.

</details>

[Back to NoSQL](README.md)
