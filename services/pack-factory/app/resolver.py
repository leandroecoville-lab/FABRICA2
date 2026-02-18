from __future__ import annotations

import hashlib
import json
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Dict, Any, Tuple

from .utils import utc_now_iso


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def resolve_zip_chain(ref: str) -> Tuple[bytes, Dict[str, Any]]:
    """
    Resolve referência no formato:
      zip::<zip_path_1>::<zip_entry_zip_2>::...::<final_entry_path>

    Exemplo:
      zip::/mnt/data/A.zip::B.zip::docs/PLAN.md
    """
    parts = [p for p in (ref or "").split("::") if p != ""]
    if len(parts) < 3 or parts[0].strip().lower() != "zip":
        raise ValueError("ref inválida. Use: zip::<zip1>::<...>::<file>")

    zip1_path = Path(parts[1]).expanduser()
    if not zip1_path.exists():
        raise FileNotFoundError(f"zip não encontrado: {zip1_path}")

    chain = parts[2:]

    current_zip_path: Path | None = zip1_path
    current_zip_bytes: bytes | None = None

    def _open_zip() -> zipfile.ZipFile:
        if current_zip_path is not None:
            return zipfile.ZipFile(current_zip_path, "r")
        assert current_zip_bytes is not None
        return zipfile.ZipFile(BytesIO(current_zip_bytes), "r")

    # intermediate zips
    for token in chain[:-1]:
        with _open_zip() as z:
            try:
                data = z.read(token)
            except KeyError:
                raise FileNotFoundError(f"entrada não encontrada no zip: {token}")
        current_zip_path = None
        current_zip_bytes = data

    final_name = chain[-1]
    with _open_zip() as z:
        try:
            out_bytes = z.read(final_name)
        except KeyError:
            raise FileNotFoundError(f"entrada final não encontrada no zip: {final_name}")

    report = {
        "schema_version": "1.0",
        "timestamp": utc_now_iso(),
        "ref": ref,
        "bytes": len(out_bytes),
        "sha256": _sha256_bytes(out_bytes),
    }
    return out_bytes, report


def resolve_to_file(ref: str, out_path: Path, trace_id: str) -> Dict[str, Any]:
    b, rep = resolve_zip_chain(ref)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(b)
    rep["trace_id"] = trace_id
    rep["out"] = str(out_path)
    return rep
