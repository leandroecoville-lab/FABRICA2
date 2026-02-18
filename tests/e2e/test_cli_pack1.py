from __future__ import annotations

import os
import subprocess
import sys
import zipfile
from pathlib import Path


def _run_cli(args: list[str], env: dict[str,str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-m", "app.cli"] + args, cwd=cwd, env=env, capture_output=True, text=True)


def test_plan_pack1_generates_zip(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[2]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root / "services" / "pack-factory") + os.pathsep + str(repo_root)

    r = _run_cli(["plan-pack1","--module","lai-connect","--out", str(tmp_path),"--trace","p1"], env, repo_root)
    assert r.returncode == 0, r.stderr
    zips = list(tmp_path.glob("pack1-lai-connect-*.zip"))
    assert zips
    with zipfile.ZipFile(zips[0], "r") as z:
        names = z.namelist()
    assert any(n.endswith("02_INVENTORY/manifest.json") for n in names)
    assert any("services/" in n for n in names)
