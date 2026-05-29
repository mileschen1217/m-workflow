"""AC-5 — epic_storage selector resolution with default + AdapterNotFoundError."""
from pathlib import Path

import pytest

from skills.epic_driven_roadmap import selector
from skills.epic_driven_roadmap.adapters.local_markdown import schema as S


def _write_yaml(p: Path, body: str):
    p.write_text(body)


def test_absent_key_resolves_to_local_markdown(tmp_path: Path):
    y = tmp_path / "touchstone.yaml"
    _write_yaml(y, "workspace_root: .touchstone\n")
    name = selector.resolve_adapter_name(y)
    assert name == "local-markdown"


def test_explicit_local_markdown_resolves(tmp_path: Path):
    y = tmp_path / "touchstone.yaml"
    _write_yaml(y, "epic_storage: local-markdown\n")
    assert selector.resolve_adapter_name(y) == "local-markdown"


def test_unknown_adapter_raises_adapter_not_found(tmp_path: Path):
    y = tmp_path / "touchstone.yaml"
    _write_yaml(y, "epic_storage: nonexistent-adapter\n")
    with pytest.raises(S.AdapterNotFoundError) as exc:
        selector.resolve_adapter_name(y)
    assert exc.value.selector == "nonexistent-adapter"


def test_missing_yaml_resolves_to_local_markdown(tmp_path: Path):
    name = selector.resolve_adapter_name(tmp_path / "absent.yaml")
    assert name == "local-markdown"
