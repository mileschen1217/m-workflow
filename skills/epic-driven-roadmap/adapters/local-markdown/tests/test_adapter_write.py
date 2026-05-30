"""write() atomicity + serialisation/sidecar errors."""
import hashlib
import os
from pathlib import Path

import pytest

from skills.epic_driven_roadmap.adapters.local_markdown import adapter as A
from skills.epic_driven_roadmap.adapters.local_markdown import schema as S


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _make_epic(tmp_path: Path, slug: str = "demo") -> Path:
    root = tmp_path / "epics"
    (root / slug).mkdir(parents=True)
    p = root / slug / "index.md"
    p.write_text(
        "---\nschema_version: 1\nslug: demo\nstatus: active\nstarted: 2026-05-01\n---\n\n"
        "**Aim:** x.\n\n## Foundation\n\n- Intention: y.\n\n## Phases\n\n## Retrospective\n\n## Open Questions\n"
    )
    return root


def test_write_creates_first_epic(tmp_path: Path):
    root = tmp_path / "epics"
    root.mkdir()
    a = A.LocalMarkdownAdapter(root=root)
    data = S.EpicData(slug="new", status="active", started="2026-05-01", aim="ship")
    data.open_questions = []
    a.write("new", data)
    assert (root / "new" / "index.md").exists()


def test_write_atomic_no_tmp_residue_on_success(tmp_path: Path):
    root = _make_epic(tmp_path)
    a = A.LocalMarkdownAdapter(root=root)
    data = a.read("demo")
    data.aim = "updated"
    a.write("demo", data)
    leftovers = list((root / "demo").glob("index.md.tmp.*"))
    assert leftovers == []


def test_write_throws_on_serialiser_failure_after_partial_tmp(tmp_path: Path, monkeypatch):
    root = _make_epic(tmp_path)
    a = A.LocalMarkdownAdapter(root=root)
    pre = _sha(root / "demo" / "index.md")
    data = a.read("demo")

    # Inject failure AFTER serialise() begins writing the tmp file
    orig_serialise = a._serialise
    def boom(d):
        # Write a partial tmp file before raising to simulate post-step-1 failure
        tmp = root / "demo" / "index.md.tmp.99999"
        tmp.write_text("partial")
        raise S.CanonicalSerialisationError(field="phases", backend="local-markdown")
    monkeypatch.setattr(a, "_serialise", boom)

    with pytest.raises(S.CanonicalSerialisationError):
        a.write("demo", data)

    assert _sha(root / "demo" / "index.md") == pre
    assert list((root / "demo").glob("index.md.tmp.*")) == []


def test_write_throws_on_serialiser_failure_before_tmp(tmp_path: Path, monkeypatch):
    root = _make_epic(tmp_path)
    a = A.LocalMarkdownAdapter(root=root)
    pre = _sha(root / "demo" / "index.md")
    data = a.read("demo")

    def boom(d):
        raise S.CanonicalSerialisationError(field="aim", backend="local-markdown")
    monkeypatch.setattr(a, "_serialise", boom)

    with pytest.raises(S.CanonicalSerialisationError):
        a.write("demo", data)
    assert _sha(root / "demo" / "index.md") == pre
    assert list((root / "demo").glob("index.md.tmp.*")) == []


def test_write_throws_on_unstorable_sidecar(tmp_path: Path):
    root = _make_epic(tmp_path)
    a = A.LocalMarkdownAdapter(root=root)
    data = a.read("demo")
    data.sidecar["bad"] = 42  # int — outside SidecarValue tagged shape

    pre = _sha(root / "demo" / "index.md")
    with pytest.raises(S.SidecarUnstorableError):
        a.write("demo", data)
    assert _sha(root / "demo" / "index.md") == pre
    assert list((root / "demo").glob("index.md.tmp.*")) == []


def test_write_stamps_schema_version_overriding_caller(tmp_path: Path):
    root = _make_epic(tmp_path)
    a = A.LocalMarkdownAdapter(root=root)
    data = a.read("demo")
    data.schema_version = 99  # caller value MUST be ignored
    a.write("demo", data)
    reread = a.read("demo")
    assert reread.schema_version == S.SCHEMA_VERSION
