"""
MODELLO DIPENDENTE
==================
Classe che rappresenta un dipendente.
"""

from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Dipendente:
    """Rappresenta un dipendente aziendale."""
    
    cognome: str
    nome: str
    codice_fiscale: str
    
    id: Optional[int] = None
    data_nascita: str = ""
    luogo_nascita: str = ""
    indirizzo_residenza: str = ""
    citta_residenza: str = ""
    cap_residenza: str = ""
    mansione: str = ""
    cellulare: str = ""
    email: str = ""
    data_assunzione: str = ""
    scadenza_contratto: str = ""
    mezzo: str = ""
    targa: str = ""
    foto_nome: str = ""
    documento_nome: str = ""
    data_creazione: Optional[str] = None
    data_modifica: Optional[str] = None
    
    @property
    def nome_completo(self) -> str:
        return f"{self.cognome} {self.nome}"
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    def to_tuple_db(self) -> tuple:
        return (
            self.cognome, self.nome, self.codice_fiscale,
            self.data_nascita, self.luogo_nascita,
            self.indirizzo_residenza, self.citta_residenza, self.cap_residenza,
            self.mansione, self.cellulare, self.email,
            self.data_assunzione, self.scadenza_contratto,
            self.mezzo, self.targa, self.foto_nome, self.documento_nome
        )
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Dipendente':
        return cls(
            id=data.get('id'),
            cognome=data.get('cognome', ''),
            nome=data.get('nome', ''),
            codice_fiscale=data.get('codice_fiscale', ''),
            data_nascita=data.get('data_nascita', ''),
            luogo_nascita=data.get('luogo_nascita', ''),
            indirizzo_residenza=data.get('indirizzo_residenza', ''),
            citta_residenza=data.get('città_residenza', ''),
            cap_residenza=data.get('cap_residenza', ''),
            mansione=data.get('mansione', ''),
            cellulare=data.get('cellulare', ''),
            email=data.get('email', ''),
            data_assunzione=data.get('data_assunzione', ''),
            scadenza_contratto=data.get('scadenza_contratto', ''),
            mezzo=data.get('mezzo', ''),
            targa=data.get('targa', ''),
            foto_nome=data.get('foto_nome', ''),
            documento_nome=data.get('documento_nome', '')
        )
    
    @classmethod
    def from_form(cls, form_data: dict) -> 'Dipendente':
        return cls(
            cognome=form_data.get('cognome', '').upper().strip(),
            nome=form_data.get('nome', '').upper().strip(),
            codice_fiscale=form_data.get('codice_fiscale', '').upper().strip(),
            data_nascita=form_data.get('data_nascita', '').strip(),
            luogo_nascita=form_data.get('luogo_nascita', '').upper().strip(),
            indirizzo_residenza=form_data.get('indirizzo_residenza', '').upper().strip(),
            citta_residenza=form_data.get('citta_residenza', '').upper().strip(),
            cap_residenza=form_data.get('cap_residenza', '').strip(),
            mansione=form_data.get('mansione', '').upper().strip(),
            cellulare=form_data.get('cellulare', '').strip(),
            email=form_data.get('email', '').lower().strip(),
            data_assunzione=form_data.get('data_assunzione', '').strip(),
            scadenza_contratto=form_data.get('scadenza_contratto', '').strip(),
            mezzo=form_data.get('mezzo', '').upper().strip(),
            targa=form_data.get('targa', '').upper().strip(),
            foto_nome=form_data.get('foto_nome', '').strip(),
            documento_nome=form_data.get('documento_nome', '').strip()
        )