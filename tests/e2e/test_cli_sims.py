from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def _run_cli(args: list[str], env: dict[str,str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-m", "app.cli"] + args, cwd=cwd, env=env, capture_output=True, text=True)


def test_cli_sims_generate_reports(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[2]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root / "services" / "pack-factory") + os.pathsep + str(repo_root)

    out1 = tmp_path / "connect.json"
    r1 = _run_cli(["connect-sim","--out", str(out1),"--trace","s1"], env, repo_root)
    assert r1.returncode == 0, r1.stderr
    data1 = json.loads(out1.read_text(encoding="utf-8"))
    assert data1["overall_status"] in ("PASS","FAIL")
    assert data1["events_count"] >= 1

    out2 = tmp_path / "app.json"
    r2 = _run_cli(["app-sim","--out", str(out2),"--trace","s2"], env, repo_root)
    assert r2.returncode == 0, r2.stderr
    data2 = json.loads(out2.read_text(encoding="utf-8"))
    assert data2["events_count"] >= 1

    out3 = tmp_path / "cp.json"
    r3 = _run_cli(["culture-people-sim","--out", str(out3),"--trace","s3"], env, repo_root)
    assert r3.returncode == 0, r3.stderr
    data3 = json.loads(out3.read_text(encoding="utf-8"))
    assert data3["events_count"] >= 1
