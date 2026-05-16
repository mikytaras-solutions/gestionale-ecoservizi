"""
MODELLI MAGAZZINO
=================
Classi per la gestione del magazzino DPI.
"""

from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Taglia:
    """Taglia DPI (es. 40, 41, 42, M, L, XL, UNI)."""
    taglia: str
    id: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Taglia':
        return cls(
            id=data.get('id'),
            taglia=data.get('taglia', '')
        )
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Categoria:
    """Categoria DPI (es. Scarpe, Guanti, Caschi)."""
    nome: str
    id: Optional[int] = None
    prefisso: str = ""
    descrizione: str = ""
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Categoria':
        return cls(
            id=data.get('id'),
            nome=data.get('nome', ''),
            prefisso=data.get('prefisso', ''),
            descrizione=data.get('descrizione', '')
        )
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Articolo:
    """Articolo DPI in magazzino."""
    codice: str
    descrizione: str
    categoria_id: int
    tipo_articolo: str = ""
    taglia_id: Optional[int] = None
    quantita: int = 0
    prezzo_unitario: float = 0.0
    scorta_minima: int = 0
    stato: str = "ATTIVO"
    ubicazione: str = ""
    posizione: str = ""
    note: str = ""
    id: Optional[int] = None
    
    @property
    def valore_totale(self) -> float:
        return self.quantita * self.prezzo_unitario
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Articolo':
        return cls(
            id=data.get('id'),
            codice=data.get('codice', ''),
            descrizione=data.get('descrizione', ''),
            categoria_id=data.get('categoria_id'),
            tipo_articolo=data.get('tipo_articolo', ''),
            taglia_id=data.get('taglia_id'),
            quantita=data.get('quantita', 0),
            prezzo_unitario=data.get('prezzo_unitario', 0.0),
            scorta_minima=data.get('scorta_minima', 0),
            stato=data.get('stato', 'ATTIVO'),
            ubicazione=data.get('ubicazione', ''),
            posizione=data.get('posizione', ''),
            note=data.get('note', '')
        )
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Movimentazione:
    """Movimento di carico/scarico."""
    data_movimento: str
    tipo: str
    articolo_id: int
    quantita: int
    dipendente_id: Optional[int] = None
    note: str = ""
    id: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Movimentazione':
        return cls(
            id=data.get('id'),
            data_movimento=data.get('data_movimento', ''),
            tipo=data.get('tipo', ''),
            articolo_id=data.get('articolo_id'),
            quantita=data.get('quantita', 0),
            dipendente_id=data.get('dipendente_id'),
            note=data.get('note', '')
        )
    
    def to_dict(self) -> dict:
        return asdict(self)