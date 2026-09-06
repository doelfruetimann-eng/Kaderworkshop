"""Die Budgetzahlen fuers Abendessen — eine Quelle fuer alle Mails.

Herkunft: docs/abendessen-ziegelhuette.md. Wird die Auswahl dort geaendert,
gehoeren die Zahlen hier nachgezogen.
"""

POSTEN = [
    ('Schüsselsalat für alle', '10 × 8.30', 'CHF 83.–'),
    ('Hauptgang', '10 × Ø 35.–', 'CHF 290.– bis 400.–'),
    ('Getränke, Kaffee', '10 × 20.– bis 25.–', 'CHF 200.– bis 250.–'),
    ('Raummiete', 'entfällt, wir essen im Haus', 'CHF 0.–'),
]
SUMME = 'rund CHF 650.– bis 750.–'
MIT_DESSERT = 'gegen CHF 800.–'


def tabelle_text() -> str:
    breite = max(len(p[0]) for p in POSTEN)
    zeilen = [f'{p[0]:<{breite}}  {p[2]}' for p in POSTEN]
    zeilen.append(f'{"Zusammen":<{breite}}  {SUMME}')
    return '\n'.join(zeilen)


def tabelle_html() -> str:
    import html
    zeilen = ''.join(
        '<tr>'
        f'<td style="padding:5px 14px 5px 0">{html.escape(p[0])}</td>'
        f'<td style="padding:5px 14px 5px 0;color:#555">{html.escape(p[1])}</td>'
        f'<td style="padding:5px 0;white-space:nowrap">{html.escape(p[2])}</td>'
        '</tr>' for p in POSTEN)
    return ('<table style="margin:18px 0;border-collapse:collapse;font-size:11pt">'
            + zeilen +
            '<tr><td colspan="2" style="padding:8px 14px 0 0;border-top:1px solid #ccc">'
            '<strong>Zusammen</strong></td>'
            '<td style="padding:8px 0 0;border-top:1px solid #ccc;white-space:nowrap">'
            f'<strong>{html.escape(SUMME)}</strong></td></tr></table>')
