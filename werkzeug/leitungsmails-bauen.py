#!/usr/bin/env python3
"""Baut die Mails mit dem Dashboard-Zugang fuer die Leitung.

ACHTUNG: Diese Mails enthalten den Leitungsschluessel im Klartext. Er oeffnet
ohne PIN saemtliche Abgaben aller neun Personen. Die Dateien bleiben im
Scratchpad und gehen nie ins Repo.

Melinas Mailadresse ist im Projekt nirgends hinterlegt. Sie laesst sich per
--melina mitgeben; ohne Angabe bleibt das An-Feld leer und wird in Outlook
von Hand gesetzt.

Kodierung wie bei den uebrigen Mails: HTML-Teil plus Textteil, beide 8bit,
Betreff in reinem ASCII.
"""
import argparse
import html
import json
import pathlib
from email.message import EmailMessage

import budget

WURZEL = pathlib.Path(__file__).resolve().parent.parent
ZIEL = WURZEL / 'scratchpad' / 'einladungen'
DASHBOARD = 'https://umfrage.win/kadertagung/dashboard'
WERKBANK = 'https://umfrage.win/kadertagung/werkbank'
ABSENDER = 'Doelf.Ruetimann@spitaeler-sh.ch'

WAS_MAN_SIEHT = [
    'wer schon abgegeben hat und wer noch offen ist',
    'die eingereichten Themen, nach Einheit geordnet',
    'die Auswertung der Standortbestimmung — wo das Kader heute mit KI steht',
    'das Stimmungsbild aus dem Kurz-Feedback',
    'einen Knopf, der aus allen Themen per KI Cluster vorschlägt',
    'einen Knopf, der eine Erinnerungsmail an alle Offenen vorbereitet',
]


def absaetze(vorname: str, extra: list) -> list:
    return [
        f'Hallo {vorname}',

        'Die Einladungen an die neun Teilnehmenden sind raus. Damit du den '
        'Rücklauf mitverfolgen kannst, hier dein Zugang zum Dashboard.',

        ('zugang',),

        ('liste', 'Was du dort siehst:'),

        'Die Seite fragt beim Öffnen nach dem Schlüssel und merkt ihn sich '
        'danach in deinem Browser. Es gibt keine Benutzernamen und keine '
        'Konten — der Schlüssel allein ist der Zugang.',

        'Zwei Bitten dazu: Bitte nicht weiterleiten und nicht in einen '
        'geteilten Ordner oder ein Wiki legen. Der Schlüssel öffnet ohne '
        'weitere Abfrage sämtliche Abgaben aller neun Personen. Wenn er '
        'irgendwo landet, wo er nicht hingehört, sag mir Bescheid — ich '
        'erzeuge dann einen neuen.',

        'Ein Hinweis zum Netz: Die Seite liegt ausserhalb des Spitalnetzes '
        'und ist im internen Netz gesperrt. Vom Arbeitsplatz aus kommst du '
        'nur über das Patienten-WLAN darauf; von zu Hause oder über die '
        'Mobildaten des Handys geht es direkt.',

        *extra,

        'Fragen jederzeit an mich.',

        'Herzliche Grüsse\nDölf',
    ]


EXTRA = {
    'Markus': [
        'Und eine Frage an dich als ICT-Leiter: Könntest du umfrage.win im '
        'internen Netz freischalten? Dann fällt der Umweg übers '
        'Patienten-WLAN für alle weg — ich musste den Leuten vorhin extra '
        'eine Nachtragsmail deswegen schreiben. Es ist eine statische Seite '
        'auf Cloudflare, ohne Downloads und ohne Anmeldung ausser unserer '
        'eigenen.',
    ],
    'Fabienne': [
        'Für dich ist das Dashboard aus einem zweiten Grund interessant: Du '
        'hast den Entwurf für die Kadertagung ursprünglich geschrieben, und '
        'deine sechs Leitfragen sind wortgleich die sechs Fragen, die jetzt '
        'jedes Thema strukturieren. Im Dashboard siehst du also, was aus '
        'deiner Idee geworden ist, sobald die ersten Abgaben eintreffen.',

        'Dein Zugang als Teilnehmerin bleibt davon unberührt — der Link und '
        'die PIN aus der Einladung gelten weiter. Das hier ist ein zweiter, '
        'getrennter Zugang.',

        ('titel', 'Und noch etwas anderes: das Budget fürs Abendessen'),

        'Dazu fehlt mir noch deine Freigabe. Wir sind zu zehnt — die neun '
        'Einheitsleitungen und Melina — und essen im Gasthof Ziegelhütte. '
        'Jede Person wählt ihr Menü am Schluss der Online-Vorbereitung '
        'selbst; das Dashboard zählt die Bestellungen zusammen, die Küche '
        'weiss also rechtzeitig Bescheid.',

        ('budget',),

        f'Mit einer Dessert- und Kaffeerunde plane ich {budget.MIT_DESSERT}. '
        f'Für den Raum kommt nichts dazu: Die Ziegelhütte verlangt keine '
        f'Miete, weil wir dort essen. Der ganze Betrag geht in Essen und '
        f'Getränke.',

        'Zur Auswahl: drei Fleischgerichte (Cordon bleu von der Karte, '
        'Wienerschnitzel, Zürcher Geschnetzeltes), dazu ein vegetarisches '
        'und ein veganes Gericht, für alle ein Schüsselsalat. Beim Cordon '
        'bleu habe ich mit der 150-Gramm-Portion gerechnet; wer eine '
        'grössere will, zahlt die Differenz selbst. Den Wein wählt Jürg aus, '
        'das Bier Raphael.',

        'Reserviert ist bereits, das musst du nicht mehr anstossen. Meine '
        'Frage ist nur: Klärst du das Budget mit Jürg? Er ist als Leiter '
        'Finanzen ohnehin dabei und wählt auch den Wein aus — dann ist es '
        'in einem Aufwasch erledigt und ich weiss, mit welchem Betrag ich '
        'rechnen darf.',
    ],
    'Melina': [
        'Für den Abend selbst gibt es zusätzlich die Werkbank unter '
        f'{WERKBANK}. Dort werden die Themen bewertet, priorisiert und für '
        'die Diskussion aufbereitet. Die schauen wir zusammen an, sobald der '
        'Rücklauf steht — vorher ist sie noch leer.',

        'Sobald ein paar Abgaben da sind, würde ich mit dir kurz durchgehen, '
        'was wir daraus für deinen Impuls und für die Moderation mitnehmen.',
    ],
}


def als_text(teile: list, schluessel: str) -> str:
    raus = []
    for a in teile:
        if isinstance(a, tuple) and a[0] == 'zugang':
            raus.append(f'Dashboard: {DASHBOARD}\n'
                        f'Dein Leitungsschlüssel: {schluessel}')
        elif isinstance(a, tuple) and a[0] == 'liste':
            raus.append(a[1] + '\n' + '\n'.join('- ' + z for z in WAS_MAN_SIEHT))
        elif isinstance(a, tuple) and a[0] == 'titel':
            raus.append(a[1].upper())
        elif isinstance(a, tuple) and a[0] == 'budget':
            raus.append(budget.tabelle_text())
        else:
            raus.append(a)
    return '\n\n'.join(raus) + '\n'


def als_html(teile: list, schluessel: str) -> str:
    raus = []
    for a in teile:
        if isinstance(a, tuple) and a[0] == 'zugang':
            raus.append(
                '<div style="margin:22px 0;padding:14px 16px;border-left:4px solid #1f6feb;'
                'background:#f3f7fd">'
                '<div style="margin-bottom:8px"><strong>Dashboard</strong></div>'
                f'<div style="margin-bottom:10px"><a href="{DASHBOARD}">{DASHBOARD}</a></div>'
                '<div><strong>Dein Leitungsschlüssel</strong></div>'
                '<div style="font-family:Consolas,monospace;font-size:12pt;'
                'letter-spacing:.5px;margin-top:4px">'
                f'{html.escape(schluessel)}</div></div>')
        elif isinstance(a, tuple) and a[0] == 'titel':
            raus.append('<h3 style="margin:26px 0 10px;padding-top:16px;'
                        'border-top:1px solid #ddd;font-size:12pt">'
                        + html.escape(a[1]) + '</h3>')
        elif isinstance(a, tuple) and a[0] == 'budget':
            raus.append(budget.tabelle_html())
        elif isinstance(a, tuple) and a[0] == 'liste':
            punkte = ''.join(f'<li style="margin-bottom:5px">{html.escape(z)}</li>'
                             for z in WAS_MAN_SIEHT)
            raus.append(f'<p style="margin:0 0 8px">{html.escape(a[1])}</p>'
                        f'<ul style="margin:0 0 14px;padding-left:20px">{punkte}</ul>')
        else:
            raus.append('<p style="margin:0 0 14px">'
                        + html.escape(a).replace('\n', '<br>') + '</p>')
    return ('<html><body style="font-family:Calibri,Arial,sans-serif;font-size:11pt;'
            'line-height:1.5;color:#111">' + ''.join(raus) + '</body></html>')


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--melina', default='', help='Mailadresse von Melina')
    a = p.parse_args()

    config = json.loads((WURZEL / 'werkzeug' / 'kader-config.json').read_text('utf-8'))
    schluessel = {v['name']: t for t, v in config['tokens'].items()
                  if v.get('rolle') == 'leitung'}
    ZIEL.mkdir(parents=True, exist_ok=True)

    empfaenger = {
        'Markus': ('Markus Hausmann-Spiess', 'vorname.name@spitaeler-sh.ch'),
        'Melina': ('Melina', a.melina),
        'Fabienne': ('Fabienne Grant', 'vorname.name@spitaeler-sh.ch'),
    }

    for vorname, (voller_name, adresse) in empfaenger.items():
        if voller_name not in schluessel:
            print(f'  ! kein Leitungsschlüssel für {voller_name} — übersprungen')
            continue
        teile = absaetze(vorname, EXTRA[vorname])
        mail = EmailMessage()
        mail['Subject'] = 'Kadertagung: dein Zugang zum Dashboard'
        mail['From'] = ABSENDER
        if adresse:
            mail['To'] = adresse
        mail.set_content(als_text(teile, schluessel[voller_name]),
                         charset='utf-8', cte='8bit')
        mail.add_alternative(als_html(teile, schluessel[voller_name]),
                             subtype='html', charset='utf-8', cte='8bit')
        ziel = ZIEL / f'dashboard-{vorname.lower()}.eml'
        ziel.write_bytes(bytes(mail))
        print(f'{ziel.name}  →  {adresse or "(Adresse fehlt, in Outlook setzen)"}')


if __name__ == '__main__':
    main()
