from pathlib import Path

def test_cli_exists():
    assert Path('services/pack-factory/app/cli.py').exists()
