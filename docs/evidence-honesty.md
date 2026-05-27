---
kind: workflow
date: 2026-05-27
---

# Evidence Honesty

The workflow's foundation stance for behavioural done-ness.

## The principle

A **claim never exceeds its evidence.** A feature is reported done / green only
when evidence in source entails the claim. Known-bad is acceptable and plannable
— a gap carried as an explicit `[unverified: reason]` with informed human consent
may proceed. **Silent false-green is not acceptable**: a done/covered claim that
no test actually backs, carried without disclosure, is the one thing this stance
forbids. The gate enforces honest *status*, not *passing* — known-red may proceed
with consent; green on weak evidence may not.

## One spine, four siblings

Evidence-honesty is the deliverable-certification sibling of the plugin's existing
honesty spine — `grounded-claims`, `source-as-truth`,
`verification-before-completion`, and `intention-first`. Same spine, different
surface: those govern narration, docs, scope, and evidence-before-claims; this one
governs "it works". For the precise term definitions, see
`CONTEXT.md § Verification vocabulary` — this doc states the stance and does not
restate the glossary.

## How it is enforced (falsifiable)

Coverage is **derived** by the fresh-context reviewer reading test source each
pass — there is no stored AC→test mapping to rot. The reviewer applies the coverage
criteria at `code-review batch` and at epic-close (where test source exists), and
the lighter *declaration* check at design-review (Stage 0, before any test exists).
Each of those behaviours is falsifiable by grep against the shipped SKILL.md prompts
(see the keystone decision in `docs/adr/0009-evidence-honesty-gate.md`). A
deterministic structural-floor checker (`scripts/check-spec-floor.sh`) guards the
standing spec state — every AC enumerable, every `[unverified]` justified.

## Live-bearing claims (the live boundary)

Some claims cross a **live boundary** — a real device, a network/DB call, a real
browser render, a real `Agent()` dispatch, real-scale perf. These cannot be
discharged offline. A live-bearing AC requires a **live artifact** (the captured
output of actually exercising the behaviour against the real boundary, never a
static proxy or mock) carrying **provenance** (which producer made it + freshness),
which a fresh-context reviewer authenticates at `code-review batch` and epic-close.
The producer is never the reviewer (producer ≠ judge). For the term definitions see
`CONTEXT.md § Verification vocabulary`; for the contract-only-not-skill decision and
the three-way division of labour see `docs/adr/0010-live-bearing-ac-contract.md` —
this doc states the stance and points at those, it does not restate them.
