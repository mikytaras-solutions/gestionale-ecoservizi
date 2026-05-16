"""
SETTINGS - Configurazioni Globali
=================================
Tutte le costanti e i percorsi dell'applicazione.
"""

import os

# ============================================================
#                   PERCORSI PRINCIPALI
# ============================================================

# Directory radice del progetto (GestionaleEcoservizi)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Directory dati
DATA_DIR = os.path.join(BASE_DIR, "data")
DATABASE_DIR = os.path.join(DATA_DIR, "database")
EXCEL_DIR = os.path.join(DATA_DIR, "excel")
FOTO_DIR = os.path.join(DATA_DIR, "Foto")

# Directory assets
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")

# ============================================================
#                   DATABASE
# ============================================================

DB_NAME = os.path.join(DATABASE_DIR, "db_ecoservizi.db")

# ============================================================
#                   FILE EXCEL
# ============================================================

EXCEL_ORIGINE = os.path.join(EXCEL_DIR, "Dipendenti_3.xlsx")

# ============================================================
#                   LOGO
# ============================================================

LOGO_PATH = os.path.join(IMAGES_DIR, "LOGO_ECOSERVIZI2.png")

# ============================================================
#                   VERSIONE APP
# ============================================================

APP_NAME = "Ecoservizi Gestionale Pro"
APP_VERSION = "1.0.0"

# ============================================================
#                   OPZIONI
# ============================================================

OPZIONI_MEZZO = ["", "AUTO", "MOTO", "FURGONE", "CAMION"]

# ============================================================
#                   CREAZIONE CARTELLE
# ============================================================

def crea_cartelle():
    """Crea tutte le cartelle necessarie se non esistono."""
    cartelle = [DATA_DIR, DATABASE_DIR, EXCEL_DIR, FOTO_DIR, ASSETS_DIR, IMAGES_DIR]
    for cartella in cartelle:
        os.makedirs(cartella, exist_ok=True)