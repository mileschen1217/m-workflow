"""Golden fixtures parse to expected canonical + sidecar superset."""
import dataclasses
import json
from pathlib import Path

import pytest

from skills.epic_driven_roadmap.adapters.local_markdown import adapter as A
from skills.epic_driven_roadmap.adapters.local_markdown import schema as S

GOLDEN = Path(__file__).parent / "golden"


def _cases() -> list[Path]:
    return sorted(p for p in GOLDEN.iterdir() if p.is_dir())


@pytest.mark.parametrize("case_dir", _cases(), ids=lambda p: p.name)
def test_golden_parses_to_expected(tmp_path, case_dir: Path):
    expected = json.loads((case_dir / "expected.json").read_text())
    root = tmp_path / "epics"
    (root / "fixture").mkdir(parents=True)
    (root / "fixture" / "index.md").write_text((case_dir / "input.md").read_text())
    a = A.LocalMarkdownAdapter(root=root)

    if "error" in expected:
        with pytest.raises(getattr(S, expected["error"]["class"])) as exc:
            a.read("fixture")
        for k, v in expected["error"].get("attrs", {}).items():
            assert getattr(exc.value, k) == v
        return

    data = a.read("fixture")
    actual = dataclasses.asdict(data)
    actual["slug"] = "fixture"  # path-derived

    # Canonical fields must match exactly
    for canonical_key in (
        "schema_version", "status", "started", "landed",
        "aim", "intention", "out_of_scope",
        "retrospective", "open_questions",
    ):
        assert actual[canonical_key] == expected.get(canonical_key, actual[canonical_key]), (
            f"canonical mismatch on {canonical_key}"
        )

    # Phases canonical
    assert len(actual["phases"]) == len(expected.get("phases", []))
    for ap, ep in zip(actual["phases"], expected.get("phases", [])):
        for k in ("n", "title", "status", "landed"):
            assert ap[k] == ep.get(k, ap[k]), f"phase canonical mismatch on {k}"

    # Sidecar SUPERSET requirement: every expected sidecar key must appear in actual
    expected_sc = expected.get("sidecar", {})
    for k, v in expected_sc.items():
        assert k in actual["sidecar"], f"sidecar key {k} dropped"
        assert actual["sidecar"][k] == v, f"sidecar value mismatch on {k}"
