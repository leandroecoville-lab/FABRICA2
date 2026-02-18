import json
from pathlib import Path

from app.onca_scanner import scan_onca, validate_onca


def test_onca_scan_and_validate_ok(tmp_path: Path):
    # create sample files
    (tmp_path / "a.txt").write_text("hello", encoding="utf-8")
    (tmp_path / "b.md").write_text("# doc", encoding="utf-8")

    out = tmp_path / "onca.jsonl"
    rep = scan_onca(tmp_path, out, trace_id="t1", recursive=False, max_files=100)
    assert rep["rows"] == 2
    assert out.exists()

    v = validate_onca(out, trace_id="t2")
    assert v["ok"] is True
    assert v["counts"]["rows"] == 2


def test_onca_validate_detects_duplicate_sha(tmp_path: Path):
    # two lines with same sha256
    p = tmp_path / "onca.jsonl"
    line1 = {"onca_id":"ONCA-0001","sha256":"abc","path_fisico":"/x","schema_version":"1.0"}
    line2 = {"onca_id":"ONCA-0002","sha256":"abc","path_fisico":"/y","schema_version":"1.0"}
    p.write_text(json.dumps(line1)+"\n"+json.dumps(line2)+"\n", encoding="utf-8")
    v = validate_onca(p, trace_id="t3")
    assert v["ok"] is True
    assert "duplicate_sha256" in (v.get("warnings") or [])
