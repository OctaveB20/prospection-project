"""Stockage SQLite.

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

SCHEMA = """
CREATE TABLE IF NOT EXISTS api_usage (
    day TEXT NOT NULL, sku TEXT NOT NULL, count INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (day, sku)
);
CREATE TABLE IF NOT EXISTS scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
);
"""

STATUTS = ["repéré", "contacté", "démo vue", "relancé", "signé", "refus"]


def maintenant() -> datetime:
    return datetime.now(timezone.utc)


@contextmanager
def connexion():
    config.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(config.DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        con.executescript(SCHEMA)
        yield con
        con.commit()
    finally:
        con.close()


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
            "ON CONFLICT(day, sku) DO UPDATE SET count = count + excluded.count",
            (jour, sku, n),
        )


# ---------- Scans (anti-rescan) ----------
def dernier_scan(metier: str, zone: str) -> sqlite3.Row | None:
    limite = (maintenant() - timedelta(days=config.RESCAN_DAYS)).isoformat()
    with connexion() as con:
        return con.execute(
            "SELECT * FROM scans WHERE metier = ? AND zone = ? AND scanned_at >= ? ORDER BY scanned_at DESC LIMIT 1",
            (metier, normaliser_zone(zone), limite),
        ).fetchone()


def enregistrer_scan(metier: str, zone: str, requetes: int, place_ids: list[str]) -> int:
    with connexion() as con:
        cur = con.execute(
            "INSERT INTO scans (metier, zone, scanned_at, requetes, lieux) VALUES (?, ?, ?, ?, ?)",
            (metier, normaliser_zone(zone), maintenant().isoformat(), requetes, len(place_ids)),
        )
        scan_id = cur.lastrowid
        con.executemany(
            "INSERT OR IGNORE INTO scan_places (scan_id, place_id) VALUES (?, ?)",
            [(scan_id, pid) for pid in place_ids],
        )
    return scan_id


def place_ids_du_scan(scan_id: int) -> list[str]:
    with connexion() as con:
        return [r["place_id"] for r in con.execute("SELECT place_id FROM scan_places WHERE scan_id = ?", (scan_id,))]


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
        rows = con.execute(f"SELECT place_id, data FROM places_cache WHERE place_id IN ({marques})", place_ids)
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


def lire_prospects() -> list[dict]:
    with connexion() as con:
        return [dict(r) for r in con.execute("SELECT * FROM prospects ORDER BY score DESC")]


def lire_analyses(place_ids: list[str]) -> dict[str, dict]:
    if not place_ids:
        return {}
    marques = ",".join("?" * len(place_ids))
    with connexion() as con:
        rows = con.execute(f"SELECT * FROM prospects WHERE place_id IN ({marques})", place_ids)
        return {r["place_id"]: dict(r) for r in rows}


def maj_crm(place_id: str, statut: str, relance_le: str | None, notes: str | None) -> None:
    if statut not in STATUTS:
        raise ValueError(f"Statut inconnu : {statut}")
    with connexion() as con:
        con.execute(
            "UPDATE prospects SET statut = ?, relance_le = ?, notes = ? WHERE place_id = ?",
            (statut, relance_le or None, notes or None, place_id),
        )
