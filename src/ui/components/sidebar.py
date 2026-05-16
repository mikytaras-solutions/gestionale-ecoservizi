"""
SIDEBAR COMPONENT
=================
Menu di navigazione laterale con menu a tendina.
"""

import streamlit as st
import os
from src.config.settings import LOGO_PATH, APP_NAME


def render_sidebar():
    """Renderizza la sidebar di navigazione."""
    
    with st.sidebar:
        # Logo
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if os.path.exists(LOGO_PATH):
                from PIL import Image
                st.image(Image.open(LOGO_PATH), use_container_width=True)
        
        st.markdown(f"### {APP_NAME}")
        st.markdown("---")
        
        # Navigazione principale
        if st.button("🏠 Dashboard", key="nav_dash", use_container_width=True):
            st.session_state.current_page = "dashboard"
            st.rerun()
        
        st.markdown("---")
        
        # ============================================================
        # MODULO DIPENDENTI (menu a tendina)
        # ============================================================
        with st.expander("👥 Dipendenti", expanded=False):
            if st.button("📋 Anagrafica", key="dip_anag", use_container_width=True):
                st.session_state.current_page = "anagrafica"
                st.rerun()
            if st.button("➕ Nuovo Dipendente", key="dip_new", use_container_width=True):
                st.session_state.current_page = "nuovo_dipendente"
                st.rerun()
            if st.button("📊 Esporta Dati", key="dip_exp", use_container_width=True):
                st.session_state.current_page = "esporta"
                st.rerun()
        
        # ============================================================
        # MODULO MAGAZZINO (menu a tendina)
        # ============================================================
        with st.expander("📦 Magazzino", expanded=False):
            if st.button("📋 Gestione DPI", key="mag_gest", use_container_width=True):
                st.session_state.current_page = "magazzino"
                st.rerun()
            st.button("📊 Report Magazzino", key="mag_rep", use_container_width=True, disabled=True)
            st.button("⚠️ Sotto Scorta", key="mag_scorta", use_container_width=True, disabled=True)
        
        # ============================================================
        # MODULO VISITE MEDICHE (menu a tendina)
        # ============================================================
        with st.expander("🏥 Visite Mediche", expanded=False):
            st.button("📅 Calendario", key="vis_cal", use_container_width=True, disabled=True)
            st.button("📋 Gestione Visite", key="vis_gest", use_container_width=True, disabled=True)
            st.button("⚠️ Scadenze", key="vis_scad", use_container_width=True, disabled=True)
        
        # ============================================================
        # MODULO FORMAZIONE (menu a tendina)
        # ============================================================
        with st.expander("📚 Formazione", expanded=False):
            st.button("📋 Corsi", key="form_corsi", use_container_width=True, disabled=True)
            st.button("📜 Attestati", key="form_att", use_container_width=True, disabled=True)
            st.button("⚠️ Scadenze", key="form_scad", use_container_width=True, disabled=True)
        
        # ============================================================
        # MODULO PRIMA NOTA (menu a tendina)
        # ============================================================
        with st.expander("💶 Prima Nota", expanded=False):
            st.button("💰 Entrate/Uscite", key="cassa_ent", use_container_width=True, disabled=True)
            st.button("📊 Bilancio", key="cassa_bil", use_container_width=True, disabled=True)
        
        # ============================================================
        # MODULO FORNITORI (menu a tendina)
        # ============================================================
        with st.expander("🏢 Fornitori", expanded=False):
            st.button("📋 Anagrafica", key="forn_anag", use_container_width=True, disabled=True)
            st.button("📄 Fatture", key="forn_fatt", use_container_width=True, disabled=True)
        
        st.markdown("---")

        # ============================================================
        #                   MONITORAGGIO
        # ============================================================
        with st.expander("📊 Monitoraggio", expanded=False):
            from src.services.monitoraggio_service import get_statistiche_sistema, crea_backup
            
            stats = get_statistiche_sistema()
            
            st.metric("👥 Dipendenti", stats['dipendenti'])
            st.metric("📦 Articoli", stats['articoli'])
            st.metric("🔄 Movimenti oggi", stats['movimenti_oggi'])
            st.metric("💰 Valore magazzino", f"{stats['valore_magazzino']:.2f}€")
            
            st.markdown("---")
            
            if st.button("📥 Crea Backup", key="btn_backup", use_container_width=True):
                nome = crea_backup()
                if nome:
                    st.success(f"✅ Backup: {nome}")
                    st.rerun()
        
        # Logout
        if st.button("🚪 Logout", key="nav_out", use_container_width=True, type="secondary"):
            st.session_state.show_splash = True
            st.session_state.current_page = "dashboard"
            st.rerun()