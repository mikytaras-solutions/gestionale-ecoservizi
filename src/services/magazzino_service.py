"""
MAGAZZINO SERVICE (VERSIONE B - CODICE LIBERO)
==============================================
Business logic per la gestione magazzino DPI.
"""

from typing import List, Optional
from datetime import datetime

from src.core.database import get_cursore, commit
from src.models.magazzino import Taglia, Categoria, Articolo, Movimentazione


# ============================================================
#                   TAGLIE
# ============================================================

def get_taglie() -> List[Taglia]:
    cursore = get_cursore()
    cursore.execute("SELECT * FROM taglie ORDER BY taglia")
    return [Taglia.from_dict(dict(row)) for row in cursore.fetchall()]


def insert_taglia(taglia: str) -> int:
    cursore = get_cursore()
    cursore.execute("INSERT INTO taglie (taglia) VALUES (?)", (taglia.upper().strip(),))
    commit()
    return cursore.lastrowid


# ============================================================
#                   CATEGORIE
# ============================================================

def get_categorie() -> List[Categoria]:
    cursore = get_cursore()
    cursore.execute("SELECT * FROM categorie_dpi ORDER BY nome")
    return [Categoria.from_dict(dict(row)) for row in cursore.fetchall()]


def insert_categoria(nome: str, prefisso: str = "", descrizione: str = "") -> int:
    cursore = get_cursore()
    cursore.execute(
        "INSERT INTO categorie_dpi (nome, prefisso, descrizione) VALUES (?, ?, ?)",
        (nome.upper().strip(), prefisso.upper().strip(), descrizione.strip())
    )
    commit()
    return cursore.lastrowid


# ============================================================
#                   ARTICOLI
# ============================================================

def get_articoli(categoria_id: Optional[int] = None) -> List[Articolo]:
    cursore = get_cursore()
    if categoria_id:
        cursore.execute("SELECT * FROM articoli WHERE categoria_id = ? ORDER BY descrizione", (categoria_id,))
    else:
        cursore.execute("SELECT * FROM articoli ORDER BY descrizione")
    return [Articolo.from_dict(dict(row)) for row in cursore.fetchall()]


def insert_articolo(art: Articolo) -> int:
    cursore = get_cursore()
    cursore.execute('''
        INSERT INTO articoli (codice, categoria_id, descrizione, tipo_articolo, taglia_id,
            quantita, prezzo_unitario, scorta_minima,
            stato, ubicazione, posizione, note)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        art.codice.upper().strip(), art.categoria_id, art.descrizione.upper().strip(),
        art.tipo_articolo.upper().strip(), art.taglia_id,
        art.quantita, art.prezzo_unitario, art.scorta_minima, art.stato,
        art.ubicazione.upper().strip(), art.posizione.upper().strip(), art.note.strip()
    ))
    commit()
    return cursore.lastrowid


def update_articolo(art: Articolo):
    cursore = get_cursore()
    cursore.execute('''
        UPDATE articoli SET codice=?, categoria_id=?, descrizione=?, tipo_articolo=?, taglia_id=?,
            quantita=?, prezzo_unitario=?, scorta_minima=?,
            stato=?, ubicazione=?, posizione=?, note=?
        WHERE id=?
    ''', (
        art.codice.upper().strip(), art.categoria_id, art.descrizione.upper().strip(),
        art.tipo_articolo.upper().strip(), art.taglia_id,
        art.quantita, art.prezzo_unitario, art.scorta_minima, art.stato,
        art.ubicazione.upper().strip(), art.posizione.upper().strip(), art.note.strip(),
        art.id
    ))
    commit()


def delete_articolo(id_valore: int):
    cursore = get_cursore()
    cursore.execute("DELETE FROM articoli WHERE id = ?", (id_valore,))
    commit()


# ============================================================
#                   MOVIMENTI
# ============================================================

def carico_articolo(articolo_id: int, quantita: int, note: str = "") -> int:
    cursore = get_cursore()
    
    cursore.execute('''
        INSERT INTO movimenti (data_movimento, tipo, articolo_id, quantita, note)
        VALUES (?, 'CARICO', ?, ?, ?)
    ''', (datetime.now().strftime('%d/%m/%Y'), articolo_id, quantita, note))
    
    cursore.execute("UPDATE articoli SET quantita = quantita + ? WHERE id = ?",
                   (quantita, articolo_id))
    commit()
    return cursore.lastrowid


def scarico_articolo(articolo_id: int, quantita: int, dipendente_id: int, note: str = "") -> int:
    cursore = get_cursore()
    
    cursore.execute('''
        INSERT INTO movimenti (data_movimento, tipo, articolo_id, quantita, dipendente_id, note)
        VALUES (?, 'SCARICO', ?, ?, ?, ?)
    ''', (datetime.now().strftime('%d/%m/%Y'), articolo_id, quantita, dipendente_id, note))
    
    cursore.execute("UPDATE articoli SET quantita = quantita - ? WHERE id = ?",
                   (quantita, articolo_id))
    commit()
    return cursore.lastrowid


def get_movimenti(limit: int = 500) -> list:
    cursore = get_cursore()
    cursore.execute('''
        SELECT m.*, 
               a.codice as articolo_cod, 
               a.descrizione as articolo_desc,
               a.tipo_articolo as tipo_articolo,
               t.taglia as taglia,
               c.nome as categoria,
               d.cognome, 
               d.nome
        FROM movimenti m
        LEFT JOIN articoli a ON m.articolo_id = a.id
        LEFT JOIN taglie t ON a.taglia_id = t.id
        LEFT JOIN categorie_dpi c ON a.categoria_id = c.id
        LEFT JOIN dipendenti d ON m.dipendente_id = d.id
        ORDER BY m.id DESC 
        LIMIT ?
    ''', (limit,))
    return [dict(row) for row in cursore.fetchall()]


def get_consegne_dipendente(dipendente_id: int) -> list:
    cursore = get_cursore()
    cursore.execute('''
        SELECT m.data_movimento, a.codice, a.descrizione, a.tipo_articolo,
               t.taglia, c.nome as categoria,
               m.quantita, a.prezzo_unitario, (m.quantita * a.prezzo_unitario) as valore
        FROM movimenti m
        JOIN articoli a ON m.articolo_id = a.id
        LEFT JOIN taglie t ON a.taglia_id = t.id
        LEFT JOIN categorie_dpi c ON a.categoria_id = c.id
        WHERE m.tipo = 'SCARICO' AND m.dipendente_id = ?
        ORDER BY m.data_movimento DESC
    ''', (dipendente_id,))
    return [dict(row) for row in cursore.fetchall()]