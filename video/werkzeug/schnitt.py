#!/usr/bin/env python3
"""Leitet die Szenendauern aus der Tonaufnahme ab.

Wichtig: Jede Szene bekommt die Sprechdauer PLUS die darauf folgende Pause.
Damit bleibt der Atem zwischen den Saetzen erhalten — genau so, wie die Stimme
ihn gesprochen hat. Die frueher gebaute Fassung hat alle Pausen herausgeworfen
und wirkte deshalb gehetzt.

Ausserdem: VORLAUF Sekunden Stille vor dem ersten Wort, damit der Anfang nicht
auf dem allerersten Einzelbild sitzt und verschluckt wird.
"""
import json, pathlib, re, subprocess, sys

HIER    = pathlib.Path(__file__).parent
SZENEN  = pathlib.Path('/home/user/CAS-KI/docs/lernvideo-teilnahme-szenen.json')
TEXT    = pathlib.Path('/home/user/CAS-KI/docs/lernvideo-teilnahme-sprechtexte-elevenlabs.txt')
MP3     = pathlib.Path(sys.argv[1])
VORLAUF = 2.0      # Sekunden Stille vor dem ersten Wort
LANG    = 1.3      # ab dieser Laenge gilt eine Stille als Segmentgrenze

dauer = float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration',
        '-of','csv=p=0',str(MP3)],capture_output=True,text=True).stdout.strip())


def stillen(bis=None, mindest=0.55):
    """Stillen der Aufnahme als Liste (von, bis)."""
    cmd = ['ffmpeg']
    if bis: cmd += ['-t', str(bis)]
    cmd += ['-i', str(MP3), '-af', f'silencedetect=noise=-38dB:d={mindest}', '-f','null','-']
    roh = subprocess.run(cmd, capture_output=True, text=True).stderr
    paare, st = [], None
    for m in re.finditer(r'silence_(start|end): ([0-9.]+)', roh):
        if m.group(1)=='start': st=float(m.group(2))
        elif st is not None: paare.append((st, float(m.group(2)))); st=None
    return paare


# Regel: Was klingt, bleibt. Verworfen wird ausschliesslich eine fuehrende
# STILLE (die vorangestellte break-Marke im Text). Frueher gab es hier eine
# Erkennung fuer Lautfragmente — sie konnte die Woerter "Ich helfe dir" nicht
# von einem Stoergeraeusch unterscheiden und hat sie mehrfach entsorgt.
VORSPANN = 0.0

# Eine Stille, die am Dateianfang liegt, ist keine Segmentgrenze — sie kann
# aus einer versehentlich vorangestellten <break>-Marke stammen. Der Vorlauf
# vor dem ersten Wort wird ohnehin beim Mischen erzeugt.
grenzen = [(a,b) for a,b in stillen() if b-a >= LANG and a > max(VORSPANN, 0.10)]
if grenzen and grenzen[0][0] > 0 and VORSPANN == 0.0:
    fuehrend = [p for p in stillen() if p[0] <= 0.10 and p[1]-p[0] >= LANG]
    if fuehrend:
        VORSPANN = fuehrend[0][1]
        print(f"HINWEIS: Fuehrende Pause von {VORSPANN:.2f}s im Text — wird verworfen, "
              f"der Vorlauf entsteht beim Mischen.")

texte = [z.strip() for z in TEXT.read_text(encoding='utf-8').split('\n')
         if z.strip() and not z.strip().startswith('<break')]

if len(grenzen) != len(texte)-1:
    print(f"ABBRUCH: {len(grenzen)} lange Stillen gefunden, aber {len(texte)-1} erwartet "
          f"({len(texte)} Textsegmente). Aufnahme oder Text pruefen.")
    sys.exit(1)

# Sprechbereiche und die jeweils folgende Pause
bereiche, vor = [], VORSPANN
for a,b in grenzen:
    bereiche.append((vor, a, b))          # Sprache von..bis, naechste Sprache ab b
    vor = b
bereiche.append((vor, dauer, dauer))

alt = {s['id']: s for s in json.loads(SZENEN.read_text(encoding='utf-8'))}
neu, uhr = [], VORLAUF
for i, (a, b, naechste) in enumerate(bereiche):
    s = dict(list(alt.values())[i])       # Aktionen und Untertitel behalten
    sprech = b - a
    pause  = naechste - b                 # Atem nach diesem Satz
    s['dauer']    = round(sprech + pause, 2)
    s['sprechdauer'] = round(sprech, 2)
    s['ton_von']  = round(a, 3)
    s['ton_bis']  = round(b, 3)
    s['sprech']   = texte[i]
    neu.append(s)
    uhr += s['dauer']

neu[0]['dauer'] = round(neu[0]['dauer'] + VORLAUF, 2)   # Vorlauf faellt in Szene 1
SZENEN.write_text(json.dumps(neu, ensure_ascii=False, indent=2)+"\n", encoding='utf-8')

# Plausibilitaet: Verliert ein Segment Woerter (ElevenLabs schneidet
# gelegentlich den Anfang ab), bleibt seine Dauer gleich, waehrend der Text
# laenger ist — das Segment laeuft dann rechnerisch viel langsamer als die
# uebrigen. Ein Ausreisser nach oben ist das Warnzeichen.
tempo = sorted((s['sprechdauer']/max(len(s['sprech']),1)*1000, s['id']) for s in neu)
mitte = tempo[len(tempo)//2][0]
# Fehlen Woerter, ist das Segment kuerzer als sein Text — das Tempo faellt
# rechnerisch zu SCHNELL aus. Umgekehrt deutet ein zu langsames Segment auf
# Fremdmaterial hin, das mitgeschnitten wurde.
auffaellig = [(t, i) for t, i in tempo if t < mitte*0.80 or t > mitte*1.25]
print(f"\nSprechtempo: Mittelwert {mitte:.0f} ms/Zeichen, Spanne {tempo[0][0]:.0f}-{tempo[-1][0]:.0f}")
if auffaellig:
    for t, i in auffaellig:
        was = "zu schnell — moeglicherweise fehlen Woerter" if t < mitte else \
              "zu langsam — moeglicherweise ist Fremdmaterial drin"
        print(f"  ACHTUNG {i}: {t:.0f} ms/Zeichen, {t/mitte:.0%} des Mittels — {was}.")
else:
    print("  alle Segmente im normalen Bereich — kein Segment verliert Text\n")

print(f"MP3 {dauer:.2f}s · {len(neu)} Segmente · Vorlauf {VORLAUF}s")
print(f"{'Szene':16} {'Sprache':>8} {'Pause':>7} {'Szene':>8}")
for s in neu:
    print(f"{s['id']:16} {s['sprechdauer']:8.2f} {s['dauer']-s['sprechdauer']:7.2f} {s['dauer']:8.2f}")
print(f"\nVideolaenge wird {sum(s['dauer'] for s in neu):.2f}s (MP3 + Vorlauf = {dauer+VORLAUF:.2f}s)")
