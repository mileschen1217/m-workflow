# Fixture: bypass-unknown-arg — AC-7 (Baseline always-on: Step 0 reached on unrecognized arg)
# Harness contract: skills/<skill>/tests/step0-fixtures/ two-layer schema
# Spec authority: intention-first epic § AC-7
#
# "report-export" is parsed as feature_name (not a flag); must NOT skip Step 0.
# This fixture proves Step 0 is REACHED.

```yaml
invocation: { skill: design-spec, args: "report-export" }

# ── Layer 1 (deterministic) ──────────────────────────────────────────────
required-phrases:
  - "Please describe the intended work in your own words."   # full exact emit (Step 0 reached)

# harness-wide guard (implicit per spec § Interfaces "Harness-wide
# premature-hand-off invariant"): this fixture is NOT aim-handoff.
forbidden-substrings:
  - "Sharpened the Foundation aim into testable acceptance criteria — confirm or edit."
forbidden-mode: literal
```
