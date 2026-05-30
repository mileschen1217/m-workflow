"""Canonical-field byte-equal round trip over every existing epic on disk."""
import dataclasses
import shutil
from pathlib import Path

import pytest

from skills.epic_driven_roadmap.adapters.local_markdown import adapter as A
from skills.epic_driven_roadmap.adapters.local_markdown import schema as S

REPO = Path(__file__).resolve().parents[5]
EPICS = REPO / ".touchstone" / "epics"


def _live_slugs() -> list[str]:
    if not EPICS.exists():
        return []
    out = []
    for child in EPICS.iterdir():
        if child.is_dir() and (child / "index.md").exists():
            out.append(child.name)
    return out


def _canonical_only(d: S.EpicData) -> dict:
    out = dataclasses.asdict(d)
    out.pop("sidecar", None)
    for ph in out.get("phases", []):
        ph.pop("sidecar", None)
    return out


@pytest.mark.parametrize("slug", _live_slugs())
def test_round_trip_canonical_byte_equal(tmp_path: Path, slug: str):
    # Copy the epic into a scratch root so we don't mutate the live tree
    scratch = tmp_path / "epics"
    scratch.mkdir()
    shutil.copytree(EPICS / slug, scratch / slug)

    a = A.LocalMarkdownAdapter(root=scratch)
    try:
        first = a.read(slug)
    except S.StructuralHostMissingError:
        pytest.skip(f"{slug}: missing Open Questions section — out of round-trip scope")

    a.write(slug, first)
    second = a.read(slug)

    assert _canonical_only(first) == _canonical_only(second)
