from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


# ----------------------------
# Tempo / texto / JSON
# ----------------------------

def utc_now_iso() -> str:
    """UTC ISO-8601 sem microssegundos. Ex: 2026-02-18T12:34:56Z"""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ensure_dir(path: str | Path) -> Path:
    """Garante pasta existente e retorna Path."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def read_text(path: str | Path, default: str = "") -> str:
    p = Path(path)
    if not p.exists():
        return default
    return p.read_text(encoding="utf-8")


def write_text(path: str | Path, text: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def read_json(path: str | Path, default: Any = None) -> Any:
    p = Path(path)
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))


def write_json(path: str | Path, data: Any) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def atomic_write_text(path: str | Path, text: str) -> None:
    """Escreve sem risco de arquivo quebrado (grava em temp e troca)."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir = p.parent
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=str(tmp_dir), delete=False) as f:
        f.write(text)
        tmp_name = f.name
    os.replace(tmp_name, p)


def atomic_write_json(path: str | Path, data: Any) -> None:
    atomic_write_text(path, json.dumps(data, ensure_ascii=False, indent=2))


# ----------------------------
# Hash / arquivos
# ----------------------------

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str | Path) -> str:
    """Hash sha256 de arquivo (stream, não estoura memória)."""
    p = Path(path)
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_exists(path: str | Path) -> bool:
    return Path(path).exists()


def file_size(path: str | Path) -> int:
    p = Path(path)
    return p.stat().st_size if p.exists() else 0


def list_files(root: str | Path, pattern: str = "*") -> list[Path]:
    r = Path(root)
    if not r.exists():
        return []
    return sorted([p for p in r.rglob(pattern) if p.is_file()])


def safe_rm(path: str | Path) -> None:
    p = Path(path)
    if not p.exists():
        return
    if p.is_dir():
        shutil.rmtree(p)
    else:
        p.unlink(missing_ok=True)


def copy_file(src: str | Path, dst: str | Path) -> None:
    s = Path(src)
    d = Path(dst)
    d.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(s, d)


def copy_tree(src: str | Path, dst: str | Path) -> None:
    s = Path(src)
    d = Path(dst)
    if not s.exists():
        return
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(s, d)


# ----------------------------
# Pequenas utilidades
# ----------------------------

def clamp(n: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, n))


def chunks(it: Iterable[Any], size: int) -> list[list[Any]]:
    buf: list[Any] = []
    out: list[list[Any]] = []
    for x in it:
        buf.append(x)
        if len(buf) >= size:
            out.append(buf)
            buf = []
    if buf:
        out.append(buf)
    return out
