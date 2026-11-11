# Normalization and Schema Design: Exercises

These problems go with the [Normalization and Schema Design lesson](README.md). Try each one before opening its solution.

## Problems

### Normalization
1. This table stores `(student_id, course_id, student_name, course_title, instructor, instructor_office, grade)` with key `(student_id, course_id)`. List the functional dependencies, identify the 2NF and 3NF violations, and write a normalized schema.
2. A `contacts` table has a column `phones` holding `'0300-111, 0321-222'`. Which normal form does it violate? Redesign it.
3. A table `employee(id, name, department_id, department_name, department_head)`. Which dependency is transitive? Fix it.
4. Explain why `order_items.unit_price` should be stored even though `products.price` exists.

### Design from requirements
5. **Library:** members borrow books; each book can have several authors; each author can write several books; a member can borrow many copies over time; track due and return dates. Design tables and keys.
6. **Blog:** users write posts; posts have tags (many-to-many); users comment on posts; comments can reply to other comments. Design the schema.
7. **Hospital:** doctors, patients, appointments (a doctor sees one patient per time slot). Add the constraint that prevents double-booking a doctor.
8. **Hierarchy:** categories nested to any depth (Electronics > Computers > Laptops). Provide the table and a query that lists all descendants of a category.

### Trade-offs
9. Give two situations where you would deliberately denormalize, and how you would keep the data consistent.
10. Review this design and list five problems:
```sql
CREATE TABLE stuff (
    id INTEGER, name TEXT, tags TEXT, price REAL, owner TEXT, status INTEGER, data TEXT
);
```

<details>
<summary>Solutions</summary>

**1.** Dependencies: `student_id -> student_name`; `course_id -> course_title, instructor`; `instructor -> instructor_office`; `(student_id, course_id) -> grade`. 2NF violations: `student_name` depends only on `student_id`, and `course_title`/`instructor` only on `course_id` (partial dependencies). 3NF violation: `instructor_office` depends on `instructor`, not the key (transitive).
```sql
CREATE TABLE students    (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE instructors (id INTEGER PRIMARY KEY, name TEXT NOT NULL, office TEXT);
CREATE TABLE courses     (id INTEGER PRIMARY KEY, title TEXT NOT NULL,
                          instructor_id INTEGER NOT NULL REFERENCES instructors(id));
CREATE TABLE enrollments (student_id INTEGER REFERENCES students(id),
                          course_id  INTEGER REFERENCES courses(id),
                          grade TEXT,
                          PRIMARY KEY (student_id, course_id));
```

**2.** It violates 1NF (multiple values in one cell).
```sql
CREATE TABLE contacts (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE contact_phones (contact_id INTEGER NOT NULL REFERENCES contacts(id), phone TEXT NOT NULL,
                             PRIMARY KEY (contact_id, phone));
```

**3.** `id -> department_id -> department_name, department_head` is transitive. Move department attributes to a `departments(id, name, head_id)` table and keep only `department_id` in `employee`.

**4.** It records what the customer actually paid at that time. If the product's price changes later, historical orders and invoices must not change. It is a different fact, not redundant data.

**5.**
```sql
CREATE TABLE members (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL);
CREATE TABLE books   (id INTEGER PRIMARY KEY, title TEXT NOT NULL, isbn TEXT UNIQUE);
CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE book_authors (book_id INTEGER REFERENCES books(id), author_id INTEGER REFERENCES authors(id),
                           PRIMARY KEY (book_id, author_id));
CREATE TABLE copies  (id INTEGER PRIMARY KEY, book_id INTEGER NOT NULL REFERENCES books(id));
CREATE TABLE loans   (id INTEGER PRIMARY KEY, copy_id INTEGER NOT NULL REFERENCES copies(id),
                      member_id INTEGER NOT NULL REFERENCES members(id),
                      borrowed_on TEXT NOT NULL, due_on TEXT NOT NULL, returned_on TEXT);
```

**6.**
```sql
CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL);
CREATE TABLE posts (id INTEGER PRIMARY KEY, author_id INTEGER NOT NULL REFERENCES users(id),
                    title TEXT NOT NULL, body TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE tags  (id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL);
CREATE TABLE post_tags (post_id INTEGER REFERENCES posts(id), tag_id INTEGER REFERENCES tags(id),
                        PRIMARY KEY (post_id, tag_id));
CREATE TABLE comments (id INTEGER PRIMARY KEY, post_id INTEGER NOT NULL REFERENCES posts(id),
                       user_id INTEGER NOT NULL REFERENCES users(id),
                       parent_id INTEGER REFERENCES comments(id),    -- NULL for top-level
                       body TEXT NOT NULL, created_at TEXT NOT NULL);
```

**7.**
```sql
CREATE TABLE doctors  (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE patients (id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE appointments (
    id INTEGER PRIMARY KEY,
    doctor_id  INTEGER NOT NULL REFERENCES doctors(id),
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    starts_at  TEXT NOT NULL,
    UNIQUE (doctor_id, starts_at)          -- a doctor cannot be double-booked for a slot
);
```
(Overlapping time *ranges* need an exclusion constraint in PostgreSQL; fixed slots can use `UNIQUE`.)

**8.**
```sql
CREATE TABLE categories (id INTEGER PRIMARY KEY, name TEXT NOT NULL,
                         parent_id INTEGER REFERENCES categories(id));

WITH RECURSIVE sub AS (
    SELECT id, name FROM categories WHERE name = 'Electronics'
    UNION ALL
    SELECT c.id, c.name FROM categories c JOIN sub ON c.parent_id = sub.id
)
SELECT name FROM sub;
```

**9.** (a) A stored `orders.total` or `post.comment_count` to avoid summing or counting on every list view; keep it in sync in the same transaction as the change, or with a trigger, and add a periodic reconciliation job. (b) A reporting table or materialized view for dashboards; refresh it on a schedule and label it as slightly stale.

**10.** (a) No primary key (`id INTEGER` is not declared `PRIMARY KEY`); (b) `tags TEXT` holds a list, violating 1NF; (c) `price REAL` uses floating point for money; (d) `owner TEXT` should be a foreign key to a users table; (e) `status INTEGER` is a magic number with no lookup or `CHECK`; (f) a generic `data TEXT` blob hides structure, with no types or constraints; (g) no `NOT NULL`, no timestamps, and a vague table name.

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Normalization Lab](01-normalization-lab.md)
