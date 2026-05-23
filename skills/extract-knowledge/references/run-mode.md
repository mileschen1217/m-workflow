# Run Mode

## Config Validation

Load `<project>/.claude/extract-knowledge.yaml` and validate:

**Hard validation** (exit with error):
- YAML is parseable
- No duplicate `label` values across sources or destinations
- Exactly one destination has `default: true`
- All `destinations[].type` is `obsidian-vault` or `plain-markdown`
- At least one valid source remains (after soft checks)
- At least one valid destination remains including default (after soft checks)

**Soft validation** (warn and continue):
- Source path doesn't exist → print warning, skip this source
- Destination path unreachable → print warning, skip this destination

## Load Policy

Read `~/.claude/skills/m-extract-knowledge/policy.md` into context.
If the file is missing, print error and exit:
"Error: policy.md not found at ~/.claude/skills/m-extract-knowledge/policy.md. Re-install the skill."

## Load Vault Conventions

For each destination where `type: obsidian-vault`:
1. Read `<destination.path>/CLAUDE.md` if it exists
2. If not found, try reading the parent directory's `CLAUDE.md` (vaults inherit root conventions)
3. Extract: default `area` value, folder rules (which `type` goes where), tag taxonomy
4. Store in memory for use during extraction

## Phase 1: Scan

For each source in config:
1. Glob `<source.path>/**/*.md`
2. For each file, read the YAML frontmatter only (first `---` to second `---`)
3. Check the `extracted_to` field:
   - **Has `extracted_to` with `target: "SKIP"`:**
     - Compute current body hash (see Body Hash section below)
     - If body hash matches `body_hash` in the SKIP entry → skip (still not reusable)
     - If body hash differs → re-evaluate (content changed, might be reusable now)
   - **Has `extracted_to` with real targets:**
     - Compute current body hash
     - If body hash matches any `body_hash` in ledger → skip (already extracted, unchanged)
     - If body hash differs → flag for re-extraction (content changed)
   - **No `extracted_to` field:** → collect as new candidate
4. Print scan summary:
   ```
   Scanning 5 sources...
     financial        → 6 candidates (14 files, 8 extracted)
     deadline-capture → 4 candidates (11 files, 7 extracted)
     ...
   Found 20 candidates (18 new, 2 stale)
   ```

If 0 candidates found, print "Nothing to extract." and exit.

### Body Hash Computation

The body hash is used for staleness detection. It hashes the file body **excluding YAML frontmatter** to prevent self-invalidation (writing the hash into frontmatter would change the hash).

Compute via Bash:

```bash
# Strip YAML frontmatter (first --- to second ---), then SHA-256 the body
sed '1{/^---$/!q;};1,/^---$/d' "<file>" | shasum -a 256 | cut -c1-8
```

If the file has no frontmatter (no leading `---`), hash the entire file:
```bash
shasum -a 256 "<file>" | cut -c1-8
```

## Phase 2: Extract

Process candidates sequentially. For each candidate:

### Step 2.1: Read Full Content

Read the entire source file (not just frontmatter).

### Step 2.2: Judge Reusability

Apply the policy.md reusability test. Ask:
> "If this project were deleted tomorrow, would this knowledge still be valuable?"

- **Not reusable** → record as SKIP in results. Will be marked with durable SKIP entry in Phase 4.
- **Partially reusable** → proceed, extracting only the reusable parts.
- **Fully reusable** → proceed with full extraction.

### Step 2.3: Route to Destination

Read destination descriptions from config. Match the source content's topics against each description.

- Clear fit for one destination → route there
- Ambiguous → route to the default destination
- Fits no destination → record as SKIP

Record a one-line routing rationale for the report.

### Step 2.4: Dedup Check

Search the target destination for existing notes with overlapping topics:

1. Extract 2-3 key terms from the proposed note title
2. Glob the destination for files matching `*<term>*` patterns
3. For each candidate match, read its frontmatter `tags` and `summary`
4. Decide:
   - **Strong match** → MERGE action
   - **Partial overlap** → NEW action with overlap links
   - **No match** → NEW action

### Step 2.5: Write or Merge

**For NEW notes in obsidian-vault destinations:**

1. Determine target folder from vault conventions (e.g., `type: research` → vault root)
2. Write the note with:
   - Frontmatter following vault conventions (see policy.md Frontmatter section)
   - Distilled content (not a copy — restructured for standalone readability)
   - `## Sources` section with provenance
   - `## Related` section with wikilinks to verified existing notes
3. Verify all wikilink targets exist: `ls "<vault>/<target>.md"` for each

**For NEW notes in plain-markdown destinations:**

1. Write to destination root
2. No frontmatter (unless destination has conventions)
3. Standard markdown links, no Obsidian syntax
4. `## Sources` section with provenance

**For MERGE into existing notes:**

1. Read the existing note (mandatory)
2. Integrate new knowledge:
   - Add new sections where appropriate
   - Enrich existing sections with new data
   - Preserve all existing frontmatter, wikilinks, and structure
   - Do not expand the note's scope
   - Add new tags only if directly relevant
3. If merge would exceed ~500 words on multiple concepts → switch to NEW with overlap links

**For partial OVERLAP:**

1. Create new note (as per NEW above)
2. Read the overlapping existing note
3. Add bidirectional Related links:
   - obsidian-vault: add `[[New Note]]` to existing note's Related section
   - plain-markdown: add markdown link in "See also" section

### Step 2.6: Collect Results

For each candidate, store the result (do NOT mark source yet):
- Source file path
- Action taken: NEW, MERGED, OVERLAP, SKIP
- Destination path and note name (if applicable)
- Routing rationale (one line)
- Skip reason (if SKIP)

## Phase 3: Report

Write the extraction report to `<project>/<reports_dir>/YYYY-MM-DD-HHMMSS-extraction-report.md`.

Generate the timestamp via Bash:
```bash
date "+%Y-%m-%d-%H%M%S"
```

Report format:

```markdown
# Extraction Report — <YYYY-MM-DD HH:MM:SS>

**Config:** .claude/extract-knowledge.yaml
**Sources scanned:** <N> (<M> files total)

## Extractions

| # | Source | Action | Destination | Rationale |
|---|--------|--------|-------------|-----------|
| 1 | <label>: <filename> | NEW | <dest>/<note name> | <one-line rationale> |
| 2 | <label>: <filename> | MERGED | <dest>/<note name> | <rationale> |

## Skipped

| Source | Reason |
|--------|--------|
| <label>: <filename> | <reason> |

## Warnings

| Source | Warning |
|--------|---------|
| <label>: <filename> | <warning, e.g., "source not marked — invalid YAML"> |

## Summary

- New notes: <N>
- Merged into existing: <N>
- Re-extracted (stale): <N>
- Skipped: <N>
- Overlaps noted: <N>
```

## Phase 4: Mark Sources

After the report is successfully written, mark each processed source doc.

For each extraction result (NEW, MERGED, OVERLAP — not SKIP-because-no-destination):

1. Read the source file
2. Compute the current body hash:
   ```bash
   sed '1{/^---$/!q;};1,/^---$/d' "<file>" | shasum -a 256 | cut -c1-8
   ```
3. Add or update the `extracted_to` ledger entry in frontmatter:
   ```yaml
   extracted_to:
     - target: "<note name>"
       destination: <destination label>
       body_hash: "<8-char hash>"
       date: "<ISO-8601 datetime with timezone>"
   ```
4. If the source has no frontmatter, prepend:
   ```
   ---
   extracted_to:
     - target: "..."
       ...
   ---
   ```
   Preserve the first heading and all existing content.
5. If the source has invalid YAML frontmatter, do NOT modify it. Log a warning.

For each SKIP result:

1. Add a durable skip entry:
   ```yaml
   extracted_to:
     - target: "SKIP"
       destination: "none"
       body_hash: "<8-char hash>"
       reason: "<why it was skipped>"
       date: "<ISO-8601 datetime>"
   ```

**Error recovery:** If any marking fails (write error, permission issue),
log the failure and continue marking remaining sources. After all marking
attempts, append a "Marking Failures" section to the already-written report.

## Terminal Summary

Print:
```
Done: <N> new notes, <M> merged, <S> skipped, <R> re-extracted.
Report: <path to report>
```

If there were marking failures, also print:
```
Warning: <N> sources could not be marked. See report for details.
```

## Staleness Handling

When Phase 1 flags a source for re-extraction (body hash changed since last extraction):

1. Read the source doc fully
2. Re-extract following the same Phase 2 rules (judge, route, dedup)
3. Look up the existing destination note:
   - Read `target` from the source's extraction ledger
   - Glob the destination for `<target>.md`
   - If found → read it, then re-extract from scratch (do not diff — source docs
     and distilled notes are intentionally different forms)
   - If not found (renamed/moved) → treat as a new extraction
4. If re-extraction produces significantly different content → create new note
   with overlap links to the old one rather than silently replacing
5. Update the ledger entry with new body_hash and date

This applies to both obsidian-vault and plain-markdown destinations.
