# Fixture: bypass-invalid-vendor — AC-7 negative (Parse error: "with llama" is an invalid vendor)
# Harness contract: skills/<skill>/tests/step0-fixtures/ two-layer schema
# Spec authority: .swarm/specs/2026-05-22-intention-first-baseline.md § AC-7
#
# "with llama" is a pre-Draft validation failure: the vendor is not in the
# supported set. This is a parse-error path, NOT one of the five reachability
# fixtures. It asserts a loud error exit and no spec written.
# It does NOT assert Step 0 runs — Step 0 is intentionally not reached on
# rejected invocations (outside AC-7's reachability claim).
# harness-note: specs_dir_delta: 0 means the parse error prevents any file creation.

```yaml
invocation: { skill: design-spec, args: "with llama" }

# ── Layer 1 (deterministic) ──────────────────────────────────────────────
# Asserts loud error exit (required-phrase) and no spec written (specs_dir_delta: 0).
# Does NOT assert Step 0 runs.
required-phrases:
  # the EXACT loud-error text from design-spec/SKILL.md § Argument parsing —
  # proves the run failed loudly (not merely that the token appeared):
  - "unknown vendor in `with` modifier — expected `codex` or `cc`"

expected-artifacts:
  specs_dir_delta: 0   # no .md created under $SPECS_DIR

# harness-wide guard (implicit per spec § Interfaces "Harness-wide
# premature-hand-off invariant"): this fixture is NOT aim-handoff.
forbidden-substrings:
  - "Sharpened the Foundation aim into testable acceptance criteria — confirm or edit."
forbidden-mode: literal
```
