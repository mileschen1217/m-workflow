# Fixture: bypass-quick — AC-7 (Baseline always-on: Step 0 reached on "quick" arg)
# Harness contract: skills/<skill>/tests/step0-fixtures/ two-layer schema
# Spec authority: intention-first epic § AC-7
#
# "quick" is a real modifier that skips the Step-5 architect dispatch,
# but must NOT also skip Step 0. This fixture proves Step 0 is REACHED.

```yaml
invocation: { skill: design-spec, args: "quick" }

# ── Layer 1 (deterministic) ──────────────────────────────────────────────
required-phrases:
  - "Please describe the intended work in your own words."   # full exact emit (Step 0 reached)

# harness-wide guard (implicit per spec § Interfaces "Harness-wide
# premature-hand-off invariant"): this fixture is NOT aim-handoff.
forbidden-substrings:
  - "Sharpened the Foundation aim into testable acceptance criteria — confirm or edit."
forbidden-mode: literal
```
