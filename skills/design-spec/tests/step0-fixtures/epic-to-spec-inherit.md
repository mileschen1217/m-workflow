# Fixture: epic-to-spec-inherit — AC-4 (Epic-to-spec inheritance)
# Harness contract: skills/<skill>/tests/step0-fixtures/ two-layer schema
# Spec authority: intention-first epic § AC-4

```yaml
invocation: { skill: design-spec, args: "" }
setup:
  parent_epic: { foundation: present }

# ── Layer 1 (deterministic) ──────────────────────────────────────────────
required-phrases:
  - "Does this spec's scope differ?"

forbidden-substrings:
  - "describe the intended work in your own words"   # from-scratch opener
  # harness-wide guard (implicit per spec § Interfaces "Harness-wide
  # premature-hand-off invariant"): this fixture is NOT aim-handoff.
  - "Sharpened the Foundation aim into testable acceptance criteria — confirm or edit."
forbidden-mode: literal

expected-foundation:                 # self-contained: all three present
  intention: "<fixture-fixed phase intention>"
  aim: "<fixture-fixed phase aim>"
  out-of-scope: ["<fixture-fixed route>"]
```
