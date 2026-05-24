# m-workflow

A Claude Code plugin that bundles 10 workflow-stage skills (design-spec, design-review, arch-review, arch-discovery, epic-driven-roadmap, code-review, test-quality-audit, cross-provider-reviewer, cross-provider-architect, init) and one opinionated discipline (`source-as-truth`) that the skills load at runtime.

## Status

`experimental-MVP`. Used by the author on one project across ~30 sessions. Cross-project portability is unverified.

## What it does

After `/m-workflow:init`, each stage skill reads a per-project adopter config at `<project>/.claude/m-workflow.yaml` to learn paths (`specs_dir`, `adr_dir`, `epics_dir`, `plans_dir`, `archive_specs_dir`) and which disciplines are adopted. If `adopted_disciplines` contains `source-as-truth`, the supporting review-stage skills also load the bundled `CONTEXT.md` so the discipline's audit rules are present in the model's review context.

The skills cover stages 2–7 of an explore → grill → arch consult → spec → plan → build → review workflow. Stages 1 (explore), 1.5 (grill), and 5 (build) are out of scope; see [Companion skills](#companion-skills).

## What it does *not* do

- It does not enforce discipline at CI / commit time. All audits and `kill-on:` lifecycle gates are advisory, included in the model's prompt when a skill is invoked.
- It does not synchronise discipline content across projects. The bundled `CONTEXT.md` lives in the plugin; project-local content (specs / ADRs / epics) lives in the project repo. There is no cross-project sync mechanism.
- It does not replace `CLAUDE.md` or ADRs. It assumes both already exist and reads them at runtime.
- It does not guarantee determinism. Skills are prompt templates; the host model decides the output. Two sessions on different models may produce different review depth or spec phrasing.

## Known limitations

Hard constraints, not preference mismatches:

- **N=1 validation.** The discipline and skill set are exercised on one project. Failure modes when adopted in a different project (different language, monorepo, different conventions) are unknown.
- **No enforcement layer.** P1/P2/P3 audits and `kill-on:` lifecycle are loaded as instructions into the model's prompt. Nothing fails the build if a bridge doc has no `kill-on:`, if `kill-on:` references a completed lever, or if prose duplicates source. Drift is *surfaced* by audits when the skill is invoked — not prevented.
- **Voluntary lifecycle.** Bridge-doc retirement requires running `/m-workflow:epic-driven-roadmap` at epic close. If skipped, stale bridges accumulate without warning.
- **No observability.** There is no drift score, no count of stale bridges, no audit-report artifact. A reader cannot tell from outside whether the discipline is being applied.
- **No idempotence across sessions.** Re-running `/m-workflow:design-spec` on the same feature with the same input may produce different specs. Skills are prompt templates, not deterministic logic.
- **No team governance.** Adopter config is project-level, not contributor-level. No mechanism for resolving disagreement between contributors on adopted disciplines.
- **No exit story.** If a project adopts `source-as-truth` and later wants to drop it, the bridge `kill-on:` annotations remain in markdown without tooling to migrate or strip them.
- **Dependency surface.** Requires `everything-claude-code` for core review agents. Optional Codex dispatch adds another dependency for parallel review. No version-compatibility matrix is published.
- **No security model.** Plugin dispatches agents and runs bash. Prompt-injection from bridge docs, untrusted-repo risk, and third-party plugin behaviour are not addressed. Use in trusted contexts only — see [Install](#install) for warning.

## The bundled discipline: source-as-truth

`source-as-truth` is one workflow stance bundled with the plugin. Its three principles (loaded from `CONTEXT.md` into supporting stage skills' prompt context):

| Principle | Rule |
|---|---|
| **P1 (non-duplication)** | If source encodes the claim, do not write prose. Delete duplicates or point at source. |
| **P2 (falsifiable)** | Every doc claim must be checkable — test, probe, grep. Hedge words (*usually / typically / careful / should*) fail. |
| **P3 (no single host)** | If it fits in a `///` on one symbol → put it there. If it fits in a `// BRIDGE` on one function → there. Only when it spans files / languages / negative space does it earn an `.md`. |

Bridge `.md` docs carry a `kill-on:` field declaring the lever that should retire them. Retirement is voluntary, applied at epic-close audit.

The stance is not novel — it blends established positions (code-first development, docs-as-code, executable specifications, ADR drift hygiene). What this plugin contributes is the operational mechanic: bridge-doc `kill-on:` lifecycle + skill-driven audit prompts + adopter-config opt-in. The contribution is the packaging, not the philosophy.

## Scenarios where this might be relevant

Each scenario names a situation, the mechanic the plugin provides, and the manual work the user still has to do. No claim is made about long-term outcomes — those depend on consistent invocation, model behaviour, and the team's follow-through.

### Scenario 1 — Design specs that name their retirement levers

Situation: drafting a design spec for a feature that will leave at least one bridge-grade `.md` in the repo.

Mechanic: when `source-as-truth` is adopted, the spec template emitted by `/m-workflow:design-spec` includes a § "Source-level Deposit" block with required fields — the lever this feature advances, bridge docs created (each with a `kill-on:` value), bridge docs the feature retires.

Manual work: the author fills the fields. Nothing blocks the spec if fields are empty; the prompt asks but does not refuse. To find all pending `kill-on:` entries later, the user runs `rg '^kill-on:' <specs_dir> <adr_dir>` — there is no built-in index command.

### Scenario 2 — Triaging accumulated docs in a mature repo

Situation: a long-lived repo with documentation scattered across wiki, READMEs, comments, and ADRs of varying age.

Mechanic: source-as-truth defines a four-kind vocabulary (navigation / bridge / workflow / diagnostic) with a frontmatter `kind:` field per doc. `/m-workflow:epic-driven-roadmap` Stage 7 (doc reckoning) prompts the model, at epic close, to classify recent docs against the four kinds and flag candidates for archival or retirement.

Manual work: someone reads the flagged candidates and decides. Cleanup edits, archival, and `kill-on:` updates are by hand. The plugin makes the failure mode "wiki abandoned, nobody reads" *visible*; it does not act on it.

### Scenario 3 — Reducing the doc surface AI agents ingest in later sessions

Situation: each new AI coding session reads `CLAUDE.md`, ADRs, and bridge docs to bootstrap context. Stale claims in those docs get ingested as truth.

Mechanic: `/m-workflow:design-review` and `/m-workflow:code-review` include the P1/P2/P3 audit rules in the model's review context. Duplicative or unfalsifiable prose is flagged at authoring/review time. Bridge docs whose `kill-on:` levers have landed get surfaced at epic close.

Manual work: the team decides whether to retire flagged docs, edit them, or override the audit. No measurement is provided; a reader cannot quantify the effect on the next session's context. The doc set agents read is whatever audit work the team has actually completed.

## Pre-requisites

### Required

| Dependency | Provides | Note |
|---|---|---|
| Claude Code | Host runtime | Plugin host |
| `everything-claude-code` plugin | `architect`, `code-reviewer` agents | Dispatched by `design-spec` / `arch-review` / `code-review` |

```bash
claude plugin marketplace add anthropics/everything-claude-code
claude plugin install everything-claude-code --scope user
```

### Optional

| Dependency | Provides | If absent |
|---|---|---|
| Codex CLI | `codex` agents | `cross-provider-*` falls back to CC-only; everything else works |

### Companion skills

For the full pipeline (explore → grill → arch → spec → plan → build → review), the upstream / downstream stages are external:

| Companion | Provides | Stage |
|---|---|---|
| `superpowers` plugin | `writing-plans`, `subagent-driven-development`, `brainstorming` | Plan + build |
| `/grill-with-docs` skill | Vocabulary sharpening before spec authoring | Stage 1.5 |

m-workflow runs without companions; the handoffs from `design-spec` to plan / build just won't have an obvious next step.

## Install

> ⚠️ **Trust boundary**: The plugin dispatches agents and runs bash. Stage skills read project docs into the model's prompt, so untrusted markdown can carry prompt-injection. Install in repos and contexts you trust.

```bash
git clone https://github.com/mileschen1217/m-workflow ~/projects/m-workflow
claude plugin marketplace add ~/projects/m-workflow
claude plugin install m-workflow@m-workflow-dev --scope user
```

## Use

```
/m-workflow:init
# → writes <project>/.claude/m-workflow.yaml
# → prompts: adopt source-as-truth? [Y/n]

/m-workflow:design-spec my-feature
# → drafts <specs_dir>/YYYY-MM-DD-my-feature-design.md
# → dispatches everything-claude-code:architect for fresh-context review
```

Without `<project>/.claude/m-workflow.yaml`: every stage skill runs in default mode, printing a one-line hint to run `/m-workflow:init`. Defaults: `specs_dir=.swarm/specs`, `adr_dir=.swarm/docs/adr`, `epics_dir=.swarm/epics`, `plans_dir=.swarm/plans`, `archive_specs_dir=.swarm/archive/specs`. Skills do not refuse to run.

## Skills

| Slash command | What it does |
|---|---|
| `/m-workflow:init` | Per-project setup. Writes yaml. Idempotent without `--reset`. |
| `/m-workflow:design-spec <feature>` | Draft an ATDD+TDD-aligned spec. Routes through `architect` for fresh review. |
| `/m-workflow:design-review <path>` | Composite review (CC + Codex parallel) of a spec / plan / ADR / discovery doc. Includes bridge-content audit rules when source-as-truth is adopted. |
| `/m-workflow:arch-review` | Pre-spec architecture consult when 2+ viable approaches exist. |
| `/m-workflow:arch-discovery` | E2E system discovery — invariants × layers × flows × failures matrix. |
| `/m-workflow:epic-driven-roadmap` | Scaffold / close / audit epics. Includes Stage 7 doc reckoning when source-as-truth is adopted. |
| `/m-workflow:code-review` | Per-commit or `batch` (per-feature) code review. |
| `/m-workflow:test-quality-audit` | Audit test suite quality + coverage gaps. |
| `/m-workflow:cross-provider-reviewer` | Composite primitive: parallel review across CC + Codex with divergence labelling. |
| `/m-workflow:cross-provider-architect` | Composite primitive: parallel architect across CC + Codex. |

## When to consider this plugin

- You are already on Claude Code, use it as a primary IDE/orchestrator, and want a prebuilt skill set covering spec / review / epic stages rather than authoring your own.
- You're comfortable with advisory audits whose enforcement is at most "the model is told to check". CI / linter enforcement is not provided.
- You're a solo developer or small team. No team-governance mechanism exists.

## When not to consider it

- You need deterministic enforcement (CI failures, commit hooks). This plugin does not provide that.
- You need narrative-first artifacts for non-engineering stakeholders. `source-as-truth` assumes readers read source.
- You are evaluating against `agent-os`, `claude-flow`, `BMAD`, or `superpowers` and want a head-to-head comparison. The author has not yet produced one. See `docs/comparisons.md` for first-pass research notes; treat them as drafts.

## License

MIT
