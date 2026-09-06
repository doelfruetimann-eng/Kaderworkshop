#!/usr/bin/env python3
"""Baut die Nachtragsmail zum Netzzugang.

Eine Sammelmail an alle neun Teilnehmenden. Sie enthaelt bewusst KEINEN
persoenlichen Link und KEINE PIN — darum ist BCC hier zulaessig, anders als
bei der Einladung.

Kodierung wie bei den Einladungen: HTML-Teil plus Textteil, beide 8bit,
Betreff in reinem ASCII. Sonst zerlegt Outlook lange Zeilen an den weichen
"="-Umbruechen des quoted-printable und frisst das Zeichen dahinter.
"""
import html
import json
import pathlib
from email.message import EmailMessage

WURZEL = pathlib.Path(__file__).resolve().parent.parent
ZIEL = WURZEL / 'scratchpad' / 'einladungen'
ABSENDER = 'Doelf.Ruetimann@spitaeler-sh.ch'

ABSAETZE = [
    'Hallo zusammen',

    'Kurzer Nachtrag zu meiner Einladung von vorhin — ein Punkt fehlt darin, '
    'und ohne ihn kommt ihr nicht weiter.',

    'Die Vorbereitungsseite liegt ausserhalb des Spitalnetzes und ist im '
    'internen Netz gesperrt. Wenn ihr den Link am Arbeitsplatz anklickt, '
    'passiert schlicht nichts oder es kommt eine Sperrmeldung. Das ist kein '
    'Fehler eures Geräts.',

    ('kasten',),

    'Am einfachsten geht es ohnehin von zu Hause oder unterwegs auf dem Handy '
    'über das Mobilfunknetz — dort greift die Sperre nicht, und das Diktieren '
    'funktioniert auf dem Handy sogar besser als am Rechner.',

    'Euer persönlicher Link und eure PIN aus der ersten Mail bleiben '
    'unverändert gültig. Ihr müsst nichts neu anfordern.',

    'Entschuldigt den Nachtrag — und danke fürs Mitmachen.',

    'Herzliche Grüsse\nDölf',
]

KASTEN_TITEL = 'So kommt ihr auf die Seite'
KASTEN_ZEILEN = [
    'Im Spital: ins Patienten-WLAN wechseln. Die Anmeldung dafür holt ihr '
    'euch am Patiententerminal.',
    'Ausserhalb: ganz normal von zu Hause, oder auf dem Handy über die '
    'Mobildaten.',
]


def als_text() -> str:
    teile = []
    for a in ABSAETZE:
        if isinstance(a, tuple):
            teile.append(KASTEN_TITEL + '\n'
                         + '\n'.join('- ' + z for z in KASTEN_ZEILEN))
        else:
            teile.append(a)
    return '\n\n'.join(teile) + '\n'


def als_html() -> str:
    stuecke = []
    for a in ABSAETZE:
        if isinstance(a, tuple):
            punkte = ''.join(f'<li style="margin-bottom:6px">{html.escape(z)}</li>'
                             for z in KASTEN_ZEILEN)
            stuecke.append(
                '<div style="margin:22px 0;padding:14px 16px;border-left:4px solid #1f6feb;'
                'background:#f3f7fd">'
                f'<div style="margin-bottom:8px"><strong>{html.escape(KASTEN_TITEL)}'
                '</strong></div>'
                f'<ul style="margin:0;padding-left:20px">{punkte}</ul></div>')
        else:
            stuecke.append('<p style="margin:0 0 14px">'
                           + html.escape(a).replace('\n', '<br>') + '</p>')
    return ('<html><body style="font-family:Calibri,Arial,sans-serif;font-size:11pt;'
            'line-height:1.5;color:#111">' + ''.join(stuecke) + '</body></html>')


def main() -> None:
    config = json.loads((WURZEL / 'werkzeug' / 'kader-config.json').read_text('utf-8'))
    empfaenger = sorted({v['mail'] for v in config['tokens'].values()
                         if v.get('rolle') == 'teilnahme' and v.get('mail')})
    ZIEL.mkdir(parents=True, exist_ok=True)

    mail = EmailMessage()
    mail['Subject'] = 'Nachtrag zur Kadertagung: die Seite ist im Spitalnetz gesperrt'
    mail['From'] = ABSENDER
    mail['To'] = ABSENDER          # an sich selbst, alle uebrigen ins BCC
    mail['Bcc'] = ', '.join(empfaenger)
    mail.set_content(als_text(), charset='utf-8', cte='8bit')
    mail.add_alternative(als_html(), subtype='html', charset='utf-8', cte='8bit')

    ziel = ZIEL / 'nachtrag-netzzugang.eml'
    ziel.write_bytes(bytes(mail))
    (ZIEL / 'nachtrag-netzzugang.txt').write_text(als_text(), 'utf-8')
    print(f'Nachtrag an {len(empfaenger)} Empfänger: {ziel}')


if __name__ == '__main__':
    main()
