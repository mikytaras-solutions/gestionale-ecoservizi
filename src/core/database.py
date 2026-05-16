"""
DATABASE MANAGER
================
Gestisce la connessione al database SQLite.
Thread-safe per Streamlit.
"""

import sqlite3
import os
import threading

_connessioni = {}
_lock = threading.Lock()


def get_connessione():
    """Ottiene la connessione per il thread corrente."""
    thread_id = threading.get_ident()
    if thread_id not in _connessioni or _connessioni[thread_id] is None:
        from src.config.settings import DB_NAME, DATABASE_DIR
        os.makedirs(DATABASE_DIR, exist_ok=True)
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        with _lock:
            _connessioni[thread_id] = conn
    return _connessioni[thread_id]


def get_cursore():
    """Ottiene un cursore per eseguire query."""
    return get_connessione().cursor()


def commit():
    """Esegue il commit delle modifiche."""
    thread_id = threading.get_ident()
    if thread_id in _connessioni and _connessioni[thread_id]:
        _connessioni[thread_id].commit()


def crea_tabelle():
    """Crea le tabelle del database se non esistono."""
    cursore = get_cursore()
    
    cursore.execute('''
        CREATE TABLE IF NOT EXISTS dipendenti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cognome TEXT NOT NULL,
            nome TEXT NOT NULL,
            codice_fiscale TEXT UNIQUE NOT NULL,
            data_nascita TEXT,
            luogo_nascita TEXT,
            indirizzo_residenza TEXT,
            città_residenza TEXT,
            cap_residenza TEXT,
            mansione TEXT,
            cellulare TEXT,
            email TEXT,
            data_assunzione TEXT,
            scadenza_contratto TEXT,
            mezzo TEXT,
            targa TEXT,
            foto_nome TEXT,
            documento_nome TEXT,
            data_creazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_modifica TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    try:
        cursore.execute('''
            CREATE INDEX IF NOT EXISTS idx_cognome_nome 
            ON dipendenti(cognome, nome)
        ''')
    except:
        pass
    
    commit()
    print("✅ Tabelle dipendenti create!")


def crea_tabelle_magazzino():
    """Crea le tabelle per il modulo magazzino DPI."""
    cursore = get_cursore()
    
    cursore.execute('''
        CREATE TABLE IF NOT EXISTS taglie (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            taglia TEXT NOT NULL UNIQUE
        )
    ''')
    
    cursore.execute('''
        CREATE TABLE IF NOT EXISTS categorie_dpi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            prefisso TEXT,
            descrizione TEXT
        )
    ''')
    
    cursore.execute('''
        CREATE TABLE IF NOT EXISTS articoli (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codice TEXT UNIQUE NOT NULL,
            categoria_id INTEGER REFERENCES categorie_dpi(id),
            descrizione TEXT NOT NULL,
            tipo_articolo TEXT,
            taglia_id INTEGER REFERENCES taglie(id),
            quantita INTEGER DEFAULT 0,
            prezzo_unitario REAL DEFAULT 0.0,
            scorta_minima INTEGER DEFAULT 0,
            stato TEXT DEFAULT 'ATTIVO' CHECK (stato IN ('ATTIVO', 'ESAURITO', 'DISMESSO')),
            ubicazione TEXT,
            posizione TEXT,
            note TEXT,
            data_creazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursore.execute('''
        CREATE TABLE IF NOT EXISTS movimenti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_movimento TEXT NOT NULL,
            tipo TEXT CHECK (tipo IN ('CARICO', 'SCARICO')) NOT NULL,
            articolo_id INTEGER REFERENCES articoli(id),
            quantita INTEGER NOT NULL,
            dipendente_id INTEGER REFERENCES dipendenti(id),
            note TEXT
        )
    ''')
    
    commit()
    print("✅ Tabelle magazzino create!")


def conta_record(tabella):
    """Conta i record in una tabella."""
    cursore = get_cursore()
    cursore.execute(f"SELECT COUNT(*) FROM {tabella}")
    return cursore.fetchone()[0]