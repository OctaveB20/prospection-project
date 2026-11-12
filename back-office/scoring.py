"""Score de priorité (roadmap, phase 1) :
note × log(nb avis) + bonus métier + bonus site absent ou médiocre + bonus concurrents proches avec site.

Un commerce bondé (énormément d'avis) n'a pas forcément besoin de nous : léger malus au-delà de 1 500 avis.
"""
import math

import site_check as sc

BONUS_SITE = {
    sc.AUCUN: 4.0,
    sc.RESEAU: 4.0,
    sc.INACCESSIBLE: 4.0,
    sc.PLATEFORME: 3.0,
    sc.FAIBLE: 2.0,
    sc.SITE: 0.0,
}
RAYON_CONCURRENTS_M = 500


def distance_m(a: dict, b: dict) -> float:
    """Distance à vol d'oiseau (haversine), en mètres."""
    if None in (a.get("lat"), a.get("lng"), b.get("lat"), b.get("lng")):
        return math.inf
    r = 6_371_000
    p1, p2 = math.radians(a["lat"]), math.radians(b["lat"])
    dp, dl = p2 - p1, math.radians(b["lng"] - a["lng"])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def concurrents_avec_site(lieu: dict, tous: list[dict]) -> int:
    """Nombre de commerces du même scan, à moins de 500 m, qui ont un vrai site."""
    return sum(
        1
        for autre in tous
        if autre["place_id"] != lieu["place_id"]
        and autre.get("type_site") in (sc.SITE, sc.FAIBLE)
        and distance_m(lieu, autre) <= RAYON_CONCURRENTS_M
    )


def score(lieu: dict, bonus_metier: float) -> float:
    note = lieu.get("note") or 0
    avis = lieu.get("nb_avis") or 0
    s = note * math.log10(1 + avis)
    s += bonus_metier
    s += BONUS_SITE.get(lieu.get("type_site"), 0.0)
    if lieu.get("type_site") in (sc.SITE, sc.FAIBLE):
        psi = lieu.get("pagespeed_mobile")
        if psi is not None:
            s += 2.0 if psi < 50 else 1.0 if psi < 90 else 0.0
        if lieu.get("site_https") == 0:
            s += 1.0
    s += min(2.0, 0.5 * (lieu.get("concurrents_avec_site") or 0))
    if avis > 1500:
        s -= 2.0
    return round(s, 2)
