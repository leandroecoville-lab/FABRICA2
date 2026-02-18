from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional

from .public_export import load_public_export_policy, is_public_path

def _list_files(root: Path, public_only: bool = True) -> List[str]:
    policy = load_public_export_policy(root)
    files: List[str] = []
    for p in root.rglob("*"):
        if p.is_file():
            rel = str(p.relative_to(root)).replace("\\", "/")
            if public_only and (not is_public_path(rel, policy)):
                continue
            files.append(rel)
    return sorted(files)

def write_filemap(root: Path, out_path: Path) -> None:
    files = _list_files(root, public_only=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("# FILEMAP\n\n" + "\n".join(f"- `{f}`" for f in files) + "\n", encoding="utf-8")

def _read_text_if_exists(root: Path, rel: str) -> str:
    p = root / rel
    if not p.exists():
        return ""
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def _extract_contract_list(root: Path) -> List[str]:
    cdir = root / "contracts"
    if not cdir.exists():
        return []
    return sorted([str(p.relative_to(root)).replace("\\","/") for p in cdir.rglob("*.json") if p.is_file()])

def _extract_runbooks(root: Path) -> List[str]:
    rdir = root / "runbooks"
    if not rdir.exists():
        return []
    return sorted([str(p.relative_to(root)).replace("\\","/") for p in rdir.glob("*.md") if p.is_file()])

def _extract_history(root: Path) -> List[str]:
    hdir = root / "history"
    if not hdir.exists():
        return []
    return sorted([str(p.relative_to(root)).replace("\\","/") for p in hdir.rglob("*") if p.is_file()])

def write_software_book(root: Path, packs_merged: Optional[List[str]]=None, trace_id: str="trace_local") -> None:
    """
    Gera docs/public/SOFTWARE_BOOK.md e FILEMAP.md a partir do snapshot atual.
    Não apaga histórico: apenas escreve em docs/public/.
    """
    docs_public = root / "docs" / "public"
    docs_public.mkdir(parents=True, exist_ok=True)

    # Assets de navegação (Mapa Mestre / Índice Navegável / Modo Clone GitHub)
    try:
        assets_dir = Path(__file__).resolve().parents[3] / "docs" / "assets"
        for fname in ["MAPA_MESTRE.md","INDICE_NAVEGAVEL.md","MODO_CLONE_GITHUB.md"]:
            src = assets_dir / fname
            if src.exists():
                shutil.copy2(src, docs_public / fname)
    except Exception:
        pass


    # FileMap
    write_filemap(root, docs_public / "FILEMAP.md")

    # Inputs
    manifest = _read_text_if_exists(root, "02_INVENTORY/manifest.json")
    plan = _read_text_if_exists(root, "docs/PLAN.md")
    troubleshooting = _read_text_if_exists(root, "docs/TROUBLESHOOTING.md")
    continuity = _read_text_if_exists(root, "docs/PROMPT_CONTINUIDADE.md")

    contracts = _extract_contract_list(root)
    runbooks = _extract_runbooks(root)
    history = _extract_history(root)

    # Compose
    lines: List[str] = []
    lines.append("# SOFTWARE BOOK\n")
    lines.append(f"**trace_id:** {trace_id}\n")

    if packs_merged:
        lines.append("## Packs merged\n")
        for p in packs_merged:
            lines.append(f"- `{p}`")
        lines.append("")

    lines.append("## Visão geral\n")
    lines.append("## Navegação rápida\n")
    lines.append("- `docs/public/MAPA_MESTRE.md` (mapa auditável do ecossistema; hierarquia de fonte de verdade)\n")
    lines.append("- `docs/public/INDICE_NAVEGAVEL.md` (índice RTIP para localizar artefatos por módulo/momento)\n")
    lines.append("- `docs/public/MODO_CLONE_GITHUB.md` (padrão de estilo/artefatos com guardrails)\n")

    lines.append("Este documento é gerado automaticamente pelo `lai-pack` para acelerar manutenção e onboarding.\n")

    lines.append("## Como rodar\n")
    if runbooks:
        lines.append("Runbooks detectados:")
        for rb in runbooks:
            lines.append(f"- `{rb}`")
        lines.append("")
    else:
        lines.append("Nenhum runbook encontrado.\n")

    lines.append("## Contratos e eventos\n")
    if contracts:
        for c in contracts[:120]:
            lines.append(f"- `{c}`")
        if len(contracts) > 120:
            lines.append(f"- ... (+{len(contracts)-120} contratos)")
        lines.append("")
    else:
        lines.append("Nenhum contrato encontrado.\n")

    lines.append("## Planejamento (se existir)\n")
    if plan:
        lines.append("_Resumo automático não aplicado (fonte de verdade é o próprio PLAN.md)._\n")
        lines.append("Veja: `docs/PLAN.md`\n")
    else:
        lines.append("`docs/PLAN.md` não encontrado.\n")

    lines.append("## Troubleshooting\n")
    if troubleshooting:
        lines.append("Veja: `docs/TROUBLESHOOTING.md`\n")
    else:
        lines.append("`docs/TROUBLESHOOTING.md` não encontrado.\n")

    lines.append("## Prompt de continuidade\n")
    if continuity:
        lines.append("Veja: `docs/PROMPT_CONTINUIDADE.md`\n")
    else:
        lines.append("`docs/PROMPT_CONTINUIDADE.md` não encontrado.\n")

    lines.append("## Histórico operacional (append-only)\n")
    if history:
        for h in history[:120]:
            lines.append(f"- `{h}`")
        if len(history) > 120:
            lines.append(f"- ... (+{len(history)-120} itens)")
        lines.append("")
    else:
        lines.append("Nenhum histórico encontrado.\n")

    lines.append("## FileMap\n")
    lines.append("Veja: `docs/public/FILEMAP.md`\n")

    (docs_public / "SOFTWARE_BOOK.md").write_text("\n".join(lines) + "\n", encoding="utf-8")