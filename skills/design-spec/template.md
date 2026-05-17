# {{feature-name}} — Design Spec

**Date:** {{YYYY-MM-DD}}
**Status:** Draft

## Intention

> Filled at draft-mode entry per global CLAUDE.md § Working Style intention-alignment gate. Locks scope before any structural review. If the parent epic has an `## Intention` block, restate verbatim and confirm with the user; do not re-interrogate.

- **Goal (observable):** <What does success look like? Surface that observes success.>
- **In scope:** <≤3 bullets — what this spec covers.>
- **Out of scope (explicit):** <≤3 bullets — what this spec will NOT touch even if related. Each is a route NOT taken.>
- **Fix vs. workaround:** <If a fixture / config knob / external workaround can achieve the goal, name it here. If proceeding with production-code change anyway, justify why the workaround is rejected.>
- **Smallest change:** <Minimum diff size and shape — N files in M repos. Name what would expand it past minimum.>

## Source-level Deposit

> Filled by author at draft time. Names the lever (source-level change) this spec advances, or "none" with reason. Per ADR `source-as-truth`: every feature epic carries a deposit budget so architecture compounds in source rather than prose. Stage 7 doc-reckoning reads this field at epic close.
>
> Skip this section entirely in projects that have NOT adopted the `source-as-truth` ADR — leave the heading off.

- **Lever this spec advances:** `<lever-slug>` — one of the project's lever menu (see project ROADMAP or the `source-as-truth` ADR), or `none`.
- **If `none`:** justify in one sentence (e.g., "pure bug fix, no source-encoding gap exposed" or "lever not yet defined for this RC").
- **Bridge docs this spec creates (if any):** list paths with `kill-on:` lever each declares. If a doc has no `kill-on:`, justify here (typically: navigation, workflow, or diagnostic — not bridge).
- **Bridge docs this spec will retire on landing:** list paths the lever's land deletes.
- **Three-principle audit (per new bridge doc, per ADR `source-as-truth` § Bridge content gate):** for each bridge `.md` listed above, answer:
  - **P1 (non-duplication):** what fact does this carry that source does NOT encode? Name the source path(s) checked. **Also reject doc-as-workaround:** if the paragraph exists to explain why dead / duplicative / obsolete source still exists, file a PR to remove the source instead; do not write the paragraph.
  - **P2 (falsifiable):** how would a reader verify a claim in this doc? Name one concrete check (test / probe / grep).
  - **P3 (no single host):** if you wrote this as a `///` doc-comment, which symbol would you attach it to? **One symbol** → rung 2, not a bridge. **One function body** → rung 3 (`// BRIDGE` block), not a `.md` bridge. **No answer (spans files/teams/languages, or describes negative space)** → rung 4 `.md`, justified. See ADR `source-as-truth` § Bridge content gate for worked examples.
  - If any answer is missing or weak, fix the bridge content (delete duplicates / sharpen vague claims / move to rung 2-3) before submitting the spec.

## Problem

What hurts today? Concrete, scoped, falsifiable. State the user or system pain without jumping to a solution.

## Scope

**In scope:** bullet list of what this feature includes.

**Non-goals:** bullet list of what this feature does NOT cover. Explicit non-goals prevent scope creep during implementation.

## Acceptance Criteria

Given/When/Then scenarios — the **outer ATDD loop's contract**. Cover happy path, error paths, boundary values. Each scenario is one row in the GWT grid.

```
Given <context>
When <action>
Then <observable outcome>
```

Non-negotiable: every error path and boundary named here must correspond to at least one acceptance test scenario. This is what the outer ATDD loop asserts before declaring the feature done.

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
