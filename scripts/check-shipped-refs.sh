#!/usr/bin/env bash
# Clone-completeness guard (shipped-doc-hygiene P1). Flags a committed docs/ or
# skills/ file that references an UNTRACKED concrete file under the local-doc
# workspace_root — such a reference dangles in every clone.
#
# Best-effort floor (NOT complete): a flag is certainly a leak GIVEN the placeholder
# convention — concrete untracked refs into the workspace are leaks; illustrative
# examples MUST use a <placeholder>. A matched literal example is a correctly-flagged
# hygiene violation, not a false-positive. False-negatives are expected (odd path
# forms, out-of-scope dirs) — patch on sight. The fresh-context reviewer's
# grounded-claims lens is the semantic catch.
#
# Judge: git ls-files (untracked => not in clone). NOT git check-ignore (the legacy
# .swarm paths are deleted/renamed, not gitignored — check-ignore would miss them).
# Scope: committed files under docs/ + skills/ (git ls-files), so untracked local
# drafts are never scanned. Exit: 0 pass | 1 leak(s) | 2 operational error.
set -uo pipefail

git rev-parse --is-inside-work-tree >/dev/null 2>&1 \
  || { echo "ERROR: not inside a git work tree (cannot judge tracked-state)" >&2; exit 2; }

ws=".m-workflow"
cfg=".claude/m-workflow.yaml"
if [ -f "$cfg" ]; then
  v="$(awk -F: '/^workspace_root:/{gsub(/[[:space:]]/,"",$2); print $2}' "$cfg")"
  [ -n "$v" ] && ws="$v"
fi
# escape the workspace_root for use in an ERE
ws_re="$(printf '%s' "$ws" | sed 's/[.[\*^$()+?{}|]/\\&/g')"

violations=0
while IFS= read -r f; do
  [ -f "$f" ] || continue
  while IFS= read -r hit; do
    lineno="${hit%%:*}"
    token="${hit#*:}"
    case "$token" in *"<"*) continue;; esac
    if [ -z "$(git ls-files -- "$token" 2>/dev/null)" ]; then
      echo "$f:$lineno: $token"
      violations=$((violations+1))
    fi
  done < <(grep -noE "${ws_re}/[^<*[:space:]]*\.[A-Za-z0-9]+" "$f")
done < <(git ls-files -- docs skills)

if [ "$violations" -eq 0 ]; then echo "pass"; exit 0; fi
exit 1
