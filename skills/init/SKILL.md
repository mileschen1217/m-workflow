---
name: init
description: |
  One-time per-project setup for m-workflow plugin. Writes
  ${CLAUDE_PROJECT_DIR}/.claude/m-workflow.yaml with paths and adopted
  disciplines. Idempotent without --reset. Trigger phrases: "set up
  m-workflow", "init m-workflow", "/m-workflow:init".
kind: workflow
---

# m-workflow:init

Writes `.claude/m-workflow.yaml` in the current project, configuring paths and adopted disciplines for the m-workflow plugin's stage skills.

## Step 1 — Idempotence check

Read `${CLAUDE_PROJECT_DIR}/.claude/m-workflow.yaml`.

**If the file does not exist OR `--reset` was passed:** continue to Step 2.

**If the file exists and is unparseable (malformed YAML):** print an error naming the file and the parse error line; do NOT silently overwrite; exit non-zero.

**If the file exists, is parseable, and `--reset` was NOT passed:**

1. Print the current config (paths + adopted disciplines).

2. Check whether the `adopted_disciplines` key is present. If missing, treat it as an empty list.

3. The supported discipline today is `source-as-truth` (single-entry list; a registry-derived menu is deferred to E15). If `source-as-truth` is already in `adopted_disciplines`, print "Run /m-workflow:init --reset to overwrite." and exit 0.

4. **If `source-as-truth` is NOT yet adopted**, show the incremental-add menu:

   ```
   Current config:
     specs_dir:           .swarm/specs
     adr_dir:             .swarm/docs/adr
     epics_dir:           .swarm/epics
     plans_dir:           .swarm/plans
     archive_specs_dir:   .swarm/archive/specs
     adopted_disciplines: [] (or the current list)

   Disciplines:
     ○ source-as-truth — enables Bridge content audit + kill-on lifecycle + standing-vs-transient classification in stage skills that support it.

   Adopt source-as-truth? [Y/n]
   ```

   (Print each adopted discipline with a `✓` prefix and each not-yet-adopted one with `○`. Today only `source-as-truth` exists, so the menu shows exactly one line.)

   Accept the answer (or the `--adopt source-as-truth` flag). Merge the selection into `adopted_disciplines` **without touching paths**. Then write the updated yaml (Step 5 write logic, paths unchanged) and print the verification summary (Step 6).

5. **Non-interactive context (no TTY):** if `source-as-truth` is not yet adopted and no `--adopt` flag was passed, print:

   ```
   [m-workflow:init] Non-interactive: source-as-truth available but not adopted.
   Re-run interactively or pass --adopt source-as-truth to add.
   ```

   Then exit 0 (not an error; the existing config is valid).

**`--reset` semantics (full overwrite) are unchanged** — passing `--reset` skips all of the above and proceeds to Step 2.

## Step 2 — Collect paths

Prompt the user for each path (or accept the matching `--<dir>-name` flag if present):

| Flag | Prompt | Default |
|---|---|---|
| `--specs-dir <path>` | Where do design specs live? | `.swarm/specs` |
| `--adr-dir <path>` | Where do ADRs live? | `.swarm/docs/adr` |
| `--epics-dir <path>` | Where do epic trackers live? | `.swarm/epics` |
| `--plans-dir <path>` | Where do plans live? | `.swarm/plans` |
| `--archive-specs-dir <path>` | Where do retired specs go? | `.swarm/archive/specs` |

Values are taken verbatim. **MVP sharp edge: path escape (`../../...`) is NOT rejected.** Production hardening (reject paths outside `${CLAUDE_PROJECT_DIR}`) is deferred.

## Step 3 — Collect adopted disciplines

For each entry in the supported discipline list (currently: `source-as-truth`), prompt: "Adopt <discipline>? [Y/n]". Skip prompt if `--adopt <discipline>` was passed.

Supported disciplines (MVP):
- `source-as-truth` — enables Bridge content audit + kill-on lifecycle + standing-vs-transient classification in stage skills that support it.

## Step 4 — Create target dirs

For each collected path (`specs_dir`, `adr_dir`, `epics_dir`, `plans_dir`, `archive_specs_dir`):

```bash
mkdir -p "${CLAUDE_PROJECT_DIR}/<path>"
```

If `mkdir` fails (permission, invalid path), print error naming the path, exit non-zero.

## Step 5 — Write yaml

Write `${CLAUDE_PROJECT_DIR}/.claude/m-workflow.yaml`:

```yaml
# Written by /m-workflow:init. Hand-editable.

# Required
schema_version: 1
created_by_plugin_version: 0.1.0
specs_dir: <answer>
adr_dir: <answer>
epics_dir: <answer>
plans_dir: <answer>
archive_specs_dir: <answer>

# Optional
adopted_disciplines: [<comma-separated answers>]
```

If overwriting (`--reset` mode), first copy the existing file to `${CLAUDE_PROJECT_DIR}/.claude/m-workflow.yaml.bak`. Print "Preserved prior yaml at .bak".

## Step 6 — Verification summary

Print:

```
✓ Wrote ${CLAUDE_PROJECT_DIR}/.claude/m-workflow.yaml
  specs_dir:        <value>
  adr_dir:          <value>
  epics_dir:        <value>
  plans_dir:        <value>
  archive_specs_dir: <value>
  adopted_disciplines: [<values>]

Next: try /m-workflow:design-spec <feature-name>
```

## Argument grammar

```
/m-workflow:init                              # interactive (default)
/m-workflow:init --adopt <discipline>         # repeatable
/m-workflow:init --specs-dir <path>
/m-workflow:init --adr-dir <path>
/m-workflow:init --epics-dir <path>
/m-workflow:init --plans-dir <path>
/m-workflow:init --archive-specs-dir <path>
/m-workflow:init --reset                      # overwrite existing yaml
```
