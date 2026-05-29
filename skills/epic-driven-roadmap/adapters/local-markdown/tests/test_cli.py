"""AC-10 — CLI argv + JSON I/O + exit codes 0-9."""
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

CLI = Path(__file__).resolve().parents[1] / "cli.py"


def _run(root: Path, *args: str, stdin: str | None = None):
    env = os.environ.copy()
    env["EPIC_ROOT"] = str(root)
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[5])
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        capture_output=True, text=True, input=stdin, env=env,
    )


def _seed_epic(root: Path, slug: str = "demo") -> None:
    (root / slug).mkdir(parents=True)
    (root / slug / "index.md").write_text(textwrap.dedent("""\
        ---
        schema_version: 1
        slug: demo
        status: active
        started: 2026-05-01
        ---

        **Aim:** x.

        ## Foundation

        - Intention: y.

        ## Phases

        ## Retrospective

        ## Open Questions
        """))


def test_cli_read_success_exit_0_json_stdout(tmp_path):
    _seed_epic(tmp_path)
    r = _run(tmp_path, "read", "--slug", "demo")
    assert r.returncode == 0, r.stderr
    payload = json.loads(r.stdout)
    assert payload["slug"] == "demo"
    assert payload["status"] == "active"


def test_cli_read_missing_slug_exit_2(tmp_path):
    r = _run(tmp_path, "read", "--slug", "nope")
    assert r.returncode == 2
    assert "EpicNotFound" in r.stderr


def test_cli_read_schema_validation_error_exit_3(tmp_path):
    (tmp_path / "bad").mkdir()
    (tmp_path / "bad" / "index.md").write_text(
        "---\nschema_version: 1\nslug: bad\n---\n\n**Aim:** x.\n\n## Foundation\n\n## Phases\n\n## Retrospective\n\n## Open Questions\n"
    )
    r = _run(tmp_path, "read", "--slug", "bad")
    assert r.returncode == 3
    assert "SchemaValidationError" in r.stderr


def test_cli_read_schema_version_mismatch_exit_4(tmp_path):
    (tmp_path / "bad").mkdir()
    (tmp_path / "bad" / "index.md").write_text(
        "---\nschema_version: 99\nslug: bad\nstatus: active\nstarted: 2026-05-01\n---\n\n**Aim:** x.\n\n## Foundation\n\n## Phases\n\n## Retrospective\n\n## Open Questions\n"
    )
    r = _run(tmp_path, "read", "--slug", "bad")
    assert r.returncode == 4
    assert "SchemaVersionMismatch" in r.stderr


def test_cli_read_structural_host_missing_exit_7(tmp_path):
    (tmp_path / "bad").mkdir()
    (tmp_path / "bad" / "index.md").write_text(
        "---\nschema_version: 1\nslug: bad\nstatus: active\nstarted: 2026-05-01\n---\n\n**Aim:** x.\n\n## Foundation\n\n## Phases\n\n## Retrospective\n"
    )
    r = _run(tmp_path, "read", "--slug", "bad")
    assert r.returncode == 7
    assert "StructuralHostMissingError" in r.stderr


def test_cli_write_success_exit_0(tmp_path):
    payload = json.dumps({
        "schema_version": 1, "slug": "new", "status": "active",
        "started": "2026-05-01", "landed": None,
        "aim": "ship", "intention": "", "out_of_scope": [],
        "phases": [], "retrospective": [], "open_questions": [],
        "sidecar": {},
    })
    r = _run(tmp_path, "write", "--slug", "new", "--stdin", stdin=payload)
    assert r.returncode == 0, r.stderr
    assert (tmp_path / "new" / "index.md").exists()


def test_cli_write_path_data_mismatch_exit_3(tmp_path):
    _seed_epic(tmp_path)
    payload = json.dumps({
        "schema_version": 1, "slug": "different", "status": "active",
        "started": "2026-05-01", "landed": None, "aim": "x",
        "intention": "", "out_of_scope": [], "phases": [],
        "retrospective": [], "open_questions": [], "sidecar": {},
    })
    r = _run(tmp_path, "write", "--slug", "demo", "--stdin", stdin=payload)
    assert r.returncode == 3
    assert "SchemaValidationError" in r.stderr


def test_cli_write_sidecar_unstorable_exit_6(tmp_path):
    _seed_epic(tmp_path)
    payload = json.dumps({
        "schema_version": 1, "slug": "demo", "status": "active",
        "started": "2026-05-01", "landed": None, "aim": "x",
        "intention": "", "out_of_scope": [], "phases": [],
        "retrospective": [], "open_questions": [],
        "sidecar": {"bad": 42},
    })
    r = _run(tmp_path, "write", "--slug", "demo", "--stdin", stdin=payload)
    assert r.returncode == 6
    assert "SidecarUnstorableError" in r.stderr


def test_cli_list_exit_0_json_array(tmp_path):
    _seed_epic(tmp_path, "a")
    _seed_epic(tmp_path, "b")
    r = _run(tmp_path, "list")
    assert r.returncode == 0, r.stderr
    assert sorted(json.loads(r.stdout)) == ["a", "b"]


def test_cli_exists_present_exit_0(tmp_path):
    _seed_epic(tmp_path)
    r = _run(tmp_path, "exists", "--slug", "demo")
    assert r.returncode == 0
    assert r.stdout == ""


def test_cli_exists_absent_exit_1(tmp_path):
    r = _run(tmp_path, "exists", "--slug", "nope")
    assert r.returncode == 1
    assert r.stdout == ""


def test_cli_write_unknown_json_key_routes_to_sidecar_exit_0(tmp_path):
    """M2 — unknown payload keys land in epic.sidecar (no bare TypeError → exit 9)."""
    payload = json.dumps({
        "schema_version": 1, "slug": "new", "status": "active",
        "started": "2026-05-01", "landed": None,
        "aim": "ship", "intention": "", "out_of_scope": [],
        "phases": [], "retrospective": [], "open_questions": [],
        "sidecar": {},
        "totally_new_field": "future-value",
    })
    r = _run(tmp_path, "write", "--slug", "new", "--stdin", stdin=payload)
    assert r.returncode == 0, r.stderr
    # round-trip: read back, unknown key should appear in sidecar
    r2 = _run(tmp_path, "read", "--slug", "new")
    assert r2.returncode == 0, r2.stderr
    data = json.loads(r2.stdout)
    assert data["sidecar"].get("totally_new_field") == "future-value"


@pytest.mark.parametrize("subcommand", ["read", "write", "list", "exists"])
def test_cli_internal_error_exit_9_per_subcommand(tmp_path, subcommand):
    """AC-10 exit-9 must trigger on each subcommand when adapter raises an
    uncaught exception. Injection writes a sitecustomize.py into PYTHONPATH
    that monkey-patches the adapter method; production CLI carries NO
    test-only crash hook (the production try/except wraps RuntimeError as
    AdapterInternalError → exit 9)."""
    _seed_epic(tmp_path)

    sc_dir = tmp_path / "_inject"
    sc_dir.mkdir()
    method = {"read": "read", "write": "write", "list": "list", "exists": "exists"}[subcommand]
    repo_root = str(Path(__file__).resolve().parents[5])
    (sc_dir / "sitecustomize.py").write_text(
        "import sys, types\n"
        "from pathlib import Path\n"
        f"_root = Path({repo_root!r})\n"
        "for _qname, _relpath in [\n"
        "    ('epic_driven_roadmap', 'skills/epic-driven-roadmap'),\n"
        "    ('epic_driven_roadmap.adapters', 'skills/epic-driven-roadmap/adapters'),\n"
        "    ('epic_driven_roadmap.adapters.local_markdown', 'skills/epic-driven-roadmap/adapters/local-markdown'),\n"
        "]:\n"
        "    if _qname not in sys.modules:\n"
        "        _m = types.ModuleType(_qname)\n"
        "        _m.__path__ = [str(_root / _relpath)]\n"
        "        sys.modules[_qname] = _m\n"
        "from epic_driven_roadmap.adapters.local_markdown import adapter as A\n"
        "def _boom(self, *a, **kw):\n"
        "    raise RuntimeError('synthetic')\n"
        f"A.LocalMarkdownAdapter.{method} = _boom\n"
    )

    env = os.environ.copy()
    env["EPIC_ROOT"] = str(tmp_path)
    repo_path = str(Path(__file__).resolve().parents[5])
    env["PYTHONPATH"] = f"{sc_dir}{os.pathsep}{repo_path}"

    if subcommand == "read":
        argv = [str(CLI), "read", "--slug", "demo"]
        stdin = None
    elif subcommand == "write":
        argv = [str(CLI), "write", "--slug", "demo", "--stdin"]
        stdin = json.dumps({
            "schema_version": 1, "slug": "demo", "status": "active",
            "started": "2026-05-01", "landed": None, "aim": "x",
            "intention": "", "out_of_scope": [], "phases": [],
            "retrospective": [], "open_questions": [], "sidecar": {},
        })
    elif subcommand == "list":
        argv = [str(CLI), "list"]
        stdin = None
    else:  # exists
        argv = [str(CLI), "exists", "--slug", "demo"]
        stdin = None

    r = subprocess.run(
        [sys.executable, *argv],
        capture_output=True, text=True, input=stdin, env=env,
    )
    assert r.returncode == 9, f"{subcommand}: stderr={r.stderr}"
    assert "AdapterInternalError" in r.stderr
    assert "synthetic" in r.stderr
