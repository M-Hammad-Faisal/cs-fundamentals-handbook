# Normalization Lab: From a Messy Table to a Clean Schema

**Prerequisites:** [SQL first steps](../relational-sql/01-sql-first-steps.md), [aggregation and joins](../relational-sql/02-aggregation-and-joins-lab.md). **You will learn (by doing it on real data):** why putting everything in one big table causes **update, insert and delete anomalies**, how to detect **functional dependencies** with SQL, how to **decompose** the table into a clean schema (**1NF, 2NF, 3NF**), how to prove the split **loses no information** (a lossless join), how to model **many-to-many** relationships, and when it is right to **denormalize** on purpose.

## 1. In plain words

Imagine one spreadsheet holding every order, repeating each customer's name, email and city on every row. It works until a customer changes their email: you must fix it on dozens of rows, and if you miss one, the sheet **contradicts itself**. **Normalization** is the discipline of storing **each fact once**, in the place where it belongs, and linking tables with keys. The slogan: *"Every non-key column depends on the key, the whole key, and nothing but the key."*

## 2. The messy table

```python
import sqlite3

db = sqlite3.connect(":memory:")
db.execute("PRAGMA foreign_keys = ON")
db.execute("""CREATE TABLE orders_flat (
    order_id       INTEGER NOT NULL,                 -- key columns must be NOT NULL (SQLite would otherwise allow NULLs in a composite key)
    customer_name  TEXT,
    customer_email TEXT,
    customer_city  TEXT,
    product        TEXT    NOT NULL,
    product_price  INTEGER,
    quantity       INTEGER,
    PRIMARY KEY (order_id, product)
)""")
rows = [
    (1, "Ana",  "ana@mail.com",  "Lahore",  "Keyboard", 50,   2),
    (1, "Ana",  "ana@mail.com",  "Lahore",  "Mouse",    20,   1),
    (2, "Ana",  "ana@mail.com",  "Lahore",  "Monitor",  300,  1),
    (3, "Bilal", "bilal@mail.com", "Karachi", "Keyboard", 50,   1),
    (4, "Chen", "chen@mail.com", "Lahore",  "Laptop",   1200, 1),
    (4, "Chen", "chen@mail.com", "Lahore",  "Mouse",    20,   3),
]
db.executemany("INSERT INTO orders_flat VALUES (?, ?, ?, ?, ?, ?, ?)", rows)
db.commit()

def q(sql, *params):
    return db.execute(sql, params).fetchall()

for r in q("SELECT * FROM orders_flat ORDER BY order_id, product"):
    print(r)
# (1, 'Ana', 'ana@mail.com', 'Lahore', 'Keyboard', 50, 2)
# (1, 'Ana', 'ana@mail.com', 'Lahore', 'Mouse', 20, 1)
# (2, 'Ana', 'ana@mail.com', 'Lahore', 'Monitor', 300, 1)
# (3, 'Bilal', 'bilal@mail.com', 'Karachi', 'Keyboard', 50, 1)
# (4, 'Chen', 'chen@mail.com', 'Lahore', 'Laptop', 1200, 1)
# (4, 'Chen', 'chen@mail.com', 'Lahore', 'Mouse', 20, 3)
```

The key is `(order_id, product)`. Notice the repetition: Ana's email appears three times, the keyboard's price twice, the mouse's price twice.

## 3. The three anomalies

### Update anomaly: change one fact, forget another

```python
db.execute("UPDATE orders_flat SET customer_email = 'ana.new@mail.com' WHERE order_id = 1 AND product = 'Keyboard'")   # a buggy partial update
print(q("SELECT DISTINCT customer_email FROM orders_flat WHERE customer_name = 'Ana'"))
# [('ana.new@mail.com',), ('ana@mail.com',)]       Ana now has two emails: the data contradicts itself
db.rollback()
```

Because the email is stored **in many rows**, a change must touch all of them; a bug, a crash or a second application that forgets leaves inconsistent data. Which email is right?

### Insert anomaly: cannot record a fact without an unrelated one

```python
try:
    db.execute("INSERT INTO orders_flat (customer_name, customer_email, customer_city) VALUES ('Dina', 'dina@mail.com', 'Multan')")
except sqlite3.IntegrityError as e:
    print("cannot add a new customer:", e)
# cannot add a new customer: NOT NULL constraint failed: orders_flat.order_id    (a customer exists only as part of an order row)
db.rollback()
```

You cannot store a new **customer** (or a new **product** on the shelf) until they appear in an order, because the table's key demands an order and a product.

### Delete anomaly: removing one fact destroys another

```python
db.execute("DELETE FROM orders_flat WHERE order_id = 3")                       # cancel Bilal's only order
print(q("SELECT * FROM orders_flat WHERE customer_name = 'Bilal'"))            # []     Bilal, his email and his city are GONE with the order
db.rollback()
```

Deleting the order also deleted everything we knew about the customer.

**Root cause:** the table mixes **several different kinds of facts** (about customers, about products, about order lines), and the non-key columns depend on only *part* of the key or on other non-key columns.

## 4. Functional dependencies: the formal tool

`A -> B` ("A determines B") means: whenever two rows have the same `A`, they must have the same `B`. Examples here: `customer_name -> customer_email, customer_city`; `product -> product_price`; `order_id -> customer_name`.

You can **test a dependency against the data** with SQL: if any `A` maps to more than one `B`, the dependency fails.

```python
def holds(determinant, dependent, table="orders_flat"):
    sql = f"SELECT COUNT(*) FROM (SELECT {determinant} FROM {table} GROUP BY {determinant} HAVING COUNT(DISTINCT {dependent}) > 1)"
    return db.execute(sql).fetchone()[0] == 0                                  # no counterexample found in this data

print(holds("customer_name", "customer_email"))                                # True    each customer has one email
print(holds("product", "product_price"))                                       # True    each product has one price
print(holds("order_id", "customer_name"))                                      # True    each order belongs to one customer
print(holds("customer_name", "product"))                                       # False   a customer buys several products (not a dependency)
print(holds("customer_city", "customer_name"))                                 # False   many customers share a city
```

(Data can only **disprove** a dependency; "True" means "no counterexample yet". The real source of truth is the meaning of the business rules.)

A **key** is a column set that determines every other column. A **candidate key** is a minimal key. Here `(order_id, product)` is the key.

## 5. The normal forms, step by step

### First normal form (1NF): atomic values, no repeating groups

Each cell holds **one value**; no lists in a cell, no `product1, product2, product3` columns.

```text
BAD (not 1NF)                          GOOD (1NF)
order | products                        order | product
1     | Keyboard, Mouse                 1     | Keyboard
                                        1     | Mouse
```

Our `orders_flat` is already in 1NF (one product per row).

### Second normal form (2NF): no partial dependency on part of a composite key

If the key has several columns, every non-key column must depend on **the whole key**, not just part of it. Violations in `orders_flat`:

- `product_price` depends only on `product` (**part** of the key `(order_id, product)`).
- `customer_name`, `customer_email`, `customer_city` depend only on `order_id` (part of the key).

Only `quantity` depends on the **whole** key (how many of *this product* in *this order*).

**Fix:** move the partially dependent columns into their own tables.

```text
products(product, price)            orders(order_id, customer...)            order_items(order_id, product, quantity)
```

### Third normal form (3NF): no transitive dependency

A non-key column must not depend on **another non-key column**. After the 2NF split, `orders(order_id, customer_name, customer_email, customer_city)` still has `order_id -> customer_name -> customer_email, customer_city`: the email depends on the customer, not on the order. **Fix:** a separate `customers` table.

(Boyce-Codd normal form (BCNF) is a slightly stricter 3NF for rare cases with overlapping candidate keys; 3NF is the practical target.)

## 6. The normalized schema

```python
db.executescript("""
CREATE TABLE customers (
    id    INTEGER PRIMARY KEY,
    name  TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    city  TEXT NOT NULL
);
CREATE TABLE products (
    id    INTEGER PRIMARY KEY,
    name  TEXT NOT NULL UNIQUE,
    price INTEGER NOT NULL CHECK (price >= 0)
);
CREATE TABLE orders (
    id          INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id)
);
CREATE TABLE order_items (
    order_id   INTEGER NOT NULL REFERENCES orders(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity   INTEGER NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (order_id, product_id)
);
""")
```

### Migrate the data (decompose)

```python
db.execute("INSERT INTO customers (name, email, city) SELECT DISTINCT customer_name, customer_email, customer_city FROM orders_flat ORDER BY customer_name")
db.execute("INSERT INTO products (name, price) SELECT DISTINCT product, product_price FROM orders_flat ORDER BY product")
db.execute("""INSERT INTO orders (id, customer_id)
              SELECT DISTINCT f.order_id, c.id FROM orders_flat f JOIN customers c ON c.email = f.customer_email""")
db.execute("""INSERT INTO order_items (order_id, product_id, quantity)
              SELECT f.order_id, p.id, f.quantity FROM orders_flat f JOIN products p ON p.name = f.product""")
db.commit()

for table in ("customers", "products", "orders", "order_items"):
    print(f"{table:12}", q(f"SELECT COUNT(*) FROM {table}")[0][0], "rows")
# customers    3 rows
# products     4 rows
# orders       4 rows
# order_items  6 rows
```

Each fact now lives **once**: three customers instead of six repeated customer cells, four products with one price each.

### Is it lossless? Reconstruct the original

A decomposition must be **lossless**: joining the pieces back must give exactly the original table (no rows lost, none invented).

```python
rebuilt = q("""
    SELECT o.id, c.name, c.email, c.city, p.name, p.price, i.quantity
    FROM order_items i
    JOIN orders o    ON o.id = i.order_id
    JOIN customers c ON c.id = o.customer_id
    JOIN products p  ON p.id = i.product_id
    ORDER BY o.id, p.name""")
original = q("SELECT * FROM orders_flat ORDER BY order_id, product")
print(rebuilt == original)                                                       # True   the join reproduces the flat table exactly
```

A split is lossless when the shared column (the join column) is a **key** of at least one of the two parts, which is exactly what we did. Splitting on a non-key column can invent false rows (a "lossy" decomposition).

## 7. The anomalies are gone

```python
# Update: one place
db.execute("UPDATE customers SET email = 'ana.new@mail.com' WHERE name = 'Ana'")
print(q("""SELECT DISTINCT c.email FROM order_items i JOIN orders o ON o.id = i.order_id
           JOIN customers c ON c.id = o.customer_id WHERE c.name = 'Ana'"""))     # [('ana.new@mail.com',)]   every order sees the new email

# Insert: customers and products exist without orders
db.execute("INSERT INTO customers (name, email, city) VALUES ('Dina', 'dina@mail.com', 'Multan')")
db.execute("INSERT INTO products (name, price) VALUES ('Webcam', 80)")
print(q("SELECT name FROM customers ORDER BY name"))                             # [('Ana',), ('Bilal',), ('Chen',), ('Dina',)]

# Delete: removing an order keeps the customer
db.execute("DELETE FROM order_items WHERE order_id = 3")
db.execute("DELETE FROM orders WHERE id = 3")
print(q("SELECT name, city FROM customers WHERE name = 'Bilal'"))                # [('Bilal', 'Karachi')]   Bilal is still known
db.commit()
```

And the database now **enforces integrity**: foreign keys prevent orphans, `UNIQUE(email)` prevents duplicate customers, `CHECK` rules apply once.

```python
for sql in ("INSERT INTO orders VALUES (99, 12345)",                              # customer does not exist
            "INSERT INTO customers (name, email, city) VALUES ('Fake', 'ana.new@mail.com', 'X')",      # duplicate email
            "DELETE FROM customers WHERE name = 'Ana'"):                          # Ana still has orders
    try:
        db.execute(sql)
    except sqlite3.IntegrityError as e:
        print("blocked:", e)
# blocked: FOREIGN KEY constraint failed
# blocked: UNIQUE constraint failed: customers.email
# blocked: FOREIGN KEY constraint failed
db.rollback()
```

## 8. Many-to-many relationships need a junction table

A student takes many courses; a course has many students. You cannot put a list in a column (breaks 1NF); you create a **junction (link) table** whose key is the pair, and which can carry attributes of the relationship itself:

```python
db.executescript("""
CREATE TABLE students (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE courses  (id INTEGER PRIMARY KEY, title TEXT NOT NULL);
CREATE TABLE enrollments (
    student_id INTEGER NOT NULL REFERENCES students(id),
    course_id  INTEGER NOT NULL REFERENCES courses(id),
    grade      TEXT,                       -- belongs to the RELATIONSHIP (this student in this course)
    PRIMARY KEY (student_id, course_id)
);
INSERT INTO students VALUES (1, 'Ana'), (2, 'Bilal');
INSERT INTO courses  VALUES (1, 'Algorithms'), (2, 'Databases');
INSERT INTO enrollments VALUES (1, 1, 'A'), (1, 2, 'B'), (2, 2, 'A');
""")
print(q("""SELECT s.name, c.title, e.grade FROM enrollments e
           JOIN students s ON s.id = e.student_id JOIN courses c ON c.id = e.course_id ORDER BY s.name, c.title"""))
# [('Ana', 'Algorithms', 'A'), ('Ana', 'Databases', 'B'), ('Bilal', 'Databases', 'A')]
print(q("SELECT c.title, COUNT(*) AS students FROM enrollments e JOIN courses c ON c.id = e.course_id GROUP BY c.id ORDER BY c.id"))
# [('Algorithms', 1), ('Databases', 2)]
```

| Relationship | How to model it |
|--------------|-----------------|
| **One-to-many** (one customer, many orders) | foreign key on the "many" side (`orders.customer_id`) |
| **Many-to-many** (students and courses) | junction table with two foreign keys |
| **One-to-one** (user and profile) | foreign key with `UNIQUE`, or merge into one table |
| **Hierarchy** (employee and manager) | self-referencing foreign key (`manager_id -> employees.id`) |

## 9. Design guidelines

1. **One table per entity** (customers, products), **one row per fact**, **one column per attribute**.
2. Choose a **primary key** that never changes: a surrogate integer or UUID is safer than a natural key like email.
3. Store **raw facts, not derived values** (store `quantity` and `unit_price`, compute `total` in queries), unless a deliberate cache is documented.
4. Use proper **types** (integers of cents or `DECIMAL` for money, real dates), `NOT NULL` wherever a value is mandatory, `UNIQUE`/`CHECK`/foreign keys to put rules in the database.
5. **Prices at order time** belong on the order line (`unit_price` in `order_items`), because the product's current price may change later while history must not (a legitimate "copy" of a fact: it is a *different fact*, the price charged).
6. Avoid **EAV** (entity-attribute-value tables) and **comma-separated lists** in a column; avoid **one table per month** (use partitioning).
7. Name consistently (`customer_id`, plural or singular tables, not both).

## 10. Denormalization: breaking the rules on purpose

Normalized schemas need **joins**; at very large read volumes joins can be expensive. **Denormalizing** means deliberately duplicating data to make a critical read faster, accepting the cost of keeping copies in sync.

```python
db.executescript("""
CREATE TABLE order_totals (          -- a derived summary table for dashboards: one row per order
    order_id INTEGER PRIMARY KEY,
    customer_name TEXT NOT NULL,
    total INTEGER NOT NULL
);
INSERT INTO order_totals
SELECT o.id, c.name, SUM(i.quantity * p.price)
FROM orders o JOIN customers c ON c.id = o.customer_id
JOIN order_items i ON i.order_id = o.id JOIN products p ON p.id = i.product_id
GROUP BY o.id;
""")
print(q("SELECT * FROM order_totals ORDER BY order_id"))                          # [(1, 'Ana', 120), (2, 'Ana', 300), (4, 'Chen', 1260)]
```

Now the dashboard reads one table with no joins. The price you pay: whenever an order changes, `order_totals` must be updated too (a trigger, application code, or a periodic rebuild), or it goes stale. Common legitimate forms: **summary/aggregate tables**, **materialized views**, **cached counts** (`comments_count` on a post), **search indexes**, **data warehouse star schemas**, and **document stores** that embed related data. Rule: **normalize first; denormalize only for a measured read bottleneck, and document how the copy stays correct.**

| | Normalized | Denormalized |
|---|-----------|--------------|
| Writes | simple and consistent | must update copies |
| Reads | need joins | fast, simple |
| Storage | smaller | larger |
| Risk | slow complex reads | stale or contradictory data |
| Typical home | OLTP (apps, transactions) | analytics, caches, read models, NoSQL |

## 11. Two real-world examples

**Example 1: A shop that kept the customer address on every order.** A customer moved; support updated the address in the account page but the shipping system read the copy on the order and sent parcels to the old address. The fix was to normalize: the address lives in one place, and the **shipping address at purchase time** is intentionally stored as a snapshot on the order (a different fact: where *this* parcel went).

**Example 2: A social network's like counter.** Counting likes with `SELECT COUNT(*) FROM likes WHERE post_id = ?` over billions of rows is too slow, so each post stores a denormalized `likes_count`, updated asynchronously. It may briefly disagree with the real count: an accepted trade-off, with a periodic job that recomputes counts from the source table.

## 12. Common mistakes

- Repeating the same fact (customer email) in many rows.
- Storing lists in a column (`"red,green,blue"`) or numbered columns (`phone1`, `phone2`, `phone3`).
- Using a changeable natural key (email, phone) as the primary key.
- Storing derived values (totals, ages) without a plan to keep them correct.
- Skipping foreign keys and constraints "for speed" and then living with orphan rows.
- Over-normalizing into dozens of tiny tables for no benefit (joins everywhere).
- Denormalizing too early, before measuring a problem.
- Not deciding, fact by fact, whether a copy is a deliberate **historical snapshot** (the price charged on that order) or an accidental duplicate that must stay in sync (the customer's current email).

## 13. Practice

1. Which anomaly occurs if you store `department_name` in every `employees` row and rename a department?
2. A table `enrollment(student_id, course_id, student_name, grade)` has key `(student_id, course_id)`. Which normal form does it violate and why? Give the fix.
3. A table `book(isbn, title, publisher, publisher_country)` has key `isbn`. Which dependency violates 3NF?
4. Design tables for: authors write many books and a book can have many authors.
5. Why can a lossless decomposition be verified with a join?
6. When would you add a denormalized `comments_count` to `posts`?
7. Run `holds("customer_city", "customer_email")` on `orders_flat`. Explain the answer in business terms.

<details>
<summary>Solutions</summary>

1. An **update anomaly**: renaming requires updating every row; missing some leaves inconsistent names. (Fix: a `departments` table referenced by a foreign key.)
2. **2NF**: `student_name` depends only on `student_id` (part of the key). Fix: `students(id, name)` and `enrollment(student_id, course_id, grade)`.
3. `publisher -> publisher_country`: a non-key column (`publisher_country`) depends on another non-key column (`publisher`): a transitive dependency. Fix: `publishers(id, name, country)` and `book(isbn, title, publisher_id)`.
4. ```sql
   authors(id, name)
   books(id, title)
   book_authors(book_id REFERENCES books, author_id REFERENCES authors, PRIMARY KEY (book_id, author_id))   -- junction table
   ```
5. Joining the parts back on the shared key must reproduce exactly the original rows; if rows are missing or extra rows appear, the decomposition lost information.
6. When counting rows on every page view is too slow (large tables, high read volume): keep a counter updated by a trigger or a background job and recompute it periodically to correct drift.
7. ```python
   print(holds("customer_city", "customer_email"))                              # False    several customers (with different emails) live in Lahore
   ```
   A city does not determine an email, so it must not be used as a key for customer data.

</details>

## 14. Check yourself

1. What are the update, insert and delete anomalies?
2. State 1NF, 2NF and 3NF in one sentence each.
3. What is a functional dependency?
4. How do you model a many-to-many relationship?
5. What does "lossless decomposition" mean?
6. Why and when do we denormalize?

<details>
<summary>Answers</summary>

1. Update: a duplicated fact changed in only some places. Insert: a fact cannot be stored without an unrelated one. Delete: deleting one fact removes another.
2. 1NF: one atomic value per cell, no repeating groups. 2NF: every non-key column depends on the whole key. 3NF: no non-key column depends on another non-key column.
3. `A -> B`: the value of `A` determines the value of `B` (equal `A` means equal `B`).
4. With a junction table holding foreign keys to both sides (and any attributes of the relationship), with a composite primary key.
5. Joining the split tables back gives exactly the original data, with nothing lost or invented.
6. To speed up measured read bottlenecks by duplicating or precomputing data, accepting extra write work and the risk of staleness.

</details>

[Back to normalization and schema design](README.md)
