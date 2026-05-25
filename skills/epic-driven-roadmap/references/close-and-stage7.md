# Close an epic

1. Mark all phases `done` with landed dates.
2. Set frontmatter `status: done`, `landed: YYYY-MM-DD`.
3. Fill the Retrospective block — bullets only; typical: What worked, What pivoted, What to do differently.
4. Run **Stage 7 — Doc Reckoning** (see below) and append the block to the epic index.
5. Remove the row from ROADMAP § Active Epics; add to § Completed Epics with the landed date.
6. Commit.

## Stage 7 — Doc Reckoning

Mechanical inventory of what this epic did to the doc graph. Lists facts; does not judge whether a bridge should have been written or whether it should be downgraded to a comment — those are author judgment, intentionally NOT skillified.


**Inputs**

- Epic slug.
- Git range `--since <epic.started> --until <epic.landed>` (or branch range if known).

**Procedure**

1. **Created docs** — enumerate `.md` files added in the git range under the project's doc paths (`.swarm/research/`, `.swarm/specs/`, `.swarm/plans/`, `.swarm/docs/`). For each:
   - Read frontmatter `kind:`.
   - If `kind: bridge`, read `kill-on:`. Missing `kill-on:` on a bridge doc → **finding** (advisory; cultural reminder, not gating per the `source-as-truth` discipline).
   - List as `created` with kind + kill-on.

2. **Killed docs** — enumerate `.md` files deleted in the git range. For each, record path + the lever-related commit that removed it (best-effort: the commit message naming a `lever-*` slug, if any).

3. **Pending kills** — grep all surviving `.md` files for frontmatter `kill-on:` values matching lever slugs known to have landed (cross-check ROADMAP § Completed Epics). Any bridge doc whose `kill-on:` points at a landed lever but still exists → **pending kill** (the lever did not delete the doc it was supposed to).

3b. **Stale bridge candidates (mtime check, advisory)** — for each surviving bridge doc this epic touched, compare `git log -1 --format=%ct <bridge-path>` with the most recent `git log -1 --format=%ct <source-path>` of source paths the bridge references (best-effort: extract paths from inline links and `related:` frontmatter). Bridge older than its referenced source by >30 days → flag as **stale-candidate** (does NOT auto-delete; reader judgment required — bridge may still be accurate, or source change may have invalidated it). Per the `source-as-truth` discipline, CONTEXT.md § Bridge content gate — three principles, three-principle re-audit is the human follow-up; this check only surfaces candidates.

3c. **Rung-misclassification candidates (advisory, P3 violation)** — for each bridge `.md` this epic touched, scan section bodies for single-source-path citations. Heuristic: a section whose prose cites **exactly one** source path (single function / single struct / single file) without naming a second cross-cutting location is a rung-2/3 candidate that wandered into rung-4 `.md`. Output the section heading + the lone source path so a human can decide: move to `///` doc-comment (rung 2), or `// BRIDGE` block at call-site (rung 3), or argue it stays rung 4 (cross-cutting reason). Per CONTEXT.md § Bridge content gate — three principles, P3 worked examples — "if you wrote this as a `///` doc-comment, which symbol would you attach it to?" — single answer = wrong rung.

3d. **Doc-as-workaround candidates (advisory, P1 violation)** — scan bridge `.md` sections for prose that exists to explain why dead / duplicative / obsolete source still exists. Trigger phrases (heuristic): "deprecated", "kept until X ships", "do not use", "no-op stub", "ignored after Phase N", "legacy path", "wrapper for backward compatibility". For each match, output the section + suggested action: file a PR to remove the source, OR justify why the source must remain. Per CONTEXT.md § Bridge content gate — three principles, P1 — "would a PR removing the source be more honest than a paragraph explaining it?"

4. **Source-level deposit** — read the epic's design specs (if any) for their `## Source-level Deposit` section (per `m-design-spec` template). Record the lever each spec named, or "none" with the stated reason.

5. **Built spec distill-or-archive (per the `source-as-truth` discipline, CONTEXT.md § Standing vs transient bridge)** — for each spec under this epic whose feature has landed, decide its post-landing path:
   - **Pure transient** (all contracts now in source) → mark for move to `.swarm/archive/specs/`, frontmatter change to `kind: diagnostic`, `evidence-for: <commits / MR>`.
   - **Standing-candidate sections present** (P3-pure cross-cutting invariants) → list which sections should distill to `.swarm/docs/architecture/<topic>.md` (carrying their own `kill-on:`); residual spec then archives.
   - **Whole spec is cross-cutting** (rare) → copy whole spec to `.swarm/docs/architecture/`, retire original.
   This is a judgment call, not auto-executed. Stage 7 surfaces the candidates; the human (or author at next session) executes the move and frontmatter rewrite.

**Output — append to epic `index.md`**

```markdown
## Doc Reckoning (Stage 7)

**Deposit (from specs):**
- `<spec-path>` → advances `<lever-slug>` (or `none — <reason>`)

**Created:**
- `<doc-path>` — kind: `<kind>` · kill-on: `<lever-slug>` (or none — flag if bridge)

**Killed:**
- `<doc-path>` — removed in `<commit-sha>` (advances `<lever-slug>`)

**Pending kills:**
- `<doc-path>` — kill-on `<lever-slug>` (landed `<date>` but doc still present)

**Stale-candidate bridges (advisory):**
- `<doc-path>` — last touched `<date>`; referenced source `<source-path>` last touched `<date>` (+N days newer)

**Rung-misclassification candidates (advisory):**
- `<doc-path>` § `<section heading>` — cites only `<single-source-path>`; suggested rung: 2 (`///` doc-comment) | 3 (`// BRIDGE` block) | argue cross-cutting

**Doc-as-workaround candidates (advisory):**
- `<doc-path>` § `<section heading>` — triggered by `<phrase>`; suggested action: PR to remove `<source-path>` OR justify retention

**Built specs (distill-or-archive candidates):**
- `<spec-path>` — feature landed `<commit-sha>`; recommended path: archive | distill <section-list> → standing bridge | move-whole
```

**Boundaries (what Stage 7 is NOT)**

- Not a judge of bridge rung (rung 2 vs rung 4). Author's call.
- Not a judge of whether the deposit's lever choice was right. Author's call.
- Not a gate. Findings are advisory; the epic may close with bridge docs missing `kill-on:` if the human accepts the residual.
