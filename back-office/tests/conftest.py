import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# TEST_DATABASE_URL=postgresql://... python -m pytest  -> mêmes tests sur Postgres (comme Supabase)
TEST_PG = os.getenv("TEST_DATABASE_URL", "")


@pytest.fixture(autouse=True)
def base_temporaire(tmp_path, monkeypatch):
    import config
    import db

    monkeypatch.setattr(config, "DB_PATH", tmp_path / "test.db")
    monkeypatch.setattr(config, "DATABASE_URL", TEST_PG)
    monkeypatch.setattr(config, "FAKE_PLACES_FILE", "")
    monkeypatch.setattr(config, "PLACES_KEY", "cle-test")
    if TEST_PG:
        with db.connexion() as con:
            for t in db.TABLES:
                con.execute(f"TRUNCATE {t} RESTART IDENTITY")
    yield
