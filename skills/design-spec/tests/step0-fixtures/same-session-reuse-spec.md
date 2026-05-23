# Fixture: same-session-reuse-spec — AC-10 (Same-invocation reuse, design-spec; fresh invocation)
# Harness contract: skills/<skill>/tests/step0-fixtures/ two-layer schema
# Spec authority: .swarm/specs/2026-05-22-intention-first-baseline.md § AC-10
#
# design-spec; a parent epic foundation is present, but this is a FRESH
# invocation — session-state false. Reuse is same-invocation only; a fresh
# invocation whose parent epic has ## Foundation takes the inheritance path (AC-4).

```yaml
invocation: { skill: design-spec, args: "" }
setup: { parent_epic: { foundation: present } }
session-state: { foundation_confirmed_this_invocation: false }

# ── Layer 1 (deterministic) ──────────────────────────────────────────────
required-phrases:
  - "Does this spec's scope differ?"          # inheritance path (AC-4)

forbidden-substrings:
  - "Foundation already confirmed this session — reusing"   # NOT reuse
  # harness-wide guard (implicit per spec § Interfaces "Harness-wide
  # premature-hand-off invariant"): this fixture is NOT aim-handoff.
  - "Sharpened the Foundation aim into testable acceptance criteria — confirm or edit."
forbidden-mode: literal
```
