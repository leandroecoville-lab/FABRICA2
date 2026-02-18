from __future__ import annotations

import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

def _run_cli(args: list[str], env: dict[str,str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-m", "app.cli"] + args, cwd=cwd, env=env, capture_output=True, text=True)

def test_cli_inventory_scan_ignores_noise(tmp_path: Path):
    zpath = tmp_path / "t.zip"
    with zipfile.ZipFile(zpath, "w") as z:
        z.writestr("__MACOSX/._junk", "x")
        z.writestr(".DS_Store", "x")
        z.writestr("._hidden", "x")
        z.writestr("real/ok.txt", "hello")

    out = tmp_path / "inv.json"
    repo_root = Path(__file__).resolve().parents[2]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root / "services" / "pack-factory")

    r = _run_cli(["inventory-scan","--target", str(zpath),"--out", str(out),"--trace","t1"], env, repo_root)
    assert r.returncode == 0, r.stderr
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data.get("trace_id") == "t1"
    assert data["summary"]["files"] == 1
    assert any("__MACOSX" in p or ".DS_Store" in p or "/._" in p or p.startswith("._") for p in data.get("ignored", []))
