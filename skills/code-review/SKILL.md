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

# /m-code-review — Code Review (Patterns C and B)

<!-- keep-long: 243 lines, all main-path (mode routing + dispatch contract read every invocation). Progressive-disclosure extraction would force a per-call references load with zero token saving; held inline by design. -->

Parallel reviewers in separate contexts. Fast quality check before commit.

Dispatches:
- **Always:** generic Sonnet reviewer (primary)
- **Conditional:** language-specific reviewer(s) based on changed-file languages
- **Conditional (AI-judged):** `security-reviewer` if the diff touches security-sensitive code; `database-reviewer` if the diff touches DB/SQL/schema

## Usage

```
/m-code-review                          # default: HEAD commit, Pattern C
/m-code-review <commit-ish>             # named single commit, Pattern C
/m-code-review batch                    # logical group (default range: <main>..HEAD), Pattern B
/m-code-review batch <range>            # explicit logical group, Pattern B

/m-code-review with codex               # Pattern C; codex-reviewer replaces generic Sonnet
/m-code-review with cc                  # Pattern C; explicit (no-op — Sonnet is the default)
/m-code-review batch with cc            # Pattern B; force CC reviewer regardless of builder
/m-code-review batch with codex         # Pattern B; force Codex reviewer regardless of builder
/m-code-review solo                     # Pattern C; primary reviewer only — skip language/security/DB specialists
/m-code-review solo with codex          # Pattern C; codex-reviewer alone, no specialists
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

### Procedure

1. Resolve the commit range:
   - `/m-code-review batch <range>` → use `<range>`
   - `/m-code-review batch` → default `$(git merge-base HEAD main)..HEAD` (or `master`; project CLAUDE.md may override)
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
   - `everything-claude-code:code-reviewer` → corresponding Agent dispatch
5. Single reviewer; no parallel dispatch in Pattern B. Output is the single reviewer's verdict.
6. Surface findings; Critical / High block merge.

### Why Pattern B not Pattern A here

Per-batch volume is high enough that Pattern A's 2× cost is not justified. Cross-vendor diversity is preserved via the swap. High-leverage Pattern A is reserved for `/m-design-review` (Stage 0) and `/m-arch-review` / `/m-design-spec`.

## Dependencies

Language-specific, security, and database reviewers require the
`everything-claude-code` plugin (ECC). If not installed, the skill runs with
the generic reviewer only and logs a note about the missing dependency.

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

**For specific-file invocation** (`/m-code-review path/to/file`):

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
| 4 | ... | Medium | Sonnet | Deferred to /m-code-review batch |

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
  Medium deferred to `/m-code-review batch`.
- No re-review loop — scope is too small to justify (that's `/m-code-review batch`'s job)
- Project CLAUDE.md may override the diff path
