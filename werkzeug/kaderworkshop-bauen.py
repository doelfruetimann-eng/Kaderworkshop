#!/usr/bin/env python3
"""Baut den Inhalt fuers Repo 'kaderworkshop' zusammen.

Zweck: PeakPrivacy soll sehen, worum es geht — die eingereichten Themen,
die Erhebungswerkzeuge und den Aufbau des Systems.

NIE mitkopiert werden Zugangsdaten: kader-config.json, tokens.json,
tokenliste.md und die fertigen .eml (die tragen Links und PINs). Das Skript
bricht ab, wenn am Schluss doch ein Token oder eine PIN im Baum steht.

Mailadressen der Teilnehmenden bleiben ebenfalls draussen — sie sind fuer
die Beurteilung ohne Wert und leicht nachzuliefern, falls doch gewuenscht.
"""
import json
import pathlib
import shutil
import subprocess
import sys

WURZEL = pathlib.Path(__file__).resolve().parent.parent
YOUTUBE = pathlib.Path('/workspace/youtube')
ZIEL = WURZEL / 'scratchpad' / 'kaderworkshop'

FRAGEN = {
    'f1': 'Worum geht es? Welcher Ablauf, welche Aufgabe?',
    'f2': 'Wie läuft es heute ab, und was kostet das an Zeit und Nerven?',
    'f3': 'Wer ist betroffen?',
    'f4': 'Welche Systeme, Daten und Unterlagen sind im Spiel?',
    'f5': 'Wie sähe es aus, wenn es gut wäre?',
    'f6': 'Wo könnte KI oder ein Werkzeug helfen?',
}


def stand() -> dict:
    config = json.loads((WURZEL / 'werkzeug' / 'kader-config.json').read_text('utf-8'))
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
        sys.exit('stand-Route hat nicht geantwortet')
    return d


def putze(d: dict) -> dict:
    """Mailadressen raus, sonst alles behalten."""
    sauber = json.loads(json.dumps(d))
    for p in sauber.get('personen', []):
        p.pop('mail', None)
    return sauber


def themen_markdown(d: dict) -> str:
    zeilen = ['# Die eingereichten Themen', '',
              'Erhoben im geführten KI-Gespräch auf der Vorbereitungsseite. '
              'Jede Person nennt zwei bis drei Stellen aus ihrem Alltag, an '
              'denen die Arbeit regelmässig hakt; die KI fragt entlang von '
              'sechs Leitfragen nach.', '',
              '## Die sechs Leitfragen', '']
    zeilen += [f'{k.upper()} — {t}' for k, t in FRAGEN.items()]
    zeilen += ['', '---', '']
    for a in d.get('abgaben', []):
        zeilen += [f"## {a['name']} — {a['einheit']}", '']
        for i, pp in enumerate(a.get('painpoints') or [], 1):
            zeilen += [f"### {i}. {pp['titel']}", '']
            for k, frage in FRAGEN.items():
                antwort = (pp.get(k) or '').strip()
                zeilen += [f'**{frage}**', '',
                           antwort if antwort else '_(nicht beantwortet)_', '']
        zeilen.append('')
    return '\n'.join(zeilen)


def standort_markdown(d: dict) -> str:
    zeilen = ['# Standortbestimmung: wo das Kader heute mit KI steht', '',
              'Vor dem Erfassen der Themen beantwortet jede Person fünf '
              'Fragen zu ihrem eigenen Umgang mit KI.', '']
    for a in d.get('abgaben', []):
        s = a.get('standort') or {}
        zeilen += [f"## {a['name']} — {a['einheit']}", '',
                   f"- **Nutzung heute:** {s.get('haeufigkeit') or '—'}",
                   f"- **Wofür schon genutzt:** {', '.join(s.get('erfahrungen') or []) or '—'}",
                   f"- **Werkzeuge:** {', '.join(s.get('werkzeuge') or []) or '—'}",
                   f"- **Erwartung:** {s.get('erwartung') or '—'}",
                   f"- **Sorgen:** {s.get('sorgen') or '—'}", '']
    return '\n'.join(zeilen)


DATENSCHUTZ = """# Was den Teilnehmenden zugesichert wurde

Wichtig für alle, die dieses Repo lesen — auch für Anbieter, mit denen wir
über eine Lösung sprechen.

Jede der neun Personen hat mit der Einladung diesen Text erhalten:

> Deine Angaben liegen bis zum Absenden nur auf deinem Gerät. Danach werden
> sie verschlüsselt übertragen und in einer Datenbank in Westeuropa
> (Cloudflare) gespeichert. Zugriff haben ausschliesslich Markus
> Hausmann-Spiess, Melina Lopez Garcia und ich. Nach der Tagung wird
> gelöscht. Für das geführte Gespräch nutzen wir Claude von Anthropic, einen
> Anbieter in den USA — bitte keine Patientendaten und keine Namen von
> Mitarbeitenden eingeben.

Daraus folgt für die Nutzung dieser Daten:

- **Nur für die Kadertagung und ihre Folgearbeiten.** Keine Weitergabe an
  Dritte, keine Verwendung als Referenz oder Fallbeispiel ohne ausdrückliche
  Zustimmung der Spitäler Schaffhausen.
- **Kein Training.** Die Inhalte werden nicht zum Training allgemeiner
  Modelle verwendet.
- **Löschung nach der Tagung.** Wer eine Kopie erhält, löscht sie mit.
- Die Texte nennen interne Systeme, Ablaufschwächen und teilweise
  Personalsituationen. Sie sind nicht für die Öffentlichkeit bestimmt.

Zugangsdaten (persönliche Links, PINs, Leitungsschlüssel) sind in diesem
Repo **nicht** enthalten und gehören auch nie hinein.
"""


def readme(d: dict) -> str:
    da = [p for p in d['personen'] if p['abgegeben']]
    themen = sum(len(a.get('painpoints') or []) for a in d.get('abgaben', []))
    einheiten = len({a['einheit'] for a in d.get('abgaben', [])})
    return f"""# Kadertagung Finanzbereich — Pain Points und Erhebungswerkzeug

Spitäler Schaffhausen, Kadertagung vom 14. September 2026.
Privates Repo. Bitte zuerst [DATENSCHUTZ.md](DATENSCHUTZ.md) lesen.

## Worum es geht

Das Spital hat einen Kredit für die Einführung von KI bewilligt. Statt
über Technik zu reden, sammeln wir vorher die echten Probleme: Neun
Leitungspersonen aus dem Finanz- und Supportbereich nennen je zwei bis drei
Stellen aus ihrem Alltag, an denen die Arbeit regelmässig hakt — etwas, das
Zeit frisst, immer wiederkommt, oft schiefgeht oder das niemand gerne macht.
Eine Lösungsidee wird ausdrücklich nicht verlangt.

Am Abend der Tagung werden diese Themen nebeneinandergelegt, geclustert,
bewertet und priorisiert.

## Stand

- **{len(da)} von {len(d['personen'])} Personen** haben abgegeben
- **{themen} Themen** aus **{einheiten} von 9 Organisationseinheiten**
- Frist: 7. September 2026 · Tagung: 14. September 2026

## Was hier liegt

| Ordner | Inhalt |
|---|---|
| `daten/` | Die Themen im Volltext, die Standortbestimmung, die Rohdaten als JSON |
| `system/` | Teilnahmeseite, alle acht Serverrouten, Dashboard, Werkbank, Betriebsanleitung |
| `konzept/` | Ablauf des Abends, Methodik, Übergabeunterlagen, Papierform als PDF |
| `video/` | Das Lernvideo, die Sprechtexte und die Skripte, die es bauen |
| `werkzeug/` | Skripte für Zugänge, Mailversand und die Verteilfassung |

## Das Laufende ansehen

Alles läuft unter **umfrage.win**. Die Adressen:

| Adresse | Was zu sehen ist |
|---|---|
| [umfrage.win/kadertagung/?demo=1](https://umfrage.win/kadertagung/?demo=1) | **Der beste Einstieg.** Die Teilnahmeseite im Vorführbetrieb — ohne Zugangsdaten, mit Beispieldaten, ohne dass etwas gespeichert wird |
| [umfrage.win/kadertagung/](https://umfrage.win/kadertagung/) | Der echte Zugang. Fragt nach persönlichem Link und PIN, ohne beides kommt man nicht weiter |
| [umfrage.win/kadertagung/lernvideo.mp4](https://umfrage.win/kadertagung/lernvideo.mp4) | Zwei Minuten, zeigt den ganzen Ablauf |
| [umfrage.win/kadertagung/dashboard](https://umfrage.win/kadertagung/dashboard) | Rücklauf und Auswertung. Zeigt ohne Leitungsschlüssel nichts an |
| [umfrage.win/kadertagung/werkbank](https://umfrage.win/kadertagung/werkbank) | Das Arbeitsgerät für den Abend: Bewertung, Priorisierung, Portfolio. Startet leer, die Themen werden aus dem Dashboard hineingeladen |

Der Demo-Betrieb ist der schnellste Weg, ein Gefühl für die Erhebung zu
bekommen: Er durchläuft dieselben Schritte wie die echten Teilnehmenden,
inklusive geführtem Gespräch, nur ohne Datenbank dahinter.

## Wie erhoben wird

Die Teilnehmenden öffnen einen persönlichen Link, geben eine vierstellige
PIN ein und werden durch fünf Schritte geführt. Die Themen erzählen sie
einem KI-Gespräch, das entlang von sechs Leitfragen nachfragt und am Schluss
den Text glättet. Diktieren ist möglich; auf dem Handy funktioniert es
besser als am Rechner.

Technisch: eine statische Seite auf Cloudflare Workers, Daten in einer
D1-Datenbank in Westeuropa, KI-Aufrufe an Claude Opus 5 bei Anthropic.

## Warum dieses Repo besteht

Damit ein Anbieter sehen kann, worum es tatsächlich geht: welche Art von
Aufgaben im Haus anfallen, in welcher Sprache und Tiefe sie beschrieben
sind, und wie das Material aussieht, das eine Lösung später verarbeiten
müsste.
"""


def kopiere(quelle: pathlib.Path, ziel: pathlib.Path) -> None:
    ziel.parent.mkdir(parents=True, exist_ok=True)
    if quelle.is_dir():
        shutil.copytree(quelle, ziel, dirs_exist_ok=True)
    elif quelle.exists():
        shutil.copy2(quelle, ziel)


def maskiere_mails(config: dict) -> None:
    """Mailadressen der Teilnehmenden durch Platzhalter ersetzen.

    Sie sind fuer die Beurteilung ohne Wert. Die Adresse von Doelf bleibt —
    sie steht als Absender in den Skripten und ist ohnehin bekannt.
    """
    adressen = sorted(
        {v['mail'] for v in config['tokens'].values() if v.get('mail')}
        - {'Doelf.Ruetimann@spitaeler-sh.ch'},
        key=len, reverse=True)
    geaendert = 0
    for f in ZIEL.rglob('*'):
        if not f.is_file() or f.suffix in ('.png', '.mp4', '.pdf'):
            continue
        try:
            inhalt = f.read_text('utf-8')
        except Exception:
            continue
        neu = inhalt
        for a in adressen:
            neu = neu.replace(a, 'vorname.name@spitaeler-sh.ch')
        if neu != inhalt:
            f.write_text(neu, 'utf-8')
            geaendert += 1
    print(f'  Mailadressen maskiert in {geaendert} Dateien')


def pruefe(config: dict) -> None:
    """Abbrechen, wenn irgendwo ein Token oder eine PIN steht."""
    geheim = set(config['tokens'])
    pins = {v['pin'] for v in config['tokens'].values() if v.get('pin')}
    treffer = []
    for f in ZIEL.rglob('*'):
        if not f.is_file():
            continue
        try:
            inhalt = f.read_text('utf-8', errors='ignore')
        except Exception:
            continue
        for g in geheim:
            if g in inhalt:
                treffer.append((f.relative_to(ZIEL), 'Token'))
        for p in pins:
            # 4-stellige PIN nur melden, wenn sie als Zugangsdatum auftritt
            if f'"pin":"{p}"' in inhalt or f'PIN: {p}' in inhalt:
                treffer.append((f.relative_to(ZIEL), 'PIN'))
    if treffer:
        for f, art in treffer:
            print(f'  ! {art} in {f}')
        sys.exit('ABBRUCH: Zugangsdaten im Baum')
    print('  Sicherheitsprüfung: keine Tokens, keine PINs')


def main() -> None:
    config = json.loads((WURZEL / 'werkzeug' / 'kader-config.json').read_text('utf-8'))
    d = putze(stand())

    if ZIEL.exists():
        shutil.rmtree(ZIEL)
    ZIEL.mkdir(parents=True)

    (ZIEL / 'README.md').write_text(readme(d), 'utf-8')
    (ZIEL / 'DATENSCHUTZ.md').write_text(DATENSCHUTZ, 'utf-8')

    daten = ZIEL / 'daten'
    daten.mkdir()
    (daten / 'themen.md').write_text(themen_markdown(d), 'utf-8')
    (daten / 'standortbestimmung.md').write_text(standort_markdown(d), 'utf-8')
    (daten / 'abgaben.json').write_text(
        json.dumps(d, ensure_ascii=False, indent=2), 'utf-8')

    # Das System
    kopiere(YOUTUBE / 'web/public/kadertagung/index.html',
            ZIEL / 'system/teilnahmeseite.html')
    kopiere(YOUTUBE / 'web/public/kadertagung/dashboard.html',
            ZIEL / 'system/dashboard.html')
    kopiere(YOUTUBE / 'web/src/app/api/kadertagung', ZIEL / 'system/api')
    kopiere(YOUTUBE / 'web/src/lib/kadertagung.ts', ZIEL / 'system/kadertagung.ts')
    kopiere(YOUTUBE / 'KADERTAGUNG.md', ZIEL / 'system/BETRIEB.md')
    kopiere(WURZEL / 'werkbank-verteilfassung.html', ZIEL / 'system/werkbank.html')

    # Die Werkzeuge — ohne die Dateien mit Zugangsdaten
    for name in ('tokens.py', 'verteilfassung.py', 'budget.py',
                 'einladungen-bauen.py', 'erinnerung-bauen.py',
                 'leitungsmails-bauen.py', 'nachtrag-bauen.py',
                 'standmeldung-bauen.py', 'kaderworkshop-bauen.py'):
        kopiere(WURZEL / 'werkzeug' / name, ZIEL / 'werkzeug' / name)

    # Das Lernvideo und wie es entsteht
    kopiere(WURZEL / 'docs/lernvideo-teilnahme.mp4', ZIEL / 'video/lernvideo.mp4')
    for name in ('lernvideo-teilnahme-sprechtexte.md', 'lernvideo-elevenlabs.md',
                 'lernvideo-teilnahme-szenen.json'):
        kopiere(WURZEL / 'docs' / name, ZIEL / 'video' / name)
    for name in ('schnitt.py', 'rec.mjs', 'mische.py'):
        kopiere(WURZEL / 'scratchpad/video' / name, ZIEL / 'video/werkzeug' / name)

    # Die Konzeptseiten — Ablauf des Abends, Methodik, Uebergabe
    for name in ('index.html', 'programm.html', 'vorbereitung.html',
                 'betrieb.html', 'fuer-melina.html'):
        kopiere(WURZEL / name, ZIEL / 'konzept' / name)
    kopiere(WURZEL / 'docs/werkbank-papierform.pdf',
            ZIEL / 'konzept' / 'werkbank-papierform.pdf')

    # Unterlagen
    for name in ('abendessen-ziegelhuette.md', 'betrieb-und-datenschutz.md',
                 'kadertagung-vorbereitung.md', 'verteiler-und-einladung.md'):
        kopiere(WURZEL / 'docs' / name, ZIEL / 'unterlagen' / name)

    maskiere_mails(config)
    pruefe(config)
    dateien = sum(1 for f in ZIEL.rglob('*') if f.is_file())
    print(f'  {dateien} Dateien in {ZIEL}')


if __name__ == '__main__':
    main()
