from __future__ import annotations

import json
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class LeakViolation:
    path: str
    reason: str


def _load_policy(policy_path: Path) -> Dict[str, Any]:
    return json.loads(policy_path.read_text(encoding="utf-8"))


def leak_check_zip(
    target_zip: Path,
    policy_path: Path,
    out_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Valida um ZIP contra política de audiência (no_leak).

    Regras:
    - denylist_prefixes: qualquer path com esse prefixo é violação
    - denylist_regex: qualquer basename que bata é violação
    - allowlist_prefixes (opcional): qualquer arquivo fora da allowlist é violação

    Retorna report JSON e, se out_path informado, escreve no disco.
    """
    policy = _load_policy(policy_path)
    allow_prefixes: List[str] = [str(x) for x in (policy.get("allowlist_prefixes") or [])]
    deny_prefixes: List[str] = [str(x) for x in (policy.get("denylist_prefixes") or [])]
    deny_regexes = [re.compile(str(x)) for x in (policy.get("denylist_regex") or [])]

    violations: List[LeakViolation] = []

    with zipfile.ZipFile(target_zip, "r") as z:
        for name in z.namelist():
            if not name or name.endswith("/"):
                continue
            # normalize
            n = name.replace("\\", "/")
            base = n.split("/")[-1]

            if any(n.startswith(p) for p in deny_prefixes):
                violations.append(LeakViolation(path=n, reason="deny_prefix"))
                continue
            if any(rx.search(base) for rx in deny_regexes):
                violations.append(LeakViolation(path=n, reason="deny_regex"))
                continue
            if allow_prefixes and not any(n.startswith(p) for p in allow_prefixes):
                violations.append(LeakViolation(path=n, reason="outside_allowlist"))
                continue

    report: Dict[str, Any] = {
        "schema_version": "1.0",
        "status": "PASS" if not violations else "FAIL",
        "checked_zip": str(target_zip),
        "policy": str(policy_path),
        "violations": [v.__dict__ for v in violations],
        "counts": {"violations": len(violations)},
    }

    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    return report
