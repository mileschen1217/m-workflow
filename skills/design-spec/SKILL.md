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

Read `${CLAUDE_PROJECT_DIR}/.claude/m-workflow.yaml`.

**If yaml absent** (file not found):
  Print one line: `ℹ️  No .claude/m-workflow.yaml — using default paths. Run /m-workflow:init to configure.`
  Use hardcoded defaults for all path lookups in this invocation: `specs_dir=.swarm/specs`, `adr_dir=.swarm/docs/adr`, `epics_dir=.swarm/epics`, `plans_dir=.swarm/plans`, `archive_specs_dir=.swarm/archive/specs`.
  Treat `adopted_disciplines` as empty. Do not refuse; continue to drafting. Skip the CONTEXT.md Read below; in dispatch envelope omit `source_as_truth_vocab` and set `discipline_mode: "none"`.

**If yaml present:** check `adopted_disciplines`.

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

### Step 0 — Foundation elicitation (Baseline — always runs)

Before collecting design inputs or reading implementation source files,
locate and read the parent epic index if one is in context, then run the
elicitation gate.

Reuse check FIRST (AC-10): if a foundation was already confirmed earlier in
THIS SAME skill invocation, do NOT re-elicit. Emit this EXACT log line
verbatim (fixed emit string — do not paraphrase, do not reword):
"Foundation already confirmed this session — reusing"
then reuse the confirmed foundation and skip to step g. Do NOT emit the
from-scratch opener. Reuse is same-invocation only; a FRESH invocation
whose parent epic already has a `## Foundation` takes branch a
(inheritance), NOT reuse. Otherwise:

a. If the parent epic index has a populated ## Foundation section:
   Pre-fill the sharpening with the epic's foundation. Restate the
   epic's intention / aim / out-of-scope, then ask with this EXACT phrase
   verbatim (fixed emit string — do not paraphrase, do not substitute your
   own questions):
   "Does this spec's scope differ? If so, sharpen each field for this phase."
   Do NOT re-elicit from scratch and do NOT emit the from-scratch opener.

b. No populated `## Foundation` to inherit — two sub-cases, both run FULL
   elicitation (no pre-fill, and never the inheritance prompt "Does this
   spec's scope differ?"):

   b1. No parent epic at all (`parent_epic.foundation: absent`):
       Open with this EXACT phrase (fixed emit string):
       "Please describe the intended work in your own words." Do NOT emit
       the legacy note (there is no legacy epic to flag).

   b2. Parent epic exists but uses the legacy `## Intention` format, not
       `## Foundation` (`parent_epic.foundation: legacy-intention`):
       FIRST emit this EXACT note:
       "Parent epic uses legacy Intention format — consider updating it."
       THEN open with the same EXACT phrase
       "Please describe the intended work in your own words."

   The substring "describe the intended work in your own words" is what
   AC-7's bypass fixtures match (Step-0 reached) and what AC-4 forbids as
   the from-scratch opener — keep it verbatim, do not paraphrase. The
   legacy note fires in b2 ONLY (AC-14); it must be absent in b1.

c. Engage in a SHORT sharpening exchange. Ask only questions in the
   ALLOWED column of the boundary table (§ Interfaces — Step-0
   question boundary). Stop once intention / aim / out-of-scope are
   crisp. Do NOT slide into:
   - Requirements or design exploration (→ brainstorming, Stage 1)
   - Domain-vocabulary grilling (→ grill-with-docs, Stage 1.5)
   - Any FORBIDDEN-column topic (architecture, files, dependencies,
     tests, API shape, effort, rollout, or fix strategy)
   If the user prods toward design, deflect with ONLY this generic phrase —
   "that's a design decision for a later stage" — and return to the three
   fields. Do NOT name or restate the specific design topic the user raised
   (do not echo words like "endpoint", "migration path", "rollout", "which
   package", etc.); naming it both engages the design and would trip the
   AC-3 shallow-boundary check. Keep the deflection topic-free.

d. Synthesise a draft foundation and present it using these EXACT field
   labels (verbatim — AC-2 matches them case-sensitively): "Intention
   (why):", "Aim:", "Out of scope:". Apply the SYNTHESISED-aim vague-token
   rule: the synthesised aim must not contain a vague token {usually,
   typically, should, elegant, complex, careful, better}; if it would,
   re-prompt for an OBSERVABLE formulation — ask what the user would
   observe or measure when done (targeted clarifying questions are fine;
   "what would you observe when this is done?" is a good default). Do not
   synthesise until the aim is observable. (AC-8.) Out-of-scope sentinel rule: if the user declines to
   name any out-of-scope route after one re-prompt, record this EXACT
   sentinel verbatim (fixed string — do not paraphrase) as the out-of-scope
   value: "(no explicit boundary declared)" AND add a matching Risks/Open
   Questions entry.

e. Surface the draft to the user and ask, with this exact phrase:
   "Please confirm or edit this foundation." Do not proceed to input
   collection until confirmed. If the user insists on an aim that contains
   a vague token, warn with this EXACT phrase verbatim (fixed emit string —
   do not paraphrase, do not reword):
   "(aim contains a vague token — accept anyway?)"
   On accept, record the user's aim verbatim AND add this EXACT risk note
   verbatim to Risks/Open Questions (do not paraphrase):
   "(aim contains an unverifiable token — user-confirmed)"

f. If the user reframes during sharpening (e.g. "this should be a
   fixture, not a spec"), STOP. Do not draft a spec and do not write
   any file under specs_dir. Report:
   "Scope reframed to [X] — a design spec is not needed. Exiting Draft Mode."

g. Write the confirmed foundation into the spec under ## Foundation
   (all three fields — the spec has no tracker headline).

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
   guidance. Do not skip Foundation, Acceptance Criteria, Error Handling, or
   Invariants — Foundation locks scope; the other three feed the ATDD+TDD
   double loop. All four are mandatory.

When drafting ## Acceptance Criteria:
- Treat Foundation.aim as a provisional DIRECTION (set shallow at Step 0,
  before any design / feasibility work), not a settled target.
- Derive testable, observable acceptance criteria from it. Where Step 0
  fixed a placeholder value (e.g. a latency or recall threshold), this is
  the stage to pressure-test and adjust that value against what the design
  can actually achieve.
- Surface the result with this exact phrase:
  "Sharpened the Foundation aim into testable acceptance criteria — confirm or edit."
  Present the sharpened aim / criteria and wait for confirmation before
  finalising the AC section.
- The sharpened aim must stay traceable to the Step-0 direction. If the
  design work reveals the original direction was wrong, that is a scope
  signal — surface it, do not quietly substitute a new goal.

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

## Boundary — the Step-5 review is NOT the design-review gate

The architect dispatch in Step 5 is an **author-time, one-shot, non-gating** critique that improves the draft. It is a different thing from `/m-design-review`, the Stage-0 **design-review gate** (the gate that runs before Build). Conflating the two is a recurring mistake — they overlap (both run a cross-provider review of the spec) but differ in cadence, enforcement, and what version they judge:

| | Step-5 review (this skill) | `/m-design-review` (the gate) |
|---|---|---|
| Role | author-time critique, improve the draft | design-review gate, pass/fail before implementation |
| Verdict | `approve\|revise\|block`, advisory — no enforced iterate-to-green | C+H tiered: C+H≥5 → mandatory 2nd pass, **blocks Build until C+H=0** |
| Skippable | yes (`quick`) | no — not on user discretion at C+H≥5 |
| Judges | the freshly-drafted version | the **final, human-accepted** version |

The human-accept step sits **between** them:

```
/m-design-spec            →   Status: Draft   →   human reads / edits / accepts ★   →   /m-design-review (blocking gate)
(draft + Step-5 critique)                          (lifecycle owned by the human)        (C+H gate, blocks Build)
```

Running this skill does **not** discharge `/m-design-review`. The Step-5 critique only *satisfies* the gate when it was iterated to the gate's tiered standard (C+H=0) **and** the spec was not edited afterward; if the human edits the spec during review, re-run `/m-design-review` on the final version. Do not merge the two: the seam is exactly the human-in-the-loop accept step, and a merged action would gate the pre-edit draft, not the accepted artifact.

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
status and hands off to `/superpowers:writing-plans`. The `Draft → human accept`
step is the seam between this skill's Step-5 critique and the `/m-design-review`
gate (see Boundary above) — keep it human-owned.

## Related

- Template: `~/.claude/skills/m-design-spec/template.md` (bundled)
- Exploration routing (upstream): Topic 2 in global CLAUDE.md
- Architecture consult (upstream, conditional): `/m-arch-review` — for
  resolving architectural questions before drafting the spec
- ATDD chain (downstream): `ATDD — spec and test development` in global CLAUDE.md
- design-review gate (downstream, distinct from Step-5 review): `/m-design-review` — see Boundary section
- Plan generation (downstream): `/superpowers:writing-plans`
- ADR workflow: `~/.claude/skills/m-arch-review/adr-authoring.md`
- Example spec matching the template:
  `docs/superpowers/specs/2026-04-16-m-extract-knowledge-design.md` (Obsidian repo)
