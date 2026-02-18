from __future__ import annotations

import os
import subprocess
import sys
import zipfile
from pathlib import Path


def _run_cli(args: list[str], env: dict[str,str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-m", "app.cli"] + args, cwd=cwd, env=env, capture_output=True, text=True)


def test_book_filemap_excludes_restricted_by_default(tmp_path: Path):
    inzip = tmp_path / "p.zip"
    with zipfile.ZipFile(inzip, "w") as z:
        z.writestr("docs/ok.md", "x")
        z.writestr("docs/references/secret.pdf", "y")
        z.writestr("02_INVENTORY/semantic_index/a.jsonl", "z")

    out = tmp_path / "filemap.md"
    repo_root = Path(__file__).resolve().parents[2]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root / "services" / "pack-factory") + os.pathsep + str(repo_root)

    r = _run_cli(["book-filemap","--target", str(inzip),"--out", str(out),"--trace","b1"], env, repo_root)
    assert r.returncode == 0, r.stderr
    txt = out.read_text(encoding="utf-8")
    assert "docs/ok.md" in txt
    assert "docs/references/secret.pdf" not in txt
    assert "02_INVENTORY/semantic_index/a.jsonl" not in txt
