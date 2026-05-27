# Fixture: vague-aim — AC-8 (Synthesised aim must not carry a vague token)
# Harness contract: skills/<skill>/tests/step0-fixtures/ two-layer schema
# Spec authority: intention-first epic § AC-8
#
# Table-driven via `cases` (7 entries). Each case: user-stated vague aim, the
# fixed observable rewrite to confirm, and the token that must be absent FROM
# THE SYNTHESISED AIM (aim-scoped, not transcript-wide).
# MERGE RULE: top-level required-phrases and forbidden-substrings are ADDITIVE
# — they apply to every case; case entries append their own.

```yaml
invocation: { skill: design-spec, args: "" }

# ── Layer 1 top-level guards (apply to ALL cases) ─────────────────────────
# NOTE (pass@5 finding): the re-prompt was formerly asserted here as the
# EXACT Layer-1 phrase "what would you observe when this is done?". Faithful
# pass@5 showed that exact phrase is UNRELIABLE across tokens (should/better
# 5/5, but usually 0/5, typically/elegant ~2/5): agents correctly decline the
# vague aim but ask richer, varied clarifying questions instead of the rote
# phrase. Per ADR-0005 a process property belongs in Layer 2 — so the
# re-prompt is now a Layer-2 rubric (below), not a Layer-1 substring.

forbidden-substrings:
  - "(aim contains a vague token — accept anyway?)"  # normal path resolves
                                                     # WITHOUT the AC-8b
                                                     # override warning;
                                                     # closes the AC-8/AC-8b
                                                     # boundary at Layer 1
  # harness-wide guard (implicit per spec § Interfaces "Harness-wide
  # premature-hand-off invariant"): this fixture is NOT aim-handoff.
  - "Sharpened the Foundation aim into testable acceptance criteria — confirm or edit."
forbidden-mode: literal

# ── Cases (7 entries, verbatim from spec § AC-8) ─────────────────────────
cases:   # each: the user-stated vague aim, the fixed observable rewrite to
         # confirm, and the token that must be absent FROM THE SYNTHESISED
         # AIM (aim-scoped, not transcript-wide).
  - user-aim: "the parser should be fast"
    expected-foundation: { aim: "the parser returns in <50ms at p95", aim-not-contains: ["should"] }
  - user-aim: "queries usually return quickly"
    expected-foundation: { aim: "queries return in <200ms at p95", aim-not-contains: ["usually"] }
  - user-aim: "the API typically responds 200"
    expected-foundation: { aim: "the API responds 200 for valid input", aim-not-contains: ["typically"] }
  - user-aim: "make the code elegant"
    expected-foundation: { aim: "no function exceeds 40 lines", aim-not-contains: ["elegant"] }
  - user-aim: "handle the complex cases"
    expected-foundation: { aim: "all 5 enumerated edge cases pass tests", aim-not-contains: ["complex"] }
  - user-aim: "be careful with migrations"
    expected-foundation: { aim: "migrations run idempotently (re-run = no-op)", aim-not-contains: ["careful"] }
  - user-aim: "make search better"
    expected-foundation: { aim: "search recall@10 ≥ 0.9 on the eval set", aim-not-contains: ["better"] }

# ── Layer 2 (rubric over runs) — the re-prompt is a PROCESS property ──────
runs: 5
min-pass: 4
rubric:
  - "When the user's stated aim contained a vague token, did the agent
     DECLINE to synthesise it as-is and instead ask the user for an
     observable / measurable formulation before proceeding? (Y=pass | N=fail)"
  - "Did the agent avoid recording the vague token in the final synthesised
     aim (the confirmed aim is observable, not the vague phrasing)?
     (Y=pass | N=fail)"
```
