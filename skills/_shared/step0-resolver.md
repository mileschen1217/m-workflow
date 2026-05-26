# Step-0 Resolver (shared, single home)

Canonical Step-0 for every m-workflow reader skill. Callers invoke
it with the pinned phrase; they do NOT inline its logic.

## 1. Read config

Read `${CLAUDE_PROJECT_DIR}/.claude/m-workflow.yaml`.

- **Absent** → no config; use `workspace_root = .m-workflow`
  (default) and `disciplines = []`. Continue. (But first check
  migration detection §3 — a stale plugin `.swarm/` with no yaml
  is an old-config case.)
- **Present but malformed (parse error)** → print the filename
  and the parse-error location; do NOT enter migration; do NOT
  continue with defaults; exit non-zero.
- **Present + parseable** → continue.

## 2. Derive the path bundle (7 fields)

Let `W = workspace_root` (the parsed value, or `.m-workflow` when
the key is absent). Derive:

    bundle.specs       = W/specs
    bundle.adr         = W/docs/adr
    bundle.epics       = W/epics
    bundle.plans       = W/plans
    bundle.archive     = W/archive/specs
    bundle.research    = W/research
    bundle.disciplines = <adopted_disciplines list or []>

Always return all seven fields. Do NOT branch on which caller
invoked the resolver — every caller gets the same bundle.

## 3. Old-config detection → propose → confirm → execute

Old config is present when EITHER the parsed yaml has
`schema_version: 1` or any legacy key (`specs_dir`, `adr_dir`,
`epics_dir`, `plans_dir`, `archive_specs_dir`, `discovery_dir`,
`created_by_plugin_version`, `template`, `lenses`, `matrix`, or a
`workspace_root` of `.swarm`), OR — when the yaml is absent — a
stale plugin `.swarm/` with recognizable substructure (e.g.
`.swarm/epics/`, `.swarm/specs/`, `.swarm/docs/adr/`) sits at the
project root.

On detection: do NOT proceed silently and do NOT auto-migrate.
Determine the steps needed — typically back up the existing yaml
(if any), move `.swarm/` → `.m-workflow/`, and rewrite the yaml
to schema 2 preserving `adopted_disciplines` — PRESENT the
concrete proposed steps to the user, and execute ONLY on explicit
confirmation. On decline, abort with no destructive action.
Resolve edge cases (target dir already exists, a prior partial
migration) by judgment and surface them in the proposal for the
human to decide. This is a one-time, single-consumer operation;
the human gate, not a state machine, owns correctness.
