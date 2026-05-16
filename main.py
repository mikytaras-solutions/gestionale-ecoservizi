"""
ECOSERVIZI Gestionale Pro
=========================
Entry point principale.
"""

import streamlit as st

st.set_page_config(
    page_title="Ecoservizi Gestionale Pro",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Disabilita i tooltip di aiuto
st.markdown("""
    <style>
    [data-testid="stTooltip"] { display: none !important; }
    [data-testid="stForm"] button[title] { pointer-events: none; }
    </style>
""", unsafe_allow_html=True)

from src.ui.pages.splash import show_splash
from src.ui.pages.dashboard import show_dashboard
from src.ui.components.sidebar import render_sidebar


def main():
    """Punto di ingresso principale."""
    
    if 'show_splash' not in st.session_state:
        st.session_state.show_splash = True
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "dashboard"
    
    if st.session_state.show_splash:
        show_splash()
    else:
        render_sidebar()
        
        if st.session_state.current_page == "dashboard":
            show_dashboard()
        
        elif st.session_state.current_page == "anagrafica":
            from src.ui.pages.dipendenti.anagrafica import _mostra_anagrafica
            _mostra_anagrafica()
        
        elif st.session_state.current_page == "nuovo_dipendente":
            from src.ui.pages.dipendenti.anagrafica import _mostra_inserimento
            _mostra_inserimento()
        
        elif st.session_state.current_page == "esporta":
            from src.ui.pages.dipendenti.anagrafica import _mostra_esporta
            _mostra_esporta()
        
        elif st.session_state.current_page == "magazzino":
            from src.ui.pages.magazzino.gestione import show_magazzino
            show_magazzino()
        
        else:
            show_dashboard()


if __name__ == "__main__":
    main()