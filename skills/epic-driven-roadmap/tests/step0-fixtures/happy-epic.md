# Fixture: happy-epic — AC-1 (Elicitation happy path, epic scaffold)
# Harness contract: skills/<skill>/tests/step0-fixtures/ two-layer schema
# Spec authority: .swarm/specs/2026-05-22-intention-first-baseline.md § AC-1

```yaml
invocation: { skill: epic-driven-roadmap, args: "" }

# ── Layer 1 (deterministic) ──────────────────────────────────────────────
required-phrases:
  - "Please describe the intended work in your own words."   # from-scratch opener (full exact emit)
  - "Intention (why):"       # draft block field headings (exact)
  - "Aim:"
  - "Out of scope:"
  - "Please confirm or edit this foundation."   # exact Step-0 confirm
                                                # prompt (full phrase
                                                # disambiguates from the
                                                # AC-13 hand-off phrase,
                                                # which also contains
                                                # "confirm or edit")

# (no forbidden-substrings here — the AC-6 grep gate guarantees the four
#  shipped artifacts carry no legacy strings; this happy-path fixture does
#  not re-assert it.)

# harness-wide guard (implicit per spec § Interfaces "Harness-wide
# premature-hand-off invariant"): this fixture is NOT aim-handoff, so it
# must not contain the AC-13 hand-off phrase.
forbidden-substrings:
  - "Sharpened the Foundation aim into testable acceptance criteria — confirm or edit."
forbidden-mode: literal

expected-foundation:
  intention: "<fixture-fixed>"
  aim: "<fixture-fixed>"
  out-of-scope: ["<fixture-fixed route>"]

expected-artifacts:
  files:
    - path: "<epic dir>/index.md"
      section: "## Foundation"
      awk-shape: out-of-scope-subbullets   # AC-11 awk: 1-3 children, none nested

# ── Layer 2 (rubric over runs) ──────────────────────────────────────────
runs: 5
min-pass: 4
rubric:
  - "Before synthesising the draft, did the agent ask ≥1 clarifying
     question about intention/aim/out-of-scope? (Y=pass | N=fail)"
  - "Did the agent present the draft foundation for the user to confirm
     or edit before recording it? (Y=pass | N=fail)"
```
