#!/usr/bin/env python3
"""Baut die neun persoenlichen Einladungen als .eml.

Wichtig zur Kodierung: Die Mail geht als HTML-Teil mit einem einfachen
Text-Teil daneben, beide mit Content-Transfer-Encoding 8bit. Frueher lief
der Text ueber quoted-printable — dort setzt der Absender bei langen Zeilen
ein "=" als weiches Zeilenende, und Outlook frisst beim Entfernen der
"zusaetzlichen Zeilenumbrueche" das Zeichen dahinter. So wurde aus
"Finanzbereichs" ein "Finanzberei=hs". Mit 8bit und HTML passiert das nicht.

Quelle fuer Namen, Einheiten, Adressen, Tokens und PINs ist
werkzeug/kader-config.json — Ausgabe bleibt im Scratchpad, nie ins Repo.
"""
import html
import json
import pathlib
from email.message import EmailMessage

WURZEL = pathlib.Path(__file__).resolve().parent.parent
ZIEL = WURZEL / 'scratchpad' / 'einladungen'
BASIS = 'https://umfrage.win/kadertagung/'
ABSENDER = 'Doelf.Ruetimann@spitaeler-sh.ch'

TAGUNG = 'Montag, 14. September 2026'
ZEIT = '16:00 bis 22:00 Uhr'
ORT = 'Gasthof Ziegelhütte'
FRIST = 'Montag, 7. September 2026'
MELINA = 'Melina Lopez Garcia'

# Je Person ein konkreter Aufhaenger aus ihrem eigenen Bereich. Das ist der
# Unterschied zwischen einer Serienmail und einer, die gelesen wird. Bewusst
# als Vermutung formuliert — sie wissen besser, wo es klemmt.
AUFHAENGER = {
    'Fabienne Grant':
        'Ich denke an Rückweisungen und Nachfragen von Kostenträgern oder an '
        'das Zusammensuchen von Belegen für einen einzelnen Fall.',
    'Sevil Erdogan':
        'Ich denke an den Monatsabschluss: Zahlen aus mehreren Quellen '
        'zusammentragen und Abweichungen kommentieren, die im Kern jeden '
        'Monat dieselben sind.',
    'Daniela Graf':
        'Ich denke an Nachfragen zur Dokumentation und an das Suchen in '
        'Berichten nach der einen Angabe, die für die Codierung noch fehlt.',
    'Yannick Steiner':
        'Ich denke an Auswertungen auf Zuruf, an Stammdaten, die an zwei '
        'Orten gepflegt werden, und an Schnittstellen, die man von Hand '
        'nachkontrollieren muss.',
    'Raphael Kuhn':
        'Ich denke an das Abgleichen von Bestellung, Lieferschein und '
        'Rechnung, wenn drei Zahlen nicht zusammenpassen.',
    'Dölf Rütimann':
        'Ich denke an Störungsmeldungen, Unterhaltsnachweise und Verträge, '
        'die man jedes Mal neu zusammensucht.',
    'Markus Hausmann-Spiess':
        'Ich denke an Tickets, die immer wieder dasselbe fragen, und an '
        'Dokumentation, die es längst gibt — nur findet sie niemand.',
    'Brian Sailer':
        'Ich denke an Wartungsnachweise, Gerätedossiers und Prüfprotokolle, '
        'die für eine Kontrolle zusammengetragen werden müssen.',
    'Jürg Rahm':
        'Ich denke an die Budgetrunde, an Führungskennzahlen aus mehreren '
        'Systemen und an Anfragen von aussen, die immer eilen.',
}


def absaetze(vorname: str, name: str) -> list:
    """Der Mailtext als Liste von Absaetzen.

    Ein Absatz ist entweder Text oder ('zugang', link, pin) fuer den
    hervorgehobenen Kasten.
    """
    return [
        f'Hallo {vorname}',

        f'Am {TAGUNG} treffen wir uns zur Kadertagung des Finanzbereichs, '
        f'{ZEIT} im {ORT}. Thema ist künstliche Intelligenz — aber nicht als '
        f'Vortrag, sondern anhand unserer eigenen Arbeit. Begleitet werden wir '
        f'von {MELINA}, unserer Chief AI Officer.',

        'Damit der Abend etwas bringt, brauche ich vorher von dir zwei bis drei '
        'konkrete Pain Points: Abläufe aus deinem Alltag, die Zeit fressen, '
        'immer wiederkehren, oft schiefgehen oder die schlicht niemand gerne '
        'macht. Eine Lösung musst du nicht mitbringen — das Problem genügt.',

        AUFHAENGER.get(name, '') + ' Du weisst besser als ich, wo es bei dir '
        'wirklich klemmt.',

        ('zugang',),

        'Wie es abläuft: Die Seite führt dich Schritt für Schritt. Du erzählst '
        'einfach, was dich aufhält — tippen oder diktieren —, und die KI fragt '
        'nach, wo etwas noch unklar ist. Daraus entsteht dein Beitrag. '
        'Tippfehler sind egal: Am Schluss räumt die KI den Text auf, bevor du '
        'ihn freigibst.',

        'Nimm dir eine gute halbe Stunde Zeit: etwa drei Minuten für ein paar '
        'Fragen zu dir und KI, danach rund zehn Minuten je Thema. Du musst das '
        'nicht am Stück machen — mit demselben Link kommst du jederzeit dorthin '
        'zurück, wo du aufgehört hast, auch vom Handy aus. Das Diktieren geht '
        'dort sogar besser als am Rechner.',

        'Ein kurzes Video auf der Startseite zeigt den Ablauf, falls du lieber '
        'zuerst zuschaust.',

        f'Bitte bis {FRIST}. Bis dahin kannst du jederzeit nachbessern; es '
        f'zählt der letzte Stand. Wenn du fertig bist, bekommst du deine '
        f'eigenen Themen als Zusammenfassung zum Mitnehmen — per Mail an dich '
        f'selbst, als Text zum Kopieren oder als PDF für deine Unterlagen.',

        'Auf der Seite wählst du gleich noch dein Menü fürs Abendessen, damit '
        'die Küche planen kann.',

        'Was am Abend damit passiert: Wir legen alle Themen nebeneinander, '
        'suchen die gemeinsamen Nenner und entscheiden zusammen, welche wir '
        'zuerst angehen. Wer nichts einreicht, fehlt in dieser Auslegeordnung '
        '— darum meine Bitte, dir die halbe Stunde wirklich zu nehmen.',

        'Zum Datenschutz: Deine Angaben liegen bis zum Absenden nur auf deinem '
        'Gerät. Danach werden sie verschlüsselt übertragen und in einer '
        'Datenbank in Westeuropa (Cloudflare) gespeichert. Zugriff haben '
        f'ausschliesslich Markus Hausmann-Spiess, {MELINA} und ich. Nach der '
        'Tagung wird gelöscht. Für das geführte Gespräch nutzen wir Claude von '
        'Anthropic, einen Anbieter in den USA — bitte keine Patientendaten und '
        'keine Namen von Mitarbeitenden eingeben.',

        'Bei Fragen melde dich einfach bei mir.',

        'Herzliche Grüsse\nDölf',
    ]


def als_text(teile: list, link: str, pin: str) -> str:
    zeilen = []
    for a in teile:
        if isinstance(a, tuple):
            zeilen.append(f'Dein persönlicher Zugang:\n{link}\n'
                          f'Deine persönliche PIN: {pin}\n'
                          f'Die Seite fragt die PIN beim ersten Öffnen ab und merkt '
                          f'sie sich danach auf deinem Gerät. Bitte nicht '
                          f'weitergeben — der Link gehört zu dir persönlich.')
        else:
            zeilen.append(a)
    return '\n\n'.join(zeilen) + '\n'


def als_html(teile: list, link: str, pin: str) -> str:
    stuecke = []
    for a in teile:
        if isinstance(a, tuple):
            stuecke.append(
                '<div style="margin:22px 0;padding:14px 16px;border-left:4px solid #1f6feb;'
                'background:#f3f7fd">'
                '<div style="margin-bottom:6px"><strong>Dein persönlicher Zugang</strong></div>'
                f'<div style="margin-bottom:8px"><a href="{html.escape(link)}">'
                f'{html.escape(link)}</a></div>'
                f'<div style="margin-bottom:8px"><strong>Deine persönliche PIN: '
                f'{html.escape(pin)}</strong></div>'
                '<div style="font-size:90%;color:#444">Die Seite fragt die PIN beim '
                'ersten Öffnen ab und merkt sie sich danach auf deinem Gerät. '
                'Bitte nicht weitergeben — der Link gehört zu dir persönlich.</div>'
                '</div>')
        else:
            stuecke.append('<p style="margin:0 0 14px">'
                           + html.escape(a).replace('\n', '<br>') + '</p>')
    return ('<html><body style="font-family:Calibri,Arial,sans-serif;font-size:11pt;'
            'line-height:1.5;color:#111">' + ''.join(stuecke) + '</body></html>')


def main() -> None:
    config = json.loads((WURZEL / 'werkzeug' / 'kader-config.json').read_text('utf-8'))
    ZIEL.mkdir(parents=True, exist_ok=True)
    gebaut = 0

    for token, person in config['tokens'].items():
        if person.get('rolle') != 'teilnahme':
            continue
        name = person['name']
        vorname = name.split()[0]
        link = f'{BASIS}?t={token}'
        pin = person['pin']
        teile = absaetze(vorname, name)

        mail = EmailMessage()
        # Betreff bewusst ohne Gedankenstrich und Umlaute: reines ASCII braucht
        # keine Header-Kodierung, damit steht auch dort nirgends ein "=".
        mail['Subject'] = ('Kadertagung Finanzbereich: deine Vorbereitung '
                           '(eine halbe Stunde, bis 7. September)')
        mail['From'] = ABSENDER
        mail['To'] = person['mail']
        # 8bit statt quoted-printable — sonst zerlegt Outlook lange Zeilen und
        # frisst dabei das Zeichen hinter dem weichen "="-Umbruch.
        mail.set_content(als_text(teile, link, pin), charset='utf-8', cte='8bit')
        mail.add_alternative(als_html(teile, link, pin), subtype='html',
                             charset='utf-8', cte='8bit')

        stamm = (vorname.lower().replace('ö', 'oe')
                 .replace('ü', 'ue').replace('ä', 'ae'))
        (ZIEL / f'einladung-{stamm}.eml').write_bytes(bytes(mail))
        (ZIEL / f'einladung-{stamm}.txt').write_text(als_text(teile, link, pin), 'utf-8')
        gebaut += 1

    print(f'{gebaut} Einladungen in {ZIEL}')


if __name__ == '__main__':
    main()
