"""Google Places API (New) : Text Search avec field mask minimal.

Impact quota : les champs rating / userRatingCount / websiteUri / téléphone sont des
champs « Enterprise » -> chaque page de 20 lieux = 1 requête Text Search Enterprise
(1 000 gratuites / mois, puis 35 $ les 1 000). Une recherche de 60 lieux = 3 requêtes.
Place Details (rafraîchir une fiche) = SKU Place Details Enterprise, compté à part.
"""
import json
from pathlib import Path

import requests

import config
import db

URL_SEARCH = "https://places.googleapis.com/v1/places:searchText"
URL_DETAILS = "https://places.googleapis.com/v1/places/{}"

CHAMPS = [
    "id", "displayName", "formattedAddress", "location", "rating", "userRatingCount",
    "websiteUri", "nationalPhoneNumber", "googleMapsUri", "businessStatus",
]
MASK_SEARCH = ",".join([f"places.{c}" for c in CHAMPS] + ["nextPageToken"])
MASK_DETAILS = ",".join(CHAMPS)

SKU_SEARCH = "text_search_enterprise"
SKU_DETAILS = "place_details_enterprise"


class QuotaDepasse(Exception):
    pass


def verifier_quota(sku: str, n: int = 1) -> None:
    u = db.usage(sku)
    if u["mois"] + n > config.MONTHLY_LIMIT:
        raise QuotaDepasse(f"Limite mensuelle atteinte ({u['mois']}/{config.MONTHLY_LIMIT} requêtes {sku}).")
    if u["jour"] + n > config.DAILY_LIMIT:
        raise QuotaDepasse(f"Limite du jour atteinte ({u['jour']}/{config.DAILY_LIMIT} requêtes {sku}). Réessaie demain.")


def _cle() -> str:
    if not config.PLACES_KEY:
        raise RuntimeError("GOOGLE_PLACES_API_KEY manquante : copie .env.example en .env et mets ta clé.")
    return config.PLACES_KEY


def lieu_depuis_api(p: dict) -> dict:
    loc = p.get("location") or {}
    return {
        "place_id": p["id"],
        "nom": (p.get("displayName") or {}).get("text", ""),
        "adresse": p.get("formattedAddress"),
        "lat": loc.get("latitude"),
        "lng": loc.get("longitude"),
        "note": p.get("rating"),
        "nb_avis": p.get("userRatingCount") or 0,
        "site": p.get("websiteUri"),
        "telephone": p.get("nationalPhoneNumber"),
        "maps_url": p.get("googleMapsUri"),
        "statut_google": p.get("businessStatus"),
    }


def _faux_resultats() -> tuple[list[dict], int]:
    data = json.loads(Path(config.FAKE_PLACES_FILE).read_text(encoding="utf-8"))
    return _ouverts([lieu_depuis_api(p) for p in data.get("places", [])]), 0


def _ouverts(lieux: list[dict]) -> list[dict]:
    """Exclut les commerces fermés définitivement."""
    return [l for l in lieux if l["statut_google"] != "CLOSED_PERMANENTLY"]


def rechercher(requete: str, zone: str, type_google: str | None, max_lieux: int = 60) -> tuple[list[dict], int]:
    """Retourne (lieux, nombre de requêtes facturées). Exclut les commerces fermés définitivement."""
    if config.FAKE_PLACES_FILE:
        return _faux_resultats()

    entetes = {"X-Goog-Api-Key": _cle(), "X-Goog-FieldMask": MASK_SEARCH, "Content-Type": "application/json"}
    corps = {"textQuery": f"{requete} {zone}", "languageCode": "fr", "regionCode": "FR", "pageSize": 20}
    if type_google:
        corps["includedType"] = type_google
        corps["strictTypeFiltering"] = True

    lieux, requetes = [], 0
    while len(lieux) < max_lieux:
        verifier_quota(SKU_SEARCH)
        r = requests.post(URL_SEARCH, headers=entetes, json=corps, timeout=20)
        db.ajouter_usage(SKU_SEARCH)
        requetes += 1
        if r.status_code == 400 and "includedType" in corps:
            # Type non reconnu par Google : on retombe sur la recherche texte seule.
            corps.pop("includedType")
            corps.pop("strictTypeFiltering")
            continue
        r.raise_for_status()
        data = r.json()
        lieux += [lieu_depuis_api(p) for p in data.get("places", [])]
        jeton = data.get("nextPageToken")
        if not jeton:
            break
        corps["pageToken"] = jeton

    return _ouverts(lieux)[:max_lieux], requetes


def details(place_id: str) -> dict:
    """Rafraîchit une fiche (1 requête Place Details Enterprise)."""
    verifier_quota(SKU_DETAILS)
    r = requests.get(
        URL_DETAILS.format(place_id),
        headers={"X-Goog-Api-Key": _cle(), "X-Goog-FieldMask": MASK_DETAILS},
        params={"languageCode": "fr", "regionCode": "FR"},
        timeout=20,
    )
    db.ajouter_usage(SKU_DETAILS)
    r.raise_for_status()
    return lieu_depuis_api(r.json())
