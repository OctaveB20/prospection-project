"""Présence en ligne d'un commerce : a-t-il un vrai site ?

1. classer() : sans réseau, d'après l'URL donnée par Google.
2. analyser() : visite le site (si c'en est un) : accessible ? HTTPS ? moteur de réservation ? emails ?
3. pagespeed_mobile() : score de performance mobile (PageSpeed Insights, gratuit).

Adapté du scanner du prototype prospect-automation.
"""
import re
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

import config

# Types de présence, du plus intéressant (pas de site) au moins intéressant (vrai site).
AUCUN = "aucun site"
RESEAU = "réseau social"
PLATEFORME = "annuaire / plateforme"
FAIBLE = "site gratuit / faible"
INACCESSIBLE = "site inaccessible"
SITE = "site"
TYPES = [AUCUN, RESEAU, PLATEFORME, INACCESSIBLE, FAIBLE, SITE]
SANS_VRAI_SITE = {AUCUN, RESEAU, PLATEFORME, INACCESSIBLE}

DOMAINES_RESEAUX = (
    "facebook.com", "fb.com", "fb.me", "instagram.com", "tiktok.com", "linktr.ee", "linktree",
    "beacons.ai", "x.com", "twitter.com", "youtube.com", "linkedin.com", "snapchat.com",
    "pinterest.", "wa.me", "whatsapp.com", "taplink.", "carrd.co", "bio.link", "lnk.bio",
)
DOMAINES_PLATEFORMES = (
    "pagesjaunes.fr", "tripadvisor.", "thefork.", "lafourchette.", "ubereats.", "deliveroo.",
    "justeat.", "planity.com", "treatwell.", "kiute.", "booksy.", "doctolib.", "yelp.",
    "google.com", "g.page", "maps.app.goo.gl", "goo.gl", "zenchef.", "sevenrooms.", "opentable.",
    "mappy.", "118712.", "societe.com", "habitatpresto.", "starofservice.", "mesdepanneurs.",
    "interflora.", "aquarelle.", "123fleurs.", "florajet.",
)
# Hébergements gratuits ou constructeurs sur sous-domaine : site existant mais faible.
DOMAINES_FAIBLES = (
    "business.site", "sites.google.com", "wixsite.com", "wordpress.com", "jimdosite.com",
    "jimdofree.com", "webnode.", "e-monsite.com", "site123.me", "godaddysites.com",
    "weebly.com", "blogspot.", "over-blog.", "strikingly.com", "mystrikingly.com",
)

ENTETES = {"User-Agent": "Mozilla/5.0 (compatible; ProspectionLocale/0.1)"}
MOTEURS = {
    "Planity": ["planity.com"],
    "Zenchef": ["zenchef.com"],
    "TheFork": ["thefork.com", "thefork.fr", "lafourchette.com"],
    "SevenRooms": ["sevenrooms.com"],
    "OpenTable": ["opentable.com", "opentable.fr"],
    "Treatwell": ["treatwell.fr"],
    "Calendly": ["calendly.com"],
}
PAGES_UTILES = ("contact", "mention", "legal", "a-propos", "about", "infos", "reserv")
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
EMAIL_BRUIT = ("sentry", "wixpress", "example.", "domain.", ".png", ".jpg", ".webp", ".svg", "u003e")


def _domaine(url: str) -> str:
    if not url.startswith("http"):
        url = "https://" + url
    return urlparse(url).netloc.lower().removeprefix("www.")


def classer(url: str | None) -> str:
    """Type de présence d'après l'URL seule (aucun appel réseau)."""
    if not url or not url.strip():
        return AUCUN
    dom = _domaine(url.strip())
    texte = dom + urlparse(url if url.startswith("http") else "https://" + url).path.lower()
    if any(d in dom for d in DOMAINES_RESEAUX):
        return RESEAU
    if any(d in dom for d in DOMAINES_FAIBLES):  # avant les plateformes (sites.google.com)
        return FAIBLE
    if any(d in texte for d in DOMAINES_PLATEFORMES):
        return PLATEFORME
    return SITE


def _get(url: str, timeout: int = 10):
    try:
        r = requests.get(url, headers=ENTETES, timeout=timeout, allow_redirects=True)
        if r.ok and "text/html" in r.headers.get("content-type", ""):
            return r.url, r.text
    except requests.RequestException:
        pass
    return None, None


def _moteur(html: str, soup: BeautifulSoup) -> str | None:
    urls = [tag.get(a) for tag in soup.find_all(["a", "iframe", "script", "link"]) for a in ("href", "src", "data-src")]
    bloc = (" ".join(u for u in urls if u) + " " + html[:400_000]).lower()
    for moteur, signatures in MOTEURS.items():
        if any(s in bloc for s in signatures):
            return moteur
    return None


def _emails(soup: BeautifulSoup) -> set[str]:
    trouves = {a["href"][7:].split("?")[0].strip().lower() for a in soup.select('a[href^="mailto:"]')}
    trouves |= {m.lower() for m in EMAIL_RE.findall(soup.get_text(" "))}
    return {e for e in trouves if not any(b in e for b in EMAIL_BRUIT)}


def analyser(url: str | None) -> dict:
    """Analyse complète. Ne visite que les sites (ni réseaux sociaux ni plateformes)."""
    sortie = {"type_site": classer(url), "site_https": None, "moteur_resa": None, "emails": []}
    if sortie["type_site"] not in (SITE, FAIBLE):
        return sortie

    depart = url if url.startswith("http") else "https://" + url
    url_finale, html = _get(depart)
    if not html and depart.startswith("https://"):
        url_finale, html = _get("http://" + depart[len("https://"):])
    if not html:
        sortie["type_site"] = INACCESSIBLE
        return sortie

    sortie["site_https"] = int(url_finale.startswith("https://"))
    dom = _domaine(url_finale)
    soup = BeautifulSoup(html, "html.parser")
    pages = [(html, soup)]
    vues = {url_finale}
    for a in soup.find_all("a", href=True):
        complete = urljoin(url_finale, a["href"])
        if _domaine(complete) == dom and complete not in vues and any(k in complete.lower() for k in PAGES_UTILES):
            vues.add(complete)
            _, h = _get(complete)
            if h:
                pages.append((h, BeautifulSoup(h, "html.parser")))
        if len(pages) >= 4:
            break

    emails = set()
    for h, s in pages:
        sortie["moteur_resa"] = sortie["moteur_resa"] or _moteur(h, s)
        emails |= _emails(s)
    # Les emails du domaine du commerce d'abord
    sortie["emails"] = sorted(emails, key=lambda e: (dom not in e, e))[:3]
    return sortie


def pagespeed_mobile(url: str) -> int | None:
    """Score de performance mobile 0-100 (PageSpeed Insights). Lent : 10 à 30 s par site."""
    params = {"url": url if url.startswith("http") else "https://" + url, "strategy": "mobile", "category": "PERFORMANCE"}
    if config.PAGESPEED_KEY:
        params["key"] = config.PAGESPEED_KEY
    try:
        r = requests.get("https://www.googleapis.com/pagespeedonline/v5/runPagespeed", params=params, timeout=60)
        r.raise_for_status()
        score = r.json()["lighthouseResult"]["categories"]["performance"]["score"]
        return round(score * 100) if score is not None else None
    except (requests.RequestException, KeyError, ValueError):
        return None
