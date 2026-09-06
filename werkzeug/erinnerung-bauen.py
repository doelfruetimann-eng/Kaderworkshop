#!/usr/bin/env python3
"""Baut die Erinnerungsmail an alle, die noch nicht abgegeben haben.

Wer offen ist, wird live ueber die stand-Route ermittelt — nicht von Hand
gepflegt, sonst erinnert man jemanden, der laengst abgegeben hat.

Die Mail enthaelt bewusst KEINEN persoenlichen Link und KEINE PIN: Beides
haben die Leute aus der Einladung, und eine Sammelmail mit BCC darf keine
persoenlichen Zugaenge tragen.

Kodierung wie bei den uebrigen Mails: HTML-Teil plus Textteil, beide 8bit,
Betreff in reinem ASCII — sonst zerlegt Outlook lange Zeilen an den weichen
"="-Umbruechen des quoted-printable.
"""
import datetime
import html
import json
import pathlib
import subprocess
from email.message import EmailMessage

WURZEL = pathlib.Path(__file__).resolve().parent.parent
ZIEL = WURZEL / 'scratchpad' / 'einladungen'
ABSENDER = 'Doelf.Ruetimann@spitaeler-sh.ch'
FRIST = datetime.date(2026, 9, 7)
TAGUNG = '14. September'


def offene(config: dict) -> list:
    """Namen und Adressen derer, die noch nichts abgeschickt haben."""
    schluessel = next(t for t, v in config['tokens'].items()
                      if v.get('rolle') == 'leitung' and v['name'].startswith('Dölf'))
    roh = subprocess.run(
        ['curl', '-s', '--max-time', '25', '-X', 'POST',
         'https://umfrage.win/api/kadertagung/stand',
         '-H', 'content-type: application/json',
         '-d', json.dumps({'token': schluessel})],
        capture_output=True, text=True).stdout
    d = json.loads(roh)
    if not d.get('ok'):
        raise SystemExit('stand-Route hat nicht geantwortet — Mail nicht gebaut')
    return [(p['name'], p['mail']) for p in d['personen']
            if not p['abgegeben'] and p.get('mail')]


def absaetze(tage: int) -> list:
    return [
        'Hallo zusammen',

        f'Die Frist für die Vorbereitung auf die Kadertagung läuft am Montag, '
        f'7. September ab — das sind noch {tage} Tage. Ein paar von euch sind '
        f'schon durch, danke dafür. Diese Mail geht an alle, bei denen noch '
        f'nichts angekommen ist.',

        'Es braucht nicht viel: zwei bis drei Stellen aus deinem Alltag, an '
        'denen die Arbeit regelmässig hakt. Etwas, das Zeit frisst, immer '
        'wiederkommt, oft schiefgeht oder das niemand gerne macht. Eine '
        'Lösung musst du nicht mitbringen — das Problem genügt.',

        'Rechne mit einer guten halben Stunde. Du kannst jederzeit aufhören '
        'und später weitermachen, auch vom Handy aus; das Diktieren geht dort '
        'sogar besser als am Rechner.',

        ('kasten',),

        f'Warum das zählt: Am {TAGUNG} legen wir alle Themen nebeneinander, '
        f'suchen die gemeinsamen Nenner und entscheiden zusammen, welche wir '
        f'zuerst angehen. Wer nichts einreicht, kommt in dieser Auslegeordnung '
        f'nicht vor — und genau dort wird entschieden, wofür der KI-Kredit '
        f'eingesetzt wird.',

        'Wenn dich etwas aufhält — der Link geht nicht auf, die PIN ist weg, '
        'du bist unsicher, ob dein Thema taugt — melde dich einfach bei mir. '
        'Das ist in zwei Minuten geklärt.',

        'Danke und bis bald',

        'Herzliche Grüsse\nDölf',
    ]


KASTEN = [
    'Dein persönlicher Link und deine PIN stehen in meiner Einladungsmail '
    'vom 19. August. Beide gelten unverändert weiter.',
    'Die Seite ist im Spitalnetz gesperrt: Nimm das Patienten-WLAN, oder geh '
    'von zu Hause beziehungsweise über die Mobildaten des Handys drauf.',
    'Am Schluss wählst du gleich noch dein Menü fürs Abendessen.',
]


def als_text(teile: list) -> str:
    raus = []
    for a in teile:
        if isinstance(a, tuple):
            raus.append('\n'.join('- ' + z for z in KASTEN))
        else:
            raus.append(a)
    return '\n\n'.join(raus) + '\n'


def als_html(teile: list) -> str:
    raus = []
    for a in teile:
        if isinstance(a, tuple):
            punkte = ''.join(f'<li style="margin-bottom:6px">{html.escape(z)}</li>'
                             for z in KASTEN)
            raus.append(
                '<div style="margin:22px 0;padding:14px 16px;'
                'border-left:4px solid #1f6feb;background:#f3f7fd">'
                f'<ul style="margin:0;padding-left:20px">{punkte}</ul></div>')
        else:
            raus.append('<p style="margin:0 0 14px">'
                        + html.escape(a).replace('\n', '<br>') + '</p>')
    return ('<html><body style="font-family:Calibri,Arial,sans-serif;font-size:11pt;'
            'line-height:1.5;color:#111">' + ''.join(raus) + '</body></html>')


def main() -> None:
    config = json.loads((WURZEL / 'werkzeug' / 'kader-config.json').read_text('utf-8'))
    leute = offene(config)
    if not leute:
        print('Niemand offen — keine Erinnerung nötig.')
        return
    tage = (FRIST - datetime.date.today()).days
    teile = absaetze(tage)

    mail = EmailMessage()
    mail['Subject'] = 'Kadertagung: noch bis 7. September Zeit fuer deine Vorbereitung'
    mail['From'] = ABSENDER
    mail['To'] = ABSENDER                 # alle uebrigen ins BCC
    mail['Bcc'] = ', '.join(sorted(m for _, m in leute))
    mail.set_content(als_text(teile), charset='utf-8', cte='8bit')
    mail.add_alternative(als_html(teile), subtype='html', charset='utf-8', cte='8bit')

    ZIEL.mkdir(parents=True, exist_ok=True)
    ziel = ZIEL / 'erinnerung-offene.eml'
    ziel.write_bytes(bytes(mail))
    (ZIEL / 'erinnerung-offene.txt').write_text(als_text(teile), 'utf-8')
    print(f'Erinnerung an {len(leute)} Offene ({tage} Tage bis zur Frist):')
    for n, m in sorted(leute):
        print(f'  {n:24} {m}')
    print(f'\n{ziel}')


if __name__ == '__main__':
    main()
