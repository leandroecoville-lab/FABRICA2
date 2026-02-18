from __future__ import annotations

import zipfile
from pathlib import Path

from .public_export import load_public_export_policy, is_public_path


def filemap_from_zip(pack_zip: Path, out_md: Path, public_only: bool = True, repo_root: Path | None = None) -> None:
    """
    Gera FILEMAP.md a partir de um pack ZIP.

    public_only=True (default):
      - aplica governance/public_export_policy.json
      - evita listar paths externalizados/restritos

    public_only=False:
      - lista tudo (use com cuidado; pode expor inventário completo)
    """
    root = repo_root or Path(".")
    policy = load_public_export_policy(root)

    lines = [
        "# FileMap (auto)\n",
        f"- Source: `{pack_zip.name}`\n",
        f"- public_only: `{public_only}`\n",
        "## Arquivos\n",
    ]
    with zipfile.ZipFile(pack_zip, "r") as z:
        for name in sorted(z.namelist()):
            if name.endswith("/"):
                continue
            rel = name.replace("\\", "/")
            if public_only and (not is_public_path(rel, policy)):
                continue
            lines.append(f"- `{rel}`")
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
