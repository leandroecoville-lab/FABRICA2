from __future__ import annotations

import re
import zipfile
from pathlib import Path

from .manifest import new_manifest, write_manifest
from .utils import ensure_dir, write_json


def generate_pack1(module: str, out_dir: Path, trace_id: str) -> Path:
    """
    Pack1 = scaffold executável mínimo (thin-slice).
    Gera estrutura de serviço + contratos + runbooks + testes.
    """
    pack_id = f"pack1-{module}"
    version = "0.0.1"
    pack_root = out_dir / f"{pack_id}-{version}"
    if pack_root.exists():
        import shutil
        shutil.rmtree(pack_root)
    ensure_dir(pack_root)

    for d in [
        "00_INDEXES", "02_INVENTORY", "contracts", "services", "infra", "db/migrations",
        "observability/dashboards", "tests/unit", "tests/integration", "tests/e2e", "runbooks", "docs",
        "history/incidents", "history/changes",
    ]:
        ensure_dir(pack_root / d)

    (pack_root / "00_INDEXES" / "README.md").write_text(
        f"# Pack1 — {module}\n\nThin-slice executável (scaffold).\n",
        encoding="utf-8"
    )

    # Minimal service skeleton
    mod_key = re.sub(r"[^a-zA-Z0-9_]+", "_", module).strip("_")
    svc_dir = pack_root / "services" / mod_key / "app"
    ensure_dir(svc_dir)
    (svc_dir / "__init__.py").write_text("", encoding="utf-8")
    (svc_dir / "main.py").write_text(
        "def handler(event: dict) -> dict:\n"
        "    # TODO: implementar thin-slice\n"
        "    return {\"ok\": True, \"echo\": event}\n",
        encoding="utf-8"
    )

    write_json(pack_root / "contracts" / "README.json", {
        "schema_version": "1.0",
        "module": module,
        "note": "Coloque aqui schemas CloudEvents/DTOs do módulo."
    })

    (pack_root / "runbooks" / "HOW_TO_RUN.md").write_text(
        f"# HOW_TO_RUN — Pack1 ({module})\n\n## Rodar\n\nTODO\n",
        encoding="utf-8"
    )
    (pack_root / "runbooks" / "HOW_TO_TEST.md").write_text(
        f"# HOW_TO_TEST — Pack1 ({module})\n\n## Testes\n\nTODO\n",
        encoding="utf-8"
    )
    (pack_root / "runbooks" / "HOW_TO_ROLLBACK.md").write_text(
        f"# HOW_TO_ROLLBACK — Pack1 ({module})\n\n## Rollback\n\nTODO\n",
        encoding="utf-8"
    )

    (pack_root / "tests" / "unit" / "test_handler.py").write_text(
        f"from services.{mod_key}.app.main import handler\n\n"
        "def test_handler_echo():\n"
        "    out = handler({\"x\": 1})\n"
        "    assert out.get(\"ok\") is True\n"
        "    assert out.get(\"echo\") == {\"x\": 1}\n",
        encoding="utf-8"
    )

    entrypoints = [f"services/{mod_key}/app/main.py", "contracts/README.json"]
    m = new_manifest(pack_id=pack_id, version=version, modules=[module], entrypoints=entrypoints, trace_id=trace_id)
    write_manifest(pack_root, m)

    out_zip = out_dir / f"{pack_id}-{version}.zip"
    if out_zip.exists():
        out_zip.unlink()
    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in pack_root.rglob("*"):
            if p.is_file():
                z.write(p, p.relative_to(pack_root).as_posix())
    return out_zip
