# Extraction Policy

This document defines the rules for extracting reusable knowledge from project
research docs. The skill reads this file at runtime and follows it as instruction.

## Reusability Test

> "If this project were deleted tomorrow, would this knowledge still be valuable
> to someone starting a similar effort?"

- Yes → extract
- Partially → extract only the reusable parts, drop the project-specific framing
- No → skip (mark with durable SKIP entry)

## What to Extract

- Technology evaluations and comparisons (framework X vs Y, with benchmarks)
- Architecture patterns with rationale (why this design, what trade-offs)
- Domain knowledge (financial metrics, video production, mobile dev, etc.)
- Tool/API research (capabilities, limitations, rate limits, gotchas)
- Best practices and anti-patterns learned from implementation
- Data source evaluations (APIs, feeds, endpoints, reliability, pricing)

## What to Skip

- Project-specific implementation details (phase plans, config values, sprint specs)
- Internal file paths, variable names, class names specific to one codebase
- Status updates, roadmap items, progress tracking
- Project-specific user guides and setup instructions
- Content that merely restates official documentation without adding
  project-learned gotchas, benchmarks, or evaluation context

## Extraction Quality

- **Preserve source language** — zh-TW stays zh-TW, English stays English
- **Distill, don't copy** — restructure for standalone readability.
  Remove project phase references, sprint numbers, internal milestones.
- **Preserve concrete data** — numbers, benchmarks, API endpoints, rate limits
  are the most valuable parts. Keep them even if they overlap with official docs,
  because they represent verified, project-tested facts.
- **Separate facts from opinions** — use clear attribution for subjective
  assessments (e.g., "In our testing, X outperformed Y by 30%" not just "X is better").
- **Add a Sources section** — include source project label, original doc path,
  and any external references mentioned in the source doc.

## Routing Logic

Given a list of destination descriptions from config:

1. Match content topics against each destination's description
2. If the content clearly fits one destination → route there
3. If ambiguous or could fit multiple → route to the default destination
   and add an uncertainty callout at the top of the note (see below)
4. If content doesn't fit any destination → skip, flag in report

Routing is your judgment based on destination descriptions. Log a one-line
rationale for each routing decision in the report.

### Uncertain Routing Callout

When routing to the default destination because the content is ambiguous,
add this callout immediately after the frontmatter:

```markdown
> [!info] Auto-extracted from project/<source-label>
> Routing uncertain — this note may belong in a different vault. Review during weekly check.
```

Do NOT add this callout when routing is confident (clear match to a destination).

## Dedup and Merge Rules

Before creating a new note, search the target destination for existing notes
with overlapping topics:

1. Glob for key terms from the proposed note title (e.g., `*Evaluation*`, `*Framework*`)
2. Check frontmatter `tags` and `summary` of candidate matches

Decision:
- **Strong match** (same core topic, same scope) → merge into existing note
- **Partial overlap** (related but different scope) → create new note,
  add bidirectional Related links. Read the existing note first before adding links.
- **No match** → create new note
- **When uncertain** → prefer new note over merge (safer)

**Never merge into `type: project` notes.** Project notes track work lifecycle,
not reusable knowledge. Create a standalone knowledge note and add a Related
link to the project note instead.

### Merge Rules

When merging into an existing note:
- **Read the existing note first** (mandatory)
- Preserve all existing frontmatter fields
- Preserve all existing wikilinks
- Do not expand the note's scope beyond its current topic
- Integrate new knowledge as new sections or enrich existing sections
- Update frontmatter `tags` only if new tags are directly relevant
- If a merge would cause the note to exceed ~500 words covering multiple
  distinct concepts, prefer creating a new note with overlap links instead

## Frontmatter Conventions

### obsidian-vault destinations

Follow the destination vault's CLAUDE.md for conventions. Minimum required:

```yaml
---
type: research
status: seedling
date: <extraction date, YYYY-MM-DD>
area: <from vault CLAUDE.md default, e.g., "learning" for ai_explosion_kb>
tags: [<inferred from content, YAML list, following vault tag taxonomy>]
source: "extracted:<source-label>"
aliases: [<acronyms, abbreviations, alternative names — omit if none>]
summary: "<one-line core claim for AI scanning>"
---
```

Field guidance:
- `area`: read default from vault CLAUDE.md. ai_explosion_kb → "learning",
  work_kb → "work", life_kb → "life".
- `tags`: must be YAML list. Follow vault's exact tag taxonomy.
- `source`: format is `extracted:<label>` (e.g., `extracted:financial`).
- `aliases`: populate from acronyms (e.g., "LLM Evaluation Frameworks" → "LLM Eval"),
  abbreviations, or alternative names in the source. Omit if none.
- `summary`: one-line core claim. Used by AI scanning and dedup.

### plain-markdown destinations

No frontmatter unless the destination has its own conventions (check for README
or style guide). Write clean markdown without Obsidian-specific syntax.

### Wikilinks (obsidian-vault only)

- Use `[[Note Name]]` for internal links
- Only link to notes verified to exist (Glob the entire vault for `<name>.md`)
- Link concepts that genuinely relate — don't over-link
- For plain-markdown destinations, use standard `[text](path)` links instead

## Overlap Handling

When dedup finds partial overlap (related but different scope):

- For obsidian-vault: add `[[Related Note]]` to both notes' Related sections
- For plain-markdown: add a markdown link in a "See also" section
- Always read the existing note first before modifying it
