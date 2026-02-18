from __future__ import annotations

import hashlib
import re
import json
import shutil
import zipfile
from pathlib import Path
from typing import List

from .software_book import write_software_book
from .utils import sha256_file, utc_now_iso, write_json

HISTORY_PREFIX = "history/"


def _unzip_to_dir(zip_path: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(out_dir)


def _copy_tree(src: Path, dst: Path) -> None:
    """
    Overlay determinístico:
    - O pack mais recente sobrescreve o anterior
    - history/ é append-only, com exceções controladas:
      - history/chain_state.json: pode sobrescrever (arquivo derivado)
      - history/hashchain.jsonl: merge append-only (concat)
    """
    for p in src.rglob("*"):
        if not p.is_file():
            continue
        rel = str(p.relative_to(src)).replace("\\", "/")
        dest = dst / rel
        dest.parent.mkdir(parents=True, exist_ok=True)

        # Exceções controladas
        if rel == "history/chain_state.json":
            shutil.copy2(p, dest)
            continue

        if rel == "history/hashchain.jsonl" and dest.exists():
            with dest.open("a", encoding="utf-8") as fout, p.open("r", encoding="utf-8", errors="ignore") as fin:
                for line in fin:
                    if line.strip():
                        fout.write(line.rstrip("\n") + "\n")
            continue

        # Append-only rule (restante)
        if rel.startswith(HISTORY_PREFIX) and dest.exists():
            raise RuntimeError(f"append-only violation on {rel}")

        shutil.copy2(p, dest)


def _read_last_approval(work: Path) -> dict | None:
    approvals_dir = work / "history" / "approvals"
    if not approvals_dir.exists():
        return None
    approvals = sorted([p for p in approvals_dir.glob("*.json") if p.is_file()])
    if not approvals:
        return None
    try:
        return json.loads(approvals[-1].read_text(encoding="utf-8"))
    except Exception:
        return None


def _next_expected_from_pack_ref(pack_ref: str) -> str:
    """
    Robust next_expected:
    - aceita packN, packN.X, packN.X.Y
    - aceita pecN, pecN.X, pecN.X.Y
    - incrementa major: pack2.01 -> pack3 ; pec2.01 -> pec3
    Fallback: heurística antiga.
    """
    ref = (pack_ref or "").strip().lower()

    m = re.search(r"\b(pack|pec)\s*(\d+)(?:\.(\d+))?(?:\.(\d+))?\b", ref)
    if m:
        prefix = m.group(1)
        major = int(m.group(2))
        return f"{prefix}{major+1}"

    # fallback (compatibilidade)
    if "pack0" in ref: return "pack1"
    if "pack1" in ref: return "pack2"
    if "pack2" in ref: return "pack3"
    if "pack3" in ref: return "pack4"
    return "unknown"


def merge_packs(
    pack_zips: List[Path],
    out_zip: Path,
    tmp_dir: Path,
    trace_id: str = "trace_local",
    generate_software_book: bool = True,
    mode: str = "candidate",
) -> None:
    """
    Faz merge determinístico em snapshot ZIP final.
    mode:
      - candidate: não exige approval
      - promoted: exige pelo menos 1 approval com decision=approved
    """
    tmp_dir.mkdir(parents=True, exist_ok=True)
    work = tmp_dir / "work"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True, exist_ok=True)

    # Layered unzip + overlay copy
    for i, pzip in enumerate(pack_zips):
        layer = tmp_dir / f"layer_{i}"
        if layer.exists():
            shutil.rmtree(layer)
        _unzip_to_dir(pzip, layer)
        _copy_tree(layer, work)

    # Gate promoted
    last_approval = _read_last_approval(work)
    if mode == "promoted":
        if not last_approval:
            raise RuntimeError("promoted merge exige approval (history/approvals/*).")
        if str(last_approval.get("decision","")) != "approved":
            raise RuntimeError("promoted merge exige approval decision=approved.")

    # Auto docs
    if generate_software_book:
        write_software_book(
            work,
            packs_merged=[p.name for p in pack_zips],
            trace_id=trace_id,
        )

    # Merge receipt + chain_state + hashchain (tamper-evident)
    receipts_dir = work / "history" / "merge_receipts"
    receipts_dir.mkdir(parents=True, exist_ok=True)

    inputs_meta = []
    for pzip in pack_zips:
        try:
            inputs_meta.append({"path": pzip.name, "sha256": sha256_file(pzip)})
        except Exception:
            inputs_meta.append({"path": pzip.name, "sha256": ""})

    receipt = {
        "schema_version": "1.0",
        "trace_id": trace_id,
        "timestamp": utc_now_iso(),
        "inputs": inputs_meta,
        "mode": mode,
        "notes": "gerado automaticamente pelo merge (determinístico)",
    }
    receipt_path = receipts_dir / f"{trace_id}.json"
    write_json(receipt_path, receipt)

    chain_state = {
        "schema_version": "1.0",
        "trace_id": trace_id,
        "timestamp": utc_now_iso(),
        "current_approved_pack": (last_approval.get("pack_ref") if isinstance(last_approval, dict) else ""),
        "next_expected": _next_expected_from_pack_ref(last_approval.get("pack_ref","") if isinstance(last_approval, dict) else ""),
        "blocking_reasons": ([] if (mode == "promoted" and last_approval and last_approval.get("decision")=="approved") else (["missing_approval"] if not last_approval else ["not_promoted"])),
        "history_refs": {
            "approvals_dir": "history/approvals/",
            "run_reports_dir": "history/run_reports/",
            "ocas_dir": "history/ocas/",
            "merge_receipts_dir": "history/merge_receipts/",
        },
    }
    # MeetCore-first slicing: permitir PEC1.01..PEC1.05 como variantes do próximo esperado
    try:
        cap = str(chain_state.get("current_approved_pack","")).lower()
        if ("meetcore" in cap) and (str(chain_state.get("next_expected","")).lower() == "pack1"):
            chain_state["next_expected_variants"] = [f"PEC1.{i:02d}" for i in range(1, 6)]
            chain_state["next_expected_note"] = "MeetCore-first slicing: iniciar pelo PEC1.01 (Signaling+Rooms+Tokens) e evoluir até PEC1.05."
    except Exception:
        pass

    chain_state_path = work / "history" / "chain_state.json"
    write_json(chain_state_path, chain_state)

    # Hashchain append-only
    hashchain_path = work / "history" / "hashchain.jsonl"
    prev_hash = ""
    if hashchain_path.exists():
        try:
            last_line = [ln for ln in hashchain_path.read_text(encoding="utf-8", errors="ignore").splitlines() if ln.strip()][-1]
            prev_hash = json.loads(last_line).get("hash","")
        except Exception:
            prev_hash = ""
    payload_sha = sha256_file(receipt_path)
    entry = {
        "schema_version": "1.0",
        "entry_type": "merge_receipt",
        "payload_sha256": payload_sha,
        "prev_hash": prev_hash,
        "timestamp": utc_now_iso(),
    }
    entry_str = json.dumps(entry, ensure_ascii=False, sort_keys=True)
    entry_hash = hashlib.sha256((prev_hash + entry_str).encode("utf-8")).hexdigest()
    entry["hash"] = entry_hash
    hashchain_path.parent.mkdir(parents=True, exist_ok=True)
    with hashchain_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # Prompt de continuidade determinístico (público)
    pc_path = work / "docs" / "public" / "PROMPT_CONTINUIDADE.md"
    pc_path.parent.mkdir(parents=True, exist_ok=True)
    pc_lines = []
    pc_lines.append("# Prompt de Continuidade (snapshot)\n")
    pc_lines.append(f"**trace_id:** {trace_id}\n")
    pc_lines.append("## Packs merged\n")
    for p in [p.name for p in pack_zips]:
        pc_lines.append(f"- `{p}`")
    pc_lines.append("")
    pc_lines.append("## Estado (chain_state)\n")
    pc_lines.append(f"- current_approved_pack: `{chain_state.get('current_approved_pack','')}`")
    pc_lines.append(f"- next_expected: `{chain_state.get('next_expected','')}`")
    if chain_state.get("next_expected_variants"):
        pc_lines.append(f"- next_expected_variants: `{', '.join([str(v) for v in chain_state.get('next_expected_variants', [])])}`")
    if chain_state.get("next_expected_note"):
        pc_lines.append(f"- next_expected_note: {chain_state.get('next_expected_note', '')}")
    pc_lines.append(f"- blocking_reasons: `{', '.join(chain_state.get('blocking_reasons') or [])}`\n")
    pc_lines.append("## Navegação\n")
    pc_lines.append("- `docs/public/SOFTWARE_BOOK.md`\n- `docs/public/FILEMAP.md`\n- `docs/public/MAPA_MESTRE.md`\n- `docs/public/INDICE_NAVEGAVEL.md`\n")
    pc_lines.append("## Próximo passo\n")
    if mode == "candidate":
        pc_lines.append("- Para promover: gere RUN_REPORT + APPROVAL, empacote como patch packs e refaça merge em `--mode promoted`.\n")
    else:
        pc_lines.append(f"- Próximo pack esperado: `{chain_state.get('next_expected','')}`\n")
    pc_path.write_text("\n".join(pc_lines) + "\n", encoding="utf-8")

    # Zip snapshot
    out_zip.parent.mkdir(parents=True, exist_ok=True)
    if out_zip.exists():
        out_zip.unlink()
    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in work.rglob("*"):
            if p.is_file():
                z.write(p, arcname=str(p.relative_to(work)).replace("\\", "/"))
