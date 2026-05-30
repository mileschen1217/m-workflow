# Audit

Docs form a graph (epic indexes ↔ research ↔ specs ↔ plans ↔ ADRs). The graph has two directions:

- **Forward** — epic index links to content doc (phase spec/plan, Open Questions, Pivots, Retrospective).
- **Back** — content doc declares its epics in frontmatter: `epics: [<slug>, ...]`.

A healthy doc has both directions in agreement. The audit maintains bidirectional integrity — **fix the unambiguous misses, report only conflicts**.

**Epic-level checks** (report-only)

1. **Status drift** — every ROADMAP row's status must match the epic index frontmatter `status:`. Mismatch → finding.
2. **Staleness** — any `active` epic whose index is untouched (`git log -1 --format=%cs`) >30 days. Flag for push / pause / close.
3. **Epic orphans** — `.touchstone/epics/<slug>/` with no ROADMAP row, or ROADMAP row pointing at a non-existent index. <!-- phase-2-carve-out -->
4. **Scope overlap** — grep epic aims for shared nouns; flag only if overlap looks real.

**Link-health checks** (mix of auto-fix and report)

5. **Broken links** *(report)* — every `[text](path)` must resolve. Dangling refs → finding; include source file + missing target.
6. **Content orphans** *(report)* — every file under `.touchstone/{research,specs,plans,docs/adr}/` must have *either* an inbound link from an epic index / other content doc *or* `epics:` frontmatter. Neither → finding.
7. **Backlink integrity** *(auto-fix + report)* — reconcile forward ↔ back.
   - **Auto-fix:** doc has inbound link from epic `foo`'s index but no `epics:` frontmatter → add `epics: [foo]` (or append `foo` to existing frontmatter missing the key). Safe because both directions already agree; frontmatter is just catching up.
   - **Report (conflict):** doc declares `epics: [foo]` but `foo`'s index does not link to it. Could mean a missing index link (add it — but where? Phase? Related? human call) or over-claim in frontmatter (remove `foo`). Do not auto-fix.
   - **Report (asymmetry):** doc declares `epics: [foo]` and is linked from `bar`'s index (bar not in frontmatter). Author chose a subset intentionally, or forgot. Do not auto-fix.
8. **Rotted references** *(report)* — broken-link findings pointing at files deleted from the working tree but still in git history. Report the commit that removed the target.

**Task-level checks** *(report-only, applies when an epic has `tasks/` subdir)*

9. **Task discovery (AC G1)** — enumerate `tasks/<task-id>/result.json` for each epic; list `task_id`, `role`, `runtime`, `status` from JSON fields. Output is informational (no finding unless drift detected below).

10. **Task status drift (AC G2)** — for each task-dir:
    - If `contract.md` frontmatter declares `status: done` AND `result.json` does not exist OR `result.json` mtime < `contract.md` mtime → finding "done declared, no result" or "stale result".
    - If `result.json` declares `status: done` AND `contract.md` declares `status: pending` → finding "result ahead of contract".

11. **Task orphans (AC G3)** — for each task-dir under `.touchstone/epics/<slug>/tasks/`: <!-- phase-2-carve-out -->
    - If parent `<slug>` has no entry in ROADMAP § Active or Completed → finding "task under orphan epic".
    - If task-id path lacks `contract.md` → finding "task with no contract".

12. **result.json schema conformance** — for each `result.json`:
    - Parse as JSON; if invalid → finding "result.json malformed".
    - If `schema_version != "1"` → finding "result.json schema_version unrecognized".
    - If required fields missing (per spec § result.json schema) → finding listing missing fields.

**Running the checks**

- Enumerate files with `git ls-files`; include `.touchstone/epics/**/index.md`, `.touchstone/research/**/*.md`, `.touchstone/specs/**/*.md`, `.touchstone/plans/**/*.md`, `.touchstone/docs/adr/**/*.md`, `ROADMAP.md`. <!-- phase-2-carve-out -->
- Parse markdown links with `\[[^\]]+\]\(([^)]+)\)`; resolve relative to the source file.
- Frontmatter: grep the top-of-file `^---` block for `^epics:`; no YAML library needed. Accept both inline (`epics: [a, b]`) and block-list forms.
- Auto-fix writes: stage edits in a single commit with message `docs(audit): backfill epics: frontmatter from inbound links`; do not commit if any non-auto-fix finding is unresolved — let the user triage first.

**Report format**

Group by check number; one line per finding with source, rule, recommended action. Separate auto-fixed items under a "Fixed" heading with the list of files touched. If a check passes clean, say so in one sentence. Skip whole sections with no findings.
