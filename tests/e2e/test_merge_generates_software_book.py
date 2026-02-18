import zipfile
from pathlib import Path

from app.merger import merge_packs

def _mkzip(path: Path, files: dict):
    with zipfile.ZipFile(path, "w") as z:
        for name, content in files.items():
            z.writestr(name, content)

def test_merge_generates_software_book(tmp_path: Path):
    z1 = tmp_path / "p1.zip"
    z2 = tmp_path / "p2.zip"
    out = tmp_path / "out.zip"
    tmp = tmp_path / "tmpdir"

    _mkzip(z1, {"a.txt": "A"})
    _mkzip(z2, {"b.txt": "B"})

    merge_packs([z1, z2], out_zip=out, tmp_dir=tmp, trace_id="t-merge", generate_software_book=True)

    with zipfile.ZipFile(out, "r") as z:
        names = set(z.namelist())
        assert "docs/public/SOFTWARE_BOOK.md" in names
        assert "docs/public/FILEMAP.md" in names
        # filemap should list merged files
        filemap = z.read("docs/public/FILEMAP.md").decode("utf-8", errors="ignore")
        assert "a.txt" in filemap
        assert "b.txt" in filemap
