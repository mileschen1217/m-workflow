---
name: code-review
description: |
  Code review with caller-declared mode. Default: per-commit (Pattern C — generic Sonnet reviewer in parallel with language/security/database specialists, all in fresh context). `batch` mode: logical commit group (Pattern B — vendor-not-builder reviews; default = Codex reviews when CC builds). Mode is explicit via `batch` keyword; no commit-count heuristic. Renamed from `m-patch-review`.
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
  - Agent
user-invocable: true
kind: workflow
---

# /m-workflow:code-review — Code Review (Patterns C and B)

<!-- keep-long: 243 lines, all main-path (mode routing + dispatch contract read every invocation). Progressive-disclosure extraction would force a per-call references load with zero token saving; held inline by design. -->

Parallel reviewers in separate contexts. Fast quality check before commit.

Dispatches:
- **Always:** generic Sonnet reviewer (primary)
- **Conditional:** language-specific reviewer(s) based on changed-file languages
- **Conditional (AI-judged):** `security-reviewer` if the diff touches security-sensitive code; `database-reviewer` if the diff touches DB/SQL/schema

## Usage

```
/m-workflow:code-review                          # default: HEAD commit, Pattern C
/m-workflow:code-review <commit-ish>             # named single commit, Pattern C
/m-workflow:code-review batch                    # logical group (default range: <main>..HEAD), Pattern B
/m-workflow:code-review batch <range>            # explicit logical group, Pattern B

/m-workflow:code-review with codex               # Pattern C; codex-reviewer replaces generic Sonnet
/m-workflow:code-review with cc                  # Pattern C; explicit (no-op — Sonnet is the default)
/m-workflow:code-review batch with cc            # Pattern B; force CC reviewer regardless of builder
/m-workflow:code-review batch with codex         # Pattern B; force Codex reviewer regardless of builder
/m-workflow:code-review solo                     # Pattern C; primary reviewer only — skip language/security/DB specialists
/m-workflow:code-review solo with codex          # Pattern C; codex-reviewer alone, no specialists
```

The `batch` keyword is the explicit Pattern B trigger. Without it, even a multi-commit range invocation defaults to Pattern C applied per-commit.

The `with <vendor>` modifier overrides reviewer routing. Recognized vendors: `codex`, `cc`. The modifier is parsed after `batch` (if present) and after the commit-ish/range. Unrecognized values fail loudly: "unknown vendor in `with` modifier — expected `codex` or `cc`".

The `solo` modifier disables the parallel specialist fan-out (language reviewer, security-reviewer, database-reviewer). Useful when the diff is small / single-purpose and specialists would be noise. Pattern B already implies solo (single reviewer); `solo` on Pattern B is a no-op.

## Argument parsing

Parse the args string left-to-right:
1. If first token is `batch` → `mode = batch`, advance.
2. Next token, if not `with` / `solo`, is treated as commit-ish (Pattern C) or range (Pattern B).
3. If `solo` appears anywhere → `solo = true` (disables specialist fan-out).
4. If `with <vendor>` appears, set `force_reviewer = <vendor>`. Validate against {`codex`, `cc`}; fail loudly otherwise.

## Batch Mode (Pattern B)

When invoked with `batch` keyword, route to Pattern B — vendor-not-builder reviews.

Provenance (schema, the 5 operations, both banner formats) is defined solely in
`skills/cross-provider-reviewer/references/provenance.md`.

### Procedure

1. Resolve the commit range:
   - `/m-workflow:code-review batch <range>` → use `<range>`
   - `/m-workflow:code-review batch` → default `$(git merge-base HEAD main)..HEAD` (or `master`; project CLAUDE.md may override)
2. Detect builder (skipped if `force_reviewer` is set):
   - Scan commit-message trailers in the range:
     ```
     git log --format=%B <range> | grep -iE '^Co-Authored-By:.*(codex|gpt-?5|openai)'
     ```
   - If any commit has a Codex-flavored `Co-Authored-By:` trailer → `builder = codex`
   - Otherwise → `builder = cc` (harness default — covers both Claude-tagged and untagged commits, since this skill runs inside Claude Code)
   - **Log the detection result so the user can spot misclassification:**
     - "Builder detection: N/M commits tagged Codex → builder = codex; reviewer swap = CC"
     - "Builder detection: no Codex trailers in M commits → builder = cc (default); reviewer swap = Codex"
   - Detection requires commit-message hygiene. If a Codex agent built code without tagging commits, the swap will misroute. Override with `batch with cc` in that case.
3. Determine reviewer:
   - If `force_reviewer = codex` → reviewer = `codex-reviewer`
   - If `force_reviewer = cc` → reviewer = `everything-claude-code:code-reviewer`
   - Else cross-vendor swap based on detected builder:
     - `builder = cc` → reviewer = `codex-reviewer`
     - `builder = codex` → reviewer = `everything-claude-code:code-reviewer`
4. Dispatch the resolved reviewer:
   - `codex-reviewer` → `Agent(subagent_type: "m-workflow:codex-reviewer", description: "Codex batch review", prompt: { task: <full diff>, role: "batch-reviewer", task_dir: <optional> })`
   - `everything-claude-code:code-reviewer` → corresponding Agent dispatch  <!-- # EXTERNAL DEP — everything-claude-code (Epic B vendors this) -->
5. Single reviewer; no parallel dispatch in Pattern B.
   **Normative fallback (M3):** if the swapped reviewer (e.g. `m-workflow:codex-reviewer`)
   returns `status: failed` / a `fallback_reason` (codex unavailable), fall back to the
   builder's OWN vendor (`everything-claude-code:code-reviewer` when builder=cc) and let
   it produce the verdict. If BOTH the swap target and the builder-vendor fallback fail →
   `status: failed`, `providers_used == []`, no banner.
   **No pre-probe (L2):** do not add a `codex --version` pre-probe here — rely on the
   `m-workflow:codex-reviewer` agent's own `status: failed` / `fallback_reason` as the
   codex-availability signal.
6. Compute provenance + banners per `skills/cross-provider-reviewer/references/provenance.md`
   (sole canonical home — use the FULL plugin-relative path; a bare `references/provenance.md`
   would wrongly resolve under `skills/code-review/references/`, which does not exist):
   - `builder_vendor` = detected builder (`"cc"`/`"codex"`); `providers_used` = `[<the vendor that actually reviewed>]`.
   - `providers_expected` = `["<opposite-of-builder>"]` for a swap, or `["X"]` with `force_reviewer = true` when invoked `with X`.
   - Extract `session_id` from `raw_codex.jsonl` if codex ran (per that reference).
   - Compute degraded (Operations 1–4) + partial (Operation 5); prepend banner(s) to the verdict text and to `<task_dir>/review.md` (when `task_dir` given).
   - Write `<task_dir>/review.result.json` (review-envelope/v1; derived fields never written).
7. Surface findings; Critical / High block merge.
8. **Informed-consent checkpoint (CONSENT-3):** if the verdict carries a ⚠️ DEGRADED or
   ⚠️ PARTIAL banner, present the banner to the user and obtain explicit acknowledgement
   (an `AskUserQuestion` choice or an explicit user "proceed") BEFORE reporting the batch
   as ready to proceed/commit. This is orthogonal to the C+H block — it applies even at
   C+H == 0. A clean (no-banner) review does NOT trigger this checkpoint.

### Why Pattern B not Pattern A here

Per-batch volume is high enough that Pattern A's 2× cost is not justified. Cross-vendor diversity is preserved via the swap. High-leverage Pattern A is reserved for `/m-workflow:design-review` (Stage 0) and `/m-workflow:arch-review` / `/m-workflow:design-spec`.

## Dependencies

- `everything-claude-code:code-reviewer` + language/security/database reviewers (ECC, EXTERNAL) — Epic B vendors or makes optional.
- `m-workflow:codex-reviewer` (plugin-local) — Pattern B cross-vendor reviewer when CC builds.

Language-specific, security, and database reviewers require the
`everything-claude-code` plugin (ECC). CC-only fallback: if ECC is not
installed, the skill runs with the generic Sonnet reviewer only and logs a note
about the missing dependency.

## Process

### Step 1: Determine diff path

1. If argument provided → use that path directly
2. If project CLAUDE.md defines a diff path → use it (e.g., `dl/` for buildroot)
3. Default: `git diff HEAD`

**If `solo = true`,** skip Step 2 entirely — go straight to Step 3 with the primary reviewer alone (Sonnet, or codex-reviewer if `force_reviewer = codex`). No language reviewer, no security/DB specialists.

### Step 2: Detect languages + domain concerns

Inspect changed file paths from `git diff --name-only HEAD -- {path}`.

**Language mapping** (primary file extension → reviewer agent):
- `.py` → `everything-claude-code:python-reviewer`
- `.rs` → `everything-claude-code:rust-reviewer`
- `.go` → `everything-claude-code:go-reviewer`
- `.ts`, `.tsx`, `.js`, `.jsx` → `everything-claude-code:typescript-reviewer`
- `.java` → `everything-claude-code:java-reviewer`
- `.kt`, `.kts` → `everything-claude-code:kotlin-reviewer`
- `.cpp`, `.cc`, `.cxx`, `.hpp`, `.h`, `.c` → `everything-claude-code:cpp-reviewer`
- `.dart` → `everything-claude-code:flutter-reviewer`
- Other → skip language reviewer

If multiple languages detected, dispatch one reviewer per distinct language.
Skip languages with <10 lines changed (noise threshold).

**Domain-concern judgment (AI, not regex):**

Read the diff briefly. Dispatch the specialist only if the diff *meaningfully*
touches the domain — not just mentions a keyword:

- `security-reviewer` — new/changed auth flows, session handling, password/token
  handling, crypto primitives, input validation at trust boundaries,
  subprocess/exec calls on user input, JWT, CORS, SSRF surface, secret handling.
- `database-reviewer` — new/changed SQL queries, migration files, schema
  definitions, ORM models/relations, transaction boundaries, prepared-statement
  patterns, index definitions.

Variable names that *contain* "user" or "auth" but operate on trusted internal
data do NOT warrant dispatch. False positives here waste agents; prefer skipping
in ambiguous cases.

### Step 3: Dispatch reviewers in parallel

Launch all reviewers in a **single message** with multiple Agent tool calls, all
with `run_in_background: true`.

**Primary reviewer:**
- If `force_reviewer = codex` → dispatch `codex-reviewer` instead of the generic Sonnet reviewer below. Pass the diff in the same envelope shape used by Pattern B (`{ task: <diff>, role: "reviewer", task_dir: <optional> }`). Specialists (language / security / DB) still dispatch in parallel per below.
- Otherwise (default, or `force_reviewer = cc`) → generic Sonnet reviewer (`model: "sonnet"`), prompt:

```
You are a code reviewer. Review the changes shown by `git diff HEAD -- {path}`.

Check for:
1. Security issues (injection, auth bypass, unsafe input handling)
2. Bugs and logic errors
3. Error handling gaps (missing error paths, swallowed errors)
4. Resource leaks (unclosed handles, missing cleanup)
5. Dead code introduced by this change

Report findings as a numbered list, each tagged [Critical], [High], [Medium], or [Low].
If no issues found, report "No issues found."
Keep it concise — this is a quick check, not a deep audit.
```

**Language reviewer(s):** dispatch one per detected language. Each gets:

```
Review the changes in {diff path} for {language}-specific issues — idioms,
type safety, best practices, performance gotchas, and language-specific
security patterns beyond generic checks.

Report findings as a numbered list tagged [Critical], [High], [Medium], or [Low].
Keep it concise.
```

**security-reviewer / database-reviewer:** dispatched only when AI judgment in
Step 2 flagged the concern. Default prompts from those agents' definitions apply.

**If ECC is not installed**, log "ECC plugin not installed — language-specific
reviewers skipped" and proceed with generic only.

**For specific-file invocation** (`/m-workflow:code-review path/to/file`):

Still detect language from the file extension. Dispatch generic reviewer with
the specific-file prompt:

```
You are a reviewer. Read `{file_path}` and review it.

For code: check security, bugs, error handling, resource leaks, dead code.
For docs: check accuracy, completeness, internal consistency, broken references.

Report findings as a numbered list, each tagged [Critical], [High], [Medium], or [Low].
If no issues found, report "No issues found."
Keep it concise.
```

Also dispatch the matching language reviewer if ECC is available. Skip domain
reviewers unless the file clearly falls in the security/DB domain.

### Step 4: Aggregate findings

Wait for **all** reviewers to complete. Merge findings into one table,
deduplicating overlaps. If reviewers disagree on severity, use the higher one.
Mark which reviewer(s) found each issue for traceability.

### Step 5: Apply fixes

1. **Critical/High** — fix immediately, no asking
2. **Medium** — note in report, do not fix (save for batch review)
3. **Low** — AI judgment: if the fix is trivial (≤2 lines, no architectural
   change), fix inline; otherwise note and defer. No ledger — don't track
   deferred Lows across commits.

### Step 6: Report

```markdown
## Patch Review: {target}

**Reviewers dispatched:** generic Sonnet, {language}-reviewer{, security-reviewer}{, database-reviewer}

| # | Issue | Severity | Source | Action |
|---|---|---|---|---|
| 1 | ... | Critical | Sonnet + python-reviewer | Fixed: ... |
| 2 | ... | High | security-reviewer | Fixed: ... |
| 3 | ... | Low | python-reviewer | Fixed inline (trivial) |
| 4 | ... | Medium | Sonnet | Deferred to /m-workflow:code-review batch |

Ready to commit: {yes/no}
```

## Key Rules

- **Always spawn separate agents** — never review inline
- Generic reviewer model: **Sonnet**; language/security/DB reviewers use their
  own definition defaults (Sonnet per ECC convention)
- Dispatch all reviewers **in parallel** (single message, multiple Agent calls,
  `run_in_background: true`)
- **AI judgment, not regex**, for security/DB dispatch — prefer skipping in
  ambiguous cases to avoid agent-spawn noise
- Fix only Critical/High by default. Low fixable inline if trivial.
  Medium deferred to `/m-workflow:code-review batch`.
- No re-review loop — scope is too small to justify (that's `/m-workflow:code-review batch`'s job)
- Project CLAUDE.md may override the diff path
