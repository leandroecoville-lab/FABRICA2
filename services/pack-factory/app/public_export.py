from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class PublicExportPolicy:
    exclude_prefixes: List[str]
    exclude_name_regexes: List[str]


def load_public_export_policy(repo_root: Path) -> PublicExportPolicy:
    """
    Carrega a policy de export público. Se não existir, aplica defaults conservadores.
    Usada para:
    - docs/public/FILEMAP.md e docs/public/SOFTWARE_BOOK.md
    - export-team-pack (zip filtrado)
    """
    policy_path = repo_root / "governance" / "public_export_policy.json"
    if policy_path.exists():
        try:
            obj = json.loads(policy_path.read_text(encoding="utf-8"))
            return PublicExportPolicy(
                exclude_prefixes=list(obj.get("exclude_prefixes") or []),
                exclude_name_regexes=list(obj.get("exclude_name_regexes") or []),
            )
        except Exception:
            pass

    return PublicExportPolicy(
        exclude_prefixes=[
            "docs/references/",
            "02_INVENTORY/semantic_index/",
            "history/",
            "gpt_builder/",
            ".github/",
            ".pytest_cache/",
        ],
        exclude_name_regexes=[
            r"^⚠️",
            r"NÚCLEOS",
            r"NUCLEOS",
            r"REINTERPRETACAO",
        ],
    )


def is_public_path(rel_path: str, policy: PublicExportPolicy) -> bool:
    p = (rel_path or "").replace("\\", "/")
    for pref in policy.exclude_prefixes:
        if p.startswith(pref):
            return False
    base = p.split("/")[-1]
    for rx in policy.exclude_name_regexes:
        try:
            if re.search(rx, base, flags=re.IGNORECASE):
                return False
        except re.error:
            continue
    return True
