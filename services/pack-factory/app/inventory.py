from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Dict, Any, List

from .utils import utc_now_iso

def _kind_from_name(name: str) -> str:
    n = name.lower()
    if n.endswith(".pdf"): return "pdf"
    if n.endswith(".md") or n.endswith(".markdown"): return "md"
    if n.endswith(".json") or n.endswith(".jsonl"): return "json"
    if n.endswith(".yaml") or n.endswith(".yml"): return "yaml"
    if n.endswith(".py"): return "py"
    if n.endswith(".ts") or n.endswith(".tsx"): return "ts"
    if n.endswith(".js") or n.endswith(".jsx"): return "js"
    if n.endswith(".csv"): return "csv"
    if n.endswith(".xlsx") or n.endswith(".xls"): return "xlsx"
    if n.endswith(".zip"): return "zip"
    return "other"

def _should_ignore(path: str) -> bool:
    # Ignora ruídos comuns de ZIP (melhora DX e evita falsos positivos)
    p = path.replace("\\", "/")
    if p.startswith("__MACOSX/") or "/__MACOSX/" in p:
        return True
    base = p.split("/")[-1]
    if base == ".DS_Store" or base.startswith("._"):
        return True
    return False

def scan_zip(zip_path: Path, trace_id: str | None = None) -> Dict[str, Any]:
    items: List[Dict[str, Any]] = []
    ignored: List[str] = []
    with zipfile.ZipFile(zip_path, "r") as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            if _should_ignore(info.filename):
                ignored.append(info.filename)
                continue
            # sha256 do conteúdo extraído (stream)
            h = __import__("hashlib").sha256()
            with z.open(info, "r") as f:
                for chunk in iter(lambda: f.read(1024 * 1024), b""):
                    h.update(chunk)
            items.append({
                "path": info.filename,
                "kind": _kind_from_name(info.filename),
                "bytes": int(info.file_size),
                "sha256": h.hexdigest(),
            })
    out: Dict[str, Any] = {
        "generated_at": utc_now_iso(),
        "root": zip_path.name,
        "items": items,
        "ignored": ignored[:200],
        "summary": _summarize(items),
    }
    if trace_id is not None:
        out["trace_id"] = trace_id
    return out


def _summarize(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_kind: Dict[str, int] = {}
    total_bytes = 0
    for it in items:
        by_kind[it["kind"]] = by_kind.get(it["kind"], 0) + 1
        total_bytes += int(it.get("bytes", 0))
    return {
        "files": len(items),
        "bytes": total_bytes,
        "by_kind": dict(sorted(by_kind.items(), key=lambda kv: (-kv[1], kv[0]))),
    }
