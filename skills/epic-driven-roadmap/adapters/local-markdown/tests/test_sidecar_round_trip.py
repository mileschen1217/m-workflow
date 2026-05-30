"""Sidecar key set + value strings preserved on read→write→read."""
import json
import re
import shutil
from pathlib import Path

import pytest

from skills.epic_driven_roadmap.adapters.local_markdown import adapter as A
from skills.epic_driven_roadmap.adapters.local_markdown import schema as S

GOLDEN = Path(__file__).parent / "golden"


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


@pytest.mark.parametrize("case", ["a_all_populated", "d_populated_phase_sidecar", "e_populated_epic_sidecar"])
def test_sidecar_round_trip_preserves_keys_and_value_strings(tmp_path, case: str):
    src = GOLDEN / case / "input.md"
    expected = json.loads((GOLDEN / case / "expected.json").read_text())
    root = tmp_path / "epics"
    (root / "fixture").mkdir(parents=True)
    (root / "fixture" / "index.md").write_text(src.read_text())
    a = A.LocalMarkdownAdapter(root=root)

    first = a.read("fixture")
    a.write("fixture", first)
    second = a.read("fixture")

    # epic-level sidecar
    assert set(first.sidecar.keys()) == set(second.sidecar.keys())
    for k in first.sidecar:
        v1, v2 = first.sidecar[k], second.sidecar[k]
        assert type(v1) is type(v2), f"tag-kind drift on {k}: {type(v1)} vs {type(v2)}"
        if isinstance(v1, str):
            assert _norm(v1) == _norm(v2)
        elif isinstance(v1, list):
            assert len(v1) == len(v2)
            for a_, b_ in zip(v1, v2):
                assert _norm(a_) == _norm(b_)
        elif isinstance(v1, dict):
            assert set(v1.keys()) == set(v2.keys())
            for kk in v1:
                assert _norm(v1[kk]) == _norm(v2[kk])

    # phase sidecar (fixture (d) values are all `str` tag — list/dict tags in a
    # phase row are rejected at write time per the SidecarUnstorableError tests
    # below, since the Phases-table cell host cannot express them.)
    assert len(first.phases) == len(second.phases)
    for p1, p2 in zip(first.phases, second.phases):
        assert set(p1.sidecar.keys()) == set(p2.sidecar.keys())
        for k in p1.sidecar:
            assert _norm(p1.sidecar[k]) == _norm(p2.sidecar[k])


def test_phase_sidecar_list_value_raises_sidecar_unstorable(tmp_path):
    """Phases-table cell host cannot express list[str]; write must throw
    `SidecarUnstorableError` rather than silently coerce to a `"['a', 'b']"`
    literal cell. On-disk file must be unchanged (atomic-or-throw)."""
    import hashlib
    root = tmp_path / "epics"
    (root / "fixture").mkdir(parents=True)
    p = root / "fixture" / "index.md"
    p.write_text(
        "---\nschema_version: 1\nslug: fixture\nstatus: active\nstarted: 2026-05-01\n---\n\n"
        "**Aim:** x.\n\n## Foundation\n\n## Phases\n\n"
        "| n | title | status | landed |\n|---|---|---|---|\n"
        "| 1 | Discover | done | 2026-05-10 |\n\n"
        "## Retrospective\n\n## Open Questions\n"
    )
    pre_sha = hashlib.sha256(p.read_bytes()).hexdigest()
    pre_mtime = p.stat().st_mtime_ns

    a = A.LocalMarkdownAdapter(root=root)
    data = a.read("fixture")
    # list[str] is a valid SidecarValue tag at the schema level, but the
    # Phases-table cell host cannot carry it — write must throw, not coerce.
    data.phases[0].sidecar["tags"] = ["alpha", "beta"]

    with pytest.raises(S.SidecarUnstorableError) as exc:
        a.write("fixture", data)
    assert exc.value.field == "phases[0].sidecar.tags"
    assert "list[str] cannot be expressed in a Phases-table cell" in exc.value.reason

    # atomic-or-throw: file content + mtime unchanged, no tmp residue
    assert hashlib.sha256(p.read_bytes()).hexdigest() == pre_sha
    assert p.stat().st_mtime_ns == pre_mtime
    assert list((root / "fixture").glob("index.md.tmp.*")) == []


def test_phase_sidecar_dict_value_raises_sidecar_unstorable(tmp_path):
    """Same rule for dict[str, str]: Phases-table cell host cannot carry it."""
    import hashlib
    root = tmp_path / "epics"
    (root / "fixture").mkdir(parents=True)
    p = root / "fixture" / "index.md"
    p.write_text(
        "---\nschema_version: 1\nslug: fixture\nstatus: active\nstarted: 2026-05-01\n---\n\n"
        "**Aim:** x.\n\n## Foundation\n\n## Phases\n\n"
        "| n | title | status | landed |\n|---|---|---|---|\n"
        "| 1 | Discover | done | 2026-05-10 |\n\n"
        "## Retrospective\n\n## Open Questions\n"
    )
    pre_sha = hashlib.sha256(p.read_bytes()).hexdigest()
    a = A.LocalMarkdownAdapter(root=root)
    data = a.read("fixture")
    data.phases[0].sidecar["meta"] = {"k": "v"}

    with pytest.raises(S.SidecarUnstorableError) as exc:
        a.write("fixture", data)
    assert exc.value.field == "phases[0].sidecar.meta"
    assert "dict[str, str] cannot be expressed in a Phases-table cell" in exc.value.reason
    assert hashlib.sha256(p.read_bytes()).hexdigest() == pre_sha


def test_phase_sidecar_str_with_pipe_raises_sidecar_unstorable(tmp_path):
    """Phase-sidecar str values containing `|` would split the row on
    re-read, breaking tag-preserving round-trip. Write must throw, not silently
    escape or coerce."""
    import hashlib
    root = tmp_path / "epics"
    (root / "fixture").mkdir(parents=True)
    p = root / "fixture" / "index.md"
    p.write_text(
        "---\nschema_version: 1\nslug: fixture\nstatus: active\nstarted: 2026-05-01\n---\n\n"
        "**Aim:** x.\n\n## Foundation\n\n## Phases\n\n"
        "| n | title | status | landed |\n|---|---|---|---|\n"
        "| 1 | Discover | done | 2026-05-10 |\n\n"
        "## Retrospective\n\n## Open Questions\n"
    )
    pre_sha = hashlib.sha256(p.read_bytes()).hexdigest()
    pre_mtime = p.stat().st_mtime_ns

    a = A.LocalMarkdownAdapter(root=root)
    data = a.read("fixture")
    data.phases[0].sidecar["note"] = "left | right"

    with pytest.raises(S.SidecarUnstorableError) as exc:
        a.write("fixture", data)
    assert exc.value.field == "phases[0].sidecar.note"
    assert "literal '|'" in exc.value.reason

    # atomic-or-throw: original byte-equal, no tmp residue
    assert hashlib.sha256(p.read_bytes()).hexdigest() == pre_sha
    assert p.stat().st_mtime_ns == pre_mtime
    assert list((root / "fixture").glob("index.md.tmp.*")) == []
