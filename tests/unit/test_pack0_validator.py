import zipfile
from pathlib import Path

from app.planner import generate_pack0
from app.pack0_validator import validate_pack0

def test_generated_pack0_passes_validator(tmp_path: Path):
    generate_pack0(module="testmod", out_dir=tmp_path, trace_id="t1")
    zips = list(tmp_path.glob("pack0-testmod-*.zip"))
    assert zips, "no pack0 zip generated"
    zpath = zips[0]
    rep = validate_pack0(zpath)
    assert rep.ok, f"gaps: {rep.gaps}"

def test_validator_fails_on_missing_plan(tmp_path: Path):
    zpath = tmp_path / "broken_pack0.zip"
    with zipfile.ZipFile(zpath, "w") as z:
        z.writestr("docs/PROMPT_CONTINUIDADE.md", "x")
        z.writestr("docs/TROUBLESHOOTING.md", "x")
        z.writestr("docs/DEFINITION_OF_DONE.md", "x")
        z.writestr("runbooks/HOW_TO_RUN.md", "x")
        z.writestr("runbooks/HOW_TO_DEPLOY.md", "x")
        z.writestr("runbooks/HOW_TO_ROLLBACK.md", "x")
        z.writestr("contracts/README.json", "{}")
    rep = validate_pack0(zpath)
    assert not rep.ok
    assert any("missing_path::docs/PLAN.md" in g for g in rep.gaps)


def test_meetcore_pack0_passes_validator(tmp_path: Path):
    generate_pack0(module="meetcore", out_dir=tmp_path, trace_id="t2")
    zips = list(tmp_path.glob("pack0-meetcore-*.zip"))
    assert zips, "no meetcore pack0 zip generated"
    rep = validate_pack0(zips[0])
    assert rep.ok, f"gaps: {rep.gaps}"

def test_meetcore_validator_fails_without_required_docs(tmp_path: Path):
    zpath = tmp_path / "pack0-meetcore-0.0.1.zip"
    # Minimal structure: include manifest indicating pack0-meetcore but omit required docs.
    with zipfile.ZipFile(zpath, "w") as z:
        z.writestr("02_INVENTORY/manifest.json", '{"pack_id":"pack0-meetcore","version":"0.0.1"}')
        z.writestr("docs/PLAN.md", "# Pack0 — Planejamento Padrão (meetcore)\nRF-001\nRNF-001\nUC-001\n")
        z.writestr("docs/PROMPT_CONTINUIDADE.md", "x")
        z.writestr("docs/TROUBLESHOOTING.md", "x")
        z.writestr("docs/DEFINITION_OF_DONE.md", "x")
        z.writestr("runbooks/HOW_TO_RUN.md", "x")
        z.writestr("runbooks/HOW_TO_DEPLOY.md", "x")
        z.writestr("runbooks/HOW_TO_ROLLBACK.md", "x")
        z.writestr("contracts/README.json", "{}")
    rep = validate_pack0(zpath)
    assert not rep.ok
    assert any("missing_path::docs/MEETCORE_SLICES.md" in g for g in rep.gaps)
