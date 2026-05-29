# skills/epic-driven-roadmap/tests/test_procedure_prose_purity.py — placeholder
def test_skill_md_calls_cli_at_least_once():
    from pathlib import Path
    p = Path(__file__).resolve().parents[1] / "SKILL.md"
    assert "cli.py read" in p.read_text() or "cli.py write" in p.read_text(), \
        "SKILL.md must invoke adapter CLI for index access"


def _build_forbidden_tokens() -> list[str]:
    """AC-1 — derive forbidden tokens at test time from §Interfaces structural map."""
    import dataclasses
    from skills.epic_driven_roadmap.adapters.local_markdown import schema as S

    fm_keys = []
    for f in dataclasses.fields(S.EpicData):
        if f.name in ("schema_version", "slug", "status", "started", "landed"):
            fm_keys.append(f"{f.name}:")

    section_headers = [
        "## Foundation", "## Phases", "## Retrospective", "## Open Questions",
    ]
    body_anchors = [r"\*\*Aim:\*\*"]
    structural = [r"\.touchstone/epics/", r"index\.md"]
    shape_phrases = ["the Phases table", "the index file", "the index frontmatter"]

    return fm_keys + section_headers + body_anchors + structural + shape_phrases


def test_index_access_prose_has_no_direct_filesystem_references():
    """AC-1 — schema-driven grep over in-scope index-access files."""
    import re
    from pathlib import Path
    REPO = Path(__file__).resolve().parents[1]
    in_scope = [
        REPO / "SKILL.md",
        REPO / "references" / "close-and-stage7.md",
        REPO / "references" / "tasks.md",
    ]
    tokens = _build_forbidden_tokens()
    forbidden = re.compile("|".join(tokens))
    fence_re = re.compile(r"^```")

    violations: list[str] = []
    for f in in_scope:
        in_fence = False
        for lineno, line in enumerate(f.read_text().splitlines(), 1):
            if fence_re.match(line.strip()):
                in_fence = not in_fence; continue
            if in_fence:
                continue
            if "phase-2-carve-out" in line:
                continue
            if "ROADMAP.md" in line:
                continue
            if forbidden.search(line):
                violations.append(f"{f.relative_to(REPO)}:{lineno}: {line.strip()}")

    assert not violations, "AC-1 violations:\n" + "\n".join(violations)


def test_audit_and_bootstrap_carve_out_lines_are_marked():
    """Every line in audit.md or bootstrap.md that names .touchstone/epics/ or
    index.md must carry the <!-- phase-2-carve-out --> marker, OR sit inside
    a fenced code block."""
    from pathlib import Path
    import re
    REPO = Path(__file__).resolve().parents[1]
    targets = [
        REPO / "references" / "audit.md",
        REPO / "references" / "bootstrap.md",
    ]
    forbidden = re.compile(r"\.touchstone/epics/|index\.md")
    fence_re = re.compile(r"^```")
    for f in targets:
        in_fence = False
        for lineno, line in enumerate(f.read_text().splitlines(), 1):
            if fence_re.match(line.strip()):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if forbidden.search(line):
                assert "phase-2-carve-out" in line, (
                    f"{f.name}:{lineno} names index-access path without carve-out marker: {line!r}"
                )
