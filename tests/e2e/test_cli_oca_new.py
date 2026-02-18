from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import jsonschema

def _run_cli(args: list[str], env: dict[str,str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-m", "app.cli"] + args, cwd=cwd, env=env, capture_output=True, text=True)

def test_cli_oca_new_generates_valid_schema(tmp_path: Path):
    out = tmp_path / "oca.json"
    repo_root = Path(__file__).resolve().parents[2]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root / "services" / "pack-factory")
    env["LAI_ACTOR_ID"] = "dev-1"

    r = _run_cli([
        "oca-new",
        "--pack-target","pack-001@1.0.0",
        "--type","bugfix",
        "--summary","s",
        "--why","w",
        "--out", str(out),
        "--trace","t2",
    ], env, repo_root)
    assert r.returncode == 0, r.stderr
    obj = json.loads(out.read_text(encoding="utf-8"))
    assert obj["actors"]["author"] == "dev-1"
    assert obj["trace"]["trace_id"] == "t2"

    schema = json.loads((repo_root/"contracts/oca.v1.schema.json").read_text(encoding="utf-8"))
    jsonschema.validate(obj, schema)
