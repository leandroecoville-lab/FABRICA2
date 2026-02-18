from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
import zipfile
from pathlib import Path
from typing import List, Optional, Dict, Any

import jsonschema

from .book import filemap_from_zip
from .diag import run_diag_on_zip
from .inventory import scan_zip
from .merger import merge_packs
from .oca import new_oca
from .pack0_validator import report_to_dict, validate_pack0
from .planner import generate_pack0
from .pack1 import generate_pack1
from .onca_scanner import scan_onca, validate_onca
from .resolver import resolve_to_file
from .exporter import export_manual, export_team_pack
from .leak_check import leak_check_zip
from .utils import write_json, sha256_file, utc_now_iso


def _p(path_str: str) -> Path:
    return Path(path_str).expanduser().resolve()


def _repo_root() -> Path:
    # services/pack-factory/app/cli.py -> parents[3] = repo root
    return Path(__file__).resolve().parents[3]


def _contracts_dir() -> Path:
    return _repo_root() / "contracts"


def _load_schema(rel_path: str) -> Dict[str, Any]:
    p = _contracts_dir() / rel_path
    return json.loads(p.read_text(encoding="utf-8"))


def _validate(schema_rel_path: str, obj: Dict[str, Any]) -> None:
    schema = _load_schema(schema_rel_path)
    jsonschema.validate(obj, schema)


def _read_manifest_from_zip(zip_path: Path) -> Dict[str, Any]:
    try:
        with zipfile.ZipFile(zip_path, "r") as z:
            cands = [n for n in z.namelist() if n.endswith("02_INVENTORY/manifest.json")]
            if not cands:
                return {}
            return json.loads(z.read(cands[0]).decode("utf-8", errors="replace"))
    except Exception:
        return {}


def _pack_ref_from_manifest_or_zip(manifest: Dict[str, Any], zip_path: Path) -> str:
    pack_id = str(manifest.get("pack_id") or zip_path.stem)
    version = str(manifest.get("version") or "")
    return f"{pack_id}@{version}" if version else pack_id


def _actor_from_env_or_arg(arg: str) -> str:
    a = (arg or "").strip()
    if a:
        return a
    return os.environ.get("LAI_ACTOR_ID", "").strip() or "unknown"


def _mk_patch_pack(out_zip: Path, pack_id: str, version: str, trace_id: str, files: Dict[str, str]) -> None:
    """
    Cria um ZIP de patch pack (pack-first) mínimo:
    - 02_INVENTORY/manifest.json
    - arquivos em history/*
    """
    tmp_dir = out_zip.parent / f"._tmp_patch_{uuid.uuid4().hex[:8]}"
    if tmp_dir.exists():
        import shutil
        shutil.rmtree(tmp_dir)
    (tmp_dir / "02_INVENTORY").mkdir(parents=True, exist_ok=True)

    manifest = {
        "schema_version": "1.0",
        "pack_id": pack_id,
        "version": version,
        "created_at": utc_now_iso(),
        "parents": [],
        "modules": ["pack-factory-patch"],
        "features": ["patch-pack"],
        "entrypoints": [],
        "trace": {"trace_id": trace_id},
    }
    (tmp_dir / "02_INVENTORY" / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    for rel_path, content in files.items():
        rp = tmp_dir / rel_path
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text(content, encoding="utf-8")

    if out_zip.exists():
        out_zip.unlink()
    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in tmp_dir.rglob("*"):
            if p.is_file():
                z.write(p, arcname=str(p.relative_to(tmp_dir)).replace("\\", "/"))

    import shutil
    shutil.rmtree(tmp_dir)


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="lai-pack", description="LAI Pack Factory CLI (pack-first).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    # Pack0 planner (alias: pack0)
    p0 = sub.add_parser("plan-pack0", help="Gera um Pack0 (planejamento) para um módulo.")
    p0.add_argument("--module", required=True)
    p0.add_argument("--out", required=True, help="Diretório de saída (volume /data/out).")
    p0.add_argument("--trace", default="trace_local")

    p0a = sub.add_parser("pack0", help="Alias para plan-pack0 (compatibilidade com o orquestrador).")
    p0a.add_argument("--module", required=True)
    p0a.add_argument("--out", required=True)
    p0a.add_argument("--trace", default="trace_local")

    # Validate Pack0
    vp0 = sub.add_parser("validate-pack0", help="Valida conformidade do Pack0 (SRS + pack-first).")
    vp0.add_argument("--target", required=True, help="ZIP do Pack0 ou diretório extraído.")
    vp0.add_argument("--out", required=True, help="Arquivo JSON de relatório.")
    vp0.add_argument("--trace", default="trace_local")

    # Merge
    pm = sub.add_parser("merge", help="Faz merge de packs ZIP (ordem importa) e gera snapshot.")
    pm.add_argument("--inputs", nargs="+", required=True, help="Lista de packs ZIP na ordem de aplicação.")
    pm.add_argument("--out", required=True, help="ZIP de saída.")
    pm.add_argument("--tmp", required=True, help="Diretório temporário (volume /data/tmp).")
    pm.add_argument("--trace", default="trace_local")
    pm.add_argument("--no-book", action="store_true", help="Desabilita geração automática do Software Book.")
    pm.add_argument("--mode", default="candidate", choices=["candidate", "promoted"], help="candidate=sem gate; promoted=exige approval.")

    # Diagnóstico
    pd = sub.add_parser("diag", help="Diagnóstico rápido de um pack ZIP.")
    pd.add_argument("--target", required=True)
    pd.add_argument("--out", required=True)
    pd.add_argument("--trace", default="trace_local")

    # Inventory
    pi = sub.add_parser("inventory-scan", help="Gera inventário machine de um ZIP.")
    pi.add_argument("--target", required=True)
    pi.add_argument("--out", required=True)
    pi.add_argument("--trace", default="trace_local")

    # OCA
    po = sub.add_parser("oca-new", help="Gera template de OCA (contrato auditável de mudança).")
    po.add_argument("--pack-target", required=True)
    po.add_argument("--type", default="bugfix")
    po.add_argument("--summary", required=True)
    po.add_argument("--why", required=True)
    po.add_argument("--oca-id", default="", help="Opcional. Se vazio, é auto-gerado.")
    po.add_argument("--author", default="", help="Opcional. Se vazio, tenta LAI_ACTOR_ID, senão 'unknown'.")
    po.add_argument("--reviewer", default="", help="Opcional.")
    po.add_argument("--severity", default="low", choices=["low", "medium", "high"])
    po.add_argument("--blast-radius", default="", help="Lista separada por vírgula.")
    po.add_argument("--rollback-plan", default="reverter para o pack anterior")
    po.add_argument("--out", required=True)
    po.add_argument("--trace", default="trace_local")

    # Run Report (recibo de execução)
    pr = sub.add_parser("run-report", help="Gera RUN_REPORT (recibo) para execução do time.")
    pr.add_argument("--target", required=True, help="ZIP alvo (PEC/Pack).")
    pr.add_argument("--out", required=True, help="Arquivo JSON de saída.")
    pr.add_argument("--actor", default="", help="Opcional. Se vazio, tenta LAI_ACTOR_ID.")
    pr.add_argument("--trace", default="trace_local")

    # Approval (líder)
    pa = sub.add_parser("approve-pack", help="Gera APPROVAL do líder (depende de RUN_REPORT PASS).")
    pa.add_argument("--target", required=True, help="ZIP alvo (PEC/Pack).")
    pa.add_argument("--run-report", required=True, help="JSON do RUN_REPORT (deve ser PASS e bater sha256).")
    pa.add_argument("--decision", default="approved", choices=["approved", "rejected"])
    pa.add_argument("--criteria-version", default="DoD v1.0")
    pa.add_argument("--notes", default="")
    pa.add_argument("--actor", default="", help="Opcional. Se vazio, tenta LAI_ACTOR_ID.")
    pa.add_argument("--out", required=True, help="Arquivo JSON de saída.")
    pa.add_argument("--trace", default="trace_local")

    # Wrap RUN_REPORT/APPROVAL em patch packs
    pwr = sub.add_parser("wrap-run-report", help="Empacota RUN_REPORT.json em patch pack append-only.")
    pwr.add_argument("--in", dest="infile", required=True)
    pwr.add_argument("--out", required=True)
    pwr.add_argument("--trace", default="trace_local")

    pwa = sub.add_parser("wrap-approval", help="Empacota APPROVAL.json em patch pack append-only.")
    pwa.add_argument("--in", dest="infile", required=True)
    pwa.add_argument("--out", required=True)
    pwa.add_argument("--trace", default="trace_local")

    # RTIP sanitize
    ps = sub.add_parser("rtip-sanitize", help="Sanitiza JSONL RTIP/LT100R (NaN->null) para JSON estrito.")
    ps.add_argument("--infile", required=True, help="Arquivo JSONL de entrada.")
    ps.add_argument("--out", required=True, help="Arquivo JSONL de saída (JSON estrito).")
    ps.add_argument("--trace", default="trace_local")

    # Maintenance console
    pmc = sub.add_parser("maint", help="Console de manutenção (snapshot zip).")
    pmc_sub = pmc.add_subparsers(dest="maint_cmd", required=True)
    pmc_s = pmc_sub.add_parser("status", help="Mostra chain_state + contagens.")
    pmc_s.add_argument("--snapshot", required=True)
    pmc_s.add_argument("--out", required=True)
    pmc_s.add_argument("--trace", default="trace_local")

    pmc_w = pmc_sub.add_parser("where", help="Busca por termo em FILEMAP/SOFTWARE_BOOK.")
    pmc_w.add_argument("--snapshot", required=True)
    pmc_w.add_argument("--query", required=True)
    pmc_w.add_argument("--out", required=True)
    pmc_w.add_argument("--trace", default="trace_local")

    pmc_t = pmc_sub.add_parser("triage", help="Sugere correção usando TROUBLESHOOTING/KNOWN_ISSUES.")
    pmc_t.add_argument("--snapshot", required=True)
    pmc_t.add_argument("--query", required=True)
    pmc_t.add_argument("--out", required=True)
    pmc_t.add_argument("--trace", default="trace_local")

    pmc_g = pmc_sub.add_parser("gate-next", help="Gate do próximo pack via chain_state (next_expected/variants).")
    pmc_g.add_argument("--snapshot", required=True)
    pmc_g.add_argument("--expected", required=True, help="Ex.: pack1 | PEC1.01 | pack2")
    pmc_g.add_argument("--out", required=True, help="Arquivo JSON de saída do gate.")
    pmc_g.add_argument("--trace", default="trace_local")

    # MeetCore sim (mínimo)
    pms = sub.add_parser("meetcore-sim", help="Simula eventos MeetCore e valida schemas (mínimo).")
    pms.add_argument("--out", required=True)
    pms.add_argument("--trace", default="trace_local")

    # Sims (mínimo) — paridade com MeetCore
    pcs = sub.add_parser("connect-sim", help="Simula eventos LAI Connect e valida schemas (mínimo).")
    pcs.add_argument("--out", required=True)
    pcs.add_argument("--trace", default="trace_local")

    pas = sub.add_parser("app-sim", help="Simula eventos App LAI e valida schemas (mínimo).")
    pas.add_argument("--out", required=True)
    pas.add_argument("--trace", default="trace_local")

    pcp = sub.add_parser("culture-people-sim", help="Simula eventos Culture & People e valida schemas (mínimo).")
    pcp.add_argument("--out", required=True)
    pcp.add_argument("--trace", default="trace_local")

    # Export seguro (team-safe)
    pem = sub.add_parser("export-manual", help="Exporta manual operacional (somente o arquivo).")
    pem.add_argument("--out", required=True)
    pem.add_argument("--trace", default="trace_local")

    pet = sub.add_parser("export-team-pack", help="Gera ZIP filtrado (team-safe) sem referências/índices.")
    pet.add_argument("--in", dest="infile", required=True, help="Pack ZIP de entrada.")
    pet.add_argument("--out", required=True, help="ZIP de saída (team-safe).")
    pet.add_argument("--policy", default="", help="Policy JSON de audiência (opcional). Default: governance/audience_policy.team_pack0_only.v1.json")
    pet.add_argument("--trace", default="trace_local")

    plc = sub.add_parser("leak-check", help="Gate hard no_leak para ZIP (team-safe).")
    plc.add_argument("--target", required=True, help="ZIP para checar.")
    plc.add_argument("--policy", default="", help="Policy JSON (audience). Default: governance/audience_policy.team_pack0_only.v1.json")
    plc.add_argument("--out", required=True, help="Relatório JSON de saída.")
    plc.add_argument("--trace", default="trace_local")


    # ONCA (inventário auditável)
    pon = sub.add_parser("onca-scan", help="Gera ONCA inventory (JSONL) de um diretório.")
    pon.add_argument("--root", required=True, help="Diretório raiz (ex.: /mnt/data).")
    pon.add_argument("--out", required=True, help="Arquivo JSONL de saída.")
    pon.add_argument("--recursive", action="store_true")
    pon.add_argument("--max-files", type=int, default=5000)
    pon.add_argument("--trace", default="trace_local")

    pov = sub.add_parser("onca-validate", help="Valida ONCA inventory (JSONL).")
    pov.add_argument("--in", dest="infile", required=True, help="Arquivo JSONL de entrada.")
    pov.add_argument("--out", required=True, help="Arquivo JSON de saída.")
    pov.add_argument("--trace", default="trace_local")

    pov2 = sub.add_parser("validate-onca", help="Alias de onca-validate (gate: validate-onca).")
    pov2.add_argument("--inventory", dest="infile", required=True, help="Arquivo JSONL de inventário (entrada).")
    pov2.add_argument("--out", required=True, help="Arquivo JSON de saída.")
    pov2.add_argument("--trace", default="trace_local")


    # Resolver de zip-chains
    prs = sub.add_parser("resolve", help="Resolve referência zip::...::file e extrai bytes.")
    prs.add_argument("--ref", required=True)
    prs.add_argument("--out", required=True)
    prs.add_argument("--trace", default="trace_local")

    # Pack1 scaffold (thin-slice executável)
    p1 = sub.add_parser("plan-pack1", help="Gera um Pack1 (scaffold executável) para um módulo.")
    p1.add_argument("--module", required=True)
    p1.add_argument("--out", required=True)
    p1.add_argument("--trace", default="trace_local")

    p1a = sub.add_parser("pack1", help="Alias para plan-pack1 (compatibilidade).")
    p1a.add_argument("--module", required=True)
    p1a.add_argument("--out", required=True)
    p1a.add_argument("--trace", default="trace_local")

    # Book / Filemap
    pb = sub.add_parser("book-filemap", help="Gera FILEMAP.md para um pack ZIP.")
    pb.add_argument("--target", required=True)
    pb.add_argument("--out", required=True)
    pb.add_argument("--include-restricted", action="store_true", help="Lista também paths restritos (use com cuidado).")
    pb.add_argument("--trace", default="trace_local")

    args = ap.parse_args(argv)

    if args.cmd in ("plan-pack0", "pack0"):
        out_dir = _p(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        generate_pack0(module=args.module, out_dir=out_dir, trace_id=args.trace)
        return 0

    if args.cmd in ("plan-pack1", "pack1"):
        out_dir = _p(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        generate_pack1(module=args.module, out_dir=out_dir, trace_id=args.trace)
        return 0

    if args.cmd == "validate-pack0":
        r = validate_pack0(_p(args.target))
        report = report_to_dict(r)
        report["trace_id"] = args.trace
        write_json(_p(args.out), report)
        return 0 if report.get("ok") else 2

    if args.cmd == "merge":
        inputs = [_p(x) for x in args.inputs]
        merge_packs(
            pack_zips=inputs,
            out_zip=_p(args.out),
            tmp_dir=_p(args.tmp),
            trace_id=args.trace,
            generate_software_book=(not args.no_book),
            mode=args.mode,
        )
        return 0

    if args.cmd == "diag":
        d = run_diag_on_zip(_p(args.target))
        d["trace_id"] = args.trace
        write_json(_p(args.out), d)
        return 0 if d.get("overall_status") == "PASS" else 2

    if args.cmd == "inventory-scan":
        inv = scan_zip(_p(args.target), trace_id=args.trace)
        write_json(_p(args.out), inv)
        return 0

    if args.cmd == "oca-new":
        oca_id = (args.oca_id or "").strip() or ("oca-" + utc_now_iso().replace(":", "").replace("-", "").replace("Z", "") + "-" + uuid.uuid4().hex[:8])
        author = _actor_from_env_or_arg(args.author)
        reviewer = (args.reviewer or "").strip() or None
        blast = [x.strip() for x in (args.blast_radius or "").split(",") if x.strip()]
        o = new_oca(
            oca_id=oca_id,
            pack_target=args.pack_target,
            oca_type=args.type,
            summary=args.summary,
            why=args.why,
            author=author,
            trace_id=args.trace,
            reviewer=reviewer,
            severity=args.severity,
            blast_radius=blast if blast else None,
            rollback_plan=args.rollback_plan,
        )
        _validate("oca.v1.schema.json", o)
        write_json(_p(args.out), o)
        return 0

    if args.cmd == "run-report":
        actor = _actor_from_env_or_arg(args.actor)
        target = _p(args.target)
        pack_sha = sha256_file(target)
        manifest = _read_manifest_from_zip(target)
        pack_ref = _pack_ref_from_manifest_or_zip(manifest, target)
        pack_id = str(manifest.get("pack_id") or "")
        checks: Dict[str, Any] = {}
        failures: List[str] = []
        result = "pass"

        # Pack0 gate via validate-pack0
        if pack_id.startswith("pack0-") or target.name.startswith("pack0-"):
            r = validate_pack0(target)
            rr = report_to_dict(r)
            checks = {"pack0_validate": bool(rr.get("ok"))}
            if not rr.get("ok"):
                result = "fail"
                failures = [str(e) for e in (rr.get("errors") or [])]
        else:
            d = run_diag_on_zip(target)
            checks = d.get("checks") or {}
            if d.get("overall_status") != "PASS":
                result = "fail"
                failures = [f"diag_fail: {checks}"]

        out = {
            "schema_version": "1.0",
            "pack_ref": pack_ref,
            "pack_sha256": pack_sha,
            "result": result,
            "checks": checks,
            "failures": failures,
            "actor_id": actor,
            "trace_id": args.trace,
            "env_fingerprint": f"python={sys.version.split()[0]}",
            "timestamp": utc_now_iso(),
        }
        _validate("pack.run_report.v1.schema.json", out)
        write_json(_p(args.out), out)
        return 0 if result == "pass" else 2

    if args.cmd == "approve-pack":
        actor = _actor_from_env_or_arg(args.actor)
        target = _p(args.target)
        pack_sha = sha256_file(target)

        rr = json.loads(_p(args.run_report).read_text(encoding="utf-8"))
        _validate("pack.run_report.v1.schema.json", rr)

        if rr.get("result") != "pass":
            raise SystemExit("RUN_REPORT não está PASS; não é possível aprovar.")
        if rr.get("pack_sha256") != pack_sha:
            raise SystemExit("RUN_REPORT sha256 não bate com o ZIP alvo; não é possível aprovar.")

        approval = {
            "schema_version": "1.0",
            "pack_ref": rr.get("pack_ref") or target.stem,
            "pack_sha256": pack_sha,
            "decision": args.decision,
            "criteria_version": args.criteria_version,
            "notes": args.notes,
            "actor_id": actor,
            "trace_id": args.trace,
            "timestamp": utc_now_iso(),
        }
        _validate("pack.approval.v1.schema.json", approval)
        write_json(_p(args.out), approval)
        return 0

    if args.cmd == "wrap-run-report":
        rr = json.loads(_p(args.infile).read_text(encoding="utf-8"))
        _validate("pack.run_report.v1.schema.json", rr)
        pack_ref = str(rr.get("pack_ref") or "unknown")
        ts = utc_now_iso().replace(":", "").replace("-", "").replace("Z", "")
        fname = f"history/run_reports/{ts}_{pack_ref}_{uuid.uuid4().hex[:8]}.json"
        patch_files = {fname: json.dumps(rr, ensure_ascii=False, indent=2)}
        _mk_patch_pack(_p(args.out), "patch-run-report", "0.0.1", args.trace, patch_files)
        return 0

    if args.cmd == "wrap-approval":
        apj = json.loads(_p(args.infile).read_text(encoding="utf-8"))
        _validate("pack.approval.v1.schema.json", apj)
        pack_ref = str(apj.get("pack_ref") or "unknown")
        ts = utc_now_iso().replace(":", "").replace("-", "").replace("Z", "")
        fname = f"history/approvals/{ts}_{pack_ref}_{uuid.uuid4().hex[:8]}.json"
        patch_files = {fname: json.dumps(apj, ensure_ascii=False, indent=2)}
        _mk_patch_pack(_p(args.out), "patch-approval", "0.0.1", args.trace, patch_files)
        return 0

    if args.cmd == "rtip-sanitize":
        infile = _p(args.infile)
        outp = _p(args.out)

        def _strict_loads(s: str):
            def bad_const(x):
                return None
            return json.loads(s, parse_constant=bad_const)

        outp.parent.mkdir(parents=True, exist_ok=True)
        with infile.open("r", encoding="utf-8", errors="replace") as fin, outp.open("w", encoding="utf-8") as fout:
            for line in fin:
                line = line.strip()
                if not line:
                    continue
                obj = _strict_loads(line)
                fout.write(json.dumps(obj, ensure_ascii=False) + "\n")
        return 0

    if args.cmd == "maint":
        snapshot = _p(getattr(args, "snapshot", ""))
        out_path = _p(args.out)
        q = getattr(args, "query", "")

        def _zip_read_text(z: zipfile.ZipFile, name: str) -> str:
            try:
                return z.read(name).decode("utf-8", errors="replace")
            except Exception:
                return ""

        with zipfile.ZipFile(snapshot, "r") as z:
            names = z.namelist()
            chain_state = {}
            try:
                chain_state = json.loads(_zip_read_text(z, "history/chain_state.json") or "{}")
            except Exception:
                chain_state = {}

            if args.maint_cmd == "status":
                approvals = [n for n in names if n.startswith("history/approvals/") and n.endswith(".json")]
                run_reports = [n for n in names if n.startswith("history/run_reports/") and n.endswith(".json")]
                out = {
                    "schema_version": "1.0",
                    "trace_id": args.trace,
                    "timestamp": utc_now_iso(),
                    "chain_state": chain_state,
                    "counts": {
                        "approvals": len(approvals),
                        "run_reports": len(run_reports),
                        "history_items": len([n for n in names if n.startswith("history/")]),
                        "docs_public_items": len([n for n in names if n.startswith("docs/public/")]),
                    },
                }
                write_json(out_path, out)
                return 0

            if args.maint_cmd == "where":
                filemap = _zip_read_text(z, "docs/public/FILEMAP.md")
                book = _zip_read_text(z, "docs/public/SOFTWARE_BOOK.md")
                hay = (filemap + "\n" + book).splitlines()
                hits = [ln for ln in hay if q.lower() in ln.lower()]
                out = {
                    "schema_version": "1.0",
                    "trace_id": args.trace,
                    "timestamp": utc_now_iso(),
                    "query": q,
                    "hits": hits[:200],
                }
                write_json(out_path, out)
                return 0

            if args.maint_cmd == "triage":
                ts = _zip_read_text(z, "docs/TROUBLESHOOTING.md")
                ki = _zip_read_text(z, "docs/KNOWN_ISSUES.md")
                rb = _zip_read_text(z, "runbooks/HOW_TO_RUN.md") + "\n" + _zip_read_text(z, "runbooks/HOW_TO_TEST.md")
                corpus = (ts + "\n" + ki + "\n" + rb).splitlines()
                hits = [ln for ln in corpus if q.lower() in ln.lower()]
                out = {
                    "schema_version": "1.0",
                    "trace_id": args.trace,
                    "timestamp": utc_now_iso(),
                    "query": q,
                    "recommendations": hits[:200] or ["Sem match direto; abrir SOFTWARE_BOOK e FILEMAP e seguir runbooks."],
                    "chain_state": chain_state,
                }
                write_json(out_path, out)
                return 0


            if args.maint_cmd == "gate-next":
                expected = str(getattr(args, "expected", "")).strip()
                exp_norm = expected.lower()

                blocking = chain_state.get("blocking_reasons") or []
                next_expected = str(chain_state.get("next_expected","")).strip()
                variants = chain_state.get("next_expected_variants") or []
                variants_norm = [str(v).strip().lower() for v in variants]

                ok = True
                reasons = []

                if not chain_state:
                    ok = False
                    reasons.append("missing_chain_state")
                if blocking:
                    ok = False
                    reasons.append("blocking_reasons_present")
                if not next_expected:
                    ok = False
                    reasons.append("missing_next_expected")

                if ok:
                    if exp_norm != next_expected.lower() and exp_norm not in variants_norm:
                        ok = False
                        reasons.append("expected_mismatch")

                out = {
                    "schema_version": "1.0",
                    "trace_id": args.trace,
                    "timestamp": utc_now_iso(),
                    "ok": ok,
                    "expected": expected,
                    "next_expected": next_expected,
                    "next_expected_variants": variants,
                    "blocking_reasons": blocking,
                    "reasons": reasons,
                }
                write_json(out_path, out)
                return 0 if ok else 2
        return 2


    if args.cmd == "export-manual":
        rep = export_manual(_repo_root(), _p(args.out), args.trace)
        # Report adjacente (não inclui conteúdo)
        write_json(_p(str(_p(args.out)) + ".report.json"), rep)
        return 0

    if args.cmd == "export-team-pack":
        policy_p = _p(args.policy) if getattr(args, 'policy', '') else None
        try:
            rep = export_team_pack(_repo_root(), _p(args.infile), _p(args.out), args.trace, policy_path=policy_p)
        except Exception as e:
            print(str(e), file=sys.stderr)
            return 2
        write_json(_p(str(_p(args.out)) + ".report.json"), rep)
        return 0

    if args.cmd == "leak-check":
        policy_p = _p(args.policy) if getattr(args, 'policy', '') else (_repo_root() / "governance" / "audience_policy.team_pack0_only.v1.json")
        rep = leak_check_zip(_p(args.target), policy_p, out_path=_p(args.out))
        # Enriquecimento operacional (trace/timestamp) sem alterar contrato base
        rep["trace_id"] = args.trace
        rep["timestamp"] = utc_now_iso()
        write_json(_p(args.out), rep)
        return 0 if rep.get("status") == "PASS" else 2


    if args.cmd == "onca-scan":
        rep = scan_onca(_p(args.root), _p(args.out), args.trace, recursive=bool(args.recursive), max_files=int(args.max_files))
        write_json(_p(str(_p(args.out)) + ".summary.json"), rep)
        return 0

    if args.cmd in ("onca-validate","validate-onca"):
        rep = validate_onca(_p(args.infile), args.trace)
        write_json(_p(args.out), rep)
        return 0 if rep.get("ok") else 2

    if args.cmd == "resolve":
        rep = resolve_to_file(str(args.ref), _p(args.out), args.trace)
        write_json(_p(str(_p(args.out)) + ".report.json"), rep)
        return 0

    if args.cmd == "connect-sim":
        out_path = _p(args.out)
        trace = args.trace
        now = utc_now_iso()
        tenant_id = "tenant-demo"
        conv_id = "conv-" + uuid.uuid4().hex[:8]
        msg_id = "msg-" + uuid.uuid4().hex[:8]

        events = [
            {"specversion":"1.0","type":"lai.connect.message.received","source":"lai.connect","id":uuid.uuid4().hex,"time":now,"datacontenttype":"application/json",
             "data":{"tenant_id":tenant_id,"conversation_id":conv_id,"message_id":msg_id,"channel":"whatsapp_official","text":"Olá!","from_id":"lead-1","to_id":"seller-1"}},
            {"specversion":"1.0","type":"lai.connect.message.sent","source":"lai.connect","id":uuid.uuid4().hex,"time":now,"datacontenttype":"application/json",
             "data":{"tenant_id":tenant_id,"conversation_id":conv_id,"message_id":"msg-"+uuid.uuid4().hex[:8],"channel":"whatsapp_official","text":"Posso ajudar com agenda?","from_id":"seller-1","to_id":"lead-1"}},
        ]

        validations = []
        ok = True
        for ev in events:
            schema_file = f"events/{ev['type']}.v1.schema.json"
            schema_path = _contracts_dir() / schema_file
            if schema_path.exists():
                try:
                    schema = json.loads(schema_path.read_text(encoding="utf-8"))
                    jsonschema.validate(ev, schema)
                    validations.append({"type": ev["type"], "status": "pass"})
                except Exception as e:
                    ok = False
                    validations.append({"type": ev["type"], "status": "fail", "error": str(e)})
            else:
                validations.append({"type": ev["type"], "status": "skipped_no_schema"})

        report = {"schema_version":"1.0","trace_id":trace,"timestamp":now,"overall_status":"PASS" if ok else "FAIL","events_count":len(events),"validations":validations}
        write_json(out_path, report)
        return 0 if ok else 2

    if args.cmd == "app-sim":
        out_path = _p(args.out)
        trace = args.trace
        now = utc_now_iso()
        tenant_id = "tenant-demo"

        events = [
            {"specversion":"1.0","type":"lai.app.feed.item.created","source":"lai.app","id":uuid.uuid4().hex,"time":now,"datacontenttype":"application/json",
             "data":{"tenant_id":tenant_id,"item_id":"item-"+uuid.uuid4().hex[:8],"kind":"followup","title":"Próximo passo","body":"Ligar para o lead amanhã","refs":["conv-123"]}},
        ]

        validations = []
        ok = True
        for ev in events:
            schema_file = f"events/{ev['type']}.v1.schema.json"
            schema_path = _contracts_dir() / schema_file
            if schema_path.exists():
                try:
                    schema = json.loads(schema_path.read_text(encoding="utf-8"))
                    jsonschema.validate(ev, schema)
                    validations.append({"type": ev["type"], "status": "pass"})
                except Exception as e:
                    ok = False
                    validations.append({"type": ev["type"], "status": "fail", "error": str(e)})
            else:
                validations.append({"type": ev["type"], "status": "skipped_no_schema"})

        report = {"schema_version":"1.0","trace_id":trace,"timestamp":now,"overall_status":"PASS" if ok else "FAIL","events_count":len(events),"validations":validations}
        write_json(out_path, report)
        return 0 if ok else 2

    if args.cmd == "culture-people-sim":
        out_path = _p(args.out)
        trace = args.trace
        now = utc_now_iso()
        tenant_id = "tenant-demo"

        events = [
            {"specversion":"1.0","type":"lai.culture.session.report.created","source":"lai.culture","id":uuid.uuid4().hex,"time":now,"datacontenttype":"application/json",
             "data":{"tenant_id":tenant_id,"session_id":"sess-"+uuid.uuid4().hex[:8],"report_id":"rep-"+uuid.uuid4().hex[:8],"summary":"Resumo governado","signals":[]}},
        ]

        validations = []
        ok = True
        for ev in events:
            schema_file = f"events/{ev['type']}.v1.schema.json"
            schema_path = _contracts_dir() / schema_file
            if schema_path.exists():
                try:
                    schema = json.loads(schema_path.read_text(encoding="utf-8"))
                    jsonschema.validate(ev, schema)
                    validations.append({"type": ev["type"], "status": "pass"})
                except Exception as e:
                    ok = False
                    validations.append({"type": ev["type"], "status": "fail", "error": str(e)})
            else:
                validations.append({"type": ev["type"], "status": "skipped_no_schema"})

        report = {"schema_version":"1.0","trace_id":trace,"timestamp":now,"overall_status":"PASS" if ok else "FAIL","events_count":len(events),"validations":validations}
        write_json(out_path, report)
        return 0 if ok else 2


    if args.cmd == "meetcore-sim":
        # Simulação mínima: gera eventos e valida schemas se presentes.
        # Saída: relatório JSON com PASS/FAIL e evidências.
        out_path = _p(args.out)
        trace = args.trace
        now = utc_now_iso()
        tenant_id = "tenant-demo"
        call_id = "call-" + uuid.uuid4().hex[:8]

        events = [
            {"specversion":"1.0","type":"meetcore.call.started","source":"lai.meetcore","id":uuid.uuid4().hex,"time":now,"datacontenttype":"application/json",
             "data":{"tenant_id":tenant_id,"call_id":call_id,"room_id":"room-"+uuid.uuid4().hex[:6],"participants":[{"id":"lead-1","role":"lead"},{"id":"seller-1","role":"seller"}]}},
            {"specversion":"1.0","type":"meetcore.transcript.partial","source":"lai.meetcore","id":uuid.uuid4().hex,"time":now,"datacontenttype":"application/json",
             "data":{"tenant_id":tenant_id,"call_id":call_id,"seq":1,"text":"Olá, como posso ajudar?","confidence":0.86}},
            {"specversion":"1.0","type":"meetcore.call.ended","source":"lai.meetcore","id":uuid.uuid4().hex,"time":now,"datacontenttype":"application/json",
             "data":{"tenant_id":tenant_id,"call_id":call_id,"duration_s":62}},
            {"specversion":"1.0","type":"meetcore.postcall.completed","source":"lai.meetcore","id":uuid.uuid4().hex,"time":now,"datacontenttype":"application/json",
             "data":{"tenant_id":tenant_id,"call_id":call_id,"artifacts":["transcript","summary","topics"]}},
        ]

        validations = []
        ok = True
        # Try validate against schemas if present
        for ev in events:
            schema_file = f"events/{ev['type']}.v1.schema.json"
            schema_path = _contracts_dir() / schema_file
            if schema_path.exists():
                try:
                    schema = json.loads(schema_path.read_text(encoding="utf-8"))
                    jsonschema.validate(ev, schema)
                    validations.append({"type": ev["type"], "status": "pass"})
                except Exception as e:
                    ok = False
                    validations.append({"type": ev["type"], "status": "fail", "error": str(e)})
            else:
                validations.append({"type": ev["type"], "status": "skipped_no_schema"})

        report = {
            "schema_version": "1.0",
            "trace_id": trace,
            "timestamp": now,
            "overall_status": "PASS" if ok else "FAIL",
            "events_count": len(events),
            "validations": validations,
            "sample_call_id": call_id,
        }
        write_json(out_path, report)
        return 0 if ok else 2

    if args.cmd == "book-filemap":
        filemap_from_zip(_p(args.target), _p(args.out), public_only=(not args.include_restricted), repo_root=_repo_root())
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())