from pathlib import Path

from app.public_export import load_public_export_policy, is_public_path


def test_public_policy_excludes_references_and_semantic_index(tmp_path: Path):
    # policy file
    gov = tmp_path / "governance"
    gov.mkdir(parents=True, exist_ok=True)
    (gov / "public_export_policy.json").write_text(
        '{"exclude_prefixes":["docs/references/","02_INVENTORY/semantic_index/"],"exclude_name_regexes":[]}',
        encoding="utf-8"
    )

    policy = load_public_export_policy(tmp_path)
    assert is_public_path("docs/MANUAL_OPERACIONAL_PACK_FACTORY.md", policy)
    assert not is_public_path("docs/references/secret.pdf", policy)
    assert not is_public_path("02_INVENTORY/semantic_index/x.jsonl", policy)
