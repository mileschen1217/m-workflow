---
name: design-review
kind: workflow
description: Reviews authored design documents (spec, plan, ADR) before Build using Pattern A (dual parallel). Dispatches `m-workflow:cross-provider-reviewer` composite skill with a doc-review system prompt set via task envelope. Out of scope — research notes, READMEs, retros, daily notes. Renamed from `m-deep-review`; per-batch code review path moved to `/m-code-review batch`.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
user-invocable: true
---

# /m-design-review — Design Document Review (Pattern A)

Reviews captured design artifacts before Build. The Stage 0 gate of the Review Gate.

## When to Invoke

Required when any of:
- A spec is authored by `/m-design-spec` and ready for review
- A plan is authored by `/superpowers:writing-plans` and ready for review
- An ADR is authored and introduces a new contract
- A discovery doc authored by `/m-arch-discovery` is matrix-complete and ready for end-of-discovery audit

Out of scope — return "not in scope; this skill reviews specs / plans / ADRs / discovery docs only" and exit:
- Research notes, daily notes, MOCs, retros, READMEs, kb articles

## Usage

```
/m-design-review <path>            # one doc
/m-design-review <glob>            # multiple docs in one pass
```

## Procedure

### 0. Load vocabulary

Read `${CLAUDE_PROJECT_DIR}/.claude/m-workflow.yaml`. Check `adopted_disciplines`.

If contains `source-as-truth`:
  Read `${CLAUDE_PLUGIN_ROOT}/CONTEXT.md § "Bridge content gate"` AND `§ "Standing vs transient bridge"` — load both sections.

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
>
> Return findings sorted by severity (Critical, High, Medium, Low). Each finding cites the section and a concrete fix. End with verdict: approve | revise | block.

**For discovery doc (`type: discovery`):**

> You are auditing an architecture discovery doc produced by `/m-arch-discovery`. Check:
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

- **C+H ≥ 5** → mandatory second-pass review. After applying fixes inline, re-invoke `/m-design-review <path>`. Build is blocked until a subsequent run returns **C+H = 0** (or only Medium/Low remain). The caller MUST run the second pass; do not skip on user discretion.
- **1 ≤ C+H < 5** → surface findings; block Build until Critical+High are resolved. Single-pass fix is sufficient; second pass optional.
- **C+H = 0, only Medium / Low** → surface findings; allow Build to proceed at user's discretion.

In all cases: do not auto-promote spec status; the user (or caller skill) decides when to proceed.

## Pattern semantics (self-contained)

Pattern A composite — dispatches `m-workflow:cross-provider-reviewer`, which owns the procedure end-to-end (parallel CC + Codex review, divergence-labeled synthesis, fallback if Codex unavailable).

## Renamed from /m-deep-review

The previous `/m-deep-review` covered both doc review AND per-batch code review. Per-batch code review now lives at `/m-code-review batch` (Pattern B). The old `/m-deep-review` path returns "not found" (the skill registry no longer has that name).
