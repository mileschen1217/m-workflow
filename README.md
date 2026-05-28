# touchstone

> A test of what is genuine. (試金石 — a stone used to test the authenticity of metal.)

A Claude Code plugin for **workflow discipline** — 11 stage skills + 5 agents, organised around the **honesty spine**: *claim ≤ evidence*. Gaps are marked, not hidden.

## What it is

Touchstone bundles a 6-stage workflow (Explore → Grill → Arch-Review → Design-Spec → Plan → Build → Review Gate) with mechanisms that hold every stage to the honesty spine. The plugin's spine is **`claim ≤ evidence`** — every artifact (spec, plan, commit, review) carries the evidence its claims rest on; missing evidence is marked `[假設]`/`[unverified]`, never papered over.

The spine is carried *through* four roles (not enforced by a fifth):

- **Skill** — drafting / authoring (`design-spec`, `arch-review`, `code-review`, ...)
- **Mode** — narration discipline (`grounded-claims` — cite source, mark assumptions)
- **Discipline** — domain stance (`source-as-truth` — code is authoritative; docs describe why)
- **Baseline** — universal foundations (`intention-first` — name intent before mechanism)

## Install

```bash
git clone https://github.com/mileschen1217/touchstone ~/projects/touchstone
claude plugin marketplace add ~/projects/touchstone
claude plugin install touchstone@touchstone --scope user
```

⚠️ Plugin dispatches agents and runs bash; use in trusted contexts only.

## Dependencies

Touchstone delegates work to agents and skills that live in other plugins. Install these before running touchstone skills.

**Required:**

```bash
# everything-claude-code — architect agent + language-specific reviewers
claude plugin marketplace add https://github.com/your-org/everything-claude-code   # check upstream URL
claude plugin install everything-claude-code@everything-claude-code --scope user

# superpowers — writing-plans, using-git-worktrees, brainstorming, etc.
claude plugin install superpowers@claude-plugins-official --scope user
```

**Optional (cross-vendor review path):**

```bash
# codex — cross-vendor agents (codex:rescue, codex-* reviewers/implementers)
claude plugin install codex@openai-codex --scope user
```

Without `everything-claude-code`, the language-specific code reviewers and the `architect` agent dispatched by `cross-provider-architect` are unavailable. Without `codex`, only single-vendor (Claude-only) review paths work — touchstone degrades gracefully but loses the parallel CC+Codex composite.

## Skills

- `touchstone:init` — Bootstrap project adoption with `.claude/touchstone.yaml`.
- `touchstone:arch-discovery` — Architecture discovery matrix for new systems.
- `touchstone:arch-review` — Pressure-test design tradeoffs before spec.
- `touchstone:design-spec` — Author spec: Problem → Scope → AC (GWT) → Architecture → Interfaces.
- `touchstone:design-review` — Gate spec/plan/ADR before Build (Pattern A).
- `touchstone:code-review` — Per-commit + per-batch code review (Patterns C / B).
- `touchstone:epic-driven-roadmap` — Pure-tracker ROADMAP + per-epic index convention.
- `touchstone:grounded-claims` — Narration mode: cite source, mark `[假設]`.
- `touchstone:test-quality-audit` — Audit test suite against quality heuristics.
- `touchstone:cross-provider-architect` — Parallel CC + Codex architecture review.
- `touchstone:cross-provider-reviewer` — Parallel CC + Codex code review composite.

## Agents

- `touchstone:tdd` — Double-loop TDD agent (ATDD outer + unit-test inner).
- `touchstone:codex-implementer` — Cross-vendor task execution via Codex CLI.
- `touchstone:codex-tdd` — Cross-vendor TDD with Codex red-green-refactor.
- `touchstone:codex-reviewer` — Read-only Codex code review (Pattern B).
- `touchstone:codex-adversarial-reviewer` — Codex adversarial design critique.

## 6-stage workflow

The full workflow lives in your global `~/.claude/CLAUDE.md` (touchstone integrates as routing). See `docs/comparisons.md` for scope and `CONTEXT.md` for vocabulary.

## Status

`0.2.0`. Experimental. Used by the author on one project across ~30 sessions. Cross-project portability is unverified — see `docs/comparisons.md` for scope boundaries.

## License

MIT. See [LICENSE](LICENSE).
