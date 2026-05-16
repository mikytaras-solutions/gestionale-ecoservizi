"""
PDF GENERATOR
=============
Genera report PDF per le schede dipendenti.
"""

import io
import os
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Image as RLImage, Table, TableStyle
)
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

from src.config.settings import FOTO_DIR


def genera_pdf(dipendente: dict) -> io.BytesIO:
    """Genera il PDF della scheda dipendente."""
    
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )
    
    styles = getSampleStyleSheet()
    
    stile_sezione = ParagraphStyle(
        'TitoloSezione',
        parent=styles['Heading2'],
        textColor=colors.red,
        fontSize=14,
        spaceAfter=10
    )
    
    elementi = []
    
    # Intestazione
    elementi.append(Paragraph("Scheda Anagrafica Dipendente", styles['Title']))
    elementi.append(Spacer(1, 0.5*cm))
    
    # Foto + dati principali
    path_foto = os.path.join(FOTO_DIR, str(dipendente.get("foto_nome", "")))
    
    if dipendente.get("foto_nome") and os.path.exists(path_foto):
        try:
            img = RLImage(path_foto, width=3.5*cm, height=4.5*cm)
        except:
            img = Spacer(3.5*cm, 4.5*cm)
    else:
        img = Spacer(3.5*cm, 4.5*cm)
    
    dati = [
        ["Nominativo", f"{dipendente.get('cognome', '')} {dipendente.get('nome', '')}"],
        ["Codice Fiscale", dipendente.get("codice_fiscale", "")],
        ["Data di Nascita", dipendente.get("data_nascita", "")],
        ["Luogo di Nascita", dipendente.get("luogo_nascita", "")],
        ["Mansione", dipendente.get("mansione", "")]
    ]
    
    tab_dati = Table(dati, colWidths=[4*cm, 8*cm])
    tab_dati.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.lightgrey),
    ]))
    
    tab_header = Table([[img, tab_dati]], colWidths=[4.5*cm, 12.5*cm])
    tab_header.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    
    elementi.append(tab_header)
    elementi.append(Spacer(1, 1*cm))
    
    # Residenza
    elementi.append(Paragraph("Residenza", stile_sezione))
    dati_res = [
        ["Indirizzo", dipendente.get("indirizzo_residenza", "")],
        ["Città", dipendente.get("città_residenza", "")],
        ["CAP", dipendente.get("cap_residenza", "")]
    ]
    tab_res = Table(dati_res, colWidths=[4*cm, 13*cm])
    tab_res.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.lightgrey),
    ]))
    elementi.append(tab_res)
    elementi.append(Spacer(1, 0.8*cm))
    
    # Recapiti
    elementi.append(Paragraph("Recapiti", stile_sezione))
    dati_rec = [
        ["Cellulare", dipendente.get("cellulare", "")],
        ["Email", dipendente.get("email", "")]
    ]
    tab_rec = Table(dati_rec, colWidths=[4*cm, 13*cm])
    tab_rec.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.lightgrey),
    ]))
    elementi.append(tab_rec)
    elementi.append(Spacer(1, 0.8*cm))
    
    # Contratto
    elementi.append(Paragraph("Dati Contrattuali", stile_sezione))
    dati_cont = [
        ["Data Assunzione", dipendente.get("data_assunzione", "")],
        ["Scadenza Contratto", dipendente.get("scadenza_contratto", "")]
    ]
    tab_cont = Table(dati_cont, colWidths=[4*cm, 13*cm])
    tab_cont.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.lightgrey),
    ]))
    elementi.append(tab_cont)
    elementi.append(Spacer(1, 0.8*cm))
    
    # Mezzi
    elementi.append(Paragraph("Mezzi Autorizzati", stile_sezione))
    tab_mezzi = Table(
        [["Tipo Veicolo", "Marca", "Targa"],
         [dipendente.get("mezzo", ""), "-", dipendente.get("targa", "")]],
        colWidths=[5.6*cm, 5.6*cm, 5.8*cm]
    )
    tab_mezzi.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#D3D3D3")),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    elementi.append(tab_mezzi)
    
    doc.build(elementi)
    buffer.seek(0)
    return buffer