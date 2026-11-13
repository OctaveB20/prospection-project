"""Stockage : SQLite en local, Postgres (Supabase) en ligne si DATABASE_URL est défini.

Conditions Google : seul le place_id est conservé durablement. Les données Google
(nom, note, avis, site, téléphone, position) vont dans places_cache avec une date,
et sont purgées après CACHE_DAYS jours : il faut les rafraîchir, pas les archiver.
Les colonnes de `prospects` sont nos propres données (analyse du site, score, CRM).
"""
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

import config

# Schéma commun SQLite / Postgres (Supabase). Seule la clé auto-incrémentée diffère.
SCHEMA = """
CREATE TABLE IF NOT EXISTS api_usage (
    day TEXT NOT NULL, sku TEXT NOT NULL, count INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (day, sku)
);
CREATE TABLE IF NOT EXISTS scans (
    id {AUTO_ID},
    metier TEXT NOT NULL, zone TEXT NOT NULL, scanned_at TEXT NOT NULL,
    requetes INTEGER NOT NULL, lieux INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS scan_places (
    scan_id INTEGER NOT NULL, place_id TEXT NOT NULL,
    PRIMARY KEY (scan_id, place_id)
);
CREATE TABLE IF NOT EXISTS places_cache (
    place_id TEXT PRIMARY KEY, data TEXT NOT NULL, fetched_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS prospects (
    place_id TEXT PRIMARY KEY,
    metier TEXT, zone TEXT,
    premier_scan TEXT, dernier_scan TEXT,
    type_site TEXT, site_https INTEGER, pagespeed_mobile INTEGER,
    moteur_resa TEXT, emails TEXT, concurrents_avec_site INTEGER,
    score REAL,
    statut TEXT NOT NULL DEFAULT 'repéré',
    relance_le TEXT, notes TEXT
)
"""
TABLES = ["api_usage", "scans", "scan_places", "places_cache", "prospects"]

STATUTS = ["repéré", "contacté", "démo vue", "relancé", "signé", "refus"]


def maintenant() -> datetime:
    return datetime.now(timezone.utc)


def _dict_row(cur, row):
    return {d[0]: v for d, v in zip(cur.description, row)}


class _Con:
    """Même interface pour SQLite et Postgres : placeholders « ? », lignes en dict."""

    def __init__(self, brute, postgres: bool):
        self.brute, self.postgres = brute, postgres

    def _sql(self, sql: str) -> str:
        return sql.replace("?", "%s") if self.postgres else sql

    def execute(self, sql: str, params=()):
        cur = self.brute.cursor()
        cur.execute(self._sql(sql), params)
        return cur

    def executemany(self, sql: str, seq):
        cur = self.brute.cursor()
        cur.executemany(self._sql(sql), list(seq))
        return cur


_pg = None          # connexion Postgres réutilisée (Streamlit relance le script à chaque clic)
_schema_pret = set()


def _ouvrir_pg():
    global _pg
    import psycopg
    from psycopg.rows import dict_row

    if _pg is None or _pg.closed:
        try:
            # prepare_threshold=None : le Transaction pooler de Supabase ne gère pas les requêtes préparées.
            _pg = psycopg.connect(config.DATABASE_URL, prepare_threshold=None, connect_timeout=10, row_factory=dict_row)
        except psycopg.Error as e:  # Operational, Programming… : le message brut peut contenir l'URL
            raise ConnexionImpossible(diagnostic_url(config.DATABASE_URL, str(e))) from None
    return _pg


class ConnexionImpossible(Exception):
    """Connexion à Supabase impossible ; le message ne contient jamais le mot de passe."""


def diagnostic_url(url: str, erreur: str = "") -> str:
    """Explique ce qui cloche dans DATABASE_URL, sans jamais afficher le mot de passe."""
    from urllib.parse import urlsplit

    conseils = []
    url = url.strip()
    try:
        u = urlsplit(url)
        hote, port, user = u.hostname or "", u.port, u.username or ""
    except ValueError:
        hote, port, user = "", None, ""
        conseils.append("L'adresse est illisible : le mot de passe contient sans doute un caractère spécial "
                        "(@ : / ? # % [ ]). Change-le dans Supabase pour lettres + chiffres uniquement.")
    if url.startswith(('"', "'")) or url.endswith(('"', "'")):
        conseils.append("Des guillemets en trop entourent l'adresse : dans les Secrets, une seule paire.")
    if not url.startswith(("postgresql://", "postgres://")):
        conseils.append("L'adresse doit commencer par postgresql://")
    if "YOUR-PASSWORD" in url.upper().replace("%5B", "[").replace("%5D", "]"):
        conseils.append("[YOUR-PASSWORD] n'a pas été remplacé par ton mot de passe.")
    elif "[" in url or "]" in url:
        conseils.append("Des crochets [ ] restent dans l'adresse en dehors du mot de passe.")
    if url.count("@") > 1:
        conseils.append("Le mot de passe contient un @ : change-le pour lettres + chiffres uniquement.")
    if hote.startswith("db.") and hote.endswith(".supabase.co"):
        conseils.append("C'est l'adresse « Direct connection » (db.xxx.supabase.co), joignable seulement en IPv6 : "
                        "Streamlit Cloud ne peut pas l'atteindre. Prends « Transaction pooler » "
                        "(…pooler.supabase.com, port 6543).")
    elif hote and "pooler.supabase.com" not in hote:
        conseils.append("L'hôte n'est pas un pooler Supabase (…pooler.supabase.com) : recopie l'adresse depuis Connect.")
    if "pooler.supabase.com" in hote and user and "." not in user:
        conseils.append("Avec le pooler, l'utilisateur doit être postgres.<ref-du-projet>, pas postgres seul.")
    if "pooler.supabase.com" in hote and port not in (6543, 5432):
        conseils.append("Port attendu : 6543 (Transaction pooler).")
    if "password authentication failed" in erreur:
        conseils.append("Mot de passe refusé : recopie-le, ou réinitialise-le (Project Settings → Database).")
    if "Tenant or user not found" in erreur:
        conseils.append("Utilisateur ou région inconnus : recopie l'adresse complète depuis Connect.")
    if "timeout" in erreur.lower():
        conseils.append("Délai dépassé : le projet Supabase est peut-être en pause (Restore dans le dashboard).")
    if not conseils:
        conseils.append("Recopie l'adresse « Transaction pooler » depuis le bouton Connect de Supabase ; "
                        "vérifie que le projet n'est pas en pause.")
    resume = f"hôte « {hote or '?'} », port {port or '?'}, utilisateur « {user or '?'} »"
    return ("Connexion à Supabase impossible (" + resume + ").\n\nAdresse lue (mot de passe masqué) : `"
            + masquer_url(url) + "`\n- " + "\n- ".join(conseils))


def masquer_url(url: str) -> str:
    """postgresql://user:••••@hôte:port/base — pour vérifier la forme sans exposer le mot de passe."""
    if "://" not in url:
        return url[:12] + "…" if len(url) > 12 else "(vide)" if not url else "…"
    schema, reste = url.split("://", 1)
    if "@" not in reste:
        return f"{schema}://(identifiants manquants : pas de @)"
    identifiants, hote = reste.rsplit("@", 1)
    user = identifiants.split(":", 1)[0]
    return f"{schema}://{user}:••••••@{hote}"


def _creer_schema(con: _Con) -> None:
    cle = config.DATABASE_URL or str(config.DB_PATH)
    if cle in _schema_pret:
        return
    auto = "INTEGER PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY" if con.postgres else "INTEGER PRIMARY KEY AUTOINCREMENT"
    for instruction in SCHEMA.format(AUTO_ID=auto).split(";"):
        if instruction.strip():
            con.execute(instruction)
    if con.postgres:
        # Supabase expose le schéma public via son API REST : RLS sans politique = API fermée.
        # L'app se connecte avec le rôle postgres, qui n'est pas concerné par RLS.
        sans_rls = con.execute(
            "SELECT relname FROM pg_class WHERE relnamespace = 'public'::regnamespace "
            "AND relkind = 'r' AND NOT relrowsecurity AND relname = ANY(?)", (TABLES,)
        ).fetchall()
        for r in sans_rls:  # seulement si besoin : ALTER TABLE exige d'être propriétaire de la table
            con.execute(f"ALTER TABLE {r['relname']} ENABLE ROW LEVEL SECURITY")
    _schema_pret.add(cle)


@contextmanager
def connexion():
    global _pg
    if config.DATABASE_URL:
        brute = _ouvrir_pg()
        con = _Con(brute, postgres=True)
        try:
            _creer_schema(con)
            yield con
            brute.commit()
        except Exception as e:
            try:
                brute.rollback()
            except Exception:
                pass
            if type(e).__module__.startswith("psycopg"):  # connexion coupée par le pooler : on la rouvrira
                _pg = None
            raise
        return

    config.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    brute = sqlite3.connect(config.DB_PATH)
    brute.row_factory = _dict_row
    con = _Con(brute, postgres=False)
    try:
        _creer_schema(con)
        yield con
        brute.commit()
    finally:
        brute.close()


def normaliser_zone(zone: str) -> str:
    return " ".join(zone.lower().split())


# ---------- Quota ----------
def usage(sku: str) -> dict:
    jour = maintenant().date().isoformat()
    with connexion() as con:
        rows = con.execute(
            "SELECT day, count FROM api_usage WHERE sku = ? AND day >= ?", (sku, jour[:8] + "01")
        ).fetchall()
    return {"jour": sum(r["count"] for r in rows if r["day"] == jour), "mois": sum(r["count"] for r in rows)}


def ajouter_usage(sku: str, n: int = 1) -> None:
    jour = maintenant().date().isoformat()
    with connexion() as con:
        con.execute(
            "INSERT INTO api_usage (day, sku, count) VALUES (?, ?, ?) "
            "ON CONFLICT (day, sku) DO UPDATE SET count = api_usage.count + excluded.count",
            (jour, sku, n),
        )


# ---------- Scans (anti-rescan) ----------
def dernier_scan(metier: str, zone: str) -> dict | None:
    limite = (maintenant() - timedelta(days=config.RESCAN_DAYS)).isoformat()
    with connexion() as con:
        return con.execute(
            "SELECT * FROM scans WHERE metier = ? AND zone = ? AND scanned_at >= ? ORDER BY scanned_at DESC LIMIT 1",
            (metier, normaliser_zone(zone), limite),
        ).fetchone()


def enregistrer_scan(metier: str, zone: str, requetes: int, place_ids: list[str]) -> int:
    with connexion() as con:
        scan_id = con.execute(
            "INSERT INTO scans (metier, zone, scanned_at, requetes, lieux) VALUES (?, ?, ?, ?, ?) RETURNING id",
            (metier, normaliser_zone(zone), maintenant().isoformat(), requetes, len(place_ids)),
        ).fetchone()["id"]
        con.executemany(
            "INSERT INTO scan_places (scan_id, place_id) VALUES (?, ?) ON CONFLICT DO NOTHING",
            [(scan_id, pid) for pid in place_ids],
        )
    return scan_id


def place_ids_du_scan(scan_id: int) -> list[str]:
    with connexion() as con:
        return [r["place_id"] for r in con.execute("SELECT place_id FROM scan_places WHERE scan_id = ?", (scan_id,)).fetchall()]


# ---------- Cache Google (temporaire) ----------
def purger_cache() -> int:
    limite = (maintenant() - timedelta(days=config.CACHE_DAYS)).isoformat()
    with connexion() as con:
        return con.execute("DELETE FROM places_cache WHERE fetched_at < ?", (limite,)).rowcount


def mettre_en_cache(lieux: list[dict]) -> None:
    now = maintenant().isoformat()
    with connexion() as con:
        con.executemany(
            "INSERT INTO places_cache (place_id, data, fetched_at) VALUES (?, ?, ?) "
            "ON CONFLICT(place_id) DO UPDATE SET data = excluded.data, fetched_at = excluded.fetched_at",
            [(l["place_id"], json.dumps(l, ensure_ascii=False), now) for l in lieux],
        )


def lire_cache(place_ids: list[str]) -> dict[str, dict]:
    purger_cache()
    if not place_ids:
        return {}
    marques = ",".join("?" * len(place_ids))
    with connexion() as con:
        rows = con.execute(f"SELECT place_id, data FROM places_cache WHERE place_id IN ({marques})", place_ids).fetchall()
        return {r["place_id"]: json.loads(r["data"]) for r in rows}


# ---------- Prospects (nos données + CRM) ----------
CHAMPS_ANALYSE = ["type_site", "site_https", "pagespeed_mobile", "moteur_resa", "emails", "concurrents_avec_site", "score"]


def enregistrer_prospects(lignes: list[dict], metier: str, zone: str) -> int:
    """Insère ou met à jour l'analyse ; ne touche jamais au statut, à la relance ni aux notes."""
    now = maintenant().isoformat()
    with connexion() as con:
        for l in lignes:
            valeurs = {k: l.get(k) for k in CHAMPS_ANALYSE}
            if isinstance(valeurs["emails"], list):
                valeurs["emails"] = ", ".join(valeurs["emails"])
            con.execute(
                f"""INSERT INTO prospects (place_id, metier, zone, premier_scan, dernier_scan, {", ".join(CHAMPS_ANALYSE)})
                    VALUES (?, ?, ?, ?, ?, {", ".join("?" * len(CHAMPS_ANALYSE))})
                    ON CONFLICT(place_id) DO UPDATE SET dernier_scan = excluded.dernier_scan,
                    {", ".join(f"{k} = excluded.{k}" for k in CHAMPS_ANALYSE)}""",
                (l["place_id"], metier, normaliser_zone(zone), now, now, *valeurs.values()),
            )
    return len(lignes)


def etat_base() -> dict:
    """Où l'app écrit et combien de lignes la base contient (affiché dans la barre latérale)."""
    if config.DATABASE_URL:
        from urllib.parse import urlsplit

        try:
            u = urlsplit(config.DATABASE_URL)
            ou = f"Supabase · {u.username or '?'} @ {u.hostname or '?'}"
        except ValueError:
            ou = "Supabase · adresse illisible"
    else:
        ou = f"SQLite local · {config.DB_PATH.name}"
    with connexion() as con:
        compte = {t: con.execute(f"SELECT COUNT(*) AS n FROM {t}").fetchone()["n"] for t in ("prospects", "scans")}
    return {"ou": ou, **compte}


def lire_prospects() -> list[dict]:
    with connexion() as con:
        return con.execute("SELECT * FROM prospects ORDER BY score DESC").fetchall()


def lire_analyses(place_ids: list[str]) -> dict[str, dict]:
    if not place_ids:
        return {}
    marques = ",".join("?" * len(place_ids))
    with connexion() as con:
        rows = con.execute(f"SELECT * FROM prospects WHERE place_id IN ({marques})", place_ids).fetchall()
        return {r["place_id"]: r for r in rows}


def maj_crm(place_id: str, statut: str, relance_le: str | None, notes: str | None) -> None:
    if statut not in STATUTS:
        raise ValueError(f"Statut inconnu : {statut}")
    with connexion() as con:
        con.execute(
            "UPDATE prospects SET statut = ?, relance_le = ?, notes = ? WHERE place_id = ?",
            (statut, relance_le or None, notes or None, place_id),
        )
