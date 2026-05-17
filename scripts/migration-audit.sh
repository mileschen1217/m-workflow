#!/usr/bin/env bash
# m-workflow migration audit script.
# Modes:
#   --namespace      Detect legacy m-* namespace references; classify into 4 classes.
#   --magic-string   Detect residual `grep -l 'source-as-truth'` ADR-probe patterns.
#   --unexpanded-vars  Source-level: detect unknown / typo ${CLAUDE_*} references.
# Exits 0 on clean (--namespace: no stale; --magic-string/--unexpanded-vars: zero hits).

set -euo pipefail

MODE="${1:-}"
TARGET="${2:-${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}}"

# Scan scope: skills/ + templates/ recursively; both .md and bundled siblings.
SCAN_DIRS=("$TARGET/skills" "$TARGET/templates")

usage() {
  echo "Usage: $0 --namespace | --magic-string | --unexpanded-vars [target-path]" >&2
  exit 2
}

[ -z "$MODE" ] && usage

case "$MODE" in
  --namespace)
    # Two pattern classes:
    # (1) Slash-prefixed legacy: /m-<name>
    # (2) Bare legacy skill name (in prose, e.g., "m-design-spec" without slash)
    # (3) Filesystem-prefixed: ~/.claude/skills/m-<name>
    # Includes ground-in-source and dispatch-gemini (these stay legacy, but references must be classified).
    SKILL_NAMES='design-spec|design-review|arch-review|arch-discovery|epic-driven-roadmap|code-review|test-quality-audit|harness-audit|extract-knowledge|cross-provider-reviewer|cross-provider-architect|ground-in-source|dispatch-gemini'
    PATTERN_SLASH="/m-(${SKILL_NAMES})"
    PATTERN_BARE="\\bm-(${SKILL_NAMES})\\b"
    PATTERN_FS="~/\\.claude/skills/m-(${SKILL_NAMES})"

    # All raw hits.
    RAW=$(rg -n -E "($PATTERN_SLASH|$PATTERN_BARE|$PATTERN_FS)" "${SCAN_DIRS[@]}" 2>/dev/null || true)

    [ -z "$RAW" ] && { echo "PASS: no legacy namespace references."; exit 0; }

    # Classify each hit (rev 3 G4: per-FILE context, not per-line).
    # Wrapper file = SKILL.md whose frontmatter description contains "DEPRECATED" (these legitimately quote old commands).
    # For each hit:
    # (a) wrapper-legacy [PASS]: file is a wrapper
    # (b) renamed [PASS]: file is not a wrapper AND line contains m-workflow:<n> (already updated form)
    # (c) external [PASS, advisory]: file path outside scan scope (not expected from local scan, included for AC-9 parity)
    # (d) stale [FAIL]: file is not a wrapper AND line does NOT contain m-workflow:<n>
    >/tmp/audit_wrapper_legacy ; >/tmp/audit_renamed ; >/tmp/audit_external ; >/tmp/audit_stale

    while IFS= read -r hit; do
      [ -z "$hit" ] && continue
      file=$(echo "$hit" | awk -F: '{print $1}')
      line_content=$(echo "$hit" | awk -F: '{for(i=3;i<=NF;i++) printf "%s%s", $i, (i<NF?":":"\n")}')

      # Check file role: wrapper if first ~20 lines contain DEPRECATED in description block
      is_wrapper=0
      if [ -f "$file" ] && head -20 "$file" | grep -qE "^description:.*DEPRECATED|description:.*\n.*DEPRECATED"; then
        is_wrapper=1
      fi

      if [ "$is_wrapper" -eq 1 ]; then
        echo "$hit" >> /tmp/audit_wrapper_legacy
      elif echo "$line_content" | grep -q "m-workflow:"; then
        echo "$hit" >> /tmp/audit_renamed
      else
        echo "$hit" >> /tmp/audit_stale
      fi
    done <<< "$RAW"

    echo "=== Wrapper-legacy (PASS): $(wc -l < /tmp/audit_wrapper_legacy) hits ==="
    head -5 /tmp/audit_wrapper_legacy
    echo ""
    echo "=== Renamed (PASS): $(wc -l < /tmp/audit_renamed) hits ==="
    head -5 /tmp/audit_renamed
    echo ""
    echo "=== External (PASS, advisory): $(wc -l < /tmp/audit_external) hits ==="
    head -5 /tmp/audit_external
    echo ""
    echo "=== STALE (FAIL): $(wc -l < /tmp/audit_stale) hits ==="
    if [ -s /tmp/audit_stale ]; then
      cat /tmp/audit_stale
      echo ""
      echo "Stale hits found in non-wrapper files. Wrapper deletion (Phase B) blocked until clean."
      rm -f /tmp/audit_{wrapper_legacy,renamed,external,stale}
      exit 1
    fi
    rm -f /tmp/audit_{wrapper_legacy,renamed,external,stale}
    echo "PASS: no stale namespace references in non-wrapper files."
    ;;

  --magic-string)
    # Hits = residual `grep -l 'source-as-truth'` or ADR-probe heuristics across SKILL.md + siblings + templates.
    PATTERN='(grep[^|]*source-as-truth|grep[^|]*adopted[^|]*ADR|grep -l[^|]*\.md)'
    HITS=$(rg -n -E "$PATTERN" "${SCAN_DIRS[@]}" 2>/dev/null || true)
    if [ -n "$HITS" ]; then
      echo "MAGIC-STRING grep patterns found (rev 3 N-H4 / AC-10 violation):"
      echo "$HITS"
      exit 1
    fi
    echo "PASS: no magic-string ADR probes."
    ;;

  --unexpanded-vars)
    # Source-level audit per rev 4 H2 fix.
    # Allowed: ${CLAUDE_PLUGIN_ROOT}, ${CLAUDE_PROJECT_DIR}, ${CLAUDE_SKILL_DIR},
    #          ${CLAUDE_PLUGIN_DATA}, ${CLAUDE_SESSION_ID}, ${user_config.*}
    PATTERN='\$\{[^}]+\}'
    ALLOWED='\$\{(CLAUDE_(PLUGIN_ROOT|PROJECT_DIR|SKILL_DIR|PLUGIN_DATA|SESSION_ID)|user_config\.[a-zA-Z_]+)\}'
    HITS=$(rg -no -E "$PATTERN" "${SCAN_DIRS[@]}" 2>/dev/null | grep -vE "$ALLOWED" || true)
    if [ -n "$HITS" ]; then
      echo "UNKNOWN \${...} references found in skill bodies (typos / unsupported vars):"
      echo "$HITS"
      echo ""
      echo "Allowed set: \${CLAUDE_PLUGIN_ROOT}, \${CLAUDE_PROJECT_DIR}, \${CLAUDE_SKILL_DIR},"
      echo "             \${CLAUDE_PLUGIN_DATA}, \${CLAUDE_SESSION_ID}, \${user_config.*}"
      exit 1
    fi
    echo "PASS: only known plugin variables referenced in skill bodies."
    ;;

  *)
    usage
    ;;
esac
