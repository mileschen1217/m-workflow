"""Scope carve-out — epic-index.md template must NOT carry dead frontmatter keys."""
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parents[1] / "templates" / "epic-index.md"

DEAD_KEYS = ("target:", "owner_teams:", "gitlab_issues:", "github_issues:")


def test_template_has_no_dead_frontmatter_keys():
    text = TEMPLATE.read_text()
    for k in DEAD_KEYS:
        assert k not in text, f"dead key {k!r} still present in template"
