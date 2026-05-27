---
kind: workflow
adr_id: 0011
status: Accepted
date: 2026-05-28
---

# ADR-0011: Honesty spine as Constitution; control-axis collapse; rename to `touchstone`

## Status

Accepted. Keystone decision of the `workflow-suite-audit` epic. Decisions D1–D3
(honesty spine + control-axis collapse + audit criterion) are shipped — landed in
`CONTEXT.md § Honesty spine` on the worktree branch. Decision D4 (rename) is a
committed go decision whose **execution is a separate migration epic** (not this
audit epic — scope discipline).

## Triggered by

The `workflow-suite-audit` epic. Phase 1 (delegated honesty-spine audit, T01)
confirmed the spine is substantially threaded across the suite; Phase 2 decided the
rename. Vocabulary was sharpened at a Stage-1.5 grill (2026-05-28).

## Related ADRs

- ADR-0009 (evidence-honesty gate — Baseline + derive-don't-maintain) and ADR-0010
  (live-bearing AC contract): the two prior honesty-lineage ADRs. This ADR elevates
  their shared `claim ≤ evidence` principle from "a property two instances share" to
  a named Constitution-level spine.
- ADR-0002 (`grounded-claims` as Mode) and ADR-0004 (`source-as-truth` as Discipline):
  the other two carriers of the spine (narration; doc↔source).

## Context

The plugin's stages were added one problem at a time. The `testing-strategy` epic
surfaced the load-bearing principle — **a claim never exceeds its evidence; gaps are
marked, not hidden** — but the suite had never been re-read whole to confirm the
principle threads every stage rather than only the few surfaces that own an explicit
honesty mechanism. Two scaffolded backlog epics (`workflow-control-axis-audit` +
`honesty-lens-and-rename`/E18) were merged into `workflow-suite-audit`; at the grill
they collapsed into one lens (below).

Separately, the package name `m-workflow` carries two problems: the `m-` is personal
(miles) and opaque, and "workflow" is generic — neither signals what the plugin is or
invites adoption on a public repo.

## Decision

**D1 — Honesty spine is Constitution, not a shared property.** `claim ≤ evidence`
(gaps marked, not hidden) is elevated to a first-class organizing principle that
every stage is accountable to (`CONTEXT.md § Honesty spine`). It is **not a fifth
role** — it is content carried *through* the four roles (`grounded-claims` Mode for
narration; `testing-strategy` gate for deliverable certification; `source-as-truth`
Discipline for doc↔source).

**D2 — Control-axis collapses into the spine's two arms.** Feedforward (anticipatory
declaration: declare the claim + required evidence up front) and feedback (verification:
measure whether the claim held, force any gap to be marked) are the spine's **two
arms**, not a separate lens. The general control-system audit (is the suite FF-heavy
vs FB-heavy across *all* concerns, incl. scope/quality) is **dropped** — honesty is
that axis landed.

**D3 — Audit criterion is silent-false-green, not arm-completeness.** A stage need
not have both arms. The defect is a claim that exceeds its evidence and is closed by
no mechanism anywhere (this stage or downstream). A one-armed or armless stage is
sound when it makes sense (no unclosed claim). (Phase 1 applied this: ~11 threaded,
7 one-armed-but-sound, 3 gaps — of which 2 are accepted honest-by-design residuals
and 1 (arch-review consent) routes to existing candidate E19.)

**D4 — Rename to `touchstone`, executed now.**
- A **honesty-thematic** name (e.g. `honesty-workflow`) is **rejected** — a theme may
  broaden as new lenses appear (the very risk that would re-trigger a rename), and the
  identity is already captured in `CONTEXT.md § Honesty spine`.
- An **adoption-driven** rename to a theme-neutral, durable name is **accepted**, and
  executed **now rather than deferred**: the breaking blast radius (`m-workflow:*`
  namespace across every skill call, agent dispatch, marketplace entry, consuming
  `.claude/*.yaml`, global routing, docs) grows monotonically, and current external
  adoption is ≈ 0 — so the migration is cheapest now and only gets more expensive.
- Name: **`touchstone`** (試金石 — a stone used to test the authenticity/purity of
  metal; literally a test of what is genuine). Reflects the honesty attitude via
  metaphor without binding to a theme-label; neutral, recognizable, adoption-friendly.

## Consequences

- `CONTEXT.md § Honesty spine` is the canonical home for the spine + its two arms +
  the audit criterion. ADR-0009/0010 remain the instance-level decisions.
- The general control-system audit is not pursued; if a non-honesty FF/FB balance
  question ever arises, it would be a fresh epic, not this one.
- **The rename migration is a separate epic** (to scaffold next): rename namespace
  `m-workflow:*` → `touchstone:*`, marketplace/`plugin.json`, every skill/agent/command
  cross-ref, consuming `.claude/m-workflow.yaml` → new name, global `~/.claude/CLAUDE.md`
  routing, repo + docs. Breaking; near-irreversible once published — do it as one
  deliberate pass while adoption is ≈ 0.
- The audit's 3 gaps: grill self-attestation + grounded-claims Mode-selectivity are
  accepted honest-by-design residuals; arch-review consent → E19.

## Alternatives considered

- **Defer rename to 0.2** — rejected: deferring does not reduce cost, it grows it (more
  references accrue); and there are no current external adopters whose expectations a
  major-version boundary would protect.
- **Keep `m-workflow`** — rejected: opaque personal prefix + generic noun hurt adoption
  on a public repo.
- **Honesty-thematic name** — rejected: theme-fragile (see D4).
- **Keep control-axis as a second lens** — rejected at grill: it is the spine's internal
  structure, not an orthogonal lens; keeping it would dilute the epic's focus.
