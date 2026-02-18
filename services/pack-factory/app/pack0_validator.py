from __future__ import annotations

import json
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

REQUIRED_PATHS = [
    "docs/PLAN.md",
    "docs/PROMPT_CONTINUIDADE.md",
    "docs/TROUBLESHOOTING.md",
    "docs/DEFINITION_OF_DONE.md",
    "runbooks/HOW_TO_RUN.md",
    "runbooks/HOW_TO_DEPLOY.md",
    "runbooks/HOW_TO_ROLLBACK.md",
    "contracts/README.json",
]

REQUIRED_SECTIONS = [
    # SRS baseline (documento_de_requisitos_analise_projeto.pdf)
    "Introdução",
    "Propósito",
    "Escopo",
    "Características dos Usuários",
    "Referências",
    "Visão Geral do Produto",
    "Perspectiva do Produto",
    "Funcionalidades",
    "Ambiente Operacional",
    "Limitações",
    "Suposições e Dependências",
    "Requisitos Funcionais",
    "Requisitos Não Funcionais",
    "Casos de Uso",
    "Diagramas",
    "Rastreabilidade",

    # Pack lifecycle baseline
    "Plano de Implementação",
    "Testes",
    "Aceite",
    "Rollout",
    "Rollback",
    "Definition of Done",
]

@dataclass
class ValidationReport:
    ok: bool
    gaps: List[str]
    checked_paths: List[str]
    checked_sections: List[str]
    meta: Dict[str, str]

def _read_from_zip(z: zipfile.ZipFile, path: str) -> Optional[str]:
    try:
        with z.open(path) as f:
            return f.read().decode("utf-8", errors="ignore")
    except KeyError:
        return None

def _exists_in_zip(z: zipfile.ZipFile, path: str) -> bool:
    try:
        z.getinfo(path)
        return True
    except KeyError:
        return False

def validate_pack0(target: Union[str, Path]) -> ValidationReport:
    """
    Valida se um Pack0 contém as seções mínimas (SRS) + estrutura pack-first.
    Retorna um relatório e marca ok=False se faltarem itens.
    """
    p = Path(target)
    gaps: List[str] = []
    checked_paths = list(REQUIRED_PATHS)
    checked_sections = list(REQUIRED_SECTIONS)
    meta: Dict[str, str] = {}

    plan_text = ""

    if p.is_dir():
        # paths
        for rp in REQUIRED_PATHS:
            if not (p / rp).exists():
                gaps.append(f"missing_path::{rp}")
        # plan
        plan_file = p / "docs/PLAN.md"
        if plan_file.exists():
            plan_text = plan_file.read_text(encoding="utf-8", errors="ignore")
        # manifest meta
        mpath = p / "02_INVENTORY/manifest.json"
        if mpath.exists():
            try:
                m = json.loads(mpath.read_text(encoding="utf-8"))
                meta["pack_id"] = str(m.get("pack_id",""))
                meta["version"] = str(m.get("version",""))
            except Exception:
                pass

    else:
        # zip
        with zipfile.ZipFile(p, "r") as z:
            for rp in REQUIRED_PATHS:
                if not _exists_in_zip(z, rp):
                    gaps.append(f"missing_path::{rp}")

            plan = _read_from_zip(z, "docs/PLAN.md")
            if plan:
                plan_text = plan

            m = _read_from_zip(z, "02_INVENTORY/manifest.json")
            if m:
                try:
                    mj = json.loads(m)
                    meta["pack_id"] = str(mj.get("pack_id",""))
                    meta["version"] = str(mj.get("version",""))
                except Exception:
                    pass


    # MeetCore-first gating (Pack0 precisa carregar slices + budgets + retenção como artefatos explícitos)
    module_name = ""
    pid = meta.get("pack_id", "")
    if pid.startswith("pack0-"):
        module_name = pid[len("pack0-"):].strip().lower()
    elif p.name.startswith("pack0-"):
        # fallback quando manifest não existe
        module_name = p.name.split("-")[1].strip().lower() if "-" in p.name else ""

    # Normalização do nome do módulo (permite aliases sem quebrar gating)
    mod_key = re.sub(r"[^a-z0-9]+", "-", (module_name or "").lower()).strip("-")

    connect_required = ["docs/CONNECT_SLICES.md", "docs/DATA_RETENTION_MATRIX.md"]
    app_lai_required = ["docs/APP_LAI_SLICES.md", "docs/DATA_RETENTION_MATRIX.md"]
    culture_people_required = ["docs/CULTURE_PEOPLE_SLICES.md", "docs/DATA_RETENTION_MATRIX.md"]


    meetcore_required = [
        "docs/MEETCORE_SLICES.md",
        "docs/PERFORMANCE_BUDGETS.md",
        "docs/DATA_RETENTION_MATRIX.md",
    ]
    if mod_key == "meetcore":
        for rp in meetcore_required:
            if rp not in checked_paths:
                checked_paths.append(rp)
        # existence
        if p.is_dir():
            for rp in meetcore_required:
                if not (p / rp).exists():
                    gaps.append(f"missing_path::{rp}")
        else:
            with zipfile.ZipFile(p, "r") as z:
                for rp in meetcore_required:
                    if not _exists_in_zip(z, rp):
                        gaps.append(f"missing_path::{rp}")


        # Conteúdo mínimo: evitar drift (não é qualidade perfeita, é gate objetivo)
        try:
            if p.is_dir():
                slices = (p / "docs/MEETCORE_SLICES.md").read_text(encoding="utf-8", errors="ignore")
                budgets = (p / "docs/PERFORMANCE_BUDGETS.md").read_text(encoding="utf-8", errors="ignore")
                retention = (p / "docs/DATA_RETENTION_MATRIX.md").read_text(encoding="utf-8", errors="ignore")
            else:
                with zipfile.ZipFile(p, "r") as z:
                    slices = _read_from_zip(z, "docs/MEETCORE_SLICES.md")
                    budgets = _read_from_zip(z, "docs/PERFORMANCE_BUDGETS.md")
                    retention = _read_from_zip(z, "docs/DATA_RETENTION_MATRIX.md")

            if "pec1.01" not in slices.lower():
                gaps.append("missing_trace::meetcore_slices_PEC1_01_not_found")
            if "300ms" not in budgets.lower().replace(" ", ""):
                gaps.append("missing_trace::meetcore_budget_streaming_300ms_not_found")
            rlow = retention.lower()
            if not ("culture" in rlow and "people" in rlow and "pipeline" in rlow):
                gaps.append("missing_trace::retention_matrix_culture_people_not_found")
        except Exception:
            gaps.append("validation_error::meetcore_docs_read_failed")


    # Gating por módulo (slices obrigatórias)
    def _ensure_required(required: list[str]):
        for rp in required:
            if rp not in checked_paths:
                checked_paths.append(rp)
        if p.is_dir():
            for rp in required:
                if not (p / rp).exists():
                    gaps.append(f"missing_path::{rp}")
        else:
            with zipfile.ZipFile(p, "r") as zz:
                for rp in required:
                    if not _exists_in_zip(zz, rp):
                        gaps.append(f"missing_path::{rp}")

    if mod_key in ("lai-connect", "connect", "lai-connect-mvp"):
        _ensure_required(connect_required)

    if mod_key in ("app-lai", "app", "lai-app"):
        _ensure_required(app_lai_required)

    if mod_key in ("culture-people", "culture", "lai-culture", "culture-and-people"):
        _ensure_required(culture_people_required)



    # sections
    # Normalize whitespace to avoid false negatives due to line breaks.
    normalized = re.sub(r"\s+", " ", plan_text).lower()
    for sec in REQUIRED_SECTIONS:
        if sec.lower() not in normalized:
            gaps.append(f"missing_section::{sec}")

    # RF/RNF/UC minimal presence checks (ids)
    if not re.search(r"\bRF[-_\s]?\d+", plan_text, re.IGNORECASE):
        gaps.append("missing_trace::RF_ids_not_found")
    if not re.search(r"\bRNF[-_\s]?\d+", plan_text, re.IGNORECASE):
        gaps.append("missing_trace::RNF_ids_not_found")
    if not re.search(r"\bUC[-_\s]?\d+", plan_text, re.IGNORECASE):
        gaps.append("missing_trace::UC_ids_not_found")

    ok = len(gaps) == 0
    return ValidationReport(ok=ok, gaps=gaps, checked_paths=checked_paths, checked_sections=checked_sections, meta=meta)

def report_to_dict(r: ValidationReport) -> Dict:
    return {
        "ok": r.ok,
        "gaps": r.gaps,
        "checked_paths": r.checked_paths,
        "checked_sections": r.checked_sections,
        "meta": r.meta,
    }
