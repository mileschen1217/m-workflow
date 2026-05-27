# Fixture: same-session-reuse — AC-10 (Same-invocation reuse, not re-elicitation; epic)
# Harness contract: skills/<skill>/tests/step0-fixtures/ two-layer schema
# Spec authority: intention-first epic § AC-10

```yaml
invocation: { skill: epic-driven-roadmap, args: "" }
session-state: { foundation_confirmed_this_invocation: true }

# ── Layer 1 (deterministic) ──────────────────────────────────────────────
required-phrases:
  - "Foundation already confirmed this session — reusing"

forbidden-substrings:
  - "describe the intended work in your own words"   # no from-scratch opener
  # harness-wide guard (implicit per spec § Interfaces "Harness-wide
  # premature-hand-off invariant"): this fixture is NOT aim-handoff.
  - "Sharpened the Foundation aim into testable acceptance criteria — confirm or edit."
forbidden-mode: literal
```
