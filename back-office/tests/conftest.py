import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture(autouse=True)
def base_temporaire(tmp_path, monkeypatch):
    import config
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "test.db")
    monkeypatch.setattr(config, "FAKE_PLACES_FILE", "")
    monkeypatch.setattr(config, "PLACES_KEY", "cle-test")
    yield
