"""AC-8 (b) — Stage 7 reckoning reads landed/status via the CLI."""
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

CLI = Path(__file__).resolve().parents[2] / "adapters" / "local-markdown" / "cli.py"


def _read(root, slug):
    env = os.environ.copy()
    env["EPIC_ROOT"] = str(root)
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[5])
    return subprocess.run(
        [sys.executable, str(CLI), "read", "--slug", slug],
        capture_output=True, text=True, env=env,
    )


def test_stage7_reads_all_phases_landed_via_cli(tmp_path):
    (tmp_path / "ep").mkdir()
    (tmp_path / "ep" / "index.md").write_text(textwrap.dedent("""\
        ---
        schema_version: 1
        slug: ep
        status: done
        started: 2026-05-01
        landed: 2026-05-25
        ---

        **Aim:** x.

        ## Foundation

        ## Phases

        | n | title | status | landed |
        |---|---|---|---|
        | 1 | A | done | 2026-05-10 |
        | 2 | B | done | 2026-05-20 |

        ## Retrospective

        ## Open Questions
        """))

    r = _read(tmp_path, "ep")
    assert r.returncode == 0
    data = json.loads(r.stdout)
    all_phases_landed = all(p["landed"] for p in data["phases"])
    assert all_phases_landed
    assert data["status"] == "done"
    assert data["landed"] == "2026-05-25"
