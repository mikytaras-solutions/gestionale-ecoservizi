"""
DIPENDENTI SERVICE
==================
Business logic per la gestione dipendenti.
"""

import pandas as pd
import os
from typing import List, Optional

from src.core.database import get_cursore, commit, conta_record
from src.models.dipendente import Dipendente
from src.core.validators import normalizza_data
from src.config.settings import EXCEL_ORIGINE, FOTO_DIR


# ============================================================
#                   CRUD OPERATIONS
# ============================================================

def get_all() -> List[Dipendente]:
    """Recupera tutti i dipendenti."""
    cursore = get_cursore()
    cursore.execute("SELECT * FROM dipendenti ORDER BY cognome, nome")
    return [Dipendente.from_dict(dict(row)) for row in cursore.fetchall()]


def search(query: str) -> List[Dipendente]:
    """Cerca dipendenti per cognome o nome."""
    cursore = get_cursore()
    cursore.execute(
        "SELECT * FROM dipendenti WHERE cognome LIKE ? OR nome LIKE ? ORDER BY cognome, nome",
        (f"%{query}%", f"%{query}%")
    )
    return [Dipendente.from_dict(dict(row)) for row in cursore.fetchall()]


def insert(dip: Dipendente) -> int:
    """Inserisce un nuovo dipendente."""
    cursore = get_cursore()
    cursore.execute('''
        INSERT INTO dipendenti (
            cognome, nome, codice_fiscale, data_nascita,
            luogo_nascita, indirizzo_residenza, città_residenza,
            cap_residenza, mansione, cellulare, email,
            data_assunzione, scadenza_contratto, mezzo, targa,
            foto_nome, documento_nome
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', dip.to_tuple_db())
    commit()
    return cursore.lastrowid


def update(dip: Dipendente):
    """Aggiorna un dipendente esistente."""
    cursore = get_cursore()
    cursore.execute('''
        UPDATE dipendenti 
        SET cognome=?, nome=?, codice_fiscale=?, 
            data_nascita=?, luogo_nascita=?, 
            indirizzo_residenza=?, città_residenza=?, 
            cap_residenza=?, mansione=?, cellulare=?, 
            email=?, data_assunzione=?, 
            scadenza_contratto=?, mezzo=?, targa=?, 
            foto_nome=?, documento_nome=?,
            data_modifica=CURRENT_TIMESTAMP
        WHERE id=?
    ''', (*dip.to_tuple_db(), dip.id))
    commit()


def delete(id_valore: int):
    """Elimina un dipendente e la sua foto."""
    cursore = get_cursore()
    cursore.execute("SELECT foto_nome FROM dipendenti WHERE id = ?", (id_valore,))
    row = cursore.fetchone()
    if row and row['foto_nome']:
        path = os.path.join(FOTO_DIR, row['foto_nome'])
        if os.path.exists(path):
            os.remove(path)
    
    cursore.execute("DELETE FROM dipendenti WHERE id = ?", (id_valore,))
    commit()


def count() -> int:
    """Conta i dipendenti."""
    return conta_record("dipendenti")


# ============================================================
#                   IMPORT EXCEL
# ============================================================

def import_from_excel() -> int:
    """Importa dipendenti dal file Excel."""
    
    print("\n🔍 DEBUG IMPORT:")
    print(f"   File: {EXCEL_ORIGINE}")
    print(f"   Esiste: {os.path.exists(EXCEL_ORIGINE)}")
    
    if not os.path.exists(EXCEL_ORIGINE):
        print("   ❌ File non trovato!")
        return 0
    
    try:
        df = pd.read_excel(EXCEL_ORIGINE)
        df = df.fillna("")
        
        print(f"   ✅ Lette {len(df)} righe")
        
        if 'codcefiscale' not in df.columns:
            print("   ❌ Colonna 'codcefiscale' non trovata!")
            return 0
        
        df = df[df['codcefiscale'].astype(str).str.strip() != '']
        print(f"   Righe con CF: {len(df)}")
        
        mappatura = {
            'cognome': 'cognome',
            'nome': 'nome',
            'codcefiscale': 'codice_fiscale',
            'data_di_nascita': 'data_nascita',
            'luogo_di_nascita': 'luogo_nascita',
            'indirizzo': 'indirizzo_residenza',
            'città': 'citta_residenza',
            'cap': 'cap_residenza',
            'mansione': 'mansione',
            'cellulare': 'cellulare',
            'mail': 'email',
            'data_assunzione': 'data_assunzione',
            'mezzo': 'mezzo',
            'targa': 'targa',
            'percorsoimmagine': 'foto_nome',
            'ruolo': 'scadenza_contratto'
        }
        
        contatore = 0
        for _, row in df.iterrows():
            try:
                dati = {}
                for col_excel, col_db in mappatura.items():
                    if col_excel in row:
                        valore = str(row[col_excel]).strip()
                        
                        if 'data' in col_excel:
                            valore = normalizza_data(valore)
                        elif col_db in ['cognome', 'nome', 'codice_fiscale',
                                       'luogo_nascita', 'citta_residenza',
                                       'mansione', 'mezzo', 'targa']:
                            valore = valore.upper()
                        elif col_db == 'email':
                            valore = valore.lower()
                        elif col_db == 'cellulare' and valore.endswith('.0'):
                            valore = valore[:-2]
                        
                        dati[col_db] = valore
                
                dip = Dipendente.from_form(dati)
                
                if dip.codice_fiscale:
                    insert(dip)
                    contatore += 1
                        
            except Exception as e:
                print(f"   ⚠️ Errore riga: {e}")
        
        print(f"   🎉 TOTALE IMPORTATI: {contatore}")
        return contatore
        
    except Exception as e:
        print(f"   ❌ Errore: {e}")
        return 0


# ============================================================
#                   ESPORTAZIONE
# ============================================================

def export_to_dataframe() -> pd.DataFrame:
    """Esporta tutti i dipendenti in DataFrame."""
    cursore = get_cursore()
    return pd.read_sql("SELECT * FROM dipendenti ORDER BY cognome, nome", cursore.connection)


# ============================================================
#                   GESTIONE FOTO
# ============================================================

def salva_foto(id_dip: int, file_bytes: bytes, cognome: str, nome: str) -> str:
    """Salva una foto e restituisce il nome del file."""
    import time
    nome_file = f"{id_dip}_{cognome}_{nome}_{time.strftime('%Y%m%d%H%M%S')}.jpg"
    nome_file = nome_file.replace(" ", "_").lower()
    
    with open(os.path.join(FOTO_DIR, nome_file), "wb") as f:
        f.write(file_bytes)
    
    return nome_file


def verifica_foto(nome_file: str) -> bool:
    """Verifica se una foto esiste."""
    if not nome_file:
        return False
    return os.path.exists(os.path.join(FOTO_DIR, nome_file))


def get_percorso_foto(nome_file: str) -> str:
    """Restituisce il percorso completo della foto."""
    return os.path.join(FOTO_DIR, nome_file)