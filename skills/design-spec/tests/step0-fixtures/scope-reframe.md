# Fixture: scope-reframe — AC-12 (Scope reframe creates no spec file)
# Harness contract: skills/<skill>/tests/step0-fixtures/ two-layer schema
# Spec authority: intention-first epic § AC-12
#
# During sharpening the user reframes the work to a fixture / spike / config
# knob / workaround. This is the motivating failure mode.

```yaml
invocation: { skill: design-spec, args: "" }

# ── Layer 1 (deterministic) ──────────────────────────────────────────────
required-phrases:
  - "Scope reframed to "          # anchors the stop-message prefix
  - "a design spec is not needed"
  - "Exiting Draft Mode"

expected-foundation: none           # stop-case: nothing synthesised

expected-artifacts:
  specs_dir_delta: 0                 # no .md created under $SPECS_DIR

# harness-wide guard (implicit per spec § Interfaces "Harness-wide
# premature-hand-off invariant"): this fixture is NOT aim-handoff.
forbidden-substrings:
  - "Sharpened the Foundation aim into testable acceptance criteria — confirm or edit."
forbidden-mode: literal
```
