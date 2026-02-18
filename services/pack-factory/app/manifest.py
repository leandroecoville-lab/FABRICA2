from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Optional

from .utils import utc_now_iso, write_json

def new_manifest(pack_id: str, version: str, modules: List[str], entrypoints: List[str], trace_id: str, parents: Optional[List[str]]=None, features: Optional[List[str]]=None) -> Dict[str, Any]:
    return {
        "schema_version": "1.0",
        "pack_id": pack_id,
        "version": version,
        "created_at": utc_now_iso(),
        "parents": parents or [],
        "modules": modules,
        "features": features or [],
        "entrypoints": entrypoints,
        "trace": {"trace_id": trace_id},
    }

def write_manifest(out_dir: Path, manifest: Dict[str, Any]) -> None:
    write_json(out_dir / "02_INVENTORY" / "manifest.json", manifest)
