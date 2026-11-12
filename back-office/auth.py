"""Mot de passe d'accès : une app Streamlit Cloud est publique par défaut."""
import hmac

import streamlit as st

import config


def exiger_mot_de_passe() -> None:
    if not config.APP_PASSWORD:
        if config.DATABASE_URL:  # en ligne sans mot de passe : on refuse d'ouvrir
            st.error("APP_PASSWORD manquant dans les Secrets : l'app reste fermée tant qu'il n'est pas défini.")
            st.stop()
        return
    if st.session_state.get("authentifie"):
        return
    with st.form("connexion"):
        mdp = st.text_input("Mot de passe", type="password")
        ok = st.form_submit_button("Entrer")
    if ok and hmac.compare_digest(mdp.encode(), config.APP_PASSWORD.encode()):
        st.session_state.authentifie = True
        st.rerun()
    if ok:
        st.error("Mot de passe incorrect.")
    st.stop()
