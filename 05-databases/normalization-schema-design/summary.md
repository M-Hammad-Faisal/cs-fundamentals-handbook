# Normalization and Schema Design: One-Page Summary

## Key facts

### Why

Redundancy causes **update**, **insert** and **delete** anomalies. Normalization stores each fact once.

### Normal forms

| Form | Rule |
|------|------|
| **1NF** | Atomic values, no repeating groups, unique rows |
| **2NF** | 1NF + no **partial** dependency on part of a composite key |
| **3NF** | 2NF + no **transitive** dependency (non-key → non-key) |
| **BCNF** | Every determinant is a candidate key |
| 4NF / 5NF | Multi-valued / join dependencies (rare) |

Mnemonic: every non-key column depends on **the key, the whole key, and nothing but the key**.

### Denormalization

Deliberate duplication for read speed (stored totals, copied columns, summary tables, materialized views, star schemas). Normalize first, measure, then denormalize hotspots and add a sync mechanism.

### Design rules

- Every table has a primary key; index foreign keys.
- Surrogate keys (ids/UUIDs) for identity; keep natural keys `UNIQUE`.
- Right types: **money = DECIMAL or integer cents**; `NOT NULL` by default.
- Enforce rules with `CHECK`, `UNIQUE`, `FOREIGN KEY` (+ chosen `ON DELETE` action).
- Many-to-many = junction table. Hierarchy = `parent_id` + recursive CTE.
- Record "as-of" values (price paid) on transaction rows.
- Soft delete, audit columns, history tables where needed. Use migrations.

### Anti-patterns

CSV in a column · floats for money · no foreign keys · magic numbers · one giant table · EAV for core data · JSON replacing real columns · premature denormalization.

### Process

Entities → relationships → keys → normalize to 3NF → constraints/types → indexes → measure → denormalize if needed.

## Pitfalls

- Denormalising before measuring, or normalising past the point of usefulness.
- Comma-separated lists in a column, or entity-attribute-value tables for relational data.
- Relying on application code instead of foreign keys and constraints.
- Natural keys that change; `NULL` used to mean several different things.
- Not indexing foreign-key columns.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Normalization Lab](01-normalization-lab.md)
