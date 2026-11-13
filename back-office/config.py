"""Configuration : variables d'environnement (.env en local, st.secrets en ligne)."""
import os
from pathlib import Path

from dotenv import load_dotenv

RACINE = Path(__file__).parent
load_dotenv(RACINE / ".env")

SECRETS_ERREUR = ""
try:  # Streamlit Community Cloud : les Secrets complètent le .env
    import streamlit as st

    for k, v in st.secrets.items():
        # Tolère une section ([general], [secrets]…) et les noms en minuscules.
        valeurs = v.items() if hasattr(v, "items") else [(k, v)]
        for k2, v2 in valeurs:
            if isinstance(v2, (str, int, float, bool)):
                os.environ.setdefault(k2.upper(), str(v2))
except Exception as e:  # pas de fichier de secrets en local : normal ; TOML invalide en ligne : signalé
    SECRETS_ERREUR = f"{type(e).__name__} : {e}"


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
def normaliser_url(url: str, mot_de_passe: str = "") -> str:
    """Répare les erreurs de copie courantes dans l'adresse Supabase.

    - guillemets ou espaces en trop autour de l'adresse ;
    - crochets laissés autour du mot de passe ([MonMotDePasse]) ;
    - caractères spéciaux du mot de passe (@ : / ? # % [ ]) : encodés automatiquement ;
    - DATABASE_PASSWORD (optionnel) remplace le mot de passe de l'adresse.
    """
    from urllib.parse import quote, unquote

    url = url.strip().strip("\"'").strip()
    if "://" not in url or "@" not in url:
        return url
    schema, reste = url.split("://", 1)
    identifiants, hote = reste.rsplit("@", 1)  # le dernier @ sépare toujours le mot de passe de l'hôte
    if ":" not in identifiants:
        return url
    user, mdp = identifiants.split(":", 1)
    if mot_de_passe:
        mdp = mot_de_passe
    elif mdp.startswith("[") and mdp.endswith("]") and mdp.upper() != "[YOUR-PASSWORD]":
        mdp = mdp[1:-1]
    return f"{schema}://{user}:{quote(unquote(mdp), safe='')}@{hote}"


DATABASE_URL = normaliser_url(os.getenv("DATABASE_URL", ""), os.getenv("DATABASE_PASSWORD", "").strip())
# Mot de passe d'accès à l'app (obligatoire dès que l'app est en ligne).
APP_PASSWORD = os.getenv("APP_PASSWORD", "")
# Streamlit Community Cloud exécute l'app depuis /mount/src/<dépôt>.
EN_LIGNE = str(RACINE).startswith("/mount/src") or bool(DATABASE_URL)
# Mode test sans clé : fichier JSON au format de la réponse Text Search (voir tests/fixtures).
FAKE_PLACES_FILE = os.getenv("PLACES_FAKE_FILE", "")
