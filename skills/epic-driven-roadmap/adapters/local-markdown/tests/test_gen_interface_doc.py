"""interface.md consumer table is auto-generated; drift fails loud."""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
GEN = REPO / "skills/epic-driven-roadmap/adapters/gen_interface_doc.py"
DOC = REPO / "skills/epic-driven-roadmap/adapters/interface.md"

BEGIN = "<!-- BEGIN-GENERATED-CONSUMER-TABLE -->"
END = "<!-- END-GENERATED-CONSUMER-TABLE -->"


def _slice(text: str) -> str:
    i = text.index(BEGIN) + len(BEGIN)
    j = text.index(END)
    return text[i:j]


def test_generated_table_matches_committed_doc():
    """Drift gate — `gen_interface_doc.py --check` exits 0 iff committed == generated."""
    result = subprocess.run(
        [sys.executable, str(GEN), "--check"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, f"drift detected:\nSTDERR:\n{result.stderr}"


def test_generated_table_lists_every_canonical_field():
    """Every consumer-tagged field appears in the table."""
    from skills.epic_driven_roadmap.adapters.local_markdown import schema as S
    import dataclasses

    block = _slice(DOC.read_text())
    for f in dataclasses.fields(S.EpicData):
        if "consumer" in f.metadata:
            assert f"`{f.name}`" in block, f"EpicData.{f.name} missing from consumer table"
    for f in dataclasses.fields(S.PhaseData):
        if "consumer" in f.metadata:
            assert f"phases[].{f.name}" in block or f"`{f.name}`" in block, (
                f"PhaseData.{f.name} missing from consumer table"
            )


def test_sidecar_passthrough_lists_every_sidecar_field():
    """Every sidecar field appears in passthrough list."""
    from skills.epic_driven_roadmap.adapters.local_markdown import schema as S
    import dataclasses

    text = DOC.read_text()
    sidecar_section_start = text.index("## Sidecar passthrough")
    sidecar_section = text[sidecar_section_start:]
    for f in dataclasses.fields(S.EpicData):
        if "sidecar_rationale" in f.metadata:
            assert f"`{f.name}`" in sidecar_section, f"EpicData.{f.name} missing from sidecar list"
