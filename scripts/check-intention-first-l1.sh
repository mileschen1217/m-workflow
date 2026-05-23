#!/usr/bin/env bash
# Layer-1 deterministic gate for the intention-first Baseline epic.
# Verifies the four shipped artifacts against the spec's structural ACs
# (AC-5 template half, AC-6, AC-7 local-conditional, AC-11).
#
# Semantics (spec § "Executable-check semantics"): every check compares the
# PRINTED COUNT to its expected number — NOT grep's exit status (grep -c
# exits 1 when the count is 0, which would invert absence checks). We use
# set -uo pipefail (NOT -e) and helper assertions; the script exits with the
# number of failed checks (0 = all green).
set -uo pipefail
cd "$(dirname "$0")/.."   # repo root

fail=0
expect_count() {            # expect_count <want> <cmd...>
  local want="$1"; shift
  local got; got="$("$@" 2>/dev/null | tr -d '[:space:]')"
  if [ "$got" != "$want" ]; then echo "FAIL count want=$want got=$got: $*"; fail=$((fail+1)); fi
}
expect_no_output() {        # expect_no_output <cmd...>
  local out; out="$("$@" 2>/dev/null)"
  if [ -n "$out" ]; then echo "FAIL expected-no-output: $*"; echo "$out"; fail=$((fail+1)); fi
}
expect_absent() {           # expect_absent <grep-cmd...>  (must match nothing)
  if "$@" >/dev/null 2>&1; then echo "FAIL expected-absent: $*"; fail=$((fail+1)); fi
}

# ── AC-6 — legacy four-question absence across the four artifacts ──────────
expect_absent grep -REn \
  -e 'four answers' \
  -e 'Fix vs\. workaround' \
  -e 'Smallest change' \
  -e 'Fix the system, or work around' \
  -e 'smallest change that achieves' \
  -e '\bQ3\b' -e '\bQ4\b' \
  skills/epic-driven-roadmap/SKILL.md \
  skills/epic-driven-roadmap/templates/epic-index.md \
  skills/design-spec/SKILL.md \
  skills/design-spec/template.md

# ── AC-7 — no internal skip-conditional inside the Step-0 regions ──────────
# First assert each Step-0 heading exists exactly once — otherwise the awk
# region below would be empty and the forbidden-conditional grep would
# print 0 and false-pass (no region = no violation counted).
expect_count 1 grep -cE '^0\. \*\*Foundation elicitation' skills/epic-driven-roadmap/SKILL.md
expect_count 1 grep -cE '^### Step 0 — Foundation elicitation' skills/design-spec/SKILL.md
expect_count 0 bash -c "set -o pipefail; awk '/^0\\. \\*\\*Foundation elicitation/{f=1} /^1\\. /{f=0} f' \
  skills/epic-driven-roadmap/SKILL.md \
  | grep -cE 'adopted_disciplines|intention-first|--skip|\\bquick\\b|if .*yaml'"
expect_count 0 bash -c "set -o pipefail; awk '/^### Step 0 — Foundation elicitation/{f=1} /^### /{if(f&&!/Step 0 — Foundation elicitation/)f=0} f' \
  skills/design-spec/SKILL.md \
  | grep -cE 'adopted_disciplines|intention-first|--skip|\\bquick\\b|if .*yaml'"

# ── AC-11 — epic-index.md template structure ──────────────────────────────
T=skills/epic-driven-roadmap/templates/epic-index.md
expect_count 1 grep -cE '^\*\*Aim:\*\*' "$T"
expect_count 1 grep -cE '^## Foundation$' "$T"
expect_count 1 grep -cF '**Intention (why):**' "$T"
expect_count 1 grep -cF '**Out of scope:**' "$T"
expect_no_output grep -nE '^\s*-\s*\*\*Out of scope:\*\*\s*\S' "$T"
expect_no_output awk '
  /^- \*\*Out of scope:\*\*/{f=1;c=0;next}
  f && /^  - /{c++; next}
  f && /^    +-/{print "GRANDCHILD:" $0}
  f && /^[^ ]/{f=0; if(c<1||c>3) print "BADCOUNT:" c}
  END{if(f && (c<1||c>3)) print "BADCOUNT:" c}
' "$T"
expect_count 0 bash -c "awk '/^## Foundation/{f=1;next} /^## /{f=0} f' '$T' | grep -cE '^[[:space:]]*-[[:space:]]*\\*\\*Aim'"
expect_count 1 grep -cE '^## Phases' "$T"
expect_count 0 grep -cF 'Fix vs. workaround' "$T"
expect_count 0 grep -cF 'Smallest change' "$T"
expect_count 0 grep -cF 'Goal (observable)' "$T"
expect_count 0 grep -cF 'In scope:' "$T"
expect_count 0 grep -cwF 'Q3' "$T"
expect_count 0 grep -cwF 'Q4' "$T"

# ── AC-11 — design-spec/template.md structure ─────────────────────────────
S=skills/design-spec/template.md
expect_count 1 grep -cE '^## Foundation$' "$S"
expect_count 1 grep -cF '**Intention (why):**' "$S"
expect_count 1 grep -cF '**Aim:**' "$S"
expect_count 1 grep -cF '**Out of scope:**' "$S"
expect_count 1 grep -cE '^## Acceptance Criteria$' "$S"
expect_count 1 bash -c "awk '/^## Foundation\$/{f=1} /^## Acceptance Criteria\$/{f=0} f' '$S' | grep -cF 'provisional direction set at Step 0'"
expect_count 1 bash -c "awk '/^## Foundation\$/{f=1} /^## Acceptance Criteria\$/{f=0} f' '$S' | grep -cF 'silently inherited'"
expect_no_output grep -nE '^\s*-\s*\*\*Out of scope:\*\*\s*\S' "$S"
expect_no_output awk '
  /^- \*\*Out of scope:\*\*/{f=1;c=0;next}
  f && /^  - /{c++; next}
  f && /^    +-/{print "GRANDCHILD:" $0}
  f && /^[^ ]/{f=0; if(c<1||c>3) print "BADCOUNT:" c}
  END{if(f && (c<1||c>3)) print "BADCOUNT:" c}
' "$S"
expect_count 0 grep -cF 'four answers' "$S"
expect_count 0 grep -cF 'Fix vs. workaround' "$S"
expect_count 0 grep -cF 'Smallest change' "$S"
expect_count 0 grep -cF 'Fix the system, or work around' "$S"
expect_count 0 grep -cF 'smallest change that achieves' "$S"
expect_count 0 grep -cwF 'Q3' "$S"
expect_count 0 grep -cwF 'Q4' "$S"
expect_count 0 grep -cF 'Goal (observable)' "$S"
expect_count 0 grep -cF 'In scope:' "$S"
expect_count 0 grep -cF 'Non-goals:' "$S"

if [ "$fail" -eq 0 ]; then echo "ALL GREEN (Layer-1 structural checks pass)"; else echo "RED: $fail check(s) failed"; fi
exit "$fail"
