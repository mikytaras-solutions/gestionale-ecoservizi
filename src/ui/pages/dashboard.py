"""
DASHBOARD PAGE
==============
Dashboard principale.
"""

import streamlit as st
from datetime import datetime
from src.services.dipendenti_service import count


def show_dashboard():
    """Mostra la dashboard."""
    
    st.title("📊 Dashboard")
    st.markdown(f"📅 {datetime.now().strftime('%d/%m/%Y')}")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("👥 Dipendenti", count())
    
    with col2:
        st.metric("📦 Prodotti", "N/D")
    
    with col3:
        st.metric("🏥 Visite", "N/D")