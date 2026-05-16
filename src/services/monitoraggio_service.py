"""
MONITORAGGIO SERVICE
====================
Servizio per il monitoraggio e la diagnostica del sistema.
"""

from datetime import datetime
import os
from src.core.database import get_cursore, commit
from src.config.settings import DB_NAME, DATABASE_DIR


# ============================================================
#                   STATISTICHE GENERALI
# ============================================================

def get_statistiche_sistema():
    """Restituisce statistiche generali del sistema."""
    cursore = get_cursore()
    
    stats = {}
    
    # Totale dipendenti
    cursore.execute("SELECT COUNT(*) FROM dipendenti")
    stats['dipendenti'] = cursore.fetchone()[0]
    
    # Totale articoli
    cursore.execute("SELECT COUNT(*) FROM articoli")
    stats['articoli'] = cursore.fetchone()[0]
    
    # Totale categorie
    cursore.execute("SELECT COUNT(*) FROM categorie_dpi")
    stats['categorie'] = cursore.fetchone()[0]
    
    # Totale movimenti
    cursore.execute("SELECT COUNT(*) FROM movimenti")
    stats['movimenti_totali'] = cursore.fetchone()[0]
    
    # Movimenti oggi
    oggi = datetime.now().strftime('%d/%m/%Y')
    cursore.execute("SELECT COUNT(*) FROM movimenti WHERE data_movimento = ?", (oggi,))
    stats['movimenti_oggi'] = cursore.fetchone()[0]
    
    # Valore magazzino
    cursore.execute("SELECT SUM(quantita * prezzo_unitario) FROM articoli")
    risultato = cursore.fetchone()[0]
    stats['valore_magazzino'] = risultato if risultato else 0
    
    # Dimensione database
    if os.path.exists(DB_NAME):
        stats['dimensione_db'] = os.path.getsize(DB_NAME) / 1024
    else:
        stats['dimensione_db'] = 0
    
    return stats


# ============================================================
#                   LOG OPERAZIONI
# ============================================================

def log_operazione(tipo: str, descrizione: str, utente: str = "admin"):
    """Registra un'operazione nel log di sistema."""
    cursore = get_cursore()
    
    cursore.execute('''
        CREATE TABLE IF NOT EXISTS log_sistema (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_ora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            tipo TEXT,
            descrizione TEXT,
            utente TEXT
        )
    ''')
    
    cursore.execute('''
        INSERT INTO log_sistema (tipo, descrizione, utente)
        VALUES (?, ?, ?)
    ''', (tipo, descrizione, utente))
    
    commit()


def get_log(limit: int = 100):
    """Recupera gli ultimi log."""
    cursore = get_cursore()
    cursore.execute("SELECT * FROM log_sistema ORDER BY id DESC LIMIT ?", (limit,))
    return [dict(row) for row in cursore.fetchall()]


# ============================================================
#                   BACKUP
# ============================================================

def crea_backup():
    """Crea un backup del database."""
    import shutil
    
    if not os.path.exists(DB_NAME):
        return None
    
    data = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome_backup = f"backup_{data}.db"
    percorso_backup = os.path.join(DATABASE_DIR, nome_backup)
    
    shutil.copy2(DB_NAME, percorso_backup)
    
    log_operazione("BACKUP", f"Backup creato: {nome_backup}")
    
    return nome_backup


def elenca_backup():
    """Elenca tutti i backup disponibili."""
    backups = []
    if os.path.exists(DATABASE_DIR):
        for f in os.listdir(DATABASE_DIR):
            if f.startswith("backup_") and f.endswith(".db"):
                percorso = os.path.join(DATABASE_DIR, f)
                dimensione = os.path.getsize(percorso) / 1024
                data_file = datetime.fromtimestamp(os.path.getmtime(percorso))
                backups.append({
                    'nome': f,
                    'dimensione_kb': round(dimensione, 1),
                    'data': data_file.strftime('%d/%m/%Y %H:%M')
                })
    return sorted(backups, key=lambda x: x['nome'], reverse=True)


def ripristina_backup(nome_backup: str):
    """Ripristina il database da un backup."""
    percorso_backup = os.path.join(DATABASE_DIR, nome_backup)
    
    if not os.path.exists(percorso_backup):
        return False
    
    import shutil
    shutil.copy2(percorso_backup, DB_NAME)
    
    log_operazione("RIPRISTINO", f"Database ripristinato da: {nome_backup}")
    
    return True