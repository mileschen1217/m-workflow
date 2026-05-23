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

**Aim:** <One-sentence observable deliverable. THIS is the single home
for the aim field at epic level — do not repeat it below.>

## Foundation

> Set at scaffold time via elicitation (Step 0). One-line version of each
> field — enough to route and incremental-load without opening a spec. The
> aim field lives in the **Aim:** headline above; this block carries the
> other two foundation fields. The spec carries the full phase version.

- **Intention (why):** <One line: motivation / pain driving this epic.>
- **Out of scope:**
  - <route this epic will NOT take, even if related — a route, not a
    category>
  - <up to three sub-bullets total; flat list, never nested>

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
