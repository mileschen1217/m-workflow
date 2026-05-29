#!/usr/bin/env python3
"""Generate the canonical-field consumer table for interface.md from schema metadata.

Usage:
  gen_interface_doc.py            # rewrite the table block in interface.md in-place
  gen_interface_doc.py --check    # exit 0 if file == regenerated, 1 + diff to stderr otherwise
  gen_interface_doc.py --stdout   # print regenerated block to stdout
"""
from __future__ import annotations

import argparse
import dataclasses
import difflib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Register hyphenated-directory aliases so `epic_driven_roadmap` resolves from `skills/`
import types as _types
_root = Path(__file__).resolve().parents[2]
for _qname, _relpath in [
    ("epic_driven_roadmap", "epic-driven-roadmap"),
    ("epic_driven_roadmap.adapters", "epic-driven-roadmap/adapters"),
    ("epic_driven_roadmap.adapters.local_markdown", "epic-driven-roadmap/adapters/local-markdown"),
]:
    if _qname not in sys.modules:
        _m = _types.ModuleType(_qname)
        _m.__path__ = [str(_root / _relpath)]
        sys.modules[_qname] = _m

from epic_driven_roadmap.adapters.local_markdown import schema as S  # noqa: E402

BEGIN = "<!-- BEGIN-GENERATED-CONSUMER-TABLE -->"
END = "<!-- END-GENERATED-CONSUMER-TABLE -->"

DOC_PATH = Path(__file__).resolve().parent / "interface.md"


def build_block() -> str:
    lines = ["", "| Field | Consumer |", "|---|---|"]
    for f in dataclasses.fields(S.EpicData):
        if "consumer" in f.metadata:
            lines.append(f"| `{f.name}` | {f.metadata['consumer']} |")
    for f in dataclasses.fields(S.PhaseData):
        if "consumer" in f.metadata:
            lines.append(f"| `phases[].{f.name}` | {f.metadata['consumer']} |")
    lines.append("")
    return "\n".join(lines)


def splice(doc: str, block: str) -> str:
    i = doc.index(BEGIN) + len(BEGIN)
    j = doc.index(END)
    return doc[:i] + block + doc[j:]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    p.add_argument("--stdout", action="store_true")
    args = p.parse_args()

    block = build_block()
    if args.stdout:
        print(block)
        return 0

    current = DOC_PATH.read_text()
    regenerated = splice(current, block)

    if args.check:
        if current == regenerated:
            return 0
        diff = "\n".join(difflib.unified_diff(
            current.splitlines(), regenerated.splitlines(),
            fromfile="committed", tofile="regenerated", lineterm="",
        ))
        sys.stderr.write(diff + "\n")
        return 1

    DOC_PATH.write_text(regenerated)
    return 0


if __name__ == "__main__":
    sys.exit(main())
