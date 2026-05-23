# Step-0 fixture replay runner — PENDING (Phase D, OQ-1 deferred)

The 18 Step-0 fixtures in `skills/*/tests/step0-fixtures/` are authored and
ready, but no replay runner is wired yet. This file records the pending
decision and the execution contract for whoever wires it.

## Status by verification tier (per ADR-0005 + the spec's two-layer model)

| Tier | What | Status |
|---|---|---|
| Structural Layer-1 | greps/awk over the four shipped files (AC-6, AC-7 local-conditional, AC-11, AC-5 template half) | **GREEN now** via `scripts/check-intention-first-l1.sh` — needs no runner |
| Behavioral Layer-1 (replay) | replay each fixture, assert deterministic fields (`required-phrases`, `forbidden-substrings`, `expected-foundation` incl. `aim-not-contains`, `expected-risk-notes`, `expected-artifacts`, `awk-shape`) | **pending-harness** — needs the replay runner below |
| Layer-2 rubric | judge AC-1 / AC-2 / AC-3 / AC-13 rubrics over `runs` with `min-pass` | **pending-runner** |

Only AC-1, AC-2, AC-3, AC-13 carry `rubric`/`runs`/`min-pass`. The other
ACs are Layer-1; their behavioral parts are pending-harness (replay), NOT
"verified" — the structural script does not exercise them.

## OQ-1 — which runner? (open)

Candidates named in ADR-0005 / the spec § Interfaces: `eval-harness`,
`agent-eval`, `ai-regression-testing`. Pick the one whose invocation
contract fits the two-layer fixture schema. Decision is the human's; none is
wired in this repo today.

## Execution contract for the runner (when wired)

Author `scripts/run-step0-fixtures.sh` supporting two modes:

- `--layer1` (deterministic, GATING): for each fixture, materialize `setup`
  / `session-state`, launch the skill per `invocation`, replay the `turns`
  (per `cases` entry if present), capture transcript + filesystem, and
  assert every populated Layer-1 field. Exact pass/fail, single run. ALL
  fixtures must pass.
- `--layer2` (rubric judge): replay each rubric-bearing fixture `runs`
  times; a cross-context / cross-provider judge applies the `rubric`;
  PASS iff ≥ `min-pass` of `runs` pass the full rubric (default 4/5).

Honor the harness-wide premature-hand-off invariant: the AC-13 hand-off
phrase is forbidden in every fixture except `aim-handoff`.

## Interim (until wired)

A human may replay any fixture by hand and check its deterministic fields
on demand. Structural Layer-1 (`scripts/check-intention-first-l1.sh`) is the
standing gate and stays GREEN.
