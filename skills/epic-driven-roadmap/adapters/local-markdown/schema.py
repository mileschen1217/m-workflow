"""Canonical-form schema for epic-driven-roadmap storage adapters.

Single source of truth for EpicData / PhaseData and the typed-error hierarchy
the CLI maps to exit codes 0-9.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional, Union

SCHEMA_VERSION = 1

Status = Literal["proposed", "active", "paused", "done", "cancelled"]
STATUS_VALUES = ("proposed", "active", "paused", "done", "cancelled")

SidecarValue = Union[str, list, dict]


# ---------- typed errors ----------

class AdapterError(Exception):
    """Base class for all adapter errors."""


@dataclass
class SchemaValidationError(AdapterError):
    field: str
    slug: str = ""
    schema_version: int = SCHEMA_VERSION
    reason: str = ""

    def __str__(self) -> str:
        return f"SchemaValidationError(field={self.field!r}, slug={self.slug!r}, reason={self.reason!r})"


@dataclass
class SchemaVersionMismatch(AdapterError):
    found: int
    expected: int

    def __str__(self) -> str:
        return f"SchemaVersionMismatch(found={self.found}, expected={self.expected})"


@dataclass
class CanonicalSerialisationError(AdapterError):
    field: str
    backend: str = "local-markdown"

    def __str__(self) -> str:
        return f"CanonicalSerialisationError(field={self.field!r}, backend={self.backend!r})"


@dataclass
class SidecarUnstorableError(AdapterError):
    field: str
    backend: str = "local-markdown"
    reason: str = ""

    def __str__(self) -> str:
        return f"SidecarUnstorableError(field={self.field!r}, backend={self.backend!r}, reason={self.reason!r})"


@dataclass
class StructuralHostMissingError(AdapterError):
    field: str

    def __str__(self) -> str:
        return f"StructuralHostMissingError(field={self.field!r})"


@dataclass
class EpicNotFound(AdapterError):
    slug: str

    def __str__(self) -> str:
        return f"EpicNotFound(slug={self.slug!r})"


@dataclass
class AdapterNotFoundError(AdapterError):
    selector: str

    def __str__(self) -> str:
        return f"AdapterNotFoundError(selector={self.selector!r})"


@dataclass
class AdapterInternalError(AdapterError):
    cause: str = ""

    def __str__(self) -> str:
        return f"AdapterInternalError(cause={self.cause!r})"


# ---------- sidecar tag validation ----------

def validate_sidecar_value(v) -> None:
    """Raise SidecarUnstorableError if v is outside SidecarValue tagged shape."""
    if isinstance(v, bool):
        raise SidecarUnstorableError(field="<sidecar>", reason=f"untagged type: {type(v).__name__}")
    if isinstance(v, str):
        return
    if isinstance(v, list):
        for el in v:
            if not isinstance(el, str):
                raise SidecarUnstorableError(field="<sidecar>", reason=f"list element not str: {type(el).__name__}")
        return
    if isinstance(v, dict):
        for k, val in v.items():
            if not isinstance(k, str):
                raise SidecarUnstorableError(field="<sidecar>", reason=f"dict key not str: {type(k).__name__}")
            if not isinstance(val, str):
                raise SidecarUnstorableError(field="<sidecar>", reason=f"dict value not str: {type(val).__name__}")
        return
    raise SidecarUnstorableError(field="<sidecar>", reason=f"untagged type: {type(v).__name__}")


# ---------- canonical dataclasses ----------

@dataclass
class PhaseData:
    n: int = field(default=0, metadata={"consumer": "close procedure (phase enumeration)"})
    title: str = field(default="", metadata={"consumer": "close procedure (phase enumeration)"})
    status: str = field(default="proposed", metadata={"consumer": "close procedure (all phases done?)"})
    landed: Optional[str] = field(default=None, metadata={"consumer": "Stage 7 ship gate (per-phase landed date)"})
    sidecar: dict = field(default_factory=dict, metadata={"sidecar_rationale": "backend-specific per-phase decoration"})


@dataclass
class EpicData:
    schema_version: int = field(default=SCHEMA_VERSION, metadata={"consumer": "adapter version negotiation"})
    slug: str = field(default="", metadata={"consumer": "adapter identity"})
    status: str = field(default="proposed", metadata={"consumer": "Stage 7 ship gate; audit status-drift (carve-out)"})
    started: Optional[str] = field(default=None, metadata={"consumer": "Stage 7 ship gate (range boundary); required if status != 'proposed'"})
    landed: Optional[str] = field(default=None, metadata={"consumer": "Stage 7 ship gate; required if status == 'done'"})
    aim: str = field(default="", metadata={"consumer": "Foundation elicitation gate (reuse check)"})
    intention: str = field(default="", metadata={"consumer": "Foundation elicitation gate"})
    out_of_scope: list = field(default_factory=list, metadata={"consumer": "Foundation elicitation gate"})
    phases: list = field(default_factory=list, metadata={"consumer": "close procedure; ROADMAP rollup (carve-out)"})
    retrospective: list = field(default_factory=list, metadata={"consumer": "close procedure (append on close)"})
    open_questions: list = field(default_factory=list, metadata={"consumer": "Foundation gate (sentinel injection); audit (carve-out)"})
    sidecar: dict = field(default_factory=dict, metadata={"sidecar_rationale": "epic-level backend decoration (retro_scanned, pivots, retrospective_body_markdown)"})
