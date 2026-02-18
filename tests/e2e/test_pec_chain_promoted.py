from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

def _run_cli(args: list[str], env: dict[str,str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-m", "app.cli"] + args, cwd=cwd, env=env, capture_output=True, text=True)

def test_pec_chain_promoted_flow(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[2]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root / "services" / "pack-factory")
    env["LAI_ACTOR_ID"] = "leader-1"

    out_dir = tmp_path / "out"
    tmp_dir = tmp_path / "tmp"
    out_dir.mkdir()
    tmp_dir.mkdir()

    # pack0 meetcore
    r0 = _run_cli(["pack0","--module","meetcore","--out", str(out_dir),"--trace","T0"], env, repo_root)
    assert r0.returncode == 0, r0.stderr
    p0 = next(out_dir.glob("pack0-meetcore-0.0.1.zip"))

    # run-report
    rr_path = out_dir/"run_report.json"
    rr = _run_cli(["run-report","--target", str(p0),"--out", str(rr_path),"--trace","T1"], env, repo_root)
    assert rr.returncode == 0, rr.stderr
    rr_obj = json.loads(rr_path.read_text(encoding="utf-8"))
    assert rr_obj["result"] == "pass"

    # approval
    ap_path = out_dir/"approval.json"
    ap = _run_cli(["approve-pack","--target", str(p0),"--run-report", str(rr_path),"--out", str(ap_path),"--trace","T2"], env, repo_root)
    assert ap.returncode == 0, ap.stderr

    # wrap patches
    prr = out_dir/"patch_rr.zip"
    pap = out_dir/"patch_ap.zip"
    w1 = _run_cli(["wrap-run-report","--in", str(rr_path),"--out", str(prr),"--trace","T3"], env, repo_root)
    assert w1.returncode == 0, w1.stderr
    w2 = _run_cli(["wrap-approval","--in", str(ap_path),"--out", str(pap),"--trace","T4"], env, repo_root)
    assert w2.returncode == 0, w2.stderr

    # merge promoted
    snap = out_dir/"snapshot.zip"
    m = _run_cli(["merge","--mode","promoted","--inputs", str(p0), str(prr), str(pap),"--out", str(snap),"--tmp", str(tmp_dir),"--trace","T5"], env, repo_root)
    assert m.returncode == 0, m.stderr
    assert snap.exists()

    # maint status
    ms_path = out_dir/"maint_status.json"
    ms = _run_cli(["maint","status","--snapshot", str(snap),"--out", str(ms_path),"--trace","T6"], env, repo_root)
    assert ms.returncode == 0, ms.stderr
    ms_obj = json.loads(ms_path.read_text(encoding="utf-8"))
    assert "chain_state" in ms_obj

    # maint gate-next (expected OK)
    gate_ok_path = out_dir/"gate_ok.json"
    g1 = _run_cli(["maint","gate-next","--snapshot", str(snap),"--expected","pack1","--out", str(gate_ok_path),"--trace","T6G"], env, repo_root)
    assert g1.returncode == 0, g1.stderr

    # maint gate-next (expected mismatch -> blocked)
    gate_bad_path = out_dir/"gate_bad.json"
    g2 = _run_cli(["maint","gate-next","--snapshot", str(snap),"--expected","pack2","--out", str(gate_bad_path),"--trace","T6B"], env, repo_root)
    assert g2.returncode != 0

    # meetcore sim
    sim_path = out_dir/"meetcore_sim.json"
    sim = _run_cli(["meetcore-sim","--out", str(sim_path),"--trace","T7"], env, repo_root)
    assert sim.returncode == 0, sim.stderr
    sim_obj = json.loads(sim_path.read_text(encoding="utf-8"))
    assert sim_obj["overall_status"] == "PASS"
