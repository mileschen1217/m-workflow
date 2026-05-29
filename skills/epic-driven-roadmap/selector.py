"""Step-0 epic_storage selector resolution.

Reads `.claude/touchstone.yaml`, returns the adapter name to dispatch.
Raises AdapterNotFoundError on unknown selectors.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from .adapters.local_markdown.schema import AdapterNotFoundError

KNOWN_ADAPTERS = {"local-markdown"}
DEFAULT_ADAPTER = "local-markdown"


def resolve_adapter_name(yaml_path: Path) -> str:
    if not Path(yaml_path).exists():
        return DEFAULT_ADAPTER
    try:
        cfg = yaml.safe_load(Path(yaml_path).read_text()) or {}
    except yaml.YAMLError:
        return DEFAULT_ADAPTER
    if not isinstance(cfg, dict):
        return DEFAULT_ADAPTER
    name = cfg.get("epic_storage")
    if name is None:
        return DEFAULT_ADAPTER
    if name not in KNOWN_ADAPTERS:
        raise AdapterNotFoundError(selector=str(name))
    return str(name)
