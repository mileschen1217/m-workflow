---
slug: <slug>
status: proposed            # proposed | active | paused | done | cancelled
started:                    # YYYY-MM-DD when work begins
target:                     # optional YYYY-MM-DD
landed:                     # set on close
owner_teams: []
gitlab_issues: []
---

# <Epic Title>

**Aim:** <One-sentence deliverable. Name the surface, not the phase number.>

## Intention

> Filled at scaffold time per global CLAUDE.md § Working Style intention-alignment gate. Locks scope before any spec is written.

- **Goal (observable):** <What does success look like? Name the surface that observes success — user message, test result, REST response, on-device state.>
- **In scope:** <≤3 bullets — what this work touches.>
- **Out of scope (explicit):** <≤3 bullets — what this work will NOT touch even if related. Each bullet is a route NOT taken.>
- **Fix vs. workaround:** <If a fixture / config knob / external workaround can achieve the goal, name it here and say why it is or isn't acceptable. If proceeding with production-code change, justify why the workaround route is rejected.>
- **Smallest change:** <Minimum diff size and shape — N files in M repos, or "1 fixture file in test infra". Name what would expand it past minimum.>

## Phases

| # | Title | Spec | Plan | Status | Landed |
|---|---|---|---|---|---|
| 1 | <phase title> | [spec](../../specs/YYYY-MM-DD-<slug>.md) | [plan](../../plans/YYYY-MM-DD-<slug>.md) | proposed | |

## Pivots

*(none yet; one line each when added)*

## Open Questions

*(one line each)*

## Retrospective

*(filled on close. If `scope-changes.jsonl` exists in this epic dir, review it for scope-expansion patterns — recurring expansions signal contracts scoped too narrowly upstream.)*

**What worked**
- …

**What pivoted**
- …

**What to do differently**
- …
