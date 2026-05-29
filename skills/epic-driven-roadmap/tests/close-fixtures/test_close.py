"""AC-8 (a) — close on a clean epic exercises adapter read+write through CLI."""
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

CLI = Path(__file__).resolve().parents[2] / "adapters" / "local-markdown" / "cli.py"


def _run(root, *args, stdin=None):
    env = os.environ.copy()
    env["EPIC_ROOT"] = str(root)
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[5])
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        capture_output=True, text=True, input=stdin, env=env,
    )


def test_close_appends_retrospective_via_cli(tmp_path):
    (tmp_path / "ep").mkdir()
    (tmp_path / "ep" / "index.md").write_text(textwrap.dedent("""\
        ---
        schema_version: 1
        slug: ep
        status: active
        started: 2026-05-01
        ---

        **Aim:** ship.

        ## Foundation

        ## Phases

        | n | title | status | landed |
        |---|---|---|---|
        | 1 | Phase 1 | done | 2026-05-15 |

        ## Retrospective

        ## Open Questions
        """))

    # close procedure: read, mutate status+landed+retrospective, write
    r = _run(tmp_path, "read", "--slug", "ep")
    assert r.returncode == 0
    data = json.loads(r.stdout)
    data["status"] = "done"
    data["landed"] = "2026-05-20"
    data["retrospective"].append("Shipped clean.")

    w = _run(tmp_path, "write", "--slug", "ep", "--stdin", stdin=json.dumps(data))
    assert w.returncode == 0, w.stderr

    r2 = _run(tmp_path, "read", "--slug", "ep")
    assert r2.returncode == 0
    after = json.loads(r2.stdout)
    assert after["status"] == "done"
    assert after["landed"] == "2026-05-20"
    assert "Shipped clean." in after["retrospective"]
