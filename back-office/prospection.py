"""Pipeline : recherche Places -> analyse des sites -> score -> enregistrement.

Règle de coût : un même métier + zone n'est pas rescanné avant RESCAN_DAYS jours
(sauf demande explicite) ; on relit alors le cache et nos analyses déjà faites.
"""
from concurrent.futures import ThreadPoolExecutor

import db
import places
import scoring
import site_check as sc
from metiers import METIERS


def scanner(metier: str, zone: str, forcer: bool = False, max_lieux: int = 60, avec_pagespeed: bool = False,
            journal=print) -> dict:
    """Retourne {"lieux": [...], "requetes": n, "depuis_cache": bool}."""
    m = METIERS[metier]
    precedent = None if forcer else db.dernier_scan(metier, zone)

    if precedent:
        ids = db.place_ids_du_scan(precedent["id"])
        cache = db.lire_cache(ids)
        if len(cache) == len(ids):
            analyses = db.lire_analyses(ids)
            lieux = [{**cache[i], **{k: analyses.get(i, {}).get(k) for k in db.CHAMPS_ANALYSE}} for i in ids]
            journal(f"{metier} · {zone} : déjà scanné le {precedent['scanned_at'][:10]}, résultats relus (0 requête).")
            return {"lieux": _depuis_base(lieux), "requetes": 0, "depuis_cache": True}
        journal("Scan récent mais cache Google expiré : nouveau scan nécessaire.")

    lieux, requetes = places.rechercher(m["requete"], zone, m["type_google"], max_lieux)
    journal(f"{metier} · {zone} : {len(lieux)} lieux trouvés ({requetes} requête(s) Google).")
    db.mettre_en_cache(lieux)

    journal("Analyse des sites (accessibilité, HTTPS, réservation, emails)…")
    with ThreadPoolExecutor(max_workers=8) as ex:
        analyses = list(ex.map(lambda l: sc.analyser(l["site"]), lieux))
    for l, a in zip(lieux, analyses):
        l.update(a)

    if avec_pagespeed:
        a_tester = [l for l in lieux if l["type_site"] in (sc.SITE, sc.FAIBLE)]
        journal(f"PageSpeed mobile sur {len(a_tester)} site(s), 10 à 30 s chacun…")
        with ThreadPoolExecutor(max_workers=4) as ex:
            scores = list(ex.map(lambda l: sc.pagespeed_mobile(l["site"]), a_tester))
        for l, s in zip(a_tester, scores):
            l["pagespeed_mobile"] = s

    for l in lieux:
        l["concurrents_avec_site"] = scoring.concurrents_avec_site(l, lieux)
        l["score"] = scoring.score(l, m["bonus"])

    db.enregistrer_prospects(lieux, metier, zone)
    db.enregistrer_scan(metier, zone, requetes, [l["place_id"] for l in lieux])
    return {"lieux": lieux, "requetes": requetes, "depuis_cache": False}


def _depuis_base(lieux: list[dict]) -> list[dict]:
    for l in lieux:
        if isinstance(l.get("emails"), str):
            l["emails"] = [e for e in l["emails"].split(", ") if e]
    return lieux


def filtrer(lieux: list[dict], avis_min: int = 0, avis_max: int | None = None, note_min: float = 0.0,
            types_site: list[str] | None = None) -> list[dict]:
    sortie = []
    for l in lieux:
        avis, note = l.get("nb_avis") or 0, l.get("note") or 0
        if avis < avis_min or (avis_max is not None and avis > avis_max) or note < note_min:
            continue
        if types_site and l.get("type_site") not in types_site:
            continue
        sortie.append(l)
    return sorted(sortie, key=lambda l: l.get("score") or 0, reverse=True)
