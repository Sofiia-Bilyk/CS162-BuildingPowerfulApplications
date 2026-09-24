# PCW 13: Query Performance and Indexing

## 1. Timing Results

Each script creates three tables of 10,000 rows with random values and runs the same three-table join:

```sql
SELECT COUNT(*) FROM TEST1 t1
    JOIN TEST2 t2 ON (t1.x) = (t2.x)
    JOIN TEST3 t3 ON (t1.y) = (t3.y)
    WHERE t3.z > t1.z;
```

| Script | Indexes | Query Plan | Time |
|---|---|---|---|
| `random.sql` | None | SCAN t1, SCAN t2, SCAN t3 | **6.159 s** |
| `random_indexed.sql` | `TEST2(x)`, `TEST3(y)` | SCAN t1, SEARCH t3 via index, SEARCH t2 via index | **0.005 s** |
| `random_cover_indexed.sql` | `TEST2(x)`, `TEST3(y,z)` | SCAN t1, SEARCH t3 via covering index, SEARCH t2 via covering index | **0.007 s** |

The indexed queries are roughly **1,200x faster** than the naive scan.

---

## 2. Pseudocode: How the Fast (Indexed) Query Works

The query planner scans TEST1 once and uses B-tree index lookups for the other two tables instead of full scans.

### Minimal index version (`random_indexed.sql`)

```
count = 0

# Outer loop: full sequential scan of TEST1 — O(N)
for each row t1 in TEST1:

    # Index lookup: binary-search the B-tree on TEST3.y for t1.y — O(log N) to locate
    for each t3 in BTreeLookup(idx_test3_y, key = t1.y):

        # Must fetch the full t3 row from the table to read t3.z (not in index)
        fetch t3.z from TEST3 table row

        if t3.z > t1.z:

            # Index lookup: binary-search the B-tree on TEST2.x for t1.x — O(log N)
            # idx_test2_x stores only x, which is all that's needed — acts as covering index
            for each t2 in BTreeLookup(idx_test2_x, key = t1.x):
                count += 1

return count
```

### Covering index version (`random_cover_indexed.sql`)

```
count = 0

# Outer loop: full sequential scan of TEST1 — O(N)
for each row t1 in TEST1:

    # Index lookup on TEST3 covering index (y, z):
    # Binary-search to y = t1.y, then apply z > t1.z WITHIN the index itself — O(log N)
    # No table row fetch needed: both y and z live in the index node
    for each t3 in BTreeLookup(idx_test3_yz, key = t1.y, filter = z > t1.z):

        # t2 lookup same as before
        for each t2 in BTreeLookup(idx_test2_x, key = t1.x):
            count += 1

return count
```

The covering index on `TEST3(y, z)` allows the database to evaluate the `WHERE t3.z > t1.z` filter **inside the index scan** without ever touching the actual table rows, eliminating the extra fetch step.

---

## 3. Asymptotic Scaling of the Fast Query

Let N = number of rows per table. Values are drawn from a range of ~524,288 with only 10,000 rows, so each index lookup returns O(1) matches on average (high cardinality).

| Step | Cost |
|---|---|
| Scan TEST1 | O(N) |
| Per TEST1 row: B-tree lookup in TEST3 index | O(log N) |
| Per TEST1 row: B-tree lookup in TEST2 index | O(log N) |

**Total: O(N log N)**

In the general case with M average index matches per lookup, cost is O(N · M · log N). Here M ≈ 1, so it simplifies to **O(N log N)**, compared to **O(N³)** for the naive triple full-scan.

---

## 4. Asymptotic Scaling of Creating an Index

Building a B-tree index on a column of N rows requires:

1. **Read** all N rows from the table: O(N)
2. **Sort** the values by the indexed column: O(N log N)
3. **Bulk-load** sorted entries into the B-tree: O(N)

The sort dominates, so:

**Creating an index is O(N log N)**

Once built, individual point lookups cost O(log N) and range scans cost O(log N + k) where k is the number of matching rows returned.
