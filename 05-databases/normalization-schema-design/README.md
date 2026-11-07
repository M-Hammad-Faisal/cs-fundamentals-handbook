# Normalization and Schema Design

## Detailed lesson (start here if you are new)

- [Normalization lab](01-normalization-lab.md): see the update/insert/delete anomalies, find functional dependencies with SQL, decompose to 3NF, prove it is lossless, many-to-many, when to denormalize

The rest of this page is the quick reference.

## 1. The concept

**Normalization** organizes tables so that each fact is stored **once**, in the right place. It removes redundancy and prevents the bugs that redundancy causes. **Schema design** is the wider craft of choosing tables, keys, types, and constraints so the database stays correct as it grows.

### Why redundancy hurts: the three anomalies

Imagine one wide table that mixes everything:

```sql
CREATE TABLE orders_flat (
    order_id       INTEGER,
    order_date     TEXT,
    customer_name  TEXT,
    customer_email TEXT,
    product        TEXT,
    product_price  INTEGER,
    quantity       INTEGER
);

INSERT INTO orders_flat VALUES
    (1, '2024-01-05', 'Acme Ltd', 'ops@acme.example', 'Keyboard', 50, 2),
    (1, '2024-01-05', 'Acme Ltd', 'ops@acme.example', 'Mouse',    20, 1),
    (2, '2024-02-11', 'Acme Ltd', 'ops@acme.example', 'Monitor', 300, 1);
```

| Anomaly | Problem in this table |
|---------|-----------------------|
| **Update anomaly** | Acme changes its email. You must update every row; miss one and the database contradicts itself. |
| **Insert anomaly** | You cannot record a new product until someone orders it (there is no row without an order). |
| **Delete anomaly** | Delete the only order for Monitor and you also lose the fact that Monitors cost 300. |

Normalization removes these by splitting the data so each fact lives in one place.

## 2. Functional dependencies and keys

Normal forms are defined with **functional dependencies**. `A -> B` means "if you know `A`, you know exactly one `B`".

In `orders_flat`:

- `order_id -> order_date, customer_name, customer_email`
- `customer_name -> customer_email` (assuming one email per customer)
- `product -> product_price`
- `(order_id, product) -> quantity`

The **candidate key** here is `(order_id, product)`: it determines every other column.

## 3. The normal forms

### First normal form (1NF): atomic values, no repeating groups

Each column holds a **single value**; no lists or arrays in a cell; each row is unique.

```text
Violates 1NF:  phones = '0300-1, 0321-2'        (two values in one cell)
Fix:           a separate customer_phones(customer_id, phone) table, one row per phone
```

### Second normal form (2NF): no partial dependencies

Applies to tables with a **composite key**. Every non-key column must depend on the **whole** key, not just part of it.

In `orders_flat` with key `(order_id, product)`:

- `order_date` depends only on `order_id` (part of the key): **partial dependency**.
- `product_price` depends only on `product`: **partial dependency**.

Fix: move them to their own tables (`orders`, `products`).

### Third normal form (3NF): no transitive dependencies

Non-key columns must depend **only on the key**, not on other non-key columns.

`order_id -> customer_name -> customer_email`: `customer_email` depends on the key only *through* `customer_name`. Move customer data to a `customers` table.

> Memory aid: every non-key attribute depends on **the key, the whole key, and nothing but the key**.

### Boyce-Codd normal form (BCNF)

A stricter 3NF: for every dependency `A -> B`, `A` must be a candidate key. It matters in rare cases where a table has overlapping candidate keys. Most designs that reach 3NF are already in BCNF.

### Higher forms (awareness)

- **4NF** removes multi-valued dependencies (independent many-to-many facts crammed into one table).
- **5NF** removes join dependencies.

In practice, aim for **3NF**, and break it deliberately only with a reason.

## 4. The normalized design

```sql
CREATE TABLE customers (
    id    INTEGER PRIMARY KEY,
    name  TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);

CREATE TABLE products (
    id    INTEGER PRIMARY KEY,
    name  TEXT NOT NULL UNIQUE,
    price INTEGER NOT NULL CHECK (price >= 0)
);

CREATE TABLE orders (
    id          INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    ordered_on  TEXT    NOT NULL
);

CREATE TABLE order_items (
    order_id   INTEGER NOT NULL REFERENCES orders(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity   INTEGER NOT NULL CHECK (quantity > 0),
    unit_price INTEGER NOT NULL,                  -- price at purchase time (history!)
    PRIMARY KEY (order_id, product_id)
);
```

Now a customer's email lives in **one row**, a product's price in **one row**, and `order_items` is the junction table for the many-to-many relationship between orders and products. Note `unit_price` in `order_items`: it deliberately **copies** the price at the time of purchase, because the product's price may change later and past orders must not change. That is not a normalization violation; it records a different fact (the price paid).

Recreate the original report with joins:

```sql
INSERT INTO customers VALUES (1, 'Acme Ltd', 'ops@acme.example');
INSERT INTO products VALUES (1, 'Keyboard', 50), (2, 'Mouse', 20), (3, 'Monitor', 300);
INSERT INTO orders VALUES (1, 1, '2024-01-05'), (2, 1, '2024-02-11');
INSERT INTO order_items VALUES (1, 1, 2, 50), (1, 2, 1, 20), (2, 3, 1, 300);

SELECT o.id AS order_id, o.ordered_on, c.name, c.email, p.name AS product, oi.quantity, oi.unit_price
FROM orders o
JOIN customers c    ON c.id = o.customer_id
JOIN order_items oi ON oi.order_id = o.id
JOIN products p     ON p.id = oi.product_id
ORDER BY o.id, p.name;
```

## 5. Denormalization: breaking the rules on purpose

Normalization optimizes **correctness and writes**; it costs **joins on reads**. **Denormalization** deliberately duplicates data to make hot reads faster.

| Technique | Example | Trade-off |
|-----------|---------|-----------|
| **Stored aggregate** | `orders.total` instead of summing items each time | Must keep in sync on every change |
| **Copying a column** | `orders.customer_name` for fast display | Can drift from the source |
| **Pre-joined / summary table** | A nightly `daily_sales` table | Stale until refreshed |
| **Materialized view** | A database-managed stored query result | Needs refresh |
| **Wide analytics tables** (star schema) | Fact table + dimension tables in warehouses | Redundant by design for scan speed |

Rule: **normalize first, measure, then denormalize only the proven hotspots** and put a mechanism (trigger, job, application code, materialized view refresh) in place to keep copies consistent.

## 6. Schema design guidelines

### Keys

- Give every table a **primary key**.
- **Surrogate keys** (integer or UUID ids) are stable and compact. **Natural keys** (email, ISBN) can change or be reused; if you use them, keep them `UNIQUE` rather than as the only identifier.
- **UUIDs** avoid central coordination and are hard to guess, but are larger and, if random, scatter inserts across index pages (UUIDv7 / time-ordered IDs help).

### Types and constraints

- Use the **right type**: integers for counts, `DECIMAL` or integer cents for **money** (never floating point), dates as real date types, booleans as booleans.
- Use `NOT NULL` by default; allow `NULL` only when "unknown/absent" is meaningful.
- Add `CHECK`, `UNIQUE`, and `FOREIGN KEY` constraints so the database enforces your rules.
- Choose **foreign key actions** deliberately: `ON DELETE CASCADE` (delete children), `SET NULL`, or `RESTRICT` (block the delete).

### Relationships

| Relationship | Pattern |
|--------------|---------|
| One-to-many | FK on the "many" side |
| Many-to-many | Junction table with a composite key (and extra columns such as `quantity`) |
| One-to-one | FK with `UNIQUE`, or share the primary key |
| Hierarchy (tree) | `parent_id` self-reference; recursive CTE to query; or closure table / materialized path for heavy reads |

### Common patterns

- **Soft delete:** `deleted_at TIMESTAMP NULL` instead of removing rows (keep history; remember to filter in every query, or use a view; partial unique indexes help).
- **Audit columns:** `created_at`, `updated_at`, `created_by`.
- **History / slowly changing data:** a separate history table, or `valid_from`/`valid_to` columns.
- **Enums:** a lookup table or a `CHECK` constraint; avoid magic numbers.
- **Polymorphic data:** prefer separate tables or a clear supertype/subtype design over a single column that means different things.
- **Avoid EAV (entity-attribute-value)** for core data: it loses types and constraints. Use JSON columns for genuinely sparse, flexible attributes.

### Naming

Be consistent: `snake_case`, singular or plural (pick one) table names, `id` for primary keys, `<table>_id` for foreign keys, descriptive index names.

## 7. Anti-patterns

| Anti-pattern | Why it hurts | Better |
|--------------|--------------|--------|
| Comma-separated values in a column | Cannot index, join, or constrain | Junction table |
| Storing computed totals that drift | Wrong numbers | Compute, or maintain carefully / materialized view |
| One giant table for everything | Update, insert, delete anomalies | Normalize |
| No foreign keys "for speed" | Orphan rows and silent corruption | Add FKs; index the FK columns |
| Floats for money | Rounding errors | `DECIMAL` or integer cents |
| Magic strings and numbers | Unclear, inconsistent values | Lookup tables or `CHECK` |
| `NULL` used as a value with hidden meaning | Three-valued-logic bugs | Explicit status columns |
| Premature denormalization | Complexity without evidence | Measure first |
| Overusing JSON for relational data | No constraints, hard to query and index | Real columns; JSON only for flexible extras |

## 8. A quick design process

1. **List the entities** (nouns): customer, product, order.
2. **List the facts and rules** (verbs and constraints): a customer places many orders; an order has many items; an item belongs to one product.
3. **Draw relationships** and cardinalities (1-1, 1-N, N-M).
4. **Assign primary keys,** then foreign keys.
5. **Normalize to 3NF,** check each non-key column depends on "the key, the whole key, and nothing but the key".
6. **Add constraints and types.**
7. **Add indexes** for the queries you will actually run (see [indexes](../indexes-query-plans/README.md)).
8. **Revisit for read-heavy hotspots** and denormalize deliberately if measurements demand it.

## 9. Two real-world examples

### Example 1: E-commerce catalogue and orders

A shop stores customers, products, orders and order items in separate tables. When a customer updates their email, one row changes and every report is correct instantly. When the price of a product changes, past orders still show what customers actually paid because `order_items.unit_price` captured it. The shop also keeps a denormalized `orders.total` (kept in sync by application code) so the order list loads without summing items for thousands of rows: a measured, deliberate denormalization.

### Example 2: Analytics warehouse with a star schema

A company's BI team does not query the normalized production database. They load data into a **star schema**: a central `fact_sales` table (one row per sale, with numeric measures and foreign keys) surrounded by `dim_date`, `dim_product`, `dim_customer` tables (descriptive attributes, often denormalized). This duplicates data on purpose so that scanning and aggregating billions of rows needs few joins. The production system optimizes writes with normalization; the warehouse optimizes reads with denormalization. Different workloads, different designs.

## 10. Tips, tricks and pitfalls

- **Normalize to 3NF by default,** denormalize with evidence.
- **Store each fact once.** If you copy it, know how the copy stays correct.
- **Capture "as of then" values** (price at purchase, address at shipment) in the transaction rows.
- **Index foreign keys;** they are used in joins and in cascaded deletes.
- **Constrain in the database,** not just in the application.
- **Plan for change:** use migrations (Alembic, Django migrations, Flyway), never hand-edit production schemas.
- **Be careful renaming and dropping columns;** deploy in compatible steps (add, backfill, switch code, remove).
- **Do not store lists in a cell;** use a related table.
- **Draw an ER diagram** before writing `CREATE TABLE`.
- **Think about scale early for the largest tables:** growth, partitioning, archival.

## 11. Check yourself

1. What are the update, insert and delete anomalies? Give an example of each.
2. State 1NF, 2NF and 3NF in one sentence each.
3. Why is `order_items.unit_price` not a normalization violation?
4. How do you model a many-to-many relationship?
5. When is denormalization appropriate, and what must you add alongside it?
6. Why should money not be stored as a float?
7. What is the difference between a surrogate key and a natural key?
8. What is a star schema and why is it denormalized?
9. What is wrong with storing `'red,green,blue'` in a single column?

<details>
<summary>Answers</summary>

1. Update: changing a customer's email requires editing many rows and risks inconsistency. Insert: you cannot record a product until it is ordered. Delete: deleting the last order for a product also loses its price.
2. 1NF: every column holds a single atomic value and rows are unique. 2NF: in addition, every non-key column depends on the whole composite key (no partial dependencies). 3NF: in addition, non-key columns depend only on the key, not on other non-key columns (no transitive dependencies).
3. It stores a different fact: the price paid at the time of purchase, which must not change when the product's current price changes.
4. With a junction table that has foreign keys to both sides, typically a composite primary key, plus any relationship attributes (such as quantity).
5. When measured read performance demands it (hot paths, analytics). Add a mechanism to keep the redundant data consistent: triggers, scheduled refresh, materialized views, or application logic.
6. Floating-point numbers cannot represent most decimal fractions exactly, causing rounding errors. Use `DECIMAL` or integer cents.
7. A surrogate key is an artificial identifier (auto-increment, UUID) with no business meaning; a natural key is a real-world attribute (email, ISBN) that identifies the row but may change.
8. A central fact table of measurable events joined to descriptive dimension tables. It duplicates attributes on purpose to minimize joins for large analytical scans.
9. It violates 1NF: you cannot index, join, constrain, or query individual values efficiently. Use a child table with one row per value.

</details>
