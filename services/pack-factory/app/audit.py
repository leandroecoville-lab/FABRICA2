from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict

from .utils import ensure_dir, utc_now_iso

def append_audit(audit_dir: Path, event_type: str, data: Dict[str, Any], trace_id: str) -> None:
    ensure_dir(audit_dir)
    rec = {"time": utc_now_iso(), "type": event_type, "trace_id": trace_id, "data": data}
    (audit_dir / "audit.jsonl").open("a", encoding="utf-8").write(json.dumps(rec, ensure_ascii=False) + "\n")
