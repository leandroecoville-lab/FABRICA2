from __future__ import annotations
import zipfile
from pathlib import Path
from typing import Dict, Any

def run_diag_on_zip(target_zip: Path) -> Dict[str, Any]:
    checks = {"has_manifest": False, "has_contracts": False, "has_runbooks": False, "has_services": False}
    evidence = {}
    with zipfile.ZipFile(target_zip, "r") as z:
        names = set(z.namelist())
        checks["has_manifest"] = any(n.endswith("02_INVENTORY/manifest.json") for n in names)
        checks["has_contracts"] = any(n.startswith("contracts/") for n in names)
        checks["has_runbooks"] = any(n.startswith("runbooks/") for n in names)
        checks["has_services"] = any(n.startswith("services/") for n in names)
        evidence["zip_entries_count"] = len(names)
    overall = "PASS" if all(checks.values()) else "FAIL"
    return {"overall_status": overall, "checks": checks, "evidence": evidence}
