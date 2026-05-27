---
name: design-review
kind: workflow
description: Reviews authored design documents (spec, plan, ADR) before Build using Pattern A (dual parallel). Dispatches `m-workflow:cross-provider-reviewer` composite skill with a doc-review system prompt set via task envelope. Out of scope — research notes, READMEs, retros, daily notes. Renamed from `m-deep-review`; per-batch code review path moved to `/m-workflow:code-review batch`.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
user-invocable: true
---

# /m-workflow:design-review — Design Document Review (Pattern A)

Reviews captured design artifacts before Build. The Stage 0 gate of the Review Gate.

## When to Invoke

Required when any of:
- A spec is authored by `/m-workflow:design-spec` and ready for review
- A plan is authored by `/superpowers:writing-plans` and ready for review
- An ADR is authored and introduces a new contract
- A discovery doc authored by `/m-workflow:arch-discovery` is matrix-complete and ready for end-of-discovery audit

Out of scope — return "not in scope; this skill reviews specs / plans / ADRs / discovery docs only" and exit:
- Research notes, daily notes, MOCs, retros, READMEs, kb articles

## Relationship to /m-workflow:design-spec (this is the gate; its Step-5 review is not)

`/m-workflow:design-spec` runs its own architect critique while drafting (its "Step-5 review"). That is **not** this gate — it is an author-time, advisory, skippable (`quick`) pass that judges the freshly-drafted spec. **This skill is the design-review gate**: C+H tiered (see §4), it blocks Build, and it judges the **final, human-accepted** artifact. The two are separated by the human accept step:

```
/m-workflow:design-spec  →  Status: Draft  →  human edits / accepts ★  →  /m-workflow:design-review (here)
```

`/m-workflow:design-spec`'s Step-5 review only *discharges* this gate when it was iterated to this skill's tiered standard (C+H=0) **and** the spec was not edited afterward. If the spec changed during the human's review, run this skill on the final version — the earlier critique judged a different artifact. Do not treat "design-spec was run" as "the gate passed".

## Usage

```
/m-workflow:design-review <path>            # one doc
/m-workflow:design-review <glob>            # multiple docs in one pass
```

## Procedure

### 0. Load vocabulary

> Read `${CLAUDE_PLUGIN_ROOT}/skills/_shared/step0-resolver.md`
> with the Read tool and follow it exactly.

If `source-as-truth` is in `bundle.disciplines`, also read
`${CLAUDE_PLUGIN_ROOT}/CONTEXT.md` § "Bridge content gate" AND
§ "Standing vs transient bridge" and load both sections into context for
the envelope below.

When dispatching to `m-workflow:cross-provider-reviewer`, include in envelope:

```json
{
  "task": "<existing>",
  "system_prompt": "<existing + loaded CONTEXT.md sections verbatim>",
  "discipline_mode": "source-as-truth",
  "source_as_truth_vocab": "<verbatim loaded text>",
  "role": "design-reviewer"
}
```

If not adopted: skip Read; envelope `discipline_mode: "none"`; omit `source_as_truth_vocab`.

The Bridge content audit (P1/P2/P3 application) and Standing vs transient classification procedures stay in this skill — they are the actions; CONTEXT.md provides the vocabulary they reference.

### 1. Validate input scope

Read the target file(s). Check frontmatter `type:` field if present, or path:
- `type: spec` OR path matches `**/specs/**` → in scope (use spec/plan/ADR system prompt)
- `type: plan` OR path matches `**/plans/**` → in scope (use spec/plan/ADR system prompt)
- `type: adr` OR path matches `**/adr/**` → in scope (use spec/plan/ADR system prompt)
- `type: discovery` OR path matches `**/research/**/*-discovery.md` → in scope (use **discovery system prompt** below)
- Anything else → out of scope; exit gracefully.

### 2. Dispatch m-workflow:cross-provider-reviewer (Pattern A)

```
Skill(skill: "m-workflow:cross-provider-reviewer", args: {
  "task": "<full text of the doc being reviewed>",
  "system_prompt": "<doc-review prompt below>",
  "role": "design-reviewer",
  "task_dir": "<optional: from caller context>"
})
```

### 3. Doc-review system prompt

**For spec / plan / ADR:**

> You are reviewing an authored design document (spec, plan, or ADR). Check:
> 1. Problem / Scope / Non-goals are concrete and falsifiable
> 2. Acceptance Criteria cover happy path, error paths, boundaries
> 3. Interfaces / Contracts are specific (field names, types, error returns)
> 4. Error Handling rows map to scenarios
> 5. Invariants are cross-cutting rules
> 6. Risks / Open Questions are not hidden
> 7. Verification Strategy declaration (evidence-honesty gate, Stage 0 — no test
>    source exists yet, so this is a DECLARATION check, never a coverage read):
>    the spec has a non-empty `## Verification Strategy` section. A
>    **boundary-crossing** AC is one whose Given/When/Then asserts a behaviour at
>    a boundary the code does not own — a process boundary, a network/API call, a
>    DB or filesystem write, device I/O, a real `Agent()`/sub-process dispatch, or
>    a deployed/wired target environment (boundary TYPES, not a closed keyword
>    list — match on behaviour, not wording). Every boundary-crossing AC id must
>    appear in the section's `Live-bearing AC IDs`. If it is ambiguous whether an
>    AC crosses such a boundary, treat it as live-bearing (default stricter).
>    Surface a missing/empty section or an omitted live-bearing AC as a finding.
>    Spec-internal judgment only — do NOT read test source or judge per-AC
>    coverage (those belong to code-review batch / epic-close).
>
> Return findings sorted by severity (Critical, High, Medium, Low). Each finding cites the section and a concrete fix. End with verdict: approve | revise | block.

**For discovery doc (`type: discovery`):**

> You are auditing an architecture discovery doc produced by `/m-workflow:arch-discovery`. Check:
> 1. §1 ownership / invariants are concrete and falsifiable (not vague "should" statements).
> 2. §2 platform layer cleanly separates capability / constraint / forced behavior.
> 3. §4 flows are E2E (not stubbed mid-walk); cite §1 invariants and §2 platform behaviors at each step.
> 4. §5 lifecycle re-walks §1/§3/§4 at every phase (not a parallel state machine).
> 5. §6 failures cover per-component / per-link / per-role.
> 6. §0 matrix has no `unset` or unjustified `N/A`; every `covered` cell cites a specific section.
> 7. Open questions are not hidden in prose — surfaced in §8.
>
> Return findings sorted by severity (Critical, High, Medium, Low). Each finding cites the section/cell and a concrete fix. End with verdict: approve | revise | block.

### 4. Apply findings

Quality gate (sums findings across reviewers):

- **C+H ≥ 5** → mandatory second-pass review. After applying fixes inline, re-invoke `/m-workflow:design-review <path>`. Build is blocked until a subsequent run returns **C+H = 0** (or only Medium/Low remain). The caller MUST run the second pass; do not skip on user discretion.
- **1 ≤ C+H < 5** → surface findings; block Build until Critical+High are resolved. Single-pass fix is sufficient; second pass optional.
- **C+H = 0, only Medium / Low** → surface findings; allow Build to proceed at user's discretion.

**Informed-consent checkpoint (orthogonal to the C+H gate):** if the composite's
returned synthesis carries a ⚠️ DEGRADED or ⚠️ PARTIAL banner, present the banner
text to the user VERBATIM and obtain explicit acknowledgement (an `AskUserQuestion`
choice, or an explicit user "proceed") BEFORE allowing Build to proceed. This applies
even when C+H == 0 — the banner is informational, not a hard block, but the workflow
MUST NOT auto-advance past it without the human knowingly acknowledging. A clean
review (no banner) does not trigger this checkpoint. The banner's meaning is defined
in `skills/cross-provider-reviewer/references/provenance.md`.

In all cases: do not auto-promote spec status; the user (or caller skill) decides when to proceed.

## Pattern semantics (self-contained)

Pattern A composite — dispatches `m-workflow:cross-provider-reviewer`, which owns the procedure end-to-end (parallel CC + Codex review, divergence-labeled synthesis, fallback if Codex unavailable).

## Renamed from m-deep-review

The previous `m-deep-review` covered both doc review AND per-batch code review. Per-batch code review now lives at `/m-workflow:code-review batch` (Pattern B). The old `m-deep-review` path returns "not found" (the skill registry no longer has that name).
