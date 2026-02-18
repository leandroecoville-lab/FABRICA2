from __future__ import annotations

import json
import re
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, Any, List, Optional

from .public_export import load_public_export_policy, is_public_path
from .utils import utc_now_iso, sha256_file


DEFAULT_AUDIENCE_POLICY_PATH = "governance/audience_policy.team_pack0_only.v1.json"


def load_audience_policy(repo_root: Path, policy_path: Optional[Path] = None) -> Dict[str, Any]:
    """Carrega política de audiência (team-safe).

    - Se policy_path não for informado, usa DEFAULT_AUDIENCE_POLICY_PATH no repo.
    - O contrato é declarativo (allowlist/denylist).
    """
    p = policy_path or (repo_root / DEFAULT_AUDIENCE_POLICY_PATH)
    if not p.exists():
        # fallback conservador: default-deny forte
        return {
            "schema_version": "1.0",
            "audience": "team",
            "export_mode": "pack0_only",
            "allowlist_prefixes": ["00_INDEXES/", "02_INVENTORY/", "contracts/", "docs/", "runbooks/"],
            "denylist_prefixes": [
                "services/pack-factory/",
                "02_INVENTORY/semantic_index/",
                "docs/references/",
                "gpt_builder/",
                "history/",
                ".github/",
                ".pytest_cache/",
                "__pycache__/",
            ],
            "denylist_regex": ["\\.pyc$", "^⚠️"],
        }
    return json.loads(p.read_text(encoding="utf-8"))


def _is_probably_release_pack(extracted_root: Path) -> bool:
    # Heurística conservadora: presença do runtime da própria Pack Factory
    return (extracted_root / "services" / "pack-factory" / "app" / "cli.py").exists()



def export_manual(repo_root: Path, out_path: Path, trace_id: str) -> Dict[str, Any]:
    now = utc_now_iso()
    src = repo_root / "docs" / "MANUAL_OPERACIONAL_PACK_FACTORY.md"
    if not src.exists():
        raise FileNotFoundError("docs/MANUAL_OPERACIONAL_PACK_FACTORY.md não encontrado.")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, out_path)

    return {
        "schema_version": "1.0",
        "trace_id": trace_id,
        "timestamp": now,
        "ok": True,
        "out": str(out_path),
        "bytes": int(out_path.stat().st_size),
        "sha256": sha256_file(out_path),
    }


def export_team_pack(
    repo_root: Path,
    in_pack_zip: Path,
    out_zip: Path,
    trace_id: str,
    policy_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Gera ZIP 'team-safe' a partir de um **SNAPSHOT** (promoted) do ciclo PEC.

    Garantias (default-deny):
    - Exportação **pack0_only** por padrão (não aceitar Release Pack como entrada).
    - Allowlist/denylist declarativa (audience policy).
    - Aplica policy governance/public_export_policy.json (regex e prefixes).
    - Recalcula pack.meta.json e atualiza trace no manifest.
    """
    now = utc_now_iso()
    public_policy = load_public_export_policy(repo_root)
    audience = load_audience_policy(repo_root, policy_path=policy_path)

    allow_prefixes = [str(x) for x in (audience.get("allowlist_prefixes") or [])]
    deny_prefixes = [str(x) for x in (audience.get("denylist_prefixes") or [])]
    deny_regexes = [re.compile(str(x)) for x in (audience.get("denylist_regex") or [])]

    copied = 0
    excluded = 0

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        src_root = td_path / "src"
        dst_root = td_path / "dst"
        src_root.mkdir(parents=True, exist_ok=True)
        dst_root.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(in_pack_zip, "r") as z:
            z.extractall(src_root)

        # Default-deny: bloquear erro operacional comum (passar Release Pack em vez de snapshot)
        if audience.get("export_mode") == "pack0_only" and _is_probably_release_pack(src_root):
            raise ValueError(
                "export-team-pack recusado: entrada parece ser um Release Pack. "
                "Gere um snapshot promoted via PEC Chain (merge --mode promoted) e exporte a partir dele."
            )

        for p in src_root.rglob("*"):
            if not p.is_file():
                continue
            rel = p.relative_to(src_root).as_posix()

            # denylist prefix
            if any(rel.startswith(pref) for pref in deny_prefixes):
                excluded += 1
                continue

            # denylist regex (aplica no basename)
            base = rel.split("/")[-1]
            if any(rx.search(base) for rx in deny_regexes):
                excluded += 1
                continue

            # allowlist prefix
            if allow_prefixes and not any(rel.startswith(pref) for pref in allow_prefixes):
                excluded += 1
                continue

            # public policy (proteções extras)
            if not is_public_path(rel, public_policy):
                excluded += 1
                continue

            dest = dst_root / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dest)
            copied += 1

        # update manifest trace
        mpath = dst_root / "02_INVENTORY" / "manifest.json"
        if mpath.exists():
            try:
                m = json.loads(mpath.read_text(encoding="utf-8"))
            except Exception:
                m = {}
            m["trace"] = {"trace_id": trace_id}
            feats = list(m.get("features") or [])
            if "team-export" not in feats:
                feats.append("team-export")
            if "team-pack0-only" not in feats:
                feats.append("team-pack0-only")
            m["features"] = feats
            m["created_at"] = now
            mpath.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")

        # recompute pack.meta.json
        meta_path = dst_root / "02_INVENTORY" / "pack.meta.json"
        files: List[Dict[str, Any]] = []
        for fp in sorted(dst_root.rglob("*")):
            if not fp.is_file():
                continue
            rel2 = fp.relative_to(dst_root).as_posix()
            if rel2 == "02_INVENTORY/pack.meta.json":
                continue
            files.append({"path": rel2, "sha256": sha256_file(fp), "bytes": int(fp.stat().st_size)})

        meta = {
            "schema_version": "1.0",
            "pack_id": "lai-pack-factory",
            "version": "team",
            "generated_at": now,
            "trace_id": trace_id,
            "files": files,
            "notes": "team-safe export (pack0_only, default-deny). pack.meta.json não inclui hash de si mesmo.",
        }
        meta_path.parent.mkdir(parents=True, exist_ok=True)
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

        if out_zip.exists():
            out_zip.unlink()
        with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
            for fp in dst_root.rglob("*"):
                if fp.is_file():
                    z.write(fp, fp.relative_to(dst_root).as_posix())

    return {
        "schema_version": "1.0",
        "trace_id": trace_id,
        "timestamp": now,
        "ok": True,
        "in": str(in_pack_zip),
        "out": str(out_zip),
        "zip_bytes": int(out_zip.stat().st_size) if out_zip.exists() else 0,
        "copied_files": copied,
        "excluded_files": excluded,
        "policy": str((policy_path or (repo_root / DEFAULT_AUDIENCE_POLICY_PATH))),
    }
