"""
SPLASH PAGE - VERSIONE TEST
============================
"""

import streamlit as st
import time
import os
from src.config.settings import LOGO_PATH, APP_NAME
from src.core.database import crea_tabelle
from src.services.dipendenti_service import import_from_excel, count

def show_splash():
    crea_tabelle()
    if count() == 0:
        import_from_excel()
    
    # TEST: due colonne semplicissime
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.write("SINISTRA")
        if os.path.exists(LOGO_PATH):
            from PIL import Image
            st.image(Image.open(LOGO_PATH), width=200)
    
    with col2:
        st.write("DESTRA")
        st.title(APP_NAME)
        st.write("Benvenuto nel gestionale")
        st.progress(100)
        
        if st.button("ACCEDI AL GESTIONALE", type="primary", use_container_width=True):
            st.session_state.show_splash = False
            st.rerun()