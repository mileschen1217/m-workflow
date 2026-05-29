# skills/epic-driven-roadmap/tests/test_procedure_prose_purity.py — placeholder
def test_skill_md_calls_cli_at_least_once():
    from pathlib import Path
    p = Path(__file__).resolve().parents[1] / "SKILL.md"
    assert "cli.py read" in p.read_text() or "cli.py write" in p.read_text(), \
        "SKILL.md must invoke adapter CLI for index access"


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
