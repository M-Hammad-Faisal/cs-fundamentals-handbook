# NoSQL and Choosing a Database: Exercises

## Choosing
1. Pick the best-fit database family for each and justify it in one sentence:
   - a) Storing login sessions that expire after 30 minutes.
   - b) Bank account balances with transfers between accounts.
   - c) Full-text product search with ranking.
   - d) 500,000 temperature readings per second from sensors, queried by device and time range.
   - e) "Which users are within three hops of a flagged account?"
   - f) A CMS where each content type has different fields.
2. A startup says "let's use MongoDB because we need to scale." What questions would you ask first?

## Modeling
3. Model a **blog post with comments** as documents. Decide what to embed and what to reference, and say what would change if a post could get a million comments.
4. Design a **Cassandra-style table** (partition key and clustering key) for "the latest 50 messages in a chat room".
5. Show how to store and query a nested `order` JSON document in SQLite using `json_extract`, and index one field.

## Distributed concepts
6. With `N = 3` replicas, list `(W, R)` choices that give strong reads, fast writes, and fast reads, and say what each trades off.
7. Using the `HashRing` from the lesson, compare how many of 10,000 keys move when going from 4 to 5 nodes with consistent hashing versus `hash(key) % N`.
8. Describe what happens to a CP system and an AP system during a network partition, using a shopping cart and a bank transfer as examples.
9. Explain how you would keep a Redis cache and a PostgreSQL database consistent. What happens if the cache is stale?

<details>
<summary>Solutions</summary>

**1.** a) Key-value (Redis): fast reads with built-in expiry. b) Relational: needs multi-row ACID transactions. c) Search engine (Elasticsearch/OpenSearch): inverted index and relevance ranking. d) Wide-column or time-series database: very high append rate, partitioned by device and time. e) Graph database: multi-hop traversal. f) Document store (or PostgreSQL JSONB): flexible per-type fields.

**2.** What are the access patterns? What data volume and write rate (is it truly beyond one PostgreSQL server)? Do we need multi-row transactions or joins? What consistency is acceptable? What does the team know how to operate? Often a relational database (possibly with JSONB) is enough, and MongoDB is chosen because of document-shaped data rather than scale alone.

**3.** Embed a few recent comments (or a comment count) in the post for fast display; store each comment as its own document that references `post_id`, because comments are unbounded and need their own paging, edits and moderation. With a million comments, never embed them all: keep them in a separate collection indexed by `(post_id, created_at)` and paginate.

**4.**
```text
CREATE TABLE messages_by_room (
    room_id    uuid,
    sent_at    timeuuid,
    sender_id  uuid,
    body       text,
    PRIMARY KEY ((room_id), sent_at)
) WITH CLUSTERING ORDER BY (sent_at DESC);

SELECT * FROM messages_by_room WHERE room_id = ? LIMIT 50;
```
The partition key `room_id` keeps a room's messages together; the clustering key sorts them newest first so the query reads one contiguous slice. (Very busy rooms may need a bucketed key such as `(room_id, day)` to bound partition size.)

**5.**
```sql
CREATE TABLE orders (id INTEGER PRIMARY KEY, doc TEXT NOT NULL);
INSERT INTO orders (doc) VALUES ('{"status":"shipped","customer":{"name":"Acme"},"items":[{"product":"Keyboard","qty":2}]}');
SELECT json_extract(doc, '$.customer.name'), json_extract(doc, '$.items[0].product') FROM orders
WHERE json_extract(doc, '$.status') = 'shipped';
CREATE INDEX idx_orders_status ON orders (json_extract(doc, '$.status'));
```

**6.** Strong reads: `R + W > N`, such as `W = 2, R = 2` (balanced) or `W = 3, R = 1` (slow writes, fast reads, but writes fail if any replica is down) or `W = 1, R = 3` (fast writes, slow reads). Fast reads and writes with only eventual consistency: `W = 1, R = 1` (`R + W <= N`, stale reads possible).

**7.**
```python
import bisect, hashlib
def h(v): return int(hashlib.md5(v.encode()).hexdigest(), 16)
class HashRing:
    def __init__(self, nodes, replicas=100):
        self.ring = []
        for n in nodes: self.add(n, replicas)
    def add(self, node, replicas=100):
        for i in range(replicas): bisect.insort(self.ring, (h(f"{node}#{i}"), node))
    def get(self, key):
        i = bisect.bisect(self.ring, (h(key), ""))
        return self.ring[i % len(self.ring)][1]

keys = [f"k{i}" for i in range(10000)]
ring = HashRing([f"n{i}" for i in range(4)]); before = {k: ring.get(k) for k in keys}
ring.add("n4"); ring_moved = sum(before[k] != ring.get(k) for k in keys)
mod_moved = sum(h(k) % 4 != h(k) % 5 for k in keys)
print(ring_moved, mod_moved)     # roughly 2,000 (about 1/5) versus roughly 8,000 (about 4/5)
```

**8.** A CP system stops accepting some requests (for example the minority side of the partition) to avoid conflicting or stale data: for a bank transfer this is right, because refusing a transfer is better than a wrong balance. An AP system keeps serving both sides and reconciles later: for a shopping cart this is fine, because merging two carts is better than an error page (the Dynamo paper's classic example).

**9.** Treat PostgreSQL as the source of truth. Use cache-aside: on a read, check Redis, on a miss read the database and store the value with a TTL; on a write, update the database first, then delete (invalidate) the cache key. A stale cache returns old data until the TTL expires or the key is invalidated, so set TTLs to bound staleness, and never read-modify-write from the cache. For stricter guarantees publish invalidation events (change-data-capture or outbox).

</details>

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [NoSQL Lab](01-nosql-lab.md)
