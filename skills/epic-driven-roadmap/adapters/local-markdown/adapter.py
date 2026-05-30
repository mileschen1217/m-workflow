"""Local-markdown reference storage adapter.

read/write/list/exists for .touchstone/epics/<slug>/index.md.
Atomic-or-throw on write (tmp + os.rename).
"""
from __future__ import annotations

import hashlib
import os
import re
from dataclasses import asdict
from pathlib import Path

from . import schema as S
from .schema import (
    AdapterInternalError,
    CanonicalSerialisationError,
    EpicData,
    EpicNotFound,
    PhaseData,
    SCHEMA_VERSION,
    SchemaValidationError,
    SchemaVersionMismatch,
    SidecarUnstorableError,
    StructuralHostMissingError,
    validate_sidecar_value,
)

CANONICAL_FRONTMATTER_KEYS = {
    "schema_version", "slug", "status", "started", "landed",
}
SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)

# ---------- stdlib frontmatter parser / emitter ----------

_BARE_KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):(.*)$")
_LIST_ITEM_RE = re.compile(r"^  - (.*)$")
_DICT_PAIR_RE = re.compile(r"^  ([A-Za-z_][A-Za-z0-9_]*): (.*)$")
_BLOCK_HEAD_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):\s*([|>])\s*$")
_INT_RE = re.compile(r"^-?\d+$")


def _strip_inline_comment(s: str) -> str:
    """Strip a trailing YAML inline comment (` #...`) from an unquoted scalar string.

    Handles both ` # comment` (space-hash) and leading-hash-only (`# comment`)
    as seen in hand-authored frontmatter.
    """
    # If the whole thing is a comment token, treat as empty
    if s.startswith("#"):
        return ""
    # Strip ` # comment` suffix (YAML spec: space before hash)
    idx = s.find(" #")
    if idx != -1:
        return s[:idx].rstrip()
    return s


def _parse_scalar(raw: str, slug: str, lineno: int):
    """Coerce a raw scalar string to None / int / str. Reject unsupported syntax."""
    s = _strip_inline_comment(raw.strip())
    if s == "" or s == "null" or s == "~":
        return None
    # reject flow-style on a scalar slot
    if (s.startswith("[") and s.endswith("]")) or (s.startswith("{") and s.endswith("}")):
        raise S.SchemaValidationError(
            field="<frontmatter>", slug=slug,
            reason=f"flow-style not supported (line {lineno})",
        )
    # reject anchors / aliases
    if s.startswith("&") or s.startswith("*"):
        raise S.SchemaValidationError(
            field="<frontmatter>", slug=slug,
            reason=f"anchors/aliases not supported (line {lineno})",
        )
    # strip matched quotes
    if len(s) >= 2 and ((s[0] == s[-1] == '"') or (s[0] == s[-1] == "'")):
        return s[1:-1]
    # int?
    if _INT_RE.fullmatch(s):
        return int(s)
    return s


def _parse_frontmatter(text: str, slug: str) -> dict:
    """Parse a frontmatter block (text between the --- delimiters) into a dict.

    Supported subset: flat key:value (str/int/null), list[str], dict[str,str].
    Anything outside the subset raises SchemaValidationError.
    """
    lines = text.splitlines()
    out: dict = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip() == "" or line.strip().startswith("#"):
            i += 1
            continue
        if _BLOCK_HEAD_RE.match(line):
            raise S.SchemaValidationError(
                field="<frontmatter>", slug=slug,
                reason=f"multiline block scalar (|/>) not supported (line {i + 1})",
            )
        m = _BARE_KEY_RE.match(line)
        if not m:
            raise S.SchemaValidationError(
                field="<frontmatter>", slug=slug,
                reason=f"malformed line {i + 1}: {line!r}",
            )
        key, rest = m.group(1), m.group(2)
        rest_stripped = rest.strip()
        if rest_stripped:
            # scalar on same line
            out[key] = _parse_scalar(rest, slug, i + 1)
            i += 1
            continue
        # rest is empty — look at next lines for list or dict children
        j = i + 1
        child_lines = []
        while j < len(lines) and lines[j].startswith("  "):
            if lines[j].strip() == "":
                break
            child_lines.append((j, lines[j]))
            j += 1
        if not child_lines:
            out[key] = None
            i = j
            continue
        # decide list vs dict by first child line
        first = child_lines[0][1]
        if _LIST_ITEM_RE.match(first):
            items = []
            for ln_no, ln in child_lines:
                mm = _LIST_ITEM_RE.match(ln)
                if not mm:
                    raise S.SchemaValidationError(
                        field=key, slug=slug,
                        reason=f"mixed list/dict children (line {ln_no + 1})",
                    )
                item_raw = mm.group(1)
                # reject nested list items (e.g. "  - - nested")
                if item_raw.lstrip().startswith("-"):
                    raise S.SchemaValidationError(
                        field=key, slug=slug,
                        reason=f"nested list items not supported (line {ln_no + 1})",
                    )
                val = _parse_scalar(item_raw, slug, ln_no + 1)
                if not isinstance(val, str):
                    raise S.SchemaValidationError(
                        field=key, slug=slug,
                        reason=f"non-str list item (line {ln_no + 1})",
                    )
                items.append(val)
            out[key] = items
        elif _DICT_PAIR_RE.match(first):
            d: dict = {}
            for ln_no, ln in child_lines:
                mm = _DICT_PAIR_RE.match(ln)
                if not mm:
                    raise S.SchemaValidationError(
                        field=key, slug=slug,
                        reason=f"mixed list/dict children (line {ln_no + 1})",
                    )
                k2, v2 = mm.group(1), mm.group(2).strip()
                val = _parse_scalar(v2, slug, ln_no + 1)
                if not isinstance(val, str):
                    raise S.SchemaValidationError(
                        field=key, slug=slug,
                        reason=f"non-str dict value (line {ln_no + 1})",
                    )
                d[k2] = val
            out[key] = d
        else:
            raise S.SchemaValidationError(
                field=key, slug=slug,
                reason=f"unsupported child syntax (line {child_lines[0][0] + 1})",
            )
        i = j
    return out


def _emit_scalar(v) -> str:
    """Emit a scalar value as a YAML-compatible string."""
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    s = str(v)
    # quote strings that would be misread by the parser
    if s == "" or s in ("null", "~", "true", "false") or _INT_RE.fullmatch(s):
        return f'"{s}"'
    if any(ch in s for ch in (':', '#', '\n', '[', ']', '{', '}', '&', '*', '|', '>', '"', "'")):
        # double-quoted form, escape backslash + double quote
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def _emit_frontmatter(fm: dict) -> str:
    """Emit a frontmatter dict to a YAML-subset string (no surrounding --- markers)."""
    parts: list[str] = []
    for k, v in fm.items():
        if isinstance(v, list):
            parts.append(f"{k}:")
            for item in v:
                if not isinstance(item, str):
                    raise CanonicalSerialisationError(field=k, backend="local-markdown")
                parts.append(f"  - {_emit_scalar(item)}")
        elif isinstance(v, dict):
            parts.append(f"{k}:")
            for k2, v2 in v.items():
                if not isinstance(v2, str):
                    raise CanonicalSerialisationError(field=k, backend="local-markdown")
                parts.append(f"  {k2}: {_emit_scalar(v2)}")
        else:
            parts.append(f"{k}: {_emit_scalar(v)}")
    return "\n".join(parts)
AIM_RE = re.compile(r"^\*\*Aim:\*\*[ \t]*(.*?)[ \t]*$", re.MULTILINE)
BULLET_RE = re.compile(r"^-\s+(.+?)\s*$", re.MULTILINE)
INTENTION_BULLET_RE = re.compile(r"^-\s+Intention:\s*(.+?)\s*$", re.MULTILINE)
OOS_BULLET_RE = re.compile(r"^-\s+Out of scope:\s*(.+?)\s*$", re.MULTILINE)
PHASE_ROW_RE = re.compile(
    # Capture the four primary columns; allow any number of trailing | cells
    # (6-column rows with spec/plan sidecar columns must still match).
    # Use [ \t]* (not \s*) to prevent matching across newlines.
    r"^\|[ \t]*(\d+)[ \t]*\|[ \t]*([^\n|]+?)[ \t]*\|[ \t]*([a-z]+)[ \t]*\|[ \t]*([^\n|]*?)[ \t]*\|(?:[ \t]*[^\n|]*[ \t]*\|)*[ \t]*$",
    re.MULTILINE,
)


class LocalMarkdownAdapter:
    def __init__(self, root: Path):
        self.root = Path(root)

    # ---------- public surface ----------

    def list(self) -> list[str]:
        if not self.root.exists():
            return []
        out = []
        for child in sorted(self.root.iterdir()):
            if not child.is_dir():
                continue
            if (child / "index.md").exists():
                out.append(child.name)
        return out

    def exists(self, slug: str) -> bool:
        return (self.root / slug / "index.md").exists()

    def read(self, slug: str) -> EpicData:
        path = self.root / slug / "index.md"
        if not path.exists():
            raise EpicNotFound(slug=slug)
        text = path.read_text()
        return self._parse(text, slug=slug)

    # ---------- write ----------

    def write(self, slug: str, data: EpicData) -> None:
        # Slug discipline (path-vs-data mismatch)
        if not slug:
            raise SchemaValidationError(field="slug", reason="slug required")
        if not data.slug:
            raise SchemaValidationError(field="slug", slug=slug, reason="slug required")
        if data.slug != slug:
            raise SchemaValidationError(field="slug", slug=slug, reason="path/data mismatch")

        # Stamp schema_version
        data.schema_version = SCHEMA_VERSION

        # Validate sidecar tag shapes BEFORE touching disk
        for k, v in (data.sidecar or {}).items():
            try:
                validate_sidecar_value(v)
            except SidecarUnstorableError as e:
                raise SidecarUnstorableError(
                    field=f"sidecar.{k}", backend="local-markdown", reason=e.reason,
                )
        for i, ph in enumerate(data.phases or []):
            for k, v in (ph.sidecar or {}).items():
                try:
                    validate_sidecar_value(v)
                except SidecarUnstorableError as e:
                    raise SidecarUnstorableError(
                        field=f"phases[{i}].sidecar.{k}", backend="local-markdown", reason=e.reason,
                    )

        # Phases-table cell host can only carry `str` tag.
        # list[str] / dict[str, str] are valid SidecarValue at the schema
        # layer but cannot be expressed in a single table cell — refuse
        # rather than coerce (tag preservation).
        for i, ph in enumerate(data.phases or []):
            for k, v in (ph.sidecar or {}).items():
                if isinstance(v, list):
                    raise SidecarUnstorableError(
                        field=f"phases[{i}].sidecar.{k}",
                        backend="local-markdown",
                        reason=(
                            "list[str] cannot be expressed in a "
                            "Phases-table cell — promote to epic-level "
                            "sidecar (YAML frontmatter) or use a "
                            "sidecar-only schema bump"
                        ),
                    )
                if isinstance(v, dict):
                    raise SidecarUnstorableError(
                        field=f"phases[{i}].sidecar.{k}",
                        backend="local-markdown",
                        reason=(
                            "dict[str, str] cannot be expressed in a "
                            "Phases-table cell — promote to epic-level "
                            "sidecar (YAML frontmatter) or use a "
                            "sidecar-only schema bump"
                        ),
                    )
                if isinstance(v, str) and "|" in v:
                    raise SidecarUnstorableError(
                        field=f"phases[{i}].sidecar.{k}",
                        backend="local-markdown",
                        reason=(
                            "phase-sidecar str value contains a literal "
                            "'|' which cannot be expressed in a "
                            "Phases-table cell without breaking row "
                            "delimitation — promote to epic-level sidecar "
                            "(YAML frontmatter) or strip the pipe upstream"
                        ),
                    )

        # Conditional-required canonical rules. 'cancelled' is exempted.
        if data.status in ("active", "paused", "done") and data.started is None:
            raise SchemaValidationError(
                field="started", slug=slug, reason=f"required when status == {data.status!r}",
            )
        if data.status == "done" and data.landed is None:
            raise SchemaValidationError(
                field="landed", slug=slug, reason="required when status == done",
            )

        target_dir = self.root / slug
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / "index.md"
        tmp = target_dir / f"index.md.tmp.{os.getpid()}"

        try:
            try:
                text = self._serialise(data)
            except (CanonicalSerialisationError, SidecarUnstorableError):
                self._cleanup_tmp(target_dir)
                raise
            tmp.write_text(text)
            os.rename(tmp, target)
        except (CanonicalSerialisationError, SidecarUnstorableError):
            self._cleanup_tmp(target_dir)
            raise
        except Exception as e:
            self._cleanup_tmp(target_dir)
            raise AdapterInternalError(cause=f"{type(e).__name__}: {e}")

    def _cleanup_tmp(self, target_dir: Path) -> None:
        for stray in target_dir.glob("index.md.tmp.*"):
            try:
                stray.unlink()
            except OSError:
                pass

    def _serialise(self, data: EpicData) -> str:
        # frontmatter
        fm = {
            "schema_version": data.schema_version,
            "slug": data.slug,
            "status": data.status,
            "started": data.started,
            "landed": data.landed,
        }
        for k, v in (data.sidecar or {}).items():
            # only str / list[str] / dict[str,str] reach here (validated upstream)
            if k not in fm:
                fm[k] = v
        fm_text = _emit_frontmatter(fm)

        parts = ["---", fm_text, "---", ""]
        parts.append(f"**Aim:** {data.aim}")
        parts.append("")
        parts.append("## Foundation")
        parts.append("")
        if data.intention:
            parts.append(f"- Intention: {data.intention}")
        for o in data.out_of_scope:
            parts.append(f"- Out of scope: {o}")
        parts.append("")
        parts.append("## Phases")
        parts.append("")
        if data.phases:
            # Collect union of phase sidecar keys (preserve first-seen order)
            extra_cols: list[str] = []
            seen: set[str] = set()
            for ph in data.phases:
                for k in (ph.sidecar or {}):
                    if k not in seen:
                        seen.add(k); extra_cols.append(k)
            header = ["n", "title", "status", "landed"] + extra_cols
            parts.append("| " + " | ".join(header) + " |")
            parts.append("|" + "|".join("---" for _ in header) + "|")
            for ph in data.phases:
                cells = [str(ph.n), ph.title, ph.status, ph.landed or ""]
                for col in extra_cols:
                    val = (ph.sidecar or {}).get(col, "")
                    assert isinstance(val, str), (
                        f"phases[].sidecar.{col} reached _serialise as "
                        f"{type(val).__name__}; host-capability guard "
                        f"in write() must have been bypassed"
                    )
                    cells.append(val)
                parts.append("| " + " | ".join(cells) + " |")
        parts.append("")
        parts.append("## Retrospective")
        parts.append("")
        for r in data.retrospective:
            parts.append(f"- {r}")
        parts.append("")
        parts.append("## Open Questions")
        parts.append("")
        for q in data.open_questions:
            parts.append(f"- {q}")
        parts.append("")
        return "\n".join(parts)

    # ---------- parse ----------

    def _parse(self, text: str, slug: str) -> EpicData:
        fm, body = self._split_frontmatter(text, slug=slug)
        self._validate_frontmatter(fm, slug=slug)

        epic = EpicData()
        epic.schema_version = int(fm["schema_version"])
        epic.slug = str(fm["slug"])
        epic.status = str(fm["status"])
        epic.started = fm.get("started")
        epic.landed = fm.get("landed")

        # sidecar = unknown frontmatter keys
        for k, v in fm.items():
            if k not in CANONICAL_FRONTMATTER_KEYS:
                try:
                    validate_sidecar_value(v)
                except SidecarUnstorableError:
                    # on read we tolerate broader yaml types by stringifying
                    v = str(v)
                epic.sidecar[k] = v

        # aim
        m = AIM_RE.search(body)
        epic.aim = m.group(1).strip() if m else ""

        sections = self._sections(body)

        # Foundation: parse Intention + Out of scope bullets
        foundation = sections.get("Foundation")
        if foundation is not None:
            mi = INTENTION_BULLET_RE.search(foundation)
            epic.intention = mi.group(1).strip() if mi else ""
            for m_oos in OOS_BULLET_RE.finditer(foundation):
                epic.out_of_scope.append(m_oos.group(1).strip())

        # Phases table
        phases_section = sections.get("Phases")
        if phases_section is not None:
            for m_row in PHASE_ROW_RE.finditer(phases_section):
                landed_raw = m_row.group(4).strip()
                ph_status = m_row.group(3).strip()
                # phase.status must be one of STATUS_VALUES
                if ph_status not in S.STATUS_VALUES:
                    raise SchemaValidationError(
                        field=f"phases[{int(m_row.group(1))}].status",
                        slug=slug,
                        reason=f"invalid status value: {ph_status!r}",
                    )
                epic.phases.append(PhaseData(
                    n=int(m_row.group(1)),
                    title=m_row.group(2).strip(),
                    status=ph_status,
                    landed=landed_raw if landed_raw else None,
                ))

        # Phase sidecar — extra columns beyond (n, title, status, landed).
        # Header-driven split: index each row's cells by column position.
        if phases_section is not None and epic.phases:
            # Find the header row (first table row in the section that starts with `|`)
            header_match = None
            for line in phases_section.splitlines():
                if line.lstrip().startswith("|") and "n" in line.lower():
                    header_match = line
                    break
            if header_match:
                # Split header on `|`, strip, drop leading/trailing empties from
                # the outer pipes.
                cols = [c.strip() for c in header_match.split("|")]
                cols = [c for c in cols if c != ""]
                extra_cols = cols[4:]  # past n / title / status / landed
                if extra_cols:
                    # Build slug→PhaseData lookup by n.
                    by_n = {ph.n: ph for ph in epic.phases}
                    for line in phases_section.splitlines():
                        s = line.strip()
                        if not s.startswith("|"):
                            continue
                        # Skip header and separator (---|---|...)
                        if "---" in s:
                            continue
                        cells = [c.strip() for c in s.split("|")]
                        cells = [c for c in cells if c != ""]
                        if not cells or not cells[0].isdigit():
                            continue
                        n = int(cells[0])
                        ph = by_n.get(n)
                        if ph is None:
                            continue
                        for i, col_name in enumerate(extra_cols):
                            idx = 4 + i
                            if idx >= len(cells):
                                continue
                            val = cells[idx]
                            if val:
                                ph.sidecar[col_name] = val

        # Retrospective bullets
        retro = sections.get("Retrospective")
        if retro is not None:
            epic.retrospective = [m.group(1).strip() for m in BULLET_RE.finditer(retro)]

        # Open Questions — host MUST exist; absence is StructuralHostMissingError
        if "Open Questions" not in sections:
            raise StructuralHostMissingError(field="open_questions")
        oq = sections["Open Questions"]
        epic.open_questions = [m.group(1).strip() for m in BULLET_RE.finditer(oq)]

        # conditional-required: started if status in {active, paused, done}; landed if status == done.
        # 'cancelled' is a terminal status exempted — epics folded before work began legitimately
        # have no started date.
        if epic.status in ("active", "paused", "done") and epic.started is None:
            raise SchemaValidationError(
                field="started", slug=slug, schema_version=epic.schema_version,
                reason=f"required when status == {epic.status!r}",
            )
        if epic.status == "done" and epic.landed is None:
            raise SchemaValidationError(
                field="landed", slug=slug, schema_version=epic.schema_version,
                reason="required when status == done",
            )

        return epic

    def _split_frontmatter(self, text: str, slug: str):
        if not text.startswith("---\n"):
            raise SchemaValidationError(field="<frontmatter>", slug=slug, reason="missing frontmatter delimiter")
        end = text.find("\n---\n", 4)
        if end < 0:
            raise SchemaValidationError(field="<frontmatter>", slug=slug, reason="unterminated frontmatter")
        fm_text = text[4:end]
        body = text[end + 5 :]
        fm = _parse_frontmatter(fm_text, slug=slug)
        if not isinstance(fm, dict):
            raise SchemaValidationError(field="<frontmatter>", slug=slug, reason="frontmatter not a mapping")
        return fm, body

    def _validate_frontmatter(self, fm: dict, slug: str) -> None:
        # Legacy accommodation: pre-adapter epics lack schema_version. Default to
        # version 1 and let write() stamp it explicitly on next save.
        if "schema_version" not in fm:
            fm["schema_version"] = SCHEMA_VERSION
        try:
            sv = int(fm["schema_version"])
        except (TypeError, ValueError):
            raise SchemaValidationError(field="schema_version", slug=slug, reason="not an integer")
        if sv != SCHEMA_VERSION:
            raise SchemaVersionMismatch(found=sv, expected=SCHEMA_VERSION)
        for required in ("slug", "status"):
            if required not in fm:
                raise SchemaValidationError(field=required, slug=slug, reason="missing")
        if fm["status"] not in S.STATUS_VALUES:
            raise SchemaValidationError(field="status", slug=slug, reason=f"unknown status: {fm['status']}")

    def _sections(self, body: str) -> dict[str, str]:
        out: dict[str, str] = {}
        matches = list(SECTION_RE.finditer(body))
        for i, m in enumerate(matches):
            name = m.group(1).strip()
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
            out[name] = body[start:end]
        return out
