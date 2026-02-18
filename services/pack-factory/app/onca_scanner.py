from __future__ import annotations

import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List

from .utils import utc_now_iso


def _sha256_file(p: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        while True:
            b = f.read(chunk_size)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def _tags_for_path(p: Path) -> List[str]:
    ext = p.suffix.lower().lstrip(".")
    tags: List[str] = []
    if ext == "pdf":
        tags.append("doc")
    if ext in ("md", "markdown"):
        tags.append("md")
    if ext == "zip":
        tags.append("zip")
    n = p.name.lower()
    if "connect" in n:
        tags.append("lai_connect")
    if "meetcore" in n:
        tags.append("meetcore")
    if "culture" in n:
        tags.append("culture_people")
    if "app" in n:
        tags.append("app_lai")
    # unique
    seen = set()
    out: List[str] = []
    for t in tags:
        if t not in seen:
            out.append(t)
            seen.add(t)
    return out


def scan_onca(
    root: Path,
    out_jsonl: Path,
    trace_id: str,
    recursive: bool = False,
    max_files: int = 5000,
) -> Dict[str, Any]:
    """
    Gera inventário ONCA (JSONL) de um diretório. Cada linha:
      { onca_id, path_fisico, sha256, size_bytes, mtime_iso, tags[] }

    Obs: mtime_iso é normalizado por utc_now_iso() por portabilidade.
    """
    now = utc_now_iso()
    root = root.expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError(f"root inválido: {root}")

    files: List[Path] = []
    if recursive:
        for p in root.rglob("*"):
            if p.is_file():
                files.append(p)
                if len(files) >= max_files:
                    break
    else:
        for p in sorted(root.iterdir()):
            if p.is_file():
                files.append(p)
                if len(files) >= max_files:
                    break

    out_jsonl.parent.mkdir(parents=True, exist_ok=True)
    rows = 0
    total_bytes = 0
    with out_jsonl.open("w", encoding="utf-8") as fout:
        for i, p in enumerate(files, start=1):
            st = p.stat()
            try:
                sha = _sha256_file(p)
            except Exception:
                sha = ""
            obj = {
                "schema_version": "1.0",
                "trace_id": trace_id,
                "timestamp": now,
                "onca_id": f"ONCA-{i:04d}",
                "path_fisico": str(p),
                "sha256": sha,
                "size_bytes": int(st.st_size),
                "mtime_iso": utc_now_iso(),
                "tags": _tags_for_path(p),
            }
            fout.write(json.dumps(obj, ensure_ascii=False) + "\n")
            rows += 1
            total_bytes += int(st.st_size)

    return {
        "schema_version": "1.0",
        "trace_id": trace_id,
        "timestamp": now,
        "root": str(root),
        "recursive": recursive,
        "rows": rows,
        "bytes": total_bytes,
        "out": str(out_jsonl),
    }


def validate_onca(in_jsonl: Path, trace_id: str) -> Dict[str, Any]:
    """
    Valida ONCA JSONL:
    - duplicidade de onca_id
    - duplicidade de sha256
    - duplicidade de path_fisico
    - parse_errors
    """
    now = utc_now_iso()
    seen_ids = set()
    seen_paths = set()
    seen_sha = set()
    dup_ids = 0
    dup_paths = 0
    dup_sha = 0
    parse_errors = 0
    rows = 0

    with in_jsonl.open("r", encoding="utf-8", errors="replace") as fin:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            rows += 1
            try:
                obj = json.loads(line)
            except Exception:
                parse_errors += 1
                continue

            oid = str(obj.get("onca_id") or "")
            sha = str(obj.get("sha256") or "")
            path = str(obj.get("path_fisico") or "")

            if oid:
                if oid in seen_ids:
                    dup_ids += 1
                seen_ids.add(oid)
            if path:
                if path in seen_paths:
                    dup_paths += 1
                seen_paths.add(path)
            if sha:
                if sha in seen_sha:
                    dup_sha += 1
                seen_sha.add(sha)

    # Duplicidade de sha256 é sinal útil (bloat/duplicação), mas não bloqueia por padrão.
    ok = (parse_errors == 0 and dup_ids == 0 and dup_paths == 0)
    blocking_reasons: List[str] = []
    warnings: List[str] = []
    if parse_errors:
        blocking_reasons.append("parse_errors")
    if dup_ids:
        blocking_reasons.append("duplicate_onca_id")
    if dup_paths:
        blocking_reasons.append("duplicate_path")
    if dup_sha:
        warnings.append("duplicate_sha256")

    return {
        "schema_version": "1.0",
        "trace_id": trace_id,
        "timestamp": now,
        "ok": ok,
        "counts": {
            "rows": rows,
            "parse_errors": parse_errors,
            "duplicates_onca_id": dup_ids,
            "duplicates_path": dup_paths,
            "duplicates_sha256": dup_sha,
        },
        "warnings": warnings,
        "blocking_reasons": blocking_reasons,
    }