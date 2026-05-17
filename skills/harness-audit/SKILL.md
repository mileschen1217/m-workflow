---
name: harness-audit
description: |
  Composite harness-health dashboard. Surveys Claude Code session logs to
  surface skill usage patterns, dead skills, ADR adherence drift, and hook
  fire/fail signals. Points at specialist audits (/retro, /context-budget,
  /skill-stocktake) for deep dives. Invoke weekly or monthly to answer
  "is my custom harness working well?"
user-invocable: true
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
kind: workflow
---

# m-harness-audit

How do I know the harness runs well or bad? This skill answers that with a
composite view, then routes to specialist audits for depth.

## Scope: mostly user-level

The harness lives mostly at user-level (`~/.claude/skills/`, session logs for
ALL projects, the central ADR directory). So this skill surfaces user-level
signal regardless of CWD:

| Signal | Scope |
|---|---|
| Skill usage counts | Across ALL projects (all session JSONL under `~/.claude/projects/`) |
| Custom-skill coverage | User-level `~/.claude/skills/` (all `m-*` / `ai-*` skills) |
| Hook fire/fail | All sessions, all projects |
| Agent delegation log | All Agent dispatches (`~/.claude/agent_delegation.log`, written by `log-agent-delegation.sh` hook) |
| ADR adherence | Central ADR home (`claude_code_config/docs/adr/`) |
| auto-memory | Per-project (keyed by CWD). Use `--all-memory` to see all. |

Running under `~/Obsidian` vs `~/app/foo` gives the same view of
skill/hook/ADR signal — only the auto-memory section differs. This is
intentional: the harness is one thing, not per-project.

Project-local signal (project CLAUDE.md drift, project-local `.claude/skills/`)
is covered by `/skill-stocktake` when run with the project as CWD.

## When to Invoke

- **Weekly** — quick check (default: last 7 days)
- **Monthly** — deeper check (last 30 days) + ADR sweep
- After adding significant skills/hooks/agents
- When sessions feel slow or friction-heavy (check context bloat)

## Usage

```
/m-harness-audit              — weekly window (7d)
/m-harness-audit 30d          — monthly window
/m-harness-audit --dead       — dead-skill detection only
/m-harness-audit --adr        — ADR adherence sweep only
/m-harness-audit --full       — all signals + dispatch specialist audits
```

## Signals

### 1. Skill usage (from Claude Code session JSONL)

```bash
WINDOW_DAYS=${1:-7}
CUTOFF=$(date -v-${WINDOW_DAYS}d +%s 2>/dev/null || date -d "${WINDOW_DAYS} days ago" +%s)
SESSIONS_DIR="$HOME/.claude/projects"

# Count Skill tool invocations per skill name in recent sessions
find "$SESSIONS_DIR" -name "*.jsonl" -newer <(date -r $CUTOFF) -print0 2>/dev/null \
  | xargs -0 grep -hE '"type":"tool_use","name":"Skill"' 2>/dev/null \
  | grep -oE '"skill":"[^"]+"' | sort | uniq -c | sort -rn
```

Surface:
- **Top 10 most-invoked** — which skills earn their keep
- **Bottom 10 (zero or single-digit invocations over 30d)** — dead-skill candidates
- **Trend vs prior window** (if 30d window) — skills growing / declining

### 2. Custom-skill coverage

List every skill under `~/.claude/skills/` prefixed `m-`, `ai-`, and
project-local `.claude/skills/`, then cross-reference with invocation counts.

A custom skill with 0 invocations in 30 days is a **dead-skill candidate**.
Offer options:
- Remove (if confirmed unused)
- Relocate to project-level (if only one project uses it)
- Add to CLAUDE.md routing (if it's being forgotten rather than unneeded)

### 3. Hook fire / fail signal (from session JSONL)

Grep for hook output markers in recent session logs:

```bash
# Hook fires
find "$SESSIONS_DIR" -name "*.jsonl" -newer <(date -r $CUTOFF) -print0 2>/dev/null \
  | xargs -0 grep -hcE 'user-prompt-submit-hook|PreToolUse hook|PostToolUse hook' 2>/dev/null \
  | awk '{sum+=$1} END {print "Hook fires:", sum}'

# Hook failures (blocked, error, rejected)
find "$SESSIONS_DIR" -name "*.jsonl" -newer <(date -r $CUTOFF) -print0 2>/dev/null \
  | xargs -0 grep -hE 'hook.*(blocked|rejected|error|failed)' 2>/dev/null | head -20
```

Flag:
- **High fire / low fail rate** — hook working well
- **High fire / high fail rate** — hook is noisy (false positives); investigate
- **Zero fires** — hook not wired or broken; check settings.json

### 4. Agent delegation patterns (from `~/.claude/agent_delegation.log`)

The `log-agent-delegation.sh` PostToolUse hook appends one JSONL line per Agent() dispatch:

```json
{"ts":"...","subagent_type":"codex-implementer","description":"...",
 "prompt_chars":1234,"run_in_background":false,"is_error":false,
 "cwd":"...","session_id":"..."}
```

The log rotates at 10 MB (configurable via `AGENT_LOG_MAX_BYTES`); one prior generation kept at `agent_delegation.log.1`. To cover the full audit window even when rotation just happened, read both files:

```bash
LOG="$HOME/.claude/agent_delegation.log"
LOG_PREV="$HOME/.claude/agent_delegation.log.1"
( [ -f "$LOG" ] || [ -f "$LOG_PREV" ] ) || { echo "No agent_delegation.log yet — hook not fired."; }

CUTOFF_ISO=$(date -u -v-${WINDOW_DAYS}d +%Y-%m-%dT%H:%M:%SZ 2>/dev/null \
  || date -u -d "${WINDOW_DAYS} days ago" +%Y-%m-%dT%H:%M:%SZ)

# Helper: cat both generations (oldest first), tolerate either being missing
agent_log_concat() { cat "$LOG_PREV" 2>/dev/null; cat "$LOG" 2>/dev/null; }

# Total dispatches in window
total=$(agent_log_concat | jq -c "select(.ts >= \"$CUTOFF_ISO\")" 2>/dev/null | wc -l)

# Top agents by call count
agent_log_concat | jq -r "select(.ts >= \"$CUTOFF_ISO\") | .subagent_type" 2>/dev/null \
  | sort | uniq -c | sort -rn | head -10

# Vendor breakdown (Codex / CC / Gemini / general-purpose)
agent_log_concat | jq -r "select(.ts >= \"$CUTOFF_ISO\") |
  if (.subagent_type | test(\"^codex\")) then \"codex\"
  elif (.subagent_type | test(\"^gemini\")) then \"gemini\"
  elif (.subagent_type == \"general-purpose\") then \"general-purpose\"
  else \"cc\" end" 2>/dev/null | sort | uniq -c | sort -rn

# Error rate
errors=$(agent_log_concat | jq -c "select(.ts >= \"$CUTOFF_ISO\") | select(.is_error)" 2>/dev/null | wc -l)
echo "Error rate: $errors / $total"

# Per-project view (filter by cwd)
agent_log_concat | jq -r "select(.ts >= \"$CUTOFF_ISO\") | .cwd" 2>/dev/null \
  | sort | uniq -c | sort -rn | head -10
```

Surface:
- **Top 10 agents by dispatch count** — which backends earn their keep
- **Vendor split (Codex / CC / Gemini / general)** — confirms cross-vendor workflow is firing as designed; Codex agents at 0 over a 30d window after Phase 2 is a workflow-drift signal
- **Error rate by agent** — high errors on `codex-*` agents likely means quota / auth / sandbox issues; flag for investigation
- **Background vs foreground dispatch ratio** — sanity check (foreground should dominate; high background may indicate eager parallelization)
- **Zero dispatches** in window despite active sessions → hook not firing; check `settings.json` PostToolUse `Agent` matcher

### 5. ADR adherence sweep (`--adr` mode)

```bash
ADR_DIR="${ADR_DIR:-$HOME/claude_code/claude_code_config/docs/adr}"
ls "$ADR_DIR"/[0-9]*.md 2>/dev/null | while read f; do
  TITLE=$(head -1 "$f")
  DECISION=$(awk '/^## Decision/,/^## /' "$f" | head -20)
  echo "=== $TITLE ==="
  echo "$DECISION"
done
```

For each ADR:
1. Extract the decision (what was committed to)
2. Check the described implementation exists — file paths, skill names,
   commands referenced in the ADR should resolve
3. Flag **drifted** ADRs (referenced file missing, skill not found, etc.)

Use AI judgment, not regex. Output: list of ADRs with status
{in-force, drifted, superseded, stale}.

### 6. auto-memory health

Auto-memory is per-project (keyed by CWD). Audit the memory for the project
you invoked the skill in. Derive the project key from CWD:

```bash
PROJECT_KEY=$(pwd | sed 's|/|-|g' | sed 's|^-||')
MEM_DIR="$HOME/.claude/projects/-$PROJECT_KEY/memory"
[ -d "$MEM_DIR" ] || { echo "No auto-memory for this project yet."; exit 0; }
ls "$MEM_DIR"/*.md 2>/dev/null | wc -l      # entry count
wc -l "$MEM_DIR"/MEMORY.md 2>/dev/null      # index size
```

If the user wants to audit auto-memory across all projects, pass `--all-memory`
and iterate `~/.claude/projects/*/memory/` directories.

Flag:
- **Index >200 lines** — truncation risk; prune
- **Entries >30 days stale with no updates** — consider archiving

## Report format

```markdown
## Harness Audit: last {N} days

### Skill usage
**Top 5:** (usage count / skill)
1. superpowers:brainstorming — 42
2. m-code-review — 28
3. ...

**Dead candidates (0 invocations):**
- m-foo (custom, 34 days since last use) → suggest: remove / relocate
- ai-bar (custom, 21 days) → suggest: CLAUDE.md mention missing?

### Hooks
- commit-gate.sh: fired 14× / blocked 0× (clean)
- log-agent-delegation.sh: fired 87× / errors 0×
- Any ECC hook issues: ...

### Agent delegations (last {N} days)
**Total:** 87 dispatches | **Error rate:** 1/87 (1.1%)

**Vendor split:**
- cc: 64 (74%)
- codex: 19 (22%)
- gemini: 4 (5%)

**Top agents:**
1. everything-claude-code:code-reviewer — 22
2. codex-implementer — 11
3. Explore — 9
4. ...

**Workflow signal:** Codex agents fired (Phase 2 working). gemini-frontend rare; ok if frontend work was rare.

### ADR adherence
| ADR | Status | Note |
|---|---|---|
| 0010 | in-force | commit-gate.sh present, mentioned in CLAUDE.md |
| 0012 | **drifted** | Context7 MCP mentioned but not in settings.json |
| ... | | |

### auto-memory
- Entries: 7 / index: 9 lines (healthy)

### Recommendations
- [ ] Run `/context-budget` — last run never / >30d ago
- [ ] Run `/retro 7d` — no recent retro found
- [ ] Investigate ADR-0012 drift
- [ ] Consider removing dead skill: m-foo
```

## Specialist audit dispatch (`--full` mode)

After the composite report, offer to chain into:
- **`/retro`** — commit-driven engineering retro (gstack) — velocity, test
  health, plan completion
- **`/context-budget`** — token consumption across agents/skills/rules (ECC)
- **`/skill-stocktake`** — skill quality checklist (ECC) — full review of
  `~/.claude/skills/` custom skills
- **`/cso`** — infrastructure-first security audit (gstack) — if
  security-sensitive work happened recently

Present via AskUserQuestion which to run (or "skip").

## Frequency

| Cadence | Action |
|---|---|
| Weekly | `/m-harness-audit` (7d) — skill usage + hooks |
| Monthly | `/m-harness-audit 30d --full` — + ADR sweep + specialist dispatch |
| Quarterly | Manual: walk the 6-stage workflow end-to-end on a throwaway feature, note friction |

## Related

- Upstream signals: Claude Code session JSONL, gstack analytics, ECC instincts
- Specialist audits: `/retro`, `/context-budget`, `/skill-stocktake`, `/cso`
- ADR home: `claude_code_config/docs/adr/`
- Auto-memory: `~/.claude/projects/<project>/memory/`

## What this skill is NOT

- Not a telemetry capture layer — it reads what's already logged
- Not a replacement for `/retro` or `/skill-stocktake` — those are the deep
  dives; this skill is the triage that routes to them
- Not a hook enforcer — surfaces signals, doesn't auto-fix
