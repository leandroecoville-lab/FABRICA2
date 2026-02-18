from __future__ import annotations

import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path


def _run_cli(args: list[str], env: dict[str,str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-m", "app.cli"] + args, cwd=cwd, env=env, capture_output=True, text=True)


def test_leak_check_pass_and_fail(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[2]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root / "services" / "pack-factory") + os.pathsep + str(repo_root)
    policy = repo_root / "governance" / "audience_policy.team_pack0_only.v1.json"

    # PASS zip (only allowed prefixes)
    good = tmp_path / "good.zip"
    with zipfile.ZipFile(good, "w") as z:
        z.writestr("docs/PLAN.md", "x")
        z.writestr("02_INVENTORY/manifest.json", '{"schema_version":"1.0","pack_id":"lai-pack-factory","version":"0.0.0","created_at":"x","modules":[],"entrypoints":[],"trace":{"trace_id":"t"}}')
    out_good = tmp_path / "good_report.json"
    r1 = _run_cli(["leak-check","--target", str(good), "--policy", str(policy), "--out", str(out_good), "--trace","t1"], env, repo_root)
    assert r1.returncode == 0, (r1.stderr + r1.stdout)
    rep1 = json.loads(out_good.read_text(encoding="utf-8"))
    assert rep1["status"] == "PASS"

    # FAIL zip (deny prefix)
    bad = tmp_path / "bad.zip"
    with zipfile.ZipFile(bad, "w") as z:
        z.writestr("docs/PLAN.md", "x")
        z.writestr("history/chain_state.json", "{}")
        z.writestr("02_INVENTORY/manifest.json", '{"schema_version":"1.0","pack_id":"lai-pack-factory","version":"0.0.0","created_at":"x","modules":[],"entrypoints":[],"trace":{"trace_id":"t"}}')
    out_bad = tmp_path / "bad_report.json"
    r2 = _run_cli(["leak-check","--target", str(bad), "--policy", str(policy), "--out", str(out_bad), "--trace","t2"], env, repo_root)
    assert r2.returncode != 0
    rep2 = json.loads(out_bad.read_text(encoding="utf-8"))
    assert rep2["status"] == "FAIL"
    assert rep2["counts"]["violations"] >= 1
