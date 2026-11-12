"""Configuration : variables d'environnement (.env en local, st.secrets en ligne)."""
import os
from pathlib import Path

from dotenv import load_dotenv

RACINE = Path(__file__).parent
load_dotenv(RACINE / ".env")

try:  # Streamlit Community Cloud : les Secrets complètent le .env
    import streamlit as st

    for k, v in st.secrets.items():
        if isinstance(v, (str, int, float, bool)):
            os.environ.setdefault(k, str(v))
except Exception:
    pass


def _int(nom: str, defaut: int) -> int:
    try:
        return int(os.getenv(nom, defaut))
    except ValueError:
        return defaut


PLACES_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "")
# Pas de repli sur la clé Places : elle est limitée aux API Maps et serait refusée par PageSpeed.
PAGESPEED_KEY = os.getenv("PAGESPEED_API_KEY", "")
MONTHLY_LIMIT = _int("PLACES_MONTHLY_LIMIT", 900)
DAILY_LIMIT = _int("PLACES_DAILY_LIMIT", 60)
RESCAN_DAYS = _int("RESCAN_DAYS", 30)
CACHE_DAYS = _int("CACHE_DAYS", 30)
DB_PATH = Path(os.getenv("PROSPECTION_DB", RACINE / "data" / "prospection.db"))
# Cloud : chaîne de connexion Postgres de Supabase (Transaction pooler, port 6543).
# Vide = SQLite local (DB_PATH).
DATABASE_URL = os.getenv("DATABASE_URL", "")
# Mot de passe d'accès à l'app (obligatoire dès que l'app est en ligne).
APP_PASSWORD = os.getenv("APP_PASSWORD", "")
# Mode test sans clé : fichier JSON au format de la réponse Text Search (voir tests/fixtures).
FAKE_PLACES_FILE = os.getenv("PLACES_FAKE_FILE", "")
