#!/usr/bin/env python3
"""Baut die Standmeldung an die Leitung (Fabienne, Melina, Markus).

Alle Zahlen kommen live aus der stand-Route, keine von Hand gepflegte
Fassung — eine Standmeldung mit veralteten Zahlen ist schlimmer als keine.

Die Mail enthaelt bewusst KEINEN Leitungsschluessel: Den haben die drei
aus ihrer Dashboard-Mail. Auch keine Inhalte der Abgaben — die stehen im
Dashboard, das ist der geschuetzte Ort dafuer.

Kodierung wie bei den uebrigen Mails: HTML-Teil plus Textteil, beide 8bit,
Betreff in reinem ASCII.
"""
import argparse
import collections
import datetime
import html
import json
import pathlib
import subprocess
from email.message import EmailMessage

WURZEL = pathlib.Path(__file__).resolve().parent.parent
ZIEL = WURZEL / 'scratchpad' / 'einladungen'
DASHBOARD = 'https://umfrage.win/kadertagung/dashboard'
ABSENDER = 'Doelf.Ruetimann@spitaeler-sh.ch'
FRIST = datetime.date(2026, 9, 7)
TAGUNG = '14. September'

MENUE_NAME = {
    'cordonbleu': 'Cordon bleu', 'wienerschnitzel': 'Wienerschnitzel',
    'zuercher': 'Zürcher Geschnetzeltes', 'vegetarisch': 'vegetarisch',
    'vegan': 'vegan', 'keins': 'kein Hauptgang',
}


def stand(config: dict) -> dict:
    schluessel = next(t for t, v in config['tokens'].items()
                      if v.get('rolle') == 'leitung' and v['name'].startswith('Dölf'))
    roh = subprocess.run(
        ['curl', '-s', '--max-time', '30', '-X', 'POST',
         'https://umfrage.win/api/kadertagung/stand',
         '-H', 'content-type: application/json',
         '-d', json.dumps({'token': schluessel})],
        capture_output=True, text=True).stdout
    d = json.loads(roh)
    if not d.get('ok'):
        raise SystemExit('stand-Route hat nicht geantwortet — Mail nicht gebaut')
    return d


def absaetze(d: dict, muster: list) -> list:
    personen = d['personen']
    da = [p for p in personen if p['abgegeben']]
    offen = [p['name'] for p in personen if not p['abgegeben']]
    themen = sum(len(a.get('painpoints') or []) for a in d.get('abgaben', []))
    tage = (FRIST - datetime.date.today()).days
    menue = collections.Counter(p['menue'] for p in da if p.get('menue'))
    menue_text = ', '.join(f'{n}× {MENUE_NAME.get(k, k)}'
                           for k, n in menue.most_common())

    frist_satz = (f'noch {tage} Tage' if tage > 1 else
                  'morgen' if tage == 1 else
                  'heute' if tage == 0 else 'abgelaufen')

    teile = [
        'Hallo zusammen',

        f'Kurz zum Stand der Vorbereitung auf die Kadertagung vom {TAGUNG}. '
        f'Die Frist läuft am Montag, 7. September ab — {frist_satz}.',

        ('zahlen', [
            (f'{len(da)} von {len(personen)}', 'Personen haben abgegeben'),
            (str(themen), 'Themen sind eingegangen'),
            (f'{len({a["einheit"] for a in d.get("abgaben", [])})} von 9',
             'Organisationseinheiten sind vertreten'),
        ]),

        ('link',),

        'Dort seht ihr alle Themen im Volltext, nach Einheit geordnet, dazu '
        'die Auswertung der Standortbestimmung und das Stimmungsbild. Euren '
        'Leitungsschlüssel habt ihr aus meiner früheren Mail; die Seite fragt '
        'ihn beim Öffnen ab.',
    ]

    if muster:
        teile.append('Was sich inhaltlich bereits abzeichnet:')
        teile.append(('muster', muster))

    if offen:
        teile.append(
            'Offen sind noch: ' + ', '.join(offen) + '. Eine Erinnerung ist '
            'raus. Bis zur Frist zählt der letzte Stand, es kann also noch '
            'einiges dazukommen.')

    if menue_text:
        teile.append(f'Fürs Abendessen sind bisher gewählt: {menue_text}. '
                     f'Die Bestellung geht erst nach der Frist an die Küche.')

    teile += [
        'Wenn euch beim Durchsehen etwas auffällt, das wir für den Abend '
        'anders aufziehen sollten, sagt es mir rechtzeitig — die Werkbank '
        'für die Bewertung stelle ich in den Tagen nach der Frist zusammen.',

        'Herzliche Grüsse\nDölf',
    ]
    return teile


def als_text(teile: list) -> str:
    raus = []
    for a in teile:
        if isinstance(a, tuple) and a[0] == 'zahlen':
            raus.append('\n'.join(f'{w}  {t}' for w, t in a[1]))
        elif isinstance(a, tuple) and a[0] == 'link':
            raus.append(f'Dashboard: {DASHBOARD}')
        elif isinstance(a, tuple) and a[0] == 'muster':
            raus.append('\n'.join('- ' + z for z in a[1]))
        else:
            raus.append(a)
    return '\n\n'.join(raus) + '\n'


def als_html(teile: list) -> str:
    raus = []
    for a in teile:
        if isinstance(a, tuple) and a[0] == 'zahlen':
            zellen = ''.join(
                '<td style="padding:0 26px 0 0;vertical-align:top">'
                f'<div style="font-size:19pt;font-weight:600;color:#1f6feb">'
                f'{html.escape(w)}</div>'
                f'<div style="font-size:10pt;color:#444">{html.escape(t)}</div></td>'
                for w, t in a[1])
            raus.append('<table style="margin:20px 0;border-collapse:collapse">'
                        f'<tr>{zellen}</tr></table>')
        elif isinstance(a, tuple) and a[0] == 'link':
            raus.append(
                '<div style="margin:20px 0;padding:14px 16px;'
                'border-left:4px solid #1f6feb;background:#f3f7fd">'
                '<div style="margin-bottom:6px"><strong>Dashboard</strong></div>'
                f'<a href="{DASHBOARD}">{DASHBOARD}</a></div>')
        elif isinstance(a, tuple) and a[0] == 'muster':
            punkte = ''.join(f'<li style="margin-bottom:6px">{html.escape(z)}</li>'
                             for z in a[1])
            raus.append(f'<ul style="margin:0 0 14px;padding-left:20px">{punkte}</ul>')
        else:
            raus.append('<p style="margin:0 0 14px">'
                        + html.escape(a).replace('\n', '<br>') + '</p>')
    return ('<html><body style="font-family:Calibri,Arial,sans-serif;font-size:11pt;'
            'line-height:1.5;color:#111">' + ''.join(raus) + '</body></html>')


MUSTER = [
    'Matrix 42 taucht bei drei Personen unabhängig voneinander auf — als '
    'Ticketing, als Mängelmeldung und als Investitionsantrag. Das ist bisher '
    'der deutlichste gemeinsame Nenner.',
    'Manueller Abgleich von Dokumenten gegen Bestellungen zieht sich durch '
    'Einkauf, Medizintechnik und ERP: Auftragsbestätigungen, Lieferscheine, '
    'Serviceberichte.',
    'Mehrfach genannt wird ausserdem, dass Meldungen zwar abgesetzt werden, '
    'die Meldenden danach aber nicht sehen, was daraus geworden ist.',
]


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--melina', default='', help='Mailadresse von Melina')
    p.add_argument('--ohne-muster', action='store_true',
                   help='den Abschnitt mit den inhaltlichen Mustern weglassen')
    a = p.parse_args()

    config = json.loads((WURZEL / 'werkzeug' / 'kader-config.json').read_text('utf-8'))
    d = stand(config)
    teile = absaetze(d, [] if a.ohne_muster else MUSTER)

    an = ['vorname.name@spitaeler-sh.ch', 'vorname.name@spitaeler-sh.ch']
    if a.melina:
        an.append(a.melina)

    mail = EmailMessage()
    mail['Subject'] = 'Kadertagung: Stand der Vorbereitung'
    mail['From'] = ABSENDER
    mail['To'] = ', '.join(an)
    mail.set_content(als_text(teile), charset='utf-8', cte='8bit')
    mail.add_alternative(als_html(teile), subtype='html', charset='utf-8', cte='8bit')

    ZIEL.mkdir(parents=True, exist_ok=True)
    ziel = ZIEL / 'standmeldung-leitung.eml'
    ziel.write_bytes(bytes(mail))
    (ZIEL / 'standmeldung-leitung.txt').write_text(als_text(teile), 'utf-8')
    print('An:', ', '.join(an))
    if not a.melina:
        print('  ! Melinas Adresse fehlt — in Outlook ergänzen (oder --melina)')
    print(ziel)


if __name__ == '__main__':
    main()
