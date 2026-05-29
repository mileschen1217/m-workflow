# skills/epic-driven-roadmap/tests/test_procedure_prose_purity.py — placeholder
def test_skill_md_calls_cli_at_least_once():
    from pathlib import Path
    p = Path(__file__).resolve().parents[1] / "SKILL.md"
    assert "cli.py read" in p.read_text() or "cli.py write" in p.read_text(), \
        "SKILL.md must invoke adapter CLI for index access"
