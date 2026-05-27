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
