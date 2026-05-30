---
kind: workflow
adr_id: 0012
status: Proposed
date: 2026-05-29
---

# ADR-0012: Canonical-form storage adapter contract for `epic-driven-roadmap`

## Status

Proposed. Decided during Stage 1.5 grill-with-docs for Phase 2 of the
`portability-and-storage-adapters` epic. Implementation lands when Phase 2
design-spec ships its first conforming adapter (local-markdown reference impl).

## Triggered by

`portability-and-storage-adapters` epic, Phase 2 — split `epic-driven-roadmap`
into a procedure layer + storage adapter layer so future backends (Obsidian MCP,
GitHub Issues, Linear, …) can be added without touching workflow logic.

## Related ADRs

- ADR-0011 (honesty spine as Constitution) — the parse-loud / no-silent-drop
  posture in this ADR is a direct application of the spine: failure at the
  storage boundary must be loud, never silent false-green.
- ADR-0009 (evidence-honesty gate) — establishes "deterministic floor, no
  over-engineering" framing; canonical form follows the same minimum-floor
  discipline.

## Context

Today `epic-driven-roadmap/SKILL.md` mixes workflow logic (scaffold / close /
audit / Foundation elicitation / Stage 7 reckoning) with local-markdown IO
assumptions (it knows the on-disk shape — `.touchstone/epics/<slug>/index.md`,
markdown tables, frontmatter keys). Two pains follow:

1. **Portability.** Users wanting GitHub Issues, Obsidian MCP, or Linear as the
   epic tracker cannot adopt the workflow without forking the skill.
2. **Honesty risk.** If a future backend silently drops a field (e.g. `landed`
   not preserved), the close gate could mis-judge ship status — a silent
   false-green at the storage boundary.

Phase 2 must define the contract between procedure and adapter cleanly enough
that adding an adapter is a localised, declarative act — and that failure at
that boundary is loud.

Three serious alternatives were weighed during the grill:

- **Raw markdown blob** across the boundary, procedure parses inline via LLM.
- **Section-keyed half-structure** (`{frontmatter: {...}, sections: {Aim: "...", Phases: "..."}}`).
- **Fully-structured canonical record** with adapter-internal deterministic parse.

## Decision

Adopt a **canonical-form contract** with these properties:

1. **Two layers, one contract.** `epic-driven-roadmap` splits into:
   - **Procedure layer** — workflow prose in SKILL.md, speaks only `EpicData`.
   - **Storage adapter layer** — deterministic, script-implemented shim.
   - The two communicate exclusively through the canonical `EpicData` value.

2. **Canonical form holds the gate-required minimum, not the union of all
   backend fields.** A field belongs in canonical iff some touchstone gate or
   procedure step reads or writes it. Decorative or backend-specific fields
   ride along as **sidecar passthrough**.

   Initial canonical fields (subject to Phase 2 design-spec refinement):

   | Field | Read/written by |
   |---|---|
   | `slug`, `status`, `started`, `landed` | identity + Stage 7 ship gate |
   | `aim`, `intention`, `out_of_scope` | Foundation elicitation gate (Foundation elicitation reuse check) |
   | `phases[].{n, title, status, landed}` | close gate (all phases done?) |
   | `retrospective` | close procedure (append on close) |
   | `open_questions` | Phase 1 findings / pivot capture |

   Decorative / sidecar (not canonical): `target`, `owner_teams`,
   `gitlab_issues` / `github_issues`, `pivots`, per-phase `spec` / `plan` links,
   retrospective free-form body, anything backend-introduced.

3. **Adapter is a bidirectional shim.** Required surface:
   `read(slug) → EpicData`, `write(slug, EpicData)`, `list() → [slug...]`,
   `exists(slug) → bool`. The shim converts canonical ↔ backend-native on each
   call. Adding a backend = writing a new shim, not touching procedure prose.

4. **Parse is deterministic and inside the adapter.** Adapters implement parse
   + schema validation as scripts (Python / bash / equivalent), not as LLM
   inline parse inside SKILL.md prose. Schema mismatch on `read()` throws loud.
   Sidecar fields the backend cannot hold cause `write()` to throw, never
   silent drop.

5. **Evolution discipline.** Canonical form carries a `schema_version`.
   Canonical-form changes are an epic-driven event with adapter-migration
   responsibility; sidecar changes are per-backend and don't bump the version.

6. **Review test for canonical scope** (load-bearing): every proposed canonical
   field must answer "which gate reads or writes this?". If the answer is
   "none", the field belongs in sidecar. This test re-runs whenever canonical
   evolves.

## Consequences

**Positive**

- **Portability is mechanical.** New backend = new adapter + new shim; zero
  procedure-layer edits.
- **Honesty at the storage boundary.** Loud throws on schema mismatch and on
  impossible writes preserve the honesty spine into the IO layer.
- **Procedure layer simplifies.** Workflow prose stops reasoning about file
  paths, table layouts, or frontmatter keys.
- **Phase 5 alignment.** L1/L2 layered spec contract (Phase 5) and canonical
  form (this ADR) share the same minimum-fields philosophy — they reinforce
  each other.

**Negative / costs**

- **Schema is a first-class artifact.** Canonical form must be specced,
  versioned, and migrated; this is real engineering work, not a markdown tweak.
- **Adapter authors carry the parse burden.** Each new backend must implement
  deterministic parse + schema validation, not just IO.
- **Sidecar boundary is a judgement call.** Some fields will be borderline
  (does any gate read them?); the review test keeps the boundary honest but
  doesn't fully eliminate ambiguity.

## Alternatives considered

- **Raw markdown blob across the boundary, LLM parse in procedure.** Rejected:
  LLM parse fails silently (missing field → `None` → mis-judged gate state),
  which is the exact failure mode the honesty spine forbids.
- **Section-keyed half-structure.** Rejected: section names ("Aim", "Phases",
  "Retrospective") are a local-markdown convention with no analogue in
  Obsidian / GitHub Issue / Linear — portability breaks immediately.
- **Domain-rich adapter** (adapter knows "epic" / "phase" / "retrospective"
  semantically and exposes them as native operations). Rejected: collapses
  procedure and storage layers back together, defeating the split this epic
  exists to make.
- **Exhaustive backend research before contract design.** Rejected: new
  backends appear over time; the contract must be designed against a minimum
  principle (gate-required canonical), not against a closed backend set.
