---
kind: workflow
adr_id: 0009
status: Accepted
date: 2026-05-27
---

# ADR-0009: Evidence-honesty gate — Baseline classification + derive-don't-maintain coverage

## Status

Accepted. Records the committed design decision for `testing-strategy` Phase 1
(spec `.swarm/specs/2026-05-26-testing-strategy-phase1-design.md`, `status: Accepted`,
design-review gate cleared at C+H=0). P1 shipped 2026-05-27 — all 11 ACs
implemented and committed on the worktree branch (the 9 files in the spec's
§ Scope; ADR-0009 + CONTEXT.md vocab were the two pre-done). The decision below is
firm regardless of build order; the status tracks shipped-ness, per the honesty
bedrock this ADR itself encodes.

## Triggered by

`/m-workflow:design-spec` (`.swarm/specs/2026-05-26-testing-strategy-phase1-design.md`).

## Related ADRs

ADR-0003 (`intention-first` as Baseline — the first Baseline; the classification
mechanism this ADR reuses), ADR-0004 (`source-as-truth` as Discipline — the sibling
role this gate is deliberately NOT), ADR-0005 (two-layer verification for
non-deterministic agent-behavior ACs — the verification-layering precedent this
builds on).

## Context

The plugin verifies component specs but can report done/green when the evidence
does not entail the claim — at any layer. Static checks + mocks pass while the
assembled/wired system fails on first real run; E13's own spec discharged 9 of 11
ACs by offline static proxies, only 2 live (and those hand-crafted, not produced by
the methodology). The honesty spine already exists for narration —
`grounded-claims` (`[假設]` unless cited), `source-as-truth` (code is truth, P2
falsifiable), `verification-before-completion`, `intention-first` — but
**behavioural done-ness ("it works") has no equivalent evidence discipline**, and
the principle is nowhere stated as the workflow's foundation.

Two decisions had to be made before any of the foundation layer could be built:

1. **What role is this gate?** Skill / Mode / Discipline / Baseline (the plugin's
   4-role taxonomy, CONTEXT.md). Getting this wrong means either per-project drift
   (if Discipline) or unwarranted always-on cost (if mis-scoped).
2. **How is a behavioural claim (AC) connected to the test that backs it?** The
   obvious answer — store an AC→test mapping (a requirement-traceability matrix) —
   has a known failure mode. The alternative is to derive coverage each pass.

## Decision

### (2a) Classify the evidence-honesty gate as an always-on **Baseline**, not a per-project Discipline

The invariant **claim ≤ evidence** is not something a project can rationally opt
out of: a project that opts out is not choosing "less verification overhead", it is
choosing "permission to report false-green silently" — which no project rationally
wants. The opt-out is therefore **illusory**, the same test ADR-0003 applied to
`intention-first`. So the gate is hardcoded into the existing reviewer gates
(design-review declaration check; `code-review batch` + epic-close coverage
criteria) and the epic-close reckoning — always-on, no `adopted_disciplines` entry,
no yaml toggle.

This is stated as the design's **standing classification that this ADR commits**.
If a future argument reclassifies it (e.g. a concrete project where opt-out is
genuinely rational), this ADR is the place to revise — the classification is a
recorded decision, not a silent assumption.

Why NOT Discipline (the role `source-as-truth` holds, ADR-0004): `source-as-truth`
governs a doc-philosophy that a doc-less prototype can rationally skip — a real
opt-out case. Evidence-honesty has no such case; false-green is never a rational
project choice. Different opt-out reality ⇒ different role.

### (2b) The gate enforces honest **status**, not **passing**

A known-red / known-incomplete claim **may proceed** if it is carried as an
explicit `[unverified: reason]` with informed human consent at epic-close —
known-bad is acceptable and plannable. What is forbidden is **green on weak
evidence**: a done/covered claim that no test in source actually backs, carried
silently. The gate blocks the silent false-green; it never blocks an honest
`[unverified]`. "Honest status, not passing" is the load-bearing distinction — this
is a verification-honesty gate, not a coverage-percentage gate.

### (2c) Coverage is **DERIVED** by the reviewer from test source, never maintained as a stored AC→test mapping (option B over A)

The rejected option A is a stored per-AC AC→test pointer (a Test column in the AC
table, or any maintained mapping). We reject it and instead have the **fresh-context
reviewer read the test source each pass** and judge per-AC whether a test asserts
that AC's Then-clause. Consequences of this choice, each committed here:

- the design-spec template **removes** any stored AC→test column; the **only
  authored per-AC marker is an inline `[unverified: reason]`** (reason mandatory).
  No per-AC red/green state is kept.
- the reviewer takes the **Given/When/Then FORM only** to make its judgment
  falsifiable ("does a test assert this Then?") — it does NOT adopt executable-spec
  tooling (Cucumber/Gherkin step-binding). Form, not machinery.
- **forced `[unverified]` is the safety net**: any AC the reviewer cannot confirm is
  emitted as `[unverified: reason]`, never passed by default.
- the per-AC accounting host is the **epic-close reckoning table**, authored once at
  close by reading source — so it cannot rot the way a continuously-maintained
  mapping does.
- a small deterministic **structural-floor checker** guards standing spec state
  (every AC enumerable, every `[unverified]` has a non-empty reason) within a strict
  determinism boundary — it does NOT judge coverage; all coverage judgment is the
  LLM reviewer's.

### (2d) Grounded in traceability research

This is not an aesthetic preference. `.swarm/research/2026-05-27-requirement-traceability-research.md`
records the grounding:

- **RTM rot** — requirement-traceability matrices consume 15–30% of effort and run
  ~40% stale; a stale mapping is *worse* than none because it claims coverage that
  isn't there.
- **Adzic's 10-year Specification-by-Example retrospective** — maintained AC→test
  mapping fails even with full Cucumber tooling; "derive, don't maintain" is the
  canonical resolution.
- **LLM-as-judge for AC coverage** is validated (~94% agreement), which makes the
  derive-each-pass approach tractable for a reviewer.

## Consequences

### Positive

- A committed foundation layer (philosophy doc + this ADR + reviewer criteria) that
  later layers (Phase 2 live/wired evidence, Phase 3 dogfood) hang on.
- No traceability matrix to rot: coverage is always read from current source, so it
  cannot claim coverage that no longer exists.
- "Honest status, not passing" lets known-bad work proceed with informed consent
  instead of forcing dishonest green — it raises honesty without lowering velocity.
- Baseline ⇒ uniform behaviour across every project using the plugin; no
  "did we adopt it here?" ambiguity.

### Negative / costs

- Deriving coverage each pass is reviewer work (read spec ACs + test source every
  batch / close) — a token + time cost the stored-mapping option would amortise.
  Accepted: the mapping's amortisation is illusory once it rots.
- Coverage-judgment **quality** (does the reviewer reliably catch silent
  false-green and mock-of-boundary proxies?) is non-deterministic — a dogfood
  question watched in Phase 3, not a P1 deterministic guarantee.
- The Baseline is unconditional; a project cannot turn it off even where it might
  feel like overhead. Accepted as the point of the classification.

### Implementation hooks

The 9 files in the spec's § Scope: `docs/evidence-honesty.md` (philosophy doc),
this ADR, the `design-spec` template (Verification Strategy section + `[unverified]`
marker, Test column removed), `design-spec`/`code-review`/`design-review` SKILL.md
prompts, `epic-driven-roadmap` close reckoning step, `scripts/check-spec-floor`
(structural floor), CONTEXT.md vocabulary (already landed).

## Deliberate scope choice (over-spec guard)

The human waiver of a non-live coverage gap is **recorded inline** in the reckoning
table (a human writes the rationale + linked issue in the row), NOT a schematized
cross-product of fields/roles/expiry. For a markdown plugin whose close runs once
per epic with a human in the loop, a specced waiver state-machine would be
over-engineering. This is an intentional simplicity decision, not an omission (see
memory `markdown-plugin-no-statemachine-overspec`).

## Alternatives considered

- **Stored AC→test mapping (option A — a Test column / RTM).** Rejected: it rots
  (research above); a stale mapping is worse than none.
- **Executable-spec tooling (Cucumber/Gherkin step-binding).** Rejected: we want the
  Given/When/Then *form* for falsifiability, not the machinery — the binding layer is
  exactly the maintenance burden Adzic's retrospective finds fails.
- **Classify as Discipline (per-project yaml opt-in).** Rejected: the opt-out case
  is illusory (no project rationally wants permission to false-green); per-project
  plumbing for a toggle nobody rational flips is dead weight (same logic as ADR-0003).
- **A separate auditor agent / new Review-Gate row.** Rejected (spec D-C): a
  fresh-context reviewer reading committed source under normal review already gives
  the independence; the criteria are applied as a *lens* at existing gates, not a new
  pass.
- **Date-expiry engine for `[unverified]`.** Rejected (spec D-B): the bound is
  *visibility* (every `[unverified]` is a reckoning-table row + a linked debt issue),
  not an automated expiry mechanism.

## Related

- `.swarm/specs/2026-05-26-testing-strategy-phase1-design.md` — the spec this ADR
  records (AC-2 names this ADR as a deliverable).
- `.swarm/research/2026-05-27-requirement-traceability-research.md` — RTM rot, Adzic
  SBE 10-year, LLM-as-judge; grounds B over A.
- `CONTEXT.md` § Verification vocabulary — the settled glossary (this ADR points at
  it for term definitions, does not restate them).
- `docs/evidence-honesty.md` — the committed philosophy doc (states the principle;
  this ADR records the decision).
- memory `workflow-of-honesty-bedrock` — root logic + settled P1 design.
- ADR-0003 (Baseline mechanism), ADR-0004 (Discipline sibling), ADR-0005
  (verification layering).
