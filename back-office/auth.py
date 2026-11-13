"""Mot de passe d'accès : une app Streamlit Cloud est publique par défaut."""
import hmac

import streamlit as st

import config


def exiger_mot_de_passe() -> None:
    if not config.APP_PASSWORD:
        if config.EN_LIGNE:  # en ligne sans mot de passe : on refuse d'ouvrir
            st.error("APP_PASSWORD introuvable dans les Secrets : l'app reste fermée tant qu'il n'est pas défini.")
            if config.SECRETS_ERREUR and "No secrets" not in config.SECRETS_ERREUR:
                st.warning(f"Les Secrets sont illisibles (format TOML) : {config.SECRETS_ERREUR}")
            st.info('Format attendu, une ligne par secret, valeurs entre guillemets : APP_PASSWORD = "ton-mot-de-passe"')
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


def verifier_base() -> None:
    """Teste la base une fois ; en cas d'échec, affiche un diagnostic lisible au lieu d'une trace."""
    import db

    try:
        db.usage("test")
    except db.ConnexionImpossible as e:
        st.error(str(e))
        st.stop()
