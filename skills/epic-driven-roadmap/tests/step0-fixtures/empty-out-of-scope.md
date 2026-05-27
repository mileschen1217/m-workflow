# Fixture: empty-out-of-scope — AC-9 (Out-of-scope sentinel on decline)
# Harness contract: skills/<skill>/tests/step0-fixtures/ two-layer schema
# Spec authority: intention-first epic § AC-9

```yaml
invocation: { skill: epic-driven-roadmap, args: "" }

# ── Layer 1 (deterministic) ──────────────────────────────────────────────
required-phrases:
  - "one thing this work will NOT touch"

expected-foundation:
  out-of-scope:
    - "(no explicit boundary declared)"   # EXACT sentinel literal string

expected-risk-notes:
  - "(no explicit boundary declared)"      # paired entry in Open Questions

# harness-wide guard (implicit per spec § Interfaces "Harness-wide
# premature-hand-off invariant"): this fixture is NOT aim-handoff.
forbidden-substrings:
  - "Sharpened the Foundation aim into testable acceptance criteria — confirm or edit."
forbidden-mode: literal
```
