import json
from pathlib import Path

def test_manifest_has_required_fields():
    m = json.loads(Path("02_INVENTORY/manifest.json").read_text(encoding="utf-8"))
    for k in ["schema_version","pack_id","version","created_at","modules","entrypoints","trace"]:
        assert k in m
    assert "trace_id" in m["trace"]
