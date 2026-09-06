#!/usr/bin/env python3
"""Erzeugt aus der Werkbank eine Verteilfassung ohne Personendaten.

Die Leitungsfassung (index.html) enthält Mailadressen und die Einladungs-
funktion. Diese Fassung ist für die Weitergabe gedacht: gleiche Funktion,
aber keine Kontaktdaten und kein Versand. Damit kann sie ohne Bedenken in
eine Ablage gelegt oder verschickt werden.
"""
import re, pathlib, sys

quelle = pathlib.Path(__file__).parent.parent / "index.html"
ziel   = pathlib.Path(__file__).parent.parent / "werkbank-verteilfassung.html"
h = quelle.read_text(encoding="utf-8")

# 1. Mailadressen aus den Stammdaten entfernen
h, n_mail = re.subn(r',\s*m:"[^"]*@[^"]*"', '', h)

# 2. Einladungsversand ganz ausbauen — ohne Adressen ergibt er keinen Sinn
h, n_vers = re.subn(r'\s*<section class="card panel">\s*<div class="a-kopf">\s*<h3>Einladung versenden</h3>.*?</section>\n',
                    '\n', h, count=1, flags=re.S)
assert n_vers == 1, "Versandbereich nicht gefunden"

# 3. Mailspalte der Teilnehmendenliste entfernen
h = h.replace('<th style="min-width:210px">E-Mail</th>', '', 1)
h = re.sub(r'\s*<td><input type="text" data-tn="\$\{t\.id\}" data-k="mail".*?</td>\n',
           '\n', h, count=1, flags=re.S)

# 3b. Spalten «Persönlicher Link» und «PIN» entfernen — beides gehört
#     nicht in die Verteilfassung
h, n_lth = re.subn(r'\s*<th[^>]*>Persönlicher Link</th>', '', h, count=1)
assert n_lth == 1, "Spaltenkopf «Persönlicher Link» nicht gefunden"
h, n_ltd = re.subn(r'\s*<td><input type="text" data-tn="\$\{t\.id\}" data-k="link".*?</td>\n',
                   '\n', h, count=1, flags=re.S)
assert n_ltd == 1, "Spalte mit data-k=\"link\" nicht gefunden"
h, n_pth = re.subn(r'\s*<th[^>]*>PIN</th>', '', h, count=1)
assert n_pth == 1, "Spaltenkopf «PIN» nicht gefunden"
h, n_ptd = re.subn(r'\s*<td><input type="text" data-tn="\$\{t\.id\}" data-k="pin".*?</td>\n',
                   '\n', h, count=1, flags=re.S)
assert n_ptd == 1, "Spalte mit data-k=\"pin\" nicht gefunden"

# 4. Kennzeichnung im Kopf
h = h.replace('<span class="ort">16:00 bis 22:00 Uhr</span>',
              '<span class="ort">Verteilfassung ohne Kontaktdaten</span>', 1)

ziel.write_text(h, encoding="utf-8")
rest = len(re.findall(r'[\w.]+@spitaeler-sh\.ch', h))
print(f"{ziel.name} erzeugt · {n_mail} Adressen entfernt · verbleibend: {rest}")
if rest:
    sys.exit("FEHLER: es sind noch Adressen enthalten")
