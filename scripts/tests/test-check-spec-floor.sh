#!/usr/bin/env bash
# Fixture-based tests for check-spec-floor.sh (no bats in this repo).
# Each case asserts exit code + a required substring in output.
set -uo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
checker="$here/../check-spec-floor.sh"
fix="$here/floor-fixtures"
fail=0

# assert <name> <expected-exit> <required-substring> <fixture>
assert() {
  local name="$1" want_rc="$2" want_sub="$3" file="$4"
  local out rc
  out="$(bash "$checker" "$fix/$file" 2>&1)"; rc=$?
  if [ "$rc" -ne "$want_rc" ]; then
    echo "FAIL $name: exit want=$want_rc got=$rc"; fail=$((fail+1)); return
  fi
  if ! printf '%s' "$out" | grep -qF "$want_sub"; then
    echo "FAIL $name: output missing '$want_sub' — got: $out"; fail=$((fail+1)); return
  fi
  echo "ok $name"
}

assert happy        0 "pass"              happy.md
assert missing-body 1 "AC-2"              missing-body.md
assert orphan-body  1 "AC-2"              orphan-body.md
assert empty-reason 1 "AC-1"              empty-reason.md
assert no-table     1 "no AC table"       no-table.md
assert draft        0 "skipped: draft"    draft.md
assert dup-index    1 "AC-2"              dup-index.md
assert dup-body     1 "AC-1"              dup-body.md
assert noise        0 "pass"              noise.md

if [ "$fail" -eq 0 ]; then echo "ALL GREEN"; exit 0; else echo "RED: $fail failed"; exit 1; fi
