from __future__ import annotations
from typing import Any, Dict, List
from .utils import utc_now_iso

def new_oca(
    oca_id: str,
    pack_target: str,
    oca_type: str,
    summary: str,
    why: str,
    author: str,
    trace_id: str,
    reviewer: str | None = None,
    changes: List[Dict[str, Any]] | None = None,
    tests_added_or_updated: List[str] | None = None,
    severity: str = "low",
    blast_radius: List[str] | None = None,
    rollback_plan: str = "reverter para o pack anterior",
) -> Dict[str, Any]:
    return {
        "oca_id": oca_id,
        "pack_target": pack_target,
        "type": oca_type,
        "summary": summary,
        "why": why,
        "changes": changes or [],
        "tests_added_or_updated": tests_added_or_updated or [],
        "risk": {
            "severity": severity,
            "blast_radius": blast_radius or [],
            "rollback_plan": rollback_plan,
        },
        "actors": ({**{"author": author}, **({"reviewer": reviewer} if reviewer else {})}),
        "trace": {"trace_id": trace_id},
        "created_at": utc_now_iso(),
    }
