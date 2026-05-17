# Lenses (L1–L18)

The lens framework is the column axis of the §0 coverage matrix. Each lens is a viewpoint the discovery doc must answer for every feature — not a separate document, but a question to ask while reading any section.

A feature is **covered by a lens** when the discovery doc has a section that answers that lens's question for that feature *and* the §0 cell cites it. "Mentioned in passing" ≠ covered.

L1–L16 are required columns. L17/L18 are optional and only included when scope warrants (quality scenarios, multi-SKU support).

## Provenance

The lens set was distilled from arc42 (12-section template), IEEE/ISO/IEC 42010 (architecture description: viewpoints × concerns), 3GPP TS 23.501 (5G system architecture style: roles/state/procedures/lifecycle), Kruchten 4+1 (logical / process / dev / physical / scenarios), C4 Model (system / container / component / code), and INCOSE systems engineering (capability/constraint/forced behavior). It is not a copy of any one — it is the union projected onto a flat lens × feature grid so a single doc can claim completeness against a single matrix.

## L1 — Functional behavior

> **Question:** What does this feature do, observably, from outside?

External behavior. CLI output, REST response, on-device state change, packet egressing the box. No "internally we …" — that is L2 / L4 / L8.

Cited from: §1.1 roles, §4 flows.

## L2 — Ownership / authority

> **Question:** Who is the sole authority for the state this feature touches? Who replicates it?

Single-writer claims. "X owns Y" is load-bearing — every consequence ("any read of Y goes through X", "writes to Y from non-X are bugs") downstream cites this lens.

Cited from: §1.2 ownership model.

## L3 — Invariants

> **Question:** What property must hold E2E at every instant? What is the symptom when it doesn't?

Numbered, falsifiable. Format: `INV-<scope>-N. <statement>. Violation symptom: <what breaks>.` If you cannot name the symptom, the invariant is too vague.

Cited from: §1.3 system invariants.

## L4 — State the system carries

> **Question:** What state does this feature read/write? Where does it live (RAM / NVRAM / ASIC / SHM / peer-replicated)?

The state inventory. Each state item: owner role, replicas, sync mechanism, consistency model.

Cited from: §3.1 / §3.2.

## L5 — Information flow / config plane

> **Question:** How does operator intent become programmed state for this feature?

CLI → validation → persistence → replication → platform program → runtime visibility. Where does the change "land" before the data plane sees it?

Cited from: §4.1 config flow.

## L6 — Configuration model

> **Question:** What does the operator-facing config surface look like? Schema, defaults, validation rules.

The contract operators write against. Distinct from L5 (the *flow*); L6 is the *shape*.

Cited from: §4.1 + §7 (interfaces).

## L7 — Data plane procedures

> **Question:** What happens to a packet (or work-unit) end-to-end for this feature?

Ingress conditions → per-stage processing → egress. Cite invariants (L3) and platform forced behaviors (L11) at each step.

Cited from: §4.3 / §4.4.

## L8 — Control plane events

> **Question:** What async events drive this feature? Source, propagation, downstream consequences.

Link up/down, role change, partition, peer-down, timer-fire. For each event class: who emits, who consumes, what state mutates.

Cited from: §4.2.

## L9 — Platform capabilities

> **Question:** What does the platform *enable* that this feature uses? Mechanism + where exercised.

The capability-side of platform behavior. Examples: hardware route lookup, ASIC ARP table, multicast replication, CPSS designated-device dispatch.

Cited from: §2.1 + §2.4 (SDK contract surface).

## L10 — Platform constraints

> **Question:** What limit does the platform impose that this feature designs around? Limit value + source.

The constraint-side. Table sizes, counter widths, sampling rates, granularity floors. Source must be cited (datasheet / SDK header / experiment).

Cited from: §2.2 + §2.5 (resource limits).

## L11 — Platform forced behaviors

> **Question:** What does the platform do *without asking* that this feature must accommodate?

The "facts of life" layer. Auto-aging, hardware learning, automatic traps to CPU, silent drops on table overflow, implicit broadcast. These are not choices.

Cited from: §2.3.

## L12 — Failure modes

> **Question:** What can fail for this feature, what's the symptom, how is it detected, how does it recover?

Per component, per link, per role. Each row: what fails / observable symptom / detection / recovery / notes.

Cited from: §6.

## L13 — Lifecycle

> **Question:** How does this feature change across boot → role-elect → topology-converge → steady → fault → recover → leave?

For each phase: what ownership/state/flow changes; what invariants are transiently violated and for how long.

Cited from: §1.4 + §5.

## L14 — Interfaces & boundaries

> **Question:** What external interfaces does this feature expose? Contract shape, ownership of each side, versioning.

CLI, REST, IPC, SDK, wire protocol. Distinct from L6 (operator config) — L14 covers all interfaces including peer-to-peer, internal IPC, and machine clients.

Cited from: §7.

## L15 — Decisions

> **Question:** What architectural decisions shape this feature? Where is rationale captured?

Pointer to ADRs. Discovery doesn't restate rationale — it cites.

Cited from: §9.

## L16 — Open questions

> **Question:** What is unresolved for this feature? How will it be resolved?

Numbered, terse. Each question: resolution path (experiment / vendor consult / sibling spec / next epic).

Cited from: §8.

## L17 — Quality scenarios *(optional)*

> **Question:** What quality attributes (latency, throughput, scale, reliability) does this feature need to meet, under what scenario?

SEI Quality Attribute Workshop style: stimulus / source / environment / response / measure. Include when SLOs are part of the scope.

Cited from: §1.5 (or appendix).

## L18 — SKU / platform-support matrix *(optional)*

> **Question:** Which device variants, hardware revs, or build profiles does this feature support? What differs?

Include when the discovery covers a product family with non-trivial variation. Each row: SKU / supported / divergence / workaround.

Cited from: §2.6 (or appendix).

## How to use this file

- Discovery authoring: re-read the lens question before writing each section. If a feature row in §0 has any `unset` cells, you have not asked the lens's question yet.
- Sweep: for each `gap` cell, the lens question *is* the prompt. "What does feature X do observably?" "Who owns state Y?" "What forced behavior does the ASIC impose for Z?"
- Review: a finding like "§4.3 doesn't address what happens to the packet after the SVI lookup" is L7-coverage gap on whichever feature owns SVI lookup. Cite the lens.

The lens framework is the contract. The matrix is the audit log. The doc is the deliverable. All three move together.
