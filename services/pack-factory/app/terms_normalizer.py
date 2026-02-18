"""
Normalizador de termos (Big Tech Dictionary).

Objetivo:
- Padronizar linguagem em docs/runbooks/prompts para o "Sistema LAI — Dicionário de termos sensíveis".

IMPORTANTE:
- Não usar para ocultar intenção, auditoria ou compliance.
- Modo conservador: aplica apenas mapeamentos explicitamente declarados na policy (governance/bigtech_dictionary.v1.json).
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional


# Fallback mínimo (compatibilidade)
SAFE_MAP: Dict[str, str] = {
    "RAG": "índice semântico de manutenção",
    "OCA": "contrato auditável de mudança (OCA)",
    "registro único": "identificador único (pack_id + sha256 + semver)",
}


def _repo_root() -> Path:
    # services/pack-factory/app/terms_normalizer.py -> parents[3] = repo root
    return Path(__file__).resolve().parents[3]


@lru_cache(maxsize=2)
def _load_bigtech_map(repo_root: Optional[Path] = None) -> Dict[str, str]:
    root = (repo_root or _repo_root()).resolve()
    p = root / "governance" / "bigtech_dictionary.v1.json"
    if p.exists():
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
            mappings = obj.get("mappings") or {}
            if isinstance(mappings, dict) and mappings:
                # merge SAFE_MAP under mappings (mappings win)
                out = dict(SAFE_MAP)
                out.update({str(k): str(v) for k, v in mappings.items()})
                return out
        except Exception:
            pass
    return dict(SAFE_MAP)


def normalize(text: str, repo_root: Optional[Path] = None) -> str:
    """
    Aplica substituições do dicionário de termos sensíveis (modo conservador).
    """
    out = text
    m = _load_bigtech_map(repo_root)
    # Longest keys first (evita substituir substrings antes da frase completa)
    for k in sorted(m.keys(), key=len, reverse=True):
        v = m[k]
        # boundary friendly for phrases: ensure not inside another word
        pattern = r"(?<!\w)" + re.escape(k) + r"(?!\w)"
        out = re.sub(pattern, v, out, flags=re.IGNORECASE)
    return out
