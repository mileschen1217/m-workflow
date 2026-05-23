# Fixture: happy-spec — AC-2 (Elicitation happy path, design spec) + AC-5 (no within-doc duplication)
# Harness contract: skills/<skill>/tests/step0-fixtures/ two-layer schema
# Spec authority: .swarm/specs/2026-05-22-intention-first-baseline.md § AC-2, AC-5

```yaml
invocation: { skill: design-spec, args: "" }

# ── Layer 1 ──────────────────────────────────────────────────────────────
required-phrases:
  - "Please describe the intended work in your own words."   # b1 from-scratch opener (full exact emit)
  - "Intention (why):"
  - "Aim:"
  - "Out of scope:"
  - "Please confirm or edit this foundation."   # exact Step-0 confirm

forbidden-substrings:
  - "Parent epic uses legacy Intention format"  # b1 (no parent epic): the
                                                # AC-14 legacy note must NOT
                                                # fire on the no-epic path
  # harness-wide guard (implicit per spec § Interfaces "Harness-wide
  # premature-hand-off invariant"): this fixture is NOT aim-handoff.
  - "Sharpened the Foundation aim into testable acceptance criteria — confirm or edit."
forbidden-mode: literal

# (legacy four-question-string absence is AC-6's grep gate, not re-asserted.)
expected-foundation:
  intention: "<fixture-fixed>"
  aim: "<fixture-fixed>"
  out-of-scope: ["<fixture-fixed route>"]

# AC-5 — no within-document foundation duplication (spec § AC-5)
expected-artifacts:
  specs_dir_delta: 1
  files:
    - path: "*.md"                 # the produced spec under $SPECS_DIR
      section: "## Scope"
      # impl-level lines only, fixed verbatim; NON-framing label (no "In scope:")
      exact: |
        **Touched files/modules:**
        - skills/design-spec/template.md
      not-contains: ["In scope:", "Non-goals:"]   # legacy framing labels
    - path: "*.md"
      section: "## Foundation"
      contains: ["**Out of scope:**"]   # boundary routes live ONLY here
      awk-shape: out-of-scope-subbullets # AC-11 awk: 1-3 children, none nested

# ── Layer 2 ──────────────────────────────────────────────────────────────
runs: 5
min-pass: 4
rubric:
  - "Before synthesising, did the agent ask ≥1 clarifying question?
     (Y=pass | N=fail)"
  - "Did the agent present the draft for confirmation before writing it?
     (Y=pass | N=fail)"
```
