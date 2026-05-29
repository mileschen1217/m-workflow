#!/usr/bin/env python3
"""Local-markdown adapter CLI — AC-10 surface.

Subcommands: read / write / list / exists.
Exit codes per spec §Adapter CLI surface (0-9).

Stdout: clean JSON (or empty for exists).
Stderr: <ErrorClassName>: <message> on every non-zero exit.

Root directory taken from $EPIC_ROOT or $CLAUDE_PROJECT_DIR/.touchstone/epics.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

# Register hyphenated-directory aliases so `epic_driven_roadmap` resolves from `skills/`
import types as _types
_root_path = Path(__file__).resolve().parents[3]  # → skills/
for _qname, _relpath in [
    ("epic_driven_roadmap", "epic-driven-roadmap"),
    ("epic_driven_roadmap.adapters", "epic-driven-roadmap/adapters"),
    ("epic_driven_roadmap.adapters.local_markdown", "epic-driven-roadmap/adapters/local-markdown"),
]:
    if _qname not in sys.modules:
        _m = _types.ModuleType(_qname)
        _m.__path__ = [str(_root_path / _relpath)]
        sys.modules[_qname] = _m

from epic_driven_roadmap.adapters.local_markdown import adapter as A  # noqa: E402
from epic_driven_roadmap.adapters.local_markdown import schema as S  # noqa: E402

EXIT_MAP = {
    S.EpicNotFound: 2,
    S.SchemaValidationError: 3,
    S.SchemaVersionMismatch: 4,
    S.CanonicalSerialisationError: 5,
    S.SidecarUnstorableError: 6,
    S.StructuralHostMissingError: 7,
    S.AdapterNotFoundError: 8,
    S.AdapterInternalError: 9,
}


def _root() -> Path:
    env = os.environ.get("EPIC_ROOT")
    if env:
        return Path(env)
    project = os.environ.get("CLAUDE_PROJECT_DIR", ".")
    return Path(project) / ".touchstone" / "epics"


def _emit_error(e: BaseException) -> int:
    for cls, code in EXIT_MAP.items():
        if isinstance(e, cls):
            sys.stderr.write(f"{type(e).__name__}: {e}\n")
            return code
    sys.stderr.write(f"AdapterInternalError: {type(e).__name__}: {e}\n")
    return 9


def _epicdata_to_dict(d: S.EpicData) -> dict:
    out = dataclasses.asdict(d)
    return out


def _dict_to_epicdata(d: dict) -> S.EpicData:
    # M2 — intersect payload keys with EpicData fields; route unknown JSON keys
    # into epic-level sidecar so payload round-trips cleanly (no bare TypeError).
    epic_field_names = set(S.EpicData.__dataclass_fields__.keys())
    phase_field_names = set(S.PhaseData.__dataclass_fields__.keys())

    raw_phases = d.get("phases", []) or []
    phases: list = []
    for p in raw_phases:
        ph_kwargs = {k: v for k, v in p.items() if k in phase_field_names}
        ph = S.PhaseData(**ph_kwargs)
        # extra per-phase keys → phase sidecar
        for k, v in p.items():
            if k not in phase_field_names and k != "sidecar":
                ph.sidecar[k] = v
        phases.append(ph)

    kwargs = {k: v for k, v in d.items() if k in epic_field_names and k != "phases"}
    epic = S.EpicData(**kwargs)
    epic.phases = phases
    # extra epic-level keys → sidecar
    for k, v in d.items():
        if k not in epic_field_names:
            epic.sidecar[k] = v
    return epic


def _wrap(fn):
    """Decorator: typed-error pass-through above, catch-all → AdapterInternalError
    (exit 9) below. The catch-all is the bottom of every subcommand's stack so
    spec AC-10 (exit 9 on each subcommand) is satisfied via the real code path."""
    def inner(adapter, args):
        try:
            return fn(adapter, args)
        except S.AdapterError:
            raise  # typed errors handled by main()'s _emit_error
        except Exception as e:
            raise S.AdapterInternalError(cause=f"{type(e).__name__}: {e}")
    return inner


@_wrap
def cmd_read(adapter: A.LocalMarkdownAdapter, args: argparse.Namespace) -> int:
    data = adapter.read(args.slug)
    json.dump(_epicdata_to_dict(data), sys.stdout)
    sys.stdout.write("\n")
    return 0


@_wrap
def cmd_write(adapter: A.LocalMarkdownAdapter, args: argparse.Namespace) -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as e:
        raise S.SchemaValidationError(field="<stdin>", reason=f"json: {e}")
    data = _dict_to_epicdata(payload)
    adapter.write(args.slug, data)
    return 0


@_wrap
def cmd_list(adapter: A.LocalMarkdownAdapter, args: argparse.Namespace) -> int:
    json.dump(adapter.list(), sys.stdout)
    sys.stdout.write("\n")
    return 0


@_wrap
def cmd_exists(adapter: A.LocalMarkdownAdapter, args: argparse.Namespace) -> int:
    return 0 if adapter.exists(args.slug) else 1


def main() -> int:
    # NOTE: no test-only env-var crash hook. Test injection patches the
    # adapter method (via PYTHONPATH sitecustomize.py) so the real
    # try/except-AdapterInternalError code path is exercised end-to-end.
    p = argparse.ArgumentParser()
    sp = p.add_subparsers(dest="cmd", required=True)

    pr = sp.add_parser("read"); pr.add_argument("--slug", required=True); pr.set_defaults(fn=cmd_read)
    pw = sp.add_parser("write"); pw.add_argument("--slug", required=True); pw.add_argument("--stdin", action="store_true"); pw.set_defaults(fn=cmd_write)
    pl = sp.add_parser("list"); pl.set_defaults(fn=cmd_list)
    pe = sp.add_parser("exists"); pe.add_argument("--slug", required=True); pe.set_defaults(fn=cmd_exists)

    args = p.parse_args()
    adapter = A.LocalMarkdownAdapter(root=_root())
    try:
        return args.fn(adapter, args)
    except S.AdapterError as e:
        return _emit_error(e)
    except Exception as e:
        # belt-and-braces — should never trigger since each cmd_* is @_wrap-ed
        return _emit_error(S.AdapterInternalError(cause=f"{type(e).__name__}: {e}"))


if __name__ == "__main__":
    sys.exit(main())
