"""Foundation reuse check reads aim/intention/out_of_scope via the CLI."""
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

CLI = Path(__file__).resolve().parents[2] / "adapters" / "local-markdown" / "cli.py"


def test_foundation_reuse_reads_aim_intention_oos_via_cli(tmp_path):
    (tmp_path / "ep").mkdir()
    (tmp_path / "ep" / "index.md").write_text(textwrap.dedent("""\
        ---
        schema_version: 1
        slug: ep
        status: active
        started: 2026-05-01
        ---

        **Aim:** ship the adapter.

        ## Foundation

        - Intention: prove the contract.
        - Out of scope: Obsidian backend.
        - Out of scope: concurrency.

        ## Phases

        ## Retrospective

        ## Open Questions
        """))

    env = os.environ.copy()
    env["EPIC_ROOT"] = str(tmp_path)
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[5])
    r = subprocess.run(
        [sys.executable, str(CLI), "read", "--slug", "ep"],
        capture_output=True, text=True, env=env,
    )
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert data["aim"] == "ship the adapter."
    assert data["intention"] == "prove the contract."
    assert set(data["out_of_scope"]) == {"Obsidian backend.", "concurrency."}
