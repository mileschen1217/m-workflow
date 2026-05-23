# Step-0 fixtures — skill baseline (2026-05-23)

Baseline of the 18 intention-first Step-0 fixtures. **Two verification modes
were used** (faithful replay is the gold standard; static is a dry-run).

## Modes

- **Faithful replay** (gold): the orchestrator (Agent tool + SendMessage)
  spawns a SEPARATE under-test agent, feeds the fixture's user turns one at a
  time (the under-test agent never sees future turns or the assertions),
  captures its transcript, runs Layer-1 string checks, and a SEPARATE
  cross-context judge scores Layer-2 (builder≠reviewer per ADR-0005). Genuine
  independent behavioral verification.
- **Static conformance** (dry-run): a runner reasons whether a
  correctly-following agent WOULD satisfy the assertions. Confirms skill
  text ↔ fixtures are consistent, but is author-logic predicting itself.

Subagents have no Agent tool and headless `claude --dangerously-skip-
permissions` is blocked, so only the orchestrator can do faithful replay.

## Results — 18/18 FAITHFUL GREEN (1 run each)

| Fixture | Faithful replay |
|---|---|
| happy-epic | PASS (L1 5/5; L2 2/2; judge: stayed shallow) |
| empty-out-of-scope | PASS (sentinel verbatim after fix) |
| same-session-reuse | PASS (reuse log verbatim after fix) |
| happy-spec | PASS (L1; L2 2/2 via judge) |
| epic-to-spec-inherit | PASS (inheritance prompt) |
| vague-aim (7 cases) | PASS 7/7 (each: exact re-prompt + token-free aim) |
| vague-aim-user-override | PASS (exact warning + verbatim aim + risk note, after fix) |
| aim-handoff | PASS (L1 hand-off phrase; L2 3/3 via judge, after fix) |
| design-slide-attempt | PASS (L1 regex clean + L2 stayed-shallow via judge, after fix) |
| scope-reframe | PASS (stop message, no spec written) |
| legacy-epic | PASS (legacy note + opener, no inheritance prompt) |
| same-session-reuse-spec | PASS (inheritance, not reuse) |
| bypass-quick / with-vendor / unknown-arg / yaml-absent / yaml-no-intention-first | PASS (Step 0 reached, opener verbatim) |
| bypass-invalid-vendor | PASS (loud error verbatim, no spec, Step 0 not reached) |

## pass@5 (2026-05-23) — all 18 fixtures, orchestrator-driven, sonnet under-test + sonnet judge

Ran every fixture 5× (≥4/5 threshold per the AC). Result: **18/18 PASS**
after three pass@5 fixes (below).

| Fixture(s) | pass@5 |
|---|---|
| 6 bypass (quick/with-vendor/unknown-arg/yaml-absent/yaml-no-if/invalid-vendor) | 5/5 each |
| same-session-reuse, same-session-reuse-spec, epic-to-spec-inherit, legacy-epic | 5/5 each |
| happy-epic | 5/5 (L1 + L2 rubric via judge) |
| happy-spec | 5/5 (L1 + L2 rubric) |
| design-slide-attempt | 5/5 (after AC-3 regex narrowing; L2 stay-shallow 5/5) |
| vague-aim-user-override | 5/5 (exact warning) |
| scope-reframe | 5/5 (exact stop message) |
| empty-out-of-scope | 5/5 (verbatim sentinel + Open-Q note) |
| aim-handoff | 5/5 (verbatim hand-off phrase + L2 rubric) |
| vague-aim (7 cases) | PASS by corrected behavioral model (see finding 3) — decline-and-ask-observable was 5/5 across every token; token-free synthesis deterministic. (complex/careful behavior covered by the model + single-run; not individually 5×'d.) |

### Defects found by pass@5 (fixed; pass@1 had missed them)

1. **yaml-no-if fixture under-specified** — pass@5 2/5: 3 runs mis-routed to
   Setup Mode because the fixture pinned only `m-workflow.yaml`, not
   `design-spec.yaml` (the Draft-vs-Setup trigger). Pinned the Draft-Mode
   precondition → 5/5. (commit b0edccc)
2. **AC-3 regex over-broad** — Layer-2 5/5 but Layer-1 4/5: a correct
   deflection that NAMED the deferred topic ("migration path") tripped the
   bare token. Narrowed bare topic-nouns → interrogative/verb-anchored →
   5/5. (commit 72dee9e)
3. **AC-8 re-prompt mis-specified as a Layer-1 exact phrase** (THE big one)
   — pass@5 across all 7 tokens: should/better 5/5 exact, but usually 0/5,
   typically 2/5, elegant 2/5. Agents correctly DECLINE the vague aim but
   ask richer/varied clarifying questions instead of the rote phrase.
   Reclassified the re-prompt to a Layer-2 rubric (per ADR-0005); kept
   Layer-1 only for the deterministic final-aim checks. (commit e756b90)

### Key insight (generalizable to the whole skill-workflow foundation)

Exact-string reliability depends on the NATURE of the emit:
- **Mandated single-emit at an unambiguous decision point** (opener,
  confirm, warning, stop, legacy note, reuse log, sentinel, hand-off
  phrase): RELIABLE 5/5 when the skill frames it emphatically as a fixed
  emit.
- **A generic elicitation question that competes with the agent's instinct
  to ask richer/better questions** (the AC-8 re-prompt): UNRELIABLE as an
  exact string — it MUST be a Layer-2 behavioral rubric.

So: exact Layer-1 substrings for decision-point emits; Layer-2 rubrics for
process/elicitation behaviors. pass@1 hid finding 3 because it happened to
use tokens (should) that trigger the rote phrase; only pass@5 across token
types exposed it.

## Defects found by faithful replay (fixed; static pass had missed them)

Faithful replay (independent agents) caught real divergences the static
conformance pass predicted away. All fixed by making casually-framed
fixed-emit strings emphatic ("emit this EXACT … verbatim, do not paraphrase")
and inlining them where only referenced:

1. **Reuse log** paraphrased ("Skipping Step 0 …") instead of the verbatim
   "Foundation already confirmed this session — reusing". (commit 196d7e5)
2. **AC-8b warning + risk note**: design-spec only *referenced* the override
   path — never inlined the strings, so a design-spec agent couldn't emit
   them. Inlined verbatim. (commit aa93b4a)
3. **Out-of-scope sentinel** + **branch-a inheritance prompt** were flaky
   (one agent improvised 3 questions instead of the exact prompt). Hardened
   to fixed-emit. (commit aa93b4a)
4. **Design-probe deflection** echoed the user's design term ("migration
   path"), tripping the AC-3 Layer-1 regex — the exact residual risk this
   file flagged in the first baseline. Deflection is now topic-free. (aa93b4a)

The general lesson: an exact-emit string is only reliably emitted verbatim
when the skill frames it emphatically as a fixed emit; casual framing
("warn 'X'", "ask: 'X'") gets paraphrased. All Step-0 fixed-emits now use
the emphatic pattern.

## Mechanism validated

Orchestrator-driven subagent replay + cross-context judge is a working
faithful-verification method (no headless engine needed). A portable
unattended CI runner (`scripts/run-step0-fixtures.sh` over `claude -p`) +
the ≥4/5 pass@k sampling remain future work (see `LAYER2-RUNNER.md`, OQ-1).
