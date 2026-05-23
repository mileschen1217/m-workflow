# Fixture: vague-aim-user-override — AC-8b (User-confirmed vague-aim override)
# Harness contract: skills/<skill>/tests/step0-fixtures/ two-layer schema
# Spec authority: .swarm/specs/2026-05-22-intention-first-baseline.md § AC-8b
#
# After synthesis, the user edits the aim to reintroduce a vague token.

```yaml
invocation: { skill: design-spec, args: "" }

# ── Layer 1 (deterministic) ──────────────────────────────────────────────
required-phrases:
  - "(aim contains a vague token — accept anyway?)"   # EXACT warning

expected-foundation:
  aim: "<user's vague aim, recorded verbatim on accept>"

expected-risk-notes:
  - "(aim contains an unverifiable token — user-confirmed)"

# harness-wide guard (implicit per spec § Interfaces "Harness-wide
# premature-hand-off invariant"): this fixture is NOT aim-handoff.
forbidden-substrings:
  - "Sharpened the Foundation aim into testable acceptance criteria — confirm or edit."
forbidden-mode: literal
```
