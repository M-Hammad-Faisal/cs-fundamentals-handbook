# NoSQL and Choosing a Database

## Detailed lessons

- [NoSQL lab](01-nosql-lab.md): a key-value store with TTL and LRU, documents (embed vs reference), an inverted-index search engine, quorums and CAP

The rest of this page is the quick reference.

## 1. The concept

**NoSQL** ("not only SQL") covers databases that do not use the classic relational table model. They appeared because some workloads strain relational databases: enormous scale across many machines, very high write rates, flexible or rapidly changing data shapes, and access patterns that are simpler than SQL's full power.

NoSQL is **not** "better than SQL". It trades some relational guarantees (joins, strict schemas, multi-row transactions) for scale, flexibility, or speed in a specific shape of workload. Most real systems use **both**.

## 2. The four main families (plus two)

| Family | Data model | Strengths | Examples |
|--------|-----------|-----------|----------|
| **Key-value** | `key -> value` (opaque blob) | Fastest lookups, simple, easy to scale | Redis, DynamoDB, Memcached |
| **Document** | `key -> JSON-like document` with nested fields | Flexible schema, one document holds a whole entity, queryable by fields | MongoDB, Couchbase, Firestore |
| **Wide-column** | Rows with many dynamic columns, grouped in column families; partitioned by key | Massive write throughput, time series, linear scale | Cassandra, HBase, Bigtable |
| **Graph** | Nodes and edges with properties | Relationship traversal (friends of friends, fraud rings) | Neo4j, Amazon Neptune |
| **Search engine** | Inverted index over documents | Full-text search, ranking, aggregations | Elasticsearch, OpenSearch |
| **Time-series** | Timestamped measurements | Efficient ingestion, downsampling, retention | InfluxDB, TimescaleDB, Prometheus |

### Key-value

```python
# Conceptually a dictionary on a server; Redis adds data structures and expiry
r.set("session:42", "{...}", ex=3600)      # expires in an hour
r.incr("page_views:home")                  # atomic counter
r.zadd("leaderboard", {"alice": 120})      # sorted set (a ranked list)
```

Typical uses: caches, sessions, rate limiters, leaderboards, queues.

### Document

```json
{
  "_id": "order-1001",
  "customer": { "id": 7, "name": "Acme Ltd" },
  "status": "shipped",
  "items": [
    { "product": "Keyboard", "qty": 2, "unit_price": 50 },
    { "product": "Mouse",    "qty": 1, "unit_price": 20 }
  ]
}
```

The whole order, including line items, is **one document**: one read, no joins. Documents in one collection need not share the same fields.

### Wide-column

Data is **partitioned** by a partition key and sorted within a partition by a clustering key. You design the table **around the query** ("all readings for sensor 17, newest first"), because ad hoc queries and joins are not supported.

### Graph

```text
(Alice)-[:FRIEND]->(Bob)-[:FRIEND]->(Carol)
MATCH (a:Person {name:'Alice'})-[:FRIEND*2]->(x) RETURN x     // friends of friends (Cypher)
```

In SQL this needs self-joins that get slower with every hop; graph databases follow pointers directly.

## 3. SQL vs NoSQL

| Aspect | Relational (SQL) | NoSQL (varies) |
|--------|------------------|----------------|
| Schema | Fixed, enforced | Flexible, often enforced by the app |
| Relationships | Joins | Embedding, references, denormalization |
| Transactions | Strong ACID across rows and tables | Often single-record or limited |
| Scaling | Vertical first; horizontal with effort | Designed for horizontal scale (sharding) |
| Queries | Powerful ad hoc SQL | Fast for the designed access patterns |
| Consistency | Strong by default | Tunable; often eventual |
| Best for | Complex relations, reporting, correctness | Huge scale, flexible data, simple access patterns |

Modern relational databases blur the line: PostgreSQL has `JSONB` (document-style storage with indexing), and many NoSQL systems now offer transactions and SQL-like languages.

## 4. Distributed-data fundamentals

### Replication

Keeping copies of data on several machines for availability and read scaling.

| Topology | Idea | Risk |
|----------|------|------|
| **Leader-follower** | Writes go to one leader and replicate to followers; reads can use followers | Followers may lag (stale reads); failover must be handled |
| **Multi-leader** | Several nodes accept writes | Write conflicts need resolution |
| **Leaderless** (Dynamo-style) | Any node accepts writes; clients use **quorums** | Needs read repair and conflict handling |

### Sharding (partitioning)

Splitting data across machines so no single machine holds or serves everything.

| Strategy | How | Trade-off |
|----------|-----|-----------|
| **Range** | Keys `A-M` on node 1, `N-Z` on node 2 | Range queries are easy; **hot spots** if keys are skewed (such as timestamps) |
| **Hash** | `hash(key) % N` picks the node | Even spread; range queries scatter |
| **Consistent hashing** | Nodes and keys on a ring; a key belongs to the next node clockwise | Adding or removing a node moves only about `1/N` of the keys |

Plain `hash(key) % N` is a trap: changing `N` remaps almost every key. Consistent hashing fixes that:

```python
import bisect
import hashlib

def h(value: str) -> int:
    return int(hashlib.md5(value.encode()).hexdigest(), 16)

class HashRing:
    def __init__(self, nodes, replicas=100):
        self.ring = []                       # sorted list of (hash, node)
        for node in nodes:
            self.add(node, replicas)

    def add(self, node, replicas=100):       # virtual nodes smooth the distribution
        for i in range(replicas):
            bisect.insort(self.ring, (h(f"{node}#{i}"), node))

    def remove(self, node):
        self.ring = [(k, n) for k, n in self.ring if n != node]

    def get(self, key):
        i = bisect.bisect(self.ring, (h(key), ""))
        return self.ring[i % len(self.ring)][1]

ring = HashRing(["db1", "db2", "db3"])
before = {k: ring.get(f"user:{k}") for k in range(1000)}
ring.add("db4")
moved = sum(before[k] != ring.get(f"user:{k}") for k in range(1000))
print(f"keys moved after adding a 4th node: {moved} of 1000")   # roughly 250, not 750
```

With `hash(key) % N`, going from 3 to 4 nodes would move about **75%** of the keys; with consistent hashing about **25%** (`1/4`).

### The CAP theorem

During a **network partition** (nodes cannot talk to each other), a distributed data store must choose between:

- **Consistency (C):** every read sees the latest write (or an error).
- **Availability (A):** every request gets a (possibly stale) response.

Partitions happen in real networks, so the real choice is **CP vs AP** when they occur. When there is no partition you trade **latency vs consistency** (the **PACELC** extension).

| Leaning | Behavior during a partition | Examples |
|---------|----------------------------|----------|
| **CP** | Refuses some requests to stay correct | MongoDB (default), HBase, ZooKeeper, etcd |
| **AP** | Keeps answering, may return stale data, reconciles later | Cassandra, DynamoDB (default), CouchDB |

### Consistency models

| Model | Guarantee |
|-------|-----------|
| **Strong / linearizable** | Behaves like a single copy; reads see the latest write |
| **Eventual** | If writes stop, all replicas converge eventually; reads may be stale meanwhile |
| **Read-your-writes** | You always see your own updates |
| **Causal** | Operations that are causally related are seen in order |
| **Tunable (quorum)** | With `N` replicas, write to `W` and read from `R`; if `R + W > N`, reads overlap the latest write |

**BASE** (Basically Available, Soft state, Eventually consistent) is the informal contrast to ACID for such systems.

## 5. Modeling data in a document store

Relational modeling starts from the **data** (normalize, then query any way you like). NoSQL modeling starts from the **queries** (shape data so the common reads are one lookup).

### Embed or reference?

| Embed (nested inside the parent) | Reference (store an id, look it up) |
|----------------------------------|-------------------------------------|
| Data is read together | Data is large, shared, or changes independently |
| One-to-few relationships | One-to-many (unbounded) or many-to-many |
| Child has no life of its own | Child needs its own queries and updates |
| Example: order lines inside an order | Example: a product referenced by many orders |

Two cautions: documents have size limits (MongoDB: 16 MB) and **unbounded arrays** (such as every comment on a viral post inside the post) grow without limit.

### Keep a copy where reads need it (and accept staleness)

An order embeds the customer's **name at the time of the order** and the product price paid. That is denormalization, and for historical records it is correct.

### Try it without a server: JSON in SQLite

```sql
CREATE TABLE events (id INTEGER PRIMARY KEY, doc TEXT NOT NULL);
INSERT INTO events (doc) VALUES
    ('{"type": "click",    "user": "ayesha", "page": "/home",  "ms": 120}'),
    ('{"type": "purchase", "user": "bilal",  "total": 70,      "items": ["Keyboard", "Mouse"]}'),
    ('{"type": "click",    "user": "bilal",  "page": "/cart",  "ms": 340}');

SELECT json_extract(doc, '$.user') AS user, COUNT(*) AS events
FROM events
GROUP BY json_extract(doc, '$.user');

SELECT json_extract(doc, '$.total') AS total
FROM events
WHERE json_extract(doc, '$.type') = 'purchase';

CREATE INDEX idx_events_type ON events (json_extract(doc, '$.type'));
```

This is the "flexible document" idea inside a relational database: no fixed columns, but you can still query and index fields. PostgreSQL's `JSONB` does the same with richer indexing (GIN).

## 6. Choosing a database

Start with the **access patterns, scale and consistency needs**, not the trend.

| Need | Good fit |
|------|----------|
| Complex relations, reporting, strong transactions | **Relational** (PostgreSQL, MySQL) |
| Caching, sessions, counters, leaderboards, rate limiting | **Key-value** (Redis) |
| Flexible, nested entities read as a unit | **Document** (MongoDB, or PostgreSQL JSONB) |
| Huge write volume, time-ordered data, predictable queries | **Wide-column** (Cassandra) or **time-series** |
| Deep relationship queries (recommendations, fraud, network analysis) | **Graph** (Neo4j) |
| Text search, relevance ranking, log analytics | **Search engine** (Elasticsearch/OpenSearch) |
| Analytics across billions of rows | **Columnar warehouse** (BigQuery, Snowflake, ClickHouse) |

### Polyglot persistence

Real products combine stores, each used for what it does best:

```
PostgreSQL  -> source of truth (users, orders, payments)
Redis       -> cache, sessions, rate limits
Elasticsearch -> product search
Kafka       -> event stream between them
Warehouse   -> analytics
```

The price is **operational complexity** and keeping copies consistent (events, change-data-capture, the outbox pattern from [transactions](../transactions-acid/README.md)). Do not add a store unless the need is real.

### A sensible default

**Start with PostgreSQL.** It handles relational data, JSON documents, full-text search, time series (with extensions), and queues surprisingly well, and it scales further than most projects ever need. Add a specialized store when you can show a specific bottleneck.

## 7. Two real-world examples

### Example 1: Session store and rate limiter with Redis

A web app with many servers stores login sessions in Redis rather than in each server's memory, so any server can handle any request and a deploy does not log everyone out. It also uses Redis for **rate limiting**: `INCR` a key like `rate:user42:minute` with a 60-second expiry; if the count exceeds 100, reject. Both rely on key-value lookups in microseconds, atomic increments, and automatic expiry, all things a relational database does poorly at that speed.

### Example 2: IoT and metrics ingestion with Cassandra or a time-series database

Millions of sensors or servers each send a reading every few seconds, producing hundreds of thousands of writes per second, almost all appends, queried as "this device's readings for the last hour". A wide-column store partitions by `(device_id, day)` and sorts by timestamp, so writes spread evenly across nodes and a query reads one contiguous partition. It scales by adding machines and tolerates node failures, at the cost of giving up ad hoc joins and strong cross-row transactions. The same shape underlies monitoring systems and activity feeds.

## 8. Tips, tricks and pitfalls

- **"NoSQL scales, SQL doesn't" is a myth.** A single PostgreSQL server handles a lot; scale problems are rarer than people think.
- **Model for your queries in NoSQL.** Changing access patterns later can mean rewriting your data.
- **No schema does not mean no structure.** Without one, the application must validate, or data quality rots. Use schema validation features.
- **Beware unbounded arrays** and giant documents.
- **Eventual consistency is a product decision.** Decide where stale reads are acceptable (like counts) and where they are not (account balances).
- **Hot partitions** (a celebrity user, a timestamp key) break even sharding. Choose high-cardinality, well-distributed keys.
- **Use consistent hashing** (not `hash % N`) when nodes come and go.
- **Idempotent writes and retries:** distributed systems fail partially; design operations so repeating them is safe.
- **Do not use a cache as the source of truth;** it can be evicted or lost.
- **Pick boring technology first,** and justify each additional database.

## 9. Check yourself

1. Name the main NoSQL families and one use case for each.
2. What does the CAP theorem say, and what is the real choice in practice?
3. What is eventual consistency? Give an example where it is fine and one where it is not.
4. How does consistent hashing improve on `hash(key) % N`?
5. When do you embed data in a document, and when do you reference it?
6. What is the quorum rule `R + W > N`?
7. Why might you pick PostgreSQL even for semi-structured data?
8. What is polyglot persistence and what does it cost?
9. What is a hot partition and how do you avoid one?

<details>
<summary>Answers</summary>

1. Key-value (cache, sessions), document (flexible entities like orders), wide-column (high-volume time-ordered writes), graph (relationship traversal such as fraud or recommendations), search engine (full-text search), time-series (metrics).
2. During a network partition a system must choose between consistency (return correct data or an error) and availability (always respond, possibly stale). Partitions are unavoidable, so the real choice is CP vs AP when one occurs (and latency vs consistency otherwise).
3. Replicas converge over time if writes stop; reads may be briefly stale. Fine for like counts or a social feed; not fine for an account balance or inventory that must not oversell.
4. With `hash % N`, changing `N` remaps almost all keys. With consistent hashing on a ring, adding or removing a node moves only about `1/N` of the keys.
5. Embed when data is read together, is one-to-few, and has no independent life. Reference when data is large, shared, unbounded, or updated independently.
6. With `N` replicas, writing to `W` and reading from `R` such that `R + W > N` guarantees the read set overlaps the write set, so a read sees the latest acknowledged write.
7. It supports relational data, JSONB documents, full-text search and more, with strong transactions, and scales far for most workloads, so it avoids the operational cost of an extra database.
8. Using several specialized databases, each for what it is best at. The cost is operational complexity and keeping copies in sync (events, change-data-capture, outbox).
9. A partition that receives disproportionate traffic (a popular key or monotonically increasing key). Avoid it with well-distributed, high-cardinality partition keys, hashing, or key salting.

</details>

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

Back to the [part overview](../README.md).
