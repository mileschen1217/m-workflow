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

- **Lever this spec advances:** `<lever-slug>` — one of the project's lever menu (the menu is per-project; see project ROADMAP. Lever-epic concept defined in CONTEXT.md § Validation rubric (load-bearing)), or `none`.
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

The verification layer/mechanism never appears in an AC's Name or Given-When-Then — coverage is derived and `[unverified]` is the only authored marker (no implementation leakage into the contract).

Every AC carries a stable `AC-N` id (1-based, assigned at draft, never reused within a spec) and appears both in the index table and as a `### AC-N` block. **No stored AC→test mapping and no per-AC red/green state is kept** — coverage is DERIVED each review pass by the reviewer reading test source (see `docs/adr/0009-evidence-honesty-gate.md`, decision 2c). The ONLY authored per-AC marker is an inline `[unverified: <reason>]` line under an AC's Given/When/Then, with a mandatory non-empty reason; a live-bearing AC (one listed in Verification Strategy) may NOT carry it.

### Index

| AC | Name |
|---|---|
| AC-1 | <short-name> |

---

### AC-1 — <full-name>

```
Given <context>
When <action>
Then <observable outcome>
```

## Verification Strategy

> Coarse, risk-scaled — NOT per-AC. ~4–7 lines. States which risk layers this
> feature needs and which ACs carry live evidence. Read at design-review (presence
> + live-bearing coherence) and at epic-close (the live-bearing list gates which
> ACs may NOT be carried as `[unverified]`). See `docs/adr/0009-evidence-honesty-gate.md`.

- **Risk layers this feature needs:** <unit? integration? contract? e2e? live? perf?>
- **Power-on-able?** <can the design be exercised at the needed layer; if not, why / what's needed>
- **Live means required:** <fixture / target / device / none>
- **Live-bearing AC IDs:** <AC-N, AC-M | none>   ← these may NOT be carried as `[unverified]`
  > Live-bearing = the AC's real behaviour cannot be discharged offline (un-owned
  > process / real-scale / wired / deployed target). Invoking your OWN deterministic
  > in-repo script in a test is owned + offline → NOT live-bearing.

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
