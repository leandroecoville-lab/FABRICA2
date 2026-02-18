from pathlib import Path
import tempfile
import zipfile

from app.planner import generate_pack0
from app.pack0_validator import validate_pack0


def test_generate_pack0_creates_zip_for_core_modules():
    modules = ["meetcore", "lai-connect", "app-lai", "culture-people"]
    with tempfile.TemporaryDirectory() as td:
        out = Path(td)
        for mod in modules:
            z = generate_pack0(module=mod, out_dir=out, trace_id=f"t1-{mod}")
            assert z.exists(), f"pack0 zip not created for {mod}"
            assert z.suffix == ".zip"
            rep = validate_pack0(z)
            assert rep.ok, f"{mod} gaps: {rep.gaps}"
