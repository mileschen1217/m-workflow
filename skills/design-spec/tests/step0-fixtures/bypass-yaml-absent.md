# Fixture: bypass-yaml-absent — AC-7 (Baseline always-on: Step 0 reached when yaml absent)
# Harness contract: skills/<skill>/tests/step0-fixtures/ two-layer schema
# Spec authority: .swarm/specs/2026-05-22-intention-first-baseline.md § AC-7
#
# .claude/m-workflow.yaml is absent; must NOT skip Step 0.
# This fixture proves Step 0 is REACHED.

```yaml
invocation: { skill: design-spec, args: "" }
setup:
  yaml:
    state: absent

# ── Layer 1 (deterministic) ──────────────────────────────────────────────
required-phrases:
  - "Please describe the intended work in your own words."   # full exact emit (Step 0 reached)

# harness-wide guard (implicit per spec § Interfaces "Harness-wide
# premature-hand-off invariant"): this fixture is NOT aim-handoff.
forbidden-substrings:
  - "Sharpened the Foundation aim into testable acceptance criteria — confirm or edit."
forbidden-mode: literal
```
