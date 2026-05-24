# m-workflow CONTEXT

The canonical vocabulary the m-workflow skill family operates in. SKILL.md bodies Read this file at Step 0 when source-as-truth discipline is adopted. Edit here only; no copies live in SKILL.md.

## What this document is

Constitution + bridge content for the source-as-truth discipline. "Constitution" sections are permanent; "enforceable-rule" sections carry `kill-on: lever-discipline-mechanisation` (a future linter/CI grep tool that would mechanise them).

## Skill / Mode / Discipline / Baseline — structural roles

Constitution.

Four structural roles for cross-cutting behavior in the m-workflow plugin, distinguished by **activation scope**:

| Role | Activation scope | How turned on | Example |
|---|---|---|---|
| **Skill** | per-invocation | `Skill` tool call | `grill-with-docs` |
| **Mode** | per-session | user toggle (e.g. `/<mode-name>`) | `caveman`, `grounded-claims` |
| **Discipline** | per-project | `.claude/m-workflow.yaml` `adopted_disciplines:` | `source-as-truth` |
| **Baseline** | per-plugin | hard-coded into plugin | `intention-first` |

The four are exhaustive and mutually exclusive — every cross-cutting rule fits exactly one role.

### Classification flow

Three sequential questions decide where a concept goes:

1. **Is it cross-cutting?** (modifies ≥2 stage skills' steps)
   - No → it's a **skill** (one entry point, one purpose).
2. **What's the natural activation scope?**
   - Single moment in a task → keep as skill (manual invoke each time).
   - Ambient within one work session, may flip mid-session → **Mode**.
   - Ambient for the lifetime of a project, set once → **Discipline**.
   - Cannot reasonably opt out at any scope → **Baseline**.
3. **Is it step-level mechanisable?** (expressible as "in skill X step Y, do Z")
   - No → it's prose, belongs in `CLAUDE.md`, not in the role taxonomy.

### Why these four roles

The roles map to **who has agency over the toggle**:

- Skill: caller decides per-invocation.
- Mode: user decides per-session (highest agency for ambient behavior).
- Discipline: project owner decides at setup (institutional commitment).
- Baseline: plugin author decides; users cannot opt out.

At any one skill Step, only currently-active modes + adopted disciplines + baselines fire. Each fire is a discrete enumerable rule, not ambient mood. Adding a new role-instance should not increase per-Step cognitive load unless that Step explicitly enumerates the new rule.

Roles compose; they don't accumulate as global modifiers.

### Current inventory

The live set of role-instances. Single source of truth — ADRs classify; this table records what exists and its status.

| Instance | Role | Status | Authority |
|---|---|---|---|
| `source-as-truth` | Discipline | Adopted, shipped | ADR-0004; this doc |
| `intention-first` | Baseline | Building (Epic D); legacy always-on 4Q exists | ADR-0003 |
| `grounded-claims` | Mode | Proposed; not yet in plugin (Epic A) | ADR-0002 |
| `caveman` | Mode | External skill; not in plugin | global `~/.claude/skills/caveman` |

`grounded-claims` was formerly named `ground-as-source`; renamed to disambiguate from the `source-as-truth` Discipline (they govern different relationships — doc↔source vs claim↔evidence; see ADR-0002).

### Fire ordering (when multiple fire at one Step)

When several baselines/disciplines/modes are active at the same skill Step, scope-framing fires before content-rules: **`intention-first` (Baseline) → `source-as-truth` (Discipline) → active Modes**. Rationale: the intention gate can reframe scope ("this is a fixture, not a spec") and abort the Step; running it first avoids wasted vocabulary-load cost.

## Four doc kinds

Constitution. Every doc is one of four kinds. Each has a lifecycle.

| Kind | Question it answers | Lifecycle | `kill-on:` required? |
|---|---|---|---|
| Navigation | Where does X live? | Permanent; ideally generated | No |
| Bridge | What's the rule / trap? | Mortal — declared `kill-on:` at birth | Yes |
| Workflow | How do we work? | Permanent; human-governed | No |
| Diagnostic | How did we discover this? | Permanent but inert; `evidence-for:` link | No |

## Bridge content gate — three principles

Enforceable-rule. `kill-on: lever-discipline-mechanisation`. Every bridge claim must pass all three. Failure = defect.

- **P1 (non-duplication):** if source already encodes the claim (a type / function / test), the prose is duplicative. Delete or point at source. **Also rejects doc-as-workaround:** if prose explains why dead/duplicative source still exists, remove the source instead.
- **P2 (falsifiable):** every claim concrete enough to write a test / run a probe / grep. Forbidden tokens (signal failure): *usually, typically, complex, careful, should, elegant* (as content, not meta).
- **P3 (no single host):** if it fits in one symbol's `///` → rung 2; one function body's `// BRIDGE` → rung 3; **only** when no single host fits → rung 4 (`.md` bridge).

Composition: P1 → P2 → P3, in order. Failing one is a defect, not "needs work".

## Standing vs transient bridge

Constitution. Bridges have a second axis: scope span.

| Layer | Path | Lifecycle | Cold-start reads? |
|---|---|---|---|
| Standing | architecture docs dir | Long-lived; `kill-on: <lever>` retires it | Yes — cross-feature invariants |
| Transient | specs dir | Short-lived; retires when feature lands | No — epic-context only |

Cold-start readers enter through standing bridges + navigation, never through specs.

## Three layers of knowledge — complementarity rule

Constitution. Navigation / Bridge / Source each answer one question. Complementary, not overlapping.

| Layer | The question | Trust |
|---|---|---|
| Navigation | "Where does X live?" | High (pointer) |
| Bridge | "What's the rule?" | Medium (drifts) |
| Source | "What does it do?" | Absolute (final arbiter) |

When in doubt: Where → Navigation; What's the rule → Bridge; What does it do → Source.

## Bridge proximity ladder

Enforceable-rule. `kill-on: lever-discipline-mechanisation`. Bridge content lives at one of four rungs, descending preference.

| Rung | Form | When |
|---|---|---|
| 1 | Type or test (source itself) | The fact can be encoded mechanically |
| 2 | `///` doc-comment on a symbol | Fact attaches to one symbol |
| 3 | `// BRIDGE` block at call-site | Fact attaches to one function body's call sequence |
| 4 | `.md` bridge doc | Cross-module / cross-language / negative-space / cold-discoverability fact |

Generic example: VLAN-port-membership update order = rung 3 (`// BRIDGE` block on the call sequence).

## Validation rubric (load-bearing)

Enforceable-rule. `kill-on: lever-discipline-mechanisation`. Every lever epic satisfies three signals.

- **Signal 1 — Compile-fail test (strongest):** the lever encodes its rule as compile-time guarantee. Rust: `compile_fail` doctest. TypeScript: `// @ts-expect-error` test. Python: `mypy --strict` failing on the symbol. Adapt to the language; the principle is encoding mechanically.
- **Signal 2 — Doc deletion:** every lever names a target bridge doc that becomes deletable on land. Epic close includes the deletion commit OR residual-content note.
- **Signal 3 — Cold-start delta:** measured before/after; pass if recon turns drop meaningfully. Advisory, not gating.

## Frontmatter schema

Constitution. Fields introduced by source-as-truth:

| Field | Required when | Value |
|---|---|---|
| `kind:` | every doc | one of `navigation`, `bridge`, `workflow`, `diagnostic` |
| `kill-on:` | `kind: bridge` | slug of the lever epic that retires the doc |
| `evidence-for:` | `kind: diagnostic` | path(s) to the workflow/ADR this diagnostic supports |
| `evidence:` | optional reciprocal on workflow/ADR | list of diagnostic paths supporting the decision |

`evidence-for:` ↔ `evidence:` makes the link bidirectional.

## Agent dispatch axis

Constitution. Classifies *how a multi-task plan is executed* — orthogonal to the four structural roles (which classify activation scope of cross-cutting behavior). Workflow kind; human-governed.

One decision, one knob:

- **Dispatch: inline vs delegate.** Inline = orchestrator executes directly, reusing its loaded context. Delegate = hand the work to a subagent.
- **Delegate ⟹ fresh × on-disk contract.** A one-shot agent reads `contract.md` and emits `result.json`; cross-step state lives on disk (commits + result), never in a persistent agent's memory.
- **Granularity knob (delegate only):** bundle cohesive / shared-read-set tasks into one contract to amortize re-read; split independent tasks for parallelism / isolation; stop bundling before the agent's context rots (~2–4 tasks). Token cost is amortized by bundling, never by keeping an agent alive across turns.

Two things are NOT dispatch patterns:

- **Exploration subagent** (read-only info-gathering) is a tool — fresh, in-context, ceremony-free. No contract.
- **Persistent resource** (live bench, warmed REPL) is resource management — the *resource* persists; the agent stays fresh and reconnects via a handle carried in the contract.

Decision unit = **phase** (the longest contiguous task run whose answer is constant). A uniform plan is one phase / one pattern; cut a new phase where the answer flips (e.g. a bench-bound phase appears).

Plans are written **dispatch-agnostic** (task + AC + files + sequence). At the plan→execution surface the orchestrator derives phase segmentation + bundling from each task's `Files` and dependency edges, **recommends** a pattern + rationale, and the human **picks**. Contracts are an execution-time projection of plan tasks — generate them only when delegating.

### Scope-change protocol

When a subagent discovers mid-run that an Acceptance Criterion requires acting outside its contract Scope, it neither silently expands nor dumb-stops: it emits a structured `scope_change_request` and the orchestrator adjudicates by **reversibility, not file location** (reversible + in-boundary → auto-approve + amend Scope + re-dispatch; irreversible or cross-boundary → escalate to human). Request + decision are logged to the epic scope-change ledger for audit and epic-close retro. Schema, adjudication policy, and ledger format have one home: the task-contract template § Scope-Change Protocol.

This protocol organizes intent and auditability only. It does **not** enforce safety — preventing an unauthorized irreversible action is CC's own permission mode / hooks / sandbox / git, configured by the operator.

Transport is agnostic: the request rides result.json (`status: needs-scope-expansion`) for one-shot subagents (stable), or the agent-teams `plan_approval_request` runtime channel (experimental) when enabled.

## Template co-location

Constitution. A template lives co-located with its sole owning skill at `skills/<skill>/templates/` (a `templates/` dir even for a single file). The root `templates/` dir is reserved for templates shared by 2+ skills. Skills reference their templates by **plugin-relative path**, never an absolute `~/.claude/skills/m-*` path.

> Known violation, deferred to Epic A (consolidation): `arch-discovery` and `design-spec` reference their own bundled assets (template / lenses / coverage-matrix / exemplar / adr-authoring) via absolute `~/.claude/skills/m-*` paths. Recorded here; the systematic fix is not in scope for `doc-and-role-cleanup`.
