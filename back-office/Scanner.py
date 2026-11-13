"""Scanner de prospects : commerces locaux sans vrai site, triés par priorité."""
import pandas as pd
import streamlit as st

import auth
import config  # noqa: F401  (charge .env / secrets en premier)
import db
import places
import prospection
import site_check as sc
from metiers import METIERS, NOMS

st.set_page_config(page_title="Prospection — Scanner", page_icon="🔎", layout="wide")
auth.exiger_mot_de_passe()
auth.verifier_base()
st.title("Scanner de prospects")
st.caption("Commerces bien notés, sans vrai site, triés par priorité. Rien n'est rescanné avant "
           f"{config.RESCAN_DAYS} jours sans le demander.")

# ---------- Quota ----------
u = db.usage(places.SKU_SEARCH)
c1, c2, c3 = st.columns(3)
c1.metric("Requêtes Text Search ce mois", f"{u['mois']} / {config.MONTHLY_LIMIT}")
c2.metric("Aujourd'hui", f"{u['jour']} / {config.DAILY_LIMIT}")
c3.metric("Lieux encore scannables ce mois (≈ 20 / requête)", max(0, config.MONTHLY_LIMIT - u["mois"]) * 20)
st.progress(min(u["mois"] / config.MONTHLY_LIMIT, 1.0))
if config.FAKE_PLACES_FILE:
    st.info(f"Mode test : résultats lus dans {config.FAKE_PLACES_FILE}, aucune requête Google.")
elif not config.PLACES_KEY:
    st.warning("Aucune clé Google : copie `.env.example` en `.env` et mets ta clé GOOGLE_PLACES_API_KEY.")

# ---------- Critères ----------
with st.sidebar:
    st.header("Recherche")
    metiers = st.multiselect("Métiers", NOMS, default=["Fleuriste", "Restaurant", "Plombier"],
                             format_func=lambda n: f"{n} · {METIERS[n]['groupe']}")
    zone = st.text_input("Zone", "Paris 18e", help="Quartier, arrondissement ou ville : « Montmartre », « Paris 11e »…")
    max_lieux = st.select_slider("Lieux par métier", [20, 40, 60], value=60,
                                 help="20 lieux = 1 requête Text Search Enterprise.")
    forcer = st.checkbox(f"Rescanner même si scanné il y a moins de {config.RESCAN_DAYS} jours")
    avec_psi = st.checkbox("Mesurer la vitesse mobile (PageSpeed) des vrais sites", help="Gratuit mais lent : 10 à 30 s par site.")
    st.caption(f"Coût max : {len(metiers) * max_lieux // 20} requête(s), 0 si déjà scanné récemment.")
    lancer = st.button("Lancer le scan", type="primary", disabled=not (metiers and zone.strip()))

    st.divider()
    st.header("Filtres")
    st.caption("Appliqués aux résultats, sans nouvelle requête.")
    presence = st.multiselect("Présence en ligne", sc.TYPES, default=[sc.AUCUN, sc.RESEAU, sc.PLATEFORME, sc.INACCESSIBLE, sc.FAIBLE])
    note_min = st.slider("Note minimum", 0.0, 5.0, 4.0, 0.1)
    avis_min, avis_max = st.slider("Nombre d'avis", 0, 3000, (20, 1500), step=10)

if "resultats" not in st.session_state:
    st.session_state.resultats = []

# ---------- Scan ----------
if lancer:
    tous = []
    with st.status("Scan en cours…", expanded=True) as statut:
        try:
            vus = {}
            for m in metiers:
                res = prospection.scanner(m, zone.strip(), forcer=forcer, max_lieux=max_lieux,
                                          avec_pagespeed=avec_psi, journal=statut.write)
                for l in res["lieux"]:  # un commerce trouvé sous 2 métiers : on garde le meilleur score
                    if l["place_id"] not in vus or (l.get("score") or 0) > (vus[l["place_id"]].get("score") or 0):
                        vus[l["place_id"]] = {**l, "metier": m}
            tous = list(vus.values())
            statut.update(label=f"Terminé : {len(tous)} lieux analysés", state="complete")
        except places.QuotaDepasse as e:
            statut.update(label="Quota atteint", state="error")
            st.error(str(e))
        except Exception as e:  # clé absente, réseau, erreur Google
            statut.update(label="Erreur", state="error")
            st.error(f"Erreur : {e}")
    if tous:
        st.session_state.resultats = tous
        st.rerun()

# ---------- Résultats ----------
lieux = st.session_state.resultats
if not lieux:
    st.info("Choisis des métiers et une zone, puis lance le scan.")
    st.stop()

filtres = prospection.filtrer(lieux, avis_min, avis_max, note_min, presence)
sans_site = sum(1 for l in lieux if l.get("type_site") in sc.SANS_VRAI_SITE)
k1, k2, k3 = st.columns(3)
k1.metric("Lieux analysés", len(lieux))
k2.metric("Sans vrai site", sans_site)
k3.metric("Après filtres", len(filtres))

if not filtres:
    st.warning("Aucun lieu ne passe les filtres : élargis la note, le nombre d'avis ou la présence en ligne.")
    st.stop()

df = pd.DataFrame([{
    "Score": l.get("score"),
    "Nom": l.get("nom"),
    "Métier": l.get("metier"),
    "Présence": l.get("type_site"),
    "Lien actuel": l.get("site"),
    "Note": l.get("note"),
    "Avis": l.get("nb_avis"),
    "Concurrents avec site (500 m)": l.get("concurrents_avec_site"),
    "PageSpeed mobile": l.get("pagespeed_mobile"),
    "HTTPS": {1: "oui", 0: "non"}.get(l.get("site_https"), ""),
    "Réservation": l.get("moteur_resa"),
    "Emails": ", ".join(l.get("emails") or []),
    "Téléphone": l.get("telephone"),
    "Adresse": l.get("adresse"),
    "Formule conseillée": METIERS[l["metier"]]["formule"],
    "Fiche Google": l.get("maps_url"),
} for l in filtres]).fillna({c: "" for c in ["Lien actuel", "HTTPS", "Réservation", "Téléphone", "Adresse", "Fiche Google"]})

st.subheader("Prospects prioritaires")
st.dataframe(
    df, use_container_width=True, hide_index=True,
    column_config={
        "Score": st.column_config.NumberColumn(format="%.1f"),
        "Note": st.column_config.NumberColumn(format="%.1f ★"),
        "Lien actuel": st.column_config.LinkColumn(),
        "Fiche Google": st.column_config.LinkColumn(display_text="ouvrir"),
    },
)
st.download_button("Exporter en CSV", df.to_csv(index=False).encode("utf-8"), "prospects.csv", "text/csv")
st.caption("Tous les lieux analysés sont dans la page CRM (statut « repéré »). Les données Google sont "
           f"gardées {config.CACHE_DAYS} jours au plus, seul le place_id est conservé ensuite.")
