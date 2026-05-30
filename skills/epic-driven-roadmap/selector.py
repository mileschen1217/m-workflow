"""Step-0 epic_storage selector resolution.

Reads `.claude/touchstone.yaml`, returns the adapter name to dispatch.
Raises AdapterNotFoundError on unknown selectors.
"""
from __future__ import annotations

from pathlib import Path

from .adapters.local_markdown.schema import AdapterNotFoundError

KNOWN_ADAPTERS = {"local-markdown"}
DEFAULT_ADAPTER = "local-markdown"


def _read_epic_storage_key(yaml_path: Path) -> str | None:
    """Return epic_storage value or None. Lenient: ignores unknown keys."""
    try:
        text = Path(yaml_path).read_text()
    except OSError:
        return None
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("epic_storage:"):
            v = s.split(":", 1)[1].strip()
            # strip quotes if present
            if len(v) >= 2 and ((v[0] == v[-1] == '"') or (v[0] == v[-1] == "'")):
                v = v[1:-1]
            return v or None
    return None


def resolve_adapter_name(yaml_path: Path) -> str:
    if not Path(yaml_path).exists():
        return DEFAULT_ADAPTER
    name = _read_epic_storage_key(yaml_path)
    if name is None:
        return DEFAULT_ADAPTER
    if name not in KNOWN_ADAPTERS:
        raise AdapterNotFoundError(selector=str(name))
    return str(name)
