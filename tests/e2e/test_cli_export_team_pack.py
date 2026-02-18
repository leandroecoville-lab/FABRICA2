from __future__ import annotations

import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path


def _run_cli(args: list[str], env: dict[str,str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-m", "app.cli"] + args, cwd=cwd, env=env, capture_output=True, text=True)


def test_export_team_pack_filters_restricted(tmp_path: Path):
    # create input zip with restricted paths
    inzip = tmp_path / "in.zip"
    with zipfile.ZipFile(inzip, "w") as z:
        z.writestr("docs/ok.md", "x")
        z.writestr("docs/references/secret.pdf", "pdf")
        z.writestr("02_INVENTORY/semantic_index/x.jsonl", "y")
        z.writestr("gpt_builder/secret.md", "z")
        z.writestr("README.md", "root")
        z.writestr("02_INVENTORY/manifest.json", '{"schema_version":"1.0","pack_id":"lai-pack-factory","version":"0.0.0","created_at":"x","modules":[],"entrypoints":[],"trace":{"trace_id":"t"}}')

    outzip = tmp_path / "team.zip"
    repo_root = Path(__file__).resolve().parents[2]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root / "services" / "pack-factory") + os.pathsep + str(repo_root)

    r = _run_cli(["export-team-pack","--in", str(inzip),"--out", str(outzip),"--trace","t1"], env, repo_root)
    assert r.returncode == 0, r.stderr
    assert outzip.exists()

    with zipfile.ZipFile(outzip, "r") as z:
        names = z.namelist()
    assert "docs/ok.md" in names
    assert not any(n.startswith("docs/references/") for n in names)
    assert not any(n.startswith("02_INVENTORY/semantic_index/") for n in names)
    assert not any(n.startswith("gpt_builder/") for n in names)
