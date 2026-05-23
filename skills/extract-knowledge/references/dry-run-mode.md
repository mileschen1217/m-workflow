# Dry-Run Mode

Executes Phase 1 (scan) and Phase 2 steps 2.1-2.4 (read, judge, route, dedup)
in **read-only mode**. No files are written, no sources are marked.

This requires full content reads and AI judgment — it is not a lightweight scan.

After processing all candidates, print:

```
Proposed actions:

  NEW   <filename> → <dest>/<proposed note name>
  MERGE <filename> → <dest>/<existing note name> (existing note found)
  SKIP  <filename> → <reason>
  STALE <filename> → re-extract to <dest>/<existing note name>
  ...

  Total: <N> candidates (<new> new, <merge> merge, <skip> skip, <stale> stale)
  Dry run — no files written.
```
