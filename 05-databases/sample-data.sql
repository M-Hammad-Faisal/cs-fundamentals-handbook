-- Sample dataset used by the SQL examples in this part.
-- Works in SQLite (3.25+), and with small changes in PostgreSQL and MySQL.
--
-- Try it:   sqlite3 shop.db < sample-data.sql
-- Or:       python3 -c "import sqlite3; c = sqlite3.connect(':memory:'); c.executescript(open('sample-data.sql').read())"

PRAGMA foreign_keys = ON;

CREATE TABLE departments (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE employees (
    id            INTEGER PRIMARY KEY,
    name          TEXT    NOT NULL,
    department_id INTEGER REFERENCES departments(id),
    manager_id    INTEGER REFERENCES employees(id),
    salary        INTEGER NOT NULL CHECK (salary > 0),
    hired_on      TEXT    NOT NULL           -- ISO date: YYYY-MM-DD
);

CREATE TABLE customers (
    id      INTEGER PRIMARY KEY,
    name    TEXT NOT NULL,
    country TEXT NOT NULL
);

CREATE TABLE orders (
    id          INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    ordered_on  TEXT    NOT NULL,
    status      TEXT    NOT NULL CHECK (status IN ('pending', 'shipped', 'cancelled'))
);

CREATE TABLE order_items (
    order_id   INTEGER NOT NULL REFERENCES orders(id),
    product    TEXT    NOT NULL,
    quantity   INTEGER NOT NULL CHECK (quantity > 0),
    unit_price INTEGER NOT NULL,
    PRIMARY KEY (order_id, product)
);

INSERT INTO departments (id, name) VALUES
    (1, 'Engineering'), (2, 'Sales'), (3, 'Support'), (4, 'Legal');

INSERT INTO employees (id, name, department_id, manager_id, salary, hired_on) VALUES
    (1, 'Amina',  1, NULL, 9000, '2019-03-01'),
    (2, 'Bilal',  1, 1,    7000, '2020-06-15'),
    (3, 'Chen',   1, 1,    7000, '2021-01-10'),
    (4, 'Dana',   2, NULL, 6000, '2018-09-20'),
    (5, 'Eli',    2, 4,    4500, '2022-02-01'),
    (6, 'Farah',  3, NULL, 4000, '2020-11-05'),
    (7, 'Gus',    3, 6,    3500, '2023-04-17'),
    (8, 'Hana',   NULL, NULL, 5000, '2022-08-08');   -- no department yet

INSERT INTO customers (id, name, country) VALUES
    (1, 'Acme Ltd',    'PK'),
    (2, 'Globex',      'US'),
    (3, 'Initech',     'US'),
    (4, 'Umbrella',    'UK'),
    (5, 'Hooli',       'PK');                         -- will have no orders

INSERT INTO orders (id, customer_id, ordered_on, status) VALUES
    (1, 1, '2024-01-05', 'shipped'),
    (2, 1, '2024-02-11', 'shipped'),
    (3, 2, '2024-02-14', 'pending'),
    (4, 3, '2024-03-02', 'cancelled'),
    (5, 2, '2024-03-20', 'shipped'),
    (6, 4, '2024-03-25', 'shipped');

INSERT INTO order_items (order_id, product, quantity, unit_price) VALUES
    (1, 'Keyboard', 2, 50),
    (1, 'Mouse',    1, 20),
    (2, 'Monitor',  1, 300),
    (3, 'Keyboard', 1, 50),
    (4, 'Monitor',  2, 300),
    (5, 'Mouse',    5, 20),
    (5, 'Laptop',   1, 1200),
    (6, 'Laptop',   2, 1200);
