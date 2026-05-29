"""AC-3 happy path — adapter.read() parses an all-populated epic to EpicData."""
import textwrap
from pathlib import Path

import pytest

from skills.epic_driven_roadmap.adapters.local_markdown import adapter as A
from skills.epic_driven_roadmap.adapters.local_markdown import schema as S


FIXTURE = textwrap.dedent("""\
    ---
    schema_version: 1
    slug: demo-epic
    status: active
    started: 2026-05-01
    landed: null
    ---

    **Aim:** ship the demo.

    ## Foundation

    - Intention: prove the loop.
    - Out of scope: scope creep.

    ## Phases

    | n | title | status | landed |
    |---|---|---|---|
    | 1 | Discover | done | 2026-05-10 |
    | 2 | Build | active |  |

    ## Retrospective

    - Tighter scope helped.

    ## Open Questions

    - Concurrency?
    """)


def test_read_populated_epic(tmp_path: Path):
    root = tmp_path / "epics"
    (root / "demo-epic").mkdir(parents=True)
    (root / "demo-epic" / "index.md").write_text(FIXTURE)

    a = A.LocalMarkdownAdapter(root=root)
    data = a.read("demo-epic")

    assert data.schema_version == 1
    assert data.slug == "demo-epic"
    assert data.status == "active"
    assert data.started == "2026-05-01"
    assert data.landed is None
    assert data.aim == "ship the demo."
    assert "prove the loop." in data.intention
    assert data.out_of_scope == ["scope creep."]
    assert len(data.phases) == 2
    assert data.phases[0].n == 1
    assert data.phases[0].title == "Discover"
    assert data.phases[0].status == "done"
    assert data.phases[0].landed == "2026-05-10"
    assert data.phases[1].landed is None
    assert data.retrospective == ["Tighter scope helped."]
    assert data.open_questions == ["Concurrency?"]


ERRDIR = Path(__file__).parent / "errors"


def _seed(tmp_path: Path, slug: str, fixture_name: str) -> Path:
    src = ERRDIR / fixture_name
    root = tmp_path / "epics"
    (root / slug).mkdir(parents=True)
    (root / slug / "index.md").write_text(src.read_text())
    return root


def test_read_missing_slug_raises_epic_not_found(tmp_path: Path):
    a = A.LocalMarkdownAdapter(root=tmp_path / "epics")
    with pytest.raises(S.EpicNotFound) as exc:
        a.read("nope")
    assert exc.value.slug == "nope"


def test_read_missing_required_field_raises_schema_validation(tmp_path: Path):
    root = _seed(tmp_path, "bad", "missing_status.md")
    a = A.LocalMarkdownAdapter(root=root)
    with pytest.raises(S.SchemaValidationError) as exc:
        a.read("bad")
    assert exc.value.field == "status"


def test_read_schema_version_mismatch_raises(tmp_path: Path):
    root = _seed(tmp_path, "bad", "schema_v99.md")
    a = A.LocalMarkdownAdapter(root=root)
    with pytest.raises(S.SchemaVersionMismatch) as exc:
        a.read("bad")
    assert exc.value.found == 99 and exc.value.expected == 1


def test_read_structural_host_missing_raises(tmp_path: Path):
    root = _seed(tmp_path, "bad", "missing_open_questions.md")
    a = A.LocalMarkdownAdapter(root=root)
    with pytest.raises(S.StructuralHostMissingError) as exc:
        a.read("bad")
    assert exc.value.field == "open_questions"


def test_read_invalid_phase_status_raises_schema_validation(tmp_path: Path):
    """M1 — phase status outside STATUS_VALUES → SchemaValidationError."""
    root = _seed(tmp_path, "bad", "invalid_phase_status.md")
    a = A.LocalMarkdownAdapter(root=root)
    with pytest.raises(S.SchemaValidationError) as exc:
        a.read("bad")
    assert "phases[" in exc.value.field and ".status" in exc.value.field
