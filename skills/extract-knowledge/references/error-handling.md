# Error Handling

| Scenario | Behavior |
|----------|----------|
| Config YAML is malformed | Print parse error with line number. Exit. |
| No valid sources after validation | "Error: no reachable source paths. Check extract-knowledge.yaml." Exit. |
| No valid destinations after validation | "Error: no reachable destination paths. Check extract-knowledge.yaml." Exit. |
| policy.md missing | "Error: policy.md not found at ~/.claude/skills/m-extract-knowledge/policy.md. Re-install the skill." Exit. |
| Source doc has no YAML frontmatter | Process content normally. When marking in Phase 4, prepend a new frontmatter block. Preserve all existing content. |
| Source doc has invalid YAML frontmatter | Process content normally. Skip marking in Phase 4 (don't corrupt the file). Flag in report as warning. |
| Destination path unreachable at runtime | Skip that destination for this run. Warn in report. Process remaining destinations. |
| Vault CLAUDE.md missing | Fall back to parent directory CLAUDE.md. If also missing, use config description only. |
| Write fails during Phase 2 (note creation) | Log error, skip this extraction, continue with next candidate. Flag in report. |
| Write fails during Phase 4 (source marking) | Log error, continue marking remaining sources. Append failure to report. |
| Body hash computation fails | Treat file as a new candidate (conservative — prefer re-processing over skipping). |
