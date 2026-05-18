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
| **Mode** | per-session | user toggle (e.g. `/<mode-name>`) | `caveman`, `ground-as-source` |
| **Discipline** | per-project | `.claude/m-workflow.yaml` `adopted_disciplines:` | `source-as-truth` |
| **Baseline** | per-plugin | hard-coded into plugin | _(none currently)_ |

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
