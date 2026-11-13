import json
from pathlib import Path

import pytest

import config
import db
import places
import prospection
import scoring
import site_check as sc

FIXTURE = Path(__file__).parent / "fixtures" / "places_test.json"


@pytest.mark.parametrize("url, attendu", [
    (None, sc.AUCUN),
    ("", sc.AUCUN),
    ("https://www.facebook.com/fleurs", sc.RESEAU),
    ("instagram.com/atelier", sc.RESEAU),
    ("https://linktr.ee/resto", sc.RESEAU),
    ("https://www.pagesjaunes.fr/pros/123", sc.PLATEFORME),
    ("https://www.planity.com/salon-x", sc.PLATEFORME),
    ("https://www.thefork.fr/restaurant/x", sc.PLATEFORME),
    ("https://fleurs.business.site", sc.FAIBLE),
    ("https://sites.google.com/view/fleurs", sc.FAIBLE),
    ("https://x.wixsite.com/accueil", sc.FAIBLE),
    ("https://www.fleurs-montmartre.fr", sc.SITE),
])
def test_classer(url, attendu):
    assert sc.classer(url) == attendu


def test_reseaux_et_plateformes_jamais_visites(monkeypatch):
    monkeypatch.setattr(sc, "_get", lambda *a, **k: pytest.fail("ne doit pas visiter"))
    assert sc.analyser("https://www.instagram.com/x")["type_site"] == sc.RESEAU
    assert sc.analyser(None)["type_site"] == sc.AUCUN


def test_site_inaccessible(monkeypatch):
    monkeypatch.setattr(sc, "_get", lambda *a, **k: (None, None))
    assert sc.analyser("https://mort.example")["type_site"] == sc.INACCESSIBLE


def test_site_analyse(monkeypatch):
    html = ('<html><body><a href="mailto:Bonjour@fleurs.fr">mail</a>'
            '<script src="https://widget.planity.com/x.js"></script></body></html>')
    monkeypatch.setattr(sc, "_get", lambda url, timeout=10: ("https://www.fleurs.fr/", html))
    r = sc.analyser("https://www.fleurs.fr")
    assert r == {"type_site": sc.SITE, "site_https": 1, "moteur_resa": "Planity", "emails": ["bonjour@fleurs.fr"]}


def test_score_favorise_sans_site():
    commun = {"place_id": "a", "note": 4.6, "nb_avis": 120, "concurrents_avec_site": 0}
    sans = scoring.score({**commun, "type_site": sc.AUCUN}, 1.5)
    avec = scoring.score({**commun, "type_site": sc.SITE, "pagespeed_mobile": 95, "site_https": 1}, 1.5)
    assert sans - avec == pytest.approx(4.0)


def test_concurrents_500m():
    a = {"place_id": "a", "lat": 48.8846, "lng": 2.3381}
    proche = {"place_id": "b", "lat": 48.8852, "lng": 2.3375, "type_site": sc.SITE}
    loin = {"place_id": "c", "lat": 48.8950, "lng": 2.3500, "type_site": sc.SITE}
    sans_site = {"place_id": "d", "lat": 48.8847, "lng": 2.3382, "type_site": sc.AUCUN}
    assert scoring.concurrents_avec_site(a, [a, proche, loin, sans_site]) == 1


def _faux_post(pages):
    appels = []

    class Rep:
        def __init__(self, data, code=200):
            self._data, self.status_code = data, code

        def json(self):
            return self._data

        def raise_for_status(self):
            if self.status_code >= 400:
                raise RuntimeError(self.status_code)

    def post(url, headers, json, timeout):
        appels.append({"headers": headers, "json": dict(json)})
        return Rep(pages[len(appels) - 1])

    return post, appels


def test_recherche_field_mask_pagination_quota(monkeypatch):
    data = json.loads(FIXTURE.read_text())
    pages = [{"places": data["places"][:3], "nextPageToken": "p2"}, {"places": data["places"][3:]}]
    post, appels = _faux_post(pages)
    monkeypatch.setattr(places.requests, "post", post)
    lieux, n = places.rechercher("fleuriste", "Paris 18e", "florist", 60)
    assert n == 2 and len(appels) == 2
    assert appels[0]["headers"]["X-Goog-FieldMask"] == places.MASK_SEARCH
    assert "places.photos" not in places.MASK_SEARCH  # jamais de photos Google
    assert appels[0]["json"]["includedType"] == "florist"
    assert appels[1]["json"]["pageToken"] == "p2"
    assert "fake-006" not in {l["place_id"] for l in lieux}  # fermé définitivement
    assert db.usage(places.SKU_SEARCH)["mois"] == 2


def test_quota_bloque(monkeypatch):
    monkeypatch.setattr(config, "DAILY_LIMIT", 1)
    db.ajouter_usage(places.SKU_SEARCH, 1)
    with pytest.raises(places.QuotaDepasse):
        places.verifier_quota(places.SKU_SEARCH)


def test_pipeline_cache_et_crm(monkeypatch):
    monkeypatch.setattr(config, "FAKE_PLACES_FILE", str(FIXTURE))
    monkeypatch.setattr(sc, "_get", lambda *a, **k: (None, None))  # aucun accès réseau
    r1 = prospection.scanner("Fleuriste", "Paris 18e", journal=lambda m: None)
    assert not r1["depuis_cache"] and len(r1["lieux"]) == 5
    types = {l["place_id"]: l["type_site"] for l in r1["lieux"]}
    assert types == {"fake-001": sc.AUCUN, "fake-002": sc.RESEAU, "fake-003": sc.PLATEFORME,
                     "fake-004": sc.INACCESSIBLE, "fake-005": sc.INACCESSIBLE}

    db.maj_crm("fake-001", "contacté", "2026-11-20", "Passée en boutique")
    r2 = prospection.scanner("Fleuriste", "  paris 18E ", journal=lambda m: None)  # même zone normalisée
    assert r2["depuis_cache"] and r2["requetes"] == 0 and len(r2["lieux"]) == 5

    prospection.scanner("Fleuriste", "Paris 18e", forcer=True, journal=lambda m: None)
    p = {x["place_id"]: x for x in db.lire_prospects()}["fake-001"]
    assert (p["statut"], p["relance_le"], p["notes"]) == ("contacté", "2026-11-20", "Passée en boutique")


def test_filtres():
    lieux = [
        {"place_id": "a", "note": 4.8, "nb_avis": 100, "type_site": sc.AUCUN, "score": 9},
        {"place_id": "b", "note": 3.9, "nb_avis": 100, "type_site": sc.AUCUN, "score": 8},
        {"place_id": "c", "note": 4.5, "nb_avis": 5, "type_site": sc.AUCUN, "score": 7},
        {"place_id": "d", "note": 4.9, "nb_avis": 200, "type_site": sc.SITE, "score": 10},
    ]
    ids = [l["place_id"] for l in prospection.filtrer(lieux, 20, 1500, 4.0, [sc.AUCUN])]
    assert ids == ["a"]


def test_cache_purge(monkeypatch):
    db.mettre_en_cache([{"place_id": "x", "nom": "X"}])
    monkeypatch.setattr(config, "CACHE_DAYS", -1)
    assert db.lire_cache(["x"]) == {}


@pytest.mark.parametrize("url, indice", [
    ("postgresql://postgres:motdepasse42@db.abcdefghij.supabase.co:5432/postgres", "Direct connection"),
    ("postgresql://postgres.abc:[motdepasse42]@aws-0-eu-west-3.pooler.supabase.com:6543/postgres", "crochets"),
    ("postgresql://postgres.abc:mot@passe42@aws-0-eu-west-3.pooler.supabase.com:6543/postgres", "contient un @"),
    ("postgresql://postgres:motdepasse42@aws-0-eu-west-3.pooler.supabase.com:6543/postgres", "postgres.<ref"),
])
def test_diagnostic_sans_fuite_du_mot_de_passe(url, indice):
    msg = db.diagnostic_url(url, "")
    assert indice in msg
    assert "motdepasse42" not in msg and "passe42" not in msg


@pytest.mark.parametrize("brute, mdp_attendu", [
    ("postgresql://postgres.abc:[Simple123]@aws-0-eu-west-3.pooler.supabase.com:6543/postgres", "Simple123"),
    ("postgresql://postgres.abc:p@ss/w#rd?%[x]@aws-0-eu-west-3.pooler.supabase.com:6543/postgres", "p@ss/w#rd?%[x]"),
    ('"postgresql://postgres.abc:Simple123@aws-0-eu-west-3.pooler.supabase.com:6543/postgres" ', "Simple123"),
    ("postgresql://postgres.abc:d%C3%A9j%C3%A0%40encod%C3%A9@aws-0-eu-west-3.pooler.supabase.com:6543/postgres", "déjà@encodé"),
])
def test_normaliser_url(brute, mdp_attendu):
    from psycopg.conninfo import conninfo_to_dict

    d = conninfo_to_dict(config.normaliser_url(brute))
    assert d["password"] == mdp_attendu
    assert d["host"] == "aws-0-eu-west-3.pooler.supabase.com" and d["port"] == "6543"
    assert d["user"] == "postgres.abc" and d["dbname"] == "postgres"


def test_normaliser_url_mot_de_passe_separe():
    from psycopg.conninfo import conninfo_to_dict

    url = "postgresql://postgres.abc:[YOUR-PASSWORD]@aws-0-eu-west-3.pooler.supabase.com:6543/postgres"
    assert conninfo_to_dict(config.normaliser_url(url, "a@b:c/d"))["password"] == "a@b:c/d"
    # sans mot de passe séparé, [YOUR-PASSWORD] est gardé tel quel et signalé
    assert "pas été remplacé" in db.diagnostic_url(config.normaliser_url(url))
    assert "YOUR" not in db.masquer_url(config.normaliser_url(url))
