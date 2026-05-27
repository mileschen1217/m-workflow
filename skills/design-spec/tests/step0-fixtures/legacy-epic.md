# Fixture: legacy-epic — AC-14 (Legacy parent epic falls through to full elicitation)
# Harness contract: skills/<skill>/tests/step0-fixtures/ two-layer schema
# Spec authority: intention-first epic § AC-14
#
# design-spec invoked within an epic whose index.md predates this build
# (carries a legacy ## Intention block, NOT a ## Foundation section).
# Layer 1 only — no rubric/runs/min-pass.

```yaml
invocation: { skill: design-spec, args: "" }
setup: { parent_epic: { foundation: legacy-intention } }

# ── Layer 1 (deterministic) ──────────────────────────────────────────────
required-phrases:
  - "Please describe the intended work in your own words."   # full elicitation
    # full phrase WITH period — intentionally stricter than AC-7's substring
    # form; both pass when the skill emits the full opener
  - "Parent epic uses legacy Intention format — consider updating it."  # exact note

forbidden-substrings:
  - "Does this spec's scope differ?"   # inheritance pre-fill must NOT fire
  # harness-wide guard (implicit per spec § Interfaces "Harness-wide
  # premature-hand-off invariant"): this fixture is NOT aim-handoff.
  - "Sharpened the Foundation aim into testable acceptance criteria — confirm or edit."
forbidden-mode: literal

expected-foundation:                   # full elicitation still yields all three
  intention: "<fixture-fixed>"
  aim: "<fixture-fixed>"
  out-of-scope: ["<fixture-fixed route>"]
```
