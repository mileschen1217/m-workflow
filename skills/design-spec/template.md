---
type: spec
kind: bridge
date: YYYY-MM-DD
status: draft
epics: []
related: []
kill-on: <epic-slug>
---

# {{feature-name}} — Design Spec

**Date:** {{YYYY-MM-DD}}
**Status:** Draft

## Foundation

> Set at Draft Mode Step 0 via elicitation. Full phase version, all three
> fields — self-contained; must not require reading the parent epic to
> interpret. If a parent epic exists, its foundation is the starting point;
> sharpen to this phase's specifics. The spec has no tracker headline, so
> aim lives here (unlike the epic, where aim lives in the headline).

- **Intention (why):** <Full motivation: what hurts, what's broken, why
  this work is worth doing now.>
- **Aim:** <Observable goal: what does success look like for THIS spec's
  scope? Name the surface that observes success (user message, test pass,
  grep result, REST response).>
- **Out of scope:** 
  - <route this spec will NOT take, even if related — a route, not a
    category>
  - <up to three sub-bullets total; flat list, never nested>

## Source-level Deposit

> Filled by author at draft time. Names the lever (source-level change) this spec advances, or "none" with reason. Per the `source-as-truth` discipline (see CONTEXT.md § Bridge content gate — three principles): every feature epic carries a deposit budget so architecture compounds in source rather than prose. Stage 7 doc-reckoning reads this field at epic close.
>
> Skip this section entirely in projects that have NOT adopted the `source-as-truth` discipline — leave the heading off.

- **Lever this spec advances:** `<lever-slug>` — one of the project's lever menu (see project ROADMAP or CONTEXT.md § Four doc kinds), or `none`.
- **If `none`:** justify in one sentence (e.g., "pure bug fix, no source-encoding gap exposed" or "lever not yet defined for this RC").
- **Bridge docs this spec creates (if any):** list paths with `kill-on:` lever each declares. If a doc has no `kill-on:`, justify here (typically: navigation, workflow, or diagnostic — not bridge).
- **Bridge docs this spec will retire on landing:** list paths the lever's land deletes.
- **Three-principle audit (per new bridge doc, per the `source-as-truth` discipline, CONTEXT.md § Bridge content gate — three principles):** for each bridge `.md` listed above, answer:
  - **P1 (non-duplication):** what fact does this carry that source does NOT encode? Name the source path(s) checked. **Also reject doc-as-workaround:** if the paragraph exists to explain why dead / duplicative / obsolete source still exists, file a PR to remove the source instead; do not write the paragraph.
  - **P2 (falsifiable):** how would a reader verify a claim in this doc? Name one concrete check (test / probe / grep).
  - **P3 (no single host):** if you wrote this as a `///` doc-comment, which symbol would you attach it to? **One symbol** → rung 2, not a bridge. **One function body** → rung 3 (`// BRIDGE` block), not a `.md` bridge. **No answer (spans files/teams/languages, or describes negative space)** → rung 4 `.md`, justified. See CONTEXT.md § Bridge content gate — three principles for worked examples.
  - If any answer is missing or weak, fix the bridge content (delete duplicates / sharpen vague claims / move to rung 2-3) before submitting the spec.

## Problem

What hurts today? Concrete, scoped, falsifiable. State the user or system pain without jumping to a solution.

## Scope

(Optional) Implementation-level detail only — files, modules, repos. Boundary statements live in Foundation.out-of-scope; do not use legacy framing labels here.

**Touched files/modules:**
- <file or module path>

> Foundation.aim above is a provisional direction set at Step 0. The
> acceptance criteria below sharpen it into a testable form; that
> sharpening is confirmed with the user during drafting — it is not
> silently inherited.

## Acceptance Criteria

Given/When/Then scenarios — the **outer ATDD loop's contract**. Cover happy path, error paths, boundary values. Non-negotiable: every error path and boundary named here must correspond to at least one acceptance test scenario.

Every AC carries a stable `AC-N` id (1-based, assigned at draft, never reused within a spec) and appears both in the index table and as a `### AC-N` block. The `Test` column is `_(filled when test lands)_` at draft time and is populated at Stage-5 ATDD with a test reference or grep command (this realises the CLAUDE.md spec↔test bidirectional cross-reference).

### Index

| AC | Name | Test |
|---|---|---|
| AC-1 | <short-name> | _(filled when test lands)_ |

---

### AC-1 — <full-name>

```
Given <context>
When <action>
Then <observable outcome>
```

## Architecture

System shape — structure, components, data flow. Skip if the feature is purely additive within an existing module. Include a Mermaid diagram for non-trivial flows.

## Interfaces / Contracts

Function signatures, API shapes, message formats, config schemas. **Feeds the inner TDD loop** — each contract becomes a set of unit tests covering:
- Happy path
- At least one error path
- Boundary values
- Write-then-readback (for mutations)

Be specific — field names, types, optionality. Vagueness here means the inner loop has nothing concrete to assert against.

## Error Handling

Table: each row is a specific failure mode, its trigger, and the recovery behavior. Each row maps to a unit test in the inner TDD loop.

| Scenario | Trigger | Behavior |
|---|---|---|
| ... | ... | ... |

## Invariants

Cross-cutting correctness rules that must hold across every code path. Good invariants become property tests or assertion sweeps. Examples:
- "No operation modifies source files if the write phase fails."
- "Every successful run produces exactly one report."

## Risks / Open Questions

Unknowns that need resolution before or during build. Don't hide them — name them so the plan step can sequence around them.

## Related

- Links to exploration notes, prior specs, ADRs
- External references (papers, other projects, library docs)
