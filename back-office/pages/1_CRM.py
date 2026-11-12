"""CRM minimal (roadmap, phase 2) : statut, date de relance, notes."""
from datetime import date

import pandas as pd
import streamlit as st

import auth
import config  # noqa: F401
import db
import places

st.set_page_config(page_title="Prospection — CRM", page_icon="📋", layout="wide")
auth.exiger_mot_de_passe()
st.title("CRM")

prospects = db.lire_prospects()
if not prospects:
    st.info("Aucun prospect pour l'instant : lance un scan depuis la page principale.")
    st.stop()

cache = db.lire_cache([p["place_id"] for p in prospects])

with st.sidebar:
    st.header("Filtres")
    statuts = st.multiselect("Statut", db.STATUTS, default=[s for s in db.STATUTS if s not in ("signé", "refus")])
    a_relancer = st.checkbox("À relancer aujourd'hui (ou en retard)")
    metiers = sorted({p["metier"] for p in prospects if p["metier"]})
    sel_metiers = st.multiselect("Métier", metiers)

aujourdhui = date.today().isoformat()
lignes = []
for p in prospects:
    if p["statut"] not in statuts or (sel_metiers and p["metier"] not in sel_metiers):
        continue
    if a_relancer and not (p["relance_le"] and p["relance_le"] <= aujourdhui):
        continue
    g = cache.get(p["place_id"], {})
    lignes.append({
        "place_id": p["place_id"],
        "Nom": g.get("nom") or "(données Google expirées)",
        "Métier": p["metier"],
        "Zone": p["zone"],
        "Score": p["score"],
        "Présence": p["type_site"],
        "Note": g.get("note"),
        "Avis": g.get("nb_avis"),
        "Téléphone": g.get("telephone") or "",
        "Emails": p["emails"] or "",
        "Statut": p["statut"],
        "Relance le": pd.to_datetime(p["relance_le"]).date() if p["relance_le"] else None,
        "Notes": p["notes"] or "",
    })

c1, c2, c3 = st.columns(3)
c1.metric("Prospects", len(prospects))
c2.metric("Affichés", len(lignes))
c3.metric("À relancer aujourd'hui", sum(1 for p in prospects if p["relance_le"] and p["relance_le"] <= aujourdhui
                                        and p["statut"] not in ("signé", "refus")))

if not lignes:
    st.info("Aucun prospect avec ces filtres.")
    st.stop()

df = pd.DataFrame(lignes)
edite = st.data_editor(
    df, use_container_width=True, hide_index=True,
    disabled=[c for c in df.columns if c not in ("Statut", "Relance le", "Notes")],
    column_config={
        "place_id": None,
        "Score": st.column_config.NumberColumn(format="%.1f"),
        "Statut": st.column_config.SelectboxColumn(options=db.STATUTS, required=True),
        "Relance le": st.column_config.DateColumn(format="DD/MM/YYYY"),
        "Notes": st.column_config.TextColumn(width="large"),
    },
    key="crm",
)

if st.button("Enregistrer les modifications", type="primary"):
    def _date(x):
        return None if x is None or pd.isna(x) else pd.Timestamp(x).date().isoformat()

    n = 0
    for avant, apres in zip(df.to_dict("records"), edite.to_dict("records")):
        cle_avant = (avant["Statut"], _date(avant["Relance le"]), avant["Notes"] or "")
        cle_apres = (apres["Statut"], _date(apres["Relance le"]), apres["Notes"] or "")
        if cle_avant != cle_apres:
            db.maj_crm(apres["place_id"], apres["Statut"], cle_apres[1], cle_apres[2])
            n += 1
    st.success(f"{n} prospect(s) mis à jour.")
    st.rerun()

expires = [l["place_id"] for l in lignes if l["Nom"] == "(données Google expirées)"]
if expires:
    st.divider()
    st.write(f"{len(expires)} prospect(s) n'ont plus de données Google en cache.")
    if st.button(f"Rafraîchir ces fiches ({len(expires)} requête(s) Place Details)"):
        try:
            db.mettre_en_cache([places.details(pid) for pid in expires])
            st.rerun()
        except Exception as e:
            st.error(f"Erreur : {e}")
