---
name: init
description: |
  One-time per-project setup for touchstone plugin. Writes
  ${CLAUDE_PROJECT_DIR}/.claude/touchstone.yaml with paths and adopted
  disciplines. Idempotent without --reset. Trigger phrases: "set up
  touchstone", "init touchstone", "/touchstone:init".
kind: workflow
---

# touchstone:init

Writes `.claude/touchstone.yaml` in the current project, configuring paths and adopted disciplines for the touchstone plugin's stage skills.

## Step 1 — Idempotence check

Read `${CLAUDE_PROJECT_DIR}/.claude/touchstone.yaml`.

**If the file does not exist OR `--reset` was passed:** continue to Step 2.

**If the file exists and is unparseable (malformed YAML):** print an error naming the file and the parse error line; do NOT silently overwrite; exit non-zero.

**If the file exists, is parseable, and `--reset` was NOT passed:**

1. Print the current config (paths + adopted disciplines).

2. Check whether the `adopted_disciplines` key is present. If missing, treat it as an empty list.

3. The supported discipline today is `source-as-truth` (single-entry list; a registry-derived menu is deferred to E15). If `source-as-truth` is already in `adopted_disciplines`, print "Run /touchstone:init --reset to overwrite." and exit 0.

4. **If `source-as-truth` is NOT yet adopted**, show the incremental-add menu:

   ```
   Current config:
     workspace_root:      .touchstone (or the current value)
     adopted_disciplines: [] (or the current list)

   Disciplines:
     ○ source-as-truth — enables Bridge content audit + kill-on lifecycle + standing-vs-transient classification in stage skills that support it.

   Adopt source-as-truth? [Y/n]
   ```

   (Print each adopted discipline with a `✓` prefix and each not-yet-adopted one with `○`. Today only `source-as-truth` exists, so the menu shows exactly one line.)

   Accept the answer (or the `--adopt source-as-truth` flag). Merge the selection into `adopted_disciplines` **without touching paths**. Then write the updated yaml (Step 5 write logic, paths unchanged) and print the verification summary (Step 6).

5. **Non-interactive context (no TTY):** if `source-as-truth` is not yet adopted and no `--adopt` flag was passed, print:

   ```
   [touchstone:init] Non-interactive: source-as-truth available but not adopted.
   Re-run interactively or pass --adopt source-as-truth to add.
   ```

   Then exit 0 (not an error; the existing config is valid).

**`--reset` semantics (full overwrite) are unchanged** — passing `--reset` skips all of the above and proceeds to Step 2.

## Step 2 — Collect paths

Prompt the user for the workspace root (or accept the matching flag if present):

| Flag | Prompt | Default |
|---|---|---|
| `--workspace-root <path>` | Workspace root? | `.touchstone` |

Values are taken verbatim. **MVP sharp edge: path escape (`../../...`) is NOT rejected.** Production hardening (reject paths outside `${CLAUDE_PROJECT_DIR}`) is deferred.

## Step 3 — Collect adopted disciplines

For each entry in the supported discipline list (currently: `source-as-truth`), prompt: "Adopt <discipline>? [Y/n]". Skip prompt if `--adopt <discipline>` was passed.

Supported disciplines (MVP):
- `source-as-truth` — enables Bridge content audit + kill-on lifecycle + standing-vs-transient classification in stage skills that support it.

## Step 4 — Create target dirs

Create all six derived subpaths under `workspace_root`:

```bash
mkdir -p "${CLAUDE_PROJECT_DIR}/<workspace_root>/specs"
mkdir -p "${CLAUDE_PROJECT_DIR}/<workspace_root>/docs/adr"
mkdir -p "${CLAUDE_PROJECT_DIR}/<workspace_root>/epics"
mkdir -p "${CLAUDE_PROJECT_DIR}/<workspace_root>/plans"
mkdir -p "${CLAUDE_PROJECT_DIR}/<workspace_root>/archive/specs"
mkdir -p "${CLAUDE_PROJECT_DIR}/<workspace_root>/research"
```

If `mkdir` fails (permission, invalid path), print error naming the path, exit non-zero.

## Step 5 — Write yaml

Write `${CLAUDE_PROJECT_DIR}/.claude/touchstone.yaml`:

```yaml
# written by /touchstone:init vX.Y.Z. Hand-editable.
schema_version: 2
workspace_root: <answer or .touchstone>
adopted_disciplines: [<comma-separated answers>]
```

Recognised optional keys:

- `epic_storage: <name>` (optional) — selects the storage adapter for
  `epic-driven-roadmap`. Defaults to `local-markdown`. Unknown values raise
  `AdapterNotFoundError` (exit 8) at Step 0.

If overwriting (`--reset` mode), first copy the existing file to `${CLAUDE_PROJECT_DIR}/.claude/touchstone.yaml.bak`. Print "Preserved prior yaml at .bak".

## Step 6 — Verification summary

Print:

```
✓ Wrote ${CLAUDE_PROJECT_DIR}/.claude/touchstone.yaml
  workspace_root:      <value>
  adopted_disciplines: [<values>]

Next: try /touchstone:design-spec <feature-name>
```

## Argument grammar

```
/touchstone:init                              # interactive (default)
/touchstone:init --adopt <discipline>         # repeatable
/touchstone:init --workspace-root <path>      # override workspace root (default .touchstone)
/touchstone:init --reset                      # overwrite existing yaml
/touchstone:init --migrate                    # migrate schema-1 yaml to schema-2
```

### `--migrate` behaviour

When `--migrate` is passed:

Read `${CLAUDE_PLUGIN_ROOT}/skills/_shared/step0-resolver.md`
with the Read tool and follow it exactly.

The resolver's §3 migration steps handle reading the old schema-1 keys, deriving `workspace_root`, writing the new schema-2 yaml, and printing a diff summary. Do not duplicate that logic here.
