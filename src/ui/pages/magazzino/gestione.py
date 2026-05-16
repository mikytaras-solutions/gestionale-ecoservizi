"""
GESTIONE MAGAZZINO DPI
======================
Gestione articoli, carico e scarico DPI.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from src.services.magazzino_service import (
    get_taglie, insert_taglia,
    get_categorie, insert_categoria,
    get_articoli, insert_articolo, update_articolo, delete_articolo,
    carico_articolo, scarico_articolo, get_movimenti
)
from src.services.dipendenti_service import get_all as get_dipendenti
from src.models.magazzino import Articolo


def show_magazzino():
    st.header("📦 Gestione Magazzino DPI")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📂 Categorie e Taglie", "📋 Articoli", "📥 Carico", "📤 Scarico", "🔄 Movimenti"
    ])
    
    with tab1:
        _tab_categorie_taglie()
    with tab2:
        _tab_articoli()
    with tab3:
        _tab_carico()
    with tab4:
        _tab_scarico()
    with tab5:
        _tab_movimenti()


# ============================================================
#                   TAB CATEGORIE E TAGLIE
# ============================================================

def _tab_categorie_taglie():
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📂 Categorie")
        
        with st.form("form_categoria", clear_on_submit=True):
            nome = st.text_input("Nome categoria*", key="cat_nome")
            prefisso = st.text_input("Prefisso codice (es. SCR, GNT)", key="cat_pref")
            
            if st.form_submit_button("➕ Aggiungi Categoria", use_container_width=True):
                if nome:
                    try:
                        insert_categoria(nome, prefisso)
                        st.success(f"Categoria '{nome.upper()}' aggiunta!")
                        st.rerun()
                    except Exception as e:
                        if "UNIQUE constraint" in str(e):
                            st.warning(f"⚠️ La categoria '{nome.upper()}' esiste già!")
                        else:
                            st.error(f"Errore: {e}")
        
        st.markdown("---")
        categorie = get_categorie()
        if categorie:
            for cat in categorie:
                st.write(f"📁 **{cat.nome}**")
                if cat.prefisso:
                    st.write(f"   Prefisso: {cat.prefisso}")
        else:
            st.info("Nessuna categoria")
    
    with col2:
        st.subheader("📏 Taglie")
        
        with st.form("form_taglia", clear_on_submit=True):
            taglia = st.text_input("Nuova taglia*", key="taglia_val")
            
            if st.form_submit_button("➕ Aggiungi Taglia", use_container_width=True):
                if taglia:
                    try:
                        insert_taglia(taglia)
                        st.success(f"Taglia '{taglia.upper()}' aggiunta!")
                        st.rerun()
                    except Exception as e:
                        if "UNIQUE constraint" in str(e):
                            st.warning(f"⚠️ La taglia '{taglia.upper()}' esiste già!")
                        else:
                            st.error(f"Errore: {e}")
        
        st.markdown("---")
        taglie = get_taglie()
        if taglie:
            for t in taglie:
                st.write(f"📏 **{t.taglia}**")
        else:
            st.info("Nessuna taglia")


# ============================================================
#                   TAB ARTICOLI
# ============================================================

def _tab_articoli():
    st.subheader("📋 Articoli DPI")
    
    categorie = get_categorie()
    
    # Filtri compatti
    col_f1, col_f2 = st.columns([1, 1])
    with col_f1:
        lista_cat = [("Tutte le categorie", None)] + [(c.nome, c.id) for c in categorie]
        cat_scelta = st.selectbox("Categoria", [n for n, _ in lista_cat], key="filtro_cat_art")
        cat_id = next((cid for n, cid in lista_cat if n == cat_scelta), None)
    with col_f2:
        cerca = st.text_input("🔍 Cerca articolo", key="cerca_art", placeholder="Codice o descrizione...")
    
    articoli = get_articoli(cat_id)
    
    # Filtra per testo
    if cerca:
        articoli = [a for a in articoli if cerca.upper() in a.codice.upper() or cerca.upper() in a.descrizione.upper()]
    
    st.caption(f"📦 {len(articoli)} articoli trovati")
    
    if articoli:
        for art in articoli:
            nome_cat = next((c.nome for c in categorie if c.id == art.categoria_id), "-")
            nome_taglia = ""
            if art.taglia_id:
                taglie = get_taglie()
                nome_taglia = next((t.taglia for t in taglie if t.id == art.taglia_id), "-")
            
            # Expander compatto
            with st.expander(f"📦 {art.codice} | {art.descrizione[:40]} | Tg. {nome_taglia} | Q.tà: {art.quantita}"):
                _form_modifica_articolo(art, categorie, get_taglie())
    else:
        st.info("Nessun articolo trovato")
    
    st.markdown("---")
    
    # Pulsante mostra/nascondi form nuovo articolo
    if "mostra_form_articolo" not in st.session_state:
        st.session_state.mostra_form_articolo = False
    
    if st.button("➕ Nuovo Articolo" if not st.session_state.mostra_form_articolo else "❌ Chiudi", 
                 use_container_width=True):
        st.session_state.mostra_form_articolo = not st.session_state.mostra_form_articolo
        st.rerun()
    
    if st.session_state.mostra_form_articolo:
        _form_nuovo_articolo(categorie, get_taglie())


def _form_nuovo_articolo(categorie, taglie):
    # Leggi i valori attuali dai widget (fuori dal form!)
    cat_nomi = [c.nome for c in categorie]
    cat_scelta = st.selectbox("Categoria*", cat_nomi, key="art_cat_new") if cat_nomi else None
    
    taglia_nomi = [t.taglia for t in taglie]
    taglia_scelta = st.selectbox("Taglia", ["Nessuna"] + taglia_nomi, key="art_taglia_new")
    
    # Calcola codice suggerito in base alle selezioni attuali
    codice_suggerito = ""
    if cat_scelta and taglia_scelta and taglia_scelta != "Nessuna":
        cat_sel = next((c for c in categorie if c.nome == cat_scelta), None)
        if cat_sel and cat_sel.prefisso:
            from datetime import datetime
            anno = datetime.now().strftime('%Y')
            codice_suggerito = f"{cat_sel.prefisso}/{taglia_scelta}/{anno}"
    
    # Mostra il suggerimento
    if codice_suggerito:
        st.info(f"🪄 Codice generato: **{codice_suggerito}**")
        st.code(codice_suggerito, language=None)
        st.caption("👆 Copia il codice qui sopra e incollalo nel campo sottostante")
    
    # Campi del form
    with st.form("form_articolo", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            codice = st.text_input("Codice articolo*", key="art_codice_new", 
                                   placeholder="Incolla qui il codice generato")
        
        with col2:
            descrizione = st.text_input("Descrizione*", key="art_desc_new")
            tipo_articolo = st.text_input("Tipo Articolo", key="art_tipo_new")
            prezzo = st.number_input("Prezzo unitario (€)", min_value=0.0, value=0.0, format="%.2f", key="art_prezzo_new")
        
        with col3:
            scorta_min = st.number_input("Scorta minima", min_value=0, value=0, key="art_scorta_new")
            stato = st.selectbox("Stato", ["ATTIVO", "ESAURITO", "DISMESSO"], key="art_stato_new")
            ubicazione = st.text_input("Ubicazione", key="art_ubic_new")
            posizione = st.text_input("Posizione", key="art_pos_new")
        
        note = st.text_input("Note", key="art_note_new")
        
        cat_id = next((c.id for c in categorie if c.nome == cat_scelta), None) if cat_scelta else None
        taglia_id = next((t.id for t in taglie if t.taglia == taglia_scelta), None) if taglia_scelta != "Nessuna" else None
        
        if st.form_submit_button("💾 Salva Articolo", type="primary", use_container_width=True):
            if codice and descrizione and cat_id:
                try:
                    art = Articolo(
                        codice=codice, descrizione=descrizione, categoria_id=cat_id,
                        tipo_articolo=tipo_articolo, taglia_id=taglia_id,
                        quantita=0,  # ← sempre 0, si aggiorna con Carico
                        prezzo_unitario=prezzo,
                        scorta_minima=scorta_min, stato=stato,
                        ubicazione=ubicazione, posizione=posizione, note=note
                    )
                    insert_articolo(art)
                    st.success("✅ Articolo inserito!")
                    st.rerun()
                except Exception as e:
                    if "UNIQUE constraint" in str(e):
                        st.warning(f"⚠️ Il codice '{codice.upper()}' esiste già!")
                    else:
                        st.error(f"Errore: {e}")
            else:
                st.warning("Compila i campi obbligatori (*)")


# ============================================================
#                   MODIFICA ARTICOLO
# ============================================================

def _form_modifica_articolo(art, categorie, taglie):
    with st.form(f"form_mod_{art.id}"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            codice = st.text_input("Codice", art.codice, key=f"mod_cod_{art.id}")
            descrizione = st.text_input("Descrizione", art.descrizione, key=f"mod_desc_{art.id}")
            tipo_articolo = st.text_input("Tipo Articolo", art.tipo_articolo, key=f"mod_tipo_{art.id}")
            # Quantità SOLO LETTURA
            st.metric("Quantità attuale", art.quantita)
        
        with col2:
            prezzo = st.number_input("Prezzo (€)", value=float(art.prezzo_unitario), format="%.2f", key=f"mod_prez_{art.id}")
            scorta = st.number_input("Scorta min.", value=art.scorta_minima, key=f"mod_scorta_{art.id}")
            stato = st.selectbox("Stato", ["ATTIVO", "ESAURITO", "DISMESSO"],
                                index=["ATTIVO", "ESAURITO", "DISMESSO"].index(art.stato) if art.stato in ["ATTIVO", "ESAURITO", "DISMESSO"] else 0,
                                key=f"mod_stato_{art.id}")
        
        with col3:
            ubicazione = st.text_input("Ubicazione", art.ubicazione, key=f"mod_ubic_{art.id}")
            posizione = st.text_input("Posizione", art.posizione, key=f"mod_pos_{art.id}")
            note = st.text_input("Note", art.note, key=f"mod_note_{art.id}")
        
        st.info(f"📊 Valore giacenza: {art.valore_totale:.2f}€")
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.form_submit_button("💾 Aggiorna", use_container_width=True):
                try:
                    art.codice = codice
                    art.descrizione = descrizione
                    art.tipo_articolo = tipo_articolo
                    art.prezzo_unitario = prezzo
                    art.scorta_minima = scorta
                    art.stato = stato
                    art.ubicazione = ubicazione
                    art.posizione = posizione
                    art.note = note
                    update_articolo(art)
                    
                    st.success("✅ Aggiornato!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Errore: {e}")
        
        with col_b:
            if st.form_submit_button("🗑️ Elimina", use_container_width=True):
                delete_articolo(art.id)
                st.success("🗑️ Eliminato!")
                st.rerun()

# ============================================================
#                   TAB CARICO
# ============================================================

def _tab_carico():
    st.subheader("📥 Carico Merce")
    
    articoli = get_articoli()
    if not articoli:
        st.warning("Nessun articolo. Crealo prima nel tab Articoli.")
        return
    
    with st.form("form_carico", clear_on_submit=True):
        art_dict = {f"{a.codice} - {a.descrizione} ({a.tipo_articolo}) - Q.tà: {a.quantita}": a.id for a in articoli}
        art_scelto = st.selectbox("Articolo", list(art_dict.keys()))
        art_id = art_dict[art_scelto]
        
        col1, col2 = st.columns(2)
        with col1:
            qta = st.number_input("Quantità da caricare", min_value=1, value=1)
        with col2:
            note = st.text_input("Note")
        
        if st.form_submit_button("📥 Registra Carico", type="primary", use_container_width=True):
            try:
                carico_articolo(art_id, qta, note)
                st.success(f"✅ Carico di {qta} pezzi registrato!")
                st.rerun()
            except Exception as e:
                st.error(f"Errore: {e}")


# ============================================================
#                   TAB SCARICO
# ============================================================

def _tab_scarico():
    st.subheader("📤 Consegna DPI a Dipendente")
    
    articoli = get_articoli()
    dipendenti = get_dipendenti()
    
    if not articoli:
        st.warning("Nessun articolo disponibile.")
        return
    if not dipendenti:
        st.warning("Nessun dipendente registrato.")
        return
    
    with st.form("form_scarico", clear_on_submit=True):
        art_dict = {f"{a.codice} - {a.descrizione} ({a.tipo_articolo}) - Disp: {a.quantita}": a for a in articoli if a.quantita > 0}
        
        if not art_dict:
            st.warning("Tutti gli articoli sono esauriti!")
            return
        
        art_scelto = st.selectbox("Articolo da consegnare", list(art_dict.keys()))
        articolo = art_dict[art_scelto]
        
        dip_dict = {f"{d.cognome} {d.nome}": d.id for d in dipendenti}
        dip_scelto = st.selectbox("Dipendente", list(dip_dict.keys()))
        dip_id = dip_dict[dip_scelto]
        
        col1, col2 = st.columns(2)
        with col1:
            qta = st.number_input("Quantità", min_value=1, max_value=articolo.quantita, value=1)
        with col2:
            note = st.text_input("Note")
        
        st.info(f"📦 Disponibile: {articolo.quantita} pezzi")
        
        if st.form_submit_button("📤 Registra Consegna", type="primary", use_container_width=True):
            try:
                scarico_articolo(articolo.id, qta, dip_id, note)
                st.success(f"✅ Consegna di {qta} pezzi a {dip_scelto}!")
                st.rerun()
            except Exception as e:
                st.error(f"Errore: {e}")


# ============================================================
#                   TAB MOVIMENTI
# ============================================================

def _tab_movimenti():
    st.subheader("🔄 Storico Movimenti")
    
    movimenti = get_movimenti(limit=500)
    
    if not movimenti:
        st.info("Nessun movimento registrato")
        return
    
    df = pd.DataFrame(movimenti)
    
    # Filtri
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        tipo_filtro = st.selectbox("Tipo", ["TUTTI", "CARICO", "SCARICO"], key="filtro_tipo")
    
    with col2:
        cat_options = ["TUTTE"] + sorted(df['categoria'].dropna().unique().tolist()) if 'categoria' in df.columns else ["TUTTE"]
        cat_filtro = st.selectbox("Categoria", cat_options, key="filtro_cat")
    
    df_filtrato = df[df['categoria'] == cat_filtro] if cat_filtro != "TUTTE" else df.copy()
    
    with col3:
        taglie_disp = sorted(df_filtrato['taglia'].dropna().unique().tolist()) if 'taglia' in df_filtrato.columns else []
        taglia_options = ["TUTTE"] + taglie_disp
        taglia_filtro = st.selectbox("Taglia", taglia_options, key="filtro_taglia")
    
    if taglia_filtro != "TUTTE":
        df_filtrato = df_filtrato[df_filtrato['taglia'] == taglia_filtro]
    
    with col4:
        dip_options = ["TUTTI"] + sorted(df_filtrato['cognome'].dropna().unique().tolist()) if 'cognome' in df_filtrato.columns else ["TUTTI"]
        dip_filtro = st.selectbox("Dipendente", dip_options, key="filtro_dip")
    
    if tipo_filtro != "TUTTI":
        df_filtrato = df_filtrato[df_filtrato['tipo'] == tipo_filtro]
    if dip_filtro != "TUTTI" and 'cognome' in df_filtrato.columns:
        df_filtrato = df_filtrato[df_filtrato['cognome'] == dip_filtro]
    
    # Unisci cognome e nome in "Dipendente"
    if 'cognome' in df_filtrato.columns and 'nome' in df_filtrato.columns:
        df_filtrato['Dipendente'] = df_filtrato['cognome'].fillna('') + ' ' + df_filtrato['nome'].fillna('')
    
    # Rinomina le colonne per la visualizzazione
    colonne_rename = {
        'data_movimento': 'DATA',
        'tipo': 'TIPO',
        'articolo_cod': 'CODICE',
        'articolo_desc': 'DESCRIZIONE',
        'tipo_articolo': 'TIPO ARTICOLO',
        'taglia': 'TAGLIA',
        'categoria': 'CATEGORIA',
        'quantita': 'QUANTITÀ',
        'Dipendente': 'DIPENDENTE',
        'note': 'NOTE'
    }
    
    # Rinomina
    df_filtrato.rename(columns={k: v for k, v in colonne_rename.items() if k in df_filtrato.columns}, inplace=True)
    
    # Colonne nell'ordine giusto
    colonne_ordine = ['DATA', 'TIPO', 'CODICE', 'DESCRIZIONE', 'TIPO ARTICOLO', 'TAGLIA', 'CATEGORIA', 'QUANTITÀ', 'DIPENDENTE', 'NOTE']
    colonne_da_mostrare = [c for c in colonne_ordine if c in df_filtrato.columns]
    df_view = df_filtrato[colonne_da_mostrare]
    
    # Statistiche
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("📊 Totale", len(df_view))
    with col2: st.metric("📥 Carichi", len(df_view[df_view['TIPO'] == 'CARICO']) if 'TIPO' in df_view.columns else 0)
    with col3: st.metric("📤 Scarichi", len(df_view[df_view['TIPO'] == 'SCARICO']) if 'TIPO' in df_view.columns else 0)
    with col4: st.metric("📦 Q.tà", int(df_view['QUANTITÀ'].sum()) if 'QUANTITÀ' in df_view.columns else 0)
    
    st.markdown("---")
    st.dataframe(df_view, use_container_width=True, hide_index=True)