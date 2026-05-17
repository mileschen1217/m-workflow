---
name: design-spec
kind: workflow
description: |
  Generate a design spec for a non-trivial feature. Produces a structured spec
  document at the project's configured specs directory. Required trigger: the
  feature touches 3+ files across 2+ modules, OR introduces a new contract
  (API / CLI / IPC / skill). Smaller features skip this step and go straight to
  plan or implementation. On first invocation in a project, runs setup to record
  the specs directory. Always dispatches the `architect` agent for fresh-context
  review of the draft.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Agent
  - Skill
---

# m-design-spec

Produce an ATDD + TDD double-loop-aligned design spec for a feature, review it
in fresh context via the `architect` agent, and write the final draft to the
project's specs directory.

## When to Invoke

Required when any of these is true:
- Feature touches 3+ files across 2+ modules
- Introduces a new contract: public API, CLI command, IPC message format,
  Claude Code skill, or agent
- The user explicitly requests a design spec

Skip when:
- Feature is a single-file patch or bug fix
- Touches one module, preserves existing contracts
- Follows a pattern already specified elsewhere in the codebase

Naturally chained with exploration (Topic 2 routing) on the input side and
`/superpowers:writing-plans` on the output side:

```
Explore → /m-design-spec → /superpowers:writing-plans → Build (ATDD+TDD)
```

## Step 0 — Load vocabulary

Read `${CLAUDE_PROJECT_DIR}/.claude/m-workflow.yaml` if it exists. Check `adopted_disciplines`.

If contains `source-as-truth`:
  Read `${CLAUDE_PLUGIN_ROOT}/CONTEXT.md § "Bridge content gate"` — load text into context.

When dispatching to `m-workflow:cross-provider-architect` (Step N below), include in task envelope:

```json
{
  "task": "<existing task>",
  "system_prompt": "<existing system_prompt + loaded CONTEXT.md vocabulary verbatim>",
  "discipline_mode": "source-as-truth",
  "source_as_truth_vocab": "<loaded CONTEXT.md section text>",
  "role": "architect"
}
```

If `source-as-truth` is NOT adopted (yaml absent OR `adopted_disciplines` lacks it):
  Skip the CONTEXT.md Read. When dispatching, set:

```json
{
  "task": "<existing task>",
  "system_prompt": "<existing>",
  "discipline_mode": "none",
  "role": "architect"
}
```

(Omit `source_as_truth_vocab` field entirely; do not pass empty string.)

## Setup Mode

Triggered when `.claude/design-spec.yaml` does not exist in the current project.

### Interactive flow

1. Ask: "Where should design specs live in this project?"
   - Default: `docs/specs/`
   - Validate: directory can be created or already exists under the project root
2. Write `.claude/design-spec.yaml`:
   ```yaml
   specs_dir: docs/specs
   template: ~/.claude/skills/m-design-spec/template.md
   ```
3. Create `specs_dir` if missing
4. Confirm setup complete, proceed to Draft Mode

### Design decisions

- One question, not a wall — only the specs directory needs configuration
- Project-local config, not global — each project can use its own convention
- Template path stays defaulted to the skill's own copy; project can override
  if they need a custom template

## Draft Mode

Triggered when `.claude/design-spec.yaml` exists.

### Step 0 — Intention-alignment gate (mandatory)

Before collecting inputs or reading any file, run the gate from global CLAUDE.md § Working Style. Surface the four answers to the user and **wait for confirmation** before proceeding to inputs/drafting:

1. **Goal in observable terms** — what does success look like to the user / system / test runner?
2. **In scope vs. explicitly out of scope** — name 1-3 things this spec will NOT touch even if related.
3. **Fix the system, or work around it?** — if a fixture, config knob, or external workaround can achieve the goal, name that path. If proposing production-code change anyway, justify why the workaround is unacceptable.
4. **Smallest change that achieves the goal** — what's the diff size at minimum, and what would expand it?

If the parent epic already filled an `## Intention` block (per `m-epic-driven-roadmap`), restate the four answers verbatim from that block and ask "still accurate?" rather than re-interrogating from scratch.

The four answers go into the spec under a `## Intention` section placed immediately above `## Problem`. Skip the rest of Draft Mode if the user reframes during the gate (e.g. "this should be a fixture, not a spec"); the gate's job is to catch wrong scope before any drafting cost.

### Inputs to collect

If not provided in the invocation:
1. **Feature name** (kebab-case, used in filename)
2. **Goal statement** (one paragraph — what is this feature solving?)
3. **Exploration references** — one or more of:
   - File paths to research notes (e.g., `ai_explosion_kb/Inbox/<note>.md`)
   - Inline summary of prior exploration
   - "None — design from problem statement"

### Drafting workflow

1. **Read** the template from the path in the config (default: skill's own
   `template.md`)
2. **Read** all exploration references provided
3. **Draft** each template section. Follow the template's section order and
   guidance. Do not skip Intention, Acceptance Criteria, Error Handling, or
   Invariants — Intention locks scope; the other three feed the ATDD+TDD
   double loop. All four are mandatory.

### Line-width policy (mandatory)

- **Prose:** soft-wrap only. One logical paragraph = one line. Do NOT insert
  hard line breaks inside a paragraph. Markdown renderers reflow soft-wrapped
  prose to fit any window width; hard-wrapped prose stays cramped on wide
  screens.
- **Code blocks, tables, ASCII/Mermaid diagrams:** keep ≤80 chars where
  natural. These cannot reflow, so narrow widths avoid horizontal scroll.
- **Lists:** one bullet per line; wrap continuation lines under their bullet
  only if the bullet itself is multi-paragraph — otherwise keep each bullet
  on one line.

Rationale: specs are read in GitHub, editors, and web renderers that all
reflow Markdown. Hard-wrapping prose at 80 chars (a terminal convention)
breaks that reflow and makes specs hard to read on modern monitors.
4. **Write** the initial draft to:
   ```
   <specs_dir>/YYYY-MM-DD-<feature-name>-design.md
   ```
   with `Status: Draft` in the header.
5. **Dispatch** the architect (see below). **Skip this step entirely if `quick = true`** — write the draft and stop after step 4.
6. **Apply** architect feedback. For high-signal feedback, integrate directly.
   For judgment calls, add a `## Open Questions` entry noting the conflict and
   continue.
7. **Rewrite** the spec with architect integration. Keep `Status: Draft` until
   the user explicitly accepts — the skill does not auto-promote status.

### Architect dispatch (default: Pattern A composite — fresh context)

Resolve the dispatch target:
- `force_architect = cc` → dispatch `everything-claude-code:architect` directly with `model: "sonnet"` (single agent, fresh context — model override supersedes the agent's `model: opus` frontmatter).
- `force_architect = codex` → dispatch `codex-adversarial-reviewer` directly (single agent, fresh context).
- Default (no override) → dispatch `m-workflow:cross-provider-architect` composite (Pattern A — dual parallel: CC `architect` validates + Codex `codex-adversarial-reviewer` pressure-tests; auto-falls back to CC-only if Codex unavailable):

```
Skill(skill: "m-workflow:cross-provider-architect", args: {
  "task": "<the structural-review prompt below, with the spec path or spec text inlined>",
  "role": "architect",
  "task_dir": "<optional: absolute path>"
})
```

The dispatched skill (`m-workflow:cross-provider-architect`) owns its procedure end-to-end.

Task envelope contents:

> Review the design spec at `<absolute path to spec>`. Check:
> 1. Problem/Scope/Non-goals are concrete and falsifiable
> 2. Acceptance Criteria cover happy path, error paths, and boundaries (ATDD contract)
> 3. Interfaces/Contracts are specific enough for TDD (field names, types, error returns)
> 4. Error Handling rows map 1:1 to unit tests
> 5. Invariants are cross-cutting rules, not restatements of contracts
> 6. Risks/Open Questions are not hidden
>
> Return: structural feedback only (not line edits). Name any missing sections, any vague contracts, any missing error paths. Flag any architectural concerns that should be resolved before implementation planning begins.

Use fresh context — the composite skill orchestrates fresh subagent contexts; backend agents (CC architect, Codex adversarial reviewer) inherit no drafting context.

### Output

- One file at `<specs_dir>/YYYY-MM-DD-<feature-name>-design.md`
- Terminal summary with: spec path, architect-identified issues addressed,
  architect-identified issues surfaced to Open Questions
- Next step: `/superpowers:writing-plans` takes the spec as input for plan
  generation

## Usage

```
/m-design-spec                          # interactive draft (config exists) or setup-then-draft
/m-design-spec setup                    # force re-run setup (overwrites .claude/design-spec.yaml)
/m-design-spec <feature-name>           # skip name prompt
/m-design-spec <feature-name> quick     # skip architect dispatch (draft only — fast iteration)
/m-design-spec <feature-name> with codex   # force Codex-only architect (no parallel CC)
/m-design-spec <feature-name> with cc      # force CC-only architect (no parallel Codex)
```

The `quick` modifier skips Step 5 (architect dispatch) entirely. Useful for early sketches where structural review is premature; the user is expected to re-run without `quick` once the spec stabilizes. `Status: Draft` still applies, and the file is still written to `<specs_dir>/`.

The `with <vendor>` modifier overrides the architect routing — the default Pattern A composite (CC `architect` + Codex `codex-adversarial-reviewer` in parallel) is replaced with a single-vendor dispatch. Recognized vendors: `codex`, `cc`. Unrecognized values fail loudly: "unknown vendor in `with` modifier — expected `codex` or `cc`".

`quick` and `with <vendor>` are mutually exclusive — `quick` skips dispatch entirely, so vendor routing is moot. If both appear, `quick` wins and the `with` modifier is silently ignored.

### Argument parsing

Parse left-to-right:
1. If first token is `setup` → run Setup Mode and exit.
2. Next non-keyword token (not `quick` / `with`) → `feature_name`.
3. If `quick` appears anywhere → `quick = true` (skip architect).
4. If `with <vendor>` appears, set `force_architect = <vendor>`. Validate against {`codex`, `cc`}; fail loudly otherwise.

## Status Lifecycle (intentionally minimal)

Specs are written as `Status: Draft`. Transitions to `Accepted` / `Superseded`
are manual edits when the user approves or replaces a spec. The skill does not
manage lifecycle — when a spec is ready to implement, the human changes the
status and hands off to `/superpowers:writing-plans`.

## Related

- Template: `~/.claude/skills/m-design-spec/template.md` (bundled)
- Exploration routing (upstream): Topic 2 in global CLAUDE.md
- Architecture consult (upstream, conditional): `/m-arch-review` — for
  resolving architectural questions before drafting the spec
- ATDD chain (downstream): `ATDD — spec and test development` in global CLAUDE.md
- Plan generation (downstream): `/superpowers:writing-plans`
- ADR workflow: `~/.claude/skills/m-arch-review/adr-authoring.md`
- Example spec matching the template:
  `docs/superpowers/specs/2026-04-16-m-extract-knowledge-design.md` (Obsidian repo)
