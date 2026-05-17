---
type: discovery
epics: [{{slug}}]
status: Discovery (in progress)
---

# {{topic-name}} — Architecture Discovery

**Date:** {{YYYY-MM-DD}}
**Status:** Discovery (in progress)
**Topic slug:** {{slug}}
**Owner:** {{author or team}}

> System-definition document. Describes end-to-end behavior, ownership, invariants, state distribution, flows, lifecycle, and platform constraints — without committing to implementation. Spec authoring (Stage 3) inherits §1 (system model) and §2 (platform behavior) as starting assumptions; do not re-derive them.

> **Authoring shape (mandatory per leaf section in §1–§7):** every leaf section uses three named subsections — **Narrative**, **Diagram**, **Claims** — as `####` headers. Bullets-only sections are a defect; they read as axiom lists and lose the human-alignment audience.
>
> ```
> ### §X.Y <section title>
>
> #### Narrative
>
> 2–4 short paragraphs. Walk the reader through what this section
> establishes and why. Use a concrete scenario where it helps
> ("imagine a ping arrives at M3 …"). No bullets here.
>
> #### Diagram
>
> Mermaid block when the section has structural content (topology,
> ownership, sequence, state machine, packet walk). If skipping,
> write "*Skipped — <one-line reason>.*" so it's visibly an
> intentional choice, not an oversight.
>
> #### Claims
>
> The atomic, citable bullets / numbered items / table rows that
> downstream specs and the §0 matrix cite. This is the load-bearing
> payload — keep it tight and falsifiable.
> ```
>
> Narrative + Diagram = human-alignment surface. Claims = machine-alignment surface. Both are first-class.
>
> **Lens annotations stay out of section headers.** Lens references (L1, L2, …) live in §0 (matrix columns) and Appendix A (definitions). Section headers carry only the human title — the matrix is the authoritative cross-reference.

---

## §0 Coverage matrix

The completeness contract. Rows = features. Columns = lenses. Each cell cites the section that addresses it, or carries one of: `gap` (known missing) / `deferred (→ pointer)` / `N/A (rationale)`.

Cell-state vocabulary, transitions, and sweep protocol live in `~/.claude/skills/m-arch-discovery/coverage-matrix.md`.

| Feature \\ Lens | L1 Func | L2 Own | L3 Inv | L4 State | L5 Info | L6 Cfg | L7 Data | L8 Ctrl | L9 Cap | L10 Cstr | L11 Force | L12 Fail | L13 Life | L14 Iface | L15 Dec | L16 OQ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| <feature-1> | gap | gap | gap | gap | gap | gap | gap | gap | gap | gap | gap | gap | gap | gap | gap | gap |
| <feature-2> | gap | | | | | | | | | | | | | | | |

Optional rows (include when scope warrants): L17 Quality scenarios, L18 SKU / platform-support matrix.

---

## §1 System model

The axiom layer — everything downstream cites here.

### §1.1 Roles

Enumerate the actors / role types. For each: name, responsibility scope, election/assignment mechanism, lifecycle. *Lens coverage: L1, L13.*

### §1.2 Ownership model

Who is authoritative for what state? One claim per ownership statement, format:
> **Owner X** is the sole owner of **state Y**. **Consequence:** …

*Lens coverage: L2.*

### §1.3 System invariants

Numbered properties that must hold. Format:
> **INV-<scope>-N.** <statement>. **Applicability:** <when this must hold>. **Violation symptom:** <what breaks>.

**Mandatory: every invariant carries an applicability scope.** Without it, an invariant phrased as "must hold at every instant" will contradict the lifecycle (§1.4 / §5), which legitimately includes phases where the property is being *established* (e.g. cold-push during topology converge, eventual sync during recover). Choose one applicability per invariant:

- `always` — must hold from boot onward, no exceptions. Rare.
- `steady-state` — must hold once topology has converged and no fault is in progress. Most invariants belong here.
- `eventually-consistent during <phase>` — may transiently violate during a named §1.4 phase, must reconverge within a bounded window. State the window.
- `post-commit` — must hold after a successful config/event commit, not during the commit itself. Useful when partial-write semantics are in scope.

Group invariants by scope (identity / symmetry / authority / continuity / …) in the Narrative; list as numbered Claims with explicit applicability. *Lens coverage: L3.*

### §1.4 Lifecycle

Phases the system traverses: boot → role-elect → topology-converge → steady-state → fault → recover → leave. For each phase, name what changes in §1.2 / §1.3. Detailed state/flow per-phase walk lives in §5. *Lens coverage: L13.*

---

## §2 Platform behavior surface

The hardware / runtime layer. Three crisp categories. Do not skip on embedded / ASIC systems — this layer is what prevents architectural proposals the platform cannot uphold.

### §2.1 Capabilities

What the platform *enables* that we use. Each item: name, mechanism, where in the doc it's exercised. *Lens coverage: L9.*

### §2.2 Constraints

What the platform *forbids* that we design around. Each item: limit value, source (datasheet / SDK / experiment), workaround. *Lens coverage: L10.*

### §2.3 Forced behaviors

What the platform does *without asking*. These are not choices — they are facts the architecture must accommodate. Examples: auto-aging, hardware learning, automatic traps, silent drops on table overflow. *Lens coverage: L11.*

### §2.4 SDK / driver contract surface

The API/contract boundary between our code and the platform vendor. Names, version, availability matrix, breaking-change history if relevant. *Lens coverage: L9 (sub).*

### §2.5 Resource limits + telemetry granularity

Table sizes, counter widths, sampling rates, granularity floors. Anything that limits what we can measure or store in hardware. *Lens coverage: L10 (sub).*

---

## §3 State the system carries

### §3.1 Per-role state inventory

For each role from §1.1: what state it holds, whether authoritative or replica, where stored (RAM / NVRAM / ASIC / SHM). *Lens coverage: L4.*

### §3.2 State distribution / replication / authority

For each shared state item: who's authoritative, who replicates, sync mechanism, consistency model. *Lens coverage: L4.*

---

## §4 Flows

End-to-end procedures. Cross-cutting — features appear *within* each flow, not as parallel sub-trees.

### §4.1 Config flow

Operator intent → programmed state. Trace from CLI / REST / API entry through state replication and platform programming, ending where runtime data plane sees the change. *Lens coverage: L5, L6.*

### §4.2 Control plane events

Async event flows: link up/down, role change, partition, peer-down. For each event class: source, propagation, downstream consequences. *Lens coverage: L8.*

### §4.3 Data plane procedures

E2E packet (or work-unit) walks. For each scenario: ingress conditions; per-stage processing; cite §1 invariants and §2 platform behaviors at each step; egress / completion. *Lens coverage: L7.*

### §4.4 Trap / exception dispatch

How exceptions (TTL=1, unknown route, control packets, errors) are identified, classified, and routed to the correct handler. Often the locus of platform-specific complexity. *Lens coverage: L7 (sub).*

---

## §5 Lifecycle phases (re-walked end-to-end)

For each phase from §1.4, walk the state/flow changes. Format per phase:

#### §5.N <phase-name>

- **§1.2 ownership changes:** …
- **§3 state changes:** …
- **§4 flows triggered:** …
- **§1.3 invariants impact:** … (transient violations? reconvergence window? atomic update?)

This is the failover / partition / recovery story. Do not write a parallel state machine — re-walk the sections you've already established. *Lens coverage: L13.*

---

## §6 Failure modes

Per component, per link, per role. *Lens coverage: L12.*

| What fails | Observable symptom | Detection | Recovery | Notes |
|---|---|---|---|---|
| | | | | |

Each row should be cross-referenced from §4 walks where the failure manifests.

---

## §7 Interfaces & boundaries

External interfaces. CLI / REST / IPC / SDK / wire protocol. For each: contract shape, who owns each side, versioning policy, backwards-compat stance. *Lens coverage: L14.*

---

## §8 Constraints & open questions

Numbered, terse. Each open question links to where it'll be resolved (experiment / vendor consult / sibling spec). *Lens coverage: L16.*

- OQ-1. <question>. Resolution path: …
- OQ-2. …

---

## §9 Decisions index

One-line list. Each line cites a sibling ADR. Rationale, alternatives, and consequences live in the ADR, not here. *Lens coverage: L15.*

- ADR-NNNN: <decision title>
- …

---

## Appendix A. Lens definitions (in-doc copy)

L1–L18 brief definitions for self-contained reading. Full reference lives in `~/.claude/skills/m-arch-discovery/lenses.md`. Update via that file and re-paste here.

## Appendix B. Provenance

Section-to-framework map for reviewers. Optional but useful:
- §1 system model ← arc42 §1+§3, IEEE 42010 viewpoints, 3GPP TS 23.501 §4 reference architecture
- §2 platform behavior ← INCOSE platform/system distinction, hardware-software co-design literature
- §4 flows ← 3GPP §5 procedures, RFC 4364 §5 forwarding
- §5 lifecycle ← arc42 §11, RFC 7432 §3 PE state machine
- §6 failures ← INCOSE failure mode/effects, RFC "Operational Considerations"
- §0 matrix ← IEEE 42010 view × concern grid, SEI QAW
