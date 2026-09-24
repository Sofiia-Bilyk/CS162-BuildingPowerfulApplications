# Query Optimization and Indices

## The Query

```sql
SELECT Name, Phone FROM Customer WHERE Gender = 'f' AND ZipCode = '90210';
```

**Assumptions:**
- N = total number of rows in Customer table
- ~50% of customers are female (mirrors general population)
- ~10,000 distinct zip codes, roughly uniformly distributed → ~N/10,000 customers per zip code

---

## 1. No Indexes — Full Table Scan

Without any index the database has no choice but to read every row and test both conditions.

```
results = []

for each row in Customer:           # visits all N rows
    if row.Gender == 'f':
        if row.ZipCode == '90210':
            results.append((row.Name, row.Phone))

return results
```

**Cost: O(N)** — every row is examined.

---

## 2. Index on Gender

A B-tree (or bitmap) index on `Gender` lets the database jump directly to the female subset without reading the entire table. However, `Gender` has very low cardinality (only ~2–3 distinct values), so the index narrows the scan to roughly **50% of all rows**. Each of those rows still needs to be fetched from the table to check `ZipCode`.

```
results = []

# Binary-search the Gender index for 'f' → returns ~N/2 row pointers
for each rowid in IndexLookup(idx_gender, key='f'):   # ~N/2 iterations
    row = FetchRow(Customer, rowid)
    if row.ZipCode == '90210':
        results.append((row.Name, row.Phone))

return results
```

**Cost: O(N/2) ≈ O(N)**

**Efficiency gain vs no index: ~2×**

A gender index is nearly useless for this query. Because roughly half the population is female, the index still directs the database to half of all rows — barely better than a full scan. Low-cardinality columns make poor standalone indexes for selective queries.

---

## 3. Index on ZipCode

`ZipCode` has high cardinality (10,000 distinct values). An index on `ZipCode` narrows the candidate set to roughly **N/10,000 rows**. Each of those rows is fetched to check `Gender`.

```
results = []

# Binary-search the ZipCode index for '90210' → returns ~N/10,000 row pointers
for each rowid in IndexLookup(idx_zipcode, key='90210'):   # ~N/10,000 iterations
    row = FetchRow(Customer, rowid)
    if row.Gender == 'f':
        results.append((row.Name, row.Phone))

return results
```

**Cost: O(N/10,000)**

**Efficiency gain vs no index: ~10,000×**

After the gender filter (~50% pass), the expected result set is ~N/20,000 rows, but the index work itself is N/10,000 lookups. This is dramatically better than either the no-index or gender-index cases.

---

## 4. Composite Index

A **composite index** (also called a multi-column index) is a single B-tree built over two or more columns together. The rows are sorted first by the leading column, then by the second column within each leading-column group, and so on.

**Good composite index for this query:**

```sql
CREATE INDEX idx_zip_gender ON Customer (ZipCode, Gender);
```

`ZipCode` goes first because it is far more selective (10,000 values vs ~2). The B-tree can seek directly to the node for `('90210', 'f')` and scan only the contiguous block of entries that match both conditions simultaneously — no post-filter needed.

```
results = []

# Navigate the B-tree to the exact (ZipCode='90210', Gender='f') leaf block
# Only ~N/20,000 entries match both conditions
for each entry in BTreeRangeScan(idx_zip_gender, key=('90210', 'f')):

    # The index stores the rowid but NOT Name or Phone
    # Must fetch the full row from the table to get those columns
    row = FetchRow(Customer, entry.rowid)
    results.append((row.Name, row.Phone))

return results
```

**Cost: O(log N + N/20,000)** — O(log N) to navigate to the matching leaf, then O(N/20,000) to iterate matches and fetch rows.

**Efficiency gain vs no index: ~20,000×**

The composite index filters on both columns at once, halving the work again relative to a ZipCode-only index. The remaining cost is the table row fetches for `Name` and `Phone`.

---

## 5. Covering Index

A **covering index** is a composite index that includes every column the query needs — both the columns used in `WHERE` and the columns in `SELECT`. When the index "covers" the query, the database never needs to touch the actual table rows at all; all required data lives in the index itself.

**Covering index for this query:**

```sql
CREATE INDEX idx_covering ON Customer (ZipCode, Gender, Name, Phone);
```

The index is sorted by `(ZipCode, Gender)` and each leaf node also stores `Name` and `Phone`. A query that only needs these four columns can be answered entirely from the index.

```
results = []

# Navigate the B-tree to (ZipCode='90210', Gender='f')
# Each matching leaf node already contains Name and Phone — no table fetch needed
for each entry in BTreeRangeScan(idx_covering, key=('90210', 'f')):
    results.append((entry.Name, entry.Phone))   # data lives in the index node itself

return results
```

**Cost: O(log N + N/20,000)**

### Covering vs Composite Index — Which is More Efficient?

| | Composite `(ZipCode, Gender)` | Covering `(ZipCode, Gender, Name, Phone)` |
|---|---|---|
| Index navigation | O(log N) | O(log N) |
| Matching entries scanned | N/20,000 | N/20,000 |
| Table row fetches | **N/20,000** (random I/O) | **0** |
| Extra data stored in index | No | Yes (Name, Phone) |

**The covering index is more efficient** — both have the same Big-O, but the covering index eliminates all table row fetches. Each fetch is a random disk seek (or cache miss) that costs significantly more than reading the sequential, compact index structure. This advantage is most pronounced when:

- The result set is large (many rows to fetch)
- The table is on disk and rows are scattered across many pages
- `Name` and `Phone` are wide columns stored far from the index pages

The trade-off: the covering index is larger and slower to write to, since every `INSERT` or `UPDATE` to `Name`, `Phone`, `ZipCode`, or `Gender` must also update the index.
