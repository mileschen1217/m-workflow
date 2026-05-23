---
name: extract-knowledge
version: 1.0.0
description: |
  Scan project research docs, extract reusable knowledge, and write
  distilled notes to configured destinations (Obsidian vaults or plain
  markdown folders). Marks source docs as extracted. Run with
  /m-extract-knowledge, /m-extract-knowledge setup, or
  /m-extract-knowledge dry-run.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Agent
kind: workflow
---

# m-extract-knowledge

Extract reusable knowledge from project research docs into configured destinations.

## Mode Detection

Determine which mode to run based on arguments and config state:

1. If argument is `setup` → **Setup Mode** (even if config exists)
2. If argument is `dry-run` → check config exists, then **Dry-Run Mode**
3. If no argument:
   - Config at `<project>/.claude/extract-knowledge.yaml` exists → **Run Mode**
   - Config does not exist → **Setup Mode**

Where `<project>` is the current working directory.

## Procedures

Each mode is a mutually-exclusive path; load only the one Mode Detection selects.

- **Setup Mode** → [`references/setup-mode.md`](references/setup-mode.md) — interactive config (discover sources/destinations, write `extract-knowledge.yaml`).
- **Run Mode** → [`references/run-mode.md`](references/run-mode.md) — config validation, policy/vault-convention load, Phase 1 scan (incl. body-hash staleness), Phase 2 extract, Phase 3 report, Phase 4 mark, terminal summary, staleness handling.
- **Dry-Run Mode** → [`references/dry-run-mode.md`](references/dry-run-mode.md) — read-only scan + judge + route + dedup; no writes.
- **Error Handling** (any mode) → [`references/error-handling.md`](references/error-handling.md) — scenario→behavior lookup; consult when a specific failure fires.
