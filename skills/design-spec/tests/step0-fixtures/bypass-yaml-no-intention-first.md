# Fixture: bypass-yaml-no-intention-first — AC-7 (Baseline always-on: Step 0 reached when yaml present but adopted_disciplines empty)
# Harness contract: skills/<skill>/tests/step0-fixtures/ two-layer schema
# Spec authority: intention-first epic § AC-7
#
# .claude/m-workflow.yaml is present but adopted_disciplines is empty
# (intention-first not listed); must NOT skip Step 0.
# This fixture proves Step 0 is REACHED.

```yaml
invocation: { skill: design-spec, args: "" }
setup:
  design_spec_yaml: present   # DRAFT MODE precondition (NOT Setup Mode) —
                              # MUST be pinned: this fixture stresses
                              # m-workflow.yaml's empty adopted_disciplines,
                              # and without pinning design-spec.yaml present
                              # the agent may mis-route to Setup Mode
                              # (observed 3/5 in pass@5 when unpinned).
  yaml: { state: present, adopted_disciplines: [] }   # m-workflow.yaml

# ── Layer 1 (deterministic) ──────────────────────────────────────────────
required-phrases:
  - "Please describe the intended work in your own words."   # full exact emit (Step 0 reached)

forbidden-substrings:
  # Setup-Mode mis-route guard: the specs-dir question must NOT appear
  # (design-spec.yaml is present → Draft Mode, not Setup Mode):
  - "Where should design specs live"
  # harness-wide premature-hand-off guard (this fixture is NOT aim-handoff):
  - "Sharpened the Foundation aim into testable acceptance criteria — confirm or edit."
forbidden-mode: literal
```
