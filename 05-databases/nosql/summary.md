# NoSQL and Choosing a Database: One-Page Summary

## Families
| Family | Use it for | Examples |
|--------|-----------|----------|
| Key-value | Cache, sessions, counters, rate limits | Redis, DynamoDB |
| Document | Flexible, nested entities | MongoDB, PostgreSQL JSONB |
| Wide-column | Huge write volume, time-ordered, known queries | Cassandra, HBase |
| Graph | Relationship traversal | Neo4j |
| Search | Full-text, relevance | Elasticsearch/OpenSearch |
| Time-series | Metrics, IoT | InfluxDB, TimescaleDB |

## SQL vs NoSQL
Relational = strong schema, joins, ACID, ad hoc queries. NoSQL = flexible schema, horizontal scale, designed-for access patterns, often eventual consistency. Boundaries blur (JSONB, transactions in NoSQL).

## Distributed basics
- **Replication:** leader-follower, multi-leader, leaderless (quorums).
- **Sharding:** range (hot spots), hash (no range queries), **consistent hashing** (add/remove a node moves ~`1/N` of keys; `hash % N` moves most).
- **CAP:** during a partition choose **C** or **A** (CP vs AP). **PACELC:** otherwise latency vs consistency.
- **Consistency models:** strong, eventual, read-your-writes, causal. **Quorum:** `R + W > N`.
- **BASE** vs **ACID**.

## Modeling documents
Model for **queries**. **Embed** data read together (one-to-few); **reference** large, shared, unbounded or independently updated data. Avoid unbounded arrays; copy "as-of" values deliberately.

## Choosing
Start with the access pattern, scale and consistency need. **Default to PostgreSQL**; add specialized stores for proven bottlenecks. Polyglot persistence = more power, more operational complexity.

## Pitfalls
Myth "SQL doesn't scale" · no schema ≠ no structure · hot partitions · treating a cache as the source of truth · ignoring where stale reads are unacceptable.

[Lesson](README.md) · [Exercises](exercises.md)
