import zipfile
from pathlib import Path

from app.resolver import resolve_zip_chain


def test_resolve_zip_chain(tmp_path: Path):
    # create inner zip
    inner = tmp_path / "B.zip"
    with zipfile.ZipFile(inner, "w") as z:
        z.writestr("docs/PLAN.md", "hello-plan")

    # create outer zip containing inner zip as entry
    outer = tmp_path / "A.zip"
    with zipfile.ZipFile(outer, "w") as z:
        z.write(inner, "B.zip")

    ref = f"zip::{outer}::B.zip::docs/PLAN.md"
    b, rep = resolve_zip_chain(ref)
    assert b == b"hello-plan"
    assert rep["bytes"] == len(b)
