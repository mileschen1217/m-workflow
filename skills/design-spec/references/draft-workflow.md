# Draft inputs & workflow

## Inputs to collect

If not provided in the invocation:
1. **Feature name** (kebab-case, used in filename)
2. **Goal statement** (one paragraph — what is this feature solving?)
3. **Exploration references** — one or more of:
   - File paths to research notes (e.g., `ai_explosion_kb/Inbox/<note>.md`)
   - Inline summary of prior exploration
   - "None — design from problem statement"

## Drafting workflow

1. **Read** the template from the path in the config (default: skill's own
   `template.md`)
2. **Read** all exploration references provided
3. **Draft** each template section. Follow the template's section order and
   guidance. Do not skip Foundation, Acceptance Criteria, Error Handling, or
   Invariants — Foundation locks scope; the other three feed the ATDD+TDD
   double loop. All four are mandatory.
   Also draft the ## Verification Strategy section (coarse, risk-scaled) — state the
   risk layers, power-on-ability, live means, and the Live-bearing AC IDs list. It is
   mandatory for a full spec (the skip-spec path is exempt — see SKILL.md Skip when).

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
- Every AC must appear in the `### Index` table with a stable `AC-N` id and
  have a matching `### AC-N — <name>` block below it (1:1 — every index row
  has a block, every block has a row). Assign N 1-based at draft; never reuse
  within a spec. The index has NO Test column and no per-AC red/green state —
  coverage is derived each review pass by the reviewer reading test source. The
  only authored per-AC marker is an inline `[unverified: <reason>]` (reason
  mandatory; a live-bearing AC may not carry it). See
  `docs/adr/0009-evidence-honesty-gate.md`.

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
