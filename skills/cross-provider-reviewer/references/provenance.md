# Dispatch provenance — canonical reference

Sole canonical home of the `review-envelope/v1` contract (per E14 spec §C2 and
CONTEXT.md § Dispatch provenance "canonical contract: provenance.md wins").
The `cross-provider-reviewer`, `cross-provider-architect`, and `code-review`
skill bodies, and the `codex-reviewer` / `codex-adversarial-reviewer` agents,
POINT here and never restate any of the below.

## review-envelope/v1 schema

On-disk filename: `review.result.json` (never bare `result.json` — that is the
separate task-result artifact). All fields top-level.

| Field | Type | Required | Writer | Notes |
|---|---|---|---|---|
| `schema` | string | yes | both paths | Literal `"review-envelope/v1"` |
| `status` | string | yes | both paths | One of `"ok"`, `"partial"`, `"failed"` |
| `role` | string | yes | both paths | `"reviewer"` or `"adversarial-reviewer"` |
| `providers_expected` | string[] | yes | both paths | Intended set. Pattern A default `["cc","codex"]`; Pattern B swap = single opposite-of-builder vendor; `with X` = `["X"]`. Never empty — populated even on total failure. |
| `providers_used` | string[] | yes | both paths | Who produced content. `[]` on total failure. Values `"cc"`, `"codex"`. |
| `builder_vendor` | string or null | conditional | Pattern B body | Pattern B only: vendor that built the code (`"cc"`/`"codex"`). Null/absent for Pattern A. |
| `session_id` | string or null | no | composite / code-review body (NOT the thin agent) | Codex session id from `raw_codex.jsonl`. Null if codex absent or id not found. |
| `fallback_reason` | string or null | no | both paths | Why a provider was absent. Null when all expected ran. |
| `risks` | object[] | no | both paths | `{ "provider": string, "error": string }` each. Present on partial/failed. |
| `timestamp_utc` | string | yes | both paths | ISO 8601 UTC write time, e.g. `"2026-05-25T14:23:00Z"`. |

## No-derived-fields negative list

`review.result.json` MUST NOT contain any of: `quantity_ok`, `quantity_correct`,
`vendor_ok`, `vendor_correct`, `degraded`. These are derived at read/banner time,
never stored.

## Operations (computed at read/banner time)

`force_reviewer` is a runtime parameter, never a stored field: set true by the
writer when a `with X` modifier governed the invocation (code-review batch, or a
`with X` passed through a Pattern A envelope); default false.

**Operation 1 — compute_quantity_correct(providers_expected, providers_used) → bool**
- true iff `len(providers_used) == len(providers_expected)` AND `len(providers_used) > 0`.

**Operation 2 — compute_vendor_correct(providers_expected, providers_used, builder_vendor, force_reviewer) → bool**
- If `providers_used` empty → false.
- Else if `force_reviewer` → true.
- Else if `builder_vendor` non-null (Pattern B) → true iff `providers_used[0] != builder_vendor`.
- Else (Pattern A) → true iff `providers_used` has ≥2 distinct vendors.
- Pattern B precondition: exactly one reviewer, so `len(providers_used)` is 0 or 1; >1 is an implementation error.

**Operation 3 — compute_degraded(quantity_correct, vendor_correct, providers_used) → bool**
- true iff `(!quantity_correct || !vendor_correct)` AND `len(providers_used) > 0`.
- Non-empty guard: total failure (`providers_used == []`) is `status: failed`, NOT degraded.

**Operation 4 — format_banner(quantity_correct, vendor_correct, providers_expected, providers_used, builder_vendor) → string**
- Called only when `compute_degraded == true`. Output: `⚠️ DEGRADED — <reason-clause>`.
- `<reason-clause>`:
  - if `!quantity_correct`: `"quantity: {len(providers_used)} of {len(providers_expected)} expected providers"`
  - if both `!quantity_correct` and `!vendor_correct`: join with `"; "`
  - if `!vendor_correct` and `builder_vendor` non-null (Pattern B): `"vendor: builder={builder_vendor} and reviewer={providers_used[0]}; cross-vendor swap failed"`
  - if `!vendor_correct` and `builder_vendor` null (Pattern A): `"vendor: cross-vendor scrutiny incomplete: only {join(providers_used, ", ")} ran"`
- Examples:
  - `⚠️ DEGRADED — quantity: 1 of 2 expected providers; vendor: cross-vendor scrutiny incomplete: only cc ran`
  - `⚠️ DEGRADED — vendor: builder=cc and reviewer=cc; cross-vendor swap failed`
- Prepended (not appended) to synthesis text and review.md, then a blank line, then the body.

**Operation 5 — format_partial_banner(status, providers_used, partial_reasons) → string or null**
- If `status != "partial"` → null.
- Else for each provider in `partial_reasons` that is also in `providers_used`, emit one line:
  `⚠️ PARTIAL — <provider> contribution unreliable: <reason>`
- Example: `⚠️ PARTIAL — codex contribution unreliable: >5 malformed JSONL lines`.
- Ordering when both fire: DEGRADED first, PARTIAL second, blank line, body. PARTIAL is orthogonal to DEGRADED.

## status vs the two banner axes

- `status` (stored): was content produced — ok / partial / failed.
- DEGRADED (derived): cross-vendor completeness (quantity + vendor).
- PARTIAL (derived): content quality (a provider ran but output unreliable; `status==partial`).
- A degraded review that still produced output is `status: ok`. Both banners can co-occur.

## session_id extraction (from raw_codex.jsonl)

The composite / code-review body (NOT the thin agent) reads `<task_dir>/raw_codex.jsonl`
after the codex agent completes and extracts the session id into `review.result.json.session_id`.

Field path: the `thread.started` event's `thread_id` key (codex-cli 0.128.0, confirmed 2026-05-26).
Extraction: `jq -rR 'fromjson? | select(.type=="thread.started") | .thread_id // empty' raw_codex.jsonl | head -1`
(empty → `session_id = null`).

Note: use per-line `fromjson?` (not a plain `jq select`) — `raw_codex.jsonl` can contain a
non-JSON stderr banner line (`Reading additional input from stdin...`) because the agent
dispatches `codex exec … 2>&1`; a plain `jq` parse aborts on that line, `fromjson?` skips it.
