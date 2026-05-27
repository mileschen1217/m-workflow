---
kind: workflow
adr_id: 0010
status: Accepted
date: 2026-05-27
---

# ADR-0010: Live-bearing AC contract — contract-only extension + three-way division of labour

## Status

Accepted. Records the committed design decision for `testing-strategy` Phase 2
(spec `.m-workflow/specs/2026-05-27-testing-strategy-phase2-design.md`). Phase 2
extends the Phase-1 evidence-honesty contract (ADR-0009) to evidence that crosses
a live boundary.

## Triggered by

`/m-workflow:design-spec` (`.m-workflow/specs/2026-05-27-testing-strategy-phase2-design.md`).

## Related ADRs

ADR-0009 (the Phase-1 evidence-honesty gate: Baseline classification +
derive-don't-maintain coverage — the contract this ADR extends), ADR-0005
(two-layer verification for non-deterministic agent-behaviour ACs — the
verification-layering precedent the live-dim-3 `Agent()` case relies on).

## Context

Phase 1 (ADR-0009) shipped the evidence-honesty contract for offline-dischargeable
evidence (in-repo test source the reviewer reads directly). It stated that a
live-bearing AC "closes ONLY with cited live evidence" but did not define what live
evidence is, what marks it authentic, or what a reviewer must demand. The three AOS
holes remained possible: real-scale perf faked via env, hooks never wired
end-to-end, the classifier agent never dispatched. These are this repo's instances
of a general live-boundary class — the same gap exists for any non-offline boundary
(device, network/DB, browser render, real dispatch).

## Decision

### (4a) Contract-only — no new skill, gate, or hook

Phase 2 EXTENDS the existing reviewer criteria (`code-review batch`) and the
epic-close reckoning rules to demand live evidence + provenance for a live-bearing
AC. It does NOT add a new skill, a new Review-Gate row, or a hook. Rationale: "done"
is not a harness event (settled in ADR-0009 / the Phase-1 grill); the existing
fresh-context reviewer already reads the spec and is the right judge. A new
mechanism would duplicate that judgment and re-introduce the no-hook decision this
project already made.

### (4b) Three-way division of labour

The decision recorded here is the **split of responsibility** for a live artifact
across three roles: the **producer** makes it, the **deterministic structural floor**
(`scripts/check-spec-floor.sh`) checks only that it exists and is referenced by its
AC, and the **fresh-context reviewer** authenticates it. The standing constraint is
**producer ≠ judge** — the builder ≠ reviewer discipline applied at the live-artifact
layer.

What each of `producer`, `live artifact`, and `provenance` *means* (and the
fakeability-scaling rule, and the floor-checks-existence-not-authenticity split) is
defined in `CONTEXT.md § Verification vocabulary` — this ADR records the division
decision, not the definitions.

### (4c) Motivated by the three AOS live dims

Dim 1 real-scale perf (PreCompact timeout faked via env), Dim 2 hook wiring via
central setup (install never run end-to-end), Dim 3 real `Agent()` dispatch
(classifier verified only to have `tools: Read`). Each is unpreventable by the
Phase-1 contract alone because each needs a live artifact, not in-repo test source.

## Deliberate scope choice (over-spec guard)

The decision: live-artifact provenance is authenticated by a human-in-the-loop
reviewer at close — we deliberately do NOT add a cryptographic signing / attestation
engine. For a markdown plugin whose close runs once per epic with a human in the
loop, a signing mechanism would be over-engineering (the same guard ADR-0009 applied
to the `[unverified]` waiver). This is an intentional simplicity decision, not an
omission. (What provenance consists of is defined in `CONTEXT.md § Verification
vocabulary`, not restated here.)

## Consequences

### Positive

- A live-bearing AC can no longer be silently discharged by a static proxy — the
  AOS-class hole is closed at the contract layer.
- No new mechanism to maintain: the demand rides the existing reviewer + reckoning.

### Negative / costs

- Authenticating a live artifact is reviewer work that scales with fakeability.
  Accepted: it is the cost of honest live-boundary done-ness.
- A solo-session build (CC builds AND would review) strains producer ≠ judge — what
  recusal means there is a Phase-3 dogfood watch item, not specced now.

## Bridge-gate compliance (source-as-truth)

- **P1 (non-duplication):** this ADR POINTS AT `docs/adr/0009-evidence-honesty-gate.md`
  for the Baseline classification + derive-don't-maintain decisions, and at
  `CONTEXT.md § Verification vocabulary` for the `live evidence / live artifact`,
  `producer`, and `provenance` term definitions. It does NOT restate them.
- **P3 (no single host):** the decision spans three skill modules (`code-review`,
  `epic-driven-roadmap`, `design-spec`) plus the design-spec template — there is no
  single symbol or function host. A decision record with no single host is correctly
  a rung-4 `.md` bridge.

## Related

- `.m-workflow/specs/2026-05-27-testing-strategy-phase2-design.md` — the spec this
  ADR records.
- `docs/adr/0009-evidence-honesty-gate.md` — the Phase-1 contract this extends.
- `CONTEXT.md` § Verification vocabulary — canonical term definitions (this ADR
  points at it, does not restate).
- `docs/evidence-honesty.md` — the philosophy doc (extended with the Phase-2
  live-bearing paragraph).
- `.m-workflow/research/2026-05-26-testing-strategy-gap.md` — the three AOS live dims.
