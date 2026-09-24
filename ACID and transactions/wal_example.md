# SQLite WAL Examples

## Initial State

Main database: 
- Page 1 — Account A: $1,000
- Page 2 — Account B: $500. 

WAL file empty.

**Goal:** Transfer $200 from A to B in a single transaction.

## Transaction Steps

**1. Transaction opens.** Main database untouched. WAL is empty.

**2. Deduct $200 from A.** Writer appends to WAL: `[Page 1: A = $800]` — no commit marker yet. Main database unchanged, readers still see $1,000 / $500.

**3. Add $200 to B.** Writer appends to WAL: `[Page 1: A = $800] [Page 2: B = $700]` — still no commit marker. Main database still unchanged.

**4. Commit.** Writer appends a commit marker: `[Page 1: A = $800] [Page 2: B = $700] [COMMIT]`. Transaction is now official. Main database still untouched. New readers find both pages in the WAL and see $800 / $700.

**5. Checkpoint.** SQLite copies WAL pages into the main database, resets the WAL. Main database now permanently reads $800 / $700.

## Crash Scenarios

**Crash after step 2 or 3** — the WAL has one or two entries but no commit marker. On recovery SQLite scans the WAL, finds no valid commit marker, and discards all WAL entries. The main database was never touched, so the state remains $1,000 / $500.

**Crash while writing the commit marker (step 4)** — the marker is only partially on disk and its checksum fails. SQLite treats it as absent, discards the WAL, and again falls back to the untouched main database: $1,000 / $500.

**Crash mid-checkpoint (step 5)** — suppose Page 1 was written to the main database ($800) but Page 2 was not yet updated ($500 still on disk). The WAL is still intact with a valid commit marker. Readers consult the WAL and correctly see $800 / $700. The next checkpoint simply redoes the work and finishes the job.


