"""
SPLASH PAGE
===========
Schermata iniziale con logo a sinistra e benvenuto a destra.
"""

import streamlit as st
import time
import os
from PIL import Image
from src.config.settings import LOGO_PATH, APP_NAME
from src.core.database import crea_tabelle, crea_tabelle_magazzino
from src.services.dipendenti_service import import_from_excel, count


def show_splash():
    """Mostra la schermata iniziale con logo e accesso."""
    
    # Inizializza DB
    crea_tabelle()
    crea_tabelle_magazzino()
    if count() == 0:
        import_from_excel()
    
    # Layout a due colonne
    col_logo, col_welcome = st.columns([1, 1])
    
    with col_logo:
        st.markdown("<br>", unsafe_allow_html=True)
        if os.path.exists(LOGO_PATH):
            st.image(Image.open(LOGO_PATH), width=350)
        else:
            st.markdown("<h1 style='font-size:100px;text-align:center;'>🛠️</h1>", unsafe_allow_html=True)
    
    with col_welcome:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='color:#2E86C1;font-weight:bold;'>{APP_NAME}</h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:18px;color:#5D6D7E;'>Soluzioni integrate per la gestione aziendale</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Barra caricamento (NASCOSTO il pulsante)
        placeholder_pulsante = st.empty()
        progress = st.progress(0)
        status = st.empty()
        
        messaggi = [
            "🔄 Caricamento moduli...",
            "📡 Connessione database...",
            "✅ Preparazione interfaccia...",
            "🚀 Pronto!"
        ]
        
        for i in range(100):
            progress.progress(i + 1)
            idx = min(i // 25, 3)
            status.text(messaggi[idx])
            time.sleep(0.02)
        
        # Completa la barra
        progress.progress(100)
        status.text("✅ Completato!")
        time.sleep(0.5)
        
        # Rimuovi barra e mostra pulsante VERDE
            
        progress.empty()
        status.empty()
        
        # Pulsante VERDE con HTML/CSS inline
               # Pulsante VERDE con parametri corretti
        with placeholder_pulsante:
            st.markdown("""
                <style>
                div[data-testid="stButton"] button {
                    background-color: #27AE60 !important;
                    color: white !important;
                    font-size: 18px !important;
                    font-weight: bold !important;
                    padding: 12px 24px !important;
                    border-radius: 8px !important;
                    border: 2px solid #27AE60 !important;
                }
                div[data-testid="stButton"] button:hover {
                    background-color: #219A52 !important;
                    border-color: #219A52 !important;
                }
                </style>
            """, unsafe_allow_html=True)
            
            if st.button("🔓 ACCEDI AL GESTIONALE", key="btn_accedi_verde", use_container_width=True):
                st.session_state.show_splash = False
                st.rerun()