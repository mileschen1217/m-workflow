# Fixture: design-slide-attempt — AC-3 (Shallow boundary: gate does not slide into design)
# Harness contract: skills/<skill>/tests/step0-fixtures/ two-layer schema
# Spec authority: .swarm/specs/2026-05-22-intention-first-baseline.md § AC-3, § Interfaces "AC-3 forbidden regex families"
#
# User turns include: "which package?", "what endpoint contract?",
# "what migration path?", "how should we build it?"

```yaml
invocation: { skill: design-spec, args: "" }
turns:   # user prods toward design; the agent must stay shallow and deflect,
         # then still synthesise the three fields (AC-3)
  - { role: user, text: "Port the stats config to the new schema." }
  - { role: user, text: "which package?" }
  - { role: user, text: "what endpoint contract?" }
  - { role: user, text: "what migration path?" }
  - { role: user, text: "how should we build it?" }
  - { role: user, text: "aim: the config parses under the v2 schema" }
  - { role: user, text: "confirmed" }

# ── Layer 1 backstop ─────────────────────────────────────────────────────
# SINGLE SOURCE OF TRUTH for these patterns is spec § Interfaces "AC-3 forbidden
# regex families" (incl. the premature-hand-off guard). The fixture is
# DERIVED: each line from that section joined into ONE grep -iE pattern with
# "|". The fixture field is a one-item list (the single joined pattern), to
# match the schema's list type even in regex mode. If § Interfaces changes,
# regenerate this field — do not hand-edit it independently.
#
# The final alternation "Sharpened the Foundation aim into testable acceptance criteria"
# is the harness-wide premature-hand-off guard (spec § Interfaces). It is included
# in the AC-3 regex set per spec; aim-handoff.md is the sole fixture exempt from it
# (not this one).
  # NOTE: bare topic-nouns (rollout|migration path|backfill|workaround) were
  # REMOVED — they false-positived on legitimate deflections that NAME the
  # deferred topic (pass@5: an agent deflecting "we'll defer the migration
  # path" tripped the bare token though it stayed shallow). Replaced with
  # interrogative/verb-anchored forms so the backstop fires only when the
  # agent ASKS a design question, not when it names a topic it is deferring.
  # Layer-2 rubric remains the PRIMARY shallow check (ADR-0005).
forbidden-substrings:
  - "which (package|library|framework|dependency)|how many files|which (file|files|module|modules)|edit the file|what (api|endpoint|schema|contract|interface|signature|payload)|which tests?|what tests? (do|to) (we|edit)|which fixture to edit|how (big|long)|diff size|smallest diff|story point|estimate the|how should we (build|implement|structure|roll ?out|deploy|migrate)|what.{0,10}(migration path|rollout|deployment)|fix or work ?around|fix strategy|patch vs|Sharpened the Foundation aim into testable acceptance criteria"
forbidden-mode: regex        # grep -iE; matches nothing before synthesis

expected-foundation:         # synthesis still produces the three fields
  intention: "<fixture-fixed>"
  aim: "<fixture-fixed>"
  out-of-scope: ["<fixture-fixed route>"]

# ── Layer 2 primary ──────────────────────────────────────────────────────
runs: 5
min-pass: 4
rubric:
  - "Did any agent turn before synthesis discuss implementation, tech /
     library choice, files / modules, effort / diff size, rollout /
     deploy, or fix-vs-workaround strategy? (Y=FAIL | N=pass)"
  - "When the user prodded toward design, did the agent deflect to a
     later stage and steer back to intention/aim/out-of-scope?
     (Y=pass | N=fail)"
```
