"""
ANAGRAFICA DIPENDENTI
=====================
Gestione completa: visualizza, modifica, inserisci, esporta, documenti.
"""

import streamlit as st
import pandas as pd
import os
import io
import time
import base64
from PIL import Image

from src.services.dipendenti_service import (
    get_all, search, update, delete, insert,
    salva_foto, verifica_foto, get_percorso_foto,
    export_to_dataframe
)
from src.core.validators import valida_codice_fiscale, valida_email
from src.core.pdf_generator import genera_pdf
from src.models.dipendente import Dipendente
from src.config.settings import FOTO_DIR, OPZIONI_MEZZO, BASE_DIR


CARTELLA_CI = os.path.join(BASE_DIR, "cartaidentita")
os.makedirs(CARTELLA_CI, exist_ok=True)


def show_anagrafica():
    _mostra_anagrafica()


def _mostra_anagrafica():
    """Mostra la lista dipendenti e la modifica."""
    st.header("👥 Gestione Dipendenti")
    
    lista = get_all()
    
    if not lista:
        st.info("📭 Nessun dipendente trovato.")
        return
    
    df = pd.DataFrame([d.to_dict() for d in lista])
    df["display"] = df["cognome"] + " " + df["nome"]
    
    scelto = st.selectbox(
        "🔍 Seleziona dipendente (scrivi per cercare)",
        df["display"].tolist(),
        key="select_dip",
        index=None,
        placeholder="Scrivi il nome o cognome..."
    )
    
    if scelto:
        res = df[df["display"] == scelto].iloc[0].to_dict()
        
        col_dati, col_foto = st.columns([2, 1])
        
        with col_foto:
            st.subheader("📷 Foto")
            path = os.path.join(FOTO_DIR, str(res.get("foto_nome", "")))
            if res.get("foto_nome") and os.path.exists(path):
                st.image(Image.open(path), use_container_width=True)
            else:
                st.warning("Foto non disponibile")
        
        with col_dati:
            tab1, tab2, tab3, tab4 = st.tabs([
                "📍 Dati Personali", "💼 Lavoro", "🚗 Mezzo", "⚙️ Azioni"
            ])
            
            with tab1:
                u_cog, u_nom, u_cf, u_nas, u_luo, u_ind, u_cit, u_cap = _tab_dati_personali(res)
            
            with tab2:
                u_man, u_cel, u_mai, u_ass, u_sca = _tab_lavoro(res)
            
            with tab3:
                u_mezzo, u_targa = _tab_mezzo(res)
            
            with tab4:
                _tab_azioni(res, u_cog, u_nom, u_cf, u_nas, u_luo, u_ind, u_cit, u_cap,
                           u_man, u_cel, u_mai, u_ass, u_sca, u_mezzo, u_targa)


# ============================================================
#                   TAB DATI PERSONALI
# ============================================================

def _tab_dati_personali(res):
    col_a, col_b = st.columns(2)
    
    with col_a:
        u_cog = st.text_input("Cognome", res.get("cognome", "")).upper()
        u_nom = st.text_input("Nome", res.get("nome", "")).upper()
        u_cf = st.text_input("Codice Fiscale", res.get("codice_fiscale", "")).upper()
        if u_cf and not valida_codice_fiscale(u_cf):
            st.warning("⚠️ Formato codice fiscale non valido")
    
    with col_b:
        u_nas = st.text_input("Data Nascita", res.get("data_nascita", ""))
        u_luo = st.text_input("Luogo Nascita", res.get("luogo_nascita", "")).upper()
        st.markdown("---")
        st.subheader("🏠 Residenza")
        u_ind = st.text_input("Indirizzo", res.get("indirizzo_residenza", "")).upper()
        u_cit = st.text_input("Città", res.get("città_residenza", "")).upper()
        u_cap = st.text_input("CAP", res.get("cap_residenza", ""))
    
    return u_cog, u_nom, u_cf, u_nas, u_luo, u_ind, u_cit, u_cap


# ============================================================
#                   TAB LAVORO
# ============================================================

def _tab_lavoro(res):
    col_a, col_b = st.columns(2)
    
    with col_a:
        u_man = st.text_input("Mansione", res.get("mansione", "")).upper()
        u_cel = st.text_input("Cellulare", res.get("cellulare", ""))
        u_mai = st.text_input("Email", res.get("email", "")).lower()
        if u_mai and not valida_email(u_mai):
            st.warning("⚠️ Formato email non valido")
    
    with col_b:
        u_ass = st.text_input("Data Assunzione", res.get("data_assunzione", ""))
        u_sca = st.text_input("Scadenza Contratto", res.get("scadenza_contratto", ""))
    
    return u_man, u_cel, u_mai, u_ass, u_sca


# ============================================================
#                   TAB MEZZO
# ============================================================

def _tab_mezzo(res):
    col_a, col_b = st.columns(2)
    
    with col_a:
        idx = OPZIONI_MEZZO.index(res.get("mezzo", "")) if res.get("mezzo") in OPZIONI_MEZZO else 0
        u_mezzo = st.selectbox("Tipo Mezzo", OPZIONI_MEZZO, index=idx)
    with col_b:
        u_targa = st.text_input("Targa", res.get("targa", "")).upper()
    
    return u_mezzo, u_targa


# ============================================================
#                   TAB AZIONI
# ============================================================

def _tab_azioni(res, u_cog, u_nom, u_cf, u_nas, u_luo, u_ind, u_cit, u_cap,
               u_man, u_cel, u_mai, u_ass, u_sca, u_mezzo, u_targa):
    
    u_fot = res.get("foto_nome", "")
    u_doc = res.get("documento_nome", "")
    
    col1, col2 = st.columns(2)
    
    # ----- COLONNA SINISTRA: Upload foto e selezione documento -----
    with col1:
        st.subheader("📷 Aggiorna Foto")
        uploaded_foto = st.file_uploader("Carica nuova foto", type=["jpg","jpeg","png"], key="upload_foto")
        if uploaded_foto is not None:
            try:
                nome_file = salva_foto(res.get("id"), uploaded_foto.getbuffer(), u_cog, u_nom)
                u_fot = nome_file
                st.image(uploaded_foto, caption="Anteprima", use_container_width=True)
                st.success("✅ Foto aggiornata! Clicca SALVA.")
            except Exception as e:
                st.error(f"❌ Errore foto: {e}")
        
        st.markdown("---")
        st.subheader("🪪 Carta Identità")
        
        # Documento attuale
        if u_doc and os.path.exists(os.path.join(CARTELLA_CI, u_doc)):
            st.success(f"📄 Documento associato: {u_doc}")
            
            path_doc = os.path.join(CARTELLA_CI, u_doc)
            est = u_doc.split(".")[-1].lower()
            
            if est == "pdf":
                with open(path_doc, "rb") as f:
                    file_bytes = f.read()
                b64 = base64.b64encode(file_bytes).decode()
                st.markdown(f"""
                    <iframe src="data:application/pdf;base64,{b64}"
                            width="100%" height="400px"
                            style="border: 2px solid #2E86C1; border-radius: 5px;">
                    </iframe>
                """, unsafe_allow_html=True)
            elif est in ['jpg', 'jpeg', 'png']:
                st.image(path_doc, caption=u_doc, width=400)
        
        elif u_doc:
            st.warning(f"⚠️ File '{u_doc}' non trovato")
        
        # Selezione da archivio
        st.markdown("---")
        st.write("**Seleziona un documento:**")
        
        if os.path.exists(CARTELLA_CI):
            files_ci = sorted([f for f in os.listdir(CARTELLA_CI) if os.path.isfile(os.path.join(CARTELLA_CI, f))])
            
            # Filtra SOLO documenti di questo dipendente
            nome_key = f"{u_cog}".upper().replace(" ", "_")
            files_filtrati = [f for f in files_ci if nome_key in f.upper()]
            
            if files_filtrati:
                doc_scelto = st.selectbox(
                    "Documenti disponibili", 
                    ["-- Seleziona --"] + files_filtrati, 
                    key=f"sel_doc_{res.get('id')}"
                )
                
                if doc_scelto and doc_scelto != "-- Seleziona --":
                    u_doc = doc_scelto
                    st.success(f"✅ Selezionato: {doc_scelto}")
                    
                    path_sel = os.path.join(CARTELLA_CI, doc_scelto)
                    est = doc_scelto.split(".")[-1].lower()
                    
                    if est == "pdf":
                        with open(path_sel, "rb") as f:
                            file_bytes = f.read()
                        b64 = base64.b64encode(file_bytes).decode()
                        st.markdown(f"""
                            <iframe src="data:application/pdf;base64,{b64}"
                                    width="100%" height="600px"
                                    style="border: 2px solid #ccc; border-radius: 5px;">
                            </iframe>
                            <p style="text-align:center; color:#666; font-size:12px;">
                                💡 Per stampare: clicca col destro sul documento → Stampa
                            </p>
                        """, unsafe_allow_html=True)
                    
                    elif est in ['jpg', 'jpeg', 'png']:
                        st.image(path_sel, caption=doc_scelto, width=400)
            else:
                st.info(f"📭 Nessun documento per {u_cog} {u_nom} nella cartella")
    
    # ----- COLONNA DESTRA: Pulsanti azione -----
    with col2:
        st.subheader("⚙️ Azioni")
        
        if st.button("💾 SALVA MODIFICHE", key="btn_salva", use_container_width=True, type="primary"):
            try:
                dip = Dipendente(
                    id=res.get("id"), cognome=u_cog, nome=u_nom, codice_fiscale=u_cf,
                    data_nascita=u_nas, luogo_nascita=u_luo,
                    indirizzo_residenza=u_ind, citta_residenza=u_cit, cap_residenza=u_cap,
                    mansione=u_man, cellulare=u_cel, email=u_mai,
                    data_assunzione=u_ass, scadenza_contratto=u_sca,
                    mezzo=u_mezzo, targa=u_targa, foto_nome=u_fot, documento_nome=u_doc
                )
                update(dip)
                st.success("✅ Modifiche salvate!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Errore: {e}")
        
        # Elimina con conferma
        if "conferma" not in st.session_state:
            st.session_state.conferma = False
        
        if not st.session_state.conferma:
            if st.button("🗑️ ELIMINA", key="btn_del", use_container_width=True):
                st.session_state.conferma = True
                st.warning("⚠️ Clicca ancora per confermare")
                st.rerun()
        else:
            col_si, col_no = st.columns(2)
            with col_si:
                if st.button("✅ SÌ", key="btn_si", use_container_width=True):
                    try:
                        delete(int(res.get("id")))
                        st.session_state.conferma = False
                        st.success("🗑️ Eliminato!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Errore: {e}")
            with col_no:
                if st.button("❌ NO", key="btn_no", use_container_width=True):
                    st.session_state.conferma = False
                    st.rerun()
        
        # PDF
        if st.button("📄 STAMPA PDF", key="btn_pdf", use_container_width=True):
            try:
                dati = {
                    'cognome': u_cog, 'nome': u_nom, 'codice_fiscale': u_cf,
                    'data_nascita': u_nas, 'luogo_nascita': u_luo,
                    'indirizzo_residenza': u_ind, 'città_residenza': u_cit, 'cap_residenza': u_cap,
                    'mansione': u_man, 'cellulare': u_cel, 'email': u_mai,
                    'data_assunzione': u_ass, 'scadenza_contratto': u_sca,
                    'mezzo': u_mezzo, 'targa': u_targa, 'foto_nome': u_fot
                }
                pdf = genera_pdf(dati)
                st.download_button("📥 Scarica PDF", pdf, f"{u_cog}_{u_nom}.pdf", "application/pdf", key="down_pdf")
            except Exception as e:
                st.error(f"❌ Errore PDF: {e}")


# ============================================================
#                   INSERIMENTO NUOVO DIPENDENTE
# ============================================================

def _mostra_inserimento():
    st.header("➕ Nuovo Dipendente")
    
    tab1, tab2, tab3 = st.tabs(["👤 Dati Personali", "🏠 Residenza", "💼 Lavoro"])
    
    with st.form("form_nuovo"):
        with tab1:
            col1, col2 = st.columns(2)
            with col1: n_cog = st.text_input("Cognome*").upper()
            with col2: n_nom = st.text_input("Nome*").upper()
            col3, col4 = st.columns(2)
            with col3: n_cf = st.text_input("Codice Fiscale*").upper()
            with col4: n_nas = st.text_input("Data Nascita (GG/MM/AAAA)")
            col5, col6 = st.columns(2)
            with col5: n_luo = st.text_input("Luogo Nascita").upper()
            with col6: n_mai = st.text_input("Email").lower()
            uploaded_doc_new = st.file_uploader("🪪 Carta Identità", type=["pdf","jpg","jpeg","png"], key="up_doc_new")
        
        with tab2:
            col7, col8 = st.columns([2,1])
            with col7: n_ind = st.text_input("Indirizzo").upper()
            with col8: n_cap = st.text_input("CAP")
            n_cit = st.text_input("Città").upper()
        
        with tab3:
            col9, col10 = st.columns(2)
            with col9: n_man = st.text_input("Mansione").upper()
            with col10: n_cel = st.text_input("Cellulare")
            col11, col12 = st.columns(2)
            with col11: n_ass = st.text_input("Data Assunzione (GG/MM/AAAA)")
            with col12: n_sca = st.text_input("Scadenza Contratto (GG/MM/AAAA)")
            col13, col14 = st.columns(2)
            with col13: n_mezzo = st.selectbox("Tipo Mezzo", OPZIONI_MEZZO)
            with col14: n_targa = st.text_input("Targa").upper()
        
        if st.form_submit_button("💾 SALVA", type="primary", use_container_width=True):
            errori = []
            if not n_cog or not n_nom: errori.append("❌ Cognome e Nome obbligatori")
            if not n_cf: errori.append("❌ Codice Fiscale obbligatorio")
            elif not valida_codice_fiscale(n_cf): errori.append("❌ CF non valido")
            
            if errori:
                for e in errori: st.error(e)
            else:
                try:
                    dip = Dipendente(cognome=n_cog, nome=n_nom, codice_fiscale=n_cf,
                        data_nascita=n_nas, luogo_nascita=n_luo,
                        indirizzo_residenza=n_ind, citta_residenza=n_cit, cap_residenza=n_cap,
                        mansione=n_man, cellulare=n_cel, email=n_mai,
                        data_assunzione=n_ass, scadenza_contratto=n_sca,
                        mezzo=n_mezzo, targa=n_targa)
                    new_id = insert(dip)
                    
                    if uploaded_doc_new is not None:
                        try:
                            est = uploaded_doc_new.name.split(".")[-1].lower()
                            nome_doc = f"CI_{new_id}_{n_cog}_{n_nom}_{time.strftime('%Y%m%d%H%M%S')}.{est}"
                            nome_doc = nome_doc.replace(" ", "_").lower()
                            with open(os.path.join(CARTELLA_CI, nome_doc), "wb") as f:
                                f.write(uploaded_doc_new.getbuffer())
                            dip.id = new_id
                            dip.documento_nome = nome_doc
                            update(dip)
                        except: pass
                    
                    st.success(f"✅ {n_cog} {n_nom} inserito!")
                    st.balloons()
                except Exception as e:
                    if "UNIQUE" in str(e): st.error("❌ CF già presente")
                    else: st.error(f"❌ Errore: {e}")


# ============================================================
#                   ESPORTAZIONE
# ============================================================

def _mostra_esporta():
    st.header("📊 Esporta Dati")
    try:
        df = export_to_dataframe()
        if not df.empty:
            st.metric("Totale", len(df))
            output = io.BytesIO()
            df.to_excel(output, index=False)
            st.download_button("📥 Scarica Excel", output.getvalue(), "dipendenti.xlsx")
        else:
            st.warning("Nessun dato")
    except Exception as e:
        st.error(f"❌ Errore: {e}")