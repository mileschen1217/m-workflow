---
name: cross-provider-reviewer
description: Pattern A composite skill — reviews any artifact using CC `code-reviewer` + Codex `codex-reviewer` in parallel; synthesizes with explicit divergence labeling. Auto-falls back to CC-only when Codex unavailable. Used by `/m-workflow:design-review` (with doc-review `system_prompt` via envelope) and available for ad-hoc cross-provider review.
allowed-tools:
  - Bash
  - Read
  - Write
  - Agent
user-invocable: true
kind: workflow
---

# /m-workflow:cross-provider-reviewer — Pattern A Composite Skill

Skill body executes in main-thread context where `Agent` tool is available. Orchestrates parallel CC + Codex review and synthesizes with divergence labeling.

## Inputs (JSON envelope as `args`)

```json
{
  "task": "<diff, doc, or artifact text>",
  "task_dir": "<optional: absolute path for artifact write>",
  "system_prompt": "<optional: domain-specific reviewer prompt; default = code-review>",
  "role": "reviewer",
  "timeout_seconds": 900
}
```

## Procedure

### 1. Probe Codex

```bash
codex --version >/dev/null 2>&1 && echo "codex_healthy=1" || echo "codex_healthy=0"
```

### 2. Parallel dispatch (single assistant message, two Agent tool calls)

If `codex_healthy=1`, in ONE message issue BOTH:

- `Agent(subagent_type: "everything-claude-code:code-reviewer", description: "CC review", prompt: <task envelope with system_prompt prefix>, model: "sonnet")`  <!-- # EXTERNAL DEP — everything-claude-code (Epic B vendors this) -->

  The `model: "sonnet"` is explicit, not inherited from ECC's default — m-* family routes review through Sonnet by policy.
- `Agent(subagent_type: "m-workflow:codex-reviewer", description: "Codex review", prompt: <task envelope>)`

Wait for both to return before synthesizing.

If `codex_healthy=0`, call only `everything-claude-code:code-reviewer` and proceed to synthesis with `fallback_reason: "codex unavailable"`.

### 3. Synthesis (deterministic)

Sort raw inputs by provider name (`cc` then `codex`).

Merge findings:
- Same file:line + same category → keep one, attribute to both.
- Disagreement on severity → list both verdicts inline; keep higher severity.
- Unique to one provider → include with attribution.

Always emit a `## Divergence` section when verdicts disagree. Never silently merge.

### 4. Compute provenance, prepend banners, write artifacts

All field definitions, the correctness operations, the banner formats/ordering, and
the no-derived-fields rule live SOLELY in `references/provenance.md`. This body gives
only the ACTIONS; it restates none of those definitions.

1. Record `providers_expected` and `providers_used` for THIS invocation per
   provenance.md. `builder_vendor` is null (Pattern A has no builder).
2. Extract `session_id` from `<task_dir>/raw_codex.jsonl` per provenance.md.
3. Determine degraded/partial and, if either holds, build and prepend the banner(s)
   to the synthesis text AND to `review.md` (then a blank line, then the review body),
   per provenance.md.

Write artifacts (if `task_dir` provided):
- `<task_dir>/raw_cc.md` — CC reviewer output verbatim
- `<task_dir>/raw_codex.jsonl` — Codex reviewer output (raw JSONL)
- `<task_dir>/review.md` — synthesized review (banner-prepended when degraded/partial)
- `<task_dir>/review.result.json` — the review-envelope/v1 artifact, written per
  `references/provenance.md` (sole definition of its fields and the no-derived-fields rule).

### 5. Return synthesized review

Skill body's final assistant text: the synthesized review.md content. The orchestrator caller reads it from shared LLM working memory.

## Synthesis instruction (built-in)

> Merge findings; do not introduce new findings. Preserve provider attribution. Label divergence explicitly. Sort by severity (Critical, High, Medium, Low). Emit raw outputs alongside; never silently merge.

## Failure semantics

- Codex probe / dispatch fail → CC-only synthesis; record provenance + prepend the banner if applicable, per `references/provenance.md`.
- Both reviewers fail → no synthesis; surface as failure and record provenance per `references/provenance.md`.
- Skill itself errors (framework) → propagate to caller.

## Cost note

Pattern A — ~2× tokens per invocation. Only invoked at high-leverage gates: doc review (`/m-workflow:design-review`), arch consult (`/m-workflow:arch-review`), design spec (`/m-workflow:design-spec`), or ad-hoc opt-in for high-risk diffs.

## Dependencies

- `everything-claude-code:code-reviewer` (ECC, EXTERNAL) — CC review backend. Epic B vendors or makes optional.
- `m-workflow:codex-reviewer` (plugin-local) — Codex review backend.
- CC-only fallback: if a provider is absent, run the available provider(s), write `review.result.json` with the resulting `providers_used` / `fallback_reason`, and prepend the DEGRADED banner per `references/provenance.md`; if BOTH absent → no synthesis, surfaced as failure (envelope still written per provenance.md).
