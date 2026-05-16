"""
SPLASH PAGE
===========
Schermata iniziale con logo.
"""

import streamlit as st
import time
import os
from PIL import Image
from src.config.settings import LOGO_PATH, APP_NAME
from src.core.database import crea_tabelle
from src.services.dipendenti_service import import_from_excel, count


def show_splash():
    """Mostra la schermata iniziale."""
    
    # Inizializza DB
    crea_tabelle()
    if count() == 0:
        import_from_excel()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Logo
        if os.path.exists(LOGO_PATH):
            st.image(Image.open(LOGO_PATH), use_container_width=True)
        else:
            st.markdown("<h1 style='text-align:center;'>🛠️</h1>", unsafe_allow_html=True)
        
        st.markdown(f"<h2 style='text-align:center;'>{APP_NAME}</h2>", unsafe_allow_html=True)
        
        # Barra caricamento
        progress = st.progress(0)
        for i in range(100):
            progress.progress(i + 1)
            time.sleep(0.02)
        progress.empty()
        
        # Pulsante accesso
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("🔓 ACCEDI AL GESTIONALE", type="primary", use_container_width=True):
                st.session_state.show_splash = False
                st.rerun()