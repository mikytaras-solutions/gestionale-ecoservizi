"""
VALIDATORS
==========
Funzioni di validazione dati.
"""

import re
from datetime import datetime


def valida_codice_fiscale(cf):
    """Valida il formato del codice fiscale italiano."""
    if not cf:
        return False
    pattern = r'^[A-Z]{6}[0-9]{2}[A-Z][0-9]{2}[A-Z][0-9]{3}[A-Z]$'
    return bool(re.match(pattern, cf.upper()))


def valida_email(email):
    """Valida il formato email."""
    if not email:
        return True
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def valida_data(data_str):
    """Valida il formato data GG/MM/AAAA."""
    if not data_str:
        return True
    try:
        datetime.strptime(data_str, '%d/%m/%Y')
        return True
    except ValueError:
        return False


def normalizza_data(data_str):
    """Converte una data in formato GG/MM/AAAA."""
    if not data_str:
        return ""
    try:
        import pandas as pd
        data = pd.to_datetime(data_str, errors='coerce')
        if pd.notnull(data):
            return data.strftime('%d/%m/%Y')
    except:
        pass
    return str(data_str)