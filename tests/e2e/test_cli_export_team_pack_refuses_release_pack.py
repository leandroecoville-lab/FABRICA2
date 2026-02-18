from __future__ import annotations

import os
import subprocess
import sys
import zipfile
from pathlib import Path


def _run_cli(args: list[str], env: dict[str,str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-m", "app.cli"] + args, cwd=cwd, env=env, capture_output=True, text=True)


def test_export_team_pack_refuses_release_pack_input(tmp_path: Path):
    # Fake a "release pack" signature by adding services/pack-factory/app/cli.py
    inzip = tmp_path / "release_like.zip"
    with zipfile.ZipFile(inzip, "w") as z:
        z.writestr("services/pack-factory/app/cli.py", "print('x')")
        z.writestr("02_INVENTORY/manifest.json", '{"schema_version":"1.0","pack_id":"lai-pack-factory","version":"0.0.0","created_at":"x","modules":[],"entrypoints":[],"trace":{"trace_id":"t"}}')

    outzip = tmp_path / "team.zip"
    repo_root = Path(__file__).resolve().parents[2]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root / "services" / "pack-factory") + os.pathsep + str(repo_root)

    r = _run_cli(["export-team-pack","--in", str(inzip),"--out", str(outzip),"--trace","t1"], env, repo_root)
    assert r.returncode != 0
    assert "Release Pack" in (r.stderr + r.stdout)
