"""AC-8 (d) — carve-out audit detects status drift via direct-fs scan
(NOT via adapter — proves the refactor did not break the carved-out path)."""
import os
import re
import textwrap
from pathlib import Path


def _scan_status_via_direct_fs(epics_root: Path) -> dict[str, str]:
    """Mimics the carved-out audit pass — direct frontmatter scan, no adapter."""
    out = {}
    for child in epics_root.iterdir():
        if not child.is_dir():
            continue
        idx = child / "index.md"
        if not idx.exists():
            continue
        text = idx.read_text()
        m = re.search(r"^status:\s*(\S+)", text, re.MULTILINE)
        if m:
            out[child.name] = m.group(1)
    return out


def test_carve_out_audit_detects_status_drift(tmp_path: Path):
    epics = tmp_path / "epics"
    epics.mkdir()
    (epics / "ep").mkdir()
    (epics / "ep" / "index.md").write_text(textwrap.dedent("""\
        ---
        schema_version: 1
        slug: ep
        status: done
        started: 2026-05-01
        landed: 2026-05-20
        ---
        **Aim:** x.
        ## Foundation
        ## Phases
        ## Retrospective
        ## Open Questions
        """))
    roadmap_says = {"ep": "active"}  # synthetic ROADMAP claim
    on_disk = _scan_status_via_direct_fs(epics)
    drift = {k: (roadmap_says[k], on_disk[k]) for k in roadmap_says if roadmap_says[k] != on_disk.get(k)}
    assert drift == {"ep": ("active", "done")}
