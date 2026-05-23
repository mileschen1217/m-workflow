---
name: epic-driven-roadmap
kind: workflow
description: |
  Scaffold, maintain, and audit a project's epic-driven roadmap. Every project
  using this convention keeps a pure-tracker ROADMAP.md plus one tracker per
  epic under .swarm/epics/<slug>/index.md. Invoke when: starting a new epic,
  closing an epic (retrospective + move to Completed), auditing status drift,
  or bootstrapping the convention in a new project. Concrete paths come from
  the project's CLAUDE.md § Doc Routing; this skill owns the shape, templates,
  and procedures.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
---

# m-epic-driven-roadmap

## Step 0 — Load vocabulary

Read `${CLAUDE_PROJECT_DIR}/.claude/m-workflow.yaml`.

**If yaml absent** (file not found):
  Print one line: `ℹ️  No .claude/m-workflow.yaml — using default paths. Run /m-workflow:init to configure.`
  Use hardcoded defaults: `specs_dir=.swarm/specs`, `adr_dir=.swarm/docs/adr`, `epics_dir=.swarm/epics`, `plans_dir=.swarm/plans`, `archive_specs_dir=.swarm/archive/specs`.
  Treat `adopted_disciplines` as empty. Do not refuse; continue. Skip CONTEXT.md Read.

**If yaml present:** check `adopted_disciplines`.

If contains `source-as-truth`:
  Read 3 sections of `${CLAUDE_PLUGIN_ROOT}/CONTEXT.md`:
    - § "Bridge content gate"
    - § "Standing vs transient bridge"
    - § "Four doc kinds"

  These define the rules Stage 7 doc reckoning applies (kill-on, kind: bridge|navigation|workflow|diagnostic, distill-or-archive criteria).

This skill does not dispatch to other skills, so no envelope handoff is needed.

If not adopted: skip Read; Stage 7 doc reckoning runs in default mode (mechanical mtime-based bridge audit only, no frontmatter kind: classification, no distill-or-archive recommendation).

Pure-tracker roadmap + per-epic tracker convention. CLAUDE.md routes here; this skill owns the rule and the templates.

## When to Invoke

- **Scaffold a new epic** — user starts work on a new initiative not yet tracked.
- **Close an epic** — all phases done, needs retrospective + move to Completed table.
- **Audit** — weekly or on demand: status drift between ROADMAP row and epic frontmatter, stale epics, orphans, scope overlap.
- **Bootstrap** — new project adopts this convention (ROADMAP.md + `.swarm/epics/README.md` + first epic).

Skip if: the project doesn't use this convention (no `ROADMAP.md` or `.swarm/epics/`).

## The Rule

**Trackers are shallow pointers; content docs hold the detail.**

Trackers (ROADMAP row + epic index) may contain: title, one-sentence aim, status fields, links to content docs, phases table (one row per shippable increment), pivots (one line each), open questions (one line each), retrospective bullets on close.

Trackers may **not** contain: design prose, rationale, research findings, architectural content. Any paragraph longer than one sentence is a rule violation — move it to a content doc and link.

**Status vocabulary:** `proposed | active | paused | done | cancelled`.

## Question-per-stage pipeline

Maps to the 6-stage workflow in `~/.claude/CLAUDE.md`:

| Q (stage) | Home (abstract) |
|---|---|
| Why at all? (0) | Project vision / scope |
| Why this epic? (1) | Epic tracker index |
| What might work? (2) | Research note |
| What contract? (3, GWT) | Design spec |
| How, in order — epic-level? (4a) | **Epic master plan** (lives with the epic) |
| How, in order — per-spec? (4b) | Implementation plan (one per design spec) |
| Did it work? (5) | Commits, MRs |
| What did we learn? (6) | Retrospective on epic index |
| Did docs catch up? (7) | Doc Reckoning block on epic index (see "Close an epic") |

Concrete paths live in the project's CLAUDE.md § Doc Routing.

### Master plan vs. task plan

Two distinct artifacts; do not conflate.

- **Epic master plan (Q4a)** — sequences the epic's phases, locks cross-spec decisions (e.g. "primary gate is X, deprecate Y"), states effort + acceptance per phase, freezes scope so reactive expansion is rejected. Lives **with the epic**: `.swarm/epics/<slug>/<short-name>.md` (e.g. `v6-3-roadmap.md`, `roadmap.md`, or `master-plan.md`). The epic index links to it. One per epic — not per phase.
- **Task plan (Q4b)** — per-spec implementation plan for a single design spec. Lives under `docs/superpowers/plans/` (or the project's plan path). One per spec.

**When to write a master plan:** an epic that crosses 2+ design specs, locks methodology decisions that bind multiple specs, or needs effort sequencing across phases. Skinny epics (single spec, one PR) skip the master plan and go straight from epic index → spec → plan.

**Master plan vs. epic index:** the index is a **tracker** (one-liners, links). The master plan is **prose with tables** (decisions, phase effort, dependency graph, acceptance criteria). The index links to the master plan; it does not absorb it.

## Procedures

### Scaffold a new epic

0. **Foundation elicitation (Baseline — always runs)** — before slugging
   anything, run the 3-field elicitation gate.

   Reuse check FIRST (AC-10): if a foundation was already confirmed earlier
   in THIS SAME skill invocation (a later procedure step re-enters Step 0),
   do NOT re-elicit. Emit this EXACT log line verbatim (fixed emit string —
   do not paraphrase, do not reword):
   "Foundation already confirmed this session — reusing"
   then reuse the confirmed foundation and skip to step e. Do NOT emit the
   from-scratch opener. Reuse is same-invocation only; it never spans
   separate invocations. Otherwise run the gate:

   a. Open with this EXACT phrase (fixed emit string):
      "Please describe the intended work in your own words." The substring
      "describe the intended work in your own words" is what AC-7's bypass
      fixtures match (Step-0 reached) and what AC-4 forbids as the
      from-scratch opener — keep it verbatim, do not paraphrase. No fixed
      follow-up questions — let the user give context freely.

   b. Engage in a SHORT sharpening exchange. Ask only questions in
      the ALLOWED column of the boundary table (§ Interfaces — Step-0
      question boundary). Stop as soon as intention / aim / out-of-
      scope are crisp. Never ask a question in the FORBIDDEN column
      (architecture, files, dependencies, tests, API shape, effort,
      rollout, or fix strategy) — those are design-phase decisions.

   c. Synthesise a draft foundation and present it to the user using
      these EXACT field labels (verbatim — AC-1/AC-2 match them
      case-sensitively):
      - "Intention (why):" motivation / pain in one line
      - "Aim:" observable success at epic scope in one line
        (recorded into the **Aim:** headline, not a ## Foundation field)
      - "Out of scope:" ≤3 explicit routes not taken

      The SYNTHESISED aim must not contain a vague token
      {usually, typically, should, elegant, complex, careful, better}.
      If the user's stated aim contains one, do NOT carry it into the
      draft — re-prompt for an OBSERVABLE formulation: ask what the user
      would observe or measure when it's done (targeted clarifying
      questions are fine; "what would you observe when this is done?" is a
      good default). Do not synthesise until the aim is observable. (AC-8.)

      If the user declines to name any out-of-scope route, prompt
      once: "can you name one thing this work will NOT touch, even if
      related?" If still declined, record this EXACT sentinel verbatim
      (fixed string — do not paraphrase, this literal only) as the
      out-of-scope value: "(no explicit boundary declared)" AND add a
      matching entry to the epic's Open Questions. The sentinel is the one
      allowed placeholder.

   d. Surface the draft foundation to the user and ask, with this exact
      phrase: "Please confirm or edit this foundation." Do not proceed
      to step 1 until confirmed. If the user insists on an aim that
      contains a vague token, warn with this EXACT phrase verbatim (fixed
      emit string — do not paraphrase, do not reword):
      "(aim contains a vague token — accept anyway?)"
      On accept, record the user's aim verbatim AND add this EXACT risk
      note verbatim to Open Questions (do not paraphrase):
      "(aim contains an unverifiable token — user-confirmed)"

   e. Record the confirmed foundation: aim into the **Aim:** headline,
      intention + out-of-scope into ## Foundation (template below).
      This is the highest-ROI step — it prevents a spec being written
      for the wrong scope.
1. Pick a slug — lowercase, hyphen-separated, names the **deliverable surface** (e.g. `port-statistics-stacking`), not a phase number.
2. Read the project's CLAUDE.md § Doc Routing to get the concrete `.swarm/epics/` path.
3. Copy `templates/epic-index.md` to `<epics-dir>/<slug>/index.md`; fill in `slug`, `started` (today), `owner_teams`, aim into the `**Aim:**` headline, intention + out-of-scope into `## Foundation` (from step 0), and Phase 1.
4. Add a row to `ROADMAP.md` § Active Epics: `| <slug> | <aim> | proposed | [index](<epics-dir>/<slug>/index.md) |`.
5. When creating content docs (research, specs, plans, ADRs) for this epic, add frontmatter `epics: [<slug>]` so the backlink exists from day one. See `templates/content-doc.md`.
5. Commit.

### Close an epic

1. Mark all phases `done` with landed dates.
2. Set frontmatter `status: done`, `landed: YYYY-MM-DD`.
3. Fill the Retrospective block — bullets only; typical: What worked, What pivoted, What to do differently.
4. Run **Stage 7 — Doc Reckoning** (see below) and append the block to the epic index.
5. Remove the row from ROADMAP § Active Epics; add to § Completed Epics with the landed date.
6. Commit.

### Stage 7 — Doc Reckoning

Mechanical inventory of what this epic did to the doc graph. Lists facts; does not judge whether a bridge should have been written or whether it should be downgraded to a comment — those are author judgment, intentionally NOT skillified.


**Inputs**

- Epic slug.
- Git range `--since <epic.started> --until <epic.landed>` (or branch range if known).

**Procedure**

1. **Created docs** — enumerate `.md` files added in the git range under the project's doc paths (`.swarm/research/`, `.swarm/specs/`, `.swarm/plans/`, `.swarm/docs/`). For each:
   - Read frontmatter `kind:`.
   - If `kind: bridge`, read `kill-on:`. Missing `kill-on:` on a bridge doc → **finding** (advisory; cultural reminder, not gating per ADR § Open Questions).
   - List as `created` with kind + kill-on.

2. **Killed docs** — enumerate `.md` files deleted in the git range. For each, record path + the lever-related commit that removed it (best-effort: the commit message naming a `lever-*` slug, if any).

3. **Pending kills** — grep all surviving `.md` files for frontmatter `kill-on:` values matching lever slugs known to have landed (cross-check ROADMAP § Completed Epics). Any bridge doc whose `kill-on:` points at a landed lever but still exists → **pending kill** (the lever did not delete the doc it was supposed to).

3b. **Stale bridge candidates (mtime check, advisory)** — for each surviving bridge doc this epic touched, compare `git log -1 --format=%ct <bridge-path>` with the most recent `git log -1 --format=%ct <source-path>` of source paths the bridge references (best-effort: extract paths from inline links and `related:` frontmatter). Bridge older than its referenced source by >30 days → flag as **stale-candidate** (does NOT auto-delete; reader judgment required — bridge may still be accurate, or source change may have invalidated it). Per ADR `source-as-truth` § Bridge content gate, three-principle re-audit is the human follow-up; this check only surfaces candidates.

3c. **Rung-misclassification candidates (advisory, P3 violation)** — for each bridge `.md` this epic touched, scan section bodies for single-source-path citations. Heuristic: a section whose prose cites **exactly one** source path (single function / single struct / single file) without naming a second cross-cutting location is a rung-2/3 candidate that wandered into rung-4 `.md`. Output the section heading + the lone source path so a human can decide: move to `///` doc-comment (rung 2), or `// BRIDGE` block at call-site (rung 3), or argue it stays rung 4 (cross-cutting reason). Per ADR § Bridge content gate P3 worked examples — "if you wrote this as a `///` doc-comment, which symbol would you attach it to?" — single answer = wrong rung.

3d. **Doc-as-workaround candidates (advisory, P1 violation)** — scan bridge `.md` sections for prose that exists to explain why dead / duplicative / obsolete source still exists. Trigger phrases (heuristic): "deprecated", "kept until X ships", "do not use", "no-op stub", "ignored after Phase N", "legacy path", "wrapper for backward compatibility". For each match, output the section + suggested action: file a PR to remove the source, OR justify why the source must remain. Per ADR § Bridge content gate P1 — "would a PR removing the source be more honest than a paragraph explaining it?"

4. **Source-level deposit** — read the epic's design specs (if any) for their `## Source-level Deposit` section (per `m-design-spec` template). Record the lever each spec named, or "none" with the stated reason.

5. **Built spec distill-or-archive (per ADR `source-as-truth` § Standing vs transient bridge)** — for each spec under this epic whose feature has landed, decide its post-landing path:
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

### Scaffold a task

Tasks are finer-grained execution units within an epic phase. They produce L0 artifacts (`result.json`, optional `review.md`) per the multi-vendor dispatch convention.

1. Pick a task-id — `T<NN>-<short-slug>`, lowercase, hyphen-separated. NN is sequence within the epic (T01, T02, ...).
2. Resolve concrete path from project CLAUDE.md § Doc Routing — typically `.swarm/epics/<slug>/tasks/<task-id>/`.
3. Copy `templates/task-contract.md` to `<epics-dir>/<slug>/tasks/<task-id>/contract.md`. Fill in: `task_id`, `epic` slug, `role`, `runtime`, `created`.
4. (optional) Copy `templates/task-result.json` to the same dir as `result.json` initialized with `status: pending`.
5. Commit.

### Task contract scope

A task contract is a unit of cohesive change that an executor (CC subagent, Codex, human) can hold in mind, complete, and have reviewed as one decision. Scoping is judgment — these heuristics resolve the "is this one task or two?" question.

**Default scope of one contract:** all changes that share *all* of these properties:

- **One repo / one runtime.** Different repos and different language runtimes (Rust core vs Python tests vs C plugin) are separate review surfaces and separate executors; do not bundle.
- **One responsibility.** A single named change in the spec's "Interfaces / Contracts" or "Architecture" section. Adding a function and updating its callers is one responsibility; adding two unrelated functions is two.
- **One review boundary.** A reviewer can sensibly evaluate the diff as a unit without needing to context-switch between unrelated concerns.
- **One acceptance criterion bundle.** The contract's acceptance criteria are co-satisfied by the same change. ACs that are satisfied by *different* changes belong in *different* contracts even if they touch the same file.

**One contract may bundle multiple file edits when:**

- Edits are tightly coupled (signature change ripples through callers; rename and its references; struct field add and its serializer).
- The pattern is the same across all files (e.g., "add stacking-aware bound to plugin schema, applied identically to `config_ifmib.rs` and `config_mxport.rs`"). Treat as one contract with the pattern stated once and the file list as a parameter.
- Local helper plus its only caller — no point splitting if the helper has no other client.

**Split into multiple contracts when:**

- A decision artifact (ADR) must land before code — the ADR is its own (CC-owned) task; the consuming implementation is a separate (potentially Codex-owned) task. Sequential dependency on a *decision*, not on code.
- One implementation must land and be verified before another can be written or tested (sequential code dependency where the second can't even be specified without the first).
- The runtime is a CC-vs-Codex split — Codex contracts are mechanical implementation; CC handles work needing project-specific tooling (build orchestration, multi-repo commit discipline, bench access, on-device verification).
- Total scope is large (rule of thumb: more than ~10 file edits, or work that wouldn't fit in one focused execution session) — split along the strongest natural seam (repo, module, layer).
- Different parts of the change need different reviewers / different vendor (e.g. Rust core change goes to a Rust reviewer; Python test goes to a Python reviewer).

**Cross-repo work is NOT automatically a split.** If a small cohesive feature touches 3-4 repos with 1-2 files each, and one executor can hold it all in mind, one contract listing the per-repo edits is correct. The /nos-commit-per-repo ceremony is the orchestrator's responsibility (CC plan tasks), not the contract's. Split per-repo only when the change is large enough that splitting along the repo seam aids reviewability or unblocks parallelism.

**Anti-pattern: one task per file edit.** Splitting along file lines without semantic justification produces high-volume, low-cohesion contracts that obscure the change's intent and inflate review overhead. Bundle by responsibility, not by file count.

**Anti-pattern: one task per AC.** ACs in the spec are observable contracts, not always implementation units. A single contract can satisfy several ACs simultaneously when the underlying change is one cohesive thing (e.g., adding the role gate satisfies AC-REJECT-1 and AC-REJECT-3 with one code change).

**Distribution across executors.** When the plan mixes CC orchestration and Codex implementation:

- Code change with clear contract + standard tooling (cargo build inside repo) → Codex (`codex-implementer` or `codex-tdd`).
- Code change requiring out-of-sandbox tooling (project-specific build wrappers like `/nos-build-buildroot`, multi-repo commit discipline like `/nos-commit`, live-bench verification) → CC (sonnet hybrid implementer or human).
- Decision artifacts (ADR, spec revision, retrospective) → CC.
- Test authoring against live infrastructure → CC (executor needs test-infra context that lives in CC memory).
- Verification / build / commit → CC orchestrator regardless of who wrote the code.

The plan markdown sequences contracts and CC tasks together; contracts live under `tasks/`, CC tasks live as plan steps. Both reference each other by ID so the plan reads end-to-end.

### Close a task

1. Mark contract.md frontmatter `status: done` (or `failed`).
2. Update result.json with completion fields: `status`, `summary`, `files_changed`, `commands_run`, `tests_passed`, `risks`, `handoff_notes`, `completed_at`, `duration_ms`, `fallback_reason`.
3. (optional) If a cross-provider review ran, ensure `review.md`, `raw_cc.md`, `raw_codex.jsonl` are present.
4. Commit.

### Task status vocabulary

`pending | in-flight | blocked | done | failed`. Distinct from epic status (`proposed | active | paused | done | cancelled`) because tasks are finer-grained.

### Audit

Docs form a graph (epic indexes ↔ research ↔ specs ↔ plans ↔ ADRs). The graph has two directions:

- **Forward** — epic index links to content doc (phase spec/plan, Open Questions, Pivots, Retrospective).
- **Back** — content doc declares its epics in frontmatter: `epics: [<slug>, ...]`.

A healthy doc has both directions in agreement. The audit maintains bidirectional integrity — **fix the unambiguous misses, report only conflicts**.

**Epic-level checks** (report-only)

1. **Status drift** — every ROADMAP row's status must match the epic index frontmatter `status:`. Mismatch → finding.
2. **Staleness** — any `active` epic whose index is untouched (`git log -1 --format=%cs`) >30 days. Flag for push / pause / close.
3. **Epic orphans** — `.swarm/epics/<slug>/` with no ROADMAP row, or ROADMAP row pointing at a non-existent index.
4. **Scope overlap** — grep epic aims for shared nouns; flag only if overlap looks real.

**Link-health checks** (mix of auto-fix and report)

5. **Broken links** *(report)* — every `[text](path)` must resolve. Dangling refs → finding; include source file + missing target.
6. **Content orphans** *(report)* — every file under `.swarm/{research,specs,plans,docs/adr}/` must have *either* an inbound link from an epic index / other content doc *or* `epics:` frontmatter. Neither → finding.
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

11. **Task orphans (AC G3)** — for each task-dir under `.swarm/epics/<slug>/tasks/`:
    - If parent `<slug>` has no entry in ROADMAP § Active or Completed → finding "task under orphan epic".
    - If task-id path lacks `contract.md` → finding "task with no contract".

12. **result.json schema conformance** — for each `result.json`:
    - Parse as JSON; if invalid → finding "result.json malformed".
    - If `schema_version != "1"` → finding "result.json schema_version unrecognized".
    - If required fields missing (per spec § result.json schema) → finding listing missing fields.

**Running the checks**

- Enumerate files with `git ls-files`; include `.swarm/epics/**/index.md`, `.swarm/research/**/*.md`, `.swarm/specs/**/*.md`, `.swarm/plans/**/*.md`, `.swarm/docs/adr/**/*.md`, `ROADMAP.md`.
- Parse markdown links with `\[[^\]]+\]\(([^)]+)\)`; resolve relative to the source file.
- Frontmatter: grep the top-of-file `^---` block for `^epics:`; no YAML library needed. Accept both inline (`epics: [a, b]`) and block-list forms.
- Auto-fix writes: stage edits in a single commit with message `docs(audit): backfill epics: frontmatter from inbound links`; do not commit if any non-auto-fix finding is unresolved — let the user triage first.

**Report format**

Group by check number; one line per finding with source, rule, recommended action. Separate auto-fixed items under a "Fixed" heading with the list of files touched. If a check passes clean, say so in one sentence. Skip whole sections with no findings.

### Bootstrap a new project

1. Copy `templates/ROADMAP.md` to the project root.
2. Create `.swarm/epics/README.md` with the binding rule (copy from this skill's "The Rule" section).
3. Add `## Doc Routing` to project CLAUDE.md using the path schema below.
4. Scaffold the first epic (above).

## Path schema (project CLAUDE.md § Doc Routing)

Each project fills in concrete paths for the Q-per-stage pipeline:

| Q (stage) | Example concrete path |
|---|---|
| Why at all? (0) | `.swarm/vision.md`, `ROADMAP.md` scope block |
| Why this epic? (1) | `.swarm/epics/<slug>/index.md` |
| What might work? (2) | `.swarm/research/YYYY-MM-DD-<slug>.md` |
| What contract? (3) | `.swarm/specs/YYYY-MM-DD-<slug>.md` |
| How, in order — epic? (4a) | `.swarm/epics/<slug>/<name>-roadmap.md` (only when epic spans 2+ specs) |
| How, in order — per-spec? (4b) | `.swarm/plans/YYYY-MM-DD-<slug>.md` |
| Did it work? (5) | Commits, MRs |
| What did we learn? (6) | Retrospective on epic index |

Projects may adjust paths; the convention is the shape, not the directory names.

## Templates

- `templates/ROADMAP.md` — pure-tracker ROADMAP
- `templates/epic-index.md` — epic tracker
- `templates/content-doc.md` — research / spec / plan / ADR / reflection (frontmatter shape only; body is free-form)

Copy verbatim; edit in place.
